#!/usr/bin/python

#from zone_parser2 import read_file
import psycopg2
import sys
import os



def insert(rrList):

	####Change as required####
	DBNAME='postgres'
	DBUSER='postgres'
	DBHOST='localhost'
	DBPASS='temp@1'
	DBPORT='5432'
	dropFileName="drop2.sql"
	bindFileName="bind2.sql"

	soa=rrList[0]
	rrList=rrList[1:]
	zone=soa[0]
	conn = psycopg2.connect(dbname=DBNAME, user=DBUSER, host=DBHOST, password=DBPASS,port = DBPORT)
	cur = conn.cursor()
	end = False
	

	try:
		cur.execute("select zone_ from soa")
		zones=cur.fetchall()
		if (zone,) in zones:
			drop= raw_input("WARNING: There is data in the database for this domain. Would you like to scrub it? (y/n)")
			if drop.find('y')!=-1 or drop.find('Y')!=-1:
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
			else:
				end=True
	except Exception, e:
		#Recreate tables
		print e
		bindFile=open(bindFileName, "r")
		script=bindFile.read()
		lines=script.split(';')[:-1]
		conn.commit()
		for line in lines:
			cur.execute(line)
		conn.commit()
		print "Created", len(lines),"tables"

	if end==False:
		print "Inserting resource records into database"

		#print soa[0]+", "+str(soa[1])+", "+soa[3]+", "+soa[4]+", "+soa[5]+", "+str(soa[6])+", "+str(soa[7])+", "+str(soa[8])+", "+str(soa[9])
		try:
			cur.execute('''insert into soa(zone_, ttl, mname, rname, serial, refresh_, retry, expire, minimum) values (%s, %s, %s, %s, %s, %s, %s, %s, %s);''', (soa[0], soa[1], soa[3], soa[4], soa[5], soa[6], soa[7], soa[8], soa[9]))
			sys.stdout.write('s')
		except Exception, e: #Exception raised if the zone is already in the soa file
			#conn.commit()#Not sure why I need this but I do...
			#cur.execute("update public.soa set ttl=%s, mname=%s, rname=%s, serial=%s, refresh_=%s, retry=%s, expire=%s, minimum=%s where zone_=%s;", (soa[1], soa[3], soa[4], soa[5], soa[6], soa[7], soa[8], soa[9], soa[0]))
			sys.stdout.write('-')

		for rr in rrList:
			try:
				if rr[2] == 'NS':
					#print('NS record:\n\thost = %s\n\tttl = %s\n\tdata = %s\n' % (rr[0], rr[1], rr[3]))
					cur.execute('''insert into ns (zone_, ttl, host, nsdname) values (%s, %s, %s, %s);''', (zone, rr[1], rr[0], rr[3]))
					sys.stdout.write('n')
				elif rr[2] == 'A':
					#print('A record:\n\thost = %s\n\tttl = %s\n\tdata = %s\n' % (rr[0], rr[1], rr[3]))
					cur.execute('''insert into a (zone_, ttl, host, address, asn, country) values (%s, %s, %s, %s::inet, DEFAULT, DEFAULT);''', (zone, rr[1], rr[0], rr[3]))
					sys.stdout.write('a')
				elif rr[2] == 'AAAA':
					#print('AAAA record:\n\thost = %s\n\tttl = %s\n\tdata = %s\n' % (r[0], r[1], r[3]))
					cur.execute('''insert into aaaa (zone_, ttl, host, address) values (%s, %s, %s, %s::inet);''', (zone, r[1], r[0], r[3]))
					sys.stdout.write('A')
				elif rr[2] == 'CNAME':
					cur.execute('''insert into cname (zone_, ttl, host, cname) values (%s, %s, %s, %s);''', (zone, rr[1], rr[0], rr[3]))
					sys.stdout.write('c')
				elif rr[2] == 'HINFO':
					data=filter(None, rr.split('"'))
					if len(data)==1:
						data=filter(None, rr.split(' '))
					cur.execute('''insert into hinfo (zone_, ttl, host, cpu, os) values (%s, %s, %s, %s);''', (zone, rr[1], rr[0], data[0], data[len(data)-1]))
					sys.stdout.write('h')
				elif rr[2] == 'MX':
					data=filter(None, rr.split(' '))
					cur.execute('''insert into mx (zone_, ttl, host, preference, exchange) values (%s, %s, %s, %s);''', (zone, rr[1], rr[0], int(data[0]), data[len(data)-1]))
					sys.stdout.write('m')
				elif rr[2] == 'PTR':
					cur.execute('''insert into ptr (zone_, ttl, host, ptrdname) values (%s, %s, %s, %s);''', (zone, rr[1], rr[0], rr[3]))
					sys.stdout.write('p')
				elif rr[2] == 'SPF':
					cur.execute('''insert into spf (zone_, ttl, host, txt_data) values (%s, %s, %s, %s);''', (zone, rr[1], rr[0], rr[3]))
					sys.stdout.write('S')
				elif rr[2] == 'SRV':
					data=filter(None, rr.split(' '))
					cur.execute('''insert into srv (zone_, ttl, host, priority, weight, port, target) values (%s, %s, %s, %s, %s, %s, %s);''', (zone, rr[1], rr[0], int(data[0]), int(data[1]), int(data[2]), data[3]))
					sys.stdout.write('v')
				elif rr[2] == 'TXT':
					cur.execute('''insert into txt (zone_, ttl, host, txt_data) values (%s, %s, %s, %s);''', (zone, rr[1], rr[0], rr[3]))
					sys.stdout.write('t')
				elif rr[2] == 'XFR':
					cur.execute('''insert into xfr (zone_, client) values (%s, %s, %s, %s);''', (zone, rr[0]))
					sys.stdout.write('x')
				else:
					print rr
					sys.stdout.write('-')
			except Exception, e:
				print e
				sys.stdout.write('-')
				break

	sys.stdout.write('\n')
	sys.stdout.flush()
	conn.commit()
	cur.close()
	conn.close()
	os.system("./fill_details.py")
	###########################


