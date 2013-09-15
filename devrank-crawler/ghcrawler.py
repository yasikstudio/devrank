#!/usr/bin/env python

import logging
from logging.handlers import RotatingFileHandler

import os
import sys
sys.path.append('../devrank-sqlclient')

import collections, json, re

import requests
from requests.exceptions import HTTPError, ConnectionError

import datetime
from time import localtime, strftime, sleep

from models import *
from client import *

import config

def debug(str):
    if config.DEBUG:
        print(str)

class GitHubCrawler(object):
    """GitHub Crawler"""

    RETRY = 3
    MAX_TASK_TYPE = 5

    def __init__(self, crawler_id):
        """Initializer for GitHubCrawler."""
        self.crawler_id = crawler_id
        self.usernames = config.usernames
        self.password = config.password
        self.username_idx = 0
        self.username = self.usernames[0]
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
        etag = None
        user_dict = {}
        user = User()
        crawled_at = None

        s = self.db.makesession()
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
                s = self.db.makesession()
                s.merge(user)
                s.commit()
        s.close()
        if user_dict['type'] == 'User':
            return user
        return None

    def followers(self, username, user_id):
        """Get followers list by username"""
        path = 'users/%s/followers' % username
        url = None
        etag = None # TODO: applied
        followers = []
        users = []
        s = self.db.makesession()
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
        s.close()
        return followers

    def followings(self, username, user_id):
        """Get followings list by username"""
        path = 'users/%s/following' % username
        url = None
        etag = None # TODO: applied
        followings = []
        users = []
        s = self.db.makesession()
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
        s.close()
        return followings

    def repos(self, username, user_id):
        """Get repos list by username"""
        path = 'users/%s/repos' % username
        url = None
        etag = None # TODO: applied
        repos = []
        users_repos = []
        s = self.db.makesession()
        while path != None or url != None:
            debug('repos(%s) path=%s, url=%s' % (username, path, url))
            res = self.__get(path=path, url=url, etag=etag)
            path = url = None
            for repo in res.json:
                repo_obj = Repo().from_dict(repo)
                repo_obj.crawled_at = datetime.datetime.utcnow()
                repo_obj.owner_id = user_id
                if repo_obj.fork:
                    fork_owner_id = self.fork(username, repo_obj.name)
                    repo_obj.fork_owner_id = fork_owner_id
                s.merge(repo_obj)
                repos.append(repo)
            link = self.__link_header_parse(res.headers['link'])
            if link != None and 'next' in link:
                url = link['next']
        s.commit()
        s.close()
        return repos

    def fork(self, username, reponame):
        """Get repo's fork parent owner's id"""
        etag = None # TODO: applied

        result = self.__get(path='repos/%s/%s' % (username, reponame),
                            etag=etag)
        status_code = result.status_code
        if status_code == 304:
            debug('cached %s/%s' % (username, reponame))
        elif status_code == 200:
            repo = result.json
            return repo['parent']['owner']['id']
        else:
            # TODO: Error handling
            return None
        return None
    
    def watchers(self, username, reponame, repo_id):
        """Get repo's watchers by username, reponame"""
        path = 'repos/%s/%s/subscribers' % (username, reponame)
        url = None
        etag = None # TODO: applied
        watchers = []
        s = self.db.makesession()
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
        s.close()
        return watchers

    def stargazers(self, username, reponame, repo_id):
        """Get repo's stargazers by username, reponame"""
        path = 'repos/%s/%s/stargazers' % (username, reponame)
        url = None
        etag = None # TODO: applied
        stargazers = []
        s = self.db.makesession()
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
        s.close()
        return stargazers

    def contributors(self, username, reponame, repo_id):
        """Get repo's contributors by username, reponame"""
        path = 'repos/%s/%s/contributors' % (username, reponame)
        url = None
        etag = None # TODO: applied
        contributors = []
        debug('contributors(%s) path=%s, url=%s' % (username, path, url))
        res = self.__get(path=path, url=url, etag=etag)
        if res.status_code == 404:
            return []
        path = url = None
        s = self.db.makesession()
        for user in res.json:
            if username != user['login']:
                s.merge(Contributor(repo_id, user['id'], user['contributions']))
                contributors.append(user)
        s.commit()
        s.close()
        return contributors

    def dequeue(self):
        while True:
            s = self.db.makesession()
            select_qry = '''
            SELECT
                Q.login,
                CASE WHEN Q.task_type IN (2, 3, 4) THEN 3
                     ELSE Q.task_type
                END AS `qtype`,
                Q.task_type
            FROM queue AS Q
            WHERE Q.assignee IS NULL
            ORDER BY qtype, Q.task_id
            LIMIT 1
            '''
            result = s.execute(select_qry)
            row = result.fetchone()
            if row == None:
                return (None, None)

            login = row['login']
            task_type = row['task_type']

            update_qry = '''
            UPDATE queue SET
                assignee = :assignee,
                assigned_dt = now()
            WHERE
                    login = :login
                AND assignee IS NULL
            '''
            result = s.execute(update_qry, {
                'assignee': self.crawler_id,
                'login': login
            })
            if result.rowcount != 1:
                sleep(1)
                continue
            s.commit()
            s.close()
            return (login, task_type)

    def queue(self, username, depth):
        s = self.db.makesession()
        s.add(TaskQueue(username, depth))
        s.commit()
        s.close()

    def crawl(self):
        """Crawling start"""
        cnt = 0
        while True:
            username, task_type = self.dequeue()
            if username == None:
                sleep(config.CRAWLER_IDLE_TIME)
                continue

            cnt += 1

            # my_user_id
            user = self.user(username)
            if user == None:
                continue
            user_id = user.id

            # followers / followings
            followers = self.followers(username, user_id)
            followings = self.followings(username, user_id)

            # my repos
            repos = self.repos(username, user_id)
            contributions = []
            for repo in repos:
                if not repo['fork']:
                    watchers = self.watchers(username, repo['name'], repo['id'])
                    stargazers = self.stargazers(username,
                        repo['name'], repo['id'])
                    contributions = self.contributors(
                            username, repo['name'], repo['id'])

            # print progress
            print('[%s] username: %s, progress: %d, rate-limit: %s' %
                (strftime("%Y-%m-%d %H:%M:%S", localtime()), username, cnt,
                self.remaining_requests))

            # append new users if not in visited
            next_task_type = min(task_type + 1, self.MAX_TASK_TYPE)
            self.append(next_task_type, [str(u['login']) for u in followers])
            self.append(next_task_type, [str(u['login']) for u in followings])

            # TODO: add org's members
            # TODO: friendship flag

    def append(self, task_type, users):
        """Append users to unvisited list if not visited"""
        for u in users:
            s = self.db.makesession()
            q = s.query(TaskQueue).filter_by(login=u)
            if q.count() == 0:
                s.add(TaskQueue(u, task_type))
                s.commit()
            s.close()

if __name__ == '__main__':
    hostname = os.uname()[1]
    pid = os.getpid()
    ghcrawler_id = 'gh_%s_%s' % (hostname.replace('.', '_'), pid)
    c = GitHubCrawler(ghcrawler_id)
    try:
        c.crawl()
    except KeyboardInterrupt:
        c.flush()
        print 'exit with keyboard interuupt'
