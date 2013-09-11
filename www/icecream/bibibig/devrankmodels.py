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

    def get_gravatar_url(self, user):
        s = self.db.makesession()
        u = s.query(User).filter(User.login==user).first()
        return u and u.avatar_url or None

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
        my_avatar_url = self.get_gravatar_url(users[0])
        if my_avatar_url == None:
            return []

        # TODO not coded yet.
        """
        gravatar_url = {}
        gravatar_url[users[0]] = my_avatar_url
        links = []

        for user in users:
            avatar_url = self.get_gravatar_url(user)
            gravatar_url[user] = avatar_url

            ''' follower, following '''
            results = self.es.post(user_queryURI, data=user_queryDSL % user)
            for r in results['hits']['hits']:
                followings = r['_source']['following_users']
                for target in followings:
                    links.append({
                        "source": user,
                        "target": target['login'],
                        "gravatar_url": None,
                        "type": "type3"
                    })
                    gravatar_url[target['login']] = target['avatar_url']
                followers = r['_source']['follower_users']
                for source in followers:
                    links.append({
                        "source": source['login'],
                        "target": user,
                        "gravatar_url": None,
                        "type": "type3"
                    })
                    gravatar_url[source['login']] = source['avatar_url']

        for link in links:
            link['src_gravatar_url'] = gravatar_url[link['source']]
            link['tgt_gravatar_url'] = gravatar_url[link['target']]
        """

        return links
