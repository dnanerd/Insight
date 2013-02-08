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
import random
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

def getIngredientFrequencies(ids):
	db = sql.connect("localhost",'testuser','testpass',"test" )
	cursor=db.cursor()

	cursor.execute("SELECT id, ingredient FROM recipeingredients WHERE id IN (\'"+"\',\'".join(ids)+"\')")
	recipeTuples = cursor.fetchall()
	ingredients = [ ingr for rid, ingr in recipeTuples]
	fd = list(nltk.FreqDist(ingredients).items())
	retval = [(rid, float(int(100*float(freq)/float(len(ids))))/float(100)) for (rid, freq) in fd]

	db.close()
	return retval


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
			ingrCounts = getIngredientFrequencies(recipes)[0:5]
			retval.append({'label': "box"+str(counter), 'count': len(recipes), 'toprecipeimg': toprecipeimg, 'ingrFreq': ingrCounts, 'links': links})
	return retval
"""
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
"""

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

def getRecipeIngredientGraph(searchResultFile, ingrHash):
	db = sql.connect("localhost",'testuser','testpass',"test" )
	cursor=db.cursor()
	recipeRecords = retrieveSearchRecords(searchResultFile)
	cursor.execute("SELECT records.id, ingredient, name FROM recipeingredients, records WHERE recipeingredients.id=records.id AND records.id IN (\'"+"\',\'".join(recipeRecords)+"\')")
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
	db.commit()
	db.close()
	return (G, ingredientNodes, recipeNodes)

def getClusters(searchResultFile, query):
	db = sql.connect("localhost",'testuser','testpass',"test" )
	cursor=db.cursor()
	unitHash = pickle.load(open("unitNormHash.pickle"))
	ingrHash = pickle.load(open("ingrNormHash.pickle"))

	records = retrieveSearchRecords(searchResultFile)
#restrict this for now; later put it up on hadoop
	
	defaultGFile = query.split()[0]+'Grecipesjaccardgraph.txt'
#	(G, ingredientNodes, recipeNodes) = getRecipeIngredientGraph(searchResultFile, ingrHash)
#	sortedIngrNodes = sorted(ingredientNodes, key= lambda ingr:G.degree(ingr), reverse=True)
#	degrees = [G.degree(rn) for rn in recipeNodes]
#	mediandegree = np.median(degrees)
#	medianofmedian = np.percentile(mediandegree, 0.5)
#	essentialIngredients = [ingr for ingr in sortedIngrNodes if G.degree(ingr)>=medianofmedian]
#	print "ESSENTIAL INGREDIENTS more than ", medianofmedian," degrees"
#	print essentialIngredients
#	essentialIngredients = [ingr for ingr in sortedIngrNodes if G.degree(ingr)<medianofmedian]
#	print "ESSENTIAL INGREDIENTS less than ", medianofmedian," degrees"
#	print essentialIngredients
	Grecipes = loadRecipeGraph(records, defaultGFile, True, query.split()[0])

	recipe_components = nx.connected_component_subgraphs(Grecipes)
	db.close()
	return recipe_components

if __name__ == "__main__":
	searchResultFile = 'searchrecordids.txt'
	query = 'banana'
	components = getClusters(searchResultFile, query)
	cutoff = min(len(components), 5)
	search1jsonFile, labels = outputScreen1JSON(components, cutoff)
	search2jsonObject = [outputScreen2JSON(subCluster(component), 6) for component in components[0:5]]

