#!/Users/apple/Desktop/Work/Scripts/Insight/venv/bin/python

#import pymongo #==2.4.2
import datashopper

import json
import yummly #https://github.com/dgilland/yummly.py
import sys
import re
import unicodedata
from collections import *
import time
import pymongo
import MySQLdb
import pprint
import re
import copy

import nltk

pp = pprint.PrettyPrinter(indent=4)

db = MySQLdb.connect("localhost",'testuser','testpass',"yummly" )
# prepare a cursor object using cursor() method
cursor = db.cursor()
cursor.execute("""SELECT * FROM units""")
unitTuple = cursor.fetchall()
unitHash = dict(unitTuple)
pp.pprint(unitHash)


cursor.execute("""SELECT * FROM ingredients""")
ingredientTuples = cursor.fetchall()

ingredientsHash = defaultdict(int)
for ingrTup in ingredientTuples:
	if ingrTup[0] in ingredientsHash.keys():
		ingredientsHash[ingrTup[0]].append(ingrTup[1])
	else:
		ingredientsHash[ingrTup[0]] = [ingrTup[1]]


def mysqlify(x):
	return x.replace("\'","\\\'") 
#	a = a.replace('/', '\/')
#	a = a.replace("(", "\(")
#	a = a.replace(")", "\)")
#	return a

def findUnit(subIngrLine):
	unitMatched = False
	unit = 'NULL'
	count='NULL'
	if re.search('.*[A-Za-z].*',subIngrLine):
		#there is at least one word left besides ingredient
		for u in unitHash.keys():
			#for each unit in the database
			m = re.search("([-\/\d\s]+)\s?"+re.escape(u), subIngrLine, re.IGNORECASE)
			if m:
				#check that it's a word by itself (i.e. " c ")
				unitMatched = True
				unit = u
				count = m.group(1).strip()
			else:
				m = re.search(re.escape(u), subIngrLine, re.IGNORECASE)
				if m:
					unitMatched = True
					unit = u
				else:
#NOTE: this is a hack until I figure out something better
					m = re.search("([-\/\d\s]+)\s?([A-Za-z]+)", subIngrLine)
					if m:
						unitMatched = True
						count = m.group(1).strip()
						unit = m.group(2).strip()
	else:
		unitMatched = True
		unit = 'unit'
		m = re.search("^([-\/\d]+)",subIngrLine)
		if m:
			count = m.group(1).strip()
	return {'match':unitMatched, 'unit':unit, 'count':count}

def findIngredient(recipeid, ingredientLine):
	match = False
	ingredient = 'NULL'
	ingrMatchIndex = 0
	for ingr in ingredientsHash[recipeid]:
		#go through each ingredient that is require in this recipe
		#check to see if this ingredient is the one referred to by this ingreientLine
		if ingr in ingredientLine:
			ingrMatchIndex = ingredientLine.find(ingr)
			ingredient = ingr
			match = True
		elif ingr[0:-1] in ingredientLine:
			ingrMatchIndex = ingredientLine.find(ingr[0:-1])
			ingredient = ingr
			match = True
		elif (ingr+'s') in ingredientLine:
			ingrMatchIndex = ingredientLine.find(ingr+'s')
			ingredient = ingr
			match = True

	return {'match':match,'index':ingrMatchIndex, 'ingredient':ingredient}

#DESCRIPTION:
#looks through ingredients list and recipe list and parses recipe list ingredients
#into amount, unit, ingredient
def analyzeIngredients():
	# prepare a cursor object using cursor() method
	cursor = db.cursor()
	cursor.execute("""SELECT id, ingredientLine FROM bakingrecipes""")
	recipeTuples = cursor.fetchall()

#	pp.pprint(ingredientsHash)
#	fd = nltk.FreqDist()
#	for line in retrievedTuples:
#		ingredientLine = line[1]
#		words = nltk.word_tokenize(ingredientLine)
		# for each token in the relevant text, increment its counter
#		for word in words:
#			fd.inc(word)
#	print fd.N(), " samples"
#	print fd.B(), " bins"
#	for word in fd.keys()[:10]:
#		print word, fd[word]

	unit = nltk.FreqDist()
	unmatchedlines = nltk.FreqDist()

	matchedrecipes = dict(recipeTuples)
	unmatchedrecipes = defaultdict(int)
	totalmatched = 0
	total = 0
	for line in recipeTuples:
		recipeid = line[0]
		ingredientLine = line[1].lower()
		subIngrLine = ingredientLine

		if 'optional' in ingredientLine: continue

#		pp.pprint(ingredientsHash[recipeid])
	 	if recipeid in ingredientsHash.keys():
			total+=1

			ingrMatched = findIngredient(recipeid, ingredientLine)
			if (ingrMatched['match']):
				#store matches in database
				cursor.execute("UPDATE recipes SET ingredient=\'"+ingrMatched['ingredient']+"\' WHERE id = \'"+recipeid+"\' and ingredientLine = \'" + mysqlify(ingredientLine) + "\'")
				db.commit()
				subIngrLine = ingredientLine[0:int(ingrMatched['index'])]
			else:
				if recipeid in matchedrecipes.keys(): del matchedrecipes[recipeid]
				cursor.execute("UPDATE recipes SET ingredient=\'"+ingrMatched['ingredient']+"\' WHERE id = \'"+recipeid+"\' and ingredientLine = \'" + mysqlify(ingredientLine) + "\'")

			unitMatched = findUnit(subIngrLine)
			if (unitMatched['match']):
				#store matches in database
				cursor.execute("UPDATE recipes SET unit=\'"+unitMatched['unit']+"\' WHERE id = \'"+recipeid+"\' and ingredientLine = \'" + mysqlify(ingredientLine) + "\'")
				cursor.execute("UPDATE recipes SET count=\'"+mysqlify(unitMatched['count'])+"\' WHERE id = \'"+recipeid+"\' and ingredientLine = \'" + mysqlify(ingredientLine) + "\'")
				db.commit()
			else:
				if recipeid in matchedrecipes.keys(): del matchedrecipes[recipeid]
				cursor.execute("UPDATE recipes SET unit=\'"+unitMatched['unit']+"\' WHERE id = \'"+recipeid+"\' and ingredientLine = \'" + mysqlify(ingredientLine) + "\'")

			if (unitMatched['match'] and ingrMatched['match']):
				totalmatched+=1
			elif (not unitMatched['match']) and ingrMatched['match']:
				print subIngrLine
				unmatchedrecipes[recipeid]+=1
			else:
#				print "no ingredient matched: ", ingredientLine
				unmatchedrecipes[recipeid]+=1
	db.commit()
#				unmatchedlines.inc(ingredientLine)
#		else:
#			pp.pprint(ingredientsHash.keys())
#	for word in unit.keys()[:100]:
#		print word, unit[word]
#	for word in unmatchedlines.keys()[:100]:
#		print word, unmatchedlines[word]

	print totalmatched, " lines matched format out of ", total, " total lines"

	cursor.execute("""SELECT DISTINCT id FROM bakingrecipes""")
	recipeids = cursor.fetchall()
	print len(unmatchedrecipes.keys()), " unmatched recipes out of ", len(recipeids), " total recipes"
	print len(matchedrecipes.keys()), " matched recipes out of ", len(recipeids), " total recipes"

#	try:
#		cursor.execute("DROP VIEW formatrecipes")
#	except:
		#do nothing
#		print "formatrecipes does not exist; nothing to drop; continuing on"

	idlist = ",".join(matchedrecipes.keys())
	idlist = mysqlify(idlist)
	idlist = idlist.replace(",","\',\'")
#	cursor.execute("""CREATE VIEW formatrecipes AS SELECT * FROM bakingrecipes WHERE id IN (\'"+ idlist + "\')""")
	db.commit()
	db.close()
#END DEF ANALYZE INGREDIENTS

analyzeIngredients()

