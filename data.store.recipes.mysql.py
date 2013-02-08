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

def parseRecipeResults(recipeResultsFile):
	f = open(recipeResultsFile, 'r')
	searchResults = json.loads(f.read())
	f.close()
	for result in searchResults:
		storeRecipes(result)


#decoded = json.loads(results)

if __name__ == "__main__":
	db = MySQLdb.connect("localhost",'testuser','testpass',"test" )
#pmcon = pymongo.Connection('localhost', port=27017)
	search ="cookies"
	recipeFile = "recipedb."+search.split()[0]+".flat.txt"
	f2 = open('errorsrecipes.txt', 'w')
	f2.close()
	f = open('errors.txt', 'w')

	parseRecipeResults(recipeFile)
	db.commit()
	db.close()
