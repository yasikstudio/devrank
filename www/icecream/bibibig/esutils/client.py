#-*- coding:utf-8 -*-
import rawes

class ESClient(object):

    def __init__(self):
        self.es = rawes.Elastic('http://jweb.kr:9200')

    def search(self, query):
        queryDSL = u'''
{
    "query": {
        "filtered": {
            "query": {
                "match_all": {}
            },
            "filter": {
                "nested": {
                    "path": "repos",
                    "query":{
                        "multi_match": {
                            "query": "%s",
                            "fields": [ "description", "language" ]
                        }
                    }
                }
            }
        }
    },
    "sort": [
        { "devrank_score": "desc" }
    ],
    "size": 50
}
        ''' % (query)

        result = self.es.post('github/users/_search', data=queryDSL)
        return result['hits']

    def get_gravatar_url(self, user):
        user_queryURI = 'github/users/_search'
        user_queryDSL = u'''
{
    "query": {
        "bool": {
            "must": [
                {
                    "term": {
                        "users.login": "%s"
                    }
                }
            ]
        }
    }
}
        '''
        result = self.es.post(user_queryURI, data=user_queryDSL % user)
        r = result['hits']['hits'];
        if len(r) == 0:
            return None
        return r[0]['_source']['avatar_url']

    def social_search(self, users):
        user_queryURI = 'github/users/_search'
        user_queryDSL = u'''
{
    "query": {
        "bool": {
            "must": [
                {
                    "term": {
                        "users.login": "%s"
                    }
                }
            ]
        }
    }
}
        '''

        repo_queryURI = 'github/repos/_search'
        repo_queryDSL = u'''
{
    "query": {
        "filtered": {
            "query": {
                "match_all": {}
            },
            "filter": {
                "nested": {
                    "path": "owner",
                    "query":{
                        "bool": {
                            "must": [
                                {
                                    "term": {
                                        "owner.login": "%s"
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }
    },
    "size": 50
}
        '''

        my_avatar_url = self.get_gravatar_url(users[0])
        if my_avatar_url == None:
            return []

        gravatar_url = {}
        gravatar_url[users[0]] = my_avatar_url
        links = []

        for user in users:
            ''' follower, following '''
            results = self.es.post(user_queryURI, data=user_queryDSL % user)
            for r in results['hits']['hits']:
                followings = r['_source']['following_users']
                for target in followings:
                    links.append({
                        "source": user,
                        "target": target['login'],
                        "gravatar_url": None,
                        "type": "type1"
                    })
                    gravatar_url[target['login']] = target['avatar_url']
                followers = r['_source']['follower_users']
                for source in followers:
                    links.append({
                        "source": source['login'],
                        "target": user,
                        "gravatar_url": None,
                        "type": "type1"
                    })
                    gravatar_url[source['login']] = source['avatar_url']

        for link in links:
            link['src_gravatar_url'] = gravatar_url[link['source']]
            link['tgt_gravatar_url'] = gravatar_url[link['target']]

        return links
