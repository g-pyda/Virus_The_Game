import json
from typing import Any, Dict, Tuple, Optional, Union


class WsProtocolError(ValueError):
    pass


Envelope = Dict[str, Any]


def _validate_envelope(payload: Dict[str, Any]) -> Tuple[str, str, Dict[str, Any], Optional[str]]:
    sender = payload.get("sender")
    header = payload.get("header")
    data = payload.get("data", {})
    request_id = payload.get("request_id")

    if not isinstance(sender, str) or not sender:
        raise WsProtocolError("Missing/invalid 'sender'")
    if not isinstance(header, str) or not header:
        raise WsProtocolError("Missing/invalid 'header'")
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise WsProtocolError("'data' must be a JSON object")
    if request_id is not None and not isinstance(request_id, str):
        raise WsProtocolError("'request_id' must be a string")

    return sender, header, data, request_id


def parse_incoming(text_data: str) -> Tuple[str, str, Dict[str, Any], Optional[str]]:
    """
    Supports two formats:
    1) New (documented):
        {"sender": "...", "header": "...", "data": {...}, "request_id": "...?"}

    2) Legacy:
        {"action": "...", ...other fields...}

    Returns: (sender, header, data, request_id)
    """
    try:
        payload = json.loads(text_data)
    except Exception as e:
        raise WsProtocolError(f"Invalid JSON: {e}")

    if not isinstance(payload, dict):
        raise WsProtocolError("Payload must be a JSON object")

    # New format
    if "header" in payload:
        return _validate_envelope(payload)

    # Legacy format
    action = payload.get("action")
    if not isinstance(action, str) or not action:
        raise WsProtocolError("Missing/invalid 'action' (legacy) or 'header' (new)")

    if action in ("end_turn", "turn_end"):
        return "frontend", "turn_end", {"action": "end_turn"}, None

    # Everything else: treat as a card_play and keep fields intact
    return "frontend", "card_play", payload, None


def parse_payload(payload: Envelope) -> Tuple[str, str, Dict[str, Any], Optional[str]]:
    """
    Like parse_incoming, but for already-decoded dict payloads (internal messages).
    """
    if not isinstance(payload, dict):
        raise WsProtocolError("Internal payload must be a dict")
    if "header" not in payload:
        raise WsProtocolError("Internal payload must contain 'header'")
    return _validate_envelope(payload)


def build_envelope(sender: str, header: str, data: Dict[str, Any], request_id: Optional[str] = None) -> Envelope:
    env: Envelope = {"sender": sender, "header": header, "data": data}
    if request_id is not None:
        env["request_id"] = request_id
    return env


def build_message(sender: str, header: str, data: Dict[str, Any], request_id: Optional[str] = None) -> str:
    return json.dumps(build_envelope(sender, header, data, request_id=request_id))


def build_attempt(status: bool, message: str = "", request_id: Optional[str] = None) -> str:
    data = {"status": status, "message": message}
    return build_message("lobby", "attempt", data, request_id=request_id)
