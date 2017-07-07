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
netmaskLen=sys.argv[2] #Netmask length (0-32)

conn = psycopg2.connect(dbname=DBNAME, user=DBUSER, host=DBHOST, password=DBPASS,port = DBPORT)
cur = conn.cursor()

#Finding most common IP/24 ---Not yet tested
cur.execute("select network(set_masklen(address, {1}))::inet, count(network(set_masklen(address, {1}))) from public.a_clean group by network(set_masklen(address, {1})) order by count(network(set_masklen(address, {1}))) desc limit {0};".format(topN, netmaskLen))
topIPList=cur.fetchall()
print "=============================="
print "top "+str(topN)+" /"+str(netmaskLen)+" IP addresses"
for rr in topIPList:
	print rr

conn.commit()
cur.close()
conn.close()
