from website.elizabeth.models import *
from django.contrib import admin
from django.contrib.contenttypes import generic

class hostsettingInline(admin.TabularInline):
	model = hostsetting

#class unixhostInline(admin.TabularInline):
    #model = unixhost

class unixhostAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'os', 'id' )
    fields = ('name', 'fqdn', 'apps','level', 'os', 'comment')
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

class userlistAdmin(admin.ModelAdmin):
    # Override ModelAdmin queryset to only return distinct user accounts.
    # This is necessary when filtering by application.
    def queryset(self, request):
        qs = super(userlistAdmin, self).queryset(request)
        return qs.distinct()
    
    #fieldsets = (
    #    (None, { 'fields': ('username', 'type', 'disable', 'userCount')}),
    #)
    #fields = ('username, 'type', 'disable', 'userCount')
    
    list_display = ('username','type', 'disable')
    fields = ['username', 'name', 'type', 'source', 'hostCount', 'getHosts']
    search_fields = ['username']
    exclude = ['windowsid', 'disable']
    list_filter = ('type', 'disable', 'unixuser__host__apps')
    readonly_fields = ['username', 'hostCount', 'getHosts']
    ordering=['username']
    
	
admin.site.register(userlist, userlistAdmin)
