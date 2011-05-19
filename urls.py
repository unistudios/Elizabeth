# from django.conf.urls.defaults import *
# from django.views.generic.simple      import direct_to_template
# import settings

#Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

# urlpatterns = patterns('',
    #main index goes to opsware for now.
    # ('^$', 'opsware.views.index'),
    
    # (r'^opsware/', include('opsware.urls')),

    # (r'^admin/', include(admin.site.urls)),
    
# )

# if settings.DEBUG:
        # urlpatterns += patterns('',
                # (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'media'}),
# )    

from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
#        (r'^$', 'django.views.generic.simple.redirect_to', {'url' : 'http://wiki.nbcuni.ge.com/display/big/Unix-Linux+SOX+Compliancy'} ),
        (r'^$', 'automation.views.home'), 
        (r'^admin/(.*)', admin.site.root) ,
        (r'^likewise/', include('likewise.urls')),
        (r'^wikiexport/', include('wikiexport.urls')),
        (r'^opsware/', include('opsware.urls')),
        (r'^ice/', include('ice.urls')),
        (r'^cacti/', 'cacti.views.cacti'),
)

# help us serve media for CherryPy server
if settings.MEDIA_LOCAL:
       urlpatterns += patterns('',
               (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'media'}),
)

