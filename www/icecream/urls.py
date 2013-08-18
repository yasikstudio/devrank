from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'icecream.bibibig.views.home', name='home'),
    url(r'^social/$', 'icecream.bibibig.views.social', name='social'),
    url(r'^social.json/$', 'icecream.bibibig.views.social_json', name='social_json'),
    # url(r'^icecream/', include('icecream.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
