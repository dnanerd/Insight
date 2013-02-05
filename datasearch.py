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
import matplotlib as plt

def searchRecipes(query):

CREATE VIEW searchrecords AS SELECT * FROM records WHERE id REGEXP '.*banana.*bread.*';


