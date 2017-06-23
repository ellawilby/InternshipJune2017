#!/usr/bin/env python
import fileinput
import os
import dns.resolver
import spf

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


#url='www.capitec.co.za'
#ip = dns.resolver.query(url, 'A')
#print spf.check2('180.73.166.174', 'someone@gmail.com', 'gmail.com')

#does TXT check on each url in banksList.txt
for line in file:
	#print line
	parts=line.split()
	url=parts[len(parts)-1][4:]
	try:
		answers=dns.resolver.query(url, 'TXT')
		outputFile.write('\n'+str(answers.qname)+' num_ans.'+str(len(answers))+', ')
		#print 'query qname:', answers.qname, ' num ans.', len(answers)
		for rdata in answers:
		    	for txt_string in rdata.strings:
				outputFile.write(txt_string+', ')
				if txt_string.find("v=spf")>-1:
					spfFile.write('\n'+str(answers.qname)+', ')
					spfFile.write(txt_string+', ')
				if txt_string.find("dmarc")>-1:
					dmarcFile.write('\n'+str(answers.qname)+', ')
					dmarcFile.write(txt_string+', ')
					
	
	except Exception:
		#print url+" has no TXT record"
		outputFile.write('\n'+url+' num_ans.0,')
		outputFile.write(" "+url+" has no TXT record")
	#os.system("bash -c './searchOnURL.py %s banksTXT.txt banksSPF.txt'" % url)
file.close
outputFile.close
spfFile.close
dmarcFile.close
