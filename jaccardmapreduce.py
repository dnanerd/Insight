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
import re
import copy
import numpy as np
import scipy as sp
import pandas as pd
import nltk
import pickle
from mrjob.job import MRJob
import dataliveloadgraph as dll
import networkx as nx

db = sql.connect("localhost",'testuser','testpass',"test" )
cursor=db.cursor()
cursor.execute("SELECT DISTINCT normingredient FROM normrecipeingredients")
tuples = cursor.fetchall()
ingredients = [t[0] for t in tuples]

f2 = open("ingredients.dat", 'w')
f2.write("\n".join(ingredients))
f2.close()

db = sql.connect("localhost",'testuser','testpass',"test" )
cursor=db.cursor()
cursor.execute("SELECT id, normingredient FROM normrecipeingredients WHERE id IS NOT NULL")
recipeTuples = cursor.fetchall()
db.commit()
db.close()
recipeHash = defaultdict(list)
ingredientHash = defaultdict(list)
for rid, ingr in recipeTuples:
	recipeHash[rid].append(ingr)

pickle.dump(recipeHash, open("idToIngredient.pickle", 'w'))
#G = dll.getRecipeIngredientGraph("defaultGFile.pickle", False)
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

G = pickle.load(open("/Users/apple/Desktop/Work/Scripts/Insight/defaultGFile.pickle"))
f = open("defaultGFile.pickle", 'w')
pickle.dump(G, f)
f.close()
sizes = dict([(rnode, G.degree(rnode)) for rnode in recipeNodes])
pickle.dump(sizes, open("defaultRecipeLengths.pickle", 'w'))

