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
import os
import copy
import numpy as np
import scipy as sp
import pandas as pd
import nltk
from nltk.collocations import *
import pickle
import networkx as nx
#import matplotlib as mpl


try:
    import sklearn as ml
except ImportError:
    import scikits.learn as ml

def retrieveSearchRecords(searchResultFile):
	f = open(searchResultFile, 'r')
	results = f.read().split("\n")
	return results

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

def loadRecipeGraph(recipenodes, defaultGFile, loadFromFile = True):
	#create recipe graph
	if loadFromFile and os.path.exists(defaultGFile):
		Grecipes = pickle.load(open(defaultGFile))
		return Grecipes
	else:
		Grecipes = nx.Graph()
		print "Adding ", len(recipenodes), " nodes..."
		Grecipes.add_nodes_from(recipenodes)
		print "Retrieving jaccard scores from database..."	
		cursor = db.cursor()
		cursor.execute("SELECT * FROM recipejaccard WHERE jaccard>0.5 AND id1 IN (\'" + "\',\'".join(recipenodes) + "\') AND id2 IN (\'" + "\',\'".join(recipenodes) + "\')")
		jaccardTup = cursor.fetchall()
		print "Add jaccard scores to graph (", len(jaccardTup)," edges in total)..."
		if jaccardTup:
			Grecipes.add_weighted_edges_from(jaccardTup)
			pickle.dump(Grecipes, open(defaultGFile, 'w'))
		return Grecipes

def getClusterLabel(names):
	namesl = ".".join(names)
	#	namesl = re.sub(r'[-_]*',' ',namesl)
	tokens = nltk.WordPunctTokenizer().tokenize(namesl)
	bigram_measures = nltk.collocations.BigramAssocMeasures()
	word_fd = nltk.FreqDist(tokens)
	bigram_fd = nltk.FreqDist(nltk.bigrams(tokens))
	finder = BigramCollocationFinder(word_fd, bigram_fd)
	finder.apply_word_filter(lambda w: w in ('.', ',', '!', '\'','(', ')'))
	bigram_scored = finder.score_ngrams(bigram_measures.raw_freq)
	#	print sorted(finder.nbest(bigram_measures.raw_freq,2),reverse=True)

	trigram_measures = nltk.collocations.TrigramAssocMeasures()
	finder = TrigramCollocationFinder.from_words(tokens)
	finder.apply_word_filter(lambda w: w in ('.', ',', '!', '\'','(', ')'))
	trigram_scored = finder.score_ngrams(trigram_measures.raw_freq)

	print "Trigram: "
	print trigram_scored[0]
	print "Bigram: "
	print bigram_scored[0]
	if trigram_scored[0][1]/bigram_scored[0][1] > 0.85:
		#if the trigram score is significant compared to the bigram score
		return " ".join(trigram_scored[0][0])
	else:
		return " ".join(bigram_scored[0][0])
#	print sorted(finder.nbest(trigram_measures.raw_freq, 2)

def vectorizeIngredientsFromGraph(G, recipenodes, ingredientnodes):
	ingrHash = defaultdict(tuple)
	for rn in recipenodes:
		ingrHash[rn] = [0]*len(ingredientnodes)
		recipeIngr = G.neighbors(rn)
		for ing in recipeIngr:
			ingrHash[rn][ingredientnodes.index(ing)] += 1
	frame = pd.DataFrame(ingrHash, index = ingredientnodes,columns = recipenodes, dtype=float).T.astype(float)
	return frame


def vectorizeIngredients():
	searchResultFile = 'searchrecordids.txt'
	records = retrieveSearchRecords(searchResultFile)
	#restrict this for now; later put it up on hadoop
	cursor.execute("SELECT records.id, ingredient, name FROM recipeingredients, records WHERE recipeingredients.id=records.id AND records.id IN (\'"+"\',\'".join(records)+"\')")
	ingredientTuples = cursor.fetchall()

#	return pd.DataFrame(zip(*ingredientTuples),index=['id','ingredient', 'name']).T
	ingrHash = defaultdict(tuple)
	ingredients = list(set([ingTup[1] for ingTup in ingredientTuples]))
#	for rid, ingredient, name in ingredientTuples:

def filterRecipeGraph(Gref, cutoff):
	Gnew = Gref.copy()
	for id1, id2, edge in Gref.edges(data=True):
		if edge['weight']<cutoff:
			Gnew.remove_edge(id1,id2)
	return Gnew

def clusterVariationsTestDummy():
	jaccards = [edge['weight'] for id1, id2, edge in Grecipes.edges(data=True)]
	percentile = 97
	jcutoff = np.percentile(jaccards, percentile)
	print "The " + str(percentile) + "th percentile jaccard cutoff is ", str(jcutoff), ". Setting cutoff there."
	Gfilter = filterRecipeGraph(Grecipes, jcutoff)
	recipe_components = nx.connected_component_subgraphs(Gfilter)
	for i,recipe_mc in enumerate(recipe_components):
		if i>5: break
		clusternodes = recipe_mc.nodes()
	#	print recipe_mc.nodes()
#		if (float(len(clusternodes))/float(len(recipeNodes))) >0.01:
		print "cluster "+str(i) + ": " + str(len(clusternodes)) + " nodes"
		label = getClusterLabel([recordsHash[c] for c in clusternodes])
		print "LABEL: ", label

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

	searchResultFile = 'searchrecordids.txt'
	records = retrieveSearchRecords(searchResultFile)
#restrict this for now; later put it up on hadoop
	cursor.execute("SELECT records.id, ingredient, name FROM recipeingredients, records WHERE recipeingredients.id=records.id AND records.id IN (\'"+"\',\'".join(records)+"\')")
	ingredientTuples = cursor.fetchall()
	recordsHash = dict([(rid, name) for rid, ingr, name in ingredientTuples])

	#create recipe/ingredient graph
	G = nx.Graph()
	#add all recipes into graph as nodes
	recipeNodes = list(set([ingrTup[0] for ingrTup in ingredientTuples]))
	ingredientNodes = [ingrHash[ingr] for recipeid, ingr, name in ingredientTuples]
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
	defaultGFile = 'Grecipesjaccardgraph.txt'


	Grecipes = loadRecipeGraph(recipeNodes, defaultGFile, loadFromFile = True)
	
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
	for i,recipe_mc in enumerate(recipe_components):
		if i>5: break
		clusternodes = recipe_mc.nodes()
	#	print recipe_mc.nodes()
#		if (float(len(clusternodes))/float(len(recipeNodes))) >0.01:
		print "cluster "+str(i) + ": " + str(len(clusternodes)) + " nodes"
		label = getClusterLabel([recordsHash[c] for c in clusternodes])
		print "LABEL: ", label
		#	bet_cen = nx.betweenness_centrality(recipe_mc)
		#	clo_cen = nx.closeness_centrality(recipe_mc)
		#	eig_cen = nx.eigenvector_centrality(recipe_mc)
#			rec = [n[1] for n in highest_centrality(eig_cen,10)]

#			getClusterLabel(rec)

#	recipeDF = vectorizeIngredientsFromGraph(G, recipe_components[0].nodes(), ingredientNodes)
#	recipeDF.ix[rec]

#	recipeDF.to_csv('recipeDF.csv')

#find a way to categorize categories into groups
#create ingredient-ingredient substitutions
