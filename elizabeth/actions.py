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

########################################
# for Host Accessibility field
########################################

def setAccessible(self, request, queryset):
    for q in queryset:
        q.accessible = True
        q.save()
        print "%s set accessible" % q
setAccessible.short_description = "Set Accessible"

def setInAccessible(self, request, queryset):
    for q in queryset:
        q.accessible = False
        q.save()
        print "%s set inaccessible" % q
setInAccessible.short_description = "Set Inaccessible"