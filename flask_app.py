import flask
import json
from flask import Flask, make_response, jsonify, Response
from main import handle_get_request, handle_post_request

import dicttoxml


app = Flask(__name__)

@app.route('/fhir', defaults={'path': ''})
@app.route('/fhir/<path:path>', methods=['GET', 'POST'])
def request(path):
  url = flask.request.full_path[1:].partition('/')[2]
  content, status = handle_get_request(url)
  if flask.request.method == 'GET':
    # Check accept header
    if flask.request.headers.get('Accept') == 'application/xml' or '_format=xml' in url:
      return Response(dicttoxml.dicttoxml(content), status, mimetype='text/xml')
    else:
      return Response(json.dumps(content), status, mimetype='application/json')

  elif flask.request.method == 'POST':
    body = flask.request.json
    content, status = handle_post_request(url, body)

    if flask.request.headers.get('Accept') == 'application/xml':
      return Response(dicttoxml.dicttoxml(content), status, mimetype='text/xml')
    else:
      return Response(json.dumps(content, sort_keys=False), status, mimetype='application/json')
