import icecream.settings

import sys
sys.path.append('../devrank-sqlclient')

from models import *
from client import *


class DevRankModel(object):
    def __init__(self):
        self.db = DevRankDB(settings.SQLALCHEMY)
        self.db.connect()
        pass
    def get_gravatar_url(self, user):
        pass
    def search(self, query):
        s = self.db.makesession()
        return s.query(User).all()
    def social_search(self, users):
        pass
