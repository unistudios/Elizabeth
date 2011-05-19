from django.views.generic.simple      import direct_to_template

def ice(request):
  return direct_to_template(request, template='ice/ice.html')