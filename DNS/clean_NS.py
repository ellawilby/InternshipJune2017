#!/usr/bin/python

import sys
import os

nsFile=open(sys.argv[1], "r")
dupFile=open(sys.argv[2], "r")
outFile=open(sys.argv[3], "w")
dupIP=str(sys.argv[4])
print dupIP

dupAddresses=[]
for line in nsFile:
	parts=line.split(',')
	dup=False
	for part in parts:
		part=part.rstrip()
		if str(part)==str(dupIP):
			if len(parts)>2:
				print "----------------------------------"
			dup=True
			dupAddresses.append(parts[0])
	if dup==False:
		outFile.write(line)
		sys.stdout.write('+')

for line in dupFile:
	parts=line.split(',')
	if parts[0] in dupAddresses:
		outFile.write(line)
		sys.stdout.write('x')

nsFile.close()
dupFile.close()
outFile.close()
sys.stdout.flush()


