#!/usr/bin/python

import json
import yummly #https://github.com/dgilland/yummly.py
import sys
#import my_sql


def searchDatabase(query, outFile):
	results	= yummly.search(query)

	f = open(outFile,'w')
	f.write(json.dumps(results, indent=4, separators = (',',': ')))
	f.close()


	print "Keys: ",",".join(results.keys())
	print "Number of records: ", results["totalMatchCount"]
	print "Search: ", results["criteria"]

	for key,val in results.iteritems():
		if (key != "matches"):
			print "Key: ", key
			print "Value: ", repr(val)
		#print "DECODED: ", decoded

	return(results)


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

def parseRecipes(recipeFile):
	fr = open(recipeFile, 'r')
	recipeList = json.loads(fr.read())
	fr.close()
	for recipe in recipeList:
		ingredientList = recipe["ingredientLines"]



#decoded = json.loads(results)


yummly.api_id	=	'5dd6a908'
yummly.api_key	=	'1144f281d7ac2e4d2f08ba7883bdc396'
outFile	= "search.output.txt"
recipeFile = "search.recipes.txt"
#res = searchDatabase("banana bread", outFile)

#pullRecipes(outFile, recipeFile)
recipeList = parseRecipes(recipeFile)