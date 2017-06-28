#!/usr/bin/python

#from zone_parser2 import read_file
import psycopg2
import sys
import dns.resolver
import socket
import pyasn
from geoip import geolite2


DBNAME='postgres'
DBUSER='postgres'
DBHOST='localhost'
DBPASS='temp@1'
DBPORT='5432'

conn = psycopg2.connect(dbname=DBNAME, user=DBUSER, host=DBHOST, password=DBPASS,port = DBPORT)
cur = conn.cursor()
resolver=dns.resolver.Resolver()
resolver.timeout = 1 # timoutes
resolver.lifetime = 1

#Adding addresses for domains not yet in the a table
cur.execute("select * from public.ns;")
nsList=cur.fetchall()
acount=0
dcount=0
print "Filling in A records and addresses for domains not in the a table"
for ns in nsList:
	break
	(idnum, zone, ttl, host, nsdname)=ns
	cur.execute("select * from public.a where host='{0}';".format(nsdname))
	aList=cur.fetchall()
	if len(aList)==0: #length should be 0 for all domain names not in the .net zone
		try:
			ips=resolver.query(nsdname, 'A')
			for ip in ips:
				#print ip
				cur.execute('''insert into public.a (zone_, ttl, host, address) values (%s, DEFAULT, %s, %s);''', (zone, nsdname, str(ip)))
			sys.stdout.write('+')
			acount=acount+1
			#ip =socket.gethostbyname(nsdname)
			#print ip
			#cur.execute("update public.ns set address=%s where id=%s;", (ip, idnum))
			
		except dns.resolver.NXDOMAIN as enx:
		   	# print "Error: NXDOMAIN - domain does not exist"
		   	# writeLog("Error: NXDOMAIN - domain does not exist")
			sys.stdout.write('x')
		except dns.resolver.Timeout as etime:
		    	# print "Error: dns.exception.Timeout"
		    	# writeLog("Error: dns.exception.Timeout")
			sys.stdout.write('t');
		except Exception, e:
			# print url+" has no A record"
			sys.stdout.write('-')
		sys.stdout.flush()
		dcount=dcount+1
	
print "Processed", dcount, "domains with ",acount,"having A records"


#Finding ASN and country
#User execute the following:
#>>pip install python-geoip
#>>pip install python-geoip-geolite2
#>>cd ~/.local/bin
#>>./pyasn_util_download.py --latest
#>>./pyasn_util_convert.py --single <Downloaded RIB File> <appropriate directory>/ip2asn.bz2
asndb=pyasn.pyasn('ip2asn.bz2')
cur.execute("select * from public.a where asn is NULL or country is NULL")
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
	cur.execute("update public.a set asn={0}, country='{1}' where id={2};".format(asn, country, idnum))
	sys.stdout.flush()

print "\nProcessed", len(aList), "addresses with ",asncount,"having AS numbers and",ctycount,"having associated cities"

conn.commit()
cur.close()
conn.close()
