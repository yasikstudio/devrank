#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import *

from time import sleep

class DevRankDB(object):

    def __init__(self, conn_string):
        self.engine = create_engine(conn_string)

        User.metadata.create_all(self.engine)
        Follower.metadata.create_all(self.engine)
        Friendship.metadata.create_all(self.engine)
        Repo.metadata.create_all(self.engine)
        Watcher.metadata.create_all(self.engine)
        Stargazer.metadata.create_all(self.engine)
        Contributor.metadata.create_all(self.engine)
        Org.metadata.create_all(self.engine)
        TaskQueue.metadata.create_all(self.engine)
        Member.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine,    \
                                        autoflush = False, \
                                        autocommit = False)

    def connect(self):
        return self.engine.connect()

    def makesession(self):
        return self.session()

    def close(self):
        pass


def usage():
    print('./client.py [get|put] [file]')
    sys.exit(-1)


def sumof(d):
    '''d = ((1, 456), (1, 1), ...))'''
    data = {}
    for k, v in d:
        if k in data:
            data[k] += v
        else:
            data[k] = v
    return ','.join('%s:%d' % (k, v) for k, v in data.items())


def dump(s, f):
    # iterate all users
    for me in s.query(User):
        # U|uid|follow_id1,follow_id2,follow_id3|fork_id4,fork_id5,fork_id6

        rs = s.query(Follower.dest_id).filter(Follower.src_id == me.id)
        followings = sumof((str(x[0]), 1) for x in rs)

        rs = s.query(Repo.fork_owner_id) \
              .filter(and_(Repo.fork_owner_id == me.id, Repo.fork == True))
        forked_repos = sumof((str(x[0]), 1) for x in rs)

        # P|uid|owner_uid|count
        rs = s.query(User, Repo, Contributor) \
              .filter(and_(User.id == Repo.owner_id, \
                           Repo.id == Contributor.repo_id, \
                           Contributor.contributor_id == me.id))
        pulls = sumof((u.id, c.contributions) for u, r, c in rs)

        # S|uid|owner_uid
        rs = s.query(User, Repo, Stargazer) \
              .filter(and_(User.id == Repo.owner_id, \
                           Repo.id == Stargazer.repo_id, \
                           Stargazer.stargazer_id == me.id))
        stars = sumof((u.id, 1) for u, r, star in rs)

        # W|uid|owner_uid
        rs = s.query(User, Repo, Watcher) \
              .filter(and_(User.id == Repo.owner_id, \
                           Repo.id == Watcher.repo_id, \
                           Watcher.watcher_id == me.id))
        watches = sumof((u.id, 1) for u, r, w in rs)

        f.write('%s|true|%s|%s|%s|%s|%s\n' % (me.id, followings, forked_repos,
                                            pulls, stars, watches))


def update_score(s, f):
    try:
        count = 0
        while True:
            line = f.readline()
            if line == '':
                break
            uid, exists, score = line.strip().split(',')
            if exists == 'true':
                score = float(score)
                s.query(User).filter(User.id == uid).update({'devrank_score': score})
                count += 1
                if count % 100 == 0:
                    print('%d rows updated' % count)
        s.commit()
        print('Updating %d rows completed.' % count)
    except:
        s.rollback()
        print('Rollbacked.')
        raise


if __name__ == '__main__':
    if len(sys.argv) != 3:
        usage()

    _, method, filename = sys.argv
    if method not in ('get', 'put'):
        usage()

    from config import DB_CONN_STRING
    db = DevRankDB(DB_CONN_STRING)
    db.connect()
    s = db.makesession()

    if method == 'get':
        f = open(filename, 'w')
        dump(s, f)
        f.close()
    elif method == 'put':
        f = open(filename, 'r')
        update_score(s, f)
        f.close()
