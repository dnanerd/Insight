#!/Users/apple/Desktop/Work/Scripts/Insight/venv/bin/python

#import pymongo #==2.4.2
import datashopper, datamaid
import json
import yummly #https://github.com/dgilland/yummly.py
import sys
import re
import unicodedata
from collections import *
import time
import pymongo
import MySQLdb as sql
import pprint
import re
import copy
import numpy as np
import scipy as sp
import pandas as pd
import nltk
import networkx as nx


try:
    import sklearn as ml
except ImportError:
    import scikits.learn as ml


#modify baseIngredients to be all ingredients
def digify(numstr):
	if numstr == 'NULL': return 0
	ranges = numstr.split('-')
	numstr = ranges[0].strip() #we only take lower range for now
	if not numstr: return 0
	digits = numstr.split()
	sum = 0
	for d in digits:
		m = re.search('(\d+)/(\d+)',d)
		if m:
			#it's a fraction
			sum += float(m.group(1))/float(m.group(2))
		else:
			#not a fraction
			sum += float(d)
	return sum
def retrieveSearchRecords(searchResultFile):
	f = open(searchResultFile, 'r')
	results = f.read().split("\n")
	table = [row.split("\t") for row in results]
	return table

def vectorizeIngredients():
	searchResultFile = 'searchrecordids.txt'
	records = retrieveSearchRecords(searchResultFile)
	recordsHash = dict(records)
	#restrict this for now; later put it up on hadoop
	cursor.execute("SELECT records.id, ingredient, name FROM recipeingredients, records WHERE recipeingredients.id=records.id AND records.id IN (\'"+"\',\'".join(recordsHash.keys())+"\')")
	ingredientTuples = cursor.fetchall()

#	return pd.DataFrame(zip(*ingredientTuples),index=['id','ingredient', 'name']).T
	ingrHash = defaultdict(tuple)
	ingredients = set([ingTup[1] for ingTup in ingredientTuples])
	for rid, ingredient, name in ingredientTuples:
		


def vectorizeRecipes(recipeIDs='', ):
	cursor = db.cursor()
	cursor.execute("""SELECT * FROM formatrecipes""")
	recipeTuples = cursor.fetchall()

	ingrHash = defaultdict(tuple)
	ingrHashunit = defaultdict(tuple)
	recipe_db = np.asarray(recipeTuples)

	for (rid, ingLine, ing, unit, qty) in recipeTuples:
		if (recipeIDs != '') and (rid not in recipeIDs): continue

		if not rid in ingrHash.keys():
			ingrHash[rid] = ['0']*len(ingrVector)
			ingrHashunit[rid] = ['']*len(ingrVector)
		if ing in ingrVector:
			ingrHash[rid][ingrVector.index(ing)] = str(digify(qty))
			ingrHashunit[rid][ingrVector.index(ing)] = unit
			if unit in unitHash.keys():
				ingrHashunit[rid][ingrVector.index(ing)] = unitHash[unit]
	frame = pd.DataFrame(ingrHash, index = ingrVector,columns = ingrHash.keys(), dtype=float).T.astype(float)
	return frame


if __name__ == "__main__":
	pp = pprint.PrettyPrinter(indent=4)
	db = sql.connect("localhost",'testuser','testpass',"test" )
	cursor = db.cursor()
	cursor.execute("""SELECT * FROM units""")
	unitTuple = cursor.fetchall()
	unitHash = dict(unitTuple)
	pp.pprint(unitHash)

	frame = vectorizeIngredients()
	frame.to_csv('dummymatrix.csv')
	frame.to_csv('dummymatrix.tsv', sep="\t")

	#frame2 = pd.DataFrame(ingrHashunit, index = baseIngredients,columns = ingrHashunit.keys()).T.astype(float)
	#frame2.to_csv('dummymatrix2.tsv', sep="\t")
