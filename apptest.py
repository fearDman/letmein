#!/usr/bin/env python

#################
# Imports
#################
import time
import subprocess
import cgi
import cgitb
import smtplib
import os
import re
from os import getenv
from subprocess import Popen, PIPE
from email.mime.text import MIMEText

cgitb.enable()
##################
# DEFINE VARIABLES
##################

remote_server = "voip.syssrc.com"
remote_user = "root"
remote_key = "/opt/.ssh/letmein_key"
remote_script = "/var/www/cgi-bin/writesaveiptables.sh"
connectionstring = remote_user+"@"+remote_server
timeStr = time.strftime("%c") # obtains current time #checks local time (will be useful for logging)

##################
# GET WEB FORM DATA
##################
form = cgi.FieldStorage()
user_name = str(form.getlist("name")).strip("[']")

##################
# ACTUAL METHOD TO GET IP ADDRESS
##################

ip2 = (getenv("HTTP_CLIENT_IP") or
getenv("HTTP_X_FORWARDED_FOR") or
getenv("HTTP_X_FORWARDED_FOR") or
getenv("REMOTE_ADDR") or
"UNKOWN")

##################
# CHECK IF IP EXISTS IN GIVEN LIST OF IPS
##################
def checkiplist(iplist,ip):
        output = [x.translate(None,"'").strip() for x in iplist]
        if ip in output:
                return True
        else:
                return False
##################
# GATHER A LIST OF IPS TO BE CHECKED
##################
def getiplist(key,con,ip):
        ipt2 = "/etc/sysconfig/iptables"
        ipt = Popen(["ssh","-o","StrictHostKeyChecking=no","-i",key, con,"sudo","iptables-save"], stdout=PIPE, stderr=subprocess.STDOUT)
        output = ipt.communicate()
        for eachline in output:
#               ip_regex = re.findall(r'(?:\d{1,3}\.){3}\d{1,3}/\d{1,2}', output)
                ip_regex = re.findall(r'(?:\d{1,3}\.){3}\d{1,3}', eachline)
                iplist = str(ip_regex)
                iplistfiltered = iplist.strip("[]")
                ipsintables = iplistfiltered.split(',')
                return ipsintables


##################
# ADD IP TO IPTABLES ON REMOTE MACHINE
##################
def addiptotables(key,con,ip,ipcomm):
	ipcomment = "\""+ipcomm+"\""
	ipt = Popen(["ssh","-o","StrictHostKeyChecking=no","-i",key,con,"sudo", "iptables","-I","INPUT","7","-s",ip,"-j","LETMEIN","-m","comment","--comment", ipcomment], stdout=PIPE, stderr=subprocess.STDOUT)
	output=ipt.communicate()

##################
# WRITE HTML PAGES
##################

print("Content-Type: text/html\n\n")  # html markup follows


htmlHeader = """
<html>
 <head>
  <Title>Letmein page for {remote_server}</Title>
 </head> """

htmlForm = """
<body>
  <p>The current Eastern date and time is:  {timeStr}</p>
  <p>And your IP address is: {ip2}</p>
  <form action="/cgi-bin/apptest.py" method="POST">
	Name:<input type="text" name="name">
	<input type="submit" value="Submit">
  </form>
  <p>Output: </br>
</body>
</html> """

htmlResults = """
<body>
 <p>{user_name}, your IP address: {ip2} has been added to the firewall</p>
</body>
</html> """

htmlError = """
<body>
 <p>Your IP address: {ip2} already exists in the firewall</p>
 <p>If you are experiencing issues with your phone, please contact the Help Desk at 410-891-1711</p>
</body>
</html> """



###############################
# BEGIN MAIN PROCESS
###############################


if checkiplist(getiplist(remote_key,connectionstring,ip2), ip2):
	print(htmlHeader.format(**locals()))
	print(htmlError.format(**locals()))
elif not checkiplist(getiplist(remote_key,connectionstring,ip2), ip2):
	if "name" not in form:
		 print(htmlHeader.format(**locals()))
		 print(htmlForm.format(**locals()))
	elif "name" in form:
		addiptotables(remote_key, connectionstring, ip2, user_name)
		print(htmlHeader.format(**locals()))
		print(htmlResults.format(**locals()))

#if "name" not in form:
#	print(htmlHeader.format(**locals()))
#	print(htmlForm.format(**locals()))
#elif "name" in form:
#	ipcomment = user_name
#	addiptotables(remote_key, connectionstring, remote_script, ip2, ipcomment)
#	print(htmlHeader.format(**locals()))
#	print(htmlResults.format(**locals()))
