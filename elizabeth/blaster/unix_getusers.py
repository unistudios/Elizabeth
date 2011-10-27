#!/usr/bin/env /opt/opsware/smopython2/python
# Name: unix_getusers.py
# Descrip: Disable, remove, or list user accounts on UNIX-based servers. Called from other OGFS scripts.
# Note that the output from this script is used as input to the database.  Therefore, upon failure, nothing
# is returned and the script exits quietly.

import subprocess,time,os,sys,datetime
import logging
from optparse import OptionParser

logging.basicConfig(level=logging.DEBUG)

###################################################################################
# Configure passed parameters 
###################################################################################

# Determines what mode we will operate in (remove, disable, or list)
action  = ""
execute = ""
user_exceptions = ['root', 'sscope2']   # ignore any users in this list for actions involving modification.
user_includes   = []                    # if any users are included here, they will be the ONLY users processed.  

# Parse command line parameters
parser = OptionParser()
parser.add_option("-a", "--action", dest="action",   help="User action to perform [get|disable|remove]", default="get")
parser.add_option("-f", "--file",   dest="filename", help="File storing userlist.  Each line contains the username and user state (TRUE|FALSE).")
parser.add_option("-d", "--debug",  dest="debug",    action="store_true", default=False, help="Turn off debug mode.  Prints debug messages.")
parser.add_option("-e", "--execute",dest="execute",  action="store_true", default=False, help="Execute command (for disable and remove commands).")

try:
    (options, args) = parser.parse_args()
except:
    if debug: logging.debug("Failed to parse arguments in %s", __file__)
    raise

debug   = options.debug   == True
execute = options.execute == True

if options.action:
    action = options.action

if options.filename:
    tmpfile = options.filename
else:
    tmpfile = None

#if options.debug:
    #logging.debug("action: %s, filename: %s, debug: %s, execute: %s" % (action, tmpfile, debug, execute))

###################################################################################
# Helper Functions
###################################################################################

# Get the date the home directory was last modified
def lastLoginTime(homedir):
    if os.path.isdir(homedir):
        thetime = list(time.localtime(os.path.getmtime(homedir)))
        thetime[1]=str(thetime[1]).zfill(2)
        thetime[2]=str(thetime[2]).zfill(2)
        #return [thetime[0], thetime[1], thetime[2]]
        return ''.join(map(str,thetime[:3]))
    else:
        return "DNE"


# disable_user
# status: account status, True or False
# chk_usr_str: OS dependent "locked" string to look for in usr_str
# usr_str: if chk_usr_str is in usr_str, account is disabled
# user: username
# cmd: the OS-dependent command to execute
#
# Description: If "execute" mode is active, status is false,  and
#              user is not already disabled or in exceptions list, 
#              then disable the user.
def disable_usr(status, chk_usr_str, usr_str, user, cmd):
    #usr_str.find(chk_usr_str) == -1 and \
    #chk_usr_str not in usr_str and \
    if status == "False" and \
    user.lower() not in user_exceptions:
        if debug: logging.debug("Candidate for disabling: %s" % (user))
        print user+","+str(datetime.date.today())
        if execute:
            logging.debug("Disabling: %s" % (user))
            # backup the shadow file if it exists...
            # run the disable command
            output = subprocess.Popen(cmd+[user],stdout=subprocess.PIPE).communicate()[0]
    else:
        logging.debug("Not a candidate: %s, chk_usr_str: %s usr_str: %s" % (user, chk_usr_str, usr_str))

# remove_user
# status: account status, True or False
# chk_usr_str: OS dependent "locked" string to look for in usr_str
# usr_str: if chk_usr_str is in usr_str, account is disabled
# user: username
# cmd: the OS-dependent command to execute
#
# Description: If "execute" mode is active, remove user if already
#              disabled, and not in the exceptions list.
def remove_usr(status, chk_usr_str, usr_str, user, cmd):
    if chk_usr_str.lower() in usr_str.lower() and \
    user.lower() not in user_exceptions:
        if debug: logging.debug("Candidate for removing: %s" % (user))
        print user+","+str(datetime.date.today())
        if execute:
            #logging.debug("Removing: %s" % (user))
            # run the remove command
            output = subprocess.Popen(cmd+[user],stdout=subprocess.PIPE).communicate()[0]
    else:
        logging.debug("Not a candidate: %s, chk_usr_str: %s usr_str: %s" % (user, chk_usr_str, usr_str))

# get_user_status
# user: username
# chk_usr_str: OS-dependent string to check if user is locked
# cmd: command to execute on server
#
# Description: Return the username, status, and lastlogin time for the user
def get_user_status(user, chk_usr_str, cmd):
    output = subprocess.Popen(cmd+[user],stdout=subprocess.PIPE).communicate()[0]

    if chk_usr_str.lower() in output.lower():
        print user+",locked,"+lastlogin
    else:
        print user+",enabled,"+lastlogin

###################################################################################
# Determine host type and configure command parameters 
###################################################################################

# Determine what type of host we're on
host_os=subprocess.Popen(['uname','-s'],stdout=subprocess.PIPE).communicate()[0]
host_os=host_os.strip()

# Figure out what type of host we are, and then determine OS-level commands based on action to perform.
if host_os == "Linux":
    command_chkusr_cmd = ['/usr/bin/passwd', '-S']                  # check status of user
    command_chkusr_str = "locked"                                   # string to check for user status
    command_disableusr = ['/usr/bin/passwd', '-l']                  # command to lock account
    command_removeusr  = ['userdel']
    # Backup shadow file before beginning
    command_backupshdw = ['/bin/cp', '/etc/shadow', '/etc/shadow.ul_bak']
    command_backuppasswd = ['/bin/cp', '/etc/passwd', '/etc/passwd.ul_bak']
    command_backupgrp = ['/bin/cp', '/etc/group', '/etc/group.ul_bak']

elif host_os == "Solaris" or host_os == "SunOS":
    command_chkusr_cmd = ['/usr/bin/passwd', '-s']
    command_chkusr_str = "LK"
    command_disableusr = ['/usr/bin/passwd', '-l']
    command_removeusr  = ['userdel']
    command_backupshdw = ['/bin/cp', '/etc/shadow', '/etc/shadow.ul_bak']
    command_backuppasswd = ['/bin/cp', '/etc/passwd', '/etc/passwd.ul_bak']
    command_backupgrp = ['/bin/cp', '/etc/group', '/etc/group.ul_bak']

elif host_os == "AIX":
    command_chkusr_cmd = ['lsuser', '-c', '-a','account_locked'] # this fails with a full path (/usr/sbin/luser) for some reason...
    command_chkusr_str = "true"
    command_disableusr = ['/usr/bin/chuser', 'account_locked=true']
    command_removeusr  = ['userdel']
    # Backup shadow file before beginning
    command_backupshdw = ['/usr/bin/cp', '/etc/security/user', '/etc/security/user.ul_bak']
    command_backuppasswd = ['/bin/cp', '/etc/passwd', '/etc/passwd.ul_bak']
    command_backupgrp = ['/bin/cp', '/etc/group', '/etc/group.ul_bak']

elif host_os == "HP-UX":
    #command_chkusr_cmd = ['/usr/lbin/getprpw', '-r', '-m', 'lockout']
    #command_chkusr_cmd = ['/usr/bin/passwd', '-s']
    #command_chkusr_str = "LK"
    command_chkusr_cmd = ['/usr/lbin/getprpw', '-r', '-m', 'lockout']
    command_chkusr_str = "0000010"
    command_disableusr = ['/usr/bin/passwd', '-l']
    command_removeusr  = ['userdel']
    command_backupshdw = []
    command_backuppasswd = ['/bin/cp', '/etc/passwd', '/etc/passwd.ul_bak']
    command_backupgrp = ['/bin/cp', '/etc/group', '/etc/group.ul_bak']

else:
    if debug: logging.debug("Host %s not recognized!  Exiting." % (host_os))
    sys.exit(1) # exit immediately if the host is not recognized


###################################################################################
# Run command against host
###################################################################################

# Depending on the OS type, use the appropriate command to get the account and the account status.
# Print results (return to calling process) to insert back into database.
passwdfile = open("/etc/passwd","r")

if action=="remove" or action=="disable":
    # grab users passed in from calling script
    f = open(tmpfile, "r")
    passed_users=f.read().strip().split("\n")
    f.close()

    # and backup our important files...
    if execute:
        if command_backupshdw: output = subprocess.Popen(command_backupshdw,stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        if command_backuppasswd: output = subprocess.Popen(command_backuppasswd,stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        if command_backupgrp: output = subprocess.Popen(command_backupgrp,stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

for line in passwdfile:
    # grab users from host's passwd file
    user = line[0:line.find(":")].strip()
    homedir = line.split(":")[5]
    lastlogin = lastLoginTime(homedir)

    # proceed based on given action.  for default action, just list out the users and their status.
    if action=="remove" or action=="disable":

        for passed_user in passed_users:
            if passed_user:                   # just in case some empty list values make their way in....
                puser   = passed_user.split()[0].strip()
                pstatus = passed_user.split()[1].strip()

                # If we have a match, check the status of the user on the box
                if puser.lower() == user.lower() and ( not user_includes or user.lower() in user_includes ): # or user.lower in user_includes):
                    locked = subprocess.Popen(command_chkusr_cmd+[user],stdout=subprocess.PIPE).communicate()[0]

                    # *** DISABLE OR REMOVE THE USER *****
                    if action=="disable":
                        disable_usr(pstatus, command_chkusr_str, locked, user, command_disableusr)
                    elif action=="remove":
                        remove_usr(pstatus, command_chkusr_str, locked, user, command_removeusr)
    #elif unlock:
    #    print "Unlock Linux User"
    else:
        get_user_status(user, command_chkusr_str, command_chkusr_cmd)
