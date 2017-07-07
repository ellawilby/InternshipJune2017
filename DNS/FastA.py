#!/usr/bin/env python
import fileinput
import os
import dns.resolver
import spf
import sys

import Queue
import threading

fname=sys.argv[1]
outName=sys.argv[2]
outputFile=open(outName,"w")
timeoutLog=open("TimeoutLog.txt","w")
NXlog=open("NXlog.txt","w")
errorlog=open("error.txt","w")



# create a resolver opbject we can use
# lets one set timeouts
resolver = dns.resolver.Resolver()
resolver.nameservers = ['146.231.133.164']
resolver.timeout = 1 # timoutes
resolver.lifetime = 0.5 




class ThreadDnsLookup(threading.Thread):

	def __init__(self, queue):
       		threading.Thread.__init__(self)
        	self.queue = queue

	def run(self):
        	while True:
            		fqdn = self.queue.get()
			try:
                		answers=resolver.query(fqdn, 'A')
                		tmplist=[]
                		for rdata in answers:
                        		tmplist.append(rdata.to_text())
                
				tmpstring= '%s,%s\n' % (fqdn, (','.join(tmplist)))
                        	outputFile.write(tmpstring)
               			sys.stdout.write('+')
			except dns.resolver.NXDOMAIN as enx:
                		tmpstring = '%s\n' % (fqdn)
                		NXlog.write(tmpstring)
       			        sys.stdout.write('x')
        		except dns.resolver.Timeout as etime:
                		tmpstring = '%s\n' % (fqdn)
                		timeoutLog.write(tmpstring)
                		sys.stdout.write('t');
        		except Exception:
                		tmpstring='%s ERROR UNKNOWN\n' % (fqdn)
                		errorlog.write(tmpstring)
                		sys.stdout.write('-')

        		sys.stdout.flush()
			
			# indicate that the lookup is complete
           		self.queue.task_done()



if __name__ == '__main__':

    print " Starting  to process A data for domains in ",fname

    threadCount = 48 
    fqdn_list = open(fname,'r');

    queue = Queue.Queue()
    for i in range(threadCount):
        #t = ThreadDnsLookup(queue, rcodes, rrsets)
	t = ThreadDnsLookup(queue)
        t.setDaemon(True)
        t.start()

    # add each fqdn to check to the queue for work            
    for fqdn in fqdn_list:
#	parts=line.split()
#        url=parts[len(parts)-1][4:]
        # strip any white space at end of line
#        url=line.rstrip()
        queue.put(fqdn.rstrip())
    
    # wait for all threads to finish    
    queue.join()
    

    file.close
    outputFile.close
    timeoutLog.close
    NXlog.close
    errorlog.close
