#!/usr/bin/python
# Name: unix_sendusers.py
# Descrip: Uses OGFS to send list of SOX server users and user status to the Elizabeth database.

import sys
import os
import subprocess
import pwd
import httplib, urllib
import re

#######################################################
# USAGE INSTRUCTIONS: 
# 1. Set host database to POST results to.
# 2. Set list of servers to scan
#######################################################


#######################################################
# Configurable parameters
######################################################

DEBUG=0

# Set Database to connect to (Elizabeth, or Dev)
#conn = httplib.HTTPConnection("3.156.190.164")
conn = httplib.HTTPConnection("likewise.nbcuni.ge.com")

# OS specific commands to retrieve users
getusers = "./unix_getusers.py"

# Set the list of servers to be used.  Servers can either be grabbed from their group in OGFS, or specified directly as a list.

#server_dir = "/opsw/Server/@Group/Private/~206102890/SOX Userlist - UNIX Subset/@" # Hostname must be indicated in this directory.  Exclude trailing slash.
server_dir = "/opsw/Server/@Group/Private/~206102890/SOX Userlist - UNIX All/@" # Hostname must be indicated in this directory.  Exclude trailing slash.
server_list = os.listdir(server_dir)

#server_list = [
#'usalpapld292.nbcuni.ge.com',
#'usalpqdba033',
#'usushclsp001dbb.nbcuni.ge.com',
#'ushhp001',
#'usushssap072',
#]

#server_list = ['usalpqdba033', 'usalpdbsr019cb.nbcuni.ge.com', 'usalpaplqv101.nbcuni.ge.com']
server_list = ['usushpapa528']

login_user='root'


##########################################################
# Begin Processing...
##########################################################

headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
print "Attemping to add " + str(len(server_list)) + " items.\n"

# Loop through the hostnames, and look at their /etc/passwd file for users.  Submit those users to Elizabeth.  OS specific commands
# are run by the getusers file.  
total_servers = len(server_list)
print "Checking users on " + str(total_servers) + " servers."

server_count = 1

for host_name in server_list:

    print "Server %s of %s" % (server_count, total_servers)
    server_count += 1
    print host_name,

    # use rosh to get OS type
    try:
        host_os=subprocess.Popen(['/opsw/bin/rosh','-n',host_name,'-l',login_user,'uname','-s'],stdout=subprocess.PIPE).communicate()[0]
        host_os=host_os.strip()
        print host_os
    except:
        print host_os, "Rosh failed.  Check hostname."


    try:
        output=subprocess.Popen(['rosh', '-n', host_name, '-l',login_user,'-s',getusers],stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    except NameError:
        print "Rosh failure.  Check hostname."
        userlist = []


    if DEBUG:
        print output[1]

    userlist = output[0].strip().split("\n")


    r=re.compile("<title>(.*)</title>")
    for line in userlist:
        if line:
            line=line.strip()
            (user,status,lastlogin)=line.split(",")
            if "locked" in status:
                httpparams = urllib.urlencode({'host_name': host_name, 'user':user,'enabled':"false", 'lastlogin':lastlogin, 'osinfo': host_os, 'lastscan': "true"})
            else:
                httpparams = urllib.urlencode({'host_name': host_name, 'user':user,'enabled':"true", 'lastlogin':lastlogin, 'osinfo': host_os, 'lastscan': "true"})
            #Post our result to the db via http
            conn.request("POST","/elizabeth/user/unix/update/", httpparams, headers)
            response = conn.getresponse()
            data = response.read()

            # catch post errors due to usernames which differ only in case...
            matches = r.search(data)
            if matches:
                print host_name, line, matches.groups()[0]
            else:
                print data,
    print
    conn.close()
sys.exit(0)
