from django.conf.urls import patterns, include, url
#from api import urls as apiurls
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
import settings
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'track_system.views.home', name='home'),
    # url(r'^track_system/', include('track_system.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    # api
    url(r'^api/', include('api.urls')),
    # testing
    url(r'', include('host.urls')),
)
