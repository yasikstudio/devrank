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

def login_github(request):
    o = OAuthManager()
    return HttpResponseRedirect(o.login_request())

def oauth(request):
    o = OAuthManager()
    c = DevRankModel()
    o.callback_response(request.get_full_path())
    me = json.loads(o.getUser())['login']
    c.oauth(me)
    response = HttpResponseRedirect('/home')
    response.set_cookie('own', me)
    return response

class intro(View):
    def get(self, request, *args, **kwargs):
        var = RequestContext(request, {'page_title': u'Devrank', })
        try:
            request.COOKIES['own']
            return render_to_response('home.html', var)
        except:
            return render_to_response('intro.html', var)

class home(View):
    def get(self, request, *args, **kwargs):
        if request.GET.has_key(u'q'):
            c = DevRankModel()
            details = c.search(request.GET.get(u'q'))
            detail = {}
            for value in details:
                columns = [c.key for c in class_mapper(value.__class__).columns]
                d = dict((c, '%s' % (getattr(value, c))) for c in columns)
                detail.update({d['login']:d})

            me = 'None'
            login = False
            try:
                me = request.COOKIES['own']
                login = True
            except:
                pass

            var = RequestContext(request, {
                    'page_title': u'Devrank',
                    'results': details,
                    'result_json': SafeString(json.dumps(detail)),
                    'query': request.GET.get(u'q'),
                    'login': login,
                    'me' : me,
                    })
            return render_to_response('result_list.html', var)
        return HttpResponseRedirect('/')

class detail_json(View):
    def post(self, request, *args, **kwargs):
        data = request.POST['json']
        j = json.loads(data)
        who = j[j['who']]

        for key, value in who.iteritems():
            if value == '':
                who[key]='None';
        if who['hireable'] == True:
            who['hireable'] = "Can!"
        else:
            who['hireable'] = "Can't"

        if (not "://" in who['blog']) and who['blog'] != "None":
            who['blog'] = "http://%s" % who['blog']

        var = RequestContext(request, {
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
