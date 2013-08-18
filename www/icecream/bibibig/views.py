#-*- coding:utf-8 -*-
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext, Context
from django.shortcuts import *
from django.views.generic.base import View
import rawes
from esutils.client import ESClient

def home(request):
    c = ESClient()
    c.search('peanut')

    var = RequestContext(request, {
            'page_title': u'Home',
            })
    return render_to_response('home.html', var)

def social(request):
    var = RequestContext(request, {
            'page_title': u'social graph',
            })
    return render_to_response('social.html', var)
