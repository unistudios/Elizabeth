import datetime
import csv
import random

from django.http                      import HttpResponse
from django.views.generic.list_detail import object_detail, object_list
from django.views.generic.simple      import direct_to_template
from django.db.models                 import Q
from django.core.exceptions           import ValidationError
from django.shortcuts                 import get_object_or_404
from django.db.models                 import Avg, Max, Min, Count
from django.db.models                 import Q
from django.core.paginator            import Paginator, InvalidPage, EmptyPage

from opsware.models import Server, ENV_CHOICES, STATUS_CHOICES

def opsware(request):
    return direct_to_template(request, template='opsware/opsware.html')
    

def csv_response(request, queryset):
    # Create the HttpResponse object with the appropriate CSV header.
    # a modified example from djangoproject.com (http://docs.djangoproject.com/en/dev/howto/outputting-csv/)
    
    if queryset.count() > 0:
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=readylist.csv'
    
        writer = csv.writer(response)
        writer.writerow(['id','name'])
        for row in queryset:
             writer.writerow([row.id, row.name])
        
        return response
    else:
        return HttpResponse("")

def server_update(request, server_id):
    s = get_object_or_404(Server, pk=server_id)
    
    if request.POST:
        workdone = ""
       
        if "ip" in request.POST:
            s.ipaddr = request.POST['ip']
            s.save()
            workdone += "ip address updated,"
            
        if "name" in request.POST:
            s.name = request.POST['name']
            s.save()
            workdone += "name updated,"
            
        if "os" in request.POST:
            s.name = request.POST['name']
            s.save()
            workdone += "os updated,"
            
        if "errors" in request.POST:
            s.errors = True
            s.save()
            workdone += "error,"
            
        if "notes" in request.POST:
            s.ournotes = request.POST["notes"]
            s.save()
            workdone += "notes recorded"
            
        if "installed" in request.POST:
            s.installed = True
            s.save()
            workdone += "installed"
            
        return HttpResponse("Server id %s found, %s - %s" % (s.id, s.name, workdone) )
    else:
        return HttpResponse("ID %s is server %s" % (s.id, s.name) )

#def all(request):
#    
#    queryset = Server.objects.all()
#    
#    return object_list(request,
#                       queryset, 
#                       template_name="opsware/all.html",
#                    )

def all(request):
    server_list = Server.objects.all()
    paginator = Paginator(server_list, 50) # Show num contacts per page

    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        servers = paginator.page(page)
    except (EmptyPage, InvalidPage):
        servers = paginator.page(paginator.num_pages)

    #return render_to_response('list.html', {"servers": servers}
    #                          )

    ec = {'servers' : servers,
          'server_total' : server_list.count(),
          }
    
    return object_list(request,
                       servers.object_list, 
                       template_name="opsware/all.html",
                       extra_context=ec,
                    )


def list(request):
    # see if we got the parameter we need
    if "type" in request.REQUEST:
        if request.REQUEST["type"] == "all":
            return list_all(request)
            
        elif request.REQUEST["type"] == "ready":
            return list_ready(request)
            
        elif request.REQUEST["type"] == "hold":
            return list_hold(request)
            
        elif request.REQUEST["type"] == "noip":
            return list_noip(request)
    else:
        return HttpResponse("no type specified")

def list_noip(request):
    try:
        queryset = Server.objects.exclude(
                    ipaddr__contains="."
                    ).filter(errors=False)

        return csv_response(request, queryset)
        
    except ValidationError:
        return HttpResponse("list_noip: queryset Error")

def list_ready(request):
    if (not "date" in request.REQUEST) or (not "os" in request.REQUEST):
        return HttpResponse("you must specify a date and os parameter")
    
    try:
        queryset = Server.objects.filter(
                                         install_date = request.REQUEST['date'],
                                         installed = False,
                                         errors=False,
                                         onhold=False,
                                         os = request.REQUEST['os']
                                        )
        return csv_response(request, queryset)
        
    except ValidationError:
        return HttpResponse("list_ready, queryset Error")

def list_all(request):
    return HttpResponse("stub for %s" % __name__ + ".list_all")

def list_hold(request):
    return HttpResponse("stub for %s" % __name__ + ".list_hold")


def chartdata(request):
    # main URL view for giving back the XML template
    
    queryset = None
    template = None
    args_dict = {}
    
    if "xml" in request.REQUEST:
        # a template name was given
        
        if request.REQUEST['xml'] == "deployedbydate":
            totals = {}
            runningtotal=0
            queryset = Server.objects.filter(installed=True).values("install_date").annotate(install_count=Count("install_date")).order_by("install_date")
            # now loop through the dates, and calc the total.
            for x in queryset:
                runningtotal += x['install_count']
                totals[ x['install_date'] ] = runningtotal
                
            template = "charts/deployedbydate.xml"
            args_dict = {'totalbydate' : totals,
                    }

        # DEPLOYED BY OS            
        elif request.REQUEST['xml'] == "deployedbyos":
            queryset = Server.objects.filter(installed=True).values("os").annotate(os_count=Count("os")).order_by("os")
            template = "charts/deployedbyos.xml"
            args_dict = {'total_servers': Server.objects.filter(installed=True).count(),
                   }

        # ALL STATUS
        elif request.REQUEST['xml'] == "allstatus":
            # create a dictionary of our status and zero values for now.
            all_status = {}
            for x in STATUS_CHOICES:
                all_status[x[0]] = {'name': x[1], 'count' : 0}
            
            queryset = Server.objects.values("status").annotate(count=Count("status")).order_by("status")
            for x in queryset:
                all_status[x['status']]['count'] = x['count']
                
            template = "charts/allstatus.xml"
            args_dict = {'status':all_status}

        # DEPLOYED ALL
        elif request.REQUEST['xml'] == "deployedall":
            #queryset = Server.objects.filter(installed=True).values("os").annotate(os_count=Count("os")).order_by("os")
            data = Server.objects.values('env','status').annotate(Count('env'))
            queryset = Server.objects.filter(env=None)
            
            # zero out our Cross-Reference matrix
            xref = {}
            for x in STATUS_CHOICES:
                xref[x[1]] = {}
                for y in ENV_CHOICES:
                    xref[x[1]][y[1]] = 0

            # Now fill it in with valid data
            
            #convert our stuff to dicts for quick lookup
            sc = dict(STATUS_CHOICES)
            ec = dict(ENV_CHOICES)
            for d in data:
                xref[sc[d['status']]][ec[d['env']]] = d['env__count']

            template = "charts/deployedall.xml"
            args_dict = {'xref'   : xref,
                    }

        # PENDING DEPLOYMENT
        elif request.REQUEST['xml'] == "deploypending":
            QPending = Q(errors=False, installed=False)
            
            queryset = Server.objects.exclude(install_date=None).filter(QPending).values('install_date').annotate(install_count=Count('install_date')).order_by("install_date")
                        
            template = "charts/deploypending.xml"

        # Didn't find an XML Match
        else:
            return HttpResponse("NO match for XML name of %" % request.REQUEST['xml'])



        #
        # See if we have the data setup, if not, fail.
        #
        if queryset <> None and template <> None:
            # call the template with the queryset.
            return object_list(request,
                               queryset, 
                               template_name="opsware/%s" % template,
                               extra_context = args_dict,
                              )
        else:
            return HttpResponse("No queryset or data setup for %s parameter" % request.REQUEST['xml'])
    
    else:
        return HttpResponse("xml parameter not specified")


def chartstatus(request):
    return direct_to_template(request, 'opsware/chartstatus.html')
 
def chartdeploybydate(request):
    return direct_to_template(request, 'opsware/chartdeploybydate.html',)

#    
#def chartdeploybydatedata(request):
#    # figure out how many we've deployed by date
#    queryset = Server.objects.filter(installed=True).values("install_date").annotate(install_count=Count("install_date") ).order_by("install_date")
#
#    return object_list(request,
#                   queryset, 
#                   template_name="opsware/chartdeploybydatedata.html",
#                )
