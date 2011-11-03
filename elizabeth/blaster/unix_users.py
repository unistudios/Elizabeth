#!/usr/bin/python
# Name: unix_users.py
# Author: Kyle Flavin
# Descrip: Uses OGFS to send list of SOX server users and user status to the Elizabeth database.  Makes use of the unix_getusers.py script, which should
# reside in the same directory.

# Version 0.9: 
# Added support for host retrieval from database, or from opsware group.
# Updated the get_user and added get_host/retrieveURL functions.
# Added -g flag.
# moved some of the server_list parsing code down lower, b/c it made more sense to do the processing with the main portion of the code
# changed empty disable/remove userlines so it just continues and doesn't break if there are no users.  this is because an empty userlines
# variables may be an indication that the hostname couldn't be found.
#
# Todo: set post_results_to_db to use retrieveURL

import sys
import os
import subprocess
import threading, signal
import pwd
import httplib, urllib
import time
import re
from optparse import OptionParser

# debugging
import code
# code.interact(local=locals())
import pdb
#pdb.set_trace()
import logging

#######################################################
# Configurable parameters
######################################################

# Command Line Options

parser = OptionParser()
#booleans
parser.add_option("-d", "--debug",   dest="debug",   action="store_true", help="Debug mode")
parser.add_option("-q", "--quiet", dest="quiet",   action="store_true", help="Quiet mode")
parser.add_option("-e", "--execute", dest="execute", action="store_true", help="Execute given command (by default, will dry run)")
parser.add_option("-r", "--refresh-only", dest="refresh", action="store_true", help="Refresh host list.  If -e is specified, this is performed automatically.")
parser.add_option("-g", "--group", dest="group", action="store_true", help="Use the hardcoded Opsware group, instead of going off the database.")
parser.add_option("-u", "--update-wiki", dest="update_wiki", action="store_true", help="Update the NBCUNI Wiki (default no)")
# stored values
parser.add_option("-a", "--action",  dest="action",  help="Execute command (disable, remove, list)")
parser.add_option("-l", "--user",    dest="user",    help="Username under which commands will be executed.")
parser.add_option("-p", "--post",    dest="post",    help="Database to post back to.")
parser.add_option("-o", "--outputfile", dest="outputfile", help="Send output to file.")
parser.add_option("-s", "--server-db-list", dest="dblist", help="Specify the name of a file to provide db list of servers.")

(options, args) = parser.parse_args()

# turn on debugging
debug   = options.debug   == True
if debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.CRITICAL)

quiet   = options.quiet == True
execute = options.execute == True
refresh = options.refresh == True
group = options.group == True
update_wiki = options.update_wiki == True

if options.action == "disable":
    action = "disable"
elif options.action == "remove":
    action = "remove"
else:
    action = "scan"

if options.outputfile: outputfile = options.outputfile
else: outputfile = ""

if options.user: login = options.user
else: login = "root"

if options.post: post = options.post
else: post = "3.156.190.164"

if options.dblist: dblist = options.dblist
else: dblist = None

# Set Database to connect to (Elizabeth, or Dev)
conn = httplib.HTTPConnection(post)
headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain", "Connection": "Keep-Alive"}

getusers     = "./unix_getusers.py"
exclude_list = "./unix_exclude_list"
tmpfile      = "/tmp/.tmp_user_file"

user_update_url = "/elizabeth/user/unix/update/"
host_update_url = "/elizabeth/host/unix/update/"
wiki_update_url = "/wikiexport/update/"
list_disabled_users_url = "/elizabeth/user/disabled/"
list_removed_users_url = "/elizabeth/user/removed/"
active_hosts_url = "/elizabeth/hostlist/appEnabledUnix/"

# Hostname must be indicated in this directory.  Exclude trailing slash.
server_dir = "/opsw/Server/@Group/Private/~206102890/SOX Userlist - UNIX All/@" 
try:
    server_list = os.listdir(server_dir)
except:
    print "Failed to open directory %s" % (server_dir)
    sys.exit(1)
#server_list = [
#'usushpcla493dba',
#'usushapspv190.nbcuni.ge.com',
#'usushapspv191',
#'usushapspv192',
#'usushpapa508.nbcuni.ge.com',
#]
    
# timeout
to = 30

##########################################################
# Helper Functions
##########################################################

# Note that this class has been written specifically for Python 2.4, NOT 2.6+.  Uses the older isAlive method, and os.kill, rather than process.terminate().
class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None
        self.tmp = ""
        self.out = ""
        self.err = ""
        self.killed = False

    def run(self, timeout):
        def target():
            #print '...Thread started', timeout,
            #self.process = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT) #, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            self.process = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            self.tmp = self.process.communicate()
            self.out = self.tmp[0]
            self.err = self.tmp[1]
            #self.err = self.process.communicate()[1]
            #self.error = self.process.communicate()[1]
            #print '...Thread finished', timeout

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.isAlive():
            #print '...Terminating process', str(self.process.pid)
            self.killed = True
            os.kill(self.process.pid, signal.SIGTERM)
            thread.join()
        #print self.process.returncode


# rosh the command and then return the output
def rosh_it(host_name, file_or_command="", quiet=False, from_file=False):

    # If there's a command, run it.
    if file_or_command:
        if from_file:
            results = Command("/opsw/bin/rosh -n " + host_name + " -l " + login + " -s " + file_or_command)
            results.run(timeout=to)
        else:
            results = Command("/opsw/bin/rosh -n " + host_name + " -l " + login + " " + "\"" + file_or_command + "\"")
            results.run(timeout=to)
    else:
        return ""


    # failed to rosh
    if "Error from remote" in results.err:
        if not quiet: print "Failed!!  Could not Rosh.\n"
        return False
    # host did not exist
    if "Connection error" in results.err:
        if not quiet: print "Failed!!  Host not found.\n"
        return False
    # if the host timed out
    if results.killed:
        if not quiet: print "Failed!! Timed out rosh.\n"
        return False
    # thread terminatd
    #elif not results.out:
    #    if not quiet: print "Failed!!  Thread terminated.\n"
    #    return False

    return results

# if action is True, GET.  If False, POST.
def retrieveURL(url, action=True, httparams=None, headers={}):
    global conn, post

    if action:
        method = "GET"
    else:
        method = "POST"

    try:
        conn.request(method, url, httparams, headers)
        response = conn.getresponse()
        data = response.read().strip()
    except:
        # one more try
        try: 
            conn = httplib.HTTPConnection(post)
            conn.request(method, url, httparams, headers)
            response = conn.getresponse()
            data = response.read().strip()
        except:
            print "%s to %s: could not connect to database" % (method, url)
            data = ""

    return data

# get a list of hosts from the database
def get_hosts(url):
    servers = retrieveURL(url)
    if servers:
        servers = servers.split("<br />")

        server_list = []
        for s in servers:
            if s: server_list = server_list + [s.strip()]
    else:
        server_list = ""
    return server_list

# get a list of users to disable/remove from the database
def get_users(host_name, action):
    #global conn
    short_name = host_name.split(".")[0]

    if action == "disable":  the_url = list_disabled_users_url
    elif action == "remove": the_url = list_removed_users_url

    userlines = retrieveURL(the_url+short_name+"/")

    #try:
    #    conn.request("GET", the_url+short_name+"/") #, "", headers)  # pull down just the user accounts to disable
    #    response = conn.getresponse()
    #except:
    #    # one more try
    #    try: 
    #        conn = httplib.HTTPConnection(post)
    #        conn.request("GET", the_url+short_name+"/") #, "", headers)  # pull down just the user accounts to disable
    #        response = conn.getresponse()
    #    except:
    #        print "%s: could not connect to database" % (host_name)
    #        response = ""

    logging.debug("URL: http://%s%s%s\n" % (post, the_url, short_name))

    if userlines:
        userlines = userlines.split("\r\n")
    else:
        userlines = ""
    return userlines


    

# Exclude any users in the exclude list
def gen_build_list(userlines):
    build_list = []
    for userline in userlines:
       if userline:
           if userline.split()[0].strip() in excl:
                continue
           else:
                build_list.append(userline)
    build_list = "\n".join(build_list)
    return build_list

# post back list of disabled/removed users, return a list of users that fail to post back
def post_results(host_name, candidate_users, action):
    failed_users = []
    for u in candidate_users:

        thedate = datetime.date.today()

        if action == "disable":
            httpparams = urllib.urlencode({'host_name': host_name, 'user':u,'enabled':"false", 'datedisabled':thedate})
        elif action == "remove":
            httpparams = urllib.urlencode({'host_name': host_name, 'user':u,'enabled':"false", 'dateremoved':thedate})

        if not post_results_to_db(httpparams):
            failed_users.append(u)

    return failed_users

# post values to the database, returning true or false if the post succeeded
def post_results_to_db(httpparams, url=user_update_url):
    global post, conn
    r=re.compile("<title>(.*)</title>")

    try:
        conn.request("POST", url, httpparams, headers)
        response = conn.getresponse()
        data = response.read()
    except:
        # re-open connection and one more try...
        try:
            conn = httplib.HTTPConnection(post)
            conn.request("POST", url, httpparams, headers)
            response = conn.getresponse()
            data = response.read()
        except:
            print "%s: could not connect to database" % (host_name)
            return False
    
    matches = r.search(data)
    # checking for HTML, in which case, there was an error on the database
    if matches:
        try: html = matches.groups()[0]
        except: html = ""
        print "Database postback error: %s\nError: %s\n" % (host_name, html)
        logging.debug(data)
        return False
    else:
        logging.debug(data)
        return True

# Writer class for sending output to logfile, in addition to stdout
class MyWriter:
    def __init__(self, stdout, filename):
        self.stdout = stdout
        self.logfile = open(filename, 'a')

    def write(self, text):
        self.stdout.write(text)
        self.logfile.write(text)

    def close(self):
        self.stdout.close()
        self.stdout.close()

##########################################################
# End of helper functions..........
##########################################################










##########################################################
# Begin Processing...
##########################################################

# Prepare hosts: either use an opsware group, or go off the database
if not group:
    database_list = get_hosts(active_hosts_url)

    # grab our list of users from the database
    if dblist:
        try:
            f = open(dblist, "r")
            database_list = f.read()
            f.close()
            database_list = database_list.split()
        except:
            print "Database file failed to open or is formatted improperly."
            sys.exit(1)
    else:
        database_list = get_hosts(active_hosts_url)

    tmp_list = []

    # we have to do some checking here, because opsware is case-sensitive with host names.
    for d in database_list:
        flag = 0
        for s in server_list:
            if d.lower().split(".")[0] == s.lower().strip().split(".")[0]:
                tmp_list = tmp_list + [s]
                flag = 1
        # if we can't match it, add it in anyways and let the script mark it as failed.
        if not flag:
            tmp_list = tmp_list + [d]

    server_list = tmp_list

# setup stdout if we're writing to file + stdout
if outputfile:
    if not os.path.isfile(outputfile):
        writer = MyWriter(sys.stdout, outputfile)
        save_stdout = sys.stdout
        sys.stdout = writer
    else:
        print "File \"%s\" exists!  Will not ovewrite an existing file, please specify a new location." % outputfile
        sys.exit(1)

total_servers = len(server_list)
print "Checking users on " + str(total_servers) + " servers."

# banner
if (execute):
    print "Action:", action, "(active run)", "Servers:", total_servers
else:
    print "Action:", action, "(dry run)", "Servers:", total_servers
print "Database: %s" % post
if group:
    print "Servers: Using Opsware group for server list"
elif dblist:
    print "Servers: Using LOCAL FILE for server list"
else:
    print "Servers: Using database for server list"

print


# Open exclude file to exclude users
try:
    f=open(exclude_list, "r")
except:
    print "No user exclude file found, proceeding without it..."
else:
    print "Parsing exclude file..."
    excl = f.read()
    f.close()
excl = excl.strip().split("\n")

# Iterate over each host and pull down the userlist / enabled status for each host.
server_count = 1
succeeded = []
failed = []

# go through each server...
for host_name in server_list:
    # host status flag
    fail = 0

    # print out informational message!
    print "Server %s of %s" % (server_count, total_servers) 
    server_count += 1
    print "Host:", host_name

    # disable or removal of users
    if action == "disable" or action == "remove":
        userlines = get_users(host_name, action)       # get users from database if we're disabling/removing
        #if debug: print "userlines from database: ", userlines
        if userlines:
            build_list = gen_build_list(userlines)         # remove any users in exclude file
            #if debug: print "build list (minus excluded users):\n", build_list
        else:
            build_list = ""

        # ROSH 1 OF 3
        # pass in list of users down to the server
        build_list_cmd = "echo '"+build_list+"' > "+tmpfile+"; echo 'bogus output'"  # the extra echo is a hack to keep rosh_it from error on empty output
        output = rosh_it(host_name, build_list_cmd, quiet=True)
        if output:
            #if debug: print "Rosh1\nHostname: %s, running: %s,\noutput:\n%s\nError:\n%s\n" % (host_name, build_list_cmd, output.out, output.err)
            pass
        else: fail = 1

        # ROSH 2 OF 3
        # pass parameters onto script which will perform the requested action on the server
        run_cmd = getusers+" -a "+action+(""," -d")[debug]+(""," -e")[execute]+" -f "+tmpfile 
        output = rosh_it(host_name, run_cmd, quiet, from_file=True)
        if output:
            #if debug: print "Rosh 2\nHostname %s, running %s,\nOutput:\n%s\nError:\n%s\n" % (host_name, run_cmd, output.out, output.err)
            pass
        else: fail = 1

        if not fail:
            # put the userlines into a list
            userlines = output.out.strip().split("\n")

            # loop over the users returned and update the database appropriately
            for userline in userlines:
                if userline:
                    user,timestamp = userline.split(",")
                    if execute:
                        print action, ":", user, timestamp
                        if action == "disable":
                            #httpparams = urllib.urlencode({'host_name': host_name, 'user':user,'enabled':"false", 'datedisabled':timestamp})
                            httpparams = urllib.urlencode({'host_name': host_name, 'user':user, 'datedisabled':timestamp})
                        elif action == "remove":
                            #httpparams = urllib.urlencode({'host_name': host_name, 'user':user,'enabled':"false", 'dateremoved':timestamp})
                            httpparams = urllib.urlencode({'host_name': host_name, 'user':user, 'dateremoved':timestamp})

                        # post back to the database
                        if not post_results_to_db(httpparams):
                            #if debug: print "Error with hostname:", host_name, "user:", user
                            logging.debug("Error with hostname: %s, user: %s" %(host_name, user))
                            fail = 1
                    else:
                        print "Candidate for", action, ":", user, timestamp
            print

            # ROSH 3 OF 3
            # remove the temp file from the server
            rm_tmpf_cmd = "rm " + tmpfile + "; echo 'bogus output'" # the extra echo is a hack to keep rosh_it from error on empty output
            output = rosh_it(host_name, rm_tmpf_cmd, quiet=True)
            if output:
                #if debug: print "Rosh1\nHostname: %s, running: %s,\noutput:\n%s\nError:\n%s\n" % (host_name, build_list_cmd, output.out, output.err)
                pass

    # scanning...
    else:

        # Get host OS
        output = rosh_it(host_name, "uname -s", quiet=True)
        if output:
            host_os = output.out
            #if debug: print "Rosh 1\nHostname %s, running %s,\nOutput:\n%s\nError:\n%s\n" % (host_name, "uname -s", host_os, output.err)
        else: fail = 1

        # Get users from server
        output = rosh_it(host_name, getusers, quiet, True)
        if output:
            #if debug: print "Rosh 2\nHostname %s, running %s,\nOutput:\n%s\nError:\n%s\n" % (host_name, getusers, output.out, output.err)
            pass
        else: fail = 1

        # if we're good so far, prepare to post back to the db
        if not fail:
            userlist = output.out.strip().split("\n")

            # loop through all the users we pulled off the server
            for line in userlist:
                if line:
                    line=line.strip()

                    # if we didn't get the right output, just skip the rest
                    try: 
                        (user,status,lastlogin)=line.split(",")
                    except:
                        print "Error with hostname %s.  Skipping..." % (host_name)
                        break 

                    # set the user status in the http params, in prepartion for postback
                    if "locked" in status:
                        enabled = "false"
                        httpparams = urllib.urlencode({'host_name': host_name, 'user':user,'enabled':enabled, 'lastlogin':lastlogin, 'osinfo': host_os, 'lastscan': "true"})
                    else:
                        enabled = "true"
                        httpparams = urllib.urlencode({'host_name': host_name, 'user':user,'enabled':enabled, 'lastlogin':lastlogin, 'osinfo': host_os, 'lastscan': "true"})

                    # if execute is set, do the postback, otherwise just print out the user
                    if execute:
                        if not post_results_to_db(httpparams):
                            #if debug: print "Error with hostname:", host_name, "user:", user
                            logging.debug("Error with hostname: %s, user: %s\n" % (host_name, user))
                            fail = 1
                        else:
                            print user, enabled
                    else:
                        print user, enabled
        else:
            fail = 1



    # keep track of failed hosts
    if fail == 0:
        succeeded.append(host_name)
    else:
        failed.append(host_name)

    print

conn.close()

# final status
print "------------------------------------------------"
print "Run Completed  (" + str(total_servers) + " servers), action:", action
print "------------------------------------------------"
print
print "------------------------------------------------"
print "A total of", len(succeeded), "UNIX hosts succeeded."
print "------------------------------------------------"

print "Successful hosts:"
for i in succeeded:
   print i
print

print "------------------------------------------------"

# printout failed hosts, and possibly update database
print "A total of", len(failed), "hosts failed."
print "------------------------------------------------"
print "Failed hosts",

if refresh or execute:
    print "(postback):"
else:
    print "(no postback):"

for i in failed:
    if refresh or execute:
        httpparams = urllib.urlencode({'host_name': i, 'accessible': 'false'})
        if not post_results_to_db(httpparams, host_update_url):
            print "Error posting host update:", i, "accessible:", "false"
    print i

if update_wiki:
    print
    if "Pushing changes to wiki..." in retrieveURL(wiki_update_url):
        print "Wiki Updated."
    else:
        print "Wiki failed to update."

sys.exit(0)
