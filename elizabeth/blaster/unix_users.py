#!/usr/bin/python
# Name: unix_sendusers.py
# Descrip: Uses OGFS to send list of SOX server users and user status to the Elizabeth database.


# Add any users to exclude to the "exclude_list" file.

import sys
import os
import subprocess
import pwd
import httplib, urllib
import time
from optparse import OptionParser

#######################################################
# Configurable parameters
######################################################

parser = OptionParser()
parser.add_option("-d", "--debug",   dest="debug",   action="store_true", help="Debug mode")
parser.add_option("-e", "--execute", dest="execute", action="store_true", help="Execute given command (by default, will dry run)")
parser.add_option("-a", "--action",  dest="action",  help="Execute command (disable, remove, list)")
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
    action = "list"

if options.user: login = options.user
else: login = "root"

if options.post: post = options.post
else: post = "3.156.190.164"

# Set Database to connect to (Elizabeth, or Dev)
#conn = httplib.HTTPConnection("3.156.190.164")
conn = httplib.HTTPConnection(post)
headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain", "Connection": "Keep-Alive"}
#server_dir = "/opsw/Server/@Group/Private/~206102890/Disable Users UNIX/Group1/@" # Hostname must be indicated in this directory.  Exclude trailing slash.
#server_dir = "/opsw/Server/@Group/Private/~206102890/Disable Users UNIX/Group2/@" # Hostname must be indicated in this directory.  Exclude trailing slash.
#server_dir = "/opsw/Server/@Group/Private/~206102890/Disable Users UNIX/Group3/@" # Hostname must be indicated in this directory.  Exclude trailing slash.
server_dir = "/opsw/Server/@Group/Private/~206102890/SOX Userlist - UNIX All/@" # Hostname must be indicated in this directory.  Exclude trailing slash.
#server_dir = "/opsw/Server/@Group/Private/~206102890/test/@" # Hostname must be indicated in this directory.  Exclude trailing slash.
try:
    server_list = os.listdir(server_dir)
except:
    print "Failed to open directory %s" % (server_dir)
    sys.exit()

#"usalpapld292.nbcuni.ge.com",
#"usalpqdba033",
#"usushclsp001dbb.nbcuni.ge.com",
#"ushhp001",
#"usushssap072"


getusers     = "./unix_getusers.py"
exclude_list = "./unix_exclude_list"
tmpfile      = "/tmp/.tmp_user_file"

update_url = "/elizabeth/user/unix/update/"
list_disabled_users_url = "/elizabeth/user/disabled/"
list_removed_users_url = "/elizabeth/user/removed/"


##########################################################
# Helper Functions
##########################################################

# get a list of disabled users from the database
def get_users(host_name, action):
    global conn
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


##########################################################
# Begin Processing...
##########################################################

total_servers = len(server_list)
print "Checking users on " + str(total_servers) + " servers."

# banner
if (execute):
    print "Action:", action, "(active run)", "Servers:", total_servers
else:
    print "Action:", action, "(dry run)", "Servers:", total_servers
print "Database: %s" % post
print


# Grab users in exclude list
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

for host_name in server_list:
    print "Server %s of %s" % (server_count, total_servers) 
    server_count += 1
    print "Host:", host_name
    userlines = get_users(host_name, action)       # get users from database

    if not userlines:
        print "No users retrieved from DB"
        continue

    build_list = gen_build_list(userlines)         # remove any users in exclude file
    if debug: print "build list: ", build_list

    # setup rosh command
    cmd = ["rosh", "-n", host_name, "-l", login]

    # pass in list of users down to the server
    build_list_cmd = cmd + ["echo", "'"+build_list+"'" , ">", tmpfile] # add in command to run on remote host
    output = subprocess.Popen(build_list_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    #if debug: print "Hostname %s, running %s,\n output: %s" % (host_name, " ".join(build_list_cmd), output[1])

    # pass parameters onto script which will perform the requested action on the server
    run_cmd = cmd + ["-s", getusers, "-a", action, ("","-d")[debug], ("","-e")[execute], "-f", tmpfile]
    output = subprocess.Popen(run_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    if debug: print "Hostname %s, running %s,\nOutput:\n%s\nError Output:%s\n" % (host_name, " ".join(run_cmd), output[0], output[1])
    userlines = output[0].strip().split("\n")       # use output returned to update database

    # loop over the users returned and update the database appropriately
    for userline in userlines:
        if userline:
            user,timestamp = userline.split(",")
            if execute:
                print action, ":", user, timestamp
                if action == "disable":
                    httpparams = urllib.urlencode({'host_name': host_name, 'user':user,'enabled':"false", 'datedisabled':timestamp})
                elif action == "remove":
                    httpparams = urllib.urlencode({'host_name': host_name, 'user':user,'enabled':"false", 'dateremoved':timestamp})
                try:
                    conn.request("POST", update_url, httpparams, headers)
                    response = conn.getresponse()
                    data = response.read()
                except:
                    print "Failed to receive data! response = conn.getresponse(), line 125"
                    print data
            else:
                print "Candidate for", action, ":", user, timestamp
    print

    # remove temp file from server
    rm_tmpf_cmd = cmd + ["rm", tmpfile]
    output = subprocess.Popen(rm_tmpf_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    #if debug: print "Hostname %s, running %s,\n output: %s" % (host_name, " ".join(rm_tmpf_cmd), output[1])

sys.exit(0)

