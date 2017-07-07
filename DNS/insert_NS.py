#!/usr/bin/python

import sys
import os
import psycopg2


def insertA(connectionString, inFileName):
	inFile=open(inFileName, "r")
	conn = psycopg2.connect(connectionString)
	cur=conn.cursor()


	#cur.execute("drop table if exists a_clean cascade;")
	#cur.execute("create table a_clean (id bigserial primary key, zone_ varchar(256) not NULL, ttl int default 86400, host varchar(256) not NULL default '@', address inet not NULL, asn int default NULL,  country varchar(5) default NULL);")
	conn.commit()

	for line in inFile:
		parts=line.split(',')
		host=parts[0]
		zone=host.split('.')[-2]+"."
		l=len(parts)
		for i in range(1, l):
			address=parts[i].rstrip()
			try:
				cur.execute("insert into a (zone_, ttl, host, address, asn, country) values ('{0}', DEFAULT, '{1}', '{2}'::inet, DEFAULT, DEFAULT);".format(zone, host, address))
				sys.stdout.write("+")
			except Exception:
				sys.stdout.write("-")

	inFile.close()
	conn.commit()
	cur.close()
	conn.close()
	sys.stdout.flush()

def insertAAAA(connectionString, inFileName):
	inFile=open(inFileName, "r")
	conn = psycopg2.connect(connectionString)
	cur=conn.cursor()


	conn.commit()

	for line in inFile:
		parts=line.split(',')
		host=parts[0]
		zone=host.split('.')[-2]+"."
		l=len(parts)
		for i in range(1, l):
			address=parts[i].rstrip()
			try:
				cur.execute("insert into aaaa (zone_, ttl, host, address) values ('{0}', DEFAULT, '{1}', '{2}'::inet);".format(zone, host, address))
				sys.stdout.write("+")
			except Exception:
				sys.stdout.write("-")

	inFile.close()
	conn.commit()
	cur.close()
	conn.close()
	sys.stdout.flush()
