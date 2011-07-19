from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # ####################
    # User functions
    # ####################
    (r'^user/unix/update/$', 'website.elizabeth.views.unixuserupdate'),
    (r'^user/win/update/$', 'website.elizabeth.views.winuserupdate'),
    (r'^user/(?P<host_name>\w+)/disable/$', 'website.elizabeth.views.userdisablelist'), 

    # userlist's
    (r'^userlist/$', 'website.elizabeth.views.allusers'),    # all users
    
    # #################
    # Host Functions
    # #################
    (r'^host/update/$', 'website.elizabeth.views.hostupdate'), 
    
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
    (r'^hostlist/listunixhosts/$', 'website.elizabeth.views.listunixUsers'),
    (r'^hostlist/listwinhosts/$', 'website.elizabeth.views.listwinHosts'),
    
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
    (r'^excel/$', 'website.elizabeth.views.excelview'),

    #(r'^test/$', 'website.elizabeth.views.test'),
)

