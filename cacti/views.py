from django.http    import HttpResponseRedirect


def cacti(request):
  return HttpResponseRedirect('http://3.156.190.156/cacti/graph_view.php?action=tree&tree_id=1')


