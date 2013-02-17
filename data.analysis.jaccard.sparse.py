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
MAXRANGE = 5000

db = sql.connect("localhost",'testuser','testpass',"test" )
cursor = db.cursor()

cursor.execute("SELECT DISTINCT id FROM normrecipeingredients")
recipeTuples = cursor.fetchall()
recipeToIndex = dict([(rid[0], i) for i, rid in enumerate(recipeTuples)])

cursor.execute("SELECT id, normingredient FROM normrecipeingredients")
recipeTuples = cursor.fetchall()

recipesHash = defaultdict(list)
for rid, ingr in recipeTuples:
	recipesHash[rid].append(ingr)
pickle.dump(recipesHash, open("idToIngredient.pickle", 'w'))

db.commit()
db.close()


jaccardHash = defaultdict(float)
sys.stderr.write("Now calculating Jaccard distances")
counter1 = 0
for ind1, rid1 in enumerate(recipesHash.keys()):
	counter1+=1
	if counter1 < MINRANGE: break
	if counter1 >= MAXRANGE: break
	if counter1%100==0: sys.stderr.write(str(counter1)+" recipes printed...")
	for ind2, rid2 in enumerate(recipesHash.keys()):
		if ind1>=ind2: continue
		print rid1,":",",".join(recipesHash[rid1]),";",rid2,":",",".join(recipesHash[rid2])


#			jaccardHash["rid1,rid2"] = sp.dot(sparseMat[ind1,:].T, sparseMat[ind2,:])

