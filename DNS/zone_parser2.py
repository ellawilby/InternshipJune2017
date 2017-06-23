#!/usr/bin/python

import sys

zoneFile=open(sys.argv[1], "r")
ORIGIN=""
TTL=0
globalTTL=0
inSOA=0
cnt=0

for rr in zoneFile:
	#Splitting and cleaning line	
	parts=filter(None, rr.split(' '))
	cnt=cnt+1
	#Ignore empty lines
	if len(rr)==0:
		continue
	#Header lines
	if rr[0]==';':
		continue #Ignore for now
	#Line defining origin
	if parts[0]=="$ORIGIN":
		ORIGIN=parts[1][0:len(parts[1])]
	#Line defining TTL
	if parts[0]=="$TTL":
		globalTTL=int(parts[1][0:len(parts[1])])
	#SOA
	if rr.find(' SOA ')>-1:#Not 100% sure it will be at index 2
		continue #Ignoring for now
		inSOA=1
		if parts[0]!='@':
			ORIGIN=parts[0]
		NAMESPACE=parts[1]

	num=len(parts)
	if parts[num-2]=="NS" or (parts[num-2]=="A" and parts[0][1:]!=".GTLD-SERVERS"):
		if num==4: #If TTL not specified it is the last defined global TTL
			TTL=parts[1]
		else:
			TTL=globalTTL
		RECORD_NAME=parts[0]
		RECORD_TYPE="NS"
		if parts[num-1][len(parts[num-1])-2]=='.': #Fully qualified domain name
			RECORD_DATA=parts[num-1][0:len(parts[num-1])-1]#Should I remove the trailing dot??
		else:
			RECORD_DATA=parts[num-1][0:len(parts[num-1])-1]+"."+ORIGIN
			#print RECORD_DATA
		#INSERT INTO TABLE HERE
#		print "RN: "+RECORD_NAME+", TTL: "+str(TTL)+", RT: "+RECORD_TYPE+", RD: "+
	
		#Reset TTL to last global
		
