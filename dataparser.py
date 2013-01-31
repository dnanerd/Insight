#!/Users/apple/Desktop/Work/Scripts/Insight/venv/bin/python

#import pymongo #==2.4.2
import json
import yummly #https://github.com/dgilland/yummly.py
import sys
import re
import unicodedata
from collections import *
import time
#sys.path.append('/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages')
import pymongo
import MySQLdb

# Open database connection
db = MySQLdb.connect("localhost",'testuser','testpass',"yummly" )
# prepare a cursor object using cursor() method
cursor = db.cursor()

def searchDatabase(query, outFile, startRec=0):
	results = yummly.search(query, start=startRec)
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
	errors = 0
	counter = startRec
	while(counter<totalRecords):
		print "Starting at ", counter
		results	= yummly.search(query, start=counter)
		print "Found ", len(results["matches"]), " additional records..."
		f 	= 	open(outFile,'w')
		f.write(json.dumps(results, indent=4, separators = (',',': ')))
		f.close()

		for item in results["matches"]:
			(itemid, rating, totaltime, itemname, source) = ['NULL']*5
			try:
				if 'id' in item.keys(): itemid = item['id'].decode('string_escape').replace("\'","\\\'")
				if 'rating' in item.keys(): rating = str(item['rating'])
				if 'totalTimeInSeconds' in item.keys(): totaltime = str(item['totalTimeInSeconds'])
				if 'recipeName' in item.keys(): itemname = item['recipeName'].decode('string_escape').replace("\'","\\\'")
				if 'sourceDisplayName' in item.keys(): source = item['sourceDisplayName'].decode('string_escape').replace("\'","\\\'")
				cursor.execute("INSERT IGNORE INTO records(id, rating, totaltime, name, source) VALUES(\'"+ itemid+'\','+rating+','+totaltime+',\''+itemname+"\',\'"+source+"\')")
			except:
				errors+=1

		print len(results["matches"]), " records inserted into database..."
#		time.sleep(50)
		counter += len(results["matches"])
		db.commit()
	cursor.close()
	db.close()
	print errors, " records did not fit expectations and threw an error."

def pullRecipes(searchResultFile, recipeFile):

	f = open(searchResultFile, 'r')
	searchResult = json.loads(f.read())
	f.close()

	recipeList = [];
	for item in searchResult["matches"]:
		recipe_id = item['id']
		recipe = yummly.recipe(recipe_id)
		recipeList.append(recipe)
	fr 	= 	open(recipeFile,'w')
	fr.write(json.dumps(recipeList, indent=4, separators = (',',': ')))
	fr.close()
	return recipeList


def parseSearchResults(searchResultFile):
	f = open(searchResultFile, 'r')
	searchResult = json.loads(f.read())
	f.close()

	ingredientHash = Counter()
	for item in searchResult["matches"]:
		for ingr in item['ingredients']:
			ingredientHash[ingr.decode('string_escape')]+=1
	print "Num results: ", len(searchResult["matches"])
	for key, val in ingredientHash.most_common():
		print key, "\t", val


def parseRecipes(recipeFile):
	fr = open(recipeFile, 'r')
	recipeList = json.loads(fr.read())
	fr.close()

	for recipe in recipeList:
		ingredientList = recipe["ingredientLines"]
		for ingr in ingredientList:
			ingredientHash[repr(ingr)]+=1



#decoded = json.loads(results)


yummly.api_id	=	'5dd6a908'
yummly.api_key	=	'1144f281d7ac2e4d2f08ba7883bdc396'
outFile	= "search.output2.txt"
recipeFile = "search.recipes.txt"
res = searchDatabase("banana bread", outFile, 400)

#parseSearchResults(outFile)
#pullRecipes(outFile, recipeFile)
#recipeList = parseRecipes(recipeFile)
