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

    def _get_user_id(self, login):
        s = self.db.makesession()
        user = s.query(User).filter_by(login=login).first()
        if user == None:
            return None
        return user.id

    def search(self, query, me=None, page=1, page_per_row=20):
        # TODO search using query and me.
        if me == None:
            return self._search_global(query)
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
        me_id = self._get_user_id(me)
        s = self.db.makesession()
        users = s.query(User).from_statement(sql) \
                       .params(id=me_id).all()
        for u in users:
            u.public_repos = self._get_repos_count(s, u.id)
            u.followers = self._get_followers_count(s, u.id)
            u.following = self._get_following_count(s, u.id)
        return users

    def _search_global(self, query, page=1, page_per_row=20):
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
        if len(users) == 0:
            return []

        social_sql = u'''
select distinct * from
(
    select
        u1.login src1,
        u1.avatar_url src1_gravata,
        u2.login dest1,
        u2.avatar_url dest1_gravata,
        null src2,
        null src2_gravata,
        null dest2,
        null dest2_gravata,
        null src3,
        null src3_gravata,
        null dest3,
        null dest3_gravata,
        u.login
    from friend_relation fr
    inner join users u on fr.dest_id = u.id
    inner join users u1 on fr.src_id = u1.id
    inner join users u2 on fr.dest_id = u2.id
    where src_id = :id
    and find_in_set(u.login, ':friends')
    # 3-depth
    union all
    select
        u1.login src1,
        u1.avatar_url src1_gravata,
        u2.login dest1,
        u2.avatar_url dest1_gravata,
        u3.login src2,
        u3.avatar_url src2_gravata,
        u4.login dest2,
        u4.avatar_url dest2_gravata,
        null src3,
        null src3_gravata,
        null dest3,
        null dest3_gravata,
        u.login
    from friend_relation fr1
    inner join friend_relation fr2 on fr1.dest_id = fr2.src_id
    inner join users u on fr2.dest_id = u.id
    inner join users u1 on fr1.src_id = u1.id
    inner join users u2 on fr1.dest_id = u2.id
    inner join users u3 on fr2.src_id = u3.id
    inner join users u4 on fr2.dest_id = u4.id
    where fr1.src_id = :id
    and find_in_set(u.login, ':friends')
    # 4-depth
    union all
    select
        u1.login src1,
        u1.avatar_url src1_gravata,
        u2.login dest1,
        u2.avatar_url dest1_gravata,
        u3.login src2,
        u3.avatar_url src2_gravata,
        u4.login dest2,
        u4.avatar_url dest2_gravata,
        u5.login src3,
        u5.avatar_url src3_gravata,
        u6.login dest3,
        u6.avatar_url dest3_gravata,
        u.login
    from friend_relation fr1
    inner join friend_relation fr2 on fr1.dest_id = fr2.src_id
    inner join friend_relation fr3 on fr2.dest_id = fr3.src_id
    inner join users u on fr3.dest_id = u.id
    inner join users u1 on fr1.src_id = u1.id
    inner join users u2 on fr1.dest_id = u2.id
    inner join users u3 on fr2.src_id = u3.id
    inner join users u4 on fr2.dest_id = u4.id
    inner join users u5 on fr3.src_id = u5.id
    inner join users u6 on fr3.dest_id = u6.id
    where fr1.src_id = :id
    and find_in_set(u.login, ':friends')
) friends
'''
        s = self.db.makesession()
        me = users.pop()
        me_id = self._get_user_id(me)
        sql = social_sql.replace(':friends', ','.join(users))
        res = s.execute(sql, { 'id': me_id })
        links = []
        for row in res:
            for idx in range(1, 4):
                src = 'src%d' % idx
                dest = 'dest%d' % idx
                src_gravatar = 'src%d_gravata' % idx
                dest_gravatar = 'dest%d_gravata' % idx
                if row[src] == None:
                    continue
                links.append({
                    'source': row[src],
                    'target': row[dest],
                    'src_gravatar_url': row[src_gravatar],
                    'tgt_gravatar_url': row[dest_gravatar],
                    'type': 'type3'
                })
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
