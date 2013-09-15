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


def dump(s, f):
    # iterate all users
    for me in s.query(User):
        # U|uid|follow_id1,follow_id2,follow_id3|fork_id4,fork_id5,fork_id6
        rs = s.query(Follower.dest_id).filter(Follower.src_id == me.id)
        followings = ','.join(str(x[0]) for x in rs)
        rs = s.query(Repo.fork_owner_id) \
              .filter(and_(Repo.fork_owner_id == me.id, Repo.fork == True))
        repos = ','.join(str(x[0]) for x in rs)
        f.write('U|%s|%s|%s\n' % (me.id, followings, repos))

        # P|uid|owner_uid|count
        rs = s.query(User, Repo, Contributor) \
              .filter(and_(User.id == Repo.owner_id, \
                           Repo.id == Contributor.repo_id, \
                           Contributor.contributor_id == me.id))
        for u, r, c in rs:
            f.write('P|%s|%s|%s\n' % (me.id, u.id, c.contributions))

        # S|uid|owner_uid
        rs = s.query(User, Repo, Stargazer) \
              .filter(and_(User.id == Repo.owner_id, \
                           Repo.id == Stargazer.repo_id, \
                           Stargazer.stargazer_id == me.id))
        for u, r, star in rs:
            f.write('S|%s|%s\n' % (me.id, u.id))

        # W|uid|owner_uid
        rs = s.query(User, Repo, Watcher) \
              .filter(and_(User.id == Repo.owner_id, \
                           Repo.id == Watcher.repo_id, \
                           Watcher.watcher_id == me.id))
        for u, r, w in rs:
            f.write('W|%s|%s\n' % (me.id, u.id))


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
                s.query(User).update({'devrank_score': score})
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
