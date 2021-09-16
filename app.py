import codecs, base64
from flask import Flask, render_template, json, request
from werkzeug.exceptions import BadRequest
from suggestions import suggest, InvalidPublicKey
from ln import lnapi

app = Flask(__name__)

@app.errorhandler(InvalidPublicKey)
def handle_exception(e):
    response = BadRequest().get_response()

    response.data = json.dumps({
        "code": 400,
        "message": "Unable to find a node with that public key",
    })

    response.content_type = "application/json"

    return response


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/api/suggest/<pub_key>", methods=['GET'])
def api_suggest(pub_key):
    return {'suggestions': suggest(pub_key)}


@app.route("/api/invoice", methods=['POST'])
def api_create_invoice():
    return lnapi("invoices", method="POST", json=request.json)


@app.route("/api/invoice/<invoice>", methods=['GET'])
def api_get_invoice(invoice):
    return lnapi(f"invoice/{invoice}")
