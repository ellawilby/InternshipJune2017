#!/usr/bin/python

import psycopg2
import sys
import dns.resolver
import socket
import pyasn
from geoip import geolite2
from async_dns import AsyncResolver
import itertools
import collections
import multiprocessing.pool

#### Change as required ####
DBNAME='postgres'
DBUSER='postgres'
DBHOST='localhost'
DBPASS='temp@1'
DBPORT='5432'

def worker(url):
	"""query dns for (hostname, qname) and return (qname, [rdata,...])"""
	try:
		#url, query= arg
		query='A'
		rdatalist = resolver.query(url, query)
		return url, rdatalist
	except dns.resolver.NXDOMAIN as enx:
		sys.stdout.write('x')
		return url, []
	except dns.resolver.Timeout as etime:
		sys.stdout.write('t')
		return url, []
	except Exception, e:
		if len(str(e))>1:
			print e
		sys.stdout.write('-')
		return url, []

def resolve_dns(url_list):
    """Given a list of hosts, return dict that maps qname to
    returned rdata records.
    """
    response_dict = collections.defaultdict(list)
    # create pool for querys but cap max number of threads
    pool = multiprocessing.pool.ThreadPool(processes=min(len(url_list)*3, 60))
    # run for all combinations of hosts and qnames
    for item in pool.imap(worker, url_list, chunksize=1):
	(url, rdatalist)=item
        response_dict[url].extend(rdatalist)
	
    pool.close()
    return response_dict

conn = psycopg2.connect(dbname=DBNAME, user=DBUSER, host=DBHOST, password=DBPASS,port = DBPORT)
cur = conn.cursor()
resolver=dns.resolver.Resolver()
resolver.timeout = 1 # timoutes
resolver.lifetime = 1

#Adding addresses for domains not yet in the a table
cur.execute("select * from ns;")
nsList=cur.fetchall()
nsdList=[]
acount=0
dcount=0


ar = AsyncResolver(["www.google.com", "www.reddit.com", "www.nonexistz.net"])
resolved = ar.resolve()

for host, ip in resolved.items():
  if ip is None:
    print "%s could not be resolved." % host
  else:
    print "%s resolved to %s" % (host, ip)

print "Filling in A records and addresses for domains not in the a table"
for ns in nsList:
	(idnum, zone, ttl, host, nsdname)=ns
	conn.commit()
	cur.execute("select * from public.a where host='{0}';".format(nsdname))
	aList=cur.fetchall()
	if len(aList)==0: #length should be 0 for all domain names not in the .net zone
		#nsList.remove(ns)
		#print "Removed",nsdname
	#else:
		nsdList.append(nsdname)
		#print nsdname

print "=================================="
#ar=AsyncResolver(nsdList)
#resolved=ar.resolve()
result = resolve_dns(nsdList)
for (url, rdatalist) in result.items():
	#print url
	for rdata in rdatalist:
		try:
			conn.commit()
			cur.execute('''insert into a (zone_, ttl, host, address, asn, country) values (%s, DEFAULT, %s, %s::inet, DEFAULT, DEFAULT);''', (zone, nsdname, str(rdata)))
			sys.stdout.write('+')
			acount=acount+1
		except Exception, e:
			sys.stdout.write('-')
	sys.stdout.flush()
	dcount=dcount+1
	nsdname=""

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
