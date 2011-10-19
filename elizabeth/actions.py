from website.elizabeth.models import *

########################################
# Admin actions for enabling/disabling
########################################

def enableApp(self, request, queryset):
    for q in queryset:
        q.enabled = True
        q.save()
        print "Enabled", q
enableApp.short_description = "App Enable"

def disableApp(self, request, queryset):
    for q in queryset:
        q.enabled = False
        q.save()
        print "Disabled", q
disableApp.short_description = "App Disable"