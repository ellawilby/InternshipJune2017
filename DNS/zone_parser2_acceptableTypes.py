#!/usr/bin/python

import sys
import os
#from zone_insert2 import insert

def parseAcceptable(zoneFileName, acceptableRRTypes, globalZONE, globalTTL):

	zoneFile=open(zoneFileName, "r")
	outputFile=open("netOutput.txt", "w")
	logFile=open("netLogFile.txt", "w")

	ORIGIN=""
	TTL=0
	inSOA=0 #0=not in SOA, 1=in SOA, 2=read SOA into 1 line
	cnt=0
	SOAline=""
	rrList=[]
	OUT_TO_FILE=True #Change to False to stop text file output

	for rr in zoneFile:
		#Splitting and cleaning line	
		parts=filter(None, rr.split(' '))
		
		#Stuff to ignore
		if len(rr)==0 or parts[0]=="$ORIGIN" or parts[0]=="$TTL" or rr[0]==';' or rr.find(' SOA ')>-1:
			continue
		#Otherwise
		try:
			validType=False
			for RRtype in acceptableRRTypes:
				if rr.find(' '+RRtype+' ')!=-1:
					validType=True
					break
			if (rr.find(".GTLD-SERVERS")==-1 and parts[0]!=globalZONE) and validType: #Only includes acceptable types and ignore entries for gtld-servers
				try: #If TTL not specified it is the last defined global TTL
					TTL=int(parts[1])
					num=2
				except ValueError:
					TTL=globalTTL
					num=1
				RECORD_TYPE=parts[num]
				if (RECORD_TYPE in ["HINFO", "CNAME"]):
					RECORD_NAME=parts[0][0:len(parts[0])-1]
					ZONE=globalZONE
				elif parts[0][-2]=='.': #Fully qualified domain
					RECORD_NAME=parts[0][0:len(parts[0])-1]#Should I remove the trailing dot??
					ZONE=RECORD_NAME.split('.')[-2]
				else: #add zone to end of domain
					RECORD_NAME=parts[0][0:len(parts[0])-1]+"."+globalZONE
					ZONE=globalZONE
				RECORD_DATA=""
				for i in range(num+1,len(parts)):
					RECORD_DATA=RECORD_DATA+' '+parts[i]
				RECORD_DATA=RECORD_DATA[1:len(RECORD_DATA)-1]
				if OUT_TO_FILE==True:
					outputFile.write("RN: "+RECORD_NAME+", TTL: "+str(TTL)+", RT: "+RECORD_TYPE+", RD: "+RECORD_DATA+"\n")
				#print RECORD_NAME, TTL, RECORD_TYPE, RECORD_DATA
				rrList.append([RECORD_NAME, TTL, RECORD_TYPE, RECORD_DATA, ZONE])

		except ValueError: #Exception will be raised if the record type is not in the acceptableRRTypes list
			if OUT_TO_FILE==True:#Not included entries
				logFile.write(rr)
	return rrList
