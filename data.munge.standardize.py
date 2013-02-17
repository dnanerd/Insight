#!/Users/apple/Desktop/Work/Scripts/Insight/venv/bin/python

#import pymongo #==2.4.2


import json
import yummly #https://github.com/dgilland/yummly.py
import sys
import re
import unicodedata
from collections import *
import time
import pymongo
import MySQLdb
import pprint
import re
import copy
import networkx as nx
import nltk
import pandas
import math
from nltk.corpus import wordnet as wn


def mysqlify(x):
	return x.replace("\'","\\\'") 
#	a = a.replace('/', '\/')
#	a = a.replace("(", "\(")
#	a = a.replace(")", "\)")
#	return a


def define(word):
	synsets = wn.synsets(word)
	if synsets:
		definition = synsets[0].lemma_names[0]
		if (definition.lower() in word.lower()) or (word.lower() in definition.lower()):
			return definition
		else:
			return 'NULL'
	else:
		return 'NULL'

def defineMultiple(words):
	tokens = nltk.word_tokenize(words)
	tokenDefined = []
	for t in tokens:
		td = define(t)
		if td=='NULL':
			tokenDefined.append(t)
		elif math.fabs(len(td)-len(t))>2:
			tokenDefined.append(t)
		elif '_' in td:
			tokenDefined.append(t)
		else:
			tokenDefined.append(td)
	return " ".join(tokenDefined)

def reduceIngredient(ingr,ingrList):
	return ingr
	tokens = nltk.word_tokenize(ingr)
	if len(tokens)>1:
#		nouns = [word for word,tag in nltk.pos_tag(tokens) if 'NN' in tag]
		#if there is more than one word in the ingredient list
		#parse it to see if there are descriptors
#		candidateNouns = [n for n in nouns if n in ingrList]
		candidateIngr = [n for n in tokens if n in ingrList]
#		reducedNoun = " ".join(tokens)
		if len(candidateIngr)>1:
			#pick one
#			choice = 0
#			candidateNouns[choice]
			firstingr = tokens.index(candidateIngr[0])
			lastingr = tokens.index(candidateIngr[-1])
#			print firstingr
#			print lastingr
			reducedIngr = " ".join(tokens[firstingr:(lastingr+1)])
			print "Merge ingr ", ingr, " => ", reducedIngr, " ?"
		elif len(candidateIngr)==1:
			print "Merge ingr: 1)",ingr," 2)",candidateIngr[0], "?"
#			return candidateNouns[0]
#		else:
			#no candidate nouns in database
#			return ingr
		#merge, then call normalizeIngredient(ingr, ingrList) again with modified ingredient/ingrList


def reduceIngredients():
	db = MySQLdb.connect("localhost",'testuser','testpass',"test" )
	cursor = db.cursor()
	cursor.execute("""SELECT DISTINCT normingredient FROM ingredients""")
	ingredientTuples = cursor.fetchall()
	ingrList = [ingrTup[0] for ingrTup in ingredientTuples]
	for ingr in ingrList:
		reduceIngredient(ingr, ingrList)
	db.close()

#DESCRIPTION:
#looks through ingredients list and parses recipe list ingredients
#into amount, unit, ingredient
def standardizeIngredients():
	db = MySQLdb.connect("localhost",'testuser','testpass',"test" )
	# prepare a cursor object using cursor() method
	cursor = db.cursor()
	cursor.execute("""SELECT DISTINCT ingredient FROM ingredients""")
	ingredientTuples = cursor.fetchall()
	storedIngredientList = [ingrTup[0] for ingrTup in ingredientTuples]
	print len(storedIngredientList)
	for ingr in storedIngredientList:
		ingrNEW = ingr.replace('-',' ')
		ingrNorm = define(ingrNEW)
		cmd = "UPDATE ingredients SET normingredient = \'" + mysqlify(ingrNorm) + "\' WHERE ingredient = \'" + mysqlify(ingr) + "\'"
		cursor.execute(cmd)
	cmd = "SELECT DISTINCT ingredient FROM ingredients WHERE normingredient=\'NULL\'"
	cursor.execute(cmd)
	ingredientTuples = cursor.fetchall()
	storedIngredientList = [ingrTup[0] for ingrTup in ingredientTuples]
	for ingr in storedIngredientList:
		ingrNEW = ingr.replace('-',' ')
		ingrNorm = defineMultiple(ingrNEW)
		cmd = "UPDATE ingredients SET normingredient = \'" + mysqlify(ingrNorm) + "\' WHERE ingredient = \'" + mysqlify(ingr) + "\'"
		cursor.execute(cmd)
	db.commit()
	db.close()



if __name__ == "__main__":
	db = MySQLdb.connect("localhost",'testuser','testpass',"test" )
	# prepare a cursor object using cursor() method
	cursor = db.cursor()
	cursor.execute("""SELECT * FROM units""")
	unitTuple = cursor.fetchall()
	unitHash = dict(unitTuple)

	standardizeIngredients()
#	reduceIngredients()
	db.commit()
	db.close()
