import icecream.settings

import sys
sys.path.append('../devrank-sqlclient')

from sqlalchemy import or_
from models import *
from client import *


class DevRankModel(object):
    def __init__(self):
        self.db = DevRankDB(settings.SQLALCHEMY)
        self.db.connect()

    def get_gravatar_url(self, user):
        s = self.db.makesession()
        u = s.query(User).filter(User.login==user).first()
        return u and u.avatar_url or None

    def search(self, query):
        s = self.db.makesession()
        likequery = '%%%s%%' % query
        q = s.query(User).join(Repo, User.id == Repo.owner_id) \
             .filter(or_(Repo.description.like(likequery), \
                         Repo.language.like(likequery))) \
             .order_by(User.devrank_score.desc()) \
             .limit(20) \
             .all()
        return q

    def social_search(self, users):
        # TODO
        pass
