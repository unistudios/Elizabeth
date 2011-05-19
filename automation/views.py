from django.views.generic.simple      import direct_to_template

def home(request):
    return direct_to_template(request, template='base.html')
