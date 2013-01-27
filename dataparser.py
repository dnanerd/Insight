import json
import yummly
import pprint
import sys

yummly.api_id = '5dd6a908'
yummly.api_key = '1144f281d7ac2e4d2f08ba7883bdc396'

results = yummly.search('banana bread')


outFile = "search.output.txt"
f = open(outFile,'w')
printer = pprint.PrettyPrinter(indent=4, stream=f)
printer.pprint(results)
#print results["matches"]
f.close()

outFile = "search.output.parsed.txt"
f = open(outFile,'w')
for item in results["matches"]:
	f.write('New Item:\n')
	for key, val in item.iteritems():
		f.write("{0}\t{1}\n".format(key,val))
	f.write('\n')
f.close()

#decoded = json.loads(results)

print "Keys: ",",".join(results.keys())
print "Number of records: ", results["totalMatchCount"]
print "Search: ", results["criteria"]

for key,val in results.iteritems():
	if (key != "matches"):
		print "Key: ", key
		print "Value: ", repr(val)
#print "DECODED: ", decoded