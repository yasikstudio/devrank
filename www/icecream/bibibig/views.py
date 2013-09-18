#-*- coding:utf-8 -*-
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext, Context
from django.shortcuts import *
from django.views.generic.base import View
from devrankmodels import DevRankModel
from oauthmanagers import OAuthManager
from sqlalchemy.orm import class_mapper

import json

def login_github(request):
    #login github and allow access over oauth2
    o = OAuthManager()
    return HttpResponseRedirect(o.login_request())

def oauth(request):
    o = OAuthManager()
    c = DevRankModel()
    o.callback_response(request.get_full_path())
    me = json.loads(o.getUser())['login']
    c.oauth(me)
    return HttpResponseRedirect('/home?m='+me)


class intro(View):
    def get(self, request, *args, **kwargs):
        var = RequestContext(request, {'page_title': u'Devrank', })
        return render_to_response('intro.html', var)

class home(View):
    def get(self, request, *args, **kwargs):
        if request.GET.has_key(u'q') and request.GET.has_key(u'm'):
            c = DevRankModel()
            me = request.GET.get(u'm')
            if not c.check_oauth(me):
                me = ''
            details = c.search(request.GET.get(u'q'))

            detail_json = {}
            for value in details:
                columns = [c.key for c in class_mapper(value.__class__).columns]
                d = dict((c, str(getattr(value, c)).replace('\r\n','')) for c in columns)
                d['etag']=d['etag'].replace('"','')
                detail_json.update({d['login']:d})

            var = RequestContext(request, {
                    'page_title': u'Devrank',
                    'results': details,
                    'result_json': json.dumps(detail_json),
                    'query': request.GET.get(u'q'),
                    'login': True,
                    'me' : me,
                    })
            return render_to_response('result_list.html', var)
        elif request.GET.has_key(u'm'):
            c = DevRankModel()
            me = request.GET.get(u'm')
            if not c.check_oauth(me):
                me = ''
            var = RequestContext(request, {
                'page_title': u'Devrank',
                'me' : me,
                })
            return render_to_response('home.html', var)
        return HttpResponseRedirect('/')

class detail(View):
    def post(self, request, *args, **kwargs):
        data = request.POST['json']
        j = json.loads(data)

        var = RequestContext(request, {
            'page_title': u'Devrank',
            'me': j['me'],
            'who': j[j['who']],
            })
        return render_to_response('detail.html', var)

def social_json(request):
    c = DevRankModel()
    usersparam = request.GET.get('users', None)
    users = usersparam and usersparam.split('|') or []
    data = {
        "links": c.social_search(users)
    }
    return HttpResponse(json.dumps(data), content_type="application/json")
