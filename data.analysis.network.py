#!/Users/apple/Desktop/Work/Scripts/Insight/venv/bin/python

#import pymongo #==2.4.2
import datashopper, datamaid
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
import networkx as nx
#import matplotlib as mpl


try:
    import sklearn as ml
except ImportError:
    import scikits.learn as ml

def print_timing(func):
    def wrapper(*arg):
        t1 = time.time()
        res = func(*arg)
        t2 = time.time()
        print '%s took %0.3f ms' % (func.func_name, (t2-t1)*1000.0)
        return res
    return wrapper

def Jaccard(list1, list2):
	intersection = list(set(list1) & set(list2))
	union = list(set(list1) | set(list2))
	return float(len(intersection))/float(len(union))

def loadRecipeGraph(recipenodes):
	#create recipe graph
	Grecipes = nx.Graph()

	print "Adding ", len(recipenodes), " nodes..."
	Grecipes.add_nodes_from(recipenodes)

	print "Retrieving jaccard distances from database..."
	cursor = db.cursor()
	cursor.execute("SELECT * FROM recipejaccard WHERE jaccard>0.5 AND id1 IN (\'" + "\',\'".join(recipenodes) + "\') AND id2 IN (\'" + "\',\'".join(recipenodes) + "\')")
	jaccardTup = cursor.fetchall()

	print "Adding jaccard distances to graph..."
	if jaccardTup:
		Grecipes.add_weighted_edges_from(jaccardTup)

	counter = 0;
	#for each recipe node that we need to add to the graph
	edges = list(set([ (rn, prn) for rn in candidateRecipes for ingrnode in G.neighbors(rn) for prn in G.neighbors(ingrnode)]))
	print "Adding ", len(edges), " edges..."
	for rn, prn in edges:
		counter+=1
		if counter%10000==0: print counter, " edges added."
		#look through each node already in graph and see if we should add an edge
		#skip if same node
		if rn == prn: continue
		#skip if edge already assigned
		if ((rn, prn) in Grecipes.edges(rn)) or ((prn, rn) in Grecipes.edges(rn)): continue
		#find jaccard index between nodes
		jaccard = Jaccard(G.neighbors(rn), G.neighbors(prn))
		cursor.execute("INSERT IGNORE INTO recipejaccard(id1, id2, jaccard) VALUES (\'"+rn+"\',\'"+prn+"\',"+str(jaccard)+")")
		#if they have more than one member in common
		if jaccard>0.5:
			Grecipes.add_weighted_edges_from([(rn, prn, jaccard)])
	return Grecipes


if __name__ == "__main__":
	baseIngredients = ['eggs','all-purpose flour','sugar','salt','baking soda','vanilla extract','baking powder']
	pp = pprint.PrettyPrinter(indent=4)
	db = sql.connect("localhost",'testuser','testpass',"test" )
	cursor = db.cursor()
	cursor.execute("""SELECT * FROM units""")
	print "unit hash created"
	unitTuple = cursor.fetchall()
	unitHash = dict(unitTuple)
	cursor.execute("""SELECT ingredient, normingredient FROM ingredients""")
	ingrTuple = cursor.fetchall()
	ingrHash = dict(ingrTuple)

	print "ingredient hash created"

#restrict this for now; later put it up on hadoop
	cursor.execute("""SELECT id, ingredient FROM recipeingredients WHERE id REGEXP \'.*banana.*bread.*\'""")
	ingredientTuples = cursor.fetchall()

	#create recipe/ingredient graph
	G = nx.Graph()
	#add all recipes into graph as nodes
	recipeNodes = list(set([ingrTup[0] for ingrTup in ingredientTuples]))
	ingredientNodes = [ingrHash[ingr] for recipeid, ingr in ingredientTuples]
	ingredientNodes = list(set(ingredientNodes))
	G.add_nodes_from(recipeNodes, type='recipes')
	G.add_nodes_from(ingredientNodes, type='ingredient')
	G.add_edges_from([(ingrTup[0], ingrHash[ingrTup[1]]) for ingrTup in ingredientTuples])
	print "recipe/ingredient graph created"
	
	#sort ingredient by degree
	sortedIngrNodes = sorted(ingredientNodes, key= lambda ingr:G.degree(ingr), reverse=True)
	degrees = [G.degree(rn) for rn in recipeNodes]
	selectedIngredients = sortedIngrNodes[1:int(np.median(degrees))]

	#find candidate recipes
	candidateRecipes = set()
	for ingr in selectedIngredients:
		candidateRecipes = set(G.neighbors(ingr)) | candidateRecipes 
	candidateRecipes = list(candidateRecipes)

	Grecipes = loadRecipeGraph(candidateRecipes)
	db.commit()
	db.close()
