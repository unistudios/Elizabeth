# used primarily for POSTing back data from OGFS -- scripts and data associated with data gathering for Elizabeth

from website.elizabeth.models import *
from elizabeth.forms import *
#from datetime import datetime as dt
from django.http import HttpResponse
from website.settings_local import *

def uploadFile(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return HttpResponse("Valid form")
        return HttpResponse("Form is not valid!")
    return HttpResponse("No POST!  Exiting.")

def handle_uploaded_file(f):
    #datetimenow=str(dt.now())
    #filename = datetimenow.split()[0] +  datetimenow.split()[1].split(".")[0].replace(":", "")

    if str(f).endswith("py"):
        print "blaster/"
        directory = "/elizabeth/blaster/"
    else:
        print "ogfs_output/"
        directory = "/elizabeth/ogfs_output/"
    
    destination = open(ELIZ_PATH + directory + str(f), 'wb')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
