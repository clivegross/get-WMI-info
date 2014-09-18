##########################################################################
# NAME
# get_wmi_info.py- Get Windows WMI information from a list of Windows machines
#
# SYNOPSIS
# python get_wmi_data.py [OPTION]
#
# DESCRIPTION
# When given a list of network reachable computers or addresses, will perform a number of WMIC queries on the machines and save to a csv file (outputfile).
# The default wmic queries are:
# 	-computersystem get name
# 	-computersystem get manufacturer
# 	-computersystem get model
# 	-bios get serialnumber
# 	-os get caption
# 	-os get installdate
# 	-nicconfig get ipaddress
# Can identify the remote machines to WMIC query in one of two ways:
# 	-Provide a text file (inputfile) containing a list of computers, either hostnames or IP addresses or both
#		-Provide a range of IP addresses (startaddress-endaddress), a Netscan will be performed and WMIC queries will be made to all devices that respond
#
# ARGUMENTS
# -h
# 		Display this help document.
#
# -u username
# 		User name of Windows account for WMIC queries.
#
# -p password
#			Password of Windows account for WMIC queries.
# 
# -r startaddress-endaddress
#			Specifies a range of IP addresses to search. Cannot be used in conjunction with -i.
#
# -i inputfile
#			Specifies the input file to read containing host names or IP addresses. Cannot be used in conjunction with -r.
#
# -o outputfile
#			Specifies the output file to write the WMIC results to in csv format.
#
# -q wmicarg1-wmiarg2
#			Arguments for additional queries beyond the default, WMIC will be called with the following command:
#			'wmicarg1 get wmicarg2', eg -q=cpu-maxclockspeed would query WMIC with 'cpu get maxclockspeed'.
##########################################################################
import csv
import subprocess
from optparse import OptionParser
from sys import exit

##########################################################################
# define functions
##########################################################################
# convert a command line argument string, with 2 variables, eg arg1-arg2 into a list eg [arg1, arg2]
def doublearg2list(doublearg):
	arglist = doublearg.split('-')
	return arglist

#	execute a Windows command, 'command'
def run_cmd(command):
	p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
	stdout, stderr = p.communicate()
	if p.returncode!=0:
		print 'DOS command failed'

# take the netscan output and tidy into a file containing IP addresses only		
def clean_netscan(readfile='netscan.csv',writefile='hostlist.txt'):
	with open(readfile, 'rb') as infile:
		reader = csv.reader(infile)
		with open(writefile, 'wb') as outfile:
			writer = csv.writer(outfile)
			is_header=True
			for row in reader:
				if not is_header:
					writer.writerow([row[0]])
				is_header=False

##########################################################################
# sort command line arguments into variables, perform netscan (if required) and prepare for WMIC queries
##########################################################################
parser = OptionParser()
parser.add_option("-u", "--username", dest="user", help="Windows user name to run command under. Default administrator.", default='administrator')
parser.add_option("-p", "--password", dest="password", help="Windows user password to run command under.", default='administrator')
parser.add_option("-r", "--range", dest="iprange", help="[-r startaddress-endaddress] Specifies a range of IP addresses to search. Cannot be used in conjunction with -i.")
parser.add_option("-i", "--input", dest="infile", help="Specifies the input file to read containing host names or IP addresses. Cannot be used in conjunction with -r.")
parser.add_option("-o", "--output", dest="outfile", help="Specifies the output file to write the WMIC results to in csv format. Default results.csv.", default='results.csv')
parser.add_option("-q", "--query", dest="wmicquery", help="[-q arg1-arg2] Arguments for additional queries beyond the default, WMIC will be called with the following command:'wmicarg1 get wmicarg2', eg -q=cpu-maxclockspeed would query WMIC with 'cpu get maxclockspeed'.")
(options, args) = parser.parse_args()

if options.iprange is None:
	# make sure infile provided as argument
	if options.infile is None:
		print 'Neither an IP range or an input file have been provided you fool!'
		print 'Program terminating!'
		exit()
	else:
		hostsfile = options.infile
		print 'Using '+hostsfile+' for list of machines'
else:
	if options.infile is None:
		iprange = doublearg2list(options.iprange)
		print 'Performing netscan on IP addresses from '+str(iprange[0])+' to '+str(iprange[1])
		netscancommand = 'start /wait netscan.exe /hide /range:%s-%s /auto:netscan.csv' % (iprange[0], iprange[1])
		run_cmd(netscancommand)
		# cleanup netscan results
		readfile='netscan.csv'
		hostsfile='hostslist.txt'
		clean_netscan(readfile, hostsfile)
		print 'Netscan complete. Responded IP addresses written to '+hostsfile
	else:
		print 'Only an IP range OR an input file can be provided, not both you fool!'
		print 'Program terminating!'
		exit()
		
# read in machines from file as list 'hosts'		
with open(hostsfile) as h:
  hosts = h.readlines()
hosts = [host.rstrip() for host in hosts]
	
# make list if WMIC queries
wmicswitch = list()
wmicswitch.append(['computersystem', 'name'])
wmicswitch.append(['computersystem', 'manufacturer'])
wmicswitch.append(['computersystem', 'model'])
wmicswitch.append(['bios', 'serialnumber'])
wmicswitch.append(['os', 'caption'])
wmicswitch.append(['os', 'installdate'])
wmicswitch.append(['nicconfig', 'ipaddress'])
# header for output file
header = ['Hostname', 'Manufacturer', 'Model', 'Service tag', 'Operating system', 'Install date', 'IP address']
# if additional query provided as command line argument, add to list
if options.wmicquery is not None:
	query = doublearg2list(options.wmicquery)
	wmicswitch.append(query)
	header.append(query[1])

##########################################################################
# run WMIC queries and export results to csv
##########################################################################	
# initialize empty list for all hosts data to be appended
computerdata = list()

# loop through hosts and get wmic info
for i, host in enumerate(hosts):
	print 'Querying '+host
	# initialize empty list for a single hosts data
	compspec = list()
	# loop through wmic commands
	for switch in wmicswitch:
		wmicfile='wmicresponse.txt'
		# execute wmic command saving output to wmicfile
		wmiccommand='wmic' + ' /user:%s' % options.user + ' /password:%s' % options.password + ' /node:%s' % host + ' %s get %s' % (switch[0], switch[1]) + ' | more > %s' % wmicfile
		run_cmd(wmiccommand)
		with open(wmicfile, 'r') as infile:
			# strip down string to the required value
			q = infile.read()
			if switch[1]=='ipaddress':
				q = [i for i in q.split('"') if ' ' not in i]
			elif switch[1]=='installdate':
				q = q.split('\n')[1].rstrip()
				q = q[6:8]+'-'+q[4:6]+'-'+q[:4]+' '+q[8:10]+':'+q[10:12]+':'+q[12:14]
			else:
				q = q.split('\n')[1].rstrip()
		# append wmic value to inner list
		compspec.append(q)
	# append hosts wmic data to outer list
	computerdata.append(compspec)

# write wmic data to csv
header = ['Hostname', 'Manufacturer', 'Model', 'Service tag', 'Operating system', 'Install date', 'IP address']
with open(options.outfile, 'wb') as outfile:
	writer = csv.writer(outfile)
	writer.writerow(header)
	for row in computerdata:
		writer.writerow(row)
	
print 'Completed. View results in '+options.outfile
