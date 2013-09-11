from django.conf.urls import patterns, include, url
from icecream.bibibig.views import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', intro.as_view() ),
    url(r'^home$', home ),
    url(r'^search/(?P<search>\w+)/?$', search.as_view()),
    url(r'^social.json/$', social_json, name='social_json'),
    url(r'^oauth/$', oauth),
    url(r'^login/github/$', login_github),
    # url(r'^icecream/', include('icecream.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
