#!/usr/bin/python

import psycopg2
import sys
import dns.resolver
import socket
import os

#### Change as required ####
DBNAME='postgres'
DBUSER='postgres'
DBHOST='localhost'
DBPASS='temp@1'
DBPORT='5432'
topN=10 #How many results to return
netmaskLen=8 #Netmask length (0-32)

conn = psycopg2.connect(dbname=DBNAME, user=DBUSER, host=DBHOST, password=DBPASS,port = DBPORT)
cur = conn.cursor()

#Finding most common NS
cur.execute("select nsdname, count(nsdname) from public.ns group by nsdname order by count(nsdname) desc limit {0};".format(topN))
topNSList=cur.fetchall()
print "=============================="
print "top "+str(topN)+" most common domains"
for rr in topNSList:
	print rr

#Finding most common IP/24 ---Not yet tested
cur.execute("select network(set_masklen(address, {1}))::inet, count(network(set_masklen(address, {1}))) from public.a group by network(set_masklen(address, {1})) order by count(network(set_masklen(address, {1}))) desc limit {0};".format(topN, netmaskLen))
topIPList=cur.fetchall()
print "=============================="
print "top "+str(topN)+" /"+str(netmaskLen)+" IP addresses"
for rr in topIPList:
	print rr

#Finding most common ASN
cur.execute("select asn, count(asn) from public.a group by asn order by count(asn) desc limit {0}".format(topN))
topASNList=cur.fetchall()
print "=============================="
print "top "+str(topN)+" most common asn"
for rr in topASNList:
	print rr

#Finding most common countries
cur.execute("select country, count(country) from public.a group by country order by count(country) desc limit {0}".format(topN))
topCountryList=cur.fetchall()
print "=============================="
print "top "+str(topN)+" most common countries"
for rr in topCountryList:
	print rr

conn.commit()
cur.close()
conn.close()
