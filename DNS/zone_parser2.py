#!/usr/bin/python

import sys
import os
from zone_insert2.py import insert
from zone_parser2_soa import parseSOA
from zone_parser2_acceptableTypes import parseAcceptable
from zone_parser2_ns import splitNS
#from resolveArecords import resolveA
from listNS import constructNSList
from insert_NS import insertA, insertAAAA
from resolveASN_country import resolveASN_Country

####Change as required####
#Acceptable recource record types
acceptableRRTypes=['NS', 'A','AAAA', 'CNAME', 'HINFO', 'MX', 'PTR', 'SPF', 'SRV', 'TXT', 'XFR']
#Database details
DBNAME='postgres'
DBUSER='postgres'
DBHOST='localhost'
DBPASS='temp@1'
DBPORT='5432'
#AS numbers database
asnDatabase='ip2asn.bz2'
#Database structure
dropFileName="drop2.sql"
bindFileName="bind2.sql"

zoneFileName=sys.argv[1]
connStr="dbname={0} user={1} host={2} password={3} port={4}".format(DBNAME, DBUSER, DBHOST, DBPASS, DBPORT)

#Parse contents of zone file:
print "Parsing lines from", zoneFileName
#Parse SOA
(soaList, globalZONE, globalTTL)=parseSOA(zoneFileName)
#Insert SOA into database
insert(rrList, globalZONE, connStr)

if 'NS' in acceptableRRTypes:
	acceptableRRTypes.remove('NS')
	#Parse all RR types except NS
	rrList=parseAcceptable(zoneFileName, acceptableRRTypes, globalZONE, globalTTL)
	#Insert all RR types except NS into database
	insert(rrList, globalZONE, connStr)
	#Split NS records into manageable chuncks and parse NS records
	nsListList=splitNS(zoneFileName, globalZONE, globalTTL)
	#Insert chunks of NS records into database
	for nsList in nsListList:
		insert(nsList, globalZONE, connStr)
	#Resolve A records, ASN and Countries not yet in database
	#resolveA(connStr, asnDatabase)
	#Resolve A records. Creates files with list of A records to enter into the database
	aHosts="aHosts.txt"
	constructAList(connStr, aHosts)
	#Insert A records from the txt file into the database
	aRecords='.'.join(aHosts.split('.')[:-1])+"andIPs.txt"
	insertA(connStr, aRecords)
	#Fills in the AS numbers and Countries for elements in the a table
	resolveASN_Country(connStr, asnDatabase)
	#Resolve AAAA records. Creates file with list of AAAA records to enter into the database
	aaaaHosts="aaaaHosts.txt"
	constructAAAAList(connStr, aaaaHosts)
	#Insert AAAA records from the txt file into the database
	aaaaRecords='.'.join(aaaaHosts.split('.')[:-1])+"andIPs.txt"
	insertAAAA(connStr, aaaaRecords)
else:
	#Parse all RR types
	rrList=parseAcceptable(zoneFileName, acceptableRRTypes, globalZONE, globalTTL)
	#Insert all RR types into database
	insert(rrList, globalZONE, connStr)



