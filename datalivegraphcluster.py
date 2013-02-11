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
#import community
import random
#import matplotlib as mpl
import dataliveloadgraph
import datalivesearch


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

def loadRecipeGraph(recipenodes, defaultGFile, loadFromFile, query):
	#create recipe graph
	if loadFromFile and os.path.exists(defaultGFile):
		print "loadRecipeGraph: recipe graph file exists. loading..."
		Grecipes = pickle.load(open(defaultGFile))
		print len(Grecipes.nodes()), " nodes in jaccard graph"
		return Grecipes
	else:
		Grecipes = nx.Graph()
		print "loadRecipeGraph: Adding ", len(recipenodes), " nodes..."
		Grecipes.add_nodes_from(recipenodes)
		print "loadRecipeGraph: Retrieving jaccard scores from database..."	
		db = sql.connect("localhost",'testuser','testpass',"test" )
		cursor = db.cursor()
		cursor.execute("SELECT * FROM recipejaccard WHERE jaccard>0.5") 
		jaccardAll = cursor.fetchall()
		jaccardTup = [(id1,id2,jac) for id1,id2,jac in jaccardAll if id1 in recipenodes and id2 in recipenodes]
		db.close()

		print "loadRecipeGraph: Add jaccard scores to graph (", len(jaccardTup)," edges in total)..."
		if jaccardTup:
			Grecipes.add_weighted_edges_from(jaccardTup)
			f = open(defaultGFile, 'w')
			pickle.dump(Grecipes, f)
			f.close()
		print len(Grecipes.nodes()), " nodes in jaccard graph"
		pickle.dump(Grecipes, open(defaultGFile, 'r'))
		return Grecipes

def loadIngredientGraph(defaultGFile, loadFromFile):

	if loadFromFile and os.path.exists(defaultGFile):
		print "loadIngredientGraph: ingredient graph file exists. loading..."
		Gingredients = pickle.load(open(defaultGFile))
		print len(Gingredients.nodes()), " nodes in jaccard graph"
		return Gingredients
	else:
		db = sql.connect("localhost",'testuser','testpass',"test" )
		cursor = db.cursor()
		cmd = "SELECT DISTINCT normingredient FROM normrecipeingredients"
		ingredientTup = cursor.execute(cmd)

		Gingredients = nx.Graph()
		print "loadIngredientGraph: Adding ", len(ingredientnodes), " nodes..."
		Gingredients.add_nodes_from(ingredientnodes)
		print "loadIngredientGraph: Retrieving jaccard scores from database..."	
		cursor.execute("SELECT * FROM ingredientjaccard") 
		jaccardTup = cursor.fetchall()
		db.close()

		print "loadIngredientGraph: Add jaccard scores to graph (", len(jaccardTup)," edges in total)..."
		if jaccardTup:
			Gingredients.add_weighted_edges_from(jaccardTup)
			f = open(defaultGFile, 'w')
			pickle.dump(Gingredients, f)
			f.close()
		print len(Gingredients.nodes()), " nodes in jaccard graph"
		pickle.dump(Gingredients, open(defaultGFile, 'r'))
		return Gingredients


def getClusterLabel(ids, recordsHash):
	names = [recordsHash[c] for c in ids if c in recordsHash.keys()]
	print len(names), " out of ", len(ids), " recipes found in name translation"
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
	cursor.execute("SELECT records.id, normingredient, name FROM normrecipeingredients, records WHERE recipeingredients.id=records.id AND records.id IN (\'"+"\',\'".join(records)+"\')")
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



def getTopRatedRecipe(recipes):
	db = sql.connect("localhost",'testuser','testpass',"test" )
	cursor=db.cursor()
	#select the top races recipes in this list
	defaultimgurl = "static/imgunavailable.png"
	cmd = "SELECT id, rating, imgurl FROM records WHERE id IN (\'"+"\',\'".join(recipes)+"\') AND rating >= (SELECT max(rating) AS rating FROM records WHERE id IN (\'"+"\',\'".join(recipes)+"\'))"
	cursor.execute(cmd) 
	toprecords = cursor.fetchall()
	allrecords = [(rid, imgurl) for rid, rating, imgurl in toprecords]
	imagerecords = [(rid, imgurl) for rid, rating, imgurl in toprecords if imgurl!='NULL']
	if len(imagerecords)>0:
		return random.choice(imagerecords)
	else:
		return (random.choice(allrecords)[0], defaultimgurl)

def getIngredientFrequencies(rids):
	db = sql.connect("localhost",'testuser','testpass',"test" )
	cursor=db.cursor()

	cursor.execute("SELECT id, normingredient FROM normrecipeingredients WHERE id IN (\'"+"\',\'".join(rids)+"\')")
	recipeTuples = cursor.fetchall()
	ingredients = [ ingr for rid, ingr in recipeTuples]
	fd = list(nltk.FreqDist(ingredients).items())
	retval = [(ingr, float(int(100*float(freq)/float(len(rids))))/float(100)) for (ingr, freq) in fd]

	db.close()
	return retval

def findEnrichedIngredients(listOfIngrCounts):

	print "baisc recipe list; array of enriched ingredients"

def subCluster(component):
	#do a simple jaccard filter for now; later move on to something more sophisticated
	Gfiltered = filterRecipeGraph(component, 0.7)
	recipe_components = nx.connected_component_subgraphs(Gfiltered)
	return recipe_components

def outputScreen2JSON(recipeClusterList, maxcutoff):
	cutoff = min(maxcutoff, len(recipeClusterList))
	retval = []
	counter=0
	for recipecluster in recipeClusterList[0:cutoff]:
		counter+=1
		if counter<=cutoff:
			recipes = recipecluster.nodes()
			db = sql.connect("localhost",'testuser','testpass',"test" )
			cursor=db.cursor()
			cursor.execute("SELECT id, name, sourceurl FROM records WHERE id IN (\'"+"\',\'".join(recipes)+"\')")
			links = cursor.fetchall()
			db.close()
			toprecipeimg = getTopRatedRecipe(recipes)[1]
			ingrCounts = getIngredientFrequencies(recipes)
			retval.append({'label': "box"+str(counter), 'count': len(recipes), 'toprecipeimg': toprecipeimg, 'ingrFreq': ingrCounts, 'links': links})
	baseIngredients = retval[0]

	return retval

def outputScreen1JSON(recipe_components, cutoff):
	screen1jsonFile = "static/outputScreen1JSON.txt"
	recordsHash = pickle.load(open("idToNameHash.pickle"))
	screen1_components = []
	counts = [ len(recipe_mc.nodes()) for recipe_mc in recipe_components[0:cutoff]]
	counts = counts[0:cutoff]
	labels = [getClusterLabel(recipe_mc.nodes(), recordsHash) for recipe_mc in recipe_components[0:cutoff]]
	labels = labels[0:cutoff]

	labels = []

	for i,recipe_mc in enumerate(recipe_components):
		if i<=cutoff:
			clusternodes = recipe_mc.nodes()
			label = getClusterLabel(clusternodes, recordsHash)
			while label in labels:
				label = label+"I"
			component = {'i':i, 'label':label, 'count':len(clusternodes),'nodes':clusternodes}
			screen1_components.append(component)
			labels.append(label)
	#write json object to file
	f = open(screen1jsonFile, 'w')
	f.write(json.dumps(screen1_components))
	f.close()
	print labels
	print counts

	return screen1jsonFile, zip(labels, counts)

def getClusters(searchGrecipes):
	recipe_components = nx.connected_component_subgraphs(searchGrecipes)
	return recipe_components

def getPartitions(searchGrecipes):
	partition = community.best_partition(searchGrecipes)
	return partition

if __name__ == "__main__":
	components = getClusters(searchGrecipes)

	cutoff = min(len(components), 5)
	search1jsonFile, labels = outputScreen1JSON(components, cutoff)
	search2jsonObject = [outputScreen2JSON(subCluster(component), 6) for component in components[0:5]]

