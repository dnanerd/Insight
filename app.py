#!/usr/bin/env python

import os

from flask import Flask
from flask import url_for
from flask import render_template
from flask import jsonify
from flask import url_for
from flask import request
import datalivesearch as dls
import datalivegraphcluster as dlg


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



@app.route('/')
def index():
    return render_template('search.html')


@app.route('/search')
def search():
    return render_template('search.html')

#@app.route('/searching', methods=['GET', 'POST'])
#def searching():
#    return render_template('searching.html', query = request.args.getList('search'))


@app.route('/result', methods=['GET', 'POST'])
def result():
    search = request.args.getlist('search')[0].decode('string_escape')
    (resultFile, total) = dls.searchRecipes(search)
    search1jsonFile, labels = dlg.getClusters(resultFile)

    sidebar = [("divID"+str(i), l, c) for i, (l,c) in enumerate(labels)]
    return render_template('resultScreen1.html', query=search, totalresults = total, labels = sidebar, indices = [i for i, n in enumerate(labels)], search1jsonFile = "\""+search1jsonFile+"\"")


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
#    app.run(host='192.168.1.28', port=8000)

    
