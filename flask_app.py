from flask import Flask, request, make_response, jsonify
from main import handle_get_request


app = Flask(__name__)

@app.route('/fhir', defaults={'path': ''})
@app.route('/fhir/<path:url>')
def request(url):
  print(url)
  content, status = handle_get_request(url)
  return make_response(jsonify(content), status)
