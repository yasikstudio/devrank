#!/usr/bin/env python

import sys
import logging
from logging.handlers import RotatingFileHandler
import collections
import json
import requests
from requests.exceptions import HTTPError, ConnectionError
from pygithub3.exceptions import NotFound

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

    def user_id(self, username):
        """Get user_id by username"""
        retry = self.RETRY
        while retry > 0:
            retry -= 1
            try:
                user = self.gh.users.get(username)
                if user.type == 'User':
                    return user.id
                return None
            except (HTTPError, ConnectionError) as e:
                self.reconnect()
        raise HTTPError('API failed')

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
            user, depth = self.unvisited.popleft()

            if user in self.visited:
                continue

            # check visited
            self.visited.add(user)
            cnt += 1

            # my_user_id
            user_id = self.user_id(user)
            if user_id == None:
                continue

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

            # my repos
            repos = self.repos(user)
            fork_repos = []
            pull_requests = []
            for repo in repos:
                if repo.fork:
                    fork_repos.append(str(repo.id))
                else:
                    # watcher write
                    watchers = self.watchers(user, repo.name)
                    for watcher in watchers:
                        self.write(u'W|%d|%d' % (watcher.id, repo.id))

                    # pull requests write
                    pull_requests_cnt = self.pull_requests_cnt(user, repo.name)
                    for tup in pull_requests_cnt:
                        self.write(u'P|%d|%d|%d' % (tup[0], repo.id, tup[1]))

            # write to file
            followers_id = ','.join([str(u.id) for u in followers])
            fork_repos = ','.join(fork_repos)
            self.write(u'U|%d|%s|%s' % (user_id, followers_id, fork_repos))

            # print progress
            if cnt % 100 == 0:
                print('progress: %d' % cnt)

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
            print 'API rate limit exceeded for %s' % self.username
            raise KeyboardInterrupt

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
