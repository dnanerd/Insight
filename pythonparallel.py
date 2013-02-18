#!/Users/apple/Desktop/Work/Scripts/Insight/venv/bin/python
import json
import sys
import re
from collections import *
import MySQLdb as sql
import re
import copy
from multiprocessing import Pool

import argparse
#===========================
# Arguments
#===========================
MININD = sys.argv[1]
MAXIND = sys.argv[2]
sys.stderr.write("calculating "+MININD + " to "+MAXIND+"...")
MININD = int(MININD)
MAXIND = int(MAXIND)

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

db.commit()
db.close()



def Map(line):
	(recipeLine1, recipeLine2) = line.split(";")
	(rid1, ingredientLine1) = recipeLine1.split(":")
	(rid2, ingredientLine2) = recipeLine2.split(":")
	ingr1 = ingredientLine1.split(",")
	ingr2 = ingredientLine2.split(",")
	intersection = list(set(ingredientLine1) & set(ingredientLine2))
	if (intersection):
		unionSize = len(ingredientLine1)+len(ingredientLine2)-2*len(intersection)
		return rid1+","+rid2, float(len(intersection))/float(unionSize)

def pairs(recipes):
	retval = []
	sys.stderr.write("Now calculating Jaccard distances")
	counter1 = 0
	for rid1 in recipes:
		counter1+=1
		if counter1%100==0: sys.stderr.write(str(counter1)+" recipes printed...")
		pairs = []
		ingrList1 = recipesHash[rid1]
		for ingr in ingrList1:
			pairs.extend(ingredientHash[ingr])
		pairs = list(set(pairs))
		for rid2 in pairs:
			if rid1==rid2: continue
			ingredientLine1 = recipesHash[rid1]
			ingredientLine2 = recipesHash[rid2]
			intersection = list(set(ingredientLine1) & set(ingredientLine2))
			union = list(set(ingredientLine1) | set(ingredientLine2))
			if (intersection):
				print rid1,rid2,float(len(intersection))/float(len(union))

def chunks(l, n):
  for i in xrange(0, len(l), n):
    yield l[i:i+n]



p = Pool(processes = 8)
recipes = recipesHash.keys()[MININD:MAXIND]
partitioned_recipes = list(chunks(recipes, len(recipes) / 8))

print p.map(pairs,partitioned_recipes)
