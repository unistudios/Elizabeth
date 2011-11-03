from django.conf.urls.defaults import *

urlpatterns = patterns('',

    # Main index page, that should be it.
    (r'^$', 'website.wikiexport.views.index'),
    (r'^update/', 'website.wikiexport.views.update'),

)
