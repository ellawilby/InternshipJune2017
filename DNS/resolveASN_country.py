#!/usr/bin/python

from fillAtable import addASNandCountry
import sys
import pyasn


def resolveASN_Country(connectionString, asndbName):
	asndb=pyasn.pyasn(asndbName)

	alph=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '.', '-']
	#For loops break down sizo of section to enter into the database. Can be removed for small datasets
	for a in alph:
		#print "Filling in A records and addresses for domains not in the a table"
		for b in alph:
			#Spliced N and D records even further
			if alph=='N' or alph=='D':
				for c in aplh:
					addASNandCountry(asndb, connectionString, a+b+c)
			else:
				addASNandCountry(asndb, connectionString, a+b)

