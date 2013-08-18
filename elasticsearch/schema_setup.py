#!/usr/bin/env python

from pyes import *
from pyes.exceptions import *
import config

mappings = {}

mappings['users'] = {
    'follower_users': {
        'type': 'nested'
    },
    'following_users': {
        'type': 'nested'
    },
    'repos': {
        'type': 'nested'
    }
}

mappings['repos'] = {
    'owner': {
        'type': 'nested'
    },
    'stargazers': {
        'type': 'nested'
    },
    'subscribers': {
        'type': 'nested'
    },
    'pull_requests': {
        'type': 'nested'
    }
}

def setup(host, index_name):
    conn = ES(host)
    try:
        conn.indices.create_index(index_name)
    except IndexAlreadyExistsException:
        print 'IndexAlreadyExistsException'
        pass
    for index_type in mappings:
        conn.indices.put_mapping(
            index_type, { 'properties' : mappings[index_type] }, [ index_name ])
    conn.refresh(index_name)

if __name__ == '__main__':
    setup(config.elastic_search_host, config.index_name)
