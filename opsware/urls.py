from django.conf.urls.defaults import *
from django.views.generic.simple      import direct_to_template

urlpatterns = patterns('opsware.views',
    ('^$', 'opsware'),
    (r'^all/$', 'all'),    # this should really fall under list as a parameter.

    # list URL, requires a 'type' parameter.
    (r'^list/$', 'list'),

    # update URL - allows us to update a record
    (r'^server/(?P<server_id>\d+)/$', 'server_update'),
    
    (r'chartdata/$', 'chartdata'),
    
    # fusion charts, WIP
    (r'chartdeployedbydate/$', 'chartdeploybydate'),
    (r'chartstatus/$', 'chartstatus'),
    
    #(r'chartdeploybydatedata/$', 'chartdeploybydatedata'),
    #(r'chartstatusdata/$', 'chartstatusdata'),
    #(r'chartdeploybyos/$', 'chartdeploybyos'),
    #(r'chartdeploybyosdata/$', 'chartdeploybyosdata'),
    #
)
