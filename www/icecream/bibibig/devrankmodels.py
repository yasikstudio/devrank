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

    def get_user_id(self, login):
        s = self.db.makesession()
        user = s.query(User).filter_by(login=login).first()
        if user == None:
            return None
        return user.id

    def search(self, query, me_id=None, page=1, page_per_row=20):
        # TODO search using query and me.
        if me_id == None:
            return self.__search_global(query)
        search_sql = u'''
select distinct * from
(
    select
        distinct u.*
    from friend_relation fr
    inner join users u on fr.dest_id = u.id
    inner join repos r on u.id = r.owner_id
    where src_id = :id
    :where_clause_qry
    # 3-depth
    union all
    select
        distinct u.*
    from friend_relation fr1
    inner join friend_relation fr2 on fr1.dest_id = fr2.src_id
    inner join users u on fr2.dest_id = u.id
    inner join repos r on u.id = r.owner_id
    where fr1.src_id = :id
    :where_clause_qry
    # 4-depth
    union all
    select
        distinct u.*
    from friend_relation fr1
    inner join friend_relation fr2 on fr1.dest_id = fr2.src_id
    inner join friend_relation fr3 on fr2.dest_id = fr3.src_id
    inner join users u on fr3.dest_id = u.id
    inner join repos r on u.id = r.owner_id
    where fr1.src_id = :id
    :where_clause_qry
    order by devrank_score desc
) friends
limit :limit_clause
        '''
        limit_clause = '%d, %d' % ((page - 1) * page_per_row, page_per_row)
        where_clause_qry = '''
            and (r.description like ':like_qry'
            or r.language like ':like_qry'
            or u.location like ':like_qry'
            or u.login like ':like_qry'
            or u.name like ':like_qry')
        '''.replace(':like_qry', '%%%s%%' % query)
        sql = search_sql.replace(':where_clause_qry', where_clause_qry) \
                        .replace(':limit_clause', limit_clause)
        s = self.db.makesession()
        users = s.query(User).from_statement(sql) \
                       .params(id=me_id).all()
        for u in users:
            if u.devrank_score:
                u.devrank_score *= 1000000
            else:
                u.devrank_score = 0
            u.public_repos = self._get_repos_count(s, u.id)
            u.followers = self._get_followers_count(s, u.id)
            u.following = self._get_following_count(s, u.id)
        return users

    def __search_global(self, query, page=1, page_per_row=20):
        s = self.db.makesession()
        likequery = '%%%s%%' % query
        users = s.query(User).join(Repo, User.id == Repo.owner_id) \
                 .filter(or_(Repo.description.like(likequery), \
                             Repo.language.like(likequery), \
                             User.location.like(likequery), \
                             User.login.like(likequery), \
                             User.name.like(likequery))) \
                 .order_by(User.devrank_score.desc()) \
                 .distinct() \
                 .limit(page_per_row) \
                 .offset((page - 1) * page_per_row) \
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


    def oauth(self, user, DBSave=True):
        s = self.db.makesession()
        r = s.query(Member).filter(Member.login == user).scalar()
        if r == None:
            if DBSave:
                s = self.db.makesession()
                s.add(Member(user))
                s.commit()
            return False
        else:
            return True
