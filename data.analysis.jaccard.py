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
import networkx as nx


def mysqlify(x):
	return x.replace("\'","\\\'") 
#	a = a.replace('/', '\/')
#	a = a.replace("(", "\(")
#	a = a.replace(")", "\)")
#	return a
def calculateRecipeJaccardIndices():
	db = sql.connect("localhost",'testuser','testpass',"test" )
	cursor = db.cursor()

	lengths = [2000,4000,6000,8000,10000,12000,14000,16000,18000,20000,22000,24000,26000,28000,30000,32000,34000,36000,38000,40000]
	for length in lengths:
		filename = "pythonpp"+str(length)+".out"
		sys.stderr.write("Processing "+ filename)
		f = open(filename)
		for line in f:
			linear = line.split(" ")
			if len(linear)==3:
				cmd = "INSERT IGNORE INTO recipejaccard(id1, id2, jaccard) VALUES(\'"+mysqlify(linear[0])+"\',\'"+mysqlify(linear[1])+"\',"+linear[2]+")"
				cursor.execute(cmd)
#			else:
#				print line
		f.close()
		db.commit()
	db.close()

def initGraph():
	db = sql.connect("localhost",'testuser','testpass',"test" )
	cursor = db.cursor()
	cursor.execute("SELECT DISTINCT id FROM normrecipeingredients")
	idTuples = cursor.fetchall()
	rids = [rid[0] for rid in idTuples]
	db.commit()

	jlimit = 0.2
	#create recipe graph
	Grecipes = nx.Graph()
	Grecipes.add_nodes_from(rids)
	pickle.dump(Grecipes,open("Grecipejaccard.pickle", 'w'))

def addEdgesToGraph():

	lengths = [2000,4000,6000,8000,10000,12000,14000,16000,18000,20000,22000,24000,26000,28000,30000,32000,34000,36000,38000,40000]
	for length in lengths:
		filename = "pythonpp"+str(length)+".out"
		sys.stderr.write("Processing "+ filename)
		f = open(filename)
		edgeList = []
		for line in f:
			linear = tuple(line.split(" "))
			if len(linear)==3:
				try:
					if linear[2]>=0.8:
						edgeList.append(linear)
				except:
					sys.stderr.write("Graph insert error")
	#			else:
	#				print line
		sys.stderr.write("Add edges to graph...")
		Grecipes.add_weighted_edges_from(edgeList)
		f.close()
	sys.stderr.write("Pickling...")
	pickle.dump(Grecipes,open("Grecipejaccard.pickle", 'w'))

initGraph()
addEdgesToGraph()