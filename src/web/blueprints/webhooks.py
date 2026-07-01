"""Blueprint reserved for application-owned webhook adapters.

AUT-03 will add its Pipedrive endpoint here. No webhook route is registered yet.
"""

from flask import Blueprint, jsonify

webhooks_blueprint = Blueprint("webhooks", __name__, url_prefix="/webhooks")

@webhooks_blueprint.post("/pipedrive")
def pipedrive_webhook():
    return jsonify({"ok": True, "message": "pipedrive webhook received"}), 200