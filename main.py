from flask import Flask, request, redirect, url_for, flash
from flask import render_template
import helper
from flask import jsonify
import json
from datetime import datetime
import runpy
from urllib.parse import urlencode

import importlib




app = Flask(__name__)
app.secret_key = 'nv'

def include_module(module):
    return importlib.import_module(module)

@app.context_processor
def utility_processor():
    return dict(include_module=include_module)


@app.route('/')
def index():

    os_name = request.args.get('os_name', 'android')
    type = request.args.get('type', 'order')
    date_from_input = request.args.get('date_from', '12/18/2019')
    date_to_input = request.args.get('date_to', '12/01/2023')

    panel_class = 'primary'

    try:
        date_from = datetime.strptime(date_from_input, '%m/%d/%Y').strftime("%Y-%m-%d")
        date_to = datetime.strptime(date_to_input, '%m/%d/%Y').strftime("%Y-%m-%d")
    except ValueError:
        pass


    return render_template('index.html',
                           type=type,
                           os_name=os_name,
                           date_from=date_from,
                           date_to=date_to,
                           date_from_input=date_from_input,
                           date_to_input=date_to_input,
                           panel_class=panel_class,

                           )


@app.route('/date/<type>/<os_name>/<date_from>/<date_to>')
def date(type, os_name , date_from, date_to):
    json_net = helper.getNetwork(type=type,os_name=os_name, date_from=date_from, date_to=date_to)
    return jsonify(json_net)


@app.route('/point/<type>/<os_name>/<date_from>/<date_to>/<code>')
def point_data(type,os_name, date_from, date_to, code):
    json_net = helper.getNetwork(type=type,os_name=os_name, date_from=date_from, date_to=date_to, code=code)
    return jsonify(json_net)


@app.route('/point/<type>/<os_name>/<date_from>/<date_to>/<code>/<key>')
def point_data_key(type,os_name, date_from, date_to, code, key):
    json_net = helper.getNetwork(type=type,os_name=os_name, date_from=date_from, date_to=date_to, code=code, getkey=key)
    return jsonify(json_net)


@app.route('/events/freq/')
def events_freq():
    json_net = helper.getEventFreq()
    return jsonify(json_net)


@app.route('/plotly/<modul>/<type>/<size>/<titile>')
def plotly(modul,size, titile):

    type = request.args.get('type', 'order')
    date_from_input = request.args.get('date_from', '12/18/2019')
    date_to_input = request.args.get('date_to', '12/01/2023')

    try:
        date_from = datetime.strptime(date_from_input, '%m/%d/%Y').strftime("%Y-%m-%d")
        date_to = datetime.strptime(date_to_input, '%m/%d/%Y').strftime("%Y-%m-%d")
    except ValueError:
        pass

    modul_plot = include_module('lib.plotly')
    method_to_call = getattr(modul_plot, modul)
    return method_to_call(type=type,size=size,titile=titile, date_from=date_from, date_to=date_to)


app.run(host='0.0.0.0', port=7000, debug=True)
