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
import matplotlib as plt


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


def vectorizeRecipes(ingrVector=baseIngredients, recipeIDs='', ):
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

	baseIngredients = ['bananas', 'eggs','all-purpose flour','sugar','salt','baking soda','vanilla extract','baking powder','butter','cinnamon','milk','brown sugar', 'whole wheat flour']
	baseIngredients = ['bananas', 'eggs','all-purpose flour','sugar','salt','baking soda','vanilla extract','baking powder','butter','sour cream', 'milk','buttermilk','water', 'whole wheat flour']

	frame = vectorizeRecipes()
	frame.to_csv('dummymatrix.csv')
	frame.to_csv('dummymatrix.tsv', sep="\t")

	#frame2 = pd.DataFrame(ingrHashunit, index = baseIngredients,columns = ingrHashunit.keys()).T.astype(float)
	#frame2.to_csv('dummymatrix2.tsv', sep="\t")
