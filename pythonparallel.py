#!/Users/apple/Desktop/Work/Scripts/Insight/venv/bin/python
import json
import sys
import re
from collections import *
import MySQLdb as sql
import re
import copy
from multiprocessing import Pool
import pickle
import argparse
#===========================
# Arguments
#===========================



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
	recipesHash = pickle.load(open("recipeToIngredient.pickle"))
	ingredientHash = pickle.load(open("ingredientToRecipeHash.pickle"))

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
				jaccard = float(len(intersection))/float(len(union))
				if jaccard>=0.3:
					retval.append(rid1+","+rid2+","+str(jaccard))
	return "\n".join(retval)

def chunks(l, n):
  for i in xrange(0, len(l), n):
    yield l[i:i+n]


def runParallelJaccard(recipes):
	p = Pool(processes = 8)
	partitioned_recipes = list(chunks(recipes, len(recipes) / 8))

	retvals = p.map(pairs,partitioned_recipes)

	print "\n".join(retvals)



def runFromFile(filename):
	f = open(filename)
	newids = f.read().split("\n")
	MININD = sys.argv[1]
	MAXIND = sys.argv[2]
	sys.stderr.write("calculating "+MININD + " to "+MAXIND+"...")
	MININD = int(MININD)
	MAXIND = int(MAXIND)

	runParallelJaccard(newids[MININD: MAXIND])


def runFromDatabase():
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
	pickle.dump(recipesHash, open("recipeToIngredient.pickle", 'w'))
	pickle.dump(ingredientHash, open("ingredientToRecipeHash.pickle", 'w'))

	db.commit()
	db.close()

	recipes = recipesHash.keys()[MININD:MAXIND]

	runParallelJaccard(recipes)

if __name__ == "__main__":

	runFromFile("muffinrids.txt")

