from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from sip.models import Host
from sip.handlers import HostHandler
from piston.resource import Resource

admin.autodiscover()

hosthandler = Resource(HostHandler)
urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'admin.views.home', name='home'),
    # url(r'^admin/', include('admin.foo.urls')),
    url(r'^import_host/','sip.views.import_host'),
    url(r'^import_network/','sip.views.import_network'),
   # url(r'^install_xen/(.+)','sip.views.xen_install'),
   # url(r'^preinstall_xen/(.+)','sip.views.xen_preinstall'),
   # url(r'^process_xen/(.+)','sip.views.show_xen_process'),
   # url(r'^show_log','sip.views.show_log'),
    url(r'^ks_temp/(.+)','sip.views.list_ks_temp'),
    url(r'^get_ks_temps','sip.views.get_ks_temps'),
    url(r'^set_q','sip.views.set_install_max_no'),
    url(r'^get_q','sip.views.get_install_max_no'),
    url(r'^get_ks_module','sip.views.get_ks_module'),
    url(r'^count','sip.views.count'),
    url(r'^scan_network','sip.views.scan_all_networks'),
    url(r'^mac/(.+)','sip.views.get_host_conf'),
    url(r'^pxe','sip.views.pxe'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),


    url(r'^host/(?P<sn>[^/]+)/', hosthandler, name='host'),
    url(r'^host/', hosthandler, ),
)
