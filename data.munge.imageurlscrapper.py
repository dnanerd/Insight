#!/Users/apple/Desktop/Work/Scripts/Insight/venv/bin/python

import sys
import re
import unicodedata
from collections import *
import time
import MySQLdb as sql
import re
import copy
import networkx as nx
import nltk
import urllib
import pycurl
from StringIO import StringIO

error = defaultdict(int)
def getHTML(addr):
	storage = StringIO()
	c = pycurl.Curl()
	c.setopt(c.URL, addr)
	c.setopt(c.WRITEFUNCTION, storage.write)
	c.perform()
	c.close()
	html = storage.getvalue()
	return html

def parseFoodDotCom(addr):
	sys.stdout.write("Processing: "+addr+"")
	html = getHTML(addr)

	m = re.findall('src=\"([^"]+\/recipes\/[^"]+)',html)
	if m and len(m)>0:
		return m[0]
	else:
		sys.stdout.write("ERROR: not found!\n")
		error['fooddotcom']+=1
		return ''

def parseAllRecipes(addr):
	sys.stdout.write("Processing: "+addr+"")
	try:
		html = getHTML(addr)
		m = re.search('class\=\"rec-image rec-shadow.*src\=\"([^"]+)\"',html)
		return m.group(1)
	except:
		sys.stdout.write("ERROR: not found!\n")
		error['allrecipes']+=1
		return ''

def parseMarthaStewart(addr):
	sys.stdout.write("Processing: "+addr+"")
	try:
		html = getHTML(addr)
		m = re.search('img src\=\"([^"]+)\"',html)
		return m.group(1)
	except:
		sys.stdout.write("ERROR: not found!\n")
		error['marthastewart']+=1
		return ''
def parseTasteOfHome(addr):
	sys.stdout.write("Processing: "+addr+"")
	try:
		html = getHTML(addr)
		m = re.search('img.*id.*MainContent.*class.*src="([^"]+)"', html)
		return m.group(1)
	except:
		sys.stdout.write("ERROR: not found!\n")
		error['tasteofhome']+=1
		return ''

def parseFoodNetwork(addr):
	sys.stdout.write("Processing: "+addr+"")
	try:
		html = getHTML(addr)
		m = re.search('<a id.*class.*href="([^"]+.jpg)"',html)
		return m.group(1)
	except:
		sys.stdout.write("ERROR: not found!\n")
		error['foodnetwork']+=1
		return ''

def parseMyRecipes(addr):
	sys.stdout.write("Processing: "+addr+"")
	try:
		html = getHTML(addr)	
		m = re.search('<img.*src="([^"]+\/recipes\/[^"]+)"', html)
		return m.group(1)
	except:
		sys.stdout.write("ERROR: not found!\n")
		error['myrecipes']+=1
		return ''
def parseEpicurious(addr):
	sys.stdout.write("Processing: "+addr+"")
	try:
		photoaddr = re.sub('/views/','/photo/', addr)
		html = getHTML(photoaddr)
		m = re.search('img src\=\"(/images[^"]+)\"', html)
		return m.group(1)
	except:
		sys.stdout.write("ERROR: not found!\n")
		error['epicurious']+=1
		return ''

def parseSeriousEats(addr):
	sys.stdout.write("Processing: "+addr+"")
	try:
		html = getHTML(addr)
		m = re.search('img src\=\"([^"]+\/recipes\/[^"]+)\"', html)
		return m.group(1)
	except:
		sys.stdout.write("ERROR: not found!\n")
		error['seriouseats']+=1
		return ''

def parseChow(addr):
	sys.stdout.write("Processing: "+addr+"")
	try:
		html = getHTML(addr)
		m = re.search('img src\=\"([^"]+\/thumbnail\/[^"]+)\"', html)
		return m.group(1)
	except:
		sys.stdout.write("ERROR: not found!\n")
		error['chow']+=1
		return ''
def getImgUrls():
	db = sql.connect("localhost",'testuser','testpass',"test" )
	cursor = db.cursor()
	cursor.execute("select sourcename,sourceurl from records where imgurl!=\'NULL\' and sourceurl!=\'NULL\' and imgurllg=\'NULL\'")
	tuples = cursor.fetchall()
	db.close()
	for name, url in tuples:
		largeimg = ''
		if name=='Food.com':
			largeimg = parseFoodDotCom(url)
		elif name=='AllRecipes':
			largeimg = parseAllRecipes(url)
		elif name=='Taste of Home':
			largeimg = parseTasteOfHome(url)
		elif name=='Food Network':
			largeimg =parseFoodNetwork(url)
		elif name=='MyRecipes':
			largeimg = parseMyRecipes(url)
		elif name=='Epicurious':
			largeimg = parseEpicurious(url)
		elif name=='Serious Eats':
			largeimg = parseSeriousEats(url)
		elif name=='Chow':
			largeimg = parseChow(url)
		if largeimg:
			sys.stderr.write(url+","+largeimg+"\n")

	for key, val in error.iteritems():
		sys.stdout.write(key+" threw "+str(val)+" errors")

def storeImgUrls(filename):
	db = sql.connect("localhost",'testuser','testpass',"test" )
	cursor = db.cursor()
	f = open(filename)
	for line in f:
		(url, img) = line.split(",")
		cursor.execute("UPDATE records SET imgurllg=\'"+img+"\' WHERE sourceurl=\'"+url+"\'")
		db.commit()
	db.close()

#getImgUrls()
storeImgUrls("imgurlscrapper2.out")