# Approval Telegram helper (CLI)
# This is a helper script that formats approval requests. The actual send should be
# performed by the agent runtime using the platform's messaging tools (sessions_send).

import argparse
from pathlib import Path
from datetime import datetime

LOG = Path(__file__).resolve().parent.parent / "logs" / "approvals.log"
LOG.parent.mkdir(parents=True, exist_ok=True)

parser = argparse.ArgumentParser()
parser.add_argument('--title', required=True)
parser.add_argument('--body', required=True)
parser.add_argument('--level', choices=['low','medium','high'], default='high')
args = parser.parse_args()

entry = {
    'time': datetime.now().isoformat(),
    'title': args.title,
    'body': args.body,
    'level': args.level,
}
with LOG.open('a', encoding='utf-8') as fh:
    fh.write(str(entry) + '\n')

# Print a Telegram-ready payload (text + suggested reply tokens)
payload = f"APPROVAL REQUEST ({args.level.upper()})\n{args.title}\n\n{args.body}\n\nReply with: Allow Once / Allow Always / Deny"
print(payload)
