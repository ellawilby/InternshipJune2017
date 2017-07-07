#!/usr/bin/python

#from zone_parser2 import read_file
import psycopg2
import sys
import os
import dns.resolver


def insert(rrList, globalZONE, connectionString):
	resolver=dns.resolver.Resolver()
	resolver.timeout = 1 # timoutes
	resolver.lifetime = 1
	
	if len(rrList)>0 and rrList[0][2]=='SOA':
		soa=rrList[0]
		if len(rrList)>1:
			rrList=rrList[1:]
		else:
			rrList=[]
	else:
		soa=[]
	conn = psycopg2.connect(connectionString)
	end=checkIfSOAExists(soa, bindFileName, dropFileName, conn)
	if end==False:
		insertSOA(soa, conn)
		insertRR(rrList, conn)
	sys.stdout.write('\n')
	sys.stdout.flush()
	conn.commit()
	conn.close()


#Checks that the zone isn't already in the SOA table
def checkIfSOAExists(soa, bindFileName, dropFileName, conn): 
	cur = conn.cursor()
	end = False
	
	try:
		cur.execute("select zone_ from soa where zone_='{0}'".format(soa[0]))
		zones=cur.fetchall()
	except Exception:
		zones=[]
	try:
		if len(zones)>0:
			drop= raw_input("WARNING: There is data in the database for this domain. Would you like to scrub it? (y/n)")
			if drop.find('y')!=-1 or drop.find('Y')!=-1:#Yes
				#Drop existing tables
				dropFile=open(dropFileName, "r")
				for line in dropFile:
					cur.execute(line)
				conn.commit()
				#Recreate tables
				bindFile=open(bindFileName, "r")
				script=bindFile.read()
				lines=script.split(';')[:-1]
				conn.commit()
				for line in lines:
					cur.execute(line)
				conn.commit()
				print "Recreated", len(lines),"tables"
			else:#No. Stop doing stuff
				end=True
	except Exception, e:
		#Create tables
		print e
		bindFile=open(bindFileName, "r")
		script=bindFile.read()
		lines=script.split(';')[:-1]
		conn.commit()
		for line in lines:
			cur.execute(line)
		conn.commit()
		print "Created", len(lines),"tables"

	cur.close()
	return end
		

def insertSOA(soa, conn):
	cur=conn.cursor()
	print "Inserting resource records into database"
	try:
		if len(soa)>0:
			cur.execute('''insert into soa(zone_, ttl, mname, rname, serial, refresh_, retry, expire, minimum) values (%s, %s, %s, %s, %s, %s, %s, %s, %s);''', (soa[0], soa[1], soa[4], soa[5], soa[6], soa[7], soa[8], soa[9], soa[10]))
			sys.stdout.write('s')
	except Exception, e: #Exception raised if the zone is already in the soa filerint e
		sys.stdout.write('-')
	cur.close()


def insertRR(rrList, conn):
	cur=conn.cursor()
	for rr in rrList:
		if rr[2] == 'NS':
			cur.execute('''insert into ns (zone_, ttl, host, nsdname) values (%s, %s, %s, %s);''', (rr[4], rr[1], rr[0], rr[3]))
			sys.stdout.write('n')
		elif rr[2] == 'A':
			cur.execute('''insert into a (zone_, ttl, host, address, asn, country) values (%s, %s, %s, %s::inet, DEFAULT, DEFAULT);''', (rr[4], rr[1], rr[0], rr[3]))
			sys.stdout.write('a')
		elif rr[2] == 'AAAA':
			cur.execute('''insert into aaaa (zone_, ttl, host, address) values (%s, %s, %s, %s::inet);''', (rr[4], rr[1], rr[0], rr[3]))
			sys.stdout.write('A')
		elif rr[2] == 'CNAME':
			cur.execute('''insert into cname (zone_, ttl, host, cname) values (%s, %s, %s, %s);''', (rr[4], rr[1], rr[0], rr[3]))
			sys.stdout.write('c')
		elif rr[2] == 'HINFO':
			data=filter(None, rr.split('"'))
			if len(data)==1:
				data=filter(None, rr.split(' '))
			cur.execute('''insert into hinfo (zone_, ttl, host, cpu, os) values (%s, %s, %s, %s);''', (rr[4], rr[1], rr[0], data[0], data[len(data)-1]))
			sys.stdout.write('h')
		elif rr[2] == 'MX':
			data=filter(None, rr[3].split(' '))
			cur.execute('''insert into mx (zone_, ttl, host, preference, exchange) values (%s, %s, %s, %s);''', (rr[4], rr[1], rr[0], int(data[0]), data[len(data)-1]))
			sys.stdout.write('m')
		elif rr[2] == 'PTR':
			cur.execute('''insert into ptr (zone_, ttl, host, ptrdname) values (%s, %s, %s, %s);''', (rr[4], rr[1], rr[0], rr[3]))
			sys.stdout.write('p')
		elif rr[2] == 'SPF':
			cur.execute('''insert into spf (zone_, ttl, host, txt_data) values (%s, %s, %s, %s);''', (rr[4], rr[1], rr[0], rr[3]))
			sys.stdout.write('S')
		elif rr[2] == 'SRV':
			data=filter(None, rr.split(' '))
			cur.execute('''insert into srv (zone_, ttl, host, priority, weight, port, target) values (%s, %s, %s, %s, %s, %s, %s);''', (rr[4], rr[1], rr[0], int(data[0]), int(data[1]), int(data[2]), data[3]))
			sys.stdout.write('v')
		elif rr[2] == 'TXT':
			cur.execute('''insert into txt (zone_, ttl, host, txt_data) values (%s, %s, %s, %s);''', (rr[4], rr[1], rr[0], rr[3]))
			sys.stdout.write('t')
		elif rr[2] == 'XFR':
			cur.execute('''insert into xfr (zone_, client) values (%s, %s, %s, %s);''', (rr[4], rr[0]))
			sys.stdout.write('x')
		else:
			sys.stdout.write('-')
				
	cur.close()

	###########################


