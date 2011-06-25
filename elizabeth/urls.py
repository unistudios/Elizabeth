from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # ####################
    # User functions
    # ####################
    (r'^user/update/$', 'website.elizabeth.views.userupdate2'),
    (r'^user/(?P<host_name>\w+)/$', 'website.elizabeth.views.userupdate'),
    (r'^user/(?P<host_name>\w+)/disable/$', 'website.elizabeth.views.userdisablelist'), 

    # userlist's
    (r'^userlist/$', 'website.elizabeth.views.allusers'),    # all users
    
    # #################
    # Host Functions
    # #################
    (r'^host/(?P<host_name>\w+)/$', 'website.elizabeth.views.hostupdate'), 
    
    # ###########################################
    # Hostlist URL's - Gives back lists of unixhost's
    # ###########################################
    (r'^hostlist/newhosts/$', 'website.elizabeth.views.NewHosts'),
    (r'^hostlist/disable/$', 'website.elizabeth.views.DisableHosts'),
    (r'^hostlist/osinfo/$', 'website.elizabeth.views.HostOSinfo'),
    (r'^hostlist/prhosts/$', 'website.elizabeth.views.prHosts'),
    (r'^hostlist/run/$', 'website.elizabeth.views.hostlist_run'),
    (r'^hostlist/installed/$', 'website.elizabeth.views.installed'),
    (r'^hostlist/allsox/$', 'website.elizabeth.views.allsox'),
    (r'^hostlist/listhosts/$', 'website.elizabeth.views.listHosts'),
    
    # ###########################################
    # Used by OGFS scripts to add applications
    # ###########################################
    (r'^app/update/$', 'website.elizabeth.views.addApp'),
    (r'^app/add/host/$', 'website.elizabeth.views.addApp2Host'),
    
    # #####################
    # MISC
    # ##################### 
    # wiki values page (kludgy for now)
    (r'^wikivalues/$', 'website.elizabeth.views.wikivalues'),

    #(r'^test/$', 'website.elizabeth.views.test'),
)

