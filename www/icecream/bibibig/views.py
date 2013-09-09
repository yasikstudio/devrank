#-*- coding:utf-8 -*-
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext, Context
from django.shortcuts import *
from django.views.generic.base import View

import json


class intro(View):
    def get(self, request, *args, **kwargs):
        var = RequestContext(request, {'page_title': u'Devrank', })
        return render_to_response('intro.html', var)

def home(request):
    if request.user.is_authenticated():
        var = RequestContext(request, {'page_title': u'Devrank', })
        return render_to_response('home.html', var)
    else:
        return HttpResponseRedirect('/')

class search(View):
    def get(self, request, *args, **kwargs):
        if 'search' in kwargs:
            c = ESClient()
            r = c.search(kwargs['search'])

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
                    'query':kwargs['search'],
                    })
            return render_to_response('result_list.html', var)


def social_json(request):
    c = ESClient()
    users = request.GET.get('users', '').split('|')
    if users == '':
        users = []
    data = {
        "links": c.social_search(users)
    }
    return HttpResponse(json.dumps(data), content_type="application/json")
