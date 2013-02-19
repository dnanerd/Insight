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
import community
import random
import math
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
		cursor.execute("SELECT * FROM recipejaccard WHERE jaccard>0.2") 
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
	namesl = " ENDLINE ".join(names)
	#	namesl = re.sub(r'[-_]*',' ',namesl)
	tokens = nltk.WordPunctTokenizer().tokenize(namesl)
	tokens = namesl.split()
	bigram_measures = nltk.collocations.BigramAssocMeasures()
	word_fd = nltk.FreqDist(tokens)
	bigram_fd = nltk.FreqDist(nltk.bigrams(tokens))
	finder = BigramCollocationFinder(word_fd, bigram_fd)
	finder.apply_word_filter(lambda w: w in ('.', ',', '!', '\'','(', ')', "ENDLINE"))
	bigram_scored = finder.score_ngrams(bigram_measures.raw_freq)
	#	print sorted(finder.nbest(bigram_measures.raw_freq,2),reverse=True)

	trigram_measures = nltk.collocations.TrigramAssocMeasures()
	finder = TrigramCollocationFinder.from_words(tokens)
	finder.apply_word_filter(lambda w: w in ('.', ',', '!', '\'','(', ')', "ENDLINE"))
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
	cmd = "SELECT id, rating, imgurl, imgurllg FROM records WHERE id IN (\'"+"\',\'".join(recipes)+"\') ORDER BY rating DESC"
	cursor.execute(cmd) 
	toprecords = cursor.fetchall()
	allrecords = [(rid, imgurl) for rid, rating, imgurl, imgurllg in toprecords]
	imagerecords = [(rid, imgurl) for rid, rating, imgurl, imgurllg in toprecords if imgurl!='NULL']
	largeimagerecords = [(rid, imgurllg) for rid, rating, imgurl, imgurllg in toprecords if imgurllg!='NULL']
	if len(largeimagerecords)>0:
		return random.choice(imagerecords)
	elif len(imagerecords)>0:
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

def findEnrichedIngredients(baseFrequency, sampleFrequency):
	baseDict = dict(baseFrequency)
	sampleDict = dict(sampleFrequency)
	smoothing = 0.05
	ingredients = list(set([ingr for ingr, freq in baseFrequency if freq>0]) | set([ingr for ingr, freq in sampleFrequency if freq>0]))
	ingrDiff = {}
	for ingr in ingredients:
		sampfreq = basefreq = smoothing
		if ingr in sampleDict: sampfreq+=sampleDict[ingr]
		if ingr in baseDict: basefreq+=baseDict[ingr]

		ingrDiff[ingr] = math.log((sampfreq+smoothing)/(basefreq+smoothing), 2)
	return sorted(ingrDiff.iteritems(), key=lambda tup: tup[1], reverse=True)

def mergeClusters(cluster1, cluster2, listOfClusters):
	print "merging clusters ", cluster1, " and ", cluster2
	print "CLUSTER 1"
	print ",".join(listOfClusters[cluster1])
	print "CLUSTER 2"
	print ",".join(listOfClusters[cluster2])

	listOfClusters[cluster1].extend(listOfClusters[cluster2])
	del listOfClusters[cluster2]
	return listOfClusters

def hierarchicalCluster(listOfClusters):
	listOfFrequencies = []
	for cl in listOfClusters:
		listOfFrequencies.append(getIngredientFrequencies(cl))
	for i, freq1 in enumerate(listOfFrequencies):
		for j, freq2 in enumerate(listOfFrequencies):
			if i>=j: continue
			logRatios = findEnrichedIngredients(freq1,freq2)
			enrichment = [(ingr, log) for ingr, log in logRatios if log>=2]
			depletion = [(ingr, log) for ingr, log in logRatios if log<=-2]
			if len(enrichment)==0 and len(depletion)==0:
				print "MERGE!"
				return mergeClusters(i,j,listOfClusters)
			elif (len(enrichment) + len(depletion))<3:
				print "Enrichment: ", len(enrichment)
				print "Depletion: ", len(depletion)
				print "MERGE!"
				return mergeClusters(i,j,listOfClusters)
	return False

def combineClusters(listOfClusters):
	print "Combine clusters..."
	cluster = hierarchicalCluster(listOfClusters)
	if (cluster):
		print "Clustered!"
		return combineClusters(cluster)
	else:
		print "STOP"
		return listOfClusters

def getClusters(searchGrecipes):
	recipe_components = nx.connected_component_subgraphs(searchGrecipes)
	return recipe_components

def getPartitions(searchGrecipes):
	partition = community.best_partition(searchGrecipes)
	partitionArray = defaultdict(list)
	for k, v in partition.iteritems():
		partitionArray[v].append(k)
	sortedPartitions = sorted(partitionArray.itervalues(), key=lambda partition: len(partition), reverse=True)
#	mergedPartitions = combineClusters(sortedPartitions)
#	print mergedPartitions[0]
	components = [nx.subgraph(searchGrecipes,partition) for partition in sortedPartitions]
	return components


def outputScreenJSON(recipeClusterList, maxcutoff, searchG):
	recordsHash = pickle.load(open("idToNameHash.pickle"))
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
			name = getClusterLabel(recipes, recordsHash)

			ingrCounts = getIngredientFrequencies(recipes)
			enrichment = []
			depletion = []
			displaytype = 'basic'

			if counter>1:
				logRatios = findEnrichedIngredients(retval[0]['ingrFreq'], ingrCounts)
				enrichment = [(ingr, log) for ingr, log in logRatios if log>=2]
				depletion = [(ingr, log) for ingr, log in logRatios if log<=-2]
				if len(enrichment)<=4 and len(depletion)<=4:
					displaytype = 'extension'
			retval.append({'label': "box"+str(counter), 'name': name, 'count': len(recipes), 'toprecipeimg': toprecipeimg, 'ingrFreq': ingrCounts, 'enrichment':enrichment, 'depletion': depletion, 'displaytype':displaytype, 'links': links})
	return retval


def findNameGroups(searchresults):
	#load pickle file for id-to-name hash
	recordsHash = pickle.load(open("idToNameHash.pickle"))
	names = [recordsHash[res] for res in searchresults if res in recordsHash]
	#mark the end of line explicitly so we can work with NLTK
	namesl = " ENDLINE ".join(names)

	#split names into tokens
	tokens = namesl.split()
	#use NLTK to find bigrams
	bigram_measures = nltk.collocations.BigramAssocMeasures()
	word_fd = nltk.FreqDist(tokens)
	bigram_fd = nltk.FreqDist(nltk.bigrams(tokens))
	finder = BigramCollocationFinder(word_fd, bigram_fd)
	#remove all words with specified characters
	finder.apply_word_filter(lambda w: w in ('.', ',', '!', '\'','(', ')', "ENDLINE"))
	bigram_scored = finder.score_ngrams(bigram_measures.raw_freq)
	bigram_names = [name for name, val in bigram_scored]

	#use NLTK to find trigrams
	trigram_measures = nltk.collocations.TrigramAssocMeasures()
	finder = TrigramCollocationFinder.from_words(tokens)
	#remove all words with specified charactes
	finder.apply_word_filter(lambda w: w in ('.', ',', '!', '\'','(', ')', "ENDLINE"))
	trigram_scored = finder.score_ngrams(trigram_measures.raw_freq)
	trigram_names = [name for name, val in trigram_scored]

	#merge tri-indices and bi-indices
	deleteBiIndices = []
	deleteTriIndices = []
	for ind, tri in enumerate(trigram_scored):
			if ind>30: continue
			#find bigrams associated with the trigram
			i1 = bigram_names.index(trigram_scored[ind][0][0:2])
			i2 = bigram_names.index(trigram_scored[ind][0][1:3])
			val1 = bigram_scored[i1][1]
			val2 = bigram_scored[i2][1]			
			if math.fabs(math.log(val1/val2))<2 and val1>tri[1] and val2 > tri[1]:
			#find expected value of trigram given independence assumption
	#			if float(tri[1])/float((val1*val2)) > 2:
				#trigram is overrepresented compared to expected from bigram
				deleteBiIndices.append(i1)
				deleteBiIndices.append(i2)
			else:
				deleteTriIndices.append(ind)
	deleteBiIndices = list(set(deleteBiIndices))			
	deleteTriIndices = list(set(deleteTriIndices))			
	deleteBiIndices.reverse()
	deleteTriIndices.reverse()
	bigram_list = [(" ".join(tup), score) for tup, score in bigram_scored]
	trigram_list = [(" ".join(tup), score) for tup, score in trigram_scored]
	for i in deleteBiIndices: del bigram_list[i]
	for i in deleteTriIndices: del trigram_list[i]

	grams_scored = copy.copy(bigram_list)
	grams_scored.extend(trigram_list)
	grams_scored_sorted = sorted(grams_scored, key=lambda tup: tup[1], reverse=True)

	large_groups = [(name, score) for name, score in grams_scored_sorted if score*len(searchresults)>10]
	maxcutoff = 5
	idGroups = []
	for i, (name, score) in enumerate(large_groups):
		label = "namebox"+str(i)
		rids = [rid for rid in recordsHash.keys() if name in recordsHash[rid]]
		toprecipeimg = getTopRatedRecipe(rids)[1]
		idGroups.append({'label': label, 'name': name, 'count': len(rids), 'toprecipeimg': toprecipeimg, 'ids':rids})
	return idGroups


if __name__ == "__main__":
	groups = findNameGroups(searchresults)
	specificNameGroup = groups[0]['ids']
	(searchG, searchGrecipes, searchGingredients) = filterGraphByRecipeID(G, Grecipes, Gingredients, specificNameGroup)
	components = getPartitions(searchGrecipes)
	search1jsonObject = outputScreenJSON(components, cutoff, searchG)

