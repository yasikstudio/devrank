#-*- coding:utf-8 -*-
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext, Context
from django.shortcuts import *
from django.views.generic.base import View
from devrankmodels import DevRankModel
from oauthmanagers import OAuthManager

import json

def login_github(request):
    #login github and allow access over oauth2
    o = OAuthManager()
    return HttpResponseRedirect(o.login_request())

def oauth(request):
    o = OAuthManager()
    c = DevRankModel()
    o.callback_response(request.get_full_path())
    user = json.loads(o.getUser())['login']
    c.oauth(user)
    return HttpResponseRedirect('/home?m='+user)


class intro(View):
    def get(self, request, *args, **kwargs):
        var = RequestContext(request, {'page_title': u'Devrank', })
        return render_to_response('intro.html', var)

class home(View):
    def get(self, request, *args, **kwargs):
        if u'q' in request.GET.keys() and \
            u'm' in request.GET.keys():
            c = DevRankModel()
            user = request.GET.get(u'm')
            if not c.check_oauth(user):
                user = ''

            users = c.search(request.GET.get(u'q'))
            var = RequestContext(request, {
                    'page_title': u'Devrank',
                    'results': users,
                    'query': request.GET.get(u'q'),
                    'login': True,
                    'who' : user,
                    })
            return render_to_response('result_list.html', var)
        elif u'm' in request.GET.keys():
            c = DevRankModel()
            user = request.GET.get(u'm')
            if not c.check_oauth(user):
                user = ''
            var = RequestContext(request, {
                'page_title': u'Devrank',
                'who' : user,
                })
            return render_to_response('home.html', var)
        return HttpResponseRedirect('/')

class detail(View):
    def post(self, request, *args, **kwargs):
        me = request.POST.get('m', None)
        who = request.POST.get('w', None)
        j = json.loads(request.POST.get('j', None).replace('\r\n','\\r\\n'))

        var = RequestContext(request, {
            'page_title': u'Devrank',
            'me': me,
            'who': j[who],
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
