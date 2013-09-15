#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
        self.session = sessionmaker(bind=self.engine)

    def connect(self):
        return self.engine.connect()

    def makesession(self):
        return self.session()

    def close(self):
        pass
