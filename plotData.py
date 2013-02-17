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
	ingredientHash[ingr].append(rid)

#f = open("recipeDegrees.txt", 'w')
#for rid, ingredients in recipeHash.iteritems():
#	f.write(rid+"\t"+str(len(ingredients))+"\n")
#f.close()
#f2 = open("ingredientDegrees.txt", 'w')
#for iid in ingredientHash.keys():
#	f2.write(iid+"\t"+str(len(ingredientHash[iid]))+"\n")
#f2.close()

(unitHash, recipeNameHash, recipesHash, G, Grecipes, Gingredients) = dll.loadApp()

class MRWordCounter(MRJob):
    def mapper(self, key, line):
        for word in line.split():
            yield word, 1

    def reducer(self, word, occurrences):
        yield word, sum(occurrences)

if __name__ == '__main__':
    MRWordCounter.run()