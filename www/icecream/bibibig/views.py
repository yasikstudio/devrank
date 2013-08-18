#-*- coding:utf-8 -*-
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext, Context
from django.shortcuts import *
from django.views.generic.base import View
import rawes

def home(request):
    es = rawes.Elastic('http://jweb.kr:9200')

    #description
    # print es.post('github/_search',data=""" {
    #               "query": {
    #                 "term": {
    #                   "login": "reeoss"
    #                 }
    #               }
    #             } """)
    print es.post('github/_search',data="""
                  {
                      "query": {
                        "filtered": {
                          "query": { "term": { "language":"java"}},
                          "filter": {
                              "nested": {
                              "path": "owner",
                              "query": {
                                "filtered": {
                                  "query": { "match_all": {}},
                                  "filter": {
                                  "or":[
                                  {"term": { "owner.login": "JSansalone" }},
                                  {"term": { "owner.login": "kunny" }}
                                  ]
                                  }
                                }
                              }
                            }
                          }
                        }
                      }
                    } """)



    var = RequestContext(request, {
            'page_title': u'Home',
            })
    return render_to_response('home.html', var)

def social(request):
    var = RequestContext(request, {
            'page_title': u'social graph',
            })
    return render_to_response('social.html', var)
