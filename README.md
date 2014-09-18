NAME
====
		get_wmi_info.py
		get_wmi_info.exe
Get Windows WMI information from a list of Windows machines

SYNOPSIS
========
python
		python get_wmi_data.py [OPTIONS]

executable
		get_wmi_data.exe [OPTIONS]

DESCRIPTION
===========
When given a list of network reachable computers or addresses, will perform a number of WMIC queries on the machines and save to a csv file
(outputfile). The default WMIC queries are:
-computersystem get name
-computersystem get manufacturer
-computersystem get model
-bios get serialnumber
-os get caption
-os get installdate
-nicconfig get ipaddress
Can identify the remote machines to query in one of two ways:
-Provide a text file (inputfile) containing a list of computers, either hostnames or IP addresses or both.
-Provide a range of IP addresses (startaddress-endaddress), a Netscan will be performed and WMIC queries will be made to all devices that respond. netscan.exe (included in package) must be in the same directory.

ARGUMENTS
=========
		-h
		Display this help document.

		-u username
		User name of Windows account for WMIC queries.

		-p password
		Password of Windows account for WMIC queries.

		-r startaddress-endaddress
		Specifies a range of IP addresses to search. Cannot be used in conjunction with -i.

		-i inputfile
		Specifies the input file to read containing host names or IP addresses. Cannot be used in conjunction with -r.

		-o outputfile
		Specifies the output file to write the WMIC results to in csv format.

		-q wmicarg1-wmiarg2
		Arguments for additional WMIC queries beyond the default. WMIC will be called with the following command: 'arg1 get arg2' eg '-q cpu-maxclockspeed' corresponds to 'cpu get maxclockspeed'.

Example 1
		C:\Users\Administrator> cd Desktop\get_wmi_info\exe
		C:\Users\Administrator\Desktop\get_wmi_info\exe> get_wmi_info.exe -u administrator -p xxxxx -r 192.168.0.1-192.168.0.10
		Performing netscan on IP addresses from 192.168.0.1 to 192.168.0.10
		Netscan complete. Responded IP addresses written to hostslist.txt
		Querying 192.168.0.1
		Querying 192.168.0.2
		Querying 192.168.0.3
		Querying 192.168.0.10
		Completed. View results in results.csv

Example 2
		C:\> python get_wmi_info.py -p user123 -i hostslist.txt -o hostsdata.csv
		Using hostslist.txt for list of machines
		Querying 4GSEBIA
		Querying 4GSDVMA
		Querying 192.168.0.100
		Querying 4GSDVMB
		Completed. View results in hostsdata.csv
