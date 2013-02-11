#!/Users/apple/Desktop/Work/Scripts/Insight/venv/bin/python

#import pymongo #==2.4.2
import json
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


def mysqlify(x):
	return x.replace("\'","\\\'") 
#	a = a.replace('/', '\/')
#	a = a.replace("(", "\(")
#	a = a.replace(")", "\)")
#	return a

def Jaccard(list1, list2):
	intersection = list(set(list1) & set(list2))
	union = list(set(list1) | set(list2))
	return float(len(intersection))/float(len(union))

def highest_centrality(cent_dict, n=1):
     #Returns a tuple (node,value) with the node with largest value from Networkx centrality dictionary.
     # Create ordered tuple of centrality data
     cent_items=[(b,a) for (a,b) in cent_dict.iteritems()]
     # Sort in descending order
     cent_items.sort()
     cent_items.reverse()
     return tuple(reversed(cent_items[0:n]))

def calculateRecipeJaccardIndices(recipeids):
	db = sql.connect("localhost",'testuser','testpass',"test" )
	cursor = db.cursor()
	recipeToIngredientHash = defaultdict()

	db = sql.connect("localhost",'testuser','testpass',"test" )
	cursor = db.cursor()
	cursor.execute("SELECT id, normingredient FROM normrecipeingredients")
	ingredientTuples = cursor.fetchall()

	db.commit()
	db.close()
	
	for recipeid, recipeingr in ingredientTuples:
		if recipeid not in recipeids: continue
		if recipeid in recipeToIngredientHash.keys():
			try:
				recipeToIngredientHash[recipeid].append(recipeingr)
			except:
				print "data.analysis.jaccard/main: ",recipeid
		else:
			recipeToIngredientHash[recipeid] = [recipeingr]



	counter = 0
	print "loading jaccard indices for ", len(recipeToIngredientHash.keys()), " recipes..."

	#load all existing jaccard indices from database
	cmd = "SELECT id1,id2 FROM recipejaccard WHERE id1 IN (\'" + "\',\'".join(recipeToIngredientHash.keys()) + "\') AND id2 IN (\'" + "\',\'".join(recipeToIngredientHash.keys()) + "\')"
	cursor.execute(cmd)
	jaccardTuples = cursor.fetchall()
#	jaccardHash = defaultdict(dict)
#	for id1, id2, jaccard in jaccardTuples:
#		jaccardHash[id1][id2]=jaccard

	print "calculating jaccard indices..."
	for recipe1 in recipeToIngredientHash.keys():
		counter+=1
		if counter%10==0:
			print counter, " 1st recipes processed."
		counter2 = 0
		for recipe2 in recipeToIngredientHash.keys():
			counter2+=1
			if counter2%500==0:
				print counter2, " 2nd recipes processed."
			if recipe1==recipe2: continue #skip if comparing to self
			if (recipe1, recipe2) in jaccardTuples: continue
			if (recipe2, recipe1) in jaccardTuples: continue
#			if recipe1 in recipeToIngredientHash and recipe2 in recipeToIngredientHash[recipe1]: continue #skip if already calculated in database
#			if recipe2 in recipeToIngredientHash and recipe1 in recipeToIngredientHash[recipe2]: continue #skip if already calculated in database

			jaccard = Jaccard(recipeToIngredientHash[recipe1], recipeToIngredientHash[recipe2])
			cmd = "INSERT IGNORE INTO recipejaccard(id1, id2, jaccard) VALUES(\'"+mysqlify(recipe1)+"\',\'"+mysqlify(recipe2)+"\',"+str(jaccard)+")"
			cursor.execute(cmd)
		db.commit()
	db.close()

def calculateIngredientJaccardIndices():
	db = sql.connect("localhost",'testuser','testpass',"test" )
	cursor = db.cursor()
	counter = 0
	print "loading ingredients..."

	cmd = "SELECT id, normingredient FROM normrecipeingredients"
	#load all existing jaccard indices from database
	cursor.execute(cmd)
	recipeTuples = cursor.fetchall()
	ingrHash = defaultdict(list)
#	jaccardHash = defaultdict(dict)
#	for id1, id2, jaccard in jaccardTuples:
#		jaccardHash[id1][id2]=jaccard
	for rid, ingr in recipeTuples:
		ingrHash[ingr].append(rid)

	cmd = "SELECT ingr1,ingr2 FROM ingredientjaccard"
	cursor.execute(cmd)
	jaccardTuples = cursor.fetchall()
	db.close()

	db = sql.connect("localhost",'testuser','testpass',"test" )
	cursor = db.cursor()

	print "calculating jaccard indices for ingredients..."
	for ingr1 in ingrHash.keys():
		counter+=1
		if counter%100==0:
			print counter, " 1st ingredients processed."
		for ingr2 in ingrHash.keys():
			if ingr1==ingr2: continue #skip if comparing to self
			if (ingr1, ingr2) in jaccardTuples: continue
			if (ingr2, ingr1) in jaccardTuples: continue
			jaccard = Jaccard(ingrHash[ingr1], ingrHash[ingr2])
			cmd = "INSERT IGNORE INTO ingredientjaccard(ingr1,ingr2, jaccard) VALUES(\'"+mysqlify(ingr1)+"\',\'"+mysqlify(ingr2)+"\',"+str(jaccard)+")"
			cursor.execute(cmd)
		db.commit() 	
	db.close()
	pickle.dump(ingrHash, open("ingredientjaccard.pickle", 'w'))


if __name__ == "__main__":

	db = sql.connect("localhost",'testuser','testpass',"test" )
	cursor = db.cursor()

	searchResultFile = 'searchrecordids.txt'
	f = open(searchResultFile, 'r')
	recipenodes = f.read().split("\n")
	print "searchedrecords loaded"
#	calculateRecipeJaccardIndices(recipenodes)
	calculateIngredientJaccardIndices()
