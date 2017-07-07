#!/usr/bin/env python

import fileinput
import os
import dns.resolver
import spf

def clean(fileName):
	inputFile=open(fileName, "r")
	outputFileName=fileName.split('.')[0]+"_clean.txt"
	output_clean=open(outputFileName, "w")
	logFileName=fileName.split('.')[0]+"_log.txt"
	output_log=open(logFileName,"w")

	#Create one long string for the file
	lines=""
	for line in inputFile:
		if len(line)>1:
			lines=lines+line
	while(lines.find("include:")>=0):
		startpos=lines.find("include:")+8
		#print startpos
		endpos=lines.find(" ", startpos)
		url= lines[startpos:endpos]
		#print "--"+url
		output_log.write("\n---"+url+", num_occurences."+str(lines.count(url)))
		part=""
		try:
		
			answers=dns.resolver.query(url, 'TXT')
			for rdata in answers:
			    	for txt_string in rdata.strings:
					if txt_string[0:5]=="v=spf":
						part=part+txt_string[7:].replace(" ", "|")
						#print part

		except Exception:
			part="No SPF entries"
		output_log.write("|"+part)
		lines=lines.replace("include:"+url, part)
	output_clean.write(lines)
	inputFile.close()
	output_clean.close()
	output_log.close()

#clean("banksListSPF.txt")
