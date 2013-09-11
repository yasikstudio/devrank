from icecream.settings import SQLALCHEMY

import sys
sys.path.append('../devrank-sqlclient')

from sqlalchemy import or_
from models import *
from client import *


class DevRankModel(object):
    def __init__(self):
        self.db = DevRankDB(SQLALCHEMY)
        self.db.connect()

    def _get_gravatar_url(self, session, user):
        u = session.query(User).filter(User.login==user).first()
        return u and u.avatar_url or None

    def _get_users_by_login(self, session, users):
        '''[ (login, id, avatar_url), (login, id, avatar_url) ... ]'''
        return session.query(User.login, User.id, User.avatar_url) \
                      .filter(User.login.in_(users)).all()

    def _get_followings(self, session, users):
        return session.query(Follower) \
                      .join(User, or_(User.id == Follower.src_id, \
                                      User.id == Follower.dest_id)) \
                      .filter(User.login.in_(users)).all()

    def search(self, query):
        s = self.db.makesession()
        likequery = '%%%s%%' % query
        users = s.query(User).join(Repo, User.id == Repo.owner_id) \
                 .filter(or_(Repo.description.like(likequery), \
                             Repo.language.like(likequery))) \
                 .order_by(User.devrank_score.desc()) \
                 .limit(20) \
                 .all()
        for u in users:
            if u.devrank_score:
                u.devrank_score *= 1000000
            else:
                u.devrank_score = 0
            u.public_repos = self._get_repos_count(s, u.id)
            u.followers = self._get_followers_count(s, u.id)
            u.following = self._get_following_count(s, u.id)
        return users

    def _get_repos_count(self, session, login_id):
        return session.query(func.count(Repo.id)) \
                      .filter(Repo.owner_id == login_id).scalar()

    def _get_following_count(self, session, login_id):
        return session.query(func.count(Follower.dest_id)) \
                      .filter(Follower.src_id == login_id).scalar()

    def _get_followers_count(self, session, login_id):
        return session.query(func.count(Follower.src_id)) \
                      .filter(Follower.dest_id == login_id).scalar()

    def social_search(self, users):
        s = self.db.makesession()

        if len(users) == 0:
            return []

        matchedusers = self._get_users_by_login(s, users)
        gravatars = dict((x[0], x[2]) for x in matchedusers)
        id_to_login = dict((x[1], x[0]) for x in matchedusers)
        followings = self._get_followings(s, users)

        links = []
        for f in followings:
            if (f.src_id in id_to_login) and (f.dest_id in id_to_login):
                login_src = id_to_login[f.src_id]
                login_dest = id_to_login[f.dest_id]
                if (login_src in gravatars) and (login_dest in gravatars):
                    links.append({'source': login_src,
                                  'target': login_dest,
                                  'src_gravatar_url': gravatars[login_src],
                                  'tgt_gravatar_url': gravatars[login_dest],
                                  'type': 'type3'})
                else:
                    # TODO check this problem..
                    print('No gravatar: %s or %s' % (login_src, login_dest))
            else:
                # TODO check this problem..
                print('No id_to_login: %s or %s' % (f.src_id, f.dest_id))
        return links
