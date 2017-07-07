#!/usr/bin/python

import psycopg2
import sys
import os

#### Change as required ####
DBNAME='postgres'
DBUSER='postgres'
DBHOST='localhost'
DBPASS='temp@1'
DBPORT='5432'

topN=sys.argv[1] #How many results to return

conn = psycopg2.connect(dbname=DBNAME, user=DBUSER, host=DBHOST, password=DBPASS,port = DBPORT)
cur = conn.cursor()

#Finding most common ASN
cur.execute("select asn, count(asn) from public.a_clean group by asn order by count(asn) desc limit {0}".format(topN))
topASNList=cur.fetchall()
print "=============================="
print "top "+str(topN)+" most common asn"
for rr in topASNList:
	print rr

conn.commit()
cur.close()
conn.close()
