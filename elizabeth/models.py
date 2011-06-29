from django.db import models
from django.db.models import Q
from django.utils.safestring import mark_safe

##################################
# Custom Object Manager for UNIX
# Host Model.  Legacy -- No longer
# necessary?
##################################
class unixhostManager(models.Manager):
    def get_query_set(self):
        return super(unixhostManager, self).get_query_set()
        
    def newhosts(self):
        return super(unixhostManager, self).get_query_set().filter(
                hostsetting__userlist = False,
                hostsetting__sshkeys = True
            )

##################################
# Application Model
##################################
class unixapp(models.Model):
    class Meta:
        ordering = ['name']
        verbose_name = "Business Application"

    IMP_CHOICE= (
        ("L1", "Sox L1"),
        ("L2", "Sox L2"),
        ("BC", "Business Critical"),
        ("OT", "Other"),
    )
    
    name    = models.CharField(max_length=50)
    importance = models.CharField(max_length=2, default="OT", choices=IMP_CHOICE)
    
    # Return a list of hostnames on which app resides
    def getHosts(self):
        lines = self.unixhost_set.all()
        str=""
        for i in lines:
            str=str+i.name+"<BR />"
        return mark_safe(str)
    getHosts.short_description = "Hosts"
    
    # Return a host count for the app
    def getHostCount(self):
        return self.unixhost_set.all().count()
    getHostCount.short_description = "Host Count"
    
    def __unicode__(self):
        return "%s" % self.name

##################################
# UNIX host Model
##################################
class unixhost(models.Model):
    class Meta:
        verbose_name = "Host"

    LEVEL_CHOICE = (
        ("PR", "Production"),
        ("QA", "Quality Assurance"),
        ("DR", "Disaster Recovery"), 
        ("DV", "Development"),
        ("OT", "Other"),
    )

    name    = models.CharField(max_length=50, unique=True)                          # short name
    fqdn    = models.CharField(max_length=50, blank=True)                           # FQDN
    os      = models.CharField(max_length=10, blank=True)                           # What OS is on the box.
    level   = models.CharField(max_length=30, blank=True, choices=LEVEL_CHOICE)     # Prod, QA, DR, DEV
    comment = models.CharField(max_length=100, blank=True)
    
    # Changing app to host relationship from 12M to M2M.
    apps     = models.ManyToManyField(unixapp, blank=True, null=True)
    #app     = models.ForeignKey(unixapp, blank=True, null=True)                     # what app goes with this host.
    
    objects     = unixhostManager()                                                 # Using a custom object manager because we can...
        
    def save(self, force_insert=False, force_update=False):
        self.name = self.name.lower()
        self.fqdn = self.fqdn.lower()
        
        super(unixhost, self).save(force_insert, force_update)
        
        #if self.id == None:
        #   super(unixhost, self).save(force_insert, force_update)
        #
        #   # now, add a hostsetting record.
        #   hs = hostsetting(host=self)
        #   hs.save()
        #else:
        #   super(unixhost, self).save(force_insert, force_update)

    def activeusers(self):
        return self.unixuser_set.filter(user__type="U", enabled=True).count()

    def __unicode__(self):
        return self.name 

######################################################
# Used for Legacy elizabeth system...  Remove possibly?
######################################################
class hostsetting(models.Model):
    # settings for each host.

    # foreign key
    host        = models.OneToOneField(unixhost)
    
    # fields
    sshkeys     = models.BooleanField()     # are the keys ready?
    userlist    = models.BooleanField()     # did we scan users yet?
    installed   = models.BooleanField()     # is elizabeth installed?
    installdate = models.DateField(null=True, blank=True)
    running     = models.BooleanField()     # is elizabeth running?
    delayed     = models.BooleanField()     # is this box delayed for some reason?
    complexity  = models.BooleanField()     # has password complexity been enabled?

    # object manager
    objects = models.Manager()
    
    def __unicode__(self):
        return "I:" + str(self.installed) + " U:" + str(self.userlist) + " K:" + str(self.sshkeys) + " D:" + str(self.delayed)

##################################
# Unique User Accounts Model
##################################
class userlist(models.Model):
    class Meta:
        verbose_name = "User Account"

    USERLIST_CHOICE = (
        ("U", "User"),
        ("A", "Application"),
        ("S", "System Account"),
        ("X", "Unknown"),
    )
    
    username    = models.CharField(max_length=20, blank=True)                           # unix ID
    windowsid   = models.CharField(max_length=20, blank=True, null=True)                            # What is the equivelent ID in NBCUNI
    name        = models.CharField(max_length=50, blank=True, null=True)
    type        = models.CharField(max_length=10, choices=USERLIST_CHOICE, default="X",blank=True, null=True)   # type of account
    enabled     = models.BooleanField()                                                             # Should this account be disabled?
    source      = models.CharField(max_length=100, blank=True, null=True)                           # Where did this ID come from?  
        
    # Return a count of the total number of hosts on which the user exists.
    def hostCount(self):
        return self.unixuser_set.all().count()
    hostCount.short_description = "Number of Hosts"
    
    # Return a list of hostnames on which the user exists, in string form.
    def getHosts(self):
        lines = self.unixuser_set.all()
        str=""
        for i in lines:
            str=str+i.host.name+"<BR />"
        return mark_safe(str)
    getHosts.short_description = "Exists on Hosts"
    
    def __unicode__(self):
        return self.username 

##################################
# User Accounts across Hosts Model
##################################
class unixuser(models.Model):
    class Meta:
        verbose_name = "User to Host Mapping"

    # each user on each unixhost
    host        = models.ForeignKey(unixhost)
    user        = models.ForeignKey(userlist, null=True)
    
    username    = models.CharField(max_length=20)
    lastlogin   = models.DateField(null=True, blank=True, verbose_name="Last Login")
    enabled     = models.BooleanField(blank=True)
    datedisabled = models.DateField(null=True, blank=True)

    # default manager
    objects = models.Manager()
    
    # Get the apps that the host resides on
    def getApps(self):
        applist=""
        for app in self.host.apps.all():
            applist=applist+app.name+"<BR />"
        return mark_safe(applist)
    getApps.short_description = "Apps"

    def __unicode__(self):
        return self.host.name + " " + self.username
    
