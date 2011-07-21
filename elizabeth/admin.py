from website.elizabeth.models import *
from website.elizabeth.excel import *
from django.contrib import admin
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django import forms
#from excel_response import ExcelResponse

superuser = ""


class hostsettingInline(admin.TabularInline):
	model = hostsetting

#class unixhostInline(admin.TabularInline):
    #model = unixhost

class unixhostAdmin(admin.ModelAdmin):
    list_display = ('name', 'os', )
    fields = ('name', 'fqdn', 'apps', 'level', 'os', 'comment')
    #inlines = [ hostsettingInline,]
    search_fields = ['name', 'fqdn']
    readonly_fields = ['name', 'fqdn', 'level', 'os', 'comment']
    list_filter = ('apps',)
    filter_horizontal = ['apps']
    actions= [exportExcel]
	
admin.site.register(unixhost, unixhostAdmin)


class hostappAdmin(admin.ModelAdmin):
    fields = ('name', 'getHostCount', 'getWinHosts', 'getUnixHosts')
    list_display = ['name', 'getHostCount']
    readonly_fields = ['getHostCount', 'getHosts', 'getWinHosts', 'getUnixHosts']
    #inlines = [unixhostInline,]
    actions= [exportExcel]
	
admin.site.register(hostapp, hostappAdmin)

class unixuserAdmin(admin.ModelAdmin):
    list_display = ['host', 'user', 'lastlogin', 'enabled', 'lastscan']
    search_fields = ['username', 'host__name']
    exclude = ['datedisabled','username']
    readonly_fields = ['host', 'user', 'enabled', 'lastlogin', 'lastscan', 'getApps']
    list_filter = ['host__apps']
    actions= [exportExcelHmUnix]
	
admin.site.register(unixuser, unixuserAdmin)


#class CustomUserListAdmin(forms.ModelForm):
#    def __init__(self, request=None, *args, **kwargs):
#        self.request = request
#        super(CustomUserListAdmin, self).__init__(*args, **kwargs)
        
        

class unixuserlistAdmin(admin.ModelAdmin):
    #form = CustomUserListAdmin
    #def get_form(self, request, obj=None, **kwargs):
    #    ModelForm = super(userlistAdmin, self).get_form(request, obj, **kwargs)
    #    def form_wrapper(*args, **kwargs):
    #        a = ModelForm(request=request, *args, **kwargs)
    #        return a
    #    return form_wrapper

    # Override ModelAdmin queryset to only return distinct user accounts.
    # This is necessary when filtering by application.
    def queryset(self, request):
        qs = super(unixuserlistAdmin, self).queryset(request)
        return qs.distinct()
    
    #fieldsets = (
    #    (None, { 'fields': ('username', 'type', 'disable', 'userCount')}),
    #)
    #fields = ('username, 'type', 'disable', 'userCount')
    
    list_display = ('username','type', 'enabled')
    fields = ['username', 'name', 'type', 'source', 'hostCount', 'getHosts']
    search_fields = ['username']
    exclude = ['enabled']
    list_filter = ('type', 'enabled', 'unixuser__host__apps', 'unixuser__host__os')
    readonly_fields = ['username', 'hostCount', 'getHosts']
    ordering=['username']
    actions = [exportExcel]
    #print "Yes or no: " + request.user.is_superuser() 
	
admin.site.register(unixuserlist, unixuserlistAdmin)


class winhostAdmin(admin.ModelAdmin):
    list_display = ('name', 'os',)
    fields = ('name', 'fqdn', 'apps', 'level', 'os', 'comment')
    #inlines = [ hostsettingInline,]
    search_fields = ['name', 'fqdn']
    readonly_fields = ['name', 'fqdn', 'level', 'os', 'comment']
    list_filter = ('apps',)
    filter_horizontal = ['apps']
    actions= [exportExcel]
	
admin.site.register(winhost, winhostAdmin)

class winuserAdmin(admin.ModelAdmin):
    list_display = ['host', 'user', 'lastlogin', 'enabled', 'lastscan']
    search_fields = ['username', 'host__name']
    exclude = ['datedisabled','username']
    readonly_fields = ['host', 'user', 'enabled', 'lastlogin', 'lastscan', 'getApps']
    list_filter = ['host__apps']
    actions=[exportExcelHmWin]
	
admin.site.register(winuser, winuserAdmin)

class winuserlistAdmin(admin.ModelAdmin):
    def queryset(self, request):
        qs = super(winuserlistAdmin, self).queryset(request)
        return qs.distinct()
    
    list_display = ('username','type', 'enabled')
    fields = ['username', 'name', 'type', 'source', 'hostCount', 'getHosts']
    search_fields = ['username']
    exclude = ['windowsid', 'enabled']
    list_filter = ('type', 'enabled', 'winuser__host__apps', 'winuser__host__os')
    readonly_fields = ['username', 'hostCount', 'getHosts']
    ordering=['username']
    actions= [exportExcel]

admin.site.register(winuserlist, winuserlistAdmin)
