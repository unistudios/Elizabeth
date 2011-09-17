# views for reporting
from django.views.generic.list_detail import object_list
from django.views.generic.simple import direct_to_template
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from website.elizabeth.models import *
from django.db.models import Q
from itertools import chain
import datetime

##############################################################################################
# Values for wiki page
##############################################################################################

def todaystr():
    return datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p")


def user_summary(request):   
    ################################################################
    # Calculate the types of users across scanned environment
    ################################################################
        
    unix_disableable = unixuser.objects.filter(enabled=True, user__type="U", user__enabled=False)
    win_disableable = winuser.objects.filter(enabled=True, user__type="U", user__enabled=False)
    
    unix_removable = unixuser.objects.filter(enabled=False, user__type="U", user__enabled=False)
    win_removable = winuser.objects.filter(enabled=False, user__type="U", user__enabled=False)
    
    unix_sysaccts = unixuser.objects.filter(user__type="S")
    win_sysaccts = winuser.objects.filter(user__type="S")
    
    unix_appaccts = unixuser.objects.filter(user__type="A")
    win_appaccts = winuser.objects.filter(user__type="A")
    
    unix_unkaccts = unixuser.objects.filter(user__type="X")
    win_unkaccts = winuser.objects.filter(user__type="X")
    
    
    unix_disableable_count = unix_disableable.count()
    win_disableable_count = win_disableable.count()
    total_disableable_count = unix_disableable_count + win_disableable_count
    
    unix_removable_count = unix_removable.count()
    win_removable_count = win_removable.count()
    total_removable_count = unix_removable_count + win_removable_count
    
    # local system accounts
    unix_sysaccts_count = unix_sysaccts.count()
    win_sysaccts_count = win_sysaccts.count()
    total_sysaccts_count =  unix_sysaccts_count + win_sysaccts_count
    
    # local app accounts
    unix_appaccts_count = unix_appaccts.count()
    win_appaccts_count = win_appaccts.count()
    total_appaccts_count =  unix_appaccts_count + win_appaccts_count

    # local unknown accounts
    unix_unkaccts_count = unix_unkaccts.count()
    win_unkaccts_count = win_unkaccts.count()
    total_unkaccts_count =  unix_unkaccts_count + win_unkaccts_count
    
    # All Accounts
    total_accts_count = total_disableable_count + total_removable_count + total_sysaccts_count + total_appaccts_count + total_unkaccts_count
    
    
     ################################################################
    # Calculate the account status across scanned accounts
    ################################################################
    
    
    # update directly from webpage... maybe later...
    #t = get_template("elizabeth/reporting/user_summary.html")
    #c = {'queryset': disabled_user_pending,
    #                'total_useraccts_count': total_useraccts_count,
    #                'total_sysaccts_count': total_sysaccts_count,
    #                'total_appaccts_count': total_appaccts_count,
    #                'total_unkaccts_count': total_unkaccts_count,
    #                'total_accts_count': total_accts_count,
    #}
    #return HttpResponse(t.render(Context(c)))
       
    return direct_to_template(request,
                              template="elizabeth/reporting/user_summary.html",
                              extra_context={'total_disableable_count': total_disableable_count,
                                      'total_removable_count': total_removable_count, 
                                      'total_sysaccts_count': total_sysaccts_count,
                                      'total_appaccts_count': total_appaccts_count,
                                      'total_unkaccts_count': total_unkaccts_count,
                                      'total_accts_count': total_accts_count,
                                      'date_today': todaystr(),                                
                                     },
                    )