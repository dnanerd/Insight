#!/Users/apple/Desktop/Work/Scripts/Insight/venv/bin/python

#import pymongo #==2.4.2
import sys
import re
import unicodedata
from collections import *
import time
import MySQLdb as sql
import os
import copy
import numpy as np
import nltk
from nltk.collocations import *
import pickle
import networkx as nx
import random
#import matplotlib as mpl


try:
    import sklearn as ml
except ImportError:
    import scikits.learn as ml

def Jaccard(list1, list2):
	intersection = list(set(list1) & set(list2))
	union = list(set(list1) | set(list2))
	return float(len(intersection))/float(len(union))

def highest_centrality(cent_dict, n=1):
     """Returns a tuple (node,value) with the node
 with largest value from Networkx centrality dictionary."""
     # Create ordered tuple of centrality data
     cent_items=[(b,a) for (a,b) in cent_dict.iteritems()]
     # Sort in descending order
     cent_items.sort()
     cent_items.reverse()
     return tuple(reversed(cent_items[0:n]))

def createRecipeGraph(defaultGFile, loadFromFile):
	jlimit = 0.2
	#create recipe graph
	if loadFromFile and os.path.exists(defaultGFile):
		print "loadRecipeGraph: recipe graph file exists. loading..."
		Grecipes = pickle.load(open(defaultGFile))
		print len(Grecipes.nodes()), " nodes in jaccard graph"
		return Grecipes
	else:
		Grecipes = nx.Graph()
		print "loadRecipeGraph: Retrieving jaccard scores from database..."	
		db = sql.connect("localhost",'testuser','testpass',"test" )
		cursor = db.cursor()
		cursor.execute("SELECT id1, id2, jaccard FROM recipejaccard WHERE jaccard>"+str(jlimit)) 
		jaccardTup = cursor.fetchall()
		cursor.execute("SELECT DISTINCT id1 FROM recipejaccard WHERE jaccard>"+str(jlimit) )
		id1Tup = cursor.fetchall()
		recipenodes1 = set([id1[0] for id1 in id1Tup])

		cursor.execute("SELECT DISTINCT id2 FROM recipejaccard WHERE jaccard>"+str(jlimit) )
		id2Tup = cursor.fetchall()
		recipenodes2 = set([id2[0] for id2 in id2Tup])
		db.close()

		recipenodes = list(recipenodes1 | recipenodes2)

		print "loadRecipeGraph: Adding ", len(recipenodes), " nodes..."
		Grecipes.add_nodes_from(recipenodes)

		print "loadRecipeGraph: Add jaccard scores to graph (", len(jaccardTup)," edges in total)..."
		if jaccardTup:
			Grecipes.add_weighted_edges_from(jaccardTup)
			f = open(defaultGFile, 'w')
			pickle.dump(Grecipes, f)
			f.close()
		print len(Grecipes.nodes()), " nodes in jaccard graph"
		return Grecipes

def createIngredientGraph(G, defaultGFile, loadFromFile):

	if loadFromFile and os.path.exists(defaultGFile):
		print "loadIngredientGraph: ingredient graph file exists. loading..."
		Gingredients = pickle.load(open(defaultGFile))
		print len(Gingredients.nodes()), " nodes in jaccard graph"
		return Gingredients
	else:
		db = sql.connect("localhost",'testuser','testpass',"test" )
		cursor = db.cursor()
		cmd = "SELECT DISTINCT normingredient FROM normrecipeingredients"
		cursor.execute(cmd)
		ingredientTuples = cursor.fetchall()
		ingredientnodes = [ingrTup[0] for ingrTup in ingredientTuples]

		Gingredients = nx.MultiGraph()
		print "loadIngredientGraph: Adding ", len(ingredientnodes), " nodes..."
		Gingredients.add_nodes_from(ingredientnodes)

		for i, ingr1 in enumerate(ingredientnodes):
			for j, ingr2 in enumerate(ingredientnodes):
				if i>=j: continue
				recipesInCommon = list(set(G.neighbors(ingr1)) & set(G.neighbors(ingr2)))
				for recipe in recipesInCommon:
					Gingredients.add_edge(ingr1,ingr2, key=recipe)				
		f = open(defaultGFile, 'w')
		pickle.dump(Gingredients, f)
		f.close()
		print len(Gingredients.nodes()), " nodes in jaccard graph"
		return Gingredients


def getRecipeIngredientGraph(defaultGFile, loadFromFile):
	if loadFromFile and os.path.exists(defaultGFile):
		print "loadIngredientGraph: ingredient graph file exists. loading..."
		G = pickle.load(open(defaultGFile))
		return G
	else:
		db = sql.connect("localhost",'testuser','testpass',"test" )
		cursor=db.cursor()
		cursor.execute("SELECT id, normingredient FROM normrecipeingredients")
		ingredientTuples = cursor.fetchall()
		db.commit()
		db.close()

		#create recipe/ingredient graph
		G = nx.Graph()
		#add all recipes into graph as nodes
		recipeNodes = list(set([ ingrTup[0] for ingrTup in ingredientTuples ]))
		print "getRecipeIngredientGraph: adding ", len(recipeNodes), " recipes into graph..."
		ingredientNodes = [ingr for recipeid, ingr in ingredientTuples]
		ingredientNodes = list(set(ingredientNodes))
		G.add_nodes_from(recipeNodes, type='recipes')
		G.add_nodes_from(ingredientNodes, type='ingredient')
		G.add_edges_from([(ingrTup[0], ingrTup[1]) for ingrTup in ingredientTuples])
		print "recipe/ingredient graph created"

		f = open(defaultGFile, 'w')
		pickle.dump(G, f)
		f.close()
		return G

def loadApp():
	unitHash = pickle.load(open("unitNormHash.pickle"))
	recordsHash = pickle.load(open("idToNameHash.pickle"))
	recipesHash = pickle.load(open("idToIngredient.pickle"))

	defaultGFile = "Gjaccard.pickle"
	defaultGrecipesFile = "Grecipesjaccard.pickle"
	defaultGingredientsFile = "Gingredientsjaccard.pickle"

	print "Retrieving recipe-ingredient graph..."
	G = getRecipeIngredientGraph(defaultGFile, True)
#	print "Retrieving ingredient graph..."
	Gingredients = G
#	Gingredients = createIngredientGraph(G, defaultGingredientsFile, True)
	print "Retrieving recipe graph..."
	Grecipes = createRecipeGraph(defaultGrecipesFile, True)

	print "Done loading."
	return (unitHash, recordsHash, recipesHash, G, Grecipes, Gingredients)	


