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

def storeRecipes(recipeList):
	if recipeList:
		f = open(recipeFile, 'a')
		f.write(json.dumps(recipeList))
		f.write(",")
		f.close()

def pullRecipes(searchResultFile, recipeFile, yapi_id, yapi_key):
	errors = 0
	counter=0
	# Open database connection

	f=open(searchResultFile, 'r')
	searchRecords = json.loads(f.read())
	f.close()
	recipeids = [item["id"] for result in searchRecords for item in result["matches"] if 'id' in item.keys()]

	counter = 0
	subRecipeList = []
	for recipe_id in recipeids:
		counter+=1
		if (counter>0 and counter%50 == 0):
			print counter, " recipes found"
			storeRecipes(subRecipeList)
			subRecipeList = []
			if errors: print errors, " recipes could not be retrieved and threw an error."
			errors = 0
		try:
			recipe = yummly.recipe(recipe_id)
			subRecipeList.append(recipe)
		except:
			errors+=1;

	if len(subRecipeList)>0:
		storeRecipes(subRecipeList)


#decoded = json.loads(results)

if __name__ == "__main__":


	yummly.api_id	=	'5dd6a908'
	yummly.api_key	=	'1144f281d7ac2e4d2f08ba7883bdc396'
	search ="cookies"
	outFile	= "recordsdb."+search.split()[0]+".flat.txt"
	recipeFile = "recipedb."+search.split()[0]+".flat.txt"
	f2 = open('errorsrecipes.txt', 'w')
	f2.close()
	f = open('errors.txt', 'w')
	f.close()


	#parseSearchResults(outFile)
	f = open(recipeFile, 'w')
	f.write("[")
	f.close()

	pullRecipes(outFile, recipeFile, yummly.api_id, yummly.api_key)
	f = open(recipeFile, 'a')
	f.write("]")
	f.close()
	#recipeList = parseRecipes(recipeFile)
