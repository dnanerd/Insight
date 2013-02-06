#!/Users/apple/Desktop/Work/Scripts/Insight/venv/bin/python

import datashopper, datamaid
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

	db = sql.connect("localhost",'testuser','testpass',"test" )
	# prepare a cursor object using cursor() method
	cursor = db.cursor()
	#	cursor.execute("""SELECT * FROM units""")
	querywords = nltk.word_tokenize(query)
	cursor.execute("""DROP VIEW IF EXISTS searchrecords""")
	cursor.execute("""CREATE VIEW searchrecords AS SELECT * FROM records WHERE id REGEXP \'.*" + ".*".join(querywords)+".*\'""")
	cursor.execute("""SELECT count(*) FROM searchrecords""")
	cursor.execute("""DROP VIEW IF EXISTS searchrecipes""")
	cursor.execute("""CREATE VIEW searchrecipes AS SELECT * FROM recipes WHERE id REGEXP \'.*" + ".*".join(querywords)+".*\'""")
	cursor.execute("""SELECT count(*) FROM searchrecipes""")
	cursor.execute("""DROP VIEW IF EXISTS searchrecipeingredients""")
	cursor.execute("""CREATE VIEW searchrecipeingredients AS SELECT * FROM recipeingredients WHERE id REGEXP \'.*" + ".*".join(querywords)+".*\'""")
	cursor.execute("""SELECT count(*) FROM searchrecipeingredients""")
	db.commit()
	db.close()

if __name__ == "__main__":

	searchRecipes('cookies')