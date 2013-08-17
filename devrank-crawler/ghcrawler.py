#!/usr/bin/env python

import sys
import logging
from logging.handlers import RotatingFileHandler
import collections
import json
import requests
import re
from requests.exceptions import HTTPError, ConnectionError
from pygithub3.exceptions import NotFound

from pygithub3 import Github
from pyes import *
from pyes.query import *

import config

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
        self.reconnect()
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
        raise HTTPError('API failed')

    def __link_header_parse(self, link_header):
        result = {}
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
        print 'toggle username : %s' % self.username

    def reconnect(self):
        """Reconnect to GitHub login"""

        # using id and password
        self.gh = Github(login=self.username, password=self.password)

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
        result_dict = result.json
        result_dict['ETag'] = result.headers['ETag']
        if status_code == 304:
            print 'cached %s' % username
            return user_dict
        user_dict = result_dict
        self.es_conn.index(user_dict,
            config.index_name, config.index_type, user_dict['id'])
        return user_dict

    def followers(self, username):
        """Get followers list by username"""
        retry = self.RETRY
        while retry > 0:
            retry -= 1
            try:
                users = self.gh.users.followers.list(username).all()
                return users
            except (HTTPError, ConnectionError) as e:
                self.reconnect()
        raise HTTPError('API failed')

    def __followers(self, username, user_id=None):
        # TODO: username convert to user_id
        pass

    def followings(self, username):
        """Get followings list by username"""
        retry = self.RETRY
        while retry > 0:
            retry -= 1
            try:
                users = self.gh.users.followers.list_following(username).all()
                return users
            except (HTTPError, ConnectionError) as e:
                self.reconnect()
        raise HTTPError('API failed')

    def repos(self, username):
        """Get repos list by username"""
        retry = self.RETRY
        while retry > 0:
            retry -= 1
            try:
                repos = self.gh.repos.list(username).all()
                return repos
            except (HTTPError, ConnectionError) as e:
                self.reconnect()
        raise HTTPError('API failed')
    
    def watchers(self, username, reponame):
        """Get repo's watchers by username, reponame"""
        retry = self.RETRY
        while retry > 0:
            retry -= 1
            try:
                users = self.gh.repos.watchers.list(username, reponame).all()
                return users
            except (HTTPError, ConnectionError) as e:
                self.reconnect()
            except NotFound:
                return []
        raise HTTPError('API failed')

    def pull_requests_cnt(self, username, reponame):
        """Get repo's watchers by username, reponame"""
        retry = self.RETRY
        while retry > 0:
            retry -= 1
            try:
                pull_requests = self.gh.pull_requests.list(
                        state='closed', user=username, repo=reponame).all()
                pull_requests_cnt = {}
                result = []
                for pr in pull_requests:
                    if pr.head['user'] == None:
                        print username, reponame, pr.number
                        continue
                    head_owner_id = pr.head['user']['id']
                    if head_owner_id not in pull_requests_cnt:
                        pull_requests_cnt[head_owner_id] = 0
                    pull_requests_cnt[head_owner_id] += 1
                for head_owner_id in pull_requests_cnt:
                    cnt = pull_requests_cnt[head_owner_id]
                    result.append((head_owner_id, cnt))
                return result
            except (HTTPError, ConnectionError) as e:
                self.reconnect()
            except NotFound:
                return []
        raise HTTPError('API failed')

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
                followers = self.followers(username)
            else:
                followers = []

            # me -> following
            if depth + 1 < self.MAXDEPTH:
                followings = self.followings(username)
            else:
                followings = []

            # my repos
            repos = self.repos(username)
            fork_repo_owner_ids = []
            pull_requests = []
            for repo in repos:
                if repo.fork:
                    fork_repo_owner_ids.append(str(repo.owner.id))
                else:
                    # watcher write
                    watchers = self.watchers(username, repo.name)
                    for watcher in watchers:
                        if watcher.id != repo.owner.id:
                            self.write(u'W|%d|%d' %
                                    (watcher.id, repo.owner.id))

                    # pull requests write
                    pull_requests_cnt = self.pull_requests_cnt(
                            username, repo.name)
                    for tup in pull_requests_cnt:
                        self.write(u'P|%d|%d|%d' %
                                (repo.owner.id, tup[0], tup[1]))

            # write to file
            followings_id = ','.join([str(u.id) for u in followings])
            fork_repo_owner_ids = ','.join(fork_repo_owner_ids)
            self.write(u'U|%d|%s|%s' %
                    (user_id, followings_id, fork_repo_owner_ids))

            # print progress
            if cnt % 10 == 0:
                print('progress: %d, rate-limit: %s' %
                        (cnt, self.gh.remaining_requests))

            # append new users if not in visited
            if depth + 1 < self.MAXDEPTH:
                self.append(depth, [str(u.login) for u in followers])
                self.append(depth, [str(u.login) for u in followings])

    def append(self, depth, users):
        """Append users to unvisited list if not visited"""
        self.unvisited.extend((u, depth) for u in users
                              if u not in self.visited)

    def write(self, msg):
        """Write message to file"""
        if not self.out:
            self.out = open('gh.log', 'w') # truncate mode
        self.out.write(msg + '\n')

    def request_token(self, scopes, client_id, client_secret):
        """GitHub access token request."""
        authorizations_request_url = 'https://api.github.com/authorizations'
        scope_dicts = scopes.split(',')
        params = {
            'note': 'github_token_requestor',
            'scopes': scope_dicts,
            'client_id': client_id,
            'client_secret': client_secret
        }
        r = requests.post(authorizations_request_url,
                          auth=(self.username, self.password),
                          data=json.dumps(params))
        result = r.json
        if 'token' in result:
            return result['token']
        else:
            print('API rate limit exceeded for %s' % self.username)
            raise KeyboardInterrupt

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
