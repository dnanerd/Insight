#!/usr/bin/env python

import os

from flask import Flask
from flask import url_for
from flask import render_template
from flask import jsonify
from flask import url_for


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
    return render_template('index.html', title="MyTitle")


@app.route('/test')
def test():
    return render_template('test.html', 
                           my_name="George",
                           my_locations=filehtml,
                           )

@app.route('/start')
def start():
    return render_template('search.html')


@app.route('/searching')
def searching():
    return render_template('searching.html')


@app.route('/result')
def result():
    return render_template('barchart.html')

    
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
    app.run(host='0.0.0.0', port=port)
