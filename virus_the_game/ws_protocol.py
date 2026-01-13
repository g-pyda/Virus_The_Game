import json
from typing import Any, Dict, Tuple, Optional


class WsProtocolError(ValueError):
    pass


def parse_incoming(text_data: str) -> Tuple[str, str, Dict[str, Any], Optional[str]]:
    """
    Supports two formats:
    1) New (documented):
        {"sender": "...", "header": "...", "data": {...}, "request_id": "...?"}

    2) Legacy (current frontend-ish):
        {"action": "...", ...other fields...}

    Returns: (sender, header, data, request_id)
    """
    try:
        payload = json.loads(text_data)
    except Exception as e:
        raise WsProtocolError(f"Invalid JSON: {e}")

    if not isinstance(payload, dict):
        raise WsProtocolError("Payload must be a JSON object")

    # --- New format ---
    if "header" in payload:
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

    # --- Legacy format ---
    action = payload.get("action")
    if not isinstance(action, str) or not action:
        raise WsProtocolError("Missing/invalid 'action' (legacy) or 'header' (new)")

    # Minimal legacy mapping:
    # - If it's clearly turn end
    if action in ("end_turn", "turn_end"):
        return "frontend", "turn_end", {"action": "end_turn"}, None

    # - Otherwise treat as card play intent (your current receive builds attempt_info from these fields)
    # Keep original fields so your handler can reuse them.
    return "frontend", "card_play", payload, None


def build_message(sender: str, header: str, data: Dict[str, Any], request_id: Optional[str] = None) -> str:
    msg = {"sender": sender, "header": header, "data": data}
    if request_id:
        msg["request_id"] = request_id
    return json.dumps(msg)


def build_attempt(status: bool, message: str = "", request_id: Optional[str] = None) -> str:
    data = {"status": status, "message": message}
    return build_message("lobby", "attempt", data, request_id=request_id)
