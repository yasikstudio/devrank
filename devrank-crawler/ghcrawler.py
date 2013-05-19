#!/usr/bin/env python

import sys
import logging
from logging.handlers import RotatingFileHandler
import collections
import json
import requests
from requests.exceptions import HTTPError

from pygithub3 import Github

import config


class GitHubCrawler(object):
    """GitHub Crawler"""

    USERLIST = 'userlist.txt'
    MAXDEPTH = 5
    RETRY = 3

    def __init__(self, username, password):
        """Initializer for GitHubCrawler."""
        self.username = username
        self.password = password
        self.reconnect()
        self.visited = set()
        self.unvisited = collections.deque(self.userlist())
        self.out = None

    def reconnect(self):
        """Reconnect to GitHub login"""

        # using id and password
        #self.gh = Github(login=self.username, password=self.password)

        # using id and token
        token = self.request_token('user,public_repo',
                                   config.client_id, config.client_secret)
        self.gh = Github(login=self.username, token=token)

    def userlist(self):
        """Get users from file at first time"""
        f = open(self.USERLIST)
        users = [(u.strip(), 0) for u in f.readlines()
                 if u.strip() != '' and u.strip()[0:1] != '#']
        f.close()
        return users

    def followers(self, username):
        """Get followers list by username"""
        retry = self.RETRY
        while retry > 0:
            retry -= 1
            try:
                users = self.gh.users.followers.list(username).all()
                return [u.login for u in users]
            except HTTPError:
                self.reconnect()
        raise HTTPError('API failed')

    def followings(self, username):
        """Get followings list by username"""
        retry = self.RETRY
        while retry > 0:
            retry -= 1
            try:
                users = self.gh.users.followers.list_following(username).all()
                return [u.login for u in users]
            except HTTPError:
                self.reconnect()
        raise HTTPError('API failed')

    def crawl(self):
        """Crawling start"""
        cnt = 0
        while len(self.unvisited) > 0:
            user, depth = self.unvisited.popleft()

            if user in self.visited:
                continue

            # check visited
            self.visited.add(user)
            cnt += 1

            # follower -> me. just append without logging
            if depth + 1 < self.MAXDEPTH:
                followers = self.followers(user)
            else:
                followers = []

            # me -> following
            if depth + 1 < self.MAXDEPTH:
                followings = self.followings(user)
            else:
                followings = []

            # write to file
            links = ','.join(followings)
            self.write(u'%s,%s' % (user, links))

            # print progress
            if cnt % 100 == 0:
                print('progress: %d' % cnt)

            # append new users if not in visited
            if depth + 1 < self.MAXDEPTH:
                self.append(depth, followers)
                self.append(depth, followings)

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
        return result['token']

    def flush(self):
        if self.out:
            self.out.close()


if __name__ == '__main__':
    c = GitHubCrawler(config.username, config.password)
    try:
        c.crawl()
    except KeyboardInterrupt:
        c.flush()
        print 'exit with keyboard interuupt'
