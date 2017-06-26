#!/usr/bin/env python
import fileinput
import os
import dns.resolver
import spf
import sys

fname='banksList.txt'
file=open(fname, 'r')
outputFile=open("banksTXT.txt","w")
spfFile=open("banksSPF.txt", "w")
dmarcFile=open("banksDMARC.txt", "w")

#Cleans current contents
#outputFile.write("")
#outputFile.close
#spfFile.write("")
#spfFile.close

#some stats variables
dcount=0
spfcount=0

#url='www.capitec.co.za'
#ip = dns.resolver.query(url, 'A')
#print spf.check2('180.73.166.174', 'someone@gmail.com', 'gmail.com')

#does TXT check on each url in banksList.txt
#add some progress details


# create a resolver opbject we can use
# lets one set timeouts
resolver = dns.resolver.Resolver()
resolver.timeout = 1 # timoutes
resolver.lifetime = 1

print " Starting  to process SPF data for domains in ",fname
for line in file:
	
	#print line
#	parts=line.split()
#	url=parts[len(parts)-1][4:]
	# strip any white space at end of line
	url=line.rstrip()
	
	try:
		answers=resolver.query(url, 'TXT')
		#print 'DEBUG: query qname:', answers.qname, ' num ans.',len(answers) ,'rdata:',answers.rdata
		outputFile.write('\n'+str(answers.qname)+' num_ans.'+str(len(answers))+', ')
		for rdata in answers:
		    	for txt_string in rdata.strings:
				outputFile.write(txt_string+', ')
				if txt_string.find("v=spf")>-1:
					spfFile.write('\n'+str(answers.qname)+', ')
					spfFile.write(txt_string+', ')
		sys.stdout.write('+')	
		spfcount=spfcount+1
	except dns.resolver.NXDOMAIN as enx:
           	# print "Error: NXDOMAIN - domain does not exist"
           	# writeLog("Error: NXDOMAIN - domain does not exist")
		outputFile.write('\n'+url+' num_ans.0,')
                outputFile.write(" "+url+" returned NXDOMAIN")
		sys.stdout.write('x')
        except dns.resolver.Timeout as etime:
            	#	print "Error: dns.exception.Timeout"
            	#	writeLog("Error: dns.exception.Timeout")
		outputFile.write('\n'+url+' num_ans.0,')
                outputFile.write(" "+url+" TIMEDOUT")
		sys.stdout.write('t');
	except Exception:
	#	print url+" has no TXT record"
		outputFile.write('\n'+url+' num_ans.0,')
		outputFile.write(" "+url+" has no TXT record")
		sys.stdout.write('-')
	#os.system("bash -c './searchOnURL.py %s banksTXT.txt banksSPF.txt'" % url)
	sys.stdout.flush()
	dcount=dcount+1
	
	
print "Processed", dcount, "domains with ",spfcount,"having SPF records"

file.close
outputFile.close
spfFile.close
dmarcFile.close
