from django.db import models

# Create your models here.
class urltowiki(models.Model):
    wikipath    = models.CharField(max_length=200, blank=True)
    wikifile    = models.CharField(max_length=50, blank=True)
    url         = models.CharField(max_length=200, blank=True)
    enabled     = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s" % (self.wikifile)