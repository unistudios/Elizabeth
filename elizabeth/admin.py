from website.elizabeth.models import *
from django.contrib import admin
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django import forms

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
	
admin.site.register(unixhost, unixhostAdmin)


class unixappAdmin(admin.ModelAdmin):
    fields = ('name', 'getHostCount', 'getHosts')
    list_display = ['name', 'getHostCount']
    readonly_fields = ['getHostCount', 'getHosts']
    #inlines = [unixhostInline,]
	
admin.site.register(unixapp, unixappAdmin)

class unixuserAdmin(admin.ModelAdmin):
    list_display = ['host', 'user', 'lastlogin']
    search_fields = ['username', 'host__name']
    exclude = ['datedisabled', 'enabled']
    readonly_fields = ['host', 'user', 'username', 'lastlogin', 'getApps']
    list_filter = ['host__apps']
	
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
	
admin.site.register(winhost, winhostAdmin)

class winuserAdmin(admin.ModelAdmin):
    list_display = ['host', 'user', 'lastlogin']
    search_fields = ['username', 'host__name']
    exclude = ['datedisabled', 'enabled']
    readonly_fields = ['host', 'user', 'username', 'lastlogin', 'getApps']
    list_filter = ['host__apps']
	
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

admin.site.register(winuserlist, winuserlistAdmin)
