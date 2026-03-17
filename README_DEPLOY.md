Deploy & Approval Flow — Summary

What we implemented:
- code-agent executor with dry-run and approval wait flow (tools/code_agent_executor.py)
- approval request logger and Telegram helper (tools/approval_telegram.py)
- approval response storage and callback helper (tools/approval_callback.py)
- minimal webhook receiver (tools/telegram_webhook.py) to accept Telegram callback_query
- summarize shim & web_fetch wrapper to use local Ollama model for summaries

Quick start (dev)
1. Ensure Python deps in .venv installed (requests, pytest, etc.).
2. Start webhook receiver:
   python3 tools/telegram_webhook.py 8080 &
3. Start ngrok (or provide public URL) and set Telegram webhook to https://<your_ngrok>/telegram_webhook
4. Use approval helper to send request:
   python3 tools/approval_telegram.py --title "Approve push" --body "..." --reqid REQ-XXXX
5. Approver clicks button (or replies with A/B/C mapped to Allow Once/Always/Deny), callback recorded in logs/approvals_responses.json
6. Executor polls get_response(request_id) and proceeds accordingly.

Security notes
- Keep bot token secret; use short-lived ngrok tunnels for testing.
- Validate callback payloads and tie request_ids to user/chat ids in production.
