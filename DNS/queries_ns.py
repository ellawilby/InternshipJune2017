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

#Finding most common NS

cur.execute("select nsdname, count(nsdname) from public.ns group by nsdname order by count(nsdname) desc limit {0};".format(topN))
topNSList=cur.fetchall()
print "=============================="
print "top "+str(topN)+" most common domains"
for rr in topNSList:
	print rr

conn.commit()
cur.close()
conn.close()
