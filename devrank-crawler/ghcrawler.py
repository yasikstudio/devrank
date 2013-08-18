#!/usr/bin/env python

import sys
import logging
from logging.handlers import RotatingFileHandler
import collections
import json
import requests
import re
from requests.exceptions import HTTPError, ConnectionError
from pyes import *
from pyes.query import *
from pyes.exceptions import *
from time import localtime, strftime

import config

def debug(str):
    if config.DEBUG:
        print(str)

class GitHubCrawler(object):
    """GitHub Crawler"""

    USERLIST = 'userlist.txt'
    MAXDEPTH = 5
    RETRY = 3

    def __init__(self):
        """Initializer for GitHubCrawler."""
        self.usernames = config.usernames
        self.password = config.password
        self.username_idx = 0
        self.username = self.usernames[0]
        self.visited = set()
        self.unvisited = collections.deque(self.userlist())
        self.out = None
        self.es_conn = ES(config.es_host)
        self.remaining_requests = 0

    def __get(self, url=None, path=None, etag=None):
        retry = self.RETRY
        while retry > 0:
            retry -= 1
            try:
                if url == None and path != None:
                    url = 'https://api.github.com/%s' % path
                headers = { 'If-None-Match': etag }
                result = requests.get(url, auth=(self.username, self.password),
                        headers=headers)
                self.remaining_requests =\
                        result.headers['X-RateLimit-Remaining']
                if result.status_code == 200:
                    return result
                elif result.status_code == 304:
                    # cached
                    return result
                elif result.status_code == 403 and self.remaining_requests == 0:
                    # RateLimit
                    self.toggle_username()
                    continue
                else:
                    print result.status_code
                    print result.json
                    raise HTTPError('API failed. unexpected')
            except (HTTPError, ConnectionError) as e:
                print 'HTTPError. retry...'
                print url, path
        raise HTTPError('API failed')

    def __index(self, index_type, index_id, data):
        retry = self.RETRY
        index_name = config.index_name
        debug('__index(%s, %s)' % (index_type, index_id))
        while retry > 0:
            retry -= 1
            try:
                self.es_conn.index(data, index_name, index_type, index_id)
                return
            except NoServerAvailable:
                print 'pyes Server NoServerAvailable. retry...'
        raise HTTPError('pyes failed')

    def __update(self, index_type, index_id, script, params=None):
        retry = self.RETRY
        index_name = config.index_name
        debug('__update(%s, %s)' % (index_type, index_id))
        while retry > 0:
            retry -= 1
            try:
                self.es_conn.partial_update(index_name, index_type, index_id,
                    script=script, params=params)
                return
            except NoServerAvailable:
                print 'pyes Server NoServerAvailable. retry...'
            except DocumentMissingException:
                print('document missing (%s, %s, %s, %s)' %
                    (index_type, index_id, script, params))
        raise HTTPError('pyes failed')

    def __link_header_parse(self, link_header):
        result = {}
        if link_header == None:
            return result
        for link in link_header.split(', '):
            m = re.search('<(.+)>; rel="(.+)"', link)
            if type(m) != None:
                rel = m.group(2)
                url = m.group(1)
                result[rel] = url
        return result

    def toggle_username(self):
        self.username_idx += 1
        self.username_idx %= len(self.username)
        self.username = self.usernames[self.username_idx]
        debug('toggle username : %s' % self.username)

    def userlist(self):
        """Get users from file at first time"""
        f = open(self.USERLIST)
        users = [(u.strip(), 0) for u in f.readlines()
                 if u.strip() != '' and u.strip()[0:1] != '#']
        f.close()
        return users

    def user(self, username):
        """Get user by username"""
        etag = None
        user_dict = {}
        q = FilteredQuery(MatchAllQuery(), TermFilter('login', username))
        results = self.es_conn.search(q)
        if results.total == 1:
            user_dict = results[0]
            etag = user_dict['ETag']
        result = self.__get(path='users/%s' % username, etag=etag)
        status_code = result.status_code
        if status_code == 304:
            debug('cached %s' % username)
        else:
            user_dict = result.json
            user_dict['ETag'] = result.headers['ETag']
            self.__index('users', user_dict['id'], user_dict)
        if user_dict['type'] == 'User':
            return user_dict
        return None

    def user_id_from_es(self, username):
        user_dict = {}
        q = FilteredQuery(MatchAllQuery(), TermFilter('login', username))
        results = self.es_conn.search(q)
        if results.total == 1:
            user_dict = results[0]
            return user_dict['id']
        return None

    def followers(self, username, user_id):
        """Get followers list by username"""
        path = 'users/%s/followers' % username
        url = None
        etag = None # TODO: applied
        followers = []
        users = []
        while path != None or url != None:
            debug('followers(%s) path=%s, url=%s' % (username, path, url))
            res = self.__get(path=path, url=url, etag=etag)
            path = url = None
            for user in res.json:
                followers.append(user)
                users.append({
                    'id': user['id'],
                    'login': user['login'],
                    'avatar_url': user['avatar_url'],
                    'gravatar_id': user['gravatar_id'],
                    'url': user['url']
                })
            link = self.__link_header_parse(res.headers['link'])
            if link != None and 'next' in link:
                url = link['next']
        self.__update('users', user_id,
            'ctx._source.follower_users = users', { 'users': users })
        return followers

    def followings(self, username, user_id):
        """Get followings list by username"""
        path = 'users/%s/following' % username
        url = None
        etag = None # TODO: applied
        followings = []
        users = []
        while path != None or url != None:
            debug('followings(%s) path=%s, url=%s' % (username, path, url))
            res = self.__get(path=path, url=url, etag=etag)
            path = url = None
            for user in res.json:
                followings.append(user)
                users.append({
                    'id': user['id'],
                    'login': user['login'],
                    'avatar_url': user['avatar_url'],
                    'gravatar_id': user['gravatar_id'],
                    'url': user['url']
                })
            link = self.__link_header_parse(res.headers['link'])
            if link != None and 'next' in link:
                url = link['next']
        self.__update('users', user_id,
            'ctx._source.following_users = users', { 'users': users })
        return followings

    def repos(self, username, user_id):
        """Get repos list by username"""
        path = 'users/%s/repos' % username
        url = None
        etag = None # TODO: applied
        repos = []
        users_repos = []
        while path != None or url != None:
            debug('repos(%s) path=%s, url=%s' % (username, path, url))
            res = self.__get(path=path, url=url, etag=etag)
            path = url = None
            for repo in res.json:
                self.__index('repos', repo['id'], repo)
                users_repos.append({
                    'id': repo['id'],
                    'name': repo['name'],
                    'fork': repo['fork'],
                    'description': repo['description'],
                    'language': repo['language']
                })
                repos.append(repo)
            link = self.__link_header_parse(res.headers['link'])
            if link != None and 'next' in link:
                url = link['next']
        self.__update('users', user_id, 'ctx._source.repos = repos', {
            'repos': users_repos
        })
        return repos
    
    def watchers(self, username, reponame, repo_id):
        """Get repo's watchers by username, reponame"""
        path = 'repos/%s/%s/subscribers' % (username, reponame)
        url = None
        etag = None # TODO: applied
        watchers = []
        while path != None or url != None:
            debug('watchers(%s) path=%s, url=%s' % (username, path, url))
            res = self.__get(path=path, url=url, etag=etag)
            path = url = None
            for user in res.json:
                watchers.append({
                    'id': user['id'],
                    'login': user['login'],
                    'avatar_url': user['avatar_url'],
                    'gravatar_id': user['gravatar_id'],
                    'url': user['url']
                })
            link = self.__link_header_parse(res.headers['link'])
            if link != None and 'next' in link:
                url = link['next']
        self.__update('repos', repo_id, 'ctx._source.subscribers = watchers', {
            'watchers': watchers
        })
        return watchers

    def stargazers(self, username, reponame, repo_id):
        """Get repo's stargazers by username, reponame"""
        path = 'repos/%s/%s/stargazers' % (username, reponame)
        url = None
        etag = None # TODO: applied
        stargazers = []
        while path != None or url != None:
            debug('stargazers(%s) path=%s, url=%s' % (username, path, url))
            res = self.__get(path=path, url=url, etag=etag)
            path = url = None
            for user in res.json:
                stargazers.append({
                    'id': user['id'],
                    'login': user['login'],
                    'avatar_url': user['avatar_url'],
                    'gravatar_id': user['gravatar_id'],
                    'url': user['url']
                })
            link = self.__link_header_parse(res.headers['link'])
            if link != None and 'next' in link:
                url = link['next']
        self.__update('repos', repo_id, 'ctx._source.stargazers = stargazers', {
            'stargazers': stargazers
        })
        return stargazers

    def pull_requests_cnt(self, username, reponame, repo_id):
        """Get repo's pull_requests by username, reponame"""
        path = 'repos/%s/%s/pulls?state=closed' % (username, reponame)
        url = None
        etag = None # TODO: applied
        pull_requests_cnt = {}
        result = []
        prs = []
        while path != None or url != None:
            debug('pull_requests(%s) path=%s, url=%s' % (username, path, url))
            res = self.__get(path=path, url=url, etag=etag)
            path = url = None
            for pr in res.json:
                if pr['head']['user'] == None:
                    print 'pass pr', username, reponame, pr['number']
                    continue
                head_owner_id = pr['head']['user']['id']
                prs.append({
                    'number': pr['number'],
                    'login': pr['head']['user']['login'],
                    'id': pr['head']['user']['id']
                })
                if head_owner_id not in pull_requests_cnt:
                    pull_requests_cnt[head_owner_id] = 0
                pull_requests_cnt[head_owner_id] += 1
            link = self.__link_header_parse(res.headers['link'])
            if link != None and 'next' in link:
                url = link['next']
        self.__update('repos', repo_id, 'ctx._source.pull_requests = prs', {
            'prs': prs
        })
        for head_owner_id in pull_requests_cnt:
            cnt = pull_requests_cnt[head_owner_id]
            result.append((head_owner_id, cnt))
        return result

    def crawl(self):
        """Crawling start"""
        cnt = 0
        while len(self.unvisited) > 0:
            username, depth = self.unvisited.popleft()

            if username in self.visited:
                continue

            # check visited
            self.visited.add(username)
            cnt += 1

            # my_user_id
            #user_id = self.user_id(username)
            user_dict = self.user(username)
            if user_dict == None:
                continue
            user_id = user_dict['id']

            # follower -> me. just append without logging
            if depth + 1 < self.MAXDEPTH:
                followers = self.followers(username, user_id)
            else:
                followers = []

            # me -> following
            if depth + 1 < self.MAXDEPTH:
                followings = self.followings(username, user_id)
            else:
                followings = []

            # my repos
            repos = self.repos(username, user_id)
            fork_repo_owner_ids = []
            pull_requests = []
            for repo in repos:
                if repo['fork']:
                    fork_repo_owner_ids.append(str(repo['owner']['id']))
                else:
                    # watcher write
                    watchers = self.watchers(username, repo['name'], repo['id'])
                    for watcher in watchers:
                        if watcher['id'] != repo['owner']['id']:
                            self.write(u'W|%d|%d' %
                                    (watcher['id'], repo['owner']['id']))

                    # stargazer write
                    stargazers = self.stargazers(username,
                        repo['name'], repo['id'])
                    for stargazer in stargazers:
                        if stargazer['id'] != repo['owner']['id']:
                            self.write(u'S|%d|%d' %
                                    (stargazer['id'], repo['owner']['id']))

                    # pull requests write
                    pull_requests_cnt = self.pull_requests_cnt(
                            username, repo['name'], repo['id'])
                    for tup in pull_requests_cnt:
                        self.write(u'P|%d|%d|%d' %
                                (repo['owner']['id'], tup[0], tup[1]))

            # write to file
            followings_id = ','.join([str(u['id']) for u in followings])
            fork_repo_owner_ids = ','.join(fork_repo_owner_ids)
            self.write(u'U|%d|%s|%s' %
                    (user_id, followings_id, fork_repo_owner_ids))

            # print progress
            print('[%s] username: %s, progress: %d, rate-limit: %s' %
                (strftime("%Y-%m-%d %H:%M:%S", localtime()), username, cnt,
                self.remaining_requests))
            self.es_conn.refresh()

            # append new users if not in visited
            if depth + 1 < self.MAXDEPTH:
                self.append(depth, [str(u['login']) for u in followers])
                self.append(depth, [str(u['login']) for u in followings])

    def append(self, depth, users):
        """Append users to unvisited list if not visited"""
        self.unvisited.extend((u, depth) for u in users
                              if u not in self.visited)

    def write(self, msg):
        """Write message to file"""
        if not self.out:
            self.out = open('gh.log', 'w') # truncate mode
        self.out.write(msg + '\n')

    def flush(self):
        if self.out:
            self.out.close()


if __name__ == '__main__':
    c = GitHubCrawler()
    try:
        c.crawl()
    except KeyboardInterrupt:
        c.flush()
        print 'exit with keyboard interuupt'
