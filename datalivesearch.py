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
import networkx as nx


def searchRecipes(query):
	definedQueries = ['banana bread','cookies','cake']
	searchResultFile = 'searchrecordids.txt'

	if query in definedQueries and os.path.isfile(query.split()[0]+searchResultFile):
		f = open("recordsdb."+query.split()[0]+".flat.txt",'r')
		searchRecords = json.load(f.read())
		f.close()
		recipeids = [item["id"] for result in searchRecords for item in result["matches"] if 'id' in item.keys()]
		f = open(query.split()[0]+searchResultFile,'w')
		f.write("\n".join(recipeids))
		f.close()
		return (searchResultFile, len(recipeids))
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
		return (searchResultFile, len(records))

if __name__ == "__main__":

	searchRecipes('banana bread')