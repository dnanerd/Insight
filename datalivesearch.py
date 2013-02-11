#!/Users/apple/Desktop/Work/Scripts/Insight/venv/bin/python

import os.path
import json
import yummly #https://github.com/dgilland/yummly.py
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
import networkx as nx
import dataliveloadgraph

def mysqlify(x):
	return x.replace("\'","\\\'") 


def searchRecipes(query, searchResultFile):
	definedQueries = ['banana bread','cookies','cake', 'muffin']
	searchresults = []
	if query in definedQueries:
		searchresults = []
		if os.path.isfile(query.split()[0]+"searchrecordids.txt"):
			#just copy the contents of the search result over
			f = open(query.split()[0]+"searchrecordids.txt",'r')
			recipeids = f.read().split("\n")
			f.close()
			searchresults = recipeids
		else:
			#create contents of the search result by reading db
			yummlysearchresult ="recordsdb."+query.split()[0]+".flat.txt"
			f = open(yummlysearchresult,'r')
			searchRecords = json.loads(f.read())
			f.close()
			#process search result
			recipeids = [ item["id"] for result in searchRecords for item in result["matches"] if 'id' in item.keys() ]
			errors = 0
			for r in recipeids:
				try:
					recipeids[recipeids.index(r)] = r.decode('string_escape')
				except:
					errors+=1
					recipeids.remove(r)
			print errors, " recipes threw and error"
			searchresults = recipeids
			f = open(query.split()[0]+"searchrecordids.txt",'w')
			f.write("\n".join(searchresults))
			f.close()
		f = open(searchResultFile,'w')
		f.write("\n".join(searchresults))
		f.close()
	else:
		db = sql.connect("localhost",'testuser','testpass',"test" )
		# prepare a cursor object using cursor() method
		cursor = db.cursor()
		#	cursor.execute("""SELECT * FROM units""")
		querywords = nltk.word_tokenize(query)
		print "searching for results"
		cursor.execute("SELECT id FROM records WHERE id REGEXP \'.*" + ".*".join(querywords)+".*\'")
		records = cursor.fetchall()
		print "printing results"
		f = open(searchResultFile,'w')
		searchresults = [r[0] for r in records]
		f.write("\n".join(searchresults))
		f.close()
		db.commit()
		db.close()
	return searchresults

def filterGraphByRecipeID(G, Grecipes, nodes):
	searchGrecipes = nx.subgraph(Grecipes, nodes)
	ingrNodes = list(set([b for n in searchGrecipes.nodes() for b in G.neighbors(n)]))
	searchG = nx.subgraph(G, nodes.extend(ingrNodes))
	return (searchG, searchGrecipes)

if __name__ == "__main__":
	tempsearchfile = 'searchrecordids.txt'
	searchresults = searchRecipes('banana bread', tempsearchfile)
	(searchG, searchGrecipes) = filterGraphByRecipeID(G, Grecipes, searchresults)