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


def pullRecipes(recipeFile, yapi_id, yapi_key):
#	client = yummly.Client(api_id=yapi_id, api_key=yapi_key)
	errors = 0
	counter=0
	# Open database connection
	# prepare a cursor object using cursor() method
	cursor = db.cursor()
	cursor.execute("""SELECT id FROM records WHERE id REGEXP \'.*banana.*bread.*\'""")
	recipeList = []
	subRecipeList = []
	for recipe_id in cursor.fetchall():
		if (len(recipeList)>0 and len(recipeList)%10 == 0 ):
			print len(recipeList), " recipes found"
			subRecipeList = []
		try:
			recipe = yummly.recipe(recipe_id[0])
			recipeList.append(recipe)
			subRecipeList.append(recipe)
		except:
			errors+=1;
	if errors: print errors, " recipes could not be retrieved and threw an error."

	f = open(recipeFile, 'a')
	f.write(json.dumps(recipeList))
	f.write(",")
	f.close()


#decoded = json.loads(results)

if __name__ == "__main__":
	db = MySQLdb.connect("localhost",'testuser','testpass',"test" )
#pmcon = pymongo.Connection('localhost', port=27017)

	yummly.api_id	=	'5b136dc3'
	yummly.api_key	=	'65a226f2bf78787e207a98499cbaec5f'
	recipeFile = "recipedb.banana.flat.txt"
	f2 = open('errorsrecipes.txt', 'w')
	f2.close()
	f = open('errors.txt', 'w')
	f.close()


	#parseSearchResults(outFile)
	f = open(recipeFile, 'w')
	f.write("[")
	f.close()

	pullRecipes(recipeFile, yummly.api_id, yummly.api_key)

	f = open(recipeFile, 'a')
	f.write("]")
	f.close()
	#recipeList = parseRecipes(recipeFile)
