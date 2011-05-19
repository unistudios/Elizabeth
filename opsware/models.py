import string

from django.db import models

# ---------------------------
# Server - Keeps list of all servers to be deployed to.
# ---------------------------

# Custom Managers
class Manager_onhold(models.Manager):
    def get_query_set(self):
        return super(Manager_onhold, self).get_query_set().filter(onhold=True)

class Manager_errors(models.Manager):
    def get_query_set(self):
        return super(Manager_errors, self).get_query_set().filter(errors=True)

class Manager_installed(models.Manager):
    def get_query_set(self):
        return super(Manager_installed, self).get_query_set().filter(installed=True)

class Manager_remaining(models.Manager):
    def get_query_set(self):
        return super(Manager_remaining, self).get_query_set().filter(onhold=False, installed=False, errors=False)

OS_CHOICES = (
        ("Linux", "Linux"),
        ("Windows", "Windows"),
        ("Solaris", "Solaris"), 
        ("AIX", "AIX"),
    )

ENV_CHOICES = (
        ("xxx",   "Unknown"),
        ("dev",   "Development"),
        ("qa",    "Qualtiy Assurance"),
        ("stage", "Staging"),
        ("dr",    "Disaster Recovery"),
        ("prod",  "Production"),
)

STATUS_CHOICES= (
    ("I", "Installed"),
    ("H", "On-Hold"),
    ("E", "Error"),
    ("N", "No Status")
)

class Server(models.Model):
    name     = models.CharField(max_length=50)                  # Server name
    location = models.CharField(max_length=50, blank=True)      # server location
    ipaddr   = models.CharField(max_length=20, blank=True)      # IP Address
    env      = models.CharField(max_length=20, blank=True, choices=ENV_CHOICES, default="xxx")     # environment: dev, prod, qa
    os       = models.CharField(max_length=10, blank=True, choices=OS_CHOICES)      # What Operating System
    osver    = models.CharField(max_length=20, blank=True)      # Version of OS, 2003, rhel3
    descr    = models.CharField(max_length=100, blank=True)     # description of what server does.
    tam      = models.CharField(max_length=40, blank=True)      # Who's the TAM
    
    install_date    = models.DateField(blank=True, null=True)        # What date to install
    installed       = models.BooleanField()                          # has it been installed, updated via join
    errors          = models.BooleanField()                          # did we have any errors on install (manual)
    ournotes        = models.CharField(max_length=250, blank=True)   # internal notes.
    onhold          = models.BooleanField()                          # keep it in the DB but don't install.
    
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, blank=True)
    
    # Managers
    objects = models.Manager()                      # default
    
    objects_onhold    = Manager_onhold()
    objects_installed = Manager_installed()
    objects_remaining = Manager_remaining()
    objects_error     = Manager_errors()

    # Methods
    def __unicode__(self):
        # What should people see us as :)
        return self.name
    
    def save(self, force_insert=False, force_update=False):
        # override the save method to change things around a bit.
        
        # Lower-case 
#        self.os = string.lstrip(string.capwords(self.os))
        
        # update the status field, based on the others, note priority.
        if self.installed == True:
            self.status = "I"
        elif self.onhold == True:
            self.status = "H"
        elif self.errors == True:
            self.status = "E"
        else:
            self.status = "N"

        
        super(Server, self).save(force_insert, force_update)
        
