#!/usr/bin/python

import psycopg2
import os
import sys

def constructAList(connStr, aFileName):

	aFile=open(aFileName, "w")

	conn=psycopg2.connect(connStr)
	cur=conn.cursor()
	#Get all dns server names for which there is no a record
	conn.commit()
	cur.execute("select nsdname from ns left join a on ns.nsdname=a.host where a.address is NULL group by nsdname;")
	aList=cur.fetchall()

	for a in aList:
		if type(a)==type(('a',1)):
			(host,)=a
		else:
			host=a
		aFile.write(host+'\n')

	aFile.close()
	cur.close()
	conn.close()

	outName_v4='.'.join(aFileName.split('.')[:-1])+"andIPs.txt"
	os.system("./FastA.py {0} {1}".format(aFileName, outName_v4))

def constructAAAAList(connStr, aaaaFileName):

	aaaaFile=open(aaaaFileName, "w")

	conn=psycopg2.connect(connStr)
	cur=conn.cursor()

	#Get all dns server names for which there is no aaaa record
	conn.commit()
	cur.execute("select nsdname from ns left join aaaa on ns.nsdname=aaaa.host where aaaa.address is NULL group by nsdname;")
	aaaaList=cur.fetchall()

	for aaaa in aaaaList:
		if type(aaaa)==type(('a',1)):
			(host,)=aaaa
		else:
			host=aaaa
		aaaaFile.write(host+'\n')

	aaaaFile.close()
	cur.close()
	conn.close()

	outName_v6='.'.join(aaaaFileName.split('.')[:-1])+"andIPs.txt"
	os.system("./Fast6.py {0} {1}".format(aaaaFileName, outName_v6))
