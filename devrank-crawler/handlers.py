#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('../devrank-sqlclient')

from models import *
from client import *

import datetime

import config

def debug(str):
    if config.DEBUG:
        print(str)

class BaseHandler(object):

    MAX_TASK_TYPE = 5

    def __init__(self, crawler):
        self.crawler = crawler

    def queue(self, qu):
        s = self.crawler.db.makesession()
        q = s.query(TaskQueue).filter_by(login=qu.login, method=qu.method)
        if q.count() == 0:
            qu.task_type = min(qu.task_type, self.MAX_TASK_TYPE)
            s.add(qu)
            s.commit()
        s.close()

    def add_friendship(self, owner_id, friends_list):
        success = False
        while not success:
            try:
                debug("try add_friendship. %s, ..." % owner_id)
                s = self.crawler.db.makesession()
                already_list = s.query(Friendship).\
                                    filter_by(owner_id=owner_id).all()
                for fr in already_list:
                    if fr.friend_id in friends_list:
                        friends_list.remove(fr.friend_id)
                for fr in friends_list:
                    s.merge(Friendship(owner_id, fr))
                s.commit()
                s.close()
                success = True
            except:
                print traceback.format_exc()

    def add_friend_ownership(self, owners_list, friend_id):
        success = False
        while not success:
            try:
                debug("try add_friend_ownership. %s, ..." % friend_id)
                s = self.crawler.db.makesession()
                already_list = s.query(Friendship).\
                                    filter_by(friend_id=friend_id).all()
                for fr in already_list:
                    if fr.owner_id in owners_list:
                        owners_list.remove(fr.owner_id)
                for fr in owners_list:
                    s.merge(Friendship(fr, friend_id))
                s.commit()
                s.close()
                success = True
            except:
                print traceback.format_exc()

    def process(self, qu):
        pass


class UserHandler(BaseHandler):

    def process(self, qu):
        s = self.crawler.db.makesession()
        if qu.login != None:
            user = self.user(s, qu.login)
            if user == None:
                qu.completed_dt = datetime.datetime.utcnow()
                qu.success = False
                s.commit()
                s.close()
                return
            tasks = [
                ('followers', qu.task_type),
                ('followings', qu.task_type),
                ('repos', qu.task_type),
                ('orgs', qu.task_type)
            ]
            for method, task_type in tasks:
                new_qu = TaskQueue()
                new_qu = new_qu.from_dict({
                    'login': user.login,
                    'user_id': user.id,
                    'root_login': qu.root_login,
                    'task_type': task_type,
                    'method': method
                })
                self.queue(new_qu)
            qu.completed_dt = datetime.datetime.utcnow()
            qu.success = True
        else:
            qu.completed_dt = datetime.datetime.utcnow()
            qu.success = False
        s.commit()
        s.close()

    def user(self, session, username):
        """Get user by username"""
        etag = None
        user = User()
        q = session.query(User).filter_by(login=username)
        if q.count() == 1:
            user = q.first()
            etag = user.etag
        result = self.crawler.get(path='users/%s' % username, etag=etag)
        status_code = result.status_code
        if status_code == 304:
            debug('cached %s' % username)
        else:
            user_dict = result.json
            user_dict['ETag'] = result.headers['ETag']
            if user_dict['type'] == 'User':
                user = user.from_dict(user_dict)
                user.crawled_at = datetime.datetime.utcnow()
                session.merge(user)
            else:
                return None
        return user


class FollowerHandler(BaseHandler):

    def process(self, qu):
        s = self.crawler.db.makesession()
        if qu.login != None and qu.user_id != None:
            followers = self.followers(s, qu.login, qu.user_id)
            friend_owners = []
            for follower in followers:
                new_qu = TaskQueue()
                new_qu = new_qu.from_dict({
                    'login': follower['login'],
                    'user_id': follower['id'],
                    'root_login': qu.root_login,
                    'task_type': qu.task_type + 1,
                    'method': 'user'
                })
                self.queue(new_qu)
                # friendship flag
                #friend_owners.append(follower['id'])
                c = Friendship.__table__.insert(prefixes=['IGNORE'],
                    values=dict(owner_id=follower['id'], friend_id=qu.user_id))
                s.execute(c)
            #self.add_friend_ownership(friend_owners, qu.user_id)
            qu.completed_dt = datetime.datetime.utcnow()
            qu.success = True
        else:
            qu.completed_dt = datetime.datetime.utcnow()
            qu.success = False
        s.commit()
        s.close()

    def followers(self, session, username, user_id):
        """Get followers list by username"""
        path = 'users/%s/followers' % username
        url = link = None
        etag = None # TODO: applied
        followers = []
        users = []
        while path != None or url != None:
            debug('followers(%s) path=%s, url=%s' % (username, path, url))
            res = self.crawler.get(path=path, url=url, etag=etag)
            path = url = link = None
            if res.status_code == 200:
                for user in res.json:
                    followers.append(user)
                    c = Follower.__table__.insert(prefixes=['IGNORE'],
                            values=dict(src_id=user['id'], dest_id=user_id))
                    session.execute(c)
                link = self.crawler.link_header_parse(res.headers['link'])
            if link != None and 'next' in link:
                url = link['next']
        return followers


class FollowingHandler(BaseHandler):

    def process(self, qu):
        s = self.crawler.db.makesession()
        if qu.login != None and qu.user_id != None:
            followings = self.followings(s, qu.login, qu.user_id)
            friends = []
            for following in followings:
                new_qu = TaskQueue()
                new_qu = new_qu.from_dict({
                    'login': following['login'],
                    'user_id': following['id'],
                    'root_login': qu.root_login,
                    'task_type': qu.task_type + 1,
                    'method': 'user'
                })
                self.queue(new_qu)
                # friendship flag
                #friends.append(following['id'])
                c = Friendship.__table__.insert(prefixes=['IGNORE'],
                    values=dict(owner_id=qu.user_id, friend_id=follower['id']))
                s.execute(c)
            #self.add_friendship(qu.user_id, friends)
            qu.completed_dt = datetime.datetime.utcnow()
            qu.success = True
        else:
            qu.completed_dt = datetime.datetime.utcnow()
            qu.success = False
        s.commit()
        s.close()

    def followings(self, session, username, user_id):
        """Get followings list by username"""
        path = 'users/%s/following' % username
        url = link = None
        etag = None # TODO: applied
        followings = []
        users = []
        while path != None or url != None:
            debug('followings(%s) path=%s, url=%s' % (username, path, url))
            res = self.crawler.get(path=path, url=url, etag=etag)
            path = url = link = None
            if res.status_code == 200:
                for user in res.json:
                    c = Follower.__table__.insert(prefixes=['IGNORE'],
                            values=dict(src_id=user_id, dest_id=user['id']))
                    session.execute(c)
                link = self.crawler.link_header_parse(res.headers['link'])
            if link != None and 'next' in link:
                url = link['next']
        return followings


class RepoHandler(BaseHandler):

    def process(self, qu):
        s = self.crawler.db.makesession()
        if qu.login != None and qu.user_id != None:
            repos = self.repos(s, qu.login, qu.user_id)
            tasks = [
                ('watchers', qu.task_type),
                ('stargazers', qu.task_type),
                ('contributors', qu.task_type)
            ]
            for repo in repos:
                if repo.fork:
                    continue
                for method, task_type in tasks:
                    new_qu = TaskQueue()
                    new_qu = new_qu.from_dict({
                        'login': qu.login,
                        'user_id': qu.user_id,
                        'reponame': repo.name,
                        'repo_id': repo.id,
                        'root_login': qu.root_login,
                        'task_type': task_type,
                        'method': method
                    })
                    self.queue(new_qu)
            qu.completed_dt = datetime.datetime.utcnow()
            qu.success = True
        else:
            qu.completed_dt = datetime.datetime.utcnow()
            qu.success = False
        s.commit()
        s.close()

    def repos(self, session, username, user_id):
        """Get repos list by username"""
        path = 'users/%s/repos' % username
        url = link = None
        etag = None # TODO: applied
        repos = []
        users_repos = []
        while path != None or url != None:
            debug('repos(%s) path=%s, url=%s' % (username, path, url))
            res = self.crawler.get(path=path, url=url, etag=etag)
            path = url = link = None
            if res.status_code == 200:
                for repo in res.json:
                    repo_obj = Repo().from_dict(repo)
                    repo_obj.crawled_at = datetime.datetime.utcnow()
                    repo_obj.owner_id = user_id
                    if repo_obj.fork:
                        fork_owner_id = self.__fork(username, repo_obj.name)
                        if fork_owner_id != None:
                            repo_obj.fork_owner_id = fork_owner_id
                            session.merge(repo_obj)
                            repos.append(repo_obj)
                    else:
                        session.merge(repo_obj)
                        repos.append(repo_obj)
                link = self.crawler.link_header_parse(res.headers['link'])
            if link != None and 'next' in link:
                url = link['next']
        return repos

    def __fork(self, username, reponame):
        """Get repo's fork parent owner's id"""
        etag = None # TODO: applied

        debug('fork(%s, %s) path=%s' % (username, reponame,
                            'repos/%s/%s' % (username, reponame)))
        result = self.crawler.get(path='repos/%s/%s' % (username, reponame),
                                  etag=etag)
        status_code = result.status_code
        if status_code == 304:
            debug('cached %s/%s' % (username, reponame))
        elif status_code == 200:
            repo = result.json
            if 'parent' not in repo:
                return None
            return repo['parent']['owner']['id']
        else:
            # TODO: Error handling
            return None
        return None


class WatcherHandler(BaseHandler):

    def process(self, qu):
        s = self.crawler.db.makesession()
        if qu.login != None and qu.reponame != None and qu.repo_id != None:
            watchers = self.watchers(s, qu.login, qu.reponame, qu.repo_id)
            qu.completed_dt = datetime.datetime.utcnow()
            qu.success = True
        else:
            qu.completed_dt = datetime.datetime.utcnow()
            qu.success = False
        s.commit()
        s.close()

    def watchers(self, session, username, reponame, repo_id):
        """Get repo's watchers by username, reponame"""
        path = 'repos/%s/%s/subscribers' % (username, reponame)
        url = None
        etag = None # TODO: applied
        watchers = []
        while path != None or url != None:
            debug('watchers(%s) path=%s, url=%s' % (username, path, url))
            res = self.crawler.get(path=path, url=url, etag=etag)
            path = url = None
            for user in res.json:
                session.merge(Watcher(user['id'], repo_id))
                watchers.append(user)
            link = self.crawler.link_header_parse(res.headers['link'])
            if link != None and 'next' in link:
                url = link['next']
        return watchers


class StargazerHandler(BaseHandler):

    def process(self, qu):
        s = self.crawler.db.makesession()
        if qu.login != None and qu.reponame != None and qu.repo_id != None:
            stargazers = self.stargazers(s, qu.login, qu.reponame, qu.repo_id)
            qu.completed_dt = datetime.datetime.utcnow()
            qu.success = True
        else:
            qu.completed_dt = datetime.datetime.utcnow()
            qu.success = False
        s.commit()
        s.close()

    def stargazers(self, session, username, reponame, repo_id):
        """Get repo's stargazers by username, reponame"""
        path = 'repos/%s/%s/stargazers' % (username, reponame)
        url = None
        etag = None # TODO: applied
        stargazers = []
        while path != None or url != None:
            debug('stargazers(%s) path=%s, url=%s' % (username, path, url))
            res = self.crawler.get(path=path, url=url, etag=etag)
            path = url = None
            for user in res.json:
                session.merge(Stargazer(user['id'], repo_id))
                stargazers.append(user)
            link = self.crawler.link_header_parse(res.headers['link'])
            if link != None and 'next' in link:
                url = link['next']
        return stargazers


class ContributorHandler(BaseHandler):

    def process(self, qu):
        s = self.crawler.db.makesession()
        if qu.login != None and qu.reponame != None and qu.repo_id != None:
            contributors = self.contributors(s, qu.login,
                                             qu.reponame, qu.repo_id)
            friends = []
            friend_owners = []
            for contributor in contributors:
                new_qu = TaskQueue()
                new_qu = new_qu.from_dict({
                    'login': contributor['login'],
                    'user_id': contributor['id'],
                    'root_login': qu.root_login,
                    'task_type': qu.task_type + 1,
                    'method': 'user'
                })
                self.queue(new_qu)
                # friendship flag
                if contributor['id'] and qu.user_id != contributor['id']:
                    friends.append(contributor['id'])
                    friend_owners.append(contributor['id'])
            self.add_friendship(qu.user_id, friends)
            self.add_friend_ownership(friend_owners, qu.user_id)
            qu.completed_dt = datetime.datetime.utcnow()
            qu.success = True
        else:
            qu.completed_dt = datetime.datetime.utcnow()
            qu.success = False
        s.commit()
        s.close()

    def contributors(self, session, username, reponame, repo_id):
        """Get repo's contributors by username, reponame"""
        path = 'repos/%s/%s/contributors' % (username, reponame)
        etag = None # TODO: applied
        contributors = []
        debug('contributors(%s) path=%s' % (username, path))
        res = self.crawler.get(path=path, etag=etag)
        if res.status_code == 404:
            return []
        path = url = None
        for user in res.json:
            if username != user['login'] and user['type'] == 'User':
                session.merge(
                    Contributor(repo_id, user['id'], user['contributions']))
                contributors.append(user)
        return contributors


class OrganizationHandler(BaseHandler):

    def process(self, qu):
        s = self.crawler.db.makesession()
        if qu.login != None:
            orgs = self.orgs(qu.login)
            friends = []
            friend_owners = []
            for org in orgs:
                members = self.members(s, org['login'], org['id'])
                for member in members:
                    new_qu = TaskQueue()
                    new_qu = new_qu.from_dict({
                        'login': member['login'],
                        'user_id': member['id'],
                        'root_login': qu.root_login,
                        'task_type': qu.task_type + 1,
                        'method': 'user'
                    })
                    self.queue(new_qu)
                    # friendship flag
                    if member['id'] and qu.user_id != member['id']:
                        friends.append(contributor['id'])
                        friend_owners.append(contributor['id'])
            self.add_friendship(qu.user_id, friends)
            self.add_friend_ownership(friend_owners, qu.user_id)
            qu.completed_dt = datetime.datetime.utcnow()
            qu.success = True
        else:
            qu.completed_dt = datetime.datetime.utcnow()
            qu.success = False
        s.commit()
        s.close()

    def orgs(self, username):
        """Get organizations list by username"""
        path = 'users/%s/orgs' % username
        url = None
        etag = None # TODO: applied
        orgs = []
        while path != None or url != None:
            debug('orgs(%s) path=%s, url=%s' % (username, path, url))
            res = self.crawler.get(path=path, url=url, etag=etag)
            path = url = None
            for org in res.json:
                orgs.append(org)
            link = self.crawler.link_header_parse(res.headers['link'])
            if link != None and 'next' in link:
                url = link['next']
        return orgs

    def members(self, session, org_login, org_id):
        """Get org's members"""
        path = 'orgs/%s/members' % org_login
        etag = None # TODO: applied
        members = []
        debug('members(%s) path=%s' % (org_login, path))
        res = self.crawler.get(path=path, etag=etag)
        if res.status_code == 404:
            return []
        path = url = None
        for member in res.json:
            session.merge(Org(org_id, member['id']))
            members.append(member)
        return members

