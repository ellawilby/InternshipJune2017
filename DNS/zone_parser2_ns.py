#!/usr/bin/python

import sys
import os
import math
from zone_insert2 import insert


def parseNS(zoneFileName, globalZONE, globalTTL):
	zoneFile=open(zoneFileName, "r")
	outputFile=open("zoneOutput.txt", "w")
	logFile=open("zoneLogFile.txt", "w")

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
			if (rr.find(".GTLD-SERVERS")==-1 and parts[0]!=globalZONE) and rr.find(' NS ')!=-1: #Only includes acceptable types and ignore entries for gtld-servers
				try: #If TTL not specified it is the last defined global TTL
					TTL=int(parts[1])
					num=2
				except ValueError:
					TTL=globalTTL
					num=1
				RECORD_NAME=parts[0]
				RECORD_TYPE=parts[num]
				if parts[-1][-2]=='.': #Fully qualified domain name
					RECORD_DATA=parts[-1][0:len(parts[-1])-1]#Should I remove the trailing dot??
					ZONE=RECORD_DATA.split('.')[-2]+'.'
				else:
					RECORD_DATA=parts[-1][0:len(parts[-1])-1]+"."+globalZONE
					ZONE=globalZONE
				if OUT_TO_FILE==True:
					outputFile.write("RN: "+RECORD_NAME+", TTL: "+str(TTL)+", RT: "+RECORD_TYPE+", RD: "+RECORD_DATA+"\n")
				#print RECORD_NAME, TTL, RECORD_TYPE, RECORD_DATA
				rrList.append([RECORD_NAME, TTL, RECORD_TYPE, RECORD_DATA, ZONE])
		except ValueError, e: #Exception will be raised if the record type is not in the acceptableRRTypes list
			if OUT_TO_FILE==True:#Not included entries
				logFile.write(rr)
	return rrList

def splitNS(zoneFileName, globalZONE, globalTTL):
	with open(zoneFileName) as f:
		numLines=len(f.readlines())
	#Create temp files with a subset of the records
	files=os.system("bash -c 'split -a 5 -dl 5000 {0} temp'".format(zoneFileName))
	numFiles= int(math.ceil(numLines/5000))
	#print numLines
	nsListList=[] #List of lists of ns records
	for f in range(numFiles):
		name=("temp"+ str(f).zfill(5)) #Name of the temp file
		#print name
		nsList=parseNS(name, globalZONE, globalTTL) #Parse the NS records that are in the temp file
		nsListList.append(nsList)
		os.system("rm {0}".format(name)) #Deletes the temp file
	return nsListList
