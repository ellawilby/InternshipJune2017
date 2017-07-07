#!/usr/bin/env python
import os
import dns.resolver
import spf
import sys
from cleanIncludes2 import clean

fname=sys.argv[1]
outName='.'.join(fname.split('.')[:-1])
file=open(fname, 'r')
outputFile=open(outName+"TXT.txt","w")
spfFile=open(outName+"SPF.txt", "w")
dmarcFile=open(outName+"DMARC.txt", "w")
lameFile=open(outName+"_timeout.txt", "w")

#Cleans current contents
#outputFile.write("")
#outputFile.close
#spfFile.write("")
#spfFile.close

#some stats variables
dcount=0
spfcount=0


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
	#parts=line.split()
	#url=parts[len(parts)-1][4:]
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
            	# print "Error: dns.exception.Timeout"
            	# writeLog("Error: dns.exception.Timeout")
		outputFile.write('\n'+url+' num_ans.0,')
                outputFile.write(" "+url+" TIMEDOUT")
		lameFile.write(url)
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

file.close()
outputFile.close()
spfFile.close()
dmarcFile.close()

#Resolve all domain names for IP addresses

clean("banksListSPF.txt")

