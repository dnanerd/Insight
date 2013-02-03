#!/Users/apple/Desktop/Work/Scripts/Insight/venv/bin/python

#import pymongo #==2.4.2
#import datashopper, datamaid

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



pp = pprint.PrettyPrinter(indent=4)
db = sql.connect("localhost",'testuser','testpass',"yummly" )
cursor = db.cursor()
cursor.execute("""SELECT * FROM units""")
unitTuple = cursor.fetchall()
unitHash = dict(unitTuple)
pp.pprint(unitHash)

baseIngredients = ['bananas', 'eggs','all-purpose flour','sugar','salt','baking soda','vanilla extract','baking powder','butter','cinnamon','milk','brown sugar', 'whole wheat flour']
baseIngredients = ['bananas', 'eggs','all-purpose flour','sugar','salt','baking soda','vanilla extract','baking powder','butter','sour cream', 'milk','buttermilk','water', 'whole wheat flour']
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

	for tup in recipeTuples:
		if (recipeIDs != '') and (tup not in recipeIDs): continue

		if not tup[0] in ingrHash.keys():
			ingrHash[tup[0]] = ['0']*len(ingrVector)
			ingrHashunit[tup[0]] = ['']*len(ingrVector)
		if tup[2] in ingrVector:
			ingrHash[tup[0]][ingrVector.index(tup[2])] = str(digify(tup[4]))
			ingrHashunit[tup[0]][ingrVector.index(tup[2])] = tup[3]
			if tup[3] in unitHash.keys():
				ingrHashunit[tup[0]][ingrVector.index(tup[2])] = unitHash[tup[3]]
	frame = pd.DataFrame(ingrHash, index = ingrVector,columns = ingrHash.keys(), dtype=float).T.astype(float)
	return frame

frame = vectorizeRecipes()
frame.to_csv('dummymatrix.csv')
frame.to_csv('dummymatrix.tsv', sep="\t")

#frame2 = pd.DataFrame(ingrHashunit, index = baseIngredients,columns = ingrHashunit.keys()).T.astype(float)
#frame2.to_csv('dummymatrix2.tsv', sep="\t")
