import datetime

from django.http import HttpResponse
from django.views.generic.list_detail import *
from django.views.generic.simple import *
from django.db.models import Q

from website.likewise.models import *

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
                              template="likewise/index.html",
                              extra_context={},
                            )   

def installed(request):
    return object_list(request,
                       queryset=unixhost.objects.filter(hostsetting__installed=True,
                                                        app__importance="L1"). order_by('-hostsetting__installdate'),
                       template_name="likewise/installed.%s" % TemplateExt(request),
                       extra_context={'dToday': todaystr()},
                    )
def hostlist_run(request):
    #return object_list(request,
    #                   queryset=unixhost.objects.filter(hostsetting__installed=True).exclude(app__importance="L1").order_by('-hostsetting__installdate'),
    #                   template_name="likewise/installed.%s" % TemplateExt(request),
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
                       template_name="likewise/hostlist_run.%s" % TemplateExt(request),
                       extra_context={'dToday': todaystr(),
                                      'nRunHostsInstalled'     : nRunHostsInstalled,
                                      'nRunHostsRemaining'     : nRunHostsRemaining,
                                      'nRunUsersEnabled'       : nRunUsersEnabled, 
                                      'nRunUsersDisabled'      : nRunUsersDisabled,
                                     },
                    )

def kyle_test(request):
    #return object_list(request,
    #                   queryset=unixhost.objects.filter(hostsetting__installed=True).exclude(app__importance="L1").order_by('-hostsetting__installdate'),
    #                   template_name="likewise/installed.%s" % TemplateExt(request),
    #                   extra_context={'dToday': todaystr()},
    #                )
    qsRunHosts = unixhost.objects.exclude(app__importance="L2")
    nRunHostsInstalled = qsRunHosts.filter(hostsetting__installed=True).count()
    nRunHostsRemaining = qsRunHosts.filter(hostsetting__installed=False).count()
    
    qsRunUsers = unixuser.objects.exclude(host__app__importance="L1")
    nRunUsersEnabled = qsRunUsers.filter(enabled=True).count()
    nRunUsersDisabled = qsRunUsers.filter(enabled=False).count()

    return object_list(request,
                       queryset=qsRunHosts.order_by('-hostsetting__installdate'),
                       template_name="likewise/kyle_test.%s" % TemplateExt(request),
                       extra_context={'dToday': todaystr(),
                                      'nRunHostsInstalled'     : nRunHostsInstalled,
                                      'nRunHostsRemaining'     : nRunHostsRemaining,
                                      'nRunUsersEnabled'       : nRunUsersEnabled, 
                                      'nRunUsersDisabled'      : nRunUsersDisabled,
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
                       template_name="likewise/unixhost_list.%s" % TemplateExt(request), 
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
                       template_name="likewise/prhosts.%s" % TemplateExt(request),
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
    
    return direct_to_template(request, template="likewise/wikivalues.html", extra_context=return_context)
    
def hostupdate(request, host_name):
    # this is called when someone visits /likewise/host/<host_name>
    # look for various POST data
    
    host_result = ""
    
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
            
            if "userlist" in request.POST:
                # the setuserlist parameter was sent, so update that setting
                h.hostsetting.userlist = request.POST['userlist'] == "true"
                h.hostsetting.save()
                host_result += " userlist %s " % str(h.hostsetting.userlist)
            
            if "osinfo" in request.POST:
                h.os = request.POST['osinfo']
                h.save()
                host_result += " osinfo %s" % h.os          
                
            return HttpResponse("%s %s\n" % (h.name, host_result))
        else:
            try:
                h = unixhost.objects.get(name=host_name)
                return HttpResponse("%s\n" % h.hostname)
                
            except unixhost.DoesNotExist:
                return HttpResponse("Hostname %s not found\n" % host_name)
    except:
        return HttpResponse("Error in hostupdate")

def userupdate(request, host_name):
    # this is called when someone visits /likewise/user/<host_name>?user=<username>&enabled=True
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
                       template_name="likewise/allsox.%s" % TemplateExt(request),
                       extra_context=ec
            )
