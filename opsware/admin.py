from opsware.models import Server

from django.contrib import admin

class ServerAdmin(admin.ModelAdmin):
    search_fields = ['name', 'descr']
#    list_display = ('name','tam', 'descr','install_date', 'os', 'env','ournotes','installed','errors','onhold', )
    list_display = ('name','tam', 'descr','install_date', 'os', 'env','ournotes','status', )
    list_filter = ('install_date', 'installed', 'onhold', 'os', 'errors', 'env','tam', )

    actions = ['make_installed']

    def make_installed(self, request, queryset):
        rows_updated = queryset.update(installed=True)
        if rows_updated == 1:
            message_bit = "1 Server was updated"
        else:
            message_bit = "%s Servers were updated" % rows_updated
        self.message_user(request, "%s successfully marked as installed" % message_bit)
    make_installed.short_description = "Mark selected servers as installed"
    
admin.site.register(Server, ServerAdmin)
