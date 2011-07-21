from website.elizabeth.models import *
from excel_response import ExcelResponse

# Download spreadsheet action for UNIX user to host mappings
def exportExcelUnix(modeladmin, request, queryset):
    #qsHosts = unixuserlist.objects.all()
    entries = list(queryset.values())
    
    for e in entries:
        try:
            e['hostname'] = unixhost.objects.get(pk=int(e['host_id'])).name
        except:
            e['hostname'] = e['host_id']
        del(e['datedisabled'])
        del(e['host_id'])
        del(e['id'])
        del(e['user_id'])
                 
    
    
    #for i in qs:
    #    l.append(i.username)
    
    #u=[{'datedisabled': None,
    #    'enabled': True,
    #    'user_id': 272L,
    #    'username': u'lp'}
    #   ]
    
    #del(u[0]['enabled'])
    
    #data = ['a', 'b', 'c', 'd', 'e', [1, 2, 3]]
    
    #for i in queryset:
    #    delattr(i, "enabled")
    #    u.append(i)
              
    return ExcelResponse(entries)
exportExcelUnix.short_description = "Download UNIX spreadsheet"

# Download spreadsheet action for Windows user to host mappings
def exportExcelWin(modeladmin, request, queryset):
    entries = list(queryset.values())
    
    for e in entries:
        try:
            e['hostname'] = winhost.objects.get(pk=int(e['host_id'])).name
        except:
            e['hostname'] = e['host_id']
        del(e['datedisabled'])
        del(e['host_id'])
        del(e['id'])
        del(e['user_id'])
              
    return ExcelResponse(entries)
exportExcelWin.short_description = "Download Windows spreadsheet"

# Download spreadsheet action for others
def exportExcelAll(modeladmin, request, queryset):
    return ExcelResponse(queryset)
exportExcelAll.short_description = "Download spreadsheet"
