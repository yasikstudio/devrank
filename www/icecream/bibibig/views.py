#-*- coding:utf-8 -*-
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext, Context
from django.shortcuts import *
from django.views.generic.base import View
from django.utils.safestring import *
from devrankmodels import DevRankModel
from oauthmanagers import OAuthManager
from sqlalchemy.orm import class_mapper

import json

def logout(request):
    response = HttpResponseRedirect('/')
    response.delete_cookie('own')
    return response

def login_github(request):
    o = OAuthManager()
    return HttpResponseRedirect(o.login_request())

def oauth(request):
    o = OAuthManager()
    c = DevRankModel()
    o.callback_response(request.get_full_path())
    me = json.loads(o.getUser())['login']
    c.oauth(me)
    response = HttpResponseRedirect('/search?m='+me)
    response.set_cookie('own', me)
    return response

class intro(View):
    def get(self, request, *args, **kwargs):
        var = RequestContext(request, {'page_title': u'Devrank', })
        try:
            var = RequestContext(request, {
                    'page_title': u'Devrank',
                    'me' : request.COOKIES['own'],
                    })
            return render_to_response('home.html', var)
        except:
            return render_to_response('intro.html', var)

class search(View):
    def get(self, request, *args, **kwargs):
        if request.GET.has_key(u'q'):
            c = DevRankModel()

            me = 'None'
            login = False

            if request.GET.has_key(u'm'):
                me = request.GET.get(u'm')
                cookie = None

                try:
                    cookie = request.COOKIES['own']
                except:
                    pass

                if me == cookie:
                    #me
                    login = True
                elif c.oauth(me, False):
                    #other user
                    login = False
                else:
                    #bad user
                    var = RequestContext(request, {
                            'page_title': u'Devrank',
                            'me' : me,
                            })
                    return render_to_response('except.html', var)

            else:
                try:
                    me = request.COOKIES['own']
                    login = True
                except:
                    return HttpResponseRedirect('/')

            details = c.search(request.GET.get(u'q'), me)
            for d in details:
                if d.hireable == True:
                    d.hireable = "Can!"
                else:
                    d.hireable = "Can't"

                if isinstance(d.blog, str) and (not "://" in d.blog) :
                    d.blog = "http://%s" % d.blog


            var = RequestContext(request, {
                    'page_title': u'Devrank',
                    'results': details,
                    'query': request.GET.get(u'q'),
                    'login': login,
                    'me' : me,
                    })
            return render_to_response('result_list.html', var)
        return HttpResponseRedirect('/')

def social_json(request):
    c = DevRankModel()
    usersparam = request.GET.get('users', None)
    users = usersparam and usersparam.split(',') or []
    data = {
        "links": c.social_search(users)
    }
    return HttpResponse(json.dumps(data), content_type="application/json")
