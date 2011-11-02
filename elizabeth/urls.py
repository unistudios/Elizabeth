from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # ####################
    # User functions
    # ####################
    (r'^user/readuser/$', 'website.elizabeth.views.readuser'),  
    (r'^user/unix/update/$', 'website.elizabeth.views.unixuserupdate'),
    (r'^user/win/update/$', 'website.elizabeth.views.winuserupdate'), 
    (r'^user/removed/(?P<host_name>[0-9A-Za-z.-]+)/$', 'website.elizabeth.views.listremovableusers'),
    (r'^user/disabled/(?P<host_name>[0-9A-Za-z.-]+)/$', 'website.elizabeth.views.listdisableableusers'),
    (r'^user/(?P<host_name>\w+)/$', 'website.elizabeth.views.listusers'),

    # userlist's
    (r'^unixuserlist/$', 'website.elizabeth.views.allunixusers'),    # all users
    (r'^winuserlist/$', 'website.elizabeth.views.allwinusers'),    # all users
    
    # #################
    # Host Functions
    # #################
    (r'^host/unix/update/$', 'website.elizabeth.views.unixhostupdate'),
    (r'^host/win/update/$', 'website.elizabeth.views.winhostupdate'),
    (r'^host/update/$', 'website.elizabeth.views.hostupdate'),    
    
    # #################
    # Reporting
    # #################
    
    # wiki pages
    (r'^reporting/summary/$', 'website.elizabeth.views.user_summary'),
    (r'^reporting/type_summary/$', 'website.elizabeth.views.user_type_summary'),
    
    # wiki excel links: Local User Metrics
    (r'^reporting/disableable/$', 'website.elizabeth.excel.disableableUsers'),
    (r'^reporting/removable/$', 'website.elizabeth.excel.removableUsers'),
    (r'^reporting/system/$', 'website.elizabeth.excel.systemUsers'),
    (r'^reporting/application/$', 'website.elizabeth.excel.applicationUsers'),
    (r'^reporting/unknown/$', 'website.elizabeth.excel.unknownUsers'),
    (r'^reporting/removed/$', 'website.elizabeth.excel.removedUsers'),
    
    # wiki excel links: Account Types    
    (r'^reporting/tuser/$', 'website.elizabeth.excel.tUsers'),
    (r'^reporting/tsystem/$', 'website.elizabeth.excel.tSysUsers'),
    (r'^reporting/tapplication/$', 'website.elizabeth.excel.tAppUsers'),
    (r'^reporting/tunknown/$', 'website.elizabeth.excel.tUnkUsers'),
    
    # #################
    # Upload OGFS Files
    # #################
    (r'^delivery/$', 'website.elizabeth.views.uploadFile'), 
    
    # ###########################################
    # Hostlist URL's - Gives back lists of hosts
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
    (r'^hostlist/appEnabledUnix/$', 'website.elizabeth.views.listEnabledAppUnixHosts'),
    (r'^hostlist/appEnabledWin/$', 'website.elizabeth.views.listEnabledAppWinHosts'),
    
    # ###########################################
    # Used by OGFS scripts to add applications
    # ###########################################
    (r'^app/group1/$', 'website.elizabeth.views.group1'),
    (r'^app/group2/$', 'website.elizabeth.views.group2'),
    (r'^app/group3/$', 'website.elizabeth.views.group3'),
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

