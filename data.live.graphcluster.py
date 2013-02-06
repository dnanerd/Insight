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

def loadRecipeGraph(recipenodes):
	#create recipe graph
	Grecipes = nx.Graph()

	print "Adding ", len(recipenodes), " nodes..."
	Grecipes.add_nodes_from(recipenodes)

	cursor = db.cursor()
	cursor.execute("SELECT * FROM recipejaccard WHERE jaccard>0.5 AND id1 IN (\'" + "\',\'".join(recipenodes) + "\') AND id2 IN (\'" + "\',\'".join(recipenodes) + "\')")
	jaccardTup = cursor.fetchall()
	if jaccardTup:
		Grecipes.add_weighted_edges_from(jaccardTup)
	return Grecipes


if __name__ == "__main__":
	baseIngredients = ['eggs','all-purpose flour','sugar','salt','baking soda','vanilla extract','baking powder']
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
	mediandeg = [G.degree(rn) for rn in recipeNodes]
	selectedIngredients = sortedIngrNodes[1:int(np.median(degrees))]

	#find candidate recipes
	candidateRecipes = set()
	for ingr in selectedIngredients:
		candidateRecipes = set(G.neighbors(ingr)) | candidateRecipes 
	candidateRecipes = list(candidateRecipes)

	Grecipes = loadRecipeGraph(candidateRecipes)
	
#	candidateIngredients = list(candidateIngredients)

	#results = mpl.PCA(recipeDF)
	#recipeEdges = [ [rn1, rn2, Jaccard(G.neighbors(rn1), G.neighbors(rn2))] for rn1 in recipeNodes for rn2 in recipeNodes]


	#recipeEdges = [ [rn1, rn2, Jaccard(G.neighbors(rn1), G.neighbors(rn2))] for rn1 in recipeNodes for rn2 in recipeNodes]
	#Grecipes.add_weighted_edges_from(recipeEdges)

	#Gingredients = nx.Graph()
	#Gingredients.add_nodes_from(ingredientNodes)

	#find clusters
	#for each pair of recipes, assign Jaccard index as weight of edge

#	clust_coefficients = nx.clustering(Grecipes)
	recipe_components = nx.connected_component_subgraphs(Grecipes)
	recipe_mc = recipe_components[0]
	bet_cen = nx.betweenness_centrality(recipe_mc)
	clo_cen = nx.closeness_centrality(recipe_mc)
	eig_cen = nx.eigenvector_centrality(recipe_mc)
	rec = [n[1] for n in highest_centrality(eig_cen,10)]

#	recipeDF = vectorizeRecipes(selectedIngredients, candidateRecipes)
#	recipeDF.ix[rec]

#	recipeDF.to_csv('recipeDF.csv')

#find a way to categorize categories into groups
#create ingredient-ingredient substitutions
