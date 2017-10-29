import flask
from flask import Flask, make_response, jsonify
from main import handle_get_request


app = Flask(__name__)

@app.route('/fhir', defaults={'path': ''})
@app.route('/fhir/<path:path>')
def request(path):
  url = flask.request.full_path[1:].partition('/')[2]
  content, status = handle_get_request(url)
  return make_response(jsonify(content), status)
