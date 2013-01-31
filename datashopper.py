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
import MySQLdb


def storeRecords(results):
	(errorsRecords, errorsRecipes) = [0,0]

	# Open database connection
	db = MySQLdb.connect("localhost",'testuser','testpass',"yummly" )
	# prepare a cursor object using cursor() method
	cursor = db.cursor()

	for item in results["matches"]:
		(itemid, rating, totaltime, itemname, source) = ['NULL']*5
		try:
			if 'id' in item.keys(): itemid = item["id"].decode('string_escape').replace("\'","\\\'")
			if 'rating' in item.keys(): rating = str(item["rating"])
			if 'totalTimeInSeconds' in item.keys(): totaltime = str(item["totalTimeInSeconds"])
			if 'recipeName' in item.keys(): itemname = item["recipeName"].decode('string_escape').replace("\'","\\\'")
			if 'sourceDisplayName' in item.keys(): source = item["sourceDisplayName"].decode('string_escape').replace("\'","\\\'")
			cursor.execute("INSERT IGNORE INTO records(id, rating, totaltime, name, sourcename) VALUES(\'"+ itemid+'\','+rating+','+totaltime+',\''+itemname+"\',\'"+source+"\')")
		except:
			errorsRecords+=1

		if 'ingredients' in item.keys():
			for ingr in item["ingredients"]:
				try:
					cursor.execute("INSERT IGNORE INTO ingredients(id, ingredient) VALUES(\'" + itemid + '\',\'' + ingr + '\')')
				except:
					errorsRecipes +=1
	if errorsRecords: print errorsRecords, " records did not fit expectations and threw an error."
	if errorsRecipes: print errorsRecipes, " recipes did not fit expectations and threw an error."
	db.commit()
	db.close()


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
	counter = startRec

	while(counter<totalRecords):
		print "Starting at ", counter
		results	= yummly.search(query, start=counter)
		print "Found ", len(results["matches"]), " additional records..."
		f 	= 	open(outFile,'w')
		f.write(json.dumps(results, indent=4, separators = (',',': ')))
		f.close()
		storeRecords(results)
		print len(results["matches"]), " records inserted into database..."
#		time.sleep(10)
		counter += len(results["matches"])
 
def storeRecipes(recipeList):
	db = MySQLdb.connect("localhost",'testuser','testpass',"yummly" )
	# prepare a cursor object using cursor() method
	cursor = db.cursor()
	error = 0
	success = 0
	for recipe in recipeList:
		try:
			recipeid = recipe["id"]
			recipeid.replace("\'","\\\'")
			for ingrLine in recipe["ingredientLines"]:
				cursor.execute("INSERT IGNORE INTO recipes(id, ingredientLine) VALUES(\'" + recipeid + '\',\'' + ingrLine.replace("\'","\\\'") + '\')')
			if 'source' in recipe.keys() and 'sourceRecipeUrl' in recipe["source"].keys():
				url = recipe["source"]["sourceRecipeUrl"]
				url.replace("\'","\\\'")
				cursor.execute("UPDATE records SET sourceurl = \'"+url+"\' WHERE id=\'"+recipeid+"\'")
			if 'numberOfServings' in recipe.keys():
				servings = recipe['numberOfServings']
				if type(servings) == int:
					cursor.execute("UPDATE records SET servings = "+str(servings)+" WHERE id=\'"+recipeid+"\'")
			success += 1
		except:
			error += 1
		db.commit()
	db.close()
	print success, " recipes successfully stored in database."
	if error>0: print error, " recipes threw an error and failed to store."

def pullRecipes(searchResultFile, recipeFile):
	errors = 0
	counter=0
	# Open database connection
	db = MySQLdb.connect("localhost",'testuser','testpass',"yummly" )
	# prepare a cursor object using cursor() method
	cursor = db.cursor()
	cursor.execute("""SELECT id FROM records""")
	recipeList = []
	subRecipeList = []
	for recipe_id in cursor.fetchall():
		if (len(recipeList)>0 and len(recipeList)%10 == 0 ):
			print len(recipeList), " recipes found"
			storeRecipes(subRecipeList)
			subRecipeList = []
		try:
			recipe = yummly.recipe(recipe_id[0])
			recipeList.append(recipe)
			subRecipeList.append(recipe)
		except:
			errors+=1;
	if errors: print errors, " recipes could not be retrieved and threw an error."
	storeRecipes(recipeList)
	db.close()

	f = open(recipeFile, 'w')
	f.write(json.dumps(recipeList))
	f.close()

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


def parseRecipes():
	db = MySQLdb.connect("localhost",'testuser','testpass',"yummly" )
	# prepare a cursor object using cursor() method
	cursor = db.cursor()
	cursor.execute("""SELECT ingredientLine FROM recipes""")

	for recipe in cursor.fetchall():
		ingredientList = recipe["ingredientLines"]
		for ingr in ingredientList:
			ingredientHash[repr(ingr)]+=1



#decoded = json.loads(results)


yummly.api_id	=	'5dd6a908'
yummly.api_key	=	'1144f281d7ac2e4d2f08ba7883bdc396'
outFile	= "search.output2.txt"
recipeFile = "search.recipes.txt"
#res = searchDatabase("banana bread", outFile, 0)

#parseSearchResults(outFile)
#pullRecipes(outFile, recipeFile)
#recipeList = parseRecipes(recipeFile)
