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

def storeRecipes(recipeList):
	# prepare a cursor object using cursor() method
	db = MySQLdb.connect("localhost",'testuser','testpass',"test" )
	cursor = db.cursor()
	(storeerror, storesuccess, updateerror, updatesuccess) = (0,0,0,0)

	for recipe in recipeList:
		try:
			recipeid = recipe["id"]
			recipeid.replace("\'","\\\'")
			for ingrLine in recipe["ingredientLines"]:
				cursor.execute("INSERT IGNORE INTO recipes(id, ingredientLine) VALUES(\'" + recipeid + '\',\'' + ingrLine.replace("\'","\\\'") + '\')')
			storesuccess+=1
		except:
			storeerror += 1
		try:
			if 'source' in recipe.keys() and 'sourceRecipeUrl' in recipe["source"].keys():
				url = recipe["source"]["sourceRecipeUrl"]
				url.replace("\'","\\\'")
				cursor.execute("UPDATE records SET sourceurl = \'"+url+"\' WHERE id=\'"+recipeid+"\'")
			if 'numberOfServings' in recipe.keys():
				servings = recipe['numberOfServings']
				if type(servings) == int:
					cursor.execute("UPDATE records SET servings = "+str(servings)+" WHERE id=\'"+recipeid+"\'")
			updatesuccess+=1
		except:
			updateerror += 1
		db.commit()
	print storesuccess, " recipes successfully stored in database."
	if storeerror>0: print error, " recipes threw an error and failed to store."
	print updatesuccess, " recipes successfully updated in record table."
	if updateerror>0: print error, " recipes threw an error and failed to update."
	db.close()

def parseRecipeResults(recipeResultsFile):
	f = open(recipeResultsFile, 'r')
	searchResults = json.loads(f.read())
	f.close()
	for result in searchResults:
		storeRecipes(result)


#decoded = json.loads(results)

if __name__ == "__main__":
	search ="muffin"
	recipeFile = "../Insightdata/recipedb."+search.split()[0]+".flat.txt"
	f2 = open('errorsrecipes.txt', 'w')
	f2.close()
	f = open('errors.txt', 'w')

	parseRecipeResults(recipeFile)
