#!/usr/bin/env python

import os

from flask import Flask
from flask import url_for
from flask import render_template
from flask import jsonify
from flask import url_for
from flask import request
import dataliveloadgraph as dll
import datalivesearch as dls
import datalivegraphcluster as dlg
import datalivecluster as dlc
import networkx as nx


app = Flask(__name__)

f = open("test.txt", 'r')
filehtml = [];
for l in f:
    filehtml.append(l)
f.close

f = open("static/data.tsv", 'r')
barchart_data = [];
for l in f:
    filehtml.append(l)
f.close

(unitHash, recipeNameHash, recipesHash, G, Grecipes, Gingredients) = dll.loadApp()


#def loadData():


@app.route('/')
def index():
    return render_template('search.html')


@app.route('/result', methods=['GET'])
def result():
    search = request.args.getlist('search')[0].decode('string_escape')
    resultFile = "searchrecordids.txt"
    results = dls.searchRecipes(search, resultFile)
    total = len(results)
    idGroups = dlc.findNameGroups(results)
    idGroupsHash = {}
    for group in idGroups:
        idGroupsHash[group['label']] = group['ids']
    return render_template('finitescroll.html', query=search, totalresults = total, searchJSON=idGroups, searchJSON2=[idGroupsHash])

@app.route('/result2', methods=['GET', 'POST'])
def result2():
    results = request.form.getlist('links[]')
    total = len(results)
    (searchG, searchGrecipes, searchGingredients) = dls.filterGraphByRecipeID(G, Grecipes, Gingredients, results)
#    clusters = dlg.getClusters(searchGrecipes)
    clusters = dlg.getPartitions(searchGrecipes)
    cutoff = min(1000, len(clusters))
#    search2jsonObject = [dlg.outputScreen2JSON(subCluster(cluster)) for cluster in clusters[0:cutoff]]
    searchjsonObject = dlg.outputScreenJSON(clusters, cutoff, recipesHash)
#    searchjsonObject2 = {'object':'searchjsonObject'}
    searchjsonObject2 = [tup[2] for tup in searchjsonObject[0]['links']]

    return render_template('variations.html', query=search, totalresults = total, searchJSON=searchjsonObject, searchJSON2=searchjsonObject2)


@app.route('/result3', methods=['GET', 'POST'])
def result3():
    results = request.form.getlist('links[]')
    total = len(results)
    (searchG, searchGrecipes, searchGingredients) = dls.filterGraphByRecipeID(G, Grecipes, Gingredients, results)
#    clusters = dlg.getClusters(searchGrecipes)
    clusters = dlg.getPartitions(searchGrecipes)
    cutoff = min(1000, len(clusters))
#    search2jsonObject = [dlg.outputScreen2JSON(subCluster(cluster)) for cluster in clusters[0:cutoff]]
    searchjsonObject = dlg.outputScreenJSON(clusters, cutoff)
#    searchjsonObject2 = {'object':'searchjsonObject'}
    searchjsonObject2 = [tup[2] for tup in searchjsonObject[0]['links']]

    return render_template('infinite_scroll.html', query=search, totalresults = total, searchJSON=searchjsonObject, searchJSON2=searchjsonObject2)

@app.route('/recipes', methods=['GET', 'POST'])
def recipes():
    links = request.form.getlist('links[]')

    return render_template('test.html', links = links)

@app.route('/search')
def search():
    return render_template('search.html')

#@app.route('/searching', methods=['GET', 'POST'])
#def searching():
#    return render_template('searching.html', query = request.args.getList('search'))


@app.route('/oldresult', methods=['GET', 'POST'])
def oldresult():
    search = request.args.getlist('search')[0].decode('string_escape')
    resultFile = "searchrecordids.txt"
    results = dls.searchRecipes(search, resultFile)
    total = len(results)
    (searchG, searchGrecipes, searchGingredients) = dls.filterGraphByRecipeID(G, Grecipes, Gingredients, results)
#    clusters = dlg.getClusters(searchGrecipes)
    clusters = dlg.getPartitions(searchGrecipes)
    cutoff = min(5, len(clusters))
#    search2jsonObject = [dlg.outputScreen2JSON(subCluster(cluster)) for cluster in clusters[0:cutoff]]
    searchjsonObject = dlg.outputScreenJSON(clusters, cutoff)

    return render_template('resultScreen1.html', query=search, totalresults = total, searchJSON=searchjsonObject)


@app.route('/howitworks')
def howitworks():
    return render_template('howitworks.html')

@app.route('/data')
def data():
    return render_template('crossfilter.dummy.html')

@app.route('/contact')
def contact():
    return render_template('about.html')
    
@app.route('/api')
def api():
    recommendation = {'band':'radiohead', 'album':'Ok Computer'}
    return jsonify(recommendation)


@app.route('/broken')
def broken():
    var = does_not_exist
    return jsonify(recommendation)


@app.route('/bootstrap')
def bootstrap():
    return render_template('bootstrap.html')


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.debug = True
    app.run(host='0.0.0.0',port=5000)
#      app.run(host='192.168.1.28', port=8000)

    
