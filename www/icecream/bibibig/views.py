#-*- coding:utf-8 -*-
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext, Context
from django.shortcuts import *
from django.views.generic.base import View
from esutils.client import ESClient

import json

def home(request):
    c = ESClient()
    print len(c.search('java')['hits'])

    var = RequestContext(request, {
            'page_title': u'Home',
            })
    return render_to_response('home.html', var)

def social(request):
    var = RequestContext(request, {
            'page_title': u'social graph',
            })
    return render_to_response('social.html', var)

def social_json(request):
    c = ESClient()
    users = request.GET.get('users', '').split('|')
    if users == '':
        users = []
    print users
    data = {
        "links": c.social_search(users)
    }
    return HttpResponse(json.dumps(data), content_type="application/json")
