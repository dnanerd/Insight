#!/Users/apple/Desktop/Work/Scripts/Insight/venv/bin/python

import sys
import re
import datastorerecipesmysql as storerecipes
import datastorerecordsmysql as storerecords
import datamungestandardize as datastandardize
import datamungenormalize as datanormalize
import datamungeimageurlscrapper as dataimgurl
import pythonparallel

newrecordsfile = "recordsdb.muffin.flat.txt"

newids = storerecords.parseSearchResults(newrecordsfile)
newrecipesfile = "recipedb.muffin.flat.txt"
storerecipes.parseRecipeResults(newrecipesfile)

datastandardize.standardizeIngredients()
datanormalize.normalizeIngredients()

imgfile = "imageurlscrapper"
sys.stdout = open(imgfile+".out", 'w')
sys.stderr = open(imgfile+".err", 'w')
dataimgurl.getImgUrlsById(newids)
dataimgurl.storeImgUrls("imageurlscrapper.out")
dataimgurl.deleteBadImages("dbBadImages.txt")

sys.stdout = open("recipejaccard.out", 'w')
sys.stderr = open("recipejaccard.err", 'w')

pythonparallel.runParallelJaccard(newids[0:2000])

pythonparallel.runParallelJaccard(newids[2000:4000])
