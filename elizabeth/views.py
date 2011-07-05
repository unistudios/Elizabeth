import datetime
import sys

from django.http import HttpResponse
from django.views.generic.list_detail import *
from django.views.generic.simple import *
from django.db.models import Q

from website.elizabeth.models import *

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

def allusers(request):
    qs = userlist.objects.order_by('-type', 'username')
    return object_list(request,
                       queryset=qs,
                       extra_context={'dToday':todaystr() },
            )

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

def userupdate(request, host_name):
    # this is called when someone visits /elizabeth/user/<host_name>?user=<username>&enabled=True
    # add a user to the server
    
    if request.method == 'POST':
        # find this host first, or add a new one.
        
        try:
            h = unixhost.objects.get(name=host_name)
        except unixhost.DoesNotExist:
            # so add it!
            h = unixhost()
            h.name = host_name
            h.save()

        # new code to use userlist instead
        # make sure the user exists in the userlist table first
        
        if "user" in request.POST:
            # look it up in the userlist first.
            try:
                ul = userlist.objects.get(username=request.POST['user'])
            except userlist.DoesNotExist:
                ul = userlist()
                ul.username = username=request.POST['user']
                ul.windowsid = ""
                ul.name = ""
                ul.type = "X"
                ul.disable = False
                ul.source = ""
                ul.save()

            # so ul is the userlist user that we need to assign as a user to this host.                 
            try:
                u = h.unixuser_set.get(username=request.POST['user'])
            except unixuser.DoesNotExist:
                u = h.unixuser_set.create(username=request.POST['user'])
                
            u.user = ul
            u.save()
                
            # check if the enabled field was given
            if "disabled" in request.POST:
                u.enabled = request.POST['disabled'] != "true"

                if (u.datedisabled == None) and (u.user.type=="U") :
                    u.datedisabled = datetime.date.today()
                u.save()

            return HttpResponse("%s, %s - %s\n" % (h.name, u.username, str(u.enabled) ) )

        else:
            return HttpResponse("No user given, oh well\n")
    else:
        return HttpResponse("HTTP GET, nothing here, move on")

def linuxuserupdate(request):
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
            u.save()
            
            if lastlogin:
                if "DNE" not in str(lastlogin):
                    print "Did not equal DNE", lastlogin[0:4], lastlogin[4:6], lastlogin[6:8],
                    u.lastlogin = datetime.date(int(lastlogin[0:4]), int(lastlogin[4:6]), int(lastlogin[6:8]))
                    #u.lastlogin = datetime.date(lastlogin[0:4], lastlogin[4:6], lastlogin[6:8])
                    u.save()
                else:
                    print "Equaled DNE"

            # check if the enabled field was given
            if "enabled" in request.POST:
                u.enabled = request.POST['enabled'] == "true"
                #if (u.datedisabled == None) and (u.user.type=="U") :
                #    u.datedisabled = datetime.date.today()
                u.save()

            return HttpResponse("%s, %s - %s\n" % (h.name, u.username, str(u.enabled) ) )

        else:
            return HttpResponse("No user given, oh well\n")
    else:
        return HttpResponse("HTTP GET, nothing here, move on")      

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
            u.save()
            
            if lastlogin:
                if "DNE" not in str(lastlogin):
                    print "Did not equal DNE", lastlogin[0:4], lastlogin[4:6], lastlogin[6:8],
                    u.lastlogin = datetime.date(int(lastlogin[0:4]), int(lastlogin[4:6]), int(lastlogin[6:8]))
                    #u.lastlogin = datetime.date(lastlogin[0:4], lastlogin[4:6], lastlogin[6:8])
                    u.save()
                else:
                    print "Equaled DNE"

            # check if the enabled field was given
            if "enabled" in request.POST:
                u.enabled = request.POST['enabled'] == "true"
                #if (u.datedisabled == None) and (u.user.type=="U") :
                #    u.datedisabled = datetime.date.today()
                u.save()

            return HttpResponse("%s, %s - %s\n" % (h.name, u.username, str(u.enabled) ) )

        else:
            return HttpResponse("No user given, oh well\n")
    else:
        return HttpResponse("HTTP GET, nothing here, move on")      


# Add hosts to different apps using blaster_apps.py OGFS script
def addApp2Host(request):
    # this is called when someone visits /elizabeth/user/<host_name>?user=<username>&enabled=True
    # add a user to the server
    
    if request.method == 'POST':
        host_name = request.POST['host_name'].strip()
        app_name  = request.POST['app_name'].strip()
        
        print host_name, app_name

        # If App does not exist, add it.
        try:
            app = unixapp.objects.get(name=app_name)
        except unixapp.DoesNotExist:
            print "adding application"
            app = unixapp()
            app.name = app_name
            app.save()
            
        # If Host does not exist, quit.
        try:
            print "host: ", host_name, app.name
            host = unixhost.objects.get(name__startswith=host_name)
        except unixhost.DoesNotExist:
            print "host does not exist"
            return HttpResponse("Host %s does not exist.\n" % (host.name) )
        else:
            #  If host and app exist, associate them and save host object.
            host.apps.add(app)
            host.save()
            return HttpResponse("Added app %s to host %s" % (app.name, host.name))     
        return HttpResponse("Failed to add app %s to host %s" % (app.name, host.name))
        
    else:
        return HttpResponse("HTTP GET, nothing here, move on")           

# Add Applications to Elizabeth database
def addApp(request):
    # this is called when someone visits /elizabeth/user/<host_name>?user=<username>&enabled=True
    # add a user to the server
    
    if request.method == 'POST':
        # find this host first, or add a new one.
        app_name = request.POST['app_name']

        try:
            app = unixapp.objects.get(name=app_name)
            return HttpResponse("App already exists.\n")
        except unixapp.DoesNotExist:
            # so add it!
            app = unixapp()
            app.name = app_name
            app.save()

            return HttpResponse("App %s added\n" % (app.name) )

        else:
            return HttpResponse("Failure.\n")
    else:
        return HttpResponse("HTTP GET, nothing here, move on")        
        
def userdisablelist(self, host_name):
    queryset = unixuser.objects.all().filter(   enabled=True,
                                                host__hostsetting__delayed=False,
                                                host__name=host_name,
                                                user__disable=True
                                            )
    
    return object_list(self, queryset)
    
def allsox(request):
    QProductionHosts = Q(app__importance="L1")
    qs=unixhost.objects.filter(QProductionHosts).order_by("app__name")
    
    ec={'dToday'        : todaystr(), }
    
    return object_list(request,
                       queryset=qs,
                       template_name="elizabeth/allsox.%s" % TemplateExt(request),
                       extra_context=ec
            )
