#!/usr/bin/python

import psycopg2
import sys
import socket
import pyasn
from geoip import geolite2

#Add AS numbers and countries for those not yet specified
def addASNandCountry(asndb, connectionString, letter):#Finding ASN and country
	print "Filling for:",letter
	#User must execute the following before running:
	#>>pip install python-geoip
	#>>pip install python-geoip-geolite2
	#>>cd ~/.local/bin
	#>>./pyasn_util_download.py --latest
	#>>./pyasn_util_convert.py --single <Downloaded RIB File> <appropriate directory>/ip2asn.bz2
	conn=psycopg2.connect(connectionString)
	cur=conn.cursor()
	cur.execute("select * from public.a_clean where host like '{0}%' and (asn is NULL or country is NULL);".format(letter))
	aList=cur.fetchall()
	asnList=[]
	countryList=[]
	asncount=0
	ctycount=0
	print "\nFilling in the ASN and country fields for records in the A table"
	for a in aList:
		(idnum, zone, ttl, host, address, asn, country)=a
		#(address, count)=a
		(asn, ip)=asndb.lookup(address.split('/')[0])
		#print asn
		match=geolite2.lookup(address.split('/')[0])
		asnList.append(asn)
		country=None
		if type(match) is not type(None):
			country=match.country
			if type(country) is not type(None):
				#print str(country)+", "+address
				countryList.append((country, address))
		if asn is None:
			asn='NULL'
			sys.stdout.write('x')
		else:
			sys.stdout.write('a')
			asncount=asncount+1
		if country is None:
			country='NULL'
			sys.stdout.write('X')
		else:
			sys.stdout.write('C')
			ctycount=ctycount+1
		cur.execute("update public.a_clean set asn={0}, country='{1}' where id={2};".format(asn, country, idnum))
		sys.stdout.flush()

	print "\nProcessed", len(aList), "addresses with ",asncount,"having AS numbers and",ctycount,"having associated cities"

	conn.commit()
	cur.close()
	conn.close()
