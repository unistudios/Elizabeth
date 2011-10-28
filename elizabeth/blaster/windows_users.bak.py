#!/usr/bin/python
# Name: windows_users.py
# Author: Kyle Flavin
# Descrip: OGFS method for pushing windows users to the database.

# Version 0.9:
# Added support for host retrieval from database, or from opsware group.
# Updated the get_user and added get_host/retrieveURL functions.
# Added -g flag.
# moved some of the server_list parsing code down lower, b/c it made more sense to do the processing with the main portion of the code
#
# Todo: set post_results_to_db to use retrieveURL
# speed up windows scans by minimizing the number of rosh commands used


import subprocess,time,os,sys,re, httplib, urllib, platform
import threading, signal
import datetime
from optparse import OptionParser

#######################################################
# Command line parameters
######################################################

parser = OptionParser()
#booleans
parser.add_option("-d", "--debug",   dest="debug",   action="store_true", help="Debug")
parser.add_option("-q", "--quiet", dest="quiet",   action="store_true", help="Quiet mode")
parser.add_option("-e", "--execute", dest="execute", action="store_true", help="Execute command")
parser.add_option("-r", "--refresh-only", dest="refresh", action="store_true", help="Refresh host list.  If -e is specified, this is performed automatically.")
parser.add_option("-g", "--group", dest="group", action="store_true", help="Use the hardcoded Opsware group, instead of going off the database.")
#stored values
parser.add_option("-a", "--action",  dest="action",  help="Execute command (disable|remove|scan).  Program will do a dry run unless this is explicitly passed.")
parser.add_option("-l", "--user",    dest="user",    help="Username under which commands will be executed.")
parser.add_option("-p", "--post",    dest="post",    help="Database to post back to.")
parser.add_option("-o", "--outputfile", dest="outputfile", help="Send output to file.")
parser.add_option("-s", "--server-db-list", dest="dblist", help="Specify the name of a file to provide db list of servers.")

(options, args) = parser.parse_args()

debug   = options.debug   == True
quiet   = options.quiet == True
execute = options.execute == True
refresh = options.refresh == True
group = options.group == True

if options.action == "disable":
    action = "disable"
elif options.action == "remove":
    action = "remove"
else:
    action = "scan"

if options.outputfile: outputfile = options.outputfile
else: outputfile = ""

if options.user: login = options.user
else: login = "~206102890"

if options.post: post = options.post
else: post = "3.156.190.164"

if options.dblist: dblist = options.dblist
else: dblist = None

if debug: print action, login, "debug:",debug, "execute:",execute, post

######################################################
# Configurable parameters
######################################################

# setup connection to database
conn    = httplib.HTTPConnection(post)
headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain", "Connection": "Keep-Alive"}

exclude_list = "./win_exclude_list"
batch_file = "./blaster_win_tmp.bat"

user_update_url = "/elizabeth/user/win/update/"
host_update_url = "/elizabeth/host/win/update/"
list_disabled_users_url = "/elizabeth/user/disabled/"
list_removed_users_url = "/elizabeth/user/removed/"
active_hosts_url = "/elizabeth/hostlist/appEnabledWin/"

# Select the method for providing the server list (OGFS or list)
server_dir = "/opsw/Server/@Group/Private/~206102890/SOX Userlist - Windows All/@/"
server_list = os.listdir(server_dir)


# timeout
to = 30

#######################################################
# Helper Functions
######################################################

# Note that this class has been written specifically for Python 2.4, NOT 2.6+.  Uses the older isAlive method, and os.kill, rather than process.terminate().
class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None
        self.out = ""
        self.killed = False

    def run(self, timeout):
        def target():
            #print '...Thread started', timeout,
            self.process = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT) #, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            self.out = self.process.communicate()[0]
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

# Writer class for sending output to logfile, in addition to stdout
class MyWriter:
    def __init__(self, stdout, filename):
        self.stdout = stdout
        self.logfile = open(filename, 'a')

    def write(self, text):
        self.stdout.write(text)
        self.logfile.write(text)

    def flush(self):
        self.stdout.flush()

    def close(self):
        self.stdout.close()
        self.stdout.close()

# scan functions... get user details
# takes output from "net user <user>" and finds if the account is active, and the last login time
def get_user_details(user_details):
    enabled = True
    lastlogin = "DNE"

    for line in user_details:
        if line.startswith("Last logon"):
            lastlogin = line.split()[2]
        if line.startswith("Account active"):
            enabled = line.split()[2]
            if enabled.lower() == "no":
                enabled = "false"
            else:
                enabled = "true"

    try:
        lastloginmatch = re.search("\d+/\d+/\d+", lastlogin).group()
    except:
        lastlogin = "DNE"
    else:
        if lastlogin == "Never":
            lastlogin = "DNE"
        elif lastlogin == lastloginmatch:
            lastlogin = lastlogin.split("/")
            lastlogin = str(lastlogin[2])+str(lastlogin[0]).zfill(2)+str(lastlogin[1]).zfill(2) #"YYYYMMDD"
        else:
            lastlogin = "DNE"
    return (enabled, lastlogin)


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


# parse a list of users passed from 'net user' output
def get_user_list(netuser_out):
    # should add some checks in here to make sure the input is valid...
    users = netuser_out[netuser_out.rfind("---\r\n")+5:]
    users = users[:users.rfind("\r\nThe command")]
    users = users.split()
    return users

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

# create batch file with commands to push down to host
# list_of_users: users given by "net user" from server
# build_list: users given from database
def create_batch_file(list_of_users, build_list, action):
    candidate_users = []
    f=open(batch_file, "w")
    f.write("@echo off\n")
    #for u in list_of_users:


    # nice job -- this needs to be fixed... :(  Ugly hack for now.
    new_build_list = []
    build_list = build_list.split()
    for b in build_list:
        if b != "False" and b != "True":
            new_build_list.append(b)

    for b in new_build_list:
        # if it exists on the box, removed it, otherwise just append to the candidate list so the db can be updated.
        if b in list_of_users:
            if action == "disable":
                f.write("net user /active:no "+b+"\n")
            elif action == "remove":
                f.write("net user /delete "+b+"\n")
            candidate_users.append(b)
        else:
            candidate_users.append(b)
    f.close()

    return candidate_users


################################################
# Return a list of users that exists in database, but not on the server
# TO BE INCORPORATED LATER.....
# 
def remove_stale_users(list_of_users, build_list):
    stale_users=[]

    for b in build_list:
        if b not in list_of_users:
            stale_users.append(b)

    return stale_users
################################################

# post back list of disabled users, return a list of users that fail to post back
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

    try:
        conn.request("POST", url, httpparams, headers)
        response = conn.getresponse()
        data = response.read()
        return True
    except:
        # re-open connection and one more try...
        try:
            conn = httplib.HTTPConnection(post)
            conn.request("POST", url, httpparams, headers)
            response = conn.getresponse()
        except:
            print "%s: could not connect to database" % (host_name)
            response = ""
            return False
        return True;

# prepare list of users to exclude if the file exists
def prep_excl_list():
    # Grab users in exclude list (for disabling or removing users
    try:
        f=open(exclude_list, "r")
    except:
        print "No user exclude file found, proceeding without it...\n"
        excl = []
    else:
        print "Parsing exclude file...\n"
        excl = f.read()
        f.close()
        excl = excl.strip().split("\n")
    return excl

#####3
# Our rosh commands
#####

# Grab net user output via rosh
def rosh_it(host_name, file_or_command="", from_file=False):
    if file_or_command:
        if from_file:
            results = Command("/opsw/bin/rosh -n " + host_name + " -l " + login + " -s " + "\"" + file_or_command + "\"")
            results.run(timeout=to)
        else:
            results = Command("/opsw/bin/rosh -n " + host_name + " -l " + login + " " + "\"" + file_or_command + "\"")
            results.run(timeout=to)
    else:
        return ""

    # failed to rosh
    if "Error from remote" in results.out:
        if not quiet: print "Failed!!  Could not Rosh.\n"
        return False
    # host did not exist
    if "Connection error" in results.out:
        if not quiet: print "Failed!!  Host not found.\n"
        return False
    # thread terminatd
    if not results.out:
        if not quiet: print "Failed!!  Thread terminated.\n"
        return False
    # if rosh timed out
    if results.killed:
        if not quiet: print "Failed!! Timed out rosh.\n"
        return False

    return results

# Takes host name and timeout as arguments, returns the Windows OS version
def get_windows_version(host_name, to):
    re_winver = re.compile("Software version.*\r\n")
    output = rosh_it(host_name, "net config server")
    if output:
        output = output.out
    try: 
        r=re_winver.search(output)
        win_ver_str=r.group()[r.group().index("version")+7:].strip()
    except:
        win_ver_str="Windows Unknown"
    return win_ver_str


###
# our actions
###

# scan users of given host and post back to the database
def process_action(host_name, action="scan", execute=False):
    disable = action == "disable"
    scan = action == "scan"
    remove = action == "remove"
    fail = 0

    # get list of users to disable/remove
    if disable or remove:
        userlines  = get_users(host_name, action)
        build_list = gen_build_list(userlines)

    # grab list of users on box
    rosh_out = rosh_it(host_name, "net user")

    # if rosh failed
    if not rosh_out:
        return False
    # looks like we're good to proceed
    else:
        netuser_output = rosh_out.out
        list_of_users = get_user_list(netuser_output)
        if disable or remove: 
            candidate_users = create_batch_file(list_of_users, build_list, action)

        # scan specific actions
        if scan:
            # Get Windows version
            win_ver_str = get_windows_version(host_name, to)

            for u in list_of_users:
                user_details = rosh_it(host_name, "net user "+"\""+u+"\"")
                if user_details:
                    user_details = user_details.out
                    user_details = ''.join(map(str,user_details))
                    user_details = user_details.split("\r\n")
                    (enabled, lastlogin) = get_user_details(user_details)

                    print u,lastlogin, enabled

                    if execute:
                        httpparams = urllib.urlencode({'host_name': host_name, 'user':u.strip(), 'enabled': enabled, 'osinfo': win_ver_str, 'lastlogin': lastlogin})
                        if not post_results_to_db(httpparams):
                            if debug: print "Error with hostname:", host_name, "user:", u
                            fail = 1
                else:
                    fail = 1
            print
        # disable/remove specific actions
        elif disable or remove:
            if execute: 
                for i in candidate_users:

                    batch_output = rosh_it(host_name, batch_file, True)

                    if batch_output:
                        print action, ":", i
                        batch_output = batch_output.out

                        if "user name could not be found" in batch_output:
                            if debug: print "Error locating user(s) on host."
                            return False
                        else:
                            failed_users = post_results(host_name, candidate_users, action)

                        if failed_users:
                            if debug: print "Postback failures:", failed_users
                            return False

                        print "\n"
                    else:
                        fail = 1

            else:
                for i in candidate_users:
                    print "Candidate for", action, ":", i

                print
    if not fail: 
        return True
    else: 
        return False
    

    

#######################################################
# Begin Processing...
######################################################

failed=[]
succeeded=[]

# Prepare hosts: either use an opsware group, or go off the database
if not group:

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
                #print "match %s %s" % (d, s)
                tmp_list = tmp_list + [s]
                flag = 1
        # if we can't match it, add it in anyways and let the script mark it as failed.
        if not flag:
            #print "no match %s" % d
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

# prepare the exclude list if we're disabling or removing users
if action == "disable" or action == "remove": 
    excl = prep_excl_list()

total_servers = len(server_list)

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

status = 0
server_count = 1

# run through hosts in server_list and perform requested action
for host_name in server_list:
    print "Server %s of %s" % (server_count, total_servers)
    server_count += 1
    print "Host: ", host_name
    sys.stdout.flush()


    status = process_action(host_name, action, (False, True)[execute])
            
    # keep track of failed hosts
    if status: 
        succeeded.append(host_name)
    else: 
        failed.append(host_name)


# final status
print "------------------------------------------------"
print "Run Completed  (" + str(total_servers) + " servers), action:", action
print "------------------------------------------------"
print
print "------------------------------------------------"
print "A total of", len(succeeded), "WINDOWS hosts succeeded."
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

conn.close()
