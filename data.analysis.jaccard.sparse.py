#!/Users/apple/Desktop/Work/Scripts/Insight/venv/bin/python
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
import pickle

MINRANGE = 0
MAXRANGE = 1000

db = sql.connect("localhost",'testuser','testpass',"test" )
cursor = db.cursor()

cursor.execute("SELECT DISTINCT id FROM normrecipeingredients")
recipeTuples = cursor.fetchall()
recipeToIndex = dict([(rid[0], i) for i, rid in enumerate(recipeTuples)])

cursor.execute("SELECT id, normingredient FROM normrecipeingredients")
recipeTuples = cursor.fetchall()

recipesHash = defaultdict(list)
ingredientHash = defaultdict(list)
for rid, ingr in recipeTuples:
	recipesHash[rid].append(ingr)
	ingredientHash[ingr].append(rid)
pickle.dump(recipesHash, open("idToIngredient.pickle", 'w'))

db.commit()
db.close()


jaccardHash = defaultdict(float)
sys.stderr.write("Now calculating Jaccard distances")
counter1 = 0
for rid1, ingrList1 in recipesHash.iteritems():
	counter1+=1
	if counter1 < MINRANGE: continue
	if counter1 >= MAXRANGE: break
	if counter1%100==0: sys.stderr.write(str(counter1)+" recipes printed...")
	pairs = []
	for ingr in ingrList1:
		pairs.extend(ingredientHash[ingr])
	pairs = list(set(pairs))
	for rid2 in pairs:
		if rid1==rid2: continue
		print rid1,":",",".join(recipesHash[rid1]),";",rid2,":",",".join(recipesHash[rid2])


#			jaccardHash["rid1,rid2"] = sp.dot(sparseMat[ind1,:].T, sparseMat[ind2,:])

