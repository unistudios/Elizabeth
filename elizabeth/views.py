import datetime
import sys

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.generic.list_detail import *
from django.views.generic.simple import *
from django.db.models import Q
from excel_response import ExcelResponse
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from datetime import timedelta
import datetime

from website.elizabeth.models import *
from elizabeth.delivery import *
from elizabeth.reporting import *
from elizabeth.excel import *

##############################################################################################
# Test view for ExcelView
##############################################################################################
def excelview(request):
    data = [ ['Column 1', 'Column2'], [1,2], [23,67]]
    return ExcelResponse(data, 'my_data')

def todaystr():
    return datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p")
    
def TemplateExt(request):
    if "curl" in request.META['HTTP_USER_AGENT']:
        return "wiki"
    else:
        return "html"

def index(request):
    # return the main index.html page although this should be a redirect to the WIKI for now.
    return direct_to_template(request,
                              template="elizabeth/index.html",
                              extra_context={},
                            )   

def installed(request):
    return object_list(request,
                       queryset=unixhost.objects.filter(hostsetting__installed=True,
                                                        app__importance="L1"). order_by('-hostsetting__installdate'),
                       template_name="elizabeth/installed.%s" % TemplateExt(request),
                       extra_context={'dToday': todaystr()},
                    )
def hostlist_run(request):
    #return object_list(request,
    #                   queryset=unixhost.objects.filter(hostsetting__installed=True).exclude(app__importance="L1").order_by('-hostsetting__installdate'),
    #                   template_name="elizabeth/installed.%s" % TemplateExt(request),
    #                   extra_context={'dToday': todaystr()},
    #                )
    qsRunHosts = unixhost.objects.exclude(app__importance="L1")
    nRunHostsInstalled = qsRunHosts.filter(hostsetting__installed=True).count()
    nRunHostsRemaining = qsRunHosts.filter(hostsetting__installed=False).count()
    
    qsRunUsers = unixuser.objects.exclude(host__app__importance="L1")
    nRunUsersEnabled = qsRunUsers.filter(enabled=True).count()
    nRunUsersDisabled = qsRunUsers.filter(enabled=False).count()

    return object_list(request,
                       queryset=qsRunHosts.order_by('-hostsetting__installdate'),
                       template_name="elizabeth/hostlist_run.%s" % TemplateExt(request),
                       extra_context={'dToday': todaystr(),
                                      'nRunHostsInstalled'     : nRunHostsInstalled,
                                      'nRunHostsRemaining'     : nRunHostsRemaining,
                                      'nRunUsersEnabled'       : nRunUsersEnabled, 
                                      'nRunUsersDisabled'      : nRunUsersDisabled,
                                     },
                    )
                    
def listHosts(request):
    #return object_list(request,
    #                   queryset=unixhost.objects.filter(hostsetting__installed=True).exclude(app__importance="L1").order_by('-hostsetting__installdate'),
    #                   template_name="elizabeth/installed.%s" % TemplateExt(request),
    #                   extra_context={'dToday': todaystr()},
    #                )
    qsHosts = unixhost.objects.all()
    #return HttpResponse(qsHosts)
    return object_list(request,
                       queryset=qsHosts.order_by('name'),
                       template_name="elizabeth/listhosts.%s" % TemplateExt(request),
                       extra_context={'dToday': todaystr(),
                                      'qsHosts'     : qsHosts,
                                     },
                    )
   
def listunixUsers(request):
    #return object_list(request,
    #                   queryset=unixhost.objects.filter(hostsetting__installed=True).exclude(app__importance="L1").order_by('-hostsetting__installdate'),
    #                   template_name="elizabeth/installed.%s" % TemplateExt(request),
    #                   extra_context={'dToday': todaystr()},
    #                )
    qsHosts = unixuserlist.objects.all()      
    return object_list(request,
                       queryset=qsHosts.order_by('name'),
                       template_name="elizabeth/unixuserlist.%s" % TemplateExt(request),
                       extra_context={'dToday': todaystr(),
                                     'qsHosts'     : qsHosts,
                                     },
                    )    
    
    
def listwinHosts(request):
    #return object_list(request,
    #                   queryset=unixhost.objects.filter(hostsetting__installed=True).exclude(app__importance="L1").order_by('-hostsetting__installdate'),
    #                   template_name="elizabeth/installed.%s" % TemplateExt(request),
    #                   extra_context={'dToday': todaystr()},
    #                )
    qsHosts = winhost.objects.all()
    #return HttpResponse(qsHosts)
    return object_list(request,
                       queryset=qsHosts.order_by('name'),
                       template_name="elizabeth/listhosts.%s" % TemplateExt(request),
                       extra_context={'dToday': todaystr(),
                                      'qsHosts'     : qsHosts,
                                     },
                    )

def NewHosts(request):
    return object_list(request,
                       queryset=unixhost.objects.newhosts()
                    )

def DisableHosts(request):
    oneweekago = datetime.date.today() - datetime.timedelta(days=7)
    
    qs=unixhost.objects.all().filter(
        hostsetting__sshkeys = True,
        hostsetting__userlist = True,
        hostsetting__installed = True,
        hostsetting__delayed=False,
        level="PR",
        hostsetting__installdate__lte=oneweekago,
        unixuser__enabled = True,
        unixuser__user__disable = True
    ).distinct()

    #return object_list(request,
    #                   queryset=qs
    #                )
    return object_list(request,
                       queryset=qs,
                       template_name="elizabeth/unixhost_list.%s" % TemplateExt(request), 
                    )

def prHosts(request):
    # jfm, 3/19 - Adjust for L1 servers only
    #             use Q objects only, makes it easier.
    
    QProductionHosts = Q(level="PR", app__importance="L1")
    QProductionUsers = Q(user__type="U", host__level="PR")
    
    qs=unixhost.objects.filter(QProductionHosts).order_by("app__name")
    
    #ec={'nInstalled'    : unixhost.objects.filter(app__importance="L1", level="PR", hostsetting__installed=True).count(),
    #    'nNotInstalled' : unixhost.objects.filter(app_level="PR", hostsetting__installed=False, hostsetting__installdate__isnull=True).count(),
    #    'nScheduled'    : unixhost.objects.filter(level="PR", hostsetting__installed=False, hostsetting__installdate__isnull=False).count(),
    #    
    #    'nUserEnabled'  : unixuser.objects.filter(user__type="U", host__level="PR", enabled=True).count(),
    #    'nUserDisabled' : unixuser.objects.filter(user__type="U", host__level="PR", enabled=False).count(),
    #    
    #    'dToday'        : todaystr(),
    #}
    ec={'nInstalled'    : unixhost.objects.filter(QProductionHosts, hostsetting__installed=True).count(),
        'nNotInstalled' : unixhost.objects.filter(QProductionHosts, hostsetting__installed=False, hostsetting__installdate__isnull=True).count(),
        'nScheduled'    : unixhost.objects.filter(QProductionHosts, hostsetting__installed=False, hostsetting__installdate__isnull=False).count(),
        'nComplexDone'  : unixhost.objects.filter(QProductionHosts, hostsetting__complexity=True).count(),
        'nComplexNot'   : unixhost.objects.filter(QProductionHosts, hostsetting__complexity=False).count(),
        'nUserEnabled'  : unixuser.objects.filter(QProductionUsers, enabled=True).count(),
        'nUserDisabled' : unixuser.objects.filter(QProductionUsers, enabled=False).count(),
        
        'dToday'        : todaystr(),
    }
    
    return object_list(request,
                       queryset=qs,
                       template_name="elizabeth/prhosts.%s" % TemplateExt(request),
                       extra_context=ec
            )

def HostOSinfo(request):
    # return a list of which host's need their OS info filled in.
    queryset = unixhost.objects.all().filter(
            hostsetting__sshkeys=True,
            os__exact="",
        )
    return object_list(request,
                       queryset
                       )

##############################################################################################
# List all (unique) Windows users
##############################################################################################
def allwinusers(request):
    qs = winuserlist.objects.order_by('-type', 'username')
    return object_list(request,
                       queryset=qs,
                       extra_context={'dToday':todaystr() },
            )

##############################################################################################
# List all (unique) UNIX users
##############################################################################################    
def allunixusers(request):
    qs = unixuserlist.objects.order_by('-type', 'username')
    return object_list(request,
                       queryset=qs,
                       extra_context={'dToday':todaystr() },
            )

##############################################################################################
# John's wiki ninja'ing.
##############################################################################################
def wikivalues(request):
    # build a page with all our stats on the DB
    
    # jfm, switch to using Q objects, makes for simpler code and easy to maintain.
    
    #nHostTotal = unixhost.objects.all().count()
    QHosts = Q(app__importance="L1")
    nHostTotal = unixhost.objects.filter(QHosts).count()
    #qInstalled=unixhost.objects.filter(hostsetting__installed=True, hostsetting__installdate__isnull=False).order_by('hostsetting__installdate')
    qInstalled=unixhost.objects.filter(QHosts, hostsetting__installed=True,hostsetting__installdate__isnull=False).order_by('hostsetting__installdate')
    nHostInstalled = qInstalled.count()
    nHostRemaining = nHostTotal - nHostInstalled

    #nUserTotal = unixuser.objects.filter(user__type="U").count()
    QUsers = Q(user__type="U", host__app__importance="L1")      # only SOX L1 users
    nUserTotal = unixuser.objects.filter(QUsers).count()
    nUserDisabled = unixuser.objects.filter(QUsers, enabled = False).count()
    
    # now figure when stuff was / is going to be installed.  
    # create a dictionary with the year-month being the key, and count how many in each month.
    dDates = {
                '2008-12':0,
                '2009-01':0,
                '2009-02':0,
                '2009-03':0,
                '2009-04':0,
                '2009-05':0,
            }
    for s in qInstalled:
        datekey = s.hostsetting.installdate.strftime("%Y-%m")
        if dDates.has_key(datekey):
            dDates[datekey] += 1
        
    # dDates now contain the months when each was installed, need to sort it though
    lDateIndex = dDates.keys()
    lDateIndex.sort()

    lDateValues = []
    for x in lDateIndex:
        lDateValues.append( (x, dDates[x] ) )

    # create a dictionary of OS's installed
#    qOSGroup=unixhost.objects.filter(hostsetting__sshkeys=True)
    qOSGroup=unixhost.objects.filter(QHosts, hostsetting__sshkeys=True)
    dOS={}
    for s in qOSGroup:
        key = s.os
        if dOS.has_key(key):
            dOS[key] += 1
        else:
            dOS[key] = 1
    lOS=[]
    for x in dOS.keys():
        lOS.append( (x, dOS[x]))
    lOS.sort()

    # get the number of users disabled in each month
    dDates = {
            '2008-12':0,
            '2009-01':0,
            '2009-02':0,
            '2009-03':0,
            '2009-04':0,
            '2009-05':0,
    }
    #qDisabledUsers=unixuser.objects.filter(datedisabled__isnull=False)
    qDisabledUsers=unixuser.objects.filter(QUsers, datedisabled__isnull=False)
    for u in qDisabledUsers:
        key = u.datedisabled.strftime("%Y-%m")
        if dDates.has_key(key):
            dDates[key] += 1

    lDU = []
    for x in dDates.keys():
        lDU.append( ( x, dDates[x]))
    lDU.sort()
    
    return_context = {
                    'nHostTotal'        : nHostTotal,
                    'qInstalled'        : qInstalled, 
                    'nHostInstalled'    : nHostInstalled, 
                    'nHostRemaining'    : nHostRemaining,
                    'lDateValues'       : lDateValues,
                    'nUserTotal'        : nUserTotal, 
                    'nUserDisabled'     : nUserDisabled,
                    'nUserRemaining'    : nUserTotal - nUserDisabled,
                    'lOS'               : lOS,
                    'lDU'               : lDU,
                    'dToday'            : todaystr(),
                }
    
    return direct_to_template(request, template="elizabeth/wikivalues.html", extra_context=return_context)
    
def hostupdate(request):
    # this is called when someone visits /elizabeth/host/update/
    # look for various POST data
    
    host_result = ""
    host_name = request.POST['host_name']
    
    try:
        if request.method == 'POST':
            # find this host first, or add a new one.
            try:
                h = unixhost.objects.get(name=host_name)
            except unixhost.DoesNotExist:
                ## so add it!
                #h = unixhost()
                #h.name = host_name.lower()
                #host_result = "Added"
                return HttpResponse("Host %s does not exist, use Admin to add" % host_name)
            
            h.save()
            
            if "level" in request.POST:
                # the level parameter was sent, so update that setting
                h.level = request.POST['level']
                h.save()
                host_result += " level %s " % h.level
            
            if "osinfo" in request.POST:
                h.os = request.POST['osinfo']
                h.save()
                host_result += " osinfo %s" % h.os          
            
            h.save()    
            return HttpResponse("Updated Host: %s %s\n" % (h.name, host_result))
        else:
            try:
                h = unixhost.objects.get(name=host_name)
                return HttpResponse("%s\n" % h.hostname)
                
            except unixhost.DoesNotExist:
                return HttpResponse("Hostname %s not found\n" % host_name)
    except:
        return HttpResponse("Error in hostupdate")

##############################################################################################
# Update UNIX User
# Update an existing user, or create if it does not exist.
##############################################################################################
def unixuserupdate(request):
    
    # Start by gathering all variables in POST data
    if request.method == 'POST':
        if 'host_name' in request.POST:
            host_name = request.POST['host_name']
        else:
            host_name = ""
            
        if 'user' in request.POST:
            user      = username=request.POST['user']
        else:
            user      = "" 
        
        if 'osinfo' in request.POST:
            host_os   = request.POST['osinfo']
        else:
            host_os   = ""
        
        if 'enabled' in request.POST:
            enabled   = request.POST['enabled']
        else:
            enabled   = ""
        
        if 'lastlogin' in request.POST:
            lastlogin = request.POST['lastlogin']
        else:
            lastlogin = ""
            
        if 'datedisabled' in request.POST:
            datedisabled = request.POST['datedisabled']
        else:
            datedisabled = ""
        
        if 'dateremoved' in request.POST: 
            dateremoved = request.POST['dateremoved']
        else:
            dateremoved = ""
        
            
        print host_name, user, lastlogin, host_os
        
        # find this host first, or add a new one.
        try:
            h = unixhost.objects.get(name=host_name)
            if host_os:
                h.os = host_os
            h.save()
        except unixhost.DoesNotExist:
            # so add it!
            h = unixhost()
            h.name = host_name
            if host_os:
                h.os = host_os
            h.save()
            
        # new code to use userlist instead
        # make sure the user exists in the userlist table first

        if "user" in request.POST:
            # look it up in the userlist first.
            try:
                ul = unixuserlist.objects.get(username=request.POST['user'])
            except unixuserlist.DoesNotExist:
                ul = unixuserlist()
                ul.username = username=request.POST['user']
                ul.windowsid = ""
                ul.name = ""
                ul.type = "X"
                ul.enabled = True
                ul.source = ""
                ul.save()
                
            # so ul is the userlist user that we need to assign as a user to this host.
            try:
                u = h.unixuser_set.get(username=request.POST['user'])
            except unixuser.DoesNotExist:
                u = h.unixuser_set.create(username=request.POST['user'])

            u.user = ul
            u.lastscan = datetime.date.today()
            
            if lastlogin:
                if "DNE" not in str(lastlogin):
                    print "Last Login Time Retrieved", lastlogin[0:4], lastlogin[4:6], lastlogin[6:8],
                    u.lastlogin = datetime.date(int(lastlogin[0:4]), int(lastlogin[4:6]), int(lastlogin[6:8]))
                    #u.lastlogin = datetime.date(lastlogin[0:4], lastlogin[4:6], lastlogin[6:8])
            
            # datedisabled and dateremoved should only be set if the account is actually disabled.  also, these
            # values should not be reset after subsequent executions (ie: save only the first value...)
            if datedisabled:
                yr, mo, day = datedisabled.split("-")
                print "Date Disabled:",  yr, mo, day
                if u.datedisabled is None:
                    u.datedisabled = datetime.date(int(yr), int(mo), int(day))
                
            if dateremoved:
                yr, mo, day = dateremoved.split("-")
                print "Date Removed:",  yr, mo, day
                if u.dateremoved is None:
                    u.dateremoved = datetime.date(int(yr), int(mo), int(day))

            # check if the enabled field was given
            if "enabled" in request.POST:
                u.enabled = request.POST['enabled'] == "true"
                if u.enabled:
                    u.datedisabled = None
                    u.dateremoved  = None
                #if (u.datedisabled == None) and (u.user.type=="U") :
                #    u.datedisabled = datetime.date.today()
            
            u.save()

            return HttpResponse("%s, %s - %s\n" % (h.name, u.username, str(u.enabled) ) )

        else:
            return HttpResponse("No user given, oh well\n")
    else:
        return HttpResponse("HTTP GET, nothing here, move on")      


##############################################################################################
# Update WIN User
# Update an existing user, or create if it does not exist.
##############################################################################################

def winuserupdate(request):
    if request.method == 'POST':
        if 'host_name' in request.POST:
            host_name = request.POST['host_name']
        else:
            host_name = ""
            
        if 'user' in request.POST:
            user      = username=request.POST['user']
        else:
            user      = "" 
            
        if 'osinfo' in request.POST:
            host_os   = request.POST['osinfo']
        else:
            host_os   = ""
            
        if 'enabled' in request.POST:
            enabled   = request.POST['enabled']
        else:
            enabled   = ""
            
        if 'lastlogin' in request.POST:
            lastlogin = request.POST['lastlogin']
        else:
            lastlogin = ""
            
        if 'datedisabled' in request.POST:
            datedisabled = request.POST['datedisabled']
        else:
            datedisabled = ""
        
        if 'dateremoved' in request.POST: 
            dateremoved = request.POST['dateremoved']
        else:
            dateremoved = ""
            
        print host_name, user, lastlogin, host_os
        
        
        # find this host first, or add a new one.
        try:
            h = winhost.objects.get(name=host_name)
            if host_os:
                h.os = host_os
            h.save()
        except winhost.DoesNotExist:
            # so add it!
            h = winhost()
            h.name = host_name
            if host_os:
                h.os = host_os
            h.save()
            
        # new code to use userlist instead
        # make sure the user exists in the userlist table first

        if "user" in request.POST:
            # look it up in the userlist first.
            try:
                ul = winuserlist.objects.get(username=request.POST['user'])
            except winuserlist.DoesNotExist:
                ul = winuserlist()
                ul.username = username=request.POST['user']
                ul.windowsid = ""
                ul.name = ""
                ul.type = "X"
                ul.enabled = True
                ul.source = ""
                ul.save()

            # so ul is the userlist user that we need to assign as a user to this host.
            try:
                u = h.winuser_set.get(username=request.POST['user'])
            except winuser.DoesNotExist:
                u = h.winuser_set.create(username=request.POST['user'])

            u.user = ul
            u.lastscan = datetime.date.today()
            u.save()
            
            print "Last Login", lastlogin
            
            if lastlogin:
                if "DNE" not in str(lastlogin):
                    print "Did not equal DNE", lastlogin[0:4], lastlogin[4:6], lastlogin[6:8],
                    u.lastlogin = datetime.date(int(lastlogin[0:4]), int(lastlogin[4:6]), int(lastlogin[6:8]))
                    #u.lastlogin = datetime.date(lastlogin[0:4], lastlogin[4:6], lastlogin[6:8])
                else:
                    print "Equaled DNE"
                    
            # datedisabled and dateremoved should only be set if the account is actually disabled.  also, these
            # values should not be reset after subsequent executions (ie: save only the first value...)
            if datedisabled:
                yr, mo, day = datedisabled.split("-")
                print "Date Disabled:",  yr, mo, day
                if u.datedisabled is None:
                    u.datedisabled = datetime.date(int(yr), int(mo), int(day))
                
            if dateremoved:
                yr, mo, day = dateremoved.split("-")
                print "Date Removed:",  yr, mo, day
                if u.dateremoved is None:
                    u.dateremoved = datetime.date(int(yr), int(mo), int(day))

            # check if the enabled field was given
            if "enabled" in request.POST:
                u.enabled = request.POST['enabled'] == "true"
                if u.enabled:
                    u.datedisabled = None
                    u.dateremoved  = None
                #if (u.datedisabled == None) and (u.user.type=="U") :
                #    u.datedisabled = datetime.date.today()
            u.save()

            return HttpResponse("%s, %s - %s\n" % (h.name, u.username, str(u.enabled) ) )

        else:
            return HttpResponse("No user given, oh well\n")
    else:
        return HttpResponse("HTTP GET, nothing here, move on")      
    
    
##############################################################################################
# Import users into the database.
# ONLY UPDATE.  Do not add user if they do not already exist.
##############################################################################################
def readuser(request):
    if request.method == 'POST':
           
        if 'user' in request.POST:
            user      = username=request.POST['user']
        else:
            user      = "" 
            
        if 'tam' in request.POST:
            tam   = request.POST['tam']
        else:
            tam   = ""
            
        if 'account_type' in request.POST:
            account_type   = request.POST['account_type']
        else:
            account_type   = ""
            
        if 'enabled' in request.POST:
            enabled = request.POST['enabled']
            if enabled == "False":
                enabled = False
            else:
                enabled = True
        else:
            enabled = True
            
        if 'comments' in request.POST:
            comments = request.POST['comments']
        else:
            comments = ""

            
        print user, enabled
        
        # Find userlist
        
        flag=0

        if "user" in request.POST:
            # look it up in the userlist first.
            try:
                ul = unixuserlist.objects.get(username=user)
                flag = 1
            except unixuserlist.DoesNotExist:
                try:
                    ul = winuserlist.objects.get(username=user)
                except:
                    return HttpResponse("%s does not exist.\n" % (user) )
                    
            # if we get the user...
            ul.name = tam
            ul.type = account_type
            ul.source = comments
            ul.enabled = enabled
            ul.save()
            
            # if this came up as a unix account, we still need to see if it exists on the windows side
            if flag == 1:
                try:
                    ul = winuserlist.objects.get(username=user)
                except:
                    return HttpResponse("UNIX, %s, %s - %s\n" % (ul.username, ul.name, str(ul.enabled) ) )
                
                 # if we get the user...
                ul.name = tam
                ul.type = account_type
                ul.source = comments
                ul.enabled = enabled
                ul.save()
                return HttpResponse("BOTH, %s, %s - %s\n" % (ul.username, ul.name, str(ul.enabled) ) )
                
            else:
                return HttpResponse("Windows, %s, %s - %s\n" % (ul.username, ul.name, str(ul.enabled) ) )

        else:
            return HttpResponse("No user given, oh well\n")
    else:
        return HttpResponse("HTTP GET, nothing here, move on")      


##############################################################################################
# Associate hosts and apps using blaster_apps.py OGFS script
##############################################################################################
def addApp2Host(request):
    # this is called when someone visits /elizabeth/user/<host_name>?user=<username>&enabled=True
    # add a user to the server
    
    if request.method == 'POST':
        host_name = request.POST['host_name'].strip()
        app_name  = request.POST['app_name'].strip()
        
        print host_name, app_name

        # If App does not exist, add it.
        try:
            app = hostapp.objects.get(name=app_name)
        except hostapp.DoesNotExist:
            print "adding application"
            app = hostapp()
            app.name = app_name
            app.save()
            
        # If Host does not exist, quit.
        try:
            print "host: ", host_name, app.name
            # Check if it's a UNIX host first...
            host = unixhost.objects.get(name__startswith=host_name)
        except unixhost.DoesNotExist:
            try:
                print "try windows"
                # Try Windows next...
                host = winhost.objects.get(name__startswith=host_name)
            except winhost.DoesNotExist:
                print "except windows"
                print "host does not exist"
                return HttpResponse("Host %s does not exist.\n" % (host_name) )
        
        try:
            #  If host and app exist, associate them and save host object.
            host.apps.add(app)
            host.save()
            return HttpResponse("Added app %s to host %s" % (app.name, host.name))
        except:     
            return HttpResponse("Failed to add app %s to host %s" % (app.name, host.name))
        
    else:
        return HttpResponse("HTTP GET, nothing here, move on")           

##############################################################################################
# Add Applications to Elizabeth database
##############################################################################################
def addApp(request):
    # this is called when someone visits /elizabeth/user/<host_name>?user=<username>&enabled=True
    # add a user to the server
    
    if request.method == 'POST':
        # find this host first, or add a new one.
        app_name = request.POST['app_name']
        if "add" in request.POST:
            add = request.POST['add'] == "true"
        else:
            add = False
        
        try:
            app = hostapp.objects.get(name=app_name)
        except hostapp.DoesNotExist:
            # so add it!
            if add == True:
                app = hostapp()
                app.name = app_name
                if "importance" in request.POST:
                    try:
                        app.importance=request.POST['importance']
                    except:
                        return HttpResponse("Invalid Importance Level given." % (app.name))
                    app.save()
                    return HttpResponse("App %s added\n" % (app.name) )
            else:
                return HttpResponse("App %s already exists, will not update." % (app_name))
        else:
            # Update importance level if passed in
            if "importance" in request.POST:
                    try:
                        app.importance=request.POST['importance']
                    except:
                        return HttpResponse("Invalid Importance Level given." % (app.name))
            app.save()
            return HttpResponse("App %s updated\n" % (app.name) )
    else:
        return HttpResponse("HTTP GET, nothing here, move on")        


##############################################################################################
# List all users associated with a hostname, and indicates whether or not they should be 
# active on the box according to the userlists.
##############################################################################################
def listusers(request, host_name):
     
    try:
        qs = unixhost.objects.get(name__icontains=host_name.lower())
        s = "unix"
    except:
        try:
            qs = winhost.objects.get(name__startswith=host_name.lower())
            s = "win"
        except:
            return HttpResponse("Host %s not in database" % host_name)
            
    users  = eval("qs."+s+"user_set.all()")

    for i in users:
        print "username: ", i.user.username, i.user.enabled       
    
    return render_to_response('elizabeth/listusers.html', {'userlist': users})


##############################################################################################
# List user accounts that need to be disabled 
##############################################################################################
def listdisabledusers(request, host_name):
    queryset = unixuser.objects.filter( host__name__icontains = host_name, user__enabled = False, user__type = "U")
    if not queryset:
        print "here"
        queryset = winuser.objects.filter( host__name__icontains = host_name, user__enabled = False, user__type = "U")
    if not queryset:
        return HttpResponse("")
    
    # print out to webserver console for debugging...
    for i in queryset:
        print "username: ", i.user.username, i.user.enabled       
    
    return render_to_response('elizabeth/listusers.html', {'userlist': queryset})    

##############################################################################################
# List user accounts that need to be removed 
##############################################################################################
def listremovedusers(request, host_name):
    day_delay= 0
    
    # find users accounts that are already disabled on host_name
    queryset = unixuser.objects.filter(host__name__icontains = host_name, enabled=False, user__enabled = False, user__type = "U")
    #queryset = unixuser.objects.filter( host__name__icontains = host_name, user__enabled = False, user__type = "U", 
    #                                    datedisabled__lte=datetime.date.today()-timedelta(days=day_delay))
    if not queryset:
        # we're deleting all disabled users on the windows hosts.  no checks.  cross your fingers...
        queryset = winuser.objects.filter(host__name__icontains = host_name, enabled=False)
        
        # , user__enabled = False, user__type = "U")
        
        #queryset = winuser.objects.filter( host__name__icontains = host_name, user__enabled = False, user__type = "U",
        #                                   datedisabled__lte=datetime.date.today()-timedelta(days=day_delay))
    if not queryset:
        return HttpResponse("")
    
    # print out to webserver console for debugging...
    for i in queryset:
        print "username: ", i.user.username, i.user.enabled       
    
    return render_to_response('elizabeth/listusers.html', {'userlist': queryset})    

##############################################################################################
# List all SOX L1
##############################################################################################    
def allsox(request):
    QProductionHosts = Q(app__importance="L1")
    qs=unixhost.objects.filter(QProductionHosts).order_by("app__name")
    
    ec={'dToday'        : todaystr(), }
    
    return object_list(request,
                       queryset=qs,
                       template_name="elizabeth/allsox.%s" % TemplateExt(request),
                       extra_context=ec
            )



##############################################################################################
#
#  ********The remaining views are being used for the sept 9, 2011 disabling  *********
#
##############################################################################################

    
    
##############################################################################################
# List all windows and unix hosts associated with the apps in Group 1
##############################################################################################    
def group1(request):
    Qapps = Q(name="SSO") | \
            Q(name="Aloha (Food Point of Sale)") |\
            Q(name="Cambar") |\
            Q(name="Comshare") |\
            Q(name="Strata (CPG)") |\
            Q(name="EATEC") |\
            Q(name="EventBuilder") |\
            Q(name="Music Tracker") |\
            Q(name="OPERATIONAL DATA STORE (ODS)") |\
            Q(name="PT (Pay TV AR)") |\
            Q(name="SAFE") |\
            Q(name="STAR") |\
            Q(name="STING") |\
            Q(name="TM (Title Management)") |\
            Q(name="Unistar (TDS2000)") |\
            Q(name="VGS (POS)") |\
            Q(name="MACCS") |\
            Q(name="Tibco") |\
            Q(name="Gentran Integration Suite(EDI) - Intl") |\
            Q(name="Gentran Integration Suite(EDI) - Domestic")
            #Q(name="") |\
            
    
    qs=hostapp.objects.filter(Qapps)
    
    winlist = []
    unixlist = []
    
    for q in qs:
        unixlist = unixlist + list(q.unixhost_set.all())
        #for u in unixhosts:
        #    unixlist.append(u)
        
        winlist = winlist + list(q.winhost_set.all())
        #for w in winlist:
        #    winlist.append(w)
        
    
    print "winhosts", winlist
    print "unixhosts", unixlist        
    
    return render_to_response('elizabeth/apphosts.html', {'winlist': winlist, 'unixlist': unixlist}) 


##############################################################################################
# List all windows and unix hosts associated with the apps in Group 2
##############################################################################################    
def group2(request):
    Qapps = Q(name="Paris") |\
            Q(name="OpenTV Participate") |\
            Q(name="Vista_0984") |\
            Q(name="TRANSWORKS") |\
            Q(name="STORM") |\
            Q(name="SOLAR") |\
            Q(name="Siemens") |\
            Q(name="ScheduALL - MTC (SatOps)") |\
            Q(name="ScheduALL - NOC") |\
            Q(name="ScheduAll - Production Services") |\
            Q(name="SCHEDUALL - SOUND") |\
            Q(name="SCHEDUALL - TECH OPS") |\
            Q(name="Rental Works Editorial Facilities") |\
            Q(name="RENTAL WORKS NBCU UNIVERSAL") |\
            Q(name="Rental Tracker Pro - Albuquerque Costume") |\
            Q(name="RENTAL TRACKER PRO - COSTUME/PROPERTY") |\
            Q(name="Media Village") |\
            Q(name="Maximo") |\
            Q(name="Mastermind") |\
            Q(name="Lenel") |\
            Q(name="Lightbox") |\
            Q(name="Geoffrey") |\
            Q(name="Gateworks") |\
            Q(name="Enterprise OMS") |\
            Q(name="DSR (Digital Screening Room)") |\
            Q(name="Asset Tracker") |\
            Q(name="AMAG") |\
            Q(name="HEDWay") |\
            Q(name="WideOrbit") |\
            Q(name="VCI Orion Entertainment") |\
            Q(name="Urgent Messaging") |\
            Q(name="TVROCS") |\
            Q(name="Startover") |\
            Q(name="Research Datawarehouse") |\
            Q(name="OSI - TRAFFIC & BILLING (TELEMUNDO)") |\
            Q(name="IDEAL") |\
            Q(name="Gabriel Oxygen") |\
            Q(name="Gabriel USA SciFi") |\
            Q(name="Gabriel WS Bridge (Oxygen)") |\
            Q(name="Gabriel WS Bridge (USA/SF)") |\
            Q(name="Dealmaker Barter Sales Syndication 02") |\
            Q(name="Dealmaker Bravo") |\
            Q(name="Dealmaker Cable News") |\
            Q(name="Dealmaker Telemundo") |\
            Q(name="Data Warehouse") |\
            Q(name="COMPASS Juice") |\
            Q(name="COMPASS") |\
            Q(name="Cable ADU") |\
            Q(name="Affiliate Partnership Tool (APT)") |\
            Q(name="Affiliate Sales Toolkit (Billing Module)") |\
            Q(name="2E")
            #Q(name="") |\
            
    
    qs=hostapp.objects.filter(Qapps)
    
    winlist = []
    unixlist = []
    
    for q in qs:
        unixlist = unixlist + list(q.unixhost_set.all())
        #for u in unixhosts:
        #    unixlist.append(u)
        
        winlist = winlist + list(q.winhost_set.all())
        #for w in winlist:
        #    winlist.append(w)
        
    
    print "winhosts", winlist
    print "unixhosts", unixlist        
    
    return render_to_response('elizabeth/apphosts.html', {'winlist': winlist, 'unixlist': unixlist}) 


##############################################################################################
# List all windows and unix hosts associated with the apps in Group 3
##############################################################################################    
def group3(request):
    Qapps = Q(name="Paris") |\
            Q(name="LOUISE") |\
            Q(name="Informatica") |\
            Q(name="Elements (JD Edwards)") |\
            Q(name="TIMEKEEPER") |\
            Q(name="PPMC") |\
            Q(name="PeopleSoft HRMS 7.5") |\
            Q(name="Peoplesoft 8.4") |\
            Q(name="Oasis") |\
            Q(name="FLIX") |\
            Q(name="COMMON STAGING PLATFORM")
            #Q(name="") |\
            
    
    qs=hostapp.objects.filter(Qapps)
    
    winlist = []
    unixlist = []
    
    for q in qs:
        unixlist = unixlist + list(q.unixhost_set.all())
        #for u in unixhosts:
        #    unixlist.append(u)
        
        winlist = winlist + list(q.winhost_set.all())
        #for w in winlist:
        #    winlist.append(w)
        
    
    print "winhosts", winlist
    print "unixhosts", unixlist        
    
    return render_to_response('elizabeth/apphosts.html', {'winlist': winlist, 'unixlist': unixlist}) 

