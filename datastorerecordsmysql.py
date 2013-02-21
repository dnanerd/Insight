#!/Users/apple/Desktop/Work/Scripts/Insight/venv/bin/python

#import pymongo #==2.4.2
import json
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
	retids = defaultdict(str)

	# Open database connection
	db = MySQLdb.connect("localhost",'testuser','testpass',"test" )
	# prepare a cursor object using cursor() method
	cursor = db.cursor()
	f=open('errors.txt', 'a')
	f2 = open('errorsrecipes.txt', 'a')
	for item in results["matches"]:
		(itemid, rating, totaltime, itemname, source, imgurl) = ['NULL']*6
		try:
			if 'id' in item.keys(): itemid = mysqlify(item["id"].decode('utf-8'))
			if 'rating' in item.keys(): rating = str(item["rating"])
			if 'totalTimeInSeconds' in item.keys(): totaltime = str(item["totalTimeInSeconds"])
			if 'recipeName' in item.keys(): itemname = mysqlify(item["recipeName"].decode('string_escape'))
			if 'sourceDisplayName' in item.keys(): source = item["sourceDisplayName"].decode('string_escape').replace("\'","\\\'")
			if 'smallImageUrls' in item.keys() and len(item["smallImageUrls"])>0: imgurl = item["smallImageUrls"][0].decode('string_escape').replace("\'","\\\'")			
			sqlcmd = "INSERT IGNORE INTO records(id, rating, totaltime, name, sourcename, imgurl) VALUES(\'"+ itemid+'\','+rating+','+totaltime+',\''+itemname+"\',\'"+source+"\',\'"+imgurl+"\')"
			cursor.execute(sqlcmd)
			retids[itemid]=1
		except:
			errorsRecords+=1
			f.write(json.dumps(item,indent=4))

		if 'ingredients' in item.keys():
			for ingr in item["ingredients"]:
				try:
					cursor.execute("INSERT IGNORE INTO ingredients(ingredient) VALUES(\'" + mysqlify(ingr) + '\')')
					cursor.execute("INSERT IGNORE INTO recipeingredients(id, ingredient) VALUES(\'" + itemid + '\',\'' + mysqlify(ingr) + '\')')
					retids[itemid]=1
				except:
					errorsRecipes +=1
					f2.write(ingr+"\n")
	f.close()
	f2.close()
	if errorsRecords: print errorsRecords, " records did not fit expectations and threw an error."
	if errorsRecipes: print errorsRecipes, " recipes did not fit expectations and threw an error."
	db.commit()
	db.close()
	return retids.keys()



def parseSearchResults(searchResultFile):
	f = open(searchResultFile, 'r')
	searchResults = json.loads(f.read())
	f.close()
	retids = []
	for result in searchResults:
		retids.extend(storeRecords(result))
	return retids


if __name__ == "__main__":

	search = "muffin"
	searchResultFile= "recordsdb."+search.split()[0]+".flat.txt"
	f2 = open('errorsrecipes.txt', 'w')
	f2.close()
	f = open('errors.txt', 'w')
	f.close()

	insertedids = parseSearchResults(searchResultFile)
	