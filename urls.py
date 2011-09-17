from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'test1_3.views.home', name='home'),
    # url(r'^test1_3/', include('test1_3.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    #(r'^$', 'automation.views.home'),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    (r'^elizabeth/', include('elizabeth.urls')),
    (r'^wikiexport/', include('wikiexport.urls')),
    #(r'^opsware/', include('opsware.urls')),
    #(r'^ice/', include('ice.urls')),
    #(r'^cacti/', 'cacti.views.cacti'),
)
