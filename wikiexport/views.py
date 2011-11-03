from website.wikiexport.models import *

from django.views.generic.simple import *
from django.views.generic.list_detail import *
from django.http import HttpResponse
import subprocess
import commands

import datetime

def todaystr():
    return datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p") 

def index(request):
    
    # Changed?    
    #wikiroot="https://wiki.nbcuni.ge.com/plugins/servlet/webdav/Global/"
    wikiroot="https://wiki.nbcuni.ge.com/plugins/servlet/confluence/default/Global/"
    
    return object_list(request,
                       queryset=urltowiki.objects.filter(enabled=True),
                       extra_context={'wikiroot': wikiroot,
                                      'dTotay'  : todaystr()
                                      }, 
                    )

def update(request):
    # not great, but it'll do.
    
    ip = commands.getoutput("/sbin/ifconfig").split("\n")[1].split()[1][5:]
    
    if ip == '3.156.190.164':
        push_path = '/opt/website/elizabeth/blaster/push_wiki.sh'
    else:
        push_path ='/opt/unixmb/website/elizabeth/blaster/push_wiki.sh' 
    
    print subprocess.Popen(['/bin/bash', '-c', push_path])
    return HttpResponse("Pushing changes to wiki...")