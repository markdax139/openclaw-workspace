#!/usr/bin/env python3
"""Executor skeleton for code-automation-agent.

Responsibilities:
- Validate requested action against allowlists
- Produce dry-run outputs (diffs, test summaries)
- Request approvals for high-risk actions via Telegram
- Execute approved actions and collect artifacts
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import List

ALLOWLIST_DIR = Path(__file__).resolve().parent / "allowlists"


def load_allowlist(name: str) -> List[str]:
    path = ALLOWLIST_DIR / f"{name}.yml"
    if not path.exists():
        return []
    import yaml
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    # naive flatten
    commands = []
    for k, v in (data or {}).items():
        if isinstance(v, list):
            for item in v:
                commands.append(str(item))
    return commands


def run_dry_run(repo_path: str, action: str, args: dict) -> dict:
    """Generate dry-run artifacts depending on action.
    Supported actions: run-tests, dry-push, commit-preview
    """
    repo = Path(repo_path)
    if not repo.exists():
        return {"status": "error", "details": "repo path not found"}

    if action == "run-tests":
        # run pytest in dry mode (no changes)
        cmd = ["python3", "-m", "pytest", "-q"]
        try:
            completed = subprocess.run(cmd, cwd=str(repo), capture_output=True, text=True, timeout=120)
            return {"status": "dry-run", "type": "tests", "returncode": completed.returncode, "stdout": completed.stdout[:10000], "stderr": completed.stderr[:2000]}
        except Exception as exc:
            return {"status": "error", "details": str(exc)}

    if action == "dry-push":
        # produce a git diff against origin/main (no network changes)
        try:
            diff_cmd = ["git", "fetch", "origin"]
            subprocess.run(diff_cmd, cwd=str(repo), check=False, capture_output=True, text=True, timeout=60)
            diff_cmd = ["git", "diff", "origin/main..HEAD"]
            completed = subprocess.run(diff_cmd, cwd=str(repo), capture_output=True, text=True, timeout=30)
            diff_preview = completed.stdout[:20000]
            return {"status": "dry-run", "type": "diff", "diff": diff_preview}
        except Exception as exc:
            return {"status": "error", "details": str(exc)}

    if action == "commit-preview":
        try:
            cmd = ["git", "diff", "--staged"]
            completed = subprocess.run(cmd, cwd=str(repo), capture_output=True, text=True, timeout=30)
            return {"status": "dry-run", "type": "staged_diff", "diff": completed.stdout[:20000]}
        except Exception as exc:
            return {"status": "error", "details": str(exc)}

    return {"status": "error", "details": f"unknown action {action}"}


import uuid
import time
from tools.approval_callback import record_response, get_response
from pathlib import Path as _Path


def request_and_wait_approval(title: str, body: str, timeout: int = 300) -> str:
    """Create an approval request and wait (poll) for a response in logs.
    Returns the response string (Allow Once / Allow Always / Deny) or empty if timed out.
    """
    request_id = f"REQ-{uuid.uuid4().hex[:8]}"
    # log the request via approval_telegram helper (include request_id)
    from subprocess import run
    run([
        "python3",
        str(Path(__file__).resolve().parent / 'approval_telegram.py'),
        "--title",
        title,
        "--body",
        body,
        "--reqid",
        request_id,
    ])

    # Poll for a response
    started = time.time()
    while time.time() - started < timeout:
        resp = get_response(request_id)
        if resp:
            return resp.get('response')
        time.sleep(2)
    return ""


def execute_action(repo_path: str, action: str, args: dict) -> dict:
    """Execute approved action. This function MUST be called only after explicit approval.
    Implementations must validate against allowlists (omitted here for brevity).
    """
    repo = Path(repo_path)
    if action == "run-tests":
        cmd = ["python3", "-m", "pytest", "-q"]
        completed = subprocess.run(cmd, cwd=str(repo), capture_output=True, text=True)
        return {"status": "success" if completed.returncode==0 else "failed", "stdout": completed.stdout[:10000], "stderr": completed.stderr[:2000]}

    if action == "commit-preview":
        # actually commit staged changes with provided message
        message = args.get("message", "[auto] commit")
        cmd = ["git", "commit", "-m", message]
        completed = subprocess.run(cmd, cwd=str(repo), capture_output=True, text=True)
        return {"status": "success" if completed.returncode==0 else "failed", "stdout": completed.stdout, "stderr": completed.stderr}

    if action == "push":
        branch = args.get("branch", "HEAD")
        cmd = ["git", "push", "origin", branch]
        completed = subprocess.run(cmd, cwd=str(repo), capture_output=True, text=True)
        return {"status": "success" if completed.returncode==0 else "failed", "stdout": completed.stdout, "stderr": completed.stderr}

    return {"status": "error", "details": f"unknown action {action}"}


if __name__ == "__main__":
    # simple CLI for local testing
    if len(sys.argv) < 3:
        print("Usage: code_agent_executor.py <repo_path> <action>")
        sys.exit(1)
    repo = sys.argv[1]
    action = sys.argv[2]
    import json
    print(json.dumps(run_dry_run(repo, action, {}), indent=2))


if __name__ == "__main__":
    # simple CLI for local testing
    if len(sys.argv) < 3:
        print("Usage: code_agent_executor.py <repo_path> <action>")
        sys.exit(1)
    repo = sys.argv[1]
    action = sys.argv[2]
    import json
    print(json.dumps(run_dry_run(repo, action, {}), indent=2))
