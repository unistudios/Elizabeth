from website.elizabeth.models import *
from excel_response import ExcelResponse

# These methods are used by the admin as Django actions for 
# exporting data to Excel spreadsheets in various ways.

##############################################################################################
# Download spreadsheet action for UNIX user to host mappings
##############################################################################################
def exportExcelUnix(modeladmin, request, queryset):
    #qsHosts = unixuserlist.objects.all()
    entries = list(queryset.values())
    
    for e in entries:
        try:
            e['hostname'] = unixhost.objects.get(pk=int(e['host_id'])).name
        except:
            e['hostname'] = e['host_id']
        #del(e['datedisabled'])
        del(e['host_id'])
        del(e['id'])
        del(e['user_id'])               

    return ExcelResponse(entries)
exportExcelUnix.short_description = "Download UNIX spreadsheet"

##############################################################################################
# Download spreadsheet action for Windows user to host mappings
##############################################################################################
def exportExcelWin(modeladmin, request, queryset):
    entries = list(queryset.values())
    
    for e in entries:
        try:
            e['hostname'] = winhost.objects.get(pk=int(e['host_id'])).name
        except:
            e['hostname'] = e['host_id']
        #del(e['datedisabled'])
        del(e['host_id'])
        del(e['id'])
        del(e['user_id'])
              
    return ExcelResponse(entries)
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
    rows = [ ['Application', 'Level', 'Hostname', 'OS', 'Username', 'Last Login', 'Enabled?'], 
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
                    rows.append([app.name, app.importance, user.host.name, user.host.os, user.username, user.lastlogin, user.enabled])
        
        # Repeat for Windows...   
        for u in winhosts:
            winusers = u.winuser_set.all()
            
            for user in winusers:
                if user.enabled:
                    rows.append([app.name, app.importance, user.host.name, user.host.os, user.username, user.lastlogin, user.enabled])
                
        
    return ExcelResponse(rows)
exportExcelAppsToUsers.short_description = "Download Apps Spreadsheet"

##############################################################################################
# General method to download spreadsheet action for other views.  Exports all fields in model.
##############################################################################################
def exportExcelAll(modeladmin, request, queryset):
    return ExcelResponse(queryset)
exportExcelAll.short_description = "Download spreadsheet"
