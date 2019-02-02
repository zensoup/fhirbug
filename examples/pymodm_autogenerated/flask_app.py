import sys
from pathlib import Path
import json
import dicttoxml
import flask
from flask import Flask, Response
import pymodm

try:
    from fhirbug.config import settings
    settings.configure("settings")
    from fhirbug.server import GetRequestHandler, PostRequestHandler, PutRequestHandler
except ModuleNotFoundError:
    # Allow execution from a git clone without having fhirball installed.
    if Path('./fhirbug').is_dir(): # Executed from the example's directory`
        sys.path.append("./")
    elif Path('../../fhirbug').is_dir(): # Executed from the project's root directory`
        sys.path.append("../../")
    from fhirbug.config import settings
    settings.configure("settings")
    from fhirbug.server import GetRequestHandler, PostRequestHandler, PutRequestHandler


pymodm.connect(settings.PYMODM_CONFIG["URI"])

app = Flask(__name__)
app.config.update(debug=settings.DEBUG)


@app.route("/fhir", defaults={"path": ""})
@app.route("/fhir/<path:path>", methods=["GET", "POST", "PUT"])
def request(path):
    url = flask.request.full_path[1:].partition("/")[2]
    request_headers = flask.request.headers

    # Handle GET requests
    if flask.request.method == "GET":
        handler = GetRequestHandler()
        content, status = handler.handle(url, query_context=flask.request)

        # Check the accept header and convert to the appropriate format
        resp_content, mimetype = convert_response_content(request_headers, url, content)
        return Response(resp_content, status, mimetype=mimetype)

    # Handle POST and PUT requests
    elif flask.request.method in ["POST", "PUT"]:
        body = flask.request.json
        method = flask.request.method
        handler = PostRequestHandler() if method == "POST" else PutRequestHandler()
        content, status = handler.handle(url, body)

        # Check the accept header and convert to the appropriate format
        resp_content, mimetype = convert_response_content(request_headers, url, content)
        return Response(resp_content, status, mimetype=mimetype)


def convert_response_content(headers, url, content):
    """
    Reads the request's ``Accept`` header and the _format query parameter
    and converts content to the appropriate type.

    returns a tuple (content, mime_type)
    """
    if headers.get("Accept") == "application/xml" or "_format=xml" in url:
        return dicttoxml.dicttoxml(content), "text/xml"
    else:
        return json.dumps(content), "application/json"


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=settings.DEBUG)
