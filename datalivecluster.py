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

def retrieveSearchRecords(searchResultFile):
	f = open(searchResultFile, 'r')
	results = f.read().split("\n")
	return results

def highest_centrality(cent_dict, n=1):
     """Returns a tuple (node,value) with the node
 with largest value from Networkx centrality dictionary."""
     # Create ordered tuple of centrality data
     cent_items=[(b,a) for (a,b) in cent_dict.iteritems()]
     # Sort in descending order
     cent_items.sort()
     cent_items.reverse()
     return tuple(reversed(cent_items[0:n]))


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



def getTopRatedRecipe(recipes, results):
	#DESCRIPTION: 
	# Given a list of recipes, find the images associated with each recipe
	# From list of images, pick random image to display as icon
	# if a large high res image exists, select from high res images
	# If no high res image exists, select from lower res yummly icon
	# else: show default no-img-available photo
	db = sql.connect("localhost",'testuser','testpass',"test" )
	cursor=db.cursor()
	#select the top races recipes in this list
	defaultimgurl = "static/imgunavailable.png"
	cmd = "SELECT id, rating, imgurl, imgurllg, sourcename FROM records WHERE id IN (\'"+"\',\'".join(recipes)+"\') ORDER BY rating DESC"
	cursor.execute(cmd)
	toprecords = cursor.fetchall()
#	cmd = "SELECT id, rating, imgurl, imgurllg, sourcename FROM records WHERE id IN (\'"+"\',\'".join(results)+"\') ORDER BY rating DESC"
#	cursor.execute(cmd)
#	broadTup = cursor.fetchall()

	allrecords = [(rid, imgurl) for rid, rating, imgurl, imgurllg, sourcename in toprecords]
#	broadrecords = [(rid, imgurllg) for rid, rating, imgurl, imgurllg,sourcename in broadTup if imgurllg and imgurllg!='NULL' and '{{' not in imgurllg and sourcename!='Food.com']
	imagerecords = [(rid, imgurl) for rid, rating, imgurl, imgurllg, sourcename in toprecords if imgurl and imgurl!='NULL']
	largeimagerecords = [(rid, imgurllg) for rid, rating, imgurl, imgurllg,sourcename in toprecords if imgurllg and imgurllg!='NULL' and '{{' not in imgurllg]
	curatedimagerecords = [(rid, imgurllg) for rid, rating, imgurl, imgurllg,sourcename in toprecords if imgurllg and imgurllg!='NULL' and '{{' not in imgurllg and sourcename!='Food.com']
	if len(curatedimagerecords)>0:
		return random.choice(curatedimagerecords)
	elif len(largeimagerecords)>0:
		return random.choice(largeimagerecords)
	elif len(imagerecords)>0:
		return random.choice(imagerecords)
#	elif len(broadrecords)>0:
#		return random.choice(broadrecords)
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
			toprecipeimg = getTopRatedRecipe(recipes, recipes)[1]
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
		toprecipeimg = getTopRatedRecipe(rids, rids)[1]
		idGroups.append({'label': label, 'name': name, 'count': len(rids), 'toprecipeimg': toprecipeimg, 'ids':rids})
	return idGroups


if __name__ == "__main__":
	groups = findNameGroups(searchresults)
	specificNameGroup = groups[0]['ids']
	(searchG, searchGrecipes, searchGingredients) = filterGraphByRecipeID(G, Grecipes, Gingredients, specificNameGroup)
	components = getPartitions(searchGrecipes)
	search1jsonObject = outputScreenJSON(components, cutoff, searchG)

