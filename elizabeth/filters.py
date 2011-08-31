from django.contrib.admin.filterspecs import *
from django.db import models

FilterSpec.register(lambda f: isinstance(f, models.BooleanField) or isinstance(f, models.NullBooleanField), BooleanFieldFilterSpec)


class NullFilterSpec(FilterSpec):
    def __init__(self, f, request, params, model, model_admin):
        super(NullFilterSpec, self).__init__(f, request, params, model, model_admin)
        self.lookup_kwarg = '%s__isnull' % f.name
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)

    def choices(self, cl):
        yield {'selected': self.lookup_val is None,
               'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
               'display': _('All')}
        for k, v in ((True,_('Null')),('',_('With value'))):
            yield {'selected': k == self.lookup_val,
                    'query_string': cl.get_query_string({self.lookup_kwarg: k}),
                    'display': v}

#FilterSpec.filter_specs.insert(0, (lambda f: f.null, NullFilterSpec))
