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
                            "query": \"%s\",
                            "fields": [ "description", "language" ]
                        }
                    }
                }
            }
        }
    },
    "sort": [
        { "devrank_score": "desc" }
    ]
}
        ''' % (query)
        result = self.es.post('github/users/_search', data=queryDSL)
        return result['hits']['hits']

    def social_search(self, users):
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
                            "query": \"%s\",
                            "fields": [ "description", "language" ]
                        }
                    }
                }
            }
        }
    },
    "sort": [
        { "devrank_score": "desc" }
    ]
}
        ''' % (query)
        result = self.es.post('github/users/_search', data=queryDSL)
        return result['hits']
