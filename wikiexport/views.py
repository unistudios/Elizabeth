from website.wikiexport.models import *

from django.views.generic.simple import *
from django.views.generic.list_detail import *

import datetime

def todaystr():
    return datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p") 

def index(request):
        
    wikiroot="https://wiki.nbcuni.ge.com/plugins/servlet/webdav/Global/"
    
    return object_list(request,
                       queryset=urltowiki.objects.filter(enabled=True),
                       extra_context={'wikiroot': wikiroot,
                                      'dTotay'  : todaystr()
                                      }, 
                    )