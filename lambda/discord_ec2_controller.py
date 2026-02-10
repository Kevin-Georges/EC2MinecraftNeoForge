import os
import json
import boto3
import nacl.signing
import nacl.exceptions

INSTANCE_ID = os.environ["INSTANCE_ID"]
AWS_REGION = os.environ.get("AWS_REGION", "eu-west-2")
DISCORD_PUBLIC_KEY = os.environ["DISCORD_PUBLIC_KEY"]  # from Discord Developer Portal

ec2 = boto3.client("ec2", region_name=AWS_REGION)

def _lower_headers(event):
    h = event.get("headers") or {}
    return {k.lower(): v for k, v in h.items()}

def _verify_discord_signature(event):
    headers = _lower_headers(event)
    sig = headers.get("x-signature-ed25519")
    ts = headers.get("x-signature-timestamp")
    body = event.get("body") or ""

    if not sig or not ts:
        return False

    message = (ts + body).encode("utf-8")
    signature_bytes = bytes.fromhex(sig)

    verify_key = nacl.signing.VerifyKey(bytes.fromhex(DISCORD_PUBLIC_KEY))
    try:
        verify_key.verify(message, signature_bytes)
        return True
    except nacl.exceptions.BadSignatureError:
        return False

def _get_state():
    resp = ec2.describe_instances(InstanceIds=[INSTANCE_ID])
    return resp["Reservations"][0]["Instances"][0]["State"]["Name"]

def _discord_response(content: str):
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"type": 4, "data": {"content": content}})
    }

def lambda_handler(event, context):
    # Discord will reject if signature is not verified
    if not _verify_discord_signature(event):
        return {"statusCode": 401, "body": "invalid request signature"}

    body = json.loads(event.get("body") or "{}")
    t = body.get("type")

    # PING
    if t == 1:
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"type": 1})
        }

    # Slash command invocation
    if t == 2:
        name = (body.get("data") or {}).get("name")
        state = _get_state()

        if name == "status":
            emoji = {"running": "🟢", "stopped": "🔴", "pending": "🟡", "stopping": "🟡"}.get(state, "⚪")
            return _discord_response(f"{emoji} EC2 status: **{state}**")

        if name == "start":
            if state == "stopped":
                ec2.start_instances(InstanceIds=[INSTANCE_ID])
                return _discord_response("🚀 Server starting. Join in ~1–2 minutes.")
            if state == "running":
                return _discord_response("🟢 Server already running.")
            return _discord_response(f"⚠️ Server is currently **{state}**.")

        return _discord_response("Unknown command.")

    return {"statusCode": 400, "body": "unsupported request"}
