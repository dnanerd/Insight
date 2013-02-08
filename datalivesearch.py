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


def mysqlify(x):
	return x.replace("\'","\\\'") 


def searchRecipes(query):
	definedQueries = ['banana bread','cookies','cake', 'muffin']
	searchResultFile = 'searchrecordids.txt'
	searchresults = []
	if query in definedQueries:
		searchresults = []
		if os.path.isfile(query.split()[0]+searchResultFile):
			#just copy the contents of the search result over
			f = open(query.split()[0]+searchResultFile,'r')
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
			f = open(query.split()[0]+searchResultFile,'w')
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
		f.write("\n".join([r[0] for r in records]))
		f.close()
		db.commit()
		db.close()

	db = sql.connect("localhost",'testuser','testpass',"test" )
	cursor = db.cursor()
	cursor.execute("""SELECT * FROM units""")
	print "unit hash created"
	unitTuple = cursor.fetchall()
	unitHash = dict(unitTuple)
	pickle.dump(unitHash, open("unitNormHash.pickle", 'w'))
	cursor.execute("""SELECT ingredient, normingredient FROM ingredients""")
	ingrTuple = cursor.fetchall()
	ingrHash = dict(ingrTuple)
	pickle.dump(ingrHash, open("ingrNormHash.pickle", 'w'))
	cursor.execute("SELECT id, name FROM records")
	recordTuples = cursor.fetchall()
	recordsHash = dict(recordTuples)
	pickle.dump(recordsHash, open("idToNameHash.pickle", 'w'))
	print "ingredient hash created"
	db.close()
	return (searchResultFile, len(searchresults))

if __name__ == "__main__":

	searchRecipes('banana')