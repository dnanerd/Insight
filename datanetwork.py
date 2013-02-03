#!/Users/apple/Desktop/Work/Scripts/Insight/venv/bin/python

#import pymongo #==2.4.2
#import datashopper, datamaid

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
import matplotlib as mpl


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

def addRecipeNode(Gref, recipeid):
	if Gref.has_node(recipeid):
		return False
	else:
		return Gref.add_node(recipeid, type="recipe")
#end addRecipeNode

def addIngredientNode(Gref, ingredient):
	if Gref.has_node(ingredient):
		return False
	else:
		return Gref.add_node(ingredient, type='ingredient')
#end addIngredientNode

def addEdge(Gref, recipeid, ingredient, weight=0):
	if weight:
		if Gref.has_edge(recipeid, ingredient):
			return False
		else:
			return Gref.add_edge(recipeid, ingredient)
	else:
		if Gref.has_edge(recipeid, ingredient):
			return False
		else:
			return Gref.add_weighted_edges_from([(recipeid, ingredient, weight)])

def Jaccard(list1, list2):
	intersection = list(set(list1) & set(list2))
	union = list(set(list1) | set(list2))
	return float(len(intersection))/float(len(union))

baseIngredients = ['eggs','all-purpose flour','sugar','salt','baking soda','vanilla extract','baking powder']
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


#def createNetwork():
cursor = db.cursor()
cursor.execute("""SELECT id, ingredient FROM ingredients""")
ingredientTuples = cursor.fetchall()

G = nx.Graph()
#add all recipes into graph as nodes
recipeNodes = list(set([ingrTup[0] for ingrTup in ingredientTuples]))
ingredientNodes = list(set([ingrTup[1] for ingrTup in ingredientTuples]))
G.add_nodes_from(recipeNodes, type='recipes')
G.add_nodes_from(ingredientNodes, type='ingredient')
G.add_edges_from(ingredientTuples)

sortedIngrNodes = sorted(ingredientNodes, key= lambda ingr:G.degree(ingr), reverse=True)

selectedIngredients = sortedIngrNodes[1:20]

candidateRecipes = set()
for ingr in selectedIngredients:
	candidateRecipes = set(G.neighbors(ingr)) | candidateRecipes 
candidateRecipes = list(candidateRecipes)

Grecipes = nx.Graph()

print "Adding ", len(candidateRecipes), " nodes..."
candidateIngredients = set()
for rn in candidateRecipes:
	prevRN = Grecipes.nodes()
	Grecipes.add_node(rn)
	candidateIngredients = set(G.neighbors(rn)) | candidateIngredients
	for prn in prevRN:
		jaccard = Jaccard(G.neighbors(rn), G.neighbors(prn))
		Grecipes.add_weighted_edges_from([(rn, prn, jaccard)])
candidateIngredients = list(candidateIngredients)

recipeDF = vectorizeRecipes(selectedIngredients, candidateRecipes)

results = mpl.PCA(recipeDF)
#recipeEdges = [ [rn1, rn2, Jaccard(G.neighbors(rn1), G.neighbors(rn2))] for rn1 in recipeNodes for rn2 in recipeNodes]


#recipeEdges = [ [rn1, rn2, Jaccard(G.neighbors(rn1), G.neighbors(rn2))] for rn1 in recipeNodes for rn2 in recipeNodes]
#Grecipes.add_weighted_edges_from(recipeEdges)

#Gingredients = nx.Graph()
#Gingredients.add_nodes_from(ingredientNodes)

#find clusters
#for each pair of recipes, assign Jaccard index as weight of edge



