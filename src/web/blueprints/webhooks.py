"""Blueprint reserved for application-owned webhook adapters.

AUT-03 will add its Pipedrive endpoint here. No webhook route is registered yet.
"""

from flask import Blueprint, jsonify, request
import os
import json

from automations.slack_client import send_slack_message

webhooks_blueprint = Blueprint("webhooks", __name__, url_prefix="/webhooks")

def _check_basic_auth():
    """Check for basic auth credentials in the request."""
    expected_username = os.getenv("PIPEDRIVE_WEBHOOK_USERNAME")
    expected_password = os.getenv("PIPEDRIVE_WEBHOOK_PASSWORD")

    auth = request.authorization

    return (
        expected_username 
        and expected_password
        and auth
        and auth.username == expected_username
        and auth.password == expected_password
    )

@webhooks_blueprint.post("/pipedrive")
def pipedrive_webhook():
    if not _check_basic_auth():
        return jsonify({"ok": False, "message": "Unauthorized"}), 401
    
    payload = request.get_json(silent=True) or {}

    print("="*60)
    print(json.dumps(payload, indent=2))
    print("="*60)

    data = payload.get("data", {})
    meta = payload.get("meta", {})

    if meta.get("entity") != "deal":
        return jsonify({
            "ok": True,
            "Ignored": True,
            "reason": "not_a_deal",
            "entity": meta.get("entity"),
        }), 200
    
    current_stage_id = data.get("stage_id")
    target_stage_id = int(os.getenv("PIPEDRIVE_R1_PRIS_STAGE_ID"))

    if current_stage_id != target_stage_id:
        return jsonify({
            "ok": True,
            "Ignored": True,
            "reason": "not_r1_pris_stage",
            "current_stage_id": current_stage_id,       
        }), 200
    
    deal_id = data.get("id")
    deal_title = data.get("title", "Unknown deal")
    person_id = data.get("person_id")
    org_id = data.get("org_id")
    owner_id = data.get("owner_id")

    message = (
        "New Appointment booked\n"
        f"Deal ID: {deal_id}\n"
        f"Deal Title: {deal_title}\n"
        f"Person ID: {person_id}\n"
        f"Organization ID: {org_id}\n"
        f"Owner ID: {owner_id}\n"
    )

    send_slack_message(message)

    return jsonify({
        "ok": True,
        "Ignored": False,
        "message": "Slack Notification sent successfully",
        "deal_id": data.get("id"),
        }), 200