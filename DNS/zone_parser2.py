#!/usr/bin/python

import sys
import os
from zone_insert2 import insert

####Change as required####
acceptableRRTypes=['NS','A','AAAA']
zoneFile=open(sys.argv[1], "r")
outputFile=open("netOutput.txt", "w")
logFile=open("netLogFile.txt", "w")

ORIGIN=""
TTL=0
globalTTL=0
inSOA=0 #0=not in SOA, 1=in SOA, 2=read SOA into 1 line
cnt=0
SOAline=""
rrList=[]
OUT_TO_FILE=True

print "Parsing lines from", sys.argv[1]

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
		ORIGIN=parts[1][0:len(parts[1])-1]
		continue
	#Line defining TTL
	if parts[0]=="$TTL":
		globalTTL=int(parts[1][0:len(parts[1])])
		continue
	#SOA
	if rr.find(' SOA ')>-1:#Not 100% sure it will be at index 2
		inSOA=1
	try:
		#Constructing 1 line out of SOA
		if inSOA==1:
			pos=rr.find(';')
			#Writing SOA to 1 line
			if pos>0:#Semi-colon not at start of line
				SOAline=SOAline+rr[:pos]
			else:
				SOAline=SOAline+rr
			#Array of SOA parts
			if rr.find(')')!=-1:
				inSOA=2
		#Read in end of SOA line
		if inSOA==2:
			parts=SOAline.split()
			#Find the TTL. Could be at index 0 or 1 or neither
			pos=-1
			for i in range(2):
				try:
					TTL=int(parts[i])
					pos=i
					break
				except ValueError:
					TTL=globalTTL
			#name=origin
			if (parts[0]=='@' or parts[0]==';@') and pos!=0:
				NAME=ORIGIN
			#name explicitely stated
			elif pos!=0:
				NAME=parts[0]
			#Class will always follow TTL or name
			if pos==1:
				pos=2
			else:
				pos=1
			CLASS=parts[pos]
			#SOA at pos+1
			NAMESERVER=parts[pos+2] 
			ADMIN_EMAIL=parts[pos+3]
			#( at pos+4
			SERIAL=parts[pos+5]
			REFRESH=parts[pos+6]
			RETRY=parts[pos+7]
			EXPIRY=parts[pos+8]
			MIN=parts[pos+9]
			if parts[pos+10]!=')':
				raise Exception('Something hit the fan!')
			#print "NAME: "+NAME+", TTL:"+str(TTL)+", CLASS:"+CLASS+", NAMESERV:"+NAMESERVER+", ADMIN EMAIL:"+ADMIN_EMAIL+", SERIAL:"+SERIAL+", REFRESH:"+REFRESH+", RETRY:"+RETRY+", EXPIRY:"+EXPIRY+", MIN:"+MIN
			rrList.append([NAME, TTL, CLASS, NAMESERVER, ADMIN_EMAIL, SERIAL, int(REFRESH), int(RETRY), int(EXPIRY), int(MIN)])
			inSOA=0 #So this if won't be executed again
			continue
	except Exception:
		print "Something broke... oh dear!"
		continue
	num=len(parts)
	try:
		if ' '.join(parts).find(".GTLD-SERVERS")==-1 and (len(parts)>1 and acceptableRRTypes.index(parts[len(parts)-2])!=-1): #Only includes acceptable types and ignore entries for gtld-servers
			if num==4: #If TTL not specified it is the last defined global TTL
				TTL=int(parts[1])
			else:
				TTL=globalTTL
			RECORD_NAME=parts[0]
			RECORD_TYPE=parts[num-2]
			if parts[num-1][len(parts[num-1])-2]=='.': #Fully qualified domain name
				RECORD_DATA=parts[num-1][0:len(parts[num-1])-1]#Should I remove the trailing dot??
			else:
				RECORD_DATA=parts[num-1][0:len(parts[num-1])-1]+"."+ORIGIN
			if OUT_TO_FILE==True:
				outputFile.write("RN: "+RECORD_NAME+", TTL: "+str(TTL)+", RT: "+RECORD_TYPE+", RD: "+RECORD_DATA+"\n")
			rrList.append([RECORD_NAME, TTL, RECORD_TYPE, RECORD_DATA])

	except ValueError: #Exception will be raised if the record type is not in the acceptableRRTypes list
		if OUT_TO_FILE==True:#Not included entries
			logFile.write(rr)
insert(rrList)#Insert into database




