# approval_callback.py - placeholder for handling approval responses
# This module provides a simple in-process mapping from approval tokens to actions.
# In production, approval replies will arrive via Telegram/webhook and should be
# routed to the agent's approval handler which then resumes execution.

from pathlib import Path
import json

APPROVAL_DB = Path(__file__).resolve().parent.parent / 'logs' / 'approvals_responses.json'
APPROVAL_DB.parent.mkdir(parents=True, exist_ok=True)


def record_response(request_id: str, responder: str, response: str) -> None:
    data = {}
    if APPROVAL_DB.exists():
        data = json.loads(APPROVAL_DB.read_text(encoding='utf-8'))
    data[request_id] = {
        'responder': responder,
        'response': response,
    }
    APPROVAL_DB.write_text(json.dumps(data, indent=2), encoding='utf-8')


def get_response(request_id: str):
    if not APPROVAL_DB.exists():
        return None
    data = json.loads(APPROVAL_DB.read_text(encoding='utf-8'))
    return data.get(request_id)


if __name__ == '__main__':
    print('approval_callback module (no-op CLI)')
