#!/usr/bin/python
# Name: windows_sendusers.py
# Descrip: OGFS method for pushing windows users to the database.  The preferred way to do this
#          is through the Opsware softare policies, rather than OGFS>

import subprocess,time,os,sys,re, httplib, urllib, platform
import threading, signal
import datetime
from optparse import OptionParser

#######################################################
# Command line parameters
######################################################

parser = OptionParser()
parser.add_option("-d", "--debug",   dest="debug",   action="store_true", help="Debug")
parser.add_option("-e", "--execute", dest="execute", action="store_true", help="Execute command")
parser.add_option("-a", "--action",  dest="action",  help="Execute command (disable|remove|scan).  Program will do a dry run unless this is explicitly passed.")
parser.add_option("-l", "--user",    dest="user",    help="Username under which commands will be executed.")
parser.add_option("-p", "--post",    dest="post",    help="Database to post back to.")

(options, args) = parser.parse_args()

debug   = options.debug   == True
execute = options.execute == True

if options.action == "disable":
    action = "disable"
elif options.action == "remove":
    action = "remove"
else:
    action = "scan"

if options.user: login = options.user
else: login = "~206102890"

if options.post: post = options.post
else: post = "3.156.190.164"

if debug: print action, login, "debug:",debug, "execute:",execute, post

######################################################
# Configurable parameters
######################################################

# setup connection to database
conn    = httplib.HTTPConnection(post)
headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain", "Connection": "Keep-Alive"}
# Select the method for providing the server list (OGFS or list)
#server_dir = "/opsw/Server/@Group/Private/~206102890/SOX Userlist - Windows DMZ/@/"
#server_dir = "/opsw/Server/@Group/Private/~206102890/Disable Users WINDOWS/Group1/@"
#server_dir = "/opsw/Server/@Group/Private/~206102890/Disable Users WINDOWS/Group2/@"
#server_dir = "/opsw/Server/@Group/Private/~206102890/Disable Users WINDOWS/Group3/@"
server_dir = "/opsw/Server/@Group/Private/~206102890/SOX Userlist - Windows/@/"
server_list = os.listdir(server_dir)

#server_list = ['USALPDBWD002CB.nbcuni.ge.com', 'USALPWSWQV128LA.nbcuni.ge.com', 'USUSH2KWS130.nbcuni.ge.com']
#server_list = ['NLKONPAPW002.nbcuni.ge.com', 'USALPAPWDV015.nbcuni.ge.com',]
#server_list = ['USANYNETDEV2.nbcuni.ge.com']



exclude_list = "./win_exclude_list"
batch_file = "./blaster_win_tmp.bat"

update_url = "/elizabeth/user/win/update/"
list_disabled_users_url = "/elizabeth/user/disabled/"
list_removed_users_url = "/elizabeth/user/removed/"

# thread timeout in seconds
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
            os.kill(self.process.pid, signal.SIGTERM)
            thread.join()
        #print self.process.returncode



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




# parse a list of users passed from 'net user' output
def get_user_list(netuser_out):
    # should add some checks in here to make sure the input is valid...
    users = netuser_out[netuser_out.rfind("---\r\n")+5:]
    users = users[:users.rfind("\r\nThe command")]
    users = users.split()
    return users

# get a list of disabled users from the database
def get_users(host_name, action):
    short_name = host_name.split(".")[0]

    if action == "disable":  the_url = list_disabled_users_url
    elif action == "remove": the_url = list_removed_users_url

    try:
        conn.request("GET", the_url+short_name+"/") #, "", headers)  # pull down just the user accounts to disable
        response = conn.getresponse()
    except:
        # one more try
        try:
            conn = httplib.HTTPConnection(post)
            conn.request("GET", the_url+short_name+"/") #, "", headers)  # pull down just the user accounts to disable
            response = conn.getresponse()
        except:
            print "%s: could not connect to database" % (host_name)
            response = ""

    if response:
        userlines = response.read().strip()
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
def post_results_to_db(httpparams):
    global post, conn

    try:
        conn.request("POST", update_url, httpparams, headers)
        response = conn.getresponse()
        data = response.read()
        return True
    except:
        # one more try
        try:
            conn = httplib.HTTPConnection(post)
            conn.request("POST", update_url, httpparams, headers)
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
            return results.out
        else:
            results = Command("/opsw/bin/rosh -n " + host_name + " -l " + login + " " + "\"" + file_or_command + "\"")
            results.run(timeout=to)
            return results.out
    else:
        return ""

# Takes host name and timeout as arguments, returns the Windows OS version
def get_windows_version(host_name, to):
    re_winver = re.compile("Software version.*\r\n")
    output = rosh_it(host_name, "net config server")
    r=re_winver.search(output)
    try: 
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
    netuser_output = rosh_it(host_name, "net user")

    # failed to rosh
    if "Error from remote" in netuser_output:
        print "Failed!!  Could not Rosh.\n"
        return False
    # host did not exist
    if "Connection error" in netuser_output:
        print "Failed!!  Host not found.\n"
        return False
    # thread terminatd
    elif not netuser_output:
        print "Failed!!  Thread terminated.\n"
        return False
    # looks like we're good to proceed
    else:
        list_of_users = get_user_list(netuser_output)
        if disable or remove: 
            candidate_users = create_batch_file(list_of_users, build_list, action)

        # scan specific actions
        if scan:
            # Get Windows version
            win_ver_str = get_windows_version(host_name, to)

            for u in list_of_users:
                user_details = rosh_it(host_name, "net user "+"\""+u+"\"")
                user_details = ''.join(map(str,user_details))
                user_details = user_details.split("\r\n")
                (enabled, lastlogin) = get_user_details(user_details)

                print u,lastlogin, enabled

                if execute:
                    httpparams = urllib.urlencode({'host_name': host_name, 'user':u.strip(), 'enabled': enabled, 'osinfo': win_ver_str, 'lastlogin': lastlogin})
                    if not post_results_to_db(httpparams):
                        if debug: print "Error with hostname:", host_name, "user:", u
                        fail = 1
            print
        # disable/remove specific actions
        elif disable or remove:
            if execute: 
                for i in candidate_users:
                    print action, ":", i

                batch_output = rosh_it(host_name, batch_file, True)

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

conn.close()

# final status
print "\nA total of", len(succeeded), "hosts succeeded."
#print "Succeeded hosts", succeeded

print "Successful hosts:"
for i in succeeded:
   print i
print


print "A total of", len(failed), "hosts failed."
#print "Failed hosts", failed

print "Failed hosts:"
for i in failed:
   print i
