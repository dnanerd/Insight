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

def mysqlify(x):
	return x.replace("\'","\\\'") 
#cursor.execute("select distinct ingredient from old_recipeingredients")
#allingr = cursor.fetchall()
#for ingr in allingr:
#	cursor.execute("insert ignore into ingredients(ingredient) values (\'"+mysqlify(ingr[0])+"\')")
def storeRecords(results):
	(errorsRecords, errorsRecipes) = [0,0]

	# Open database connection
	# prepare a cursor object using cursor() method
	cursor = db.cursor()
	f=open('errors.txt', 'a')
	f2 = open('errorsrecipes.txt', 'a')
	for item in results["matches"]:
		(itemid, rating, totaltime, itemname, source) = ['NULL']*5
		try:
			if 'id' in item.keys(): itemid = mysqlify(item["id"].decode('string_escape'))
			if 'rating' in item.keys(): rating = str(item["rating"])
			if 'totalTimeInSeconds' in item.keys(): totaltime = str(item["totalTimeInSeconds"])
			if 'recipeName' in item.keys(): itemname = mysqlify(item["recipeName"].decode('string_escape'))
			if 'sourceDisplayName' in item.keys(): source = item["sourceDisplayName"].decode('string_escape').replace("\'","\\\'")
			sqlcmd = "INSERT IGNORE INTO records(id, rating, totaltime, name, sourcename) VALUES(\'"+ itemid+'\','+rating+','+totaltime+',\''+itemname+"\',\'"+source+"\')"
			cursor.execute(sqlcmd)
		except:
			errorsRecords+=1
			f.write(json.dumps(item,indent=4))
		if 'ingredients' in item.keys():
			for ingr in item["ingredients"]:
				try:
					cursor.execute("INSERT IGNORE INTO ingredients(ingredient) VALUES(\'" + mysqlify(ingr) + '\')')
					cursor.execute("INSERT IGNORE INTO recipeingredients(id, ingredient) VALUES(\'" + itemid + '\',\'' + mysqlify(ingr) + '\')')
				except:
					errorsRecipes +=1
					f2.write(ingr+"\n")
	f.close()
	f2.close()
	if errorsRecords: print errorsRecords, " records did not fit expectations and threw an error."
	if errorsRecipes: print errorsRecipes, " recipes did not fit expectations and threw an error."
	db.commit()


def searchDatabase(query, outFile, yapi_id, yapi_key, startRec=0):
	client = yummly.Client(api_id=yapi_id, api_key=yapi_key)
	results = client.search(query, maxResults=40, start=startRec)
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
			results	= client.search(query, start=counter)
			print "Found ", len(results["matches"]), " additional records..."
			storeRecords(results)
			f = open(outFile, 'a')
			f.write(json.dumps(results, indent=4))
			f.close()
			print len(results["matches"]), " records inserted into database..."
			counter += len(results["matches"])
		except:
			counter+=1


 
def storeRecipes(recipeList):
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
	print success, " recipes successfully stored in database."
	if error>0: print error, " recipes threw an error and failed to store."

def pullRecipes(searchResultFile, recipeFile, yapi_id, yapi_key):
	client = yummly.Client(api_id=yapi_id, api_key=yapi_key)
	errors = 0
	counter=0
	# Open database connection
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
#		try:
		recipe = client.recipe(recipe_id[0])
		recipeList.append(recipe)
		subRecipeList.append(recipe)
#		except:
#			errors+=1;
	if errors: print errors, " recipes could not be retrieved and threw an error."
	storeRecipes(recipeList)
	db.close()

	f = open(recipeFile, 'a')
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
	# prepare a cursor object using cursor() method
	cursor = db.cursor()
	cursor.execute("""SELECT ingredientLine FROM recipes""")

	for recipe in cursor.fetchall():
		ingredientList = recipe["ingredientLines"]
		for ingr in ingredientList:
			ingredientHash[repr(ingr)]+=1



#decoded = json.loads(results)

if __name__ == "__main__":
	db = MySQLdb.connect("localhost",'testuser','testpass',"test" )
#pmcon = pymongo.Connection('localhost', port=27017)

	yummly.api_id	=	'5b136dc3'
	yummly.api_key	=	'65a226f2bf78787e207a98499cbaec5f'
	outFile	= "search.output.txt"
	recipeFile = "search.recipes.txt"
	f2 = open('errorsrecipes.txt', 'w')
	f2.close()
	f = open('errors.txt', 'w')
	f = open(recipeFile, 'w')
	f.close()

	pullRecipes(outFile, recipeFile, yummly.api_id, yummly.api_key)
	#recipeList = parseRecipes(recipeFile)
