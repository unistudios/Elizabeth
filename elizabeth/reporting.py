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
    """
    Calculate the types of users across scanned environment
    """
    
    unix_disableable = unixuser.objects.filter(enabled=True, user__type="U", user__enabled=False, dateremoved__isnull=True, datedisabled__isnull=True, host__retired=False)
    win_disableable = winuser.objects.filter(enabled=True, user__type="U", user__enabled=False, dateremoved__isnull=True, datedisabled__isnull=True, host__retired=False)
    
    unix_removable = unixuser.objects.filter(enabled=False, user__type="U", user__enabled=False, dateremoved__isnull=True, host__retired=False)
    win_removable = winuser.objects.filter(enabled=False, user__type="U", user__enabled=False, dateremoved__isnull=True, host__retired=False)
    
    unix_sysaccts = unixuser.objects.filter(user__type="S", host__retired=False)
    win_sysaccts = winuser.objects.filter(user__type="S", host__retired=False)
    
    unix_appaccts = unixuser.objects.filter(user__type="A", host__retired=False)
    win_appaccts = winuser.objects.filter(user__type="A", host__retired=False)
    
    unix_unkaccts = unixuser.objects.filter(user__type="X", host__retired=False)
    win_unkaccts = winuser.objects.filter(user__type="X", host__retired=False)
    
    
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
    
    # All Removed Accounts
    total_removed_count = unixuser.objects.filter(user__type="U", dateremoved__isnull=False).count() + \
                                 winuser.objects.filter(user__type="U", dateremoved__isnull=False).count()
    
    # All Accounts
    total_accts_count = total_removed_count + total_disableable_count + total_removable_count + total_sysaccts_count + total_appaccts_count + total_unkaccts_count
    
    
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
                                      'total_removed_count': total_removed_count,
                                      'date_today': todaystr(),                                
                                     },
                    )
    
    
    
    
def user_type_summary(request):
    """
    Just show the various account types for display on the "Account Types" wiki page.        
    """
    ################################################################
    # Calculate the types of users across scanned environment
    ################################################################
    
    # local user accounts
    unix_usraccts_count = unixuser.objects.filter(enabled=True, user__type="U", host__retired=False, dateremoved__isnull=True, datedisabled__isnull=True).count()
    win_usraccts_count = winuser.objects.filter(enabled=True, user__type="U", host__retired=False, dateremoved__isnull=True, datedisabled__isnull=True).count()
    total_usraccts_count =  unix_usraccts_count + win_usraccts_count
    
    # local system accounts
    unix_sysaccts_count = unixuser.objects.filter(enabled=True, user__type="S", host__retired=False, dateremoved__isnull=True, datedisabled__isnull=True).count()
    win_sysaccts_count = winuser.objects.filter(enabled=True, user__type="S", host__retired=False, dateremoved__isnull=True, datedisabled__isnull=True).count()
    total_sysaccts_count =  unix_sysaccts_count + win_sysaccts_count
    
    # local app accounts
    unix_appaccts_count = unixuser.objects.filter(enabled=True, user__type="A", host__retired=False, dateremoved__isnull=True, datedisabled__isnull=True).count()
    win_appaccts_count = winuser.objects.filter(enabled=True, user__type="A", host__retired=False, dateremoved__isnull=True, datedisabled__isnull=True).count()
    total_appaccts_count =  unix_appaccts_count + win_appaccts_count

    # local unknown accounts
    unix_unkaccts_count = unixuser.objects.filter(enabled=True, user__type="X", host__retired=False, dateremoved__isnull=True, datedisabled__isnull=True).count()
    win_unkaccts_count = winuser.objects.filter(enabled=True, user__type="X", host__retired=False, dateremoved__isnull=True, datedisabled__isnull=True).count()
    total_unkaccts_count =  unix_unkaccts_count + win_unkaccts_count
    
    # All Accounts
    total_accts_count = total_sysaccts_count + total_appaccts_count + total_unkaccts_count + total_usraccts_count
    
    return direct_to_template(request,
                              template="elizabeth/reporting/user_type_summary.html",
                              extra_context={
                                      'total_usraccts_count': total_usraccts_count, 
                                      'total_sysaccts_count': total_sysaccts_count,
                                      'total_appaccts_count': total_appaccts_count,
                                      'total_unkaccts_count': total_unkaccts_count,
                                      'total_accts_count': total_accts_count,
                                      'date_today': todaystr(),                                
                                     },
                    )
    