from website.elizabeth.models import *
from excel_response import ExcelResponse
from itertools import chain
from django.utils.datastructures import SortedDict

##############################################################################################
##############################################################################################
#######################       Spreadsheets for Admin Actions           #######################
##############################################################################################
##############################################################################################


##############################################################################################
# Download spreadsheet action for UNIX user to host mappings
##############################################################################################
def exportExcelUnix(modeladmin, request, queryset):
    #qsHosts = unixuserlist.objects.all()
    entries = list(queryset.values())
    new_entries = []
    
    for e in entries:
        app_str = ""
        
        try:
            the_host = unixhost.objects.get(pk=int(e['host_id']))
        except:
            e['hostname'] = e['host_id']
            
            # no "try-finally" statement in python 2.4 :-(
            del(e['host_id'])
            del(e['id'])
            del(e['user_id'])   
        else:
            #del(e['datedisabled'])
            e['hostname'] = the_host.name
            
            for app in the_host.apps.values():
                app_str += app['name'] + ", "
            
            app_str = app_str.strip(", ")
            e['apps'] = app_str
            del(e['host_id'])
            del(e['id'])
            del(e['user_id'])
            
            # hack to put these entries at the end of the dictionary...
            e = SortedDict(e)
            e.insert(len(e), "retired", the_host.retired)
            # this one is probably better just for internal use...
            # e.insert(len(e), "accessible", the_host.accessible)
            
            new_entries.append(e)

    return ExcelResponse(new_entries)
exportExcelUnix.short_description = "Download UNIX spreadsheet"

##############################################################################################
# Download spreadsheet action for Windows user to host mappings
##############################################################################################
def exportExcelWin(modeladmin, request, queryset):
    entries = list(queryset.values())
    new_entries = []
    
    for e in entries:
        app_str = ""
        
        try:
            the_host = winhost.objects.get(pk=int(e['host_id']))
        except:
            e['hostname'] = e['host_id']
            
            # no "try-finally" statement in python 2.4 :-(
            del(e['host_id'])
            del(e['id'])
            del(e['user_id']) 
        else:
            #del(e['datedisabled'])
            e['hostname'] = the_host.name
            
            for app in the_host.apps.values():
                app_str += app['name'] + ", "
            
            app_str = app_str.strip(", ")
            e['apps'] = app_str
            del(e['host_id'])
            del(e['id'])
            del(e['user_id'])
            
            # hack to put these entries at the end of the dictionary...
            e = SortedDict(e)
            e.insert(len(e), "retired", the_host.retired)
            # this one is probably better just for internal use...
            #e.insert(len(e), "accessible", the_host.accessible)
            
            new_entries.append(e)
              
    return ExcelResponse(new_entries)
exportExcelWin.short_description = "Download Windows spreadsheet"

##########################
# *** MAY BE REMOVED *** #
##########################

##############################################################################################
# Download spreadsheet action for Windows user to host mappings
##############################################################################################
def exportExcelAppsToHosts(modeladmin, request, queryset):
    #entries = list(queryset.values())
    
    entries = [ ['Application', 'Host', 'OS'], 
              ]
    for q in queryset:    
        winhosts = ""
        unixhosts = ""

        try:
            app = hostapp.objects.filter(name=q.name)[0] # Get app query object
        except:
            print "Failed to retrieve app"
            continue
        else: 
            winhosts = app.winhost_set.all()
            unixhosts = app.unixhost_set.all()
        
        if winhosts:
            for w in winhosts:
                entries.append([app.name, w.name, w.os])
                
        if unixhosts:
            for u in unixhosts:
                #entries.append(curr_row)
                entries.append([app.name, u.name, u.os])
        
    return ExcelResponse(entries)
exportExcelAppsToHosts.short_description = "Download Apps spreadsheet"

##############################################################################################
# Create spreadsheet which shows enabled users linked to Applications
##############################################################################################
def exportExcelAppsToUsers(modeladmin, request, queryset):
    rows = [ ['Application', 'Level', 'Hostname', 'OS', 'Username', 'Type', 'Last Login', 'Enabled?'], 
              ]
    
    for app in queryset:    
        # Grab all Unix and Windows hosts associated with the apps in the queryset
        unixhosts = app.unixhost_set.all()
        winhosts  = app.winhost_set.all()
        
        # Enumerate all unixusers associated with hosts and add them into rows
        for u in unixhosts:
            unixusers = u.unixuser_set.all()
            
            for user in unixusers:
                if user.enabled:
                    rows.append([app.name, app.importance, user.host.name, user.host.os, user.username, user.user.type, user.lastlogin, user.enabled])
        
        # Repeat for Windows...   
        for u in winhosts:
            winusers = u.winuser_set.all()
            
            for user in winusers:
                if user.enabled:
                    rows.append([app.name, app.importance, user.host.name, user.host.os, user.username, user.user.type, user.lastlogin, user.enabled])
                
        
    return ExcelResponse(rows, "enabled_users_by_app")
exportExcelAppsToUsers.short_description = "Download Enabled Users by App"

def exportExcelUnixByApp(modeladmin, request, queryset):
    rows = [ ['Application', 'Level', 'Hostname', 'OS',], 
              ]
    
    for app in queryset:    
        # Grab all Unix hosts associated with the apps in the queryset
        unixhosts = app.unixhost_set.filter(retired=False)
        
        # Enumerate all unixhosts associated with hosts and add them into rows
        for u in unixhosts:
            rows.append([app.name, app.importance, u.name, u.os])

    return ExcelResponse(rows, "unixhosts_by_app")
exportExcelUnixByApp.short_description = "Download Active Hosts (UNIX) by App"

def exportExcelWinByApp(modeladmin, request, queryset):
    rows = [ ['Application', 'Level', 'Hostname', 'OS',], 
              ]
    
    for app in queryset:    
        # Grab Windows hosts associated with the apps in the queryset
        winhosts = app.winhost_set.filter(retired=False)
        
        # Enumerate all winhosts associated with hosts and add them into rows
        for u in winhosts:
            rows.append([app.name, app.importance, u.name, u.os])

    return ExcelResponse(rows, "winhosts_by_app")
exportExcelWinByApp.short_description = "Download Active Hosts (Win) by App"

def exportExcelAllByApp(modeladmin, request, queryset):
    rows = [ ['Application', 'Level', 'Hostname', 'OS',], 
              ]
    
    for app in queryset:    
        # Grab all Unix and Windows hosts associated with the apps in the queryset
        unixhosts = app.unixhost_set.filter(retired=False)
        winhosts  = app.winhost_set.filter(retired=False)
        
        # Enumerate all unixhosts associated with hosts and add them into rows
        for u in unixhosts:
            rows.append([app.name, app.importance, u.name, u.os])
            
        # Enumerate all winhosts associated with hosts and add them into rows
        for u in winhosts:
            rows.append([app.name, app.importance, u.name, u.os])

    return ExcelResponse(rows, "allhosts_by_app")
exportExcelAllByApp.short_description = "Download Active Hosts (all) by App"

##############################################################################################
# Create spreadsheet which show unixhosts
##############################################################################################
def exportExcelUnixHosts(modeladmin, request, queryset):
    rows = [ ['Hostname', 'Applications', 'OS', 'Retired'], 
              ]
    
    for host in queryset:    
        # Grab all apps associated with host
        apps = host.apps.all()      
        
        appstr = ""
        
        for a in apps:
            appstr = appstr + str(a)
            if len(apps) > 1:
                appstr += ", "
    
        rows.append([host.name, appstr, host.os, host.retired])
        
    return ExcelResponse(rows)
exportExcelUnixHosts.short_description = "Download Unix Hosts Spreadsheet"

##############################################################################################
# Create spreadsheet which show winhosts
##############################################################################################
def exportExcelWinHosts(modeladmin, request, queryset):
    rows = [ ['Hostname', 'Applications', 'OS', 'Retired'], 
              ]
    
    for host in queryset:    
        # Grab all apps associated with host
        apps = host.apps.all()      
        
        appstr = ""
        
        for a in apps:
            appstr = appstr + str(a)
            if len(apps) > 1:
                appstr += ", "
    
        rows.append([host.name, appstr, host.os, host.retired])
        
    return ExcelResponse(rows)
exportExcelWinHosts.short_description = "Download Windows Hosts Spreadsheet"

##############################################################################################
# General method to download spreadsheet action for other views.  Exports all fields in model.
##############################################################################################
def exportExcelAll(modeladmin, request, queryset):
    return ExcelResponse(queryset)
exportExcelAll.short_description = "Download spreadsheet"



##############################################################################################
##############################################################################################
#######################       Spreadsheets for WIKI download           #######################
##############################################################################################
##############################################################################################

#
# For Local User Metrics Wiki Page
#

def disableableUsers(request):
    rows = [ ['Host', 'Application', 'Username', 'Enabled', 'Allowed'], 
              ]
    unix_disableable = unixuser.objects.filter(enabled=True, user__type="U", user__enabled=False, dateremoved__isnull=True, datedisabled__isnull=True, host__retired=False)
    win_disableable = winuser.objects.filter(enabled=True, user__type="U", user__enabled=False, dateremoved__isnull=True, datedisabled__isnull=True, host__retired=False)
    return genUserReport(request, unix_disableable, win_disableable, "disableable_users")
disableableUsers.short_description = "Wiki Spreadsheet, Disable-able Users"


def removableUsers(request):
    rows = [ ['Host', 'Application', 'Username', 'Enabled', 'Allowed'], 
              ]
    unix_removable = unixuser.objects.filter(enabled=False, user__type="U", user__enabled=False, dateremoved__isnull=True, host__retired=False)
    win_removable = winuser.objects.filter(enabled=False, user__type="U", user__enabled=False, dateremoved__isnull=True, host__retired=False)
    return genUserReport(request, unix_removable, win_removable, "removable_users")
removableUsers.short_description = "Wiki Spreadsheet, Removable Users"

def localUsers(request):
    rows = [ ['Host', 'Application', 'Username', 'Enabled', 'Allowed'], 
              ]
    unix_sysaccts = unixuser.objects.filter(user__type="U", host__retired=False, user__enabled=True)
    win_sysaccts = winuser.objects.filter(user__type="U", host__retired=False, user__enabled=True)
    return genUserReport(request, unix_sysaccts, win_sysaccts, "local_users")
localUsers.short_description = "Wiki Spreadsheet, Local Users"

def systemUsers(request):
    rows = [ ['Host', 'Application', 'Username', 'Enabled', 'Allowed'], 
              ]
    unix_sysaccts = unixuser.objects.filter(user__type="S", host__retired=False)
    win_sysaccts = winuser.objects.filter(user__type="S", host__retired=False)
    return genUserReport(request, unix_sysaccts, win_sysaccts, "system_users")
systemUsers.short_description = "Wiki Spreadsheet, System Users"


def applicationUsers(request):
    rows = [ ['Host', 'Application', 'Username', 'Enabled', 'Allowed'], 
              ]
    unix_appaccts = unixuser.objects.filter(user__type="A", host__retired=False)
    win_appaccts = winuser.objects.filter(user__type="A", host__retired=False)
    return genUserReport(request, unix_appaccts, win_appaccts, "app_users")
applicationUsers.short_description = "Wiki Spreadsheet, Application Users"


def unknownUsers(request):
    rows = [ ['Host', 'Application', 'Username', 'Enabled', 'Allowed'], 
              ]
    unix_unkaccts = unixuser.objects.filter(user__type="X", host__retired=False)
    win_unkaccts = winuser.objects.filter(user__type="X", host__retired=False)
    return genUserReport(request, unix_unkaccts, win_unkaccts, "unknown_users")
unknownUsers.short_description = "Wiki Spreadsheet, Unknown Users"

def removedUsers(request):
    rows = [ ['Host', 'Application', 'Username', 'Enabled', 'Allowed'], 
              ]
    unix_remaccts = unixuser.objects.filter(user__type="U", dateremoved__isnull=False)
    win_remaccts = winuser.objects.filter(user__type="U", dateremoved__isnull=False)
    return genUserReport(request, unix_remaccts, win_remaccts, "removed_users")
removedUsers.short_description = "Wiki Spreadsheet, Removed Users"


#
# For Local User Metrics Wiki Page
#

def tUsers(request):
    rows = [ ['Host', 'Application', 'Username', 'Enabled', 'Allowed'], 
              ]
    unix_usraccts = unixuser.objects.filter(enabled=True, user__type="U", host__retired=False, dateremoved__isnull=True, datedisabled__isnull=True)
    win_usraccts = winuser.objects.filter(enabled=True, user__type="U", host__retired=False, dateremoved__isnull=True, datedisabled__isnull=True)
    return genUserReport(request, unix_usraccts, win_usraccts, "local_users")
tUsers.short_description = "Wiki Spreadsheet, Local Users"

def tAppUsers(request):
    rows = [ ['Host', 'Application', 'Username', 'Enabled', 'Allowed'], 
              ]
    unix_appaccts = unixuser.objects.filter(enabled=True, user__type="A", host__retired=False, dateremoved__isnull=True, datedisabled__isnull=True)
    win_appaccts = winuser.objects.filter(enabled=True, user__type="A", host__retired=False, dateremoved__isnull=True, datedisabled__isnull=True)
    return genUserReport(request, unix_appaccts, win_appaccts, "app_users")
tAppUsers.short_description = "Wiki Spreadsheet, Application Users"

def tUnkUsers(request):
    rows = [ ['Host', 'Application', 'Username', 'Enabled', 'Allowed'], 
              ]
    unix_unkaccts = unixuser.objects.filter(enabled=True, user__type="X", host__retired=False, dateremoved__isnull=True, datedisabled__isnull=True)
    win_unkaccts = winuser.objects.filter(enabled=True, user__type="X", host__retired=False, dateremoved__isnull=True, datedisabled__isnull=True)
    return genUserReport(request, unix_unkaccts, win_unkaccts, "unknown_users")
tUnkUsers.short_description = "Wiki Spreadsheet, Unknown Users"

def tSysUsers(request):
    rows = [ ['Host', 'Application', 'Username', 'Enabled', 'Allowed'], 
              ]
    unix_sysaccts = unixuser.objects.filter(enabled=True, user__type="S", host__retired=False, dateremoved__isnull=True, datedisabled__isnull=True)
    win_sysaccts = winuser.objects.filter(enabled=True, user__type="S", host__retired=False, dateremoved__isnull=True, datedisabled__isnull=True)
    return genUserReport(request, unix_sysaccts, win_sysaccts, "system_users")
tSysUsers.short_description = "Wiki Spreadsheet, System Users"

#
# Helper function to generate spreadsheets
#

def genUserReport(request, unix_accts, win_accts, filename):
    
    rows = [ ['Username', 'Host', 'Application', 'Enabled', 'Allowed'], 
              ]
    
    for u in unix_accts:
        app_list = u.host.apps.values_list("name", flat=True)
        app_list_str = ""
        
        for a in app_list:
            app_list_str += a + ", "
        app_list_str = app_list_str.rstrip(", ")
        
        rows.append([u.username, u.host.name, app_list_str, u.enabled, u.user.enabled])
            
    for w in win_accts:
        app_list = w.host.apps.values_list("name", flat=True)
        app_list_str = ""
        
        for a in app_list:
            app_list_str += a + ", "
            
        app_list_str = app_list_str.rstrip(", ")
        
        rows.append([w.username, w.host.name, app_list_str, w.enabled, w.user.enabled])
            
    return ExcelResponse(rows, filename)

