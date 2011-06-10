from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # ####################
    # User functions
    # ####################
    (r'^user/update/$', 'website.likewise.views.userupdate2'),
    (r'^user/(?P<host_name>\w+)/$', 'website.likewise.views.userupdate'),
    (r'^user/(?P<host_name>\w+)/disable/$', 'website.likewise.views.userdisablelist'), 

    # userlist's
    (r'^userlist/$', 'website.likewise.views.allusers'),    # all users
    
    # #################
    # Host Functions
    # #################
    (r'^host/(?P<host_name>\w+)/$', 'website.likewise.views.hostupdate'), 
    
    # ###########################################
    # Hostlist URL's - Gives back lists of unixhost's
    # ###########################################
    (r'^hostlist/newhosts/$', 'website.likewise.views.NewHosts'),
    (r'^hostlist/disable/$', 'website.likewise.views.DisableHosts'),
    (r'^hostlist/osinfo/$', 'website.likewise.views.HostOSinfo'),
    (r'^hostlist/prhosts/$', 'website.likewise.views.prHosts'),
    (r'^hostlist/run/$', 'website.likewise.views.hostlist_run'),
    (r'^hostlist/installed/$', 'website.likewise.views.installed'),
    (r'^hostlist/allsox/$', 'website.likewise.views.allsox'),
    (r'^hostlist/kyle/$', 'website.likewise.views.kyle_test'),
    
    # #####################
    # MISC
    # ##################### 
    # wiki values page (kludgy for now)
    (r'^wikivalues/$', 'website.likewise.views.wikivalues'),

    #(r'^test/$', 'website.likewise.views.test'),
)

