#!/usr/bin/env python

import logging
from logging.handlers import RotatingFileHandler

import sys
sys.path.append('../devrank-sqlclient')

import collections, json, re

import requests
from requests.exceptions import HTTPError, ConnectionError

import datetime
from time import localtime, strftime

from models import *
from client import *

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
        self.remaining_requests = 0
        self.db = DevRankDB(config.DB_CONN_STRING)
        self.db.connect()

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
                elif result.status_code == 404:
                    # Not Found
                    return result
                else:
                    print result.status_code
                    print result.json
                    raise HTTPError('API failed. unexpected')
            except (HTTPError, ConnectionError) as e:
                print 'HTTPError. retry...'
                print url, path
        raise HTTPError('API failed')

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
        s = self.db.makesession()

        etag = None
        user_dict = {}
        user = User()
        crawled_at = None

        q = s.query(User).filter_by(login=username)
        if q.count() == 1:
            user = q.first()
            for column in user.columns():
                user_dict[column] = getattr(user, column)
            etag = user.etag
            user_dict['type'] = 'User'
        result = self.__get(path='users/%s' % username, etag=etag)
        status_code = result.status_code
        if status_code == 304:
            debug('cached %s' % username)
        else:
            user_dict = result.json
            user_dict['ETag'] = result.headers['ETag']
            if user_dict['type'] == 'User':
                user = user.from_dict(user_dict)
                user.crawled_at = datetime.datetime.utcnow()
                user = s.merge(user)
                s.commit()
        if user_dict['type'] == 'User':
            return user
        return None

    def followers(self, username, user_id):
        """Get followers list by username"""
        s = self.db.makesession()
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
                s.merge(Follower(user['id'], user_id))
            link = self.__link_header_parse(res.headers['link'])
            if link != None and 'next' in link:
                url = link['next']
        s.commit()
        return followers

    def followings(self, username, user_id):
        """Get followings list by username"""
        s = self.db.makesession()
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
                s.merge(Follower(user_id, user['id']))
            link = self.__link_header_parse(res.headers['link'])
            if link != None and 'next' in link:
                url = link['next']
        s.commit()
        return followings

    def repos(self, username, user_id):
        """Get repos list by username"""
        s = self.db.makesession()
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
                repo_obj = Repo().from_dict(repo)
                repo_obj.crawled_at = datetime.datetime.utcnow()
                repo_obj.owner_id = user_id
                s.merge(repo_obj)
                repos.append(repo)
            link = self.__link_header_parse(res.headers['link'])
            if link != None and 'next' in link:
                url = link['next']
        s.commit()
        return repos
    
    def watchers(self, username, reponame, repo_id):
        """Get repo's watchers by username, reponame"""
        s = self.db.makesession()
        path = 'repos/%s/%s/subscribers' % (username, reponame)
        url = None
        etag = None # TODO: applied
        watchers = []
        while path != None or url != None:
            debug('watchers(%s) path=%s, url=%s' % (username, path, url))
            res = self.__get(path=path, url=url, etag=etag)
            path = url = None
            for user in res.json:
                s.merge(Watcher(user['id'], repo_id))
                watchers.append(user)
            link = self.__link_header_parse(res.headers['link'])
            if link != None and 'next' in link:
                url = link['next']
        s.commit()
        return watchers

    def stargazers(self, username, reponame, repo_id):
        """Get repo's stargazers by username, reponame"""
        s = self.db.makesession()
        path = 'repos/%s/%s/stargazers' % (username, reponame)
        url = None
        etag = None # TODO: applied
        stargazers = []
        while path != None or url != None:
            debug('stargazers(%s) path=%s, url=%s' % (username, path, url))
            res = self.__get(path=path, url=url, etag=etag)
            path = url = None
            for user in res.json:
                s.merge(Stargazer(user['id'], repo_id))
                stargazers.append(user)
            link = self.__link_header_parse(res.headers['link'])
            if link != None and 'next' in link:
                url = link['next']
        s.commit()
        return stargazers

    def contributors(self, username, reponame, repo_id):
        """Get repo's contributors by username, reponame"""
        s = self.db.makesession()
        path = 'repos/%s/%s/contributors' % (username, reponame)
        url = None
        etag = None # TODO: applied
        contributors = []
        debug('contributors(%s) path=%s, url=%s' % (username, path, url))
        res = self.__get(path=path, url=url, etag=etag)
        if res.status_code == 404:
            return []
        path = url = None
        for user in res.json:
            if username != user['login']:
                s.merge(Contributor(repo_id, user['id'], user['contributions']))
                contributors.append(user)
        s.commit()
        return contributors

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
            user = self.user(username)
            if user == None:
                continue
            user_id = user.id

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
            contributions = []
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

                    # contributions write
                    contributions = self.contributors(
                            username, repo['name'], repo['id'])
                    for cont in contributions:
                        self.write(u'P|%d|%d|%d' %
                                (repo['owner']['id'], cont['id'],
                                 cont['contributions']))

            # write to file
            followings_id = ','.join([str(u['id']) for u in followings])
            fork_repo_owner_ids = ','.join(fork_repo_owner_ids)
            self.write(u'U|%d|%s|%s' %
                    (user_id, followings_id, fork_repo_owner_ids))

            # print progress
            print('[%s] username: %s, progress: %d, rate-limit: %s' %
                (strftime("%Y-%m-%d %H:%M:%S", localtime()), username, cnt,
                self.remaining_requests))

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
