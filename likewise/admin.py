from website.likewise.models import *
from django.contrib import admin
from django.contrib.contenttypes import generic

class hostsettingInline(admin.TabularInline):
	model = hostsetting

class unixhostInline(admin.TabularInline):
	model = unixhost

class unixhostAdmin(admin.ModelAdmin):

	list_display = ('name', 'fqdn', 'level', hostsetting, 'app', 'os', 'id' )
	fields = ('name', 'fqdn', 'app','level', 'os', 'comment')
	inlines = [ hostsettingInline,]
	search_fields = ['name', 'fqdn']
	list_filter = ('app',)
	
admin.site.register(unixhost, unixhostAdmin)


class unixappAdmin(admin.ModelAdmin):
	#fields = ('name',)
	inlines = [unixhostInline,]
	
admin.site.register(unixapp, unixappAdmin)

class unixuserAdmin(admin.ModelAdmin):
    list_display = ['host', 'user']
    search_fields = ['username', 'host__name']
    exclude = ['datedisabled', 'enabled']
    readonly_fields = ['lastlogin']
	
admin.site.register(unixuser, unixuserAdmin)

class userlistAdmin(admin.ModelAdmin):

    #def queryset(self, request):
    #    qs = super(userlistAdmin, self).queryset(request)
    #    if request.user.is_superuser:
    #        return qs
    #    return qs.filter(username="flavink")
    
    #fieldsets = (
    #    (None, { 'fields': ('username', 'type', 'disable', 'userCount')}),
    #)
    #fields = ('username, 'type', 'disable', 'userCount')
    list_display = ('username','type', 'disable')
    fields = ['username', 'name', 'type', 'source', 'hostCount', 'getHosts']
    search_fields = ['username']
    exclude = ['windowsid', 'disable']
    list_filter = ('type', 'disable')
    readonly_fields = ['username', 'hostCount', 'getHosts']
    ordering=['username']
    
	
admin.site.register(userlist, userlistAdmin)
