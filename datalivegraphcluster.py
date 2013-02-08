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

def loadRecipeGraph(recipenodes, defaultGFile, loadFromFile):
	db = sql.connect("localhost",'testuser','testpass',"test" )
	cursor = db.cursor()
	#create recipe graph
	if loadFromFile and os.path.exists(defaultGFile):
		Grecipes = pickle.load(open(defaultGFile))
		print len(Grecipes.nodes()), " nodes in jaccard graph"
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
		print len(Grecipes.nodes()), " nodes in jaccard graph"
		return Grecipes
		db.close()

def getClusterLabel(ids, recordsHash):
	names = [recordsHash[c] for c in ids]
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

	if bigram_scored and trigram_scored:
		if trigram_scored[0][1]/bigram_scored[0][1] > 0.85:
			#if the trigram score is significant compared to the bigram score
			return " ".join(trigram_scored[0][0])
		else:
			return " ".join(bigram_scored[0][0])
	elif bigram_scored:
		return " ".join(bigram_scored[0][0])
	elif trigram_scored:
		return " ".join(trigram_scored[0][0])
	else:
		return 'None'
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
	db = sql.connect("localhost",'testuser','testpass',"test" )
	cursor = db.cursor()
	searchResultFile = 'searchrecordids.txt'
	records = retrieveSearchRecords(searchResultFile)
	#restrict this for now; later put it up on hadoop
	cursor.execute("SELECT records.id, ingredient, name FROM recipeingredients, records WHERE recipeingredients.id=records.id AND records.id IN (\'"+"\',\'".join(records)+"\')")
	ingredientTuples = cursor.fetchall()

#	return pd.DataFrame(zip(*ingredientTuples),index=['id','ingredient', 'name']).T
	ingrHash = defaultdict(tuple)
	ingredients = list(set([ingTup[1] for ingTup in ingredientTuples]))
#	for rid, ingredient, name in ingredientTuples:
	db.close()

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


def outputScreen1JSON(recipe_components):
	screen1jsonFile = "static/outputScreen1JSON.txt"
	recordsHash = pickle.load(open("idToNameHash.pickle"))
	screen1_components = []
	cutoff = min(5, len(recipe_components))
	counts = [ len(recipe_mc.nodes()) for recipe_mc in recipe_components[0:cutoff]]
	counts = counts[0:cutoff]
	labels = [getClusterLabel(recipe_mc.nodes(), recordsHash) for recipe_mc in recipe_components[0:cutoff]]
	labels = labels[0:cutoff]
	for i,recipe_mc in enumerate(recipe_components):
		if i<=cutoff:
			clusternodes = recipe_mc.nodes()
			label = getClusterLabel(clusternodes, recordsHash)
			component = {'i':i, 'label':label, 'count':len(clusternodes),'nodes':clusternodes}
			screen1_components.append(component)
	#write json object to file
	f = open(screen1jsonFile, 'w')
	f.write(json.dumps(screen1_components))
	f.close()
	print labels
	print counts

	return screen1jsonFile, zip(labels, counts)

def getClusters(searchResultFile):
	db = sql.connect("localhost",'testuser','testpass',"test" )
	cursor=db.cursor()
	unitHash = pickle.load(open("unitNormHash.pickle"))
	ingrHash = pickle.load(open("ingrNormHash.pickle"))

	records = retrieveSearchRecords(searchResultFile)
#restrict this for now; later put it up on hadoop
	cursor.execute("SELECT records.id, ingredient, name FROM recipeingredients, records WHERE recipeingredients.id=records.id AND records.id IN (\'"+"\',\'".join(records)+"\')")
	ingredientTuples = cursor.fetchall()
	#create recipe/ingredient graph
	G = nx.Graph()
	#add all recipes into graph as nodes
	recipeNodes = list(set([ingrTup[0] for ingrTup in ingredientTuples]))
	print len(recipeNodes)
	ingredientNodes = [ingrHash[ingr] for recipeid, ingr, name in ingredientTuples]
	ingredientNodes = list(set(ingredientNodes))
	G.add_nodes_from(recipeNodes, type='recipes')
	G.add_nodes_from(ingredientNodes, type='ingredient')
	G.add_edges_from([(ingrTup[0], ingrHash[ingrTup[1]]) for ingrTup in ingredientTuples])
	print "recipe/ingredient graph created"
	
	defaultGFile = 'Grecipesjaccardgraph.txt'

	Grecipes = loadRecipeGraph(recipeNodes, defaultGFile, loadFromFile = True)

	recipe_components = nx.connected_component_subgraphs(Grecipes)
	db.close()
	return outputScreen1JSON(recipe_components)

if __name__ == "__main__":
	searchResultFile = 'searchrecordids.txt'
	getClusters(searchResultFile)