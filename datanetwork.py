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

def highest_centrality(cent_dict, n=1):
     """Returns a tuple (node,value) with the node
 with largest value from Networkx centrality dictionary."""
     # Create ordered tuple of centrality data
     cent_items=[(b,a) for (a,b) in cent_dict.iteritems()]
     # Sort in descending order
     cent_items.sort()
     cent_items.reverse()
     return tuple(reversed(cent_items[0:n]))



if __name__ == "__main__":
	baseIngredients = ['eggs','all-purpose flour','sugar','salt','baking soda','vanilla extract','baking powder']
	pp = pprint.PrettyPrinter(indent=4)
	db = sql.connect("localhost",'testuser','testpass',"test" )
	cursor = db.cursor()
	cursor.execute("""SELECT * FROM units""")
	unitTuple = cursor.fetchall()
	unitHash = dict(unitTuple)

	cursor.execute("""SELECT id, ingredient FROM recipes""")
	ingredientTuples = cursor.fetchall()

	G = nx.Graph()
	#add all recipes into graph as nodes
	recipeNodes = list(set([ingrTup[0] for ingrTup in ingredientTuples]))
	ingredientNodes = list(set([ingrTup[1] for ingrTup in ingredientTuples]))
	G.add_nodes_from(recipeNodes, type='recipes')
	G.add_nodes_from(ingredientNodes, type='ingredient')
	G.add_edges_from(ingredientTuples)

	sortedIngrNodes = sorted(ingredientNodes, key= lambda ingr:G.degree(ingr), reverse=True)

	selectedIngredients = sortedIngrNodes[1:10]

	candidateRecipes = set()
	for ingr in selectedIngredients:
		candidateRecipes = set(G.neighbors(ingr)) | candidateRecipes 
	candidateRecipes = list(candidateRecipes)

	Grecipes = nx.Graph()

	print "Adding ", len(candidateRecipes), " nodes..."
	candidateIngredients = set()
	jaccardList=[]
	#for each recipe node that we need to add to the graph
	for rn in candidateRecipes:
		#collect all previous nodes
		prevRN = Grecipes.nodes()
		#add new node to graph
		Grecipes.add_node(rn)

		candidateIngredients = set(G.neighbors(rn)) | candidateIngredients
		#look through each node already in graph and see if we should add an edge
		for prn in prevRN:
			#find jaccard index between nodes
			jaccard = Jaccard(G.neighbors(rn), G.neighbors(prn))
#			jaccardList.append(jaccard)
			#if they have more than one member in common
			if jaccard>0.5:
				Grecipes.add_weighted_edges_from([(rn, prn, jaccard)])

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
