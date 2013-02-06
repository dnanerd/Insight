#!/Users/apple/Desktop/Work/Scripts/Insight/venv/bin/python

#import pymongo #==2.4.2
import json
import yummly #https://github.com/dgilland/yummly.py
import sys
import re
import unicodedata
from collections import *
import time
import pymongo

def searchDatabase(query, outFile, yapi_id, yapi_key, startRec=0):
#	client = yummly.Client(api_id=yapi_id, api_key=yapi_key)
	results = yummly.search(query, maxResults=40, start=startRec)
#	client.metadata('technique')
#	f.open('clientmetadata.txt','w')
#	f.write(client)
#	f.close()
	totalRecords = results["totalMatchCount"]
#	print results["matches"][0]["id"]

	print "Keys: ",",".join(results.keys())
	print "Number of records: ", results["totalMatchCount"]
	print "Search: ", results["criteria"]
	for key,val in results.iteritems():
		if (key != "matches"):
			print "Key: ", key
			print "Value: ", repr(val)
		#print "DECODED: ", decoded
	counter = startRec

	while(counter<totalRecords):
		print "Starting at ", counter
		try:
			results	= yummly.search(query, start=counter)
			print "Found ", len(results["matches"]), " additional records..."
			counter += len(results["matches"])
			print len(results["matches"]), " records inserted into database..."
		except:
			counter +=1
		if results:
			f = open(outFile, 'a')
			f.write(json.dumps(results, indent=4))
			f.close()


if __name__ == "__main__":
#pmcon = pymongo.Connection('localhost', port=27017)

	yummly.api_id	=	'5b136dc3'
	yummly.api_key	=	'65a226f2bf78787e207a98499cbaec5f'
	outFile	= "recordsdb.cake.flat.txt"
	f = open('errors.txt', 'w')
	f.close()
	f = open(outFile, 'w')
	f.close()


#	res = searchDatabase("banana bread", outFile, yummly.api_id, yummly.api_key, 0)
#	res = searchDatabase("cake", outFile, yummly.api_id, yummly.api_key, 0)
#	res = searchDatabase("cookies", yummly.api_id, yummly.api_key, 0) #stopped at 20800
#	res = searchDatabase("loaf", outFile, 0)
