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
import community
import random
import math
#import matplotlib as mpl
import dataliveloadgraph
import datalivesearch
import datalivecluster as dlc


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
			elif (len(enrichment) + len(depletion))<1:
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
	if len(searchGrecipes.edges())>0:
		partition = community.best_partition(searchGrecipes)
		partitionArray = defaultdict(list)
		for k, v in partition.iteritems():
			partitionArray[v].append(k)
		sortedPartitions = sorted(partitionArray.itervalues(), key=lambda partition: len(partition), reverse=True)
		mergedPartitions = combineClusters(sortedPartitions)
	#	print mergedPartitions[0]
		components = [nx.subgraph(searchGrecipes,partition) for partition in sortedPartitions]
		return components
	else:
		return searchGrecipes

def sigmoid(x):
  return 1 / (1 + math.exp(-x))

def getCentroidRecipe(recipeids, ingrFreq):
	#define centroid recipe as the recipe in the cluster which (a) contains as many "essential" as possible, and (b) contains as few "non-essential" ingredients as possible

	ingrFreqHash = dict(ingrFreq)
	for ingr, freq in ingrFreq:
		if freq>0.6:
			ingrFreqHash[ingr]=1
	recipeEssentialityScore = {}
	for rid in recipeids:
		recipeEssentialityScore[rid] = np.prod(np.array([sigmoid(freq) for ingr, freq in ingrFreqHash.iteritems()]))
	sortedRecipes = sorted(recipeEssentialityScore.iteritems(), key=lambda (rid, score): score, reverse=True)
	print sortedRecipes
	maxScore = sortedRecipes[0][1]
	maxRecipes = [rid for rid, score in sortedRecipes if score==maxScore]
	return random.choice(maxRecipes)

def outputScreenJSON(recipeClusterList, maxcutoff, recipesHash):
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
			urlDict = dict([(rid, url) for rid, name, url in links])			
			toprecipeimg = dlc.getTopRatedRecipe(recipes)[1]
			#defaultimgurl = "static/imgunavailable.png"
			ingrCounts = getIngredientFrequencies(recipes)
			ingrCountsDict = dict(ingrCounts)

			centroid_recipe = getCentroidRecipe(recipes, ingrCounts).decode('string_escape')
			centroid_recipe_url = urlDict[centroid_recipe]
			centroid_recipe_name = recordsHash[centroid_recipe]
			centroid_recipe_ingredients = recipesHash[centroid_recipe]

			
			#get ingredient enrichment frequencies, and find those that are enriched and those that are depleted
			centroid_recipe_ingredients_sorted = sorted(centroid_recipe_ingredients, key=lambda ingr: ingrCountsDict[ingr], reverse=True)

			enrichment = []
			depletion = []
			displaytype = 'extension'

			if counter>1:
				basicRecipeHash = dict(retval[0]['ingrFreq'])
				variationRecipeHash = dict(ingrCounts)
				logRatios = findEnrichedIngredients(retval[0]['ingrFreq'], ingrCounts)
				enrichment = [(ingr, log) for ingr, log in logRatios if log>=2 and (ingr not in basicRecipeHash or basicRecipeHash[ingr]<0.5)]
				depletion = [(ingr, log) for ingr, log in logRatios if log<=-2 and (ingr in basicRecipeHash and basicRecipeHash[ingr]>0.5)]
				if len(enrichment)<=4 and len(depletion)<=4:
					displaytype = 'extension'

			if counter==1:
				name = getClusterLabel(recipes, recordsHash)
			else:
				if len(enrichment)>0:
					name = "with "+ enrichment[0][0]				
				elif len(depletion)>0:
					name = "without " + depletion[-1][0]
				else:
					name = "Basic recipe"
			merged = 0
			for value in retval:
				if value['name']==name:
					#merge clusters
					merged = 1
			if merged==0:
				retval.append({'label': "box"+str(counter), 'name': name, 'count': len(recipes), 'toprecipeimg': toprecipeimg, 'centroid_recipe_url': centroid_recipe_url, 'centroid_recipe_name': centroid_recipe_name, 'centroid_recipe_ingredients': centroid_recipe_ingredients_sorted, 'ingrFreq': ingrCounts, 'enrichment':enrichment, 'depletion': depletion, 'displaytype':displaytype, 'links': links})
	return retval


if __name__ == "__main__":
	components = getPartitions(searchGrecipes)
	search1jsonObject = outputScreenJSON(components, cutoff, searchG)

