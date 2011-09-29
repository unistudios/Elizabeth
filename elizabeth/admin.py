from website.elizabeth.models import *
from website.elizabeth.excel import *
#from website.elizabeth.filters import *
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

##############################################################################################
# UNIX hosts
##############################################################################################
class unixhostAdmin(admin.ModelAdmin):
    list_display = ('name', 'os', )
    fields = ('name', 'os', 'apps', 'comment')
    #inlines = [ hostsettingInline,]
    search_fields = ['name', 'fqdn']
    readonly_fields = ['name', 'os', 'comment']
    list_filter = ('apps',)
    filter_horizontal = ['apps']
    actions= [exportExcelAll]
    
    # Remove the deleted action for non-super users
    def get_actions(self, request):   
        actions = super(unixhostAdmin, self).get_actions(request)
        
        if not request.user.is_superuser:        
            try:
                del actions['delete_selected']
            except KeyError:
                pass
            return actions
        else:
            return actions
        
    
admin.site.register(unixhost, unixhostAdmin)

##############################################################################################
# Application Admin
# Shows host to application mappings
##############################################################################################
class hostappAdmin(admin.ModelAdmin):
    fields = ('name', 'importance', 'getHostCount', 'getWinHosts', 'getUnixHosts')
    list_display = ['name', 'getHostCount', 'importance']
    #readonly_fields = ['name', 'importance', 'getHostCount', 'getHosts', 'getWinHosts', 'getUnixHosts']
    readonly_fields = ['getHostCount', 'getHosts', 'getWinHosts', 'getUnixHosts']
    #inlines = [unixhostInline,]
    actions= [exportExcelAppsToUsers]
    
    # Remove the deleted action for non-super users
    def get_actions(self, request):   
        actions = super(hostappAdmin, self).get_actions(request)
        
        if not request.user.is_superuser:        
            try:
                del actions['delete_selected']
            except KeyError:
                pass
            return actions
        else:
            return actions
        
    # Show readonly fields for non-super users
    def get_readonly_fields(self, request, obj = None):
        adminROFields = ['getHostCount', 'getHosts', 'getWinHosts', 'getUnixHosts']
        userROFields = ['name', 'importance', 'getHostCount', 'getHosts', 'getWinHosts', 'getUnixHosts']
        
        if request.user.is_superuser:
            #return ['featured',] + self.readonly_fields
            return adminROFields
        return userROFields
        
admin.site.register(hostapp, hostappAdmin)


##############################################################################################
# UNIX user list Admin - 
# Display host to user mappings and their last scan state
##############################################################################################
class unixuserAdmin(admin.ModelAdmin):
    list_display = ['host', 'user', 'lastlogin', 'lastscan', 'enabled', 'datedisabled', 'dateremoved']
    search_fields = ['username', 'host__name']
    exclude = ['username']
    readonly_fields = ['adminUserLinked', 'adminHostLinked', 'getApps']
    list_filter = ['enabled', 'user__type', 'lastlogin', 'lastscan', 'host__apps']  
    actions= [exportExcelUnix]
    
    fieldsets = (
                ("Settings", {
                        'fields': ('adminUserLinked', 'adminHostLinked', 'getApps', 'lastlogin', 'enabled', ),                    
                }),
                ("Scans", {            
                        'fields': ('lastscan', 'datedisabled', 'dateremoved'),
                }),
    )
    
    # Remove the deleted action for non-super users
    def get_actions(self, request):   
        actions = super(unixuserAdmin, self).get_actions(request)
        
        if not request.user.is_superuser:        
            try:
                del actions['delete_selected']
            except KeyError:
                pass
            return actions
        else:
            return actions
    
    # Show readonly fields for non-super users
    def get_readonly_fields(self, request, obj = None):
        adminROFields = ['adminUserLinked', 'adminHostLinked', 'host', 'user', 'getApps', 'lastlogin', 'lastscan',]
        userROFields = ['adminUserLinked', 'adminHostLinked', 'host', 'user', 'getApps', 'lastlogin', 'lastscan', 'enabled', 'datedisabled', 'dateremoved']
                      
        if obj:
            if not request.user.is_superuser:
                #return ['featured',] + self.readonly_fields
                return userROFields
            return adminROFields
        else:
            return userROFields
           
admin.site.register(unixuser, unixuserAdmin)

#class CustomUserListAdmin(forms.ModelForm):
#    def __init__(self, request=None, *args, **kwargs):
#        self.request = request
#        super(CustomUserListAdmin, self).__init__(*args, **kwargs)
        
        
##############################################################################################
# UNIX user list Admin - 
# Authoritative for what can and cannot exist in the environment
##############################################################################################
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
    
    list_display = ('username','name','type', 'enabled')
    fields = ['username', 'name', 'type', 'source', 'hostCount', 'getHosts', 'enabled']
    search_fields = ['username']
    exclude = []
    list_filter = ('type', 'enabled', 'unixuser__host__apps', 'unixuser__host__os')
    readonly_fields = ['username', 'hostCount', 'getHosts']
    ordering=['username']
    actions = [exportExcelAll]
    #print "Yes or no: " + request.user.is_superuser()
    
    # Remove the deleted action for non-super users
    def get_actions(self, request):   
        actions = super(unixuserlistAdmin, self).get_actions(request)
        
        if not request.user.is_superuser:        
            try:
                del actions['delete_selected']
            except KeyError:
                pass
            return actions
        else:
            return actions
        
    # Show readonly fields for non-super users
    def get_readonly_fields(self, request, obj = None):
        adminROFields = ['username', 'hostCount', 'getHosts',]
        userROFields = ['username', 'hostCount', 'getHosts',]
                      
        if obj:
            if not request.user.is_superuser:
                #return ['featured',] + self.readonly_fields
                return userROFields
            return adminROFields
        else:
            return userROFields
    
admin.site.register(unixuserlist, unixuserlistAdmin)


##############################################################################################
# Windows hosts
##############################################################################################
class winhostAdmin(admin.ModelAdmin):
    list_display = ('name', 'os',)
    fields = ('name', 'os', 'apps', 'comment')
    #inlines = [ hostsettingInline,]
    search_fields = ['name', 'fqdn']
    readonly_fields = ['name', 'os', 'comment']
    list_filter = ('apps',)
    filter_horizontal = ['apps']
    actions= [exportExcelAll]
    
    # Remove the deleted action for non-super users
    def get_actions(self, request):   
        actions = super(winhostAdmin, self).get_actions(request)
        
        if not request.user.is_superuser:        
            try:
                del actions['delete_selected']
            except KeyError:
                pass
            return actions
        else:
            return actions
    
admin.site.register(winhost, winhostAdmin)



##############################################################################################
# Windows user list Admin - 
# Display host to user mappings and their last scan state
##############################################################################################
class winuserAdmin(admin.ModelAdmin):
    list_display = ['host', 'user', 'lastlogin', 'lastscan', 'enabled', 'datedisabled', 'dateremoved']
    search_fields = ['username', 'host__name']
    exclude = ['username',]
    list_filter = ['enabled', 'user__type', 'lastlogin', 'lastscan', 'host__apps']
    actions = [exportExcelWin]
    readonly_fields = ['adminUserLinked', 'adminHostLinked', 'getApps']
    fieldsets = (
                ("Settings", {
                        'fields': ('adminUserLinked', 'adminHostLinked', 'getApps', 'lastlogin', 'enabled', ),                    
                }),
                ("Scans", {            
                        'fields': ('lastscan', 'datedisabled', 'dateremoved'),
                }),
    )
    
    # Remove the deleted action for non-super users
    def get_actions(self, request):   
        actions = super(winuserAdmin, self).get_actions(request)
        
        if not request.user.is_superuser:        
            try:
                del actions['delete_selected']
            except KeyError:
                pass
            return actions
        else:
            return actions
           
    # Show readonly fields for non-super users
    def get_readonly_fields(self, request, obj = None):
        adminROFields = ['adminUserLinked', 'adminHostLinked', 'host', 'user', 'getApps', 'lastlogin', 'lastscan']
        userROFields = ['adminUserLinked', 'adminHostLinked', 'host', 'user', 'getApps', 'lastlogin', 'lastscan', 'enabled', 'datedisabled', 'dateremoved']
                      
        if obj:
            if not request.user.is_superuser:
                #return ['featured',] + self.readonly_fields
                return userROFields
            return adminROFields
        else:
            return userROFields
    
admin.site.register(winuser, winuserAdmin)


##############################################################################################
# Windows user list Admin - 
# Authoritative for what can and cannot exist in the environment
##############################################################################################
class winuserlistAdmin(admin.ModelAdmin):
    def queryset(self, request):
        qs = super(winuserlistAdmin, self).queryset(request)
        return qs.distinct()
    
    list_display = ('username', 'name', 'type', 'enabled')
    fields = ['username', 'name', 'type', 'source', 'hostCount', 'getHosts', 'enabled']
    search_fields = ['username']
    exclude = ['windowsid']
    list_filter = ('type', 'enabled', 'winuser__host__apps', 'winuser__host__os')
    readonly_fields = ['username', 'hostCount', 'getHosts']
    ordering=['username']
    actions= [exportExcelAll]
    
    # Remove the deleted action for non-super users
    def get_actions(self, request):   
        actions = super(winuserlistAdmin, self).get_actions(request)
        
        if not request.user.is_superuser:        
            try:
                del actions['delete_selected']
            except KeyError:
                pass
            return actions
        else:
            return actions
        
    # Show readonly fields for non-super users
    def get_readonly_fields(self, request, obj = None):
        adminROFields = ['username', 'hostCount', 'getHosts']
        userROFields = ['username', 'hostCount', 'getHosts']
                      
        if obj:
            if not request.user.is_superuser:
                #return ['featured',] + self.readonly_fields
                return userROFields
            return adminROFields
        else:
            return userROFields

admin.site.register(winuserlist, winuserlistAdmin)
