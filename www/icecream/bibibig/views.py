#-*- coding:utf-8 -*-
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext, Context
from django.shortcuts import *
from django.views.generic.base import View
from esutils.client import ESClient

import json

def home(request):
    if request.method == 'POST':
        c = ESClient()
        r = c.search(request.POST['query'])

        for _r in r:
            _r.update({u"source":_r["_source"]})
            if u"devrank_score" in _r[u"source"].keys():
                value = float(_r[u"source"][u"devrank_score"]) * 1000000
                _r["source"].update({u"devrank_score":value})
            else:
                _r["source"].update({u"devrank_score":0})
            _r.pop(u"_source",None)

        var = RequestContext(request, {
                'page_title': u'Devrank',
                'results': r,
                'query':request.POST['query'],
                })
        return render_to_response('result_list.html', var)
    else:
        var = RequestContext(request, {'page_title': u'Home', })
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
