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

def createRecipeGraph(defaultGFile, loadFromFile):
	#there might be more ids in the jaccard graph than that which are stored in recipes
	#load the recipes hash table so we can keep track of the recipes
	recipesHash = pickle.load(open("idToIngredient.pickle"))
	#Note: this is a hackaround. Ideally we should calculate the jaccard distance only between those records in recipe table
	#TO DO: make databases consistent

	jlimit = 0.7 #set the min jaccard distance for nodes to be connected
	#create recipe graph
	if loadFromFile and os.path.exists(defaultGFile):
		#if the network has already been generated and pickled, load it
		print "loadRecipeGraph: recipe graph file exists. loading..."
		Grecipes = pickle.load(open(defaultGFile))
		print len(Grecipes.nodes()), " nodes in jaccard graph"
		return Grecipes
	else:
		Grecipes = nx.Graph()
		print "loadRecipeGraph: Retrieving jaccard scores from database..."
		#open database connection
		db = sql.connect("localhost",'testuser','testpass',"test" )
		cursor = db.cursor()

		#since jaccard distances are bidirectional, only one direction needs to be stored
		#therefore we need to 
		cursor.execute("SELECT id1, id2, jaccard FROM recipejaccard WHERE jaccard>="+str(jlimit)) 
		jaccardTup = cursor.fetchall()
		cursor.execute("SELECT DISTINCT id1 FROM recipejaccard WHERE jaccard>="+str(jlimit) )
		id1Tup = cursor.fetchall()
		recipenodes1 = set([id1[0] for id1 in id1Tup])

		cursor.execute("SELECT DISTINCT id2 FROM recipejaccard WHERE jaccard>="+str(jlimit) )
		id2Tup = cursor.fetchall()
		recipenodes2 = set([id2[0] for id2 in id2Tup])
		db.close()

		recipenodes = list(recipenodes1 | recipenodes2)

		print "loadRecipeGraph: Adding ", len(recipenodes), " nodes..."
		Grecipes.add_nodes_from(recipenodes)
		print "loadRecipeGraph: Add jaccard scores to graph (", len(jaccardTup)," edges in total)..."
		if jaccardTup:
			Grecipes.add_weighted_edges_from(jaccardTup)
			Grecipes =  nx.subgraph(Grecipes, recipesHash.keys())
			f = open(defaultGFile, 'w')
			pickle.dump(Grecipes, f)
			f.close()
		print len(Grecipes.nodes()), " nodes in jaccard graph"
		return Grecipes


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

def loadRecipeHashFromDB():
	db = sql.connect("localhost",'testuser','testpass',"test" )
	cursor=db.cursor()
	cursor.execute("SELECT id, normingredient FROM normrecipeingredients")
	ingredientTuples = cursor.fetchall()
	recipesHash = defaultdict(list)
	for rid, ingr in ingredientTuples:
		recipesHash[rid].append(ingr)
	db.commit()
	db.close()
	pickle.dump(recipesHash,open("idToIngredient.pickle", 'w'))
	return recipesHash
def loadRecipeHashFromPickle():
	recipesHash = pickle.load(open("idToIngredient.pickle"))
	return recipesHash

def loadUnitHashFromDB():
	db = sql.connect("localhost",'testuser','testpass',"test" )
	cursor=db.cursor()
	cursor.execute("SELECT keyword, unit FROM units")
	unitTuples = cursor.fetchall()
	unitHash = dict(unitTuples)
	db.commit()
	db.close()
	pickle.dump(unitHash,open("unitNormHash.pickle", 'w'))
	return unitHash
def loadUnitHashFromPickle():
	unitHash = pickle.load(open("unitNormHash.pickle"))
	return unitHash


def loadRecordNameFromDB():
	db = sql.connect("localhost",'testuser','testpass',"test" )
	cursor=db.cursor()
	cursor.execute("SELECT id, name FROM records")
	recordsTuples = cursor.fetchall()
	recordsHash = dict(recordsTuples)
	db.commit()
	db.close()
	pickle.dump(recordsHash,open("idToNameHash.pickle", 'w'))
	return recordsHash
def loadRecordNameFromPickle():
	recordsHash = pickle.load(open("idToNameHash.pickle"))
	return recordsHash

def loadJaccardFromDB():
	db = sql.connect("localhost",'testuser','testpass',"test" )
	cursor = db.cursor()

	#since jaccard distances are bidirectional, only one direction needs to be stored
	#therefore we need to 
	#select without jaccard limit
	cmd = "SELECT id1, id2, jaccard FROM recipejaccard"
	cursor.execute(cmd) 
	jaccardTuples = cursor.fetchall()
	db.close()
	jaccardHash = defaultdict(dict)
	for rid1, rid2, jaccard in jaccardTuples:
		jaccardHash[rid1][rid2] = jaccardHash
	pickle.dump(jaccardHash,open("jaccard.pickle", 'w'))
	return jaccardHash

def loadApp():

	unitHash = loadUnitHashFromDB()
	recordsHash = loadRecordNameFromDB()
	recipesHash = loadRecipeHashFromDB()
#	unitHash = loadUnitHashFromPickle()
#	recordsHash = loadRecordNameFromPickle()
#	recipesHash = loadRecipeHashFromPickle()

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


