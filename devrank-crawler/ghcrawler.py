#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

from handlers import *

import config

def debug(str):
    if config.DEBUG:
        print(str)

class GitHubCrawler(object):
    """GitHub Crawler"""

    RETRY = 3

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
        self.handlers = {
            'user': UserHandler(self),
            'followers': FollowerHandler(self),
            'followings': FollowingHandler(self),
            'repos': RepoHandler(self),
            'watchers': WatcherHandler(self),
            'stargazers': StargazerHandler(self),
            'contributors': ContributorHandler(self)
        }

    def get(self, url=None, path=None, etag=None):
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
                    self.__toggle_username()
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

    def link_header_parse(self, link_header):
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

    def __toggle_username(self):
        self.username_idx += 1
        self.username_idx %= len(self.username)
        self.username = self.usernames[self.username_idx]
        debug('toggle username : %s' % self.username)
    
    def dequeue(self, session):
        while True:
            select_qry = '''
            SELECT
                Q.task_id,
                Q.login, Q.user_id, Q.reponame, Q.repo_id,
                Q.root_login, Q.task_type, Q.method,
                Q.assignee, Q.assigned_dt, Q.completed_dt, Q.success,
                CASE WHEN Q.task_type IN (2, 3, 4) THEN 3
                     ELSE Q.task_type
                END AS `qtype`
            FROM queue AS Q
            WHERE Q.assignee IS NULL
            ORDER BY qtype, Q.task_id
            LIMIT 1
            '''
            qu = session.query(TaskQueue).from_statement(select_qry).first()
            if qu == None:
                return None

            update_qry = '''
            UPDATE queue SET
                assignee = :assignee,
                assigned_dt = now()
            WHERE
                    login = :login
                AND method = :method
                AND assignee IS NULL
            '''
            result = session.execute(update_qry, {
                'assignee': self.crawler_id,
                'login': qu.login,
                'method': qu.method
            })
            if result.rowcount != 1:
                sleep(1)
                continue
            session.commit()
            return qu

    def crawl(self):
        """Crawling start"""
        while True:
            s = self.db.makesession()
            qu = self.dequeue(s)
            if qu == None:
                sleep(config.CRAWLER_IDLE_TIME)
                continue

            username = qu.login
            method = qu.method

            handler = self.handlers[qu.method]
            handler.process(qu)

            s.merge(qu)
            s.commit()
            s.close()

            # print progress
            print('[%s] username: %s, method: %s, rate-limit: %s' %
                (strftime("%Y-%m-%d %H:%M:%S", localtime()), username,
                    method, self.remaining_requests))

            # TODO: add org's members

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
