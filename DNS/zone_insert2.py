#!/usr/bin/python

#from zone_parser2 import read_file
import psycopg2
import sys

def insert(rrList):
	DBNAME='postgres'
	DBUSER='postgres'
	DBHOST='localhost'
	DBPASS='temp@1'
	DBPORT='5432'

	#rrList=sys.argv[1][1:]
	#soa=sys.argv[1][0]
	soa=rrList[0]
	rrList=rrList[1:]
	zone=soa[0]
	conn = psycopg2.connect(dbname=DBNAME, user=DBUSER, host=DBHOST, password=DBPASS,port = DBPORT)
	cur = conn.cursor()

	print soa[0]+", "+str(soa[1])+", "+soa[3]+", "+soa[4]+", "+soa[5]+", "+str(soa[6])+", "+str(soa[7])+", "+str(soa[8])+", "+str(soa[9])
	try:
		cur.execute('''insert into public.soa(zone_, ttl, mname, rname, serial, refresh_, retry, expire, minimum) values (%s, %s, %s, %s, %s, %s, %s, %s, %s);''', (soa[0], soa[1], soa[3], soa[4], soa[5], soa[6], soa[7], soa[8], soa[9]))
	except Exception, e: #Exception raised if the zone is already in the soa file
		conn.commit()#Not sure why I need this but I do...
		cur.execute("update public.soa set ttl=%s, mname=%s, rname=%s, serial=%s, refresh_=%s, retry=%s, expire=%s, minimum=%s where zone_=%s;", (soa[1], soa[3], soa[4], soa[5], soa[6], soa[7], soa[8], soa[9], soa[0]))


	for rr in rrList:
		if rr[2] == 'NS':
		    print('NS record:\n\thost = %s\n\tttl = %s\n\tdata = %s\n' % (rr[0], rr[1], rr[3]))
		    cur.execute('''insert into ns
		    (zone_, ttl, host, nsdname) values
		    (%s, %s, %s, %s);''', (zone, rr[1], rr[0], rr[3]))
		elif rr[2] == 'A':
		    print('A record:\n\thost = %s\n\tttl = %s\n\tdata = %s\n' % (rr[0], rr[1], rr[3]))
		    cur.execute('''insert into a
		    (zone_, ttl, host, address) values
		    (%s, %s, %s, %s);''', (zone, rr[1], rr[0], rr[3]))
		elif rr[2] == 'AAAA':
		    print('AAAA record:\n\thost = %s\n\tttl = %s\n\tdata = %s\n' % (r[0], r[1], r[3]))
		    cur.execute('''insert into aaaa
		    (zone_, ttl, host, address) values
		    (%s, %s, %s, %s);''', (zone, r[1], r[0], r[3]))

	conn.commit()
	cur.close()
	conn.close()

###########################


