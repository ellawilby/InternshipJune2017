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

#Finding most common countries
cur.execute("select country, count(country) from public.a_clean group by country order by count(country) desc limit {0}".format(topN))
topCountryList=cur.fetchall()
print "=============================="
print "top "+str(topN)+" most common countries"
for rr in topCountryList:
	print rr

conn.commit()
cur.close()
conn.close()
