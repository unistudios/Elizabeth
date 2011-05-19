from django.conf.urls.defaults import *

urlpatterns = patterns('',

    # Main index page, that should be it.
    (r'^$', 'website.wikiexport.views.index'),

)
