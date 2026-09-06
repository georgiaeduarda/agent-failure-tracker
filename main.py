```python
"""
Agent Failure Tracker
Scrapes recent issues from AI agent frameworks (CrewAI, LangGraph, AutoGen)
to detect production failures, traces, and edge-case bugs for developer teardowns.
"""

import argparse
import json
import os
import sys
from datetime import datetime
import requests

GITHUB_API_URL = "https://api.github.com"
DEFAULT_TARGET_REPOS = [
    "crewAIInc/crewAI",
    "langchain-ai/langgraph"
]

FAILURE_KEYWORDS = [
    "infinite loop",
    "hallucination",
    "token limit",
    "timeout",
    "traceback",
    "context overflow",
    "tool error"
]


def fetch_recent_issues(repo: str, token: str = None) -> list:
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    url = f"{GITHUB_API_URL}/repos/{repo}/issues"
    params = {"state": "open", "per_page": 30, "sort": "created", "direction": "desc"}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[!] Error fetching data for {repo}: {e}", file=sys.stderr)
        return []


def analyze_issue(issue: dict) -> dict:
    title = issue.get("title", "")
    body = issue.get("body", "") or ""
    combined_text = f"{title} {body}".lower()

    detected_signatures = [kw for kw in FAILURE_KEYWORDS if kw in combined_text]

    return {
        "id": issue.get("id"),
        "number": issue.get("number"),
        "title": title,
        "url": issue.get("html_url"),
        "created_at": issue.get("created_at"),
        "has_stacktrace": "traceback" in combined_text or "error:" in combined_text,
        "detected_failure_types": detected_signatures,
        "is_production_leak": len(detected_signatures) > 0
    }


def main():
    parser = argparse.ArgumentParser(description="Track production agent failure signatures.")
    parser.add_argument("--repo", type=str, help="Specific repo (e.g. langchain-ai/langgraph)")
    parser.add_argument("--output", type=str, default="agent_failures.json", help="Output JSON path")
    args = parser.parse_args()

    repos_to_scan = [args.repo] if args.repo else DEFAULT_TARGET_REPOS
    github_token = os.getenv("GITHUB_TOKEN")

    results = {}

    for repo in repos_to_scan:
        print(f"[*] Scanning {repo} for failure traces...")
        raw_issues = fetch_recent_issues(repo, token=github_token)
        analyzed = [analyze_issue(i) for i in raw_issues if not i.get("pull_request")]
        flagged = [i for i in analyzed if i["is_production_leak"]]

        results[repo] = {
            "scanned_count": len(analyzed),
            "flagged_failures": len(flagged),
            "issues": flagged
        }
        print(f"    Found {len(flagged)} high-signal agent failures.")

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.utcnow().isoformat(),
            "data": results
        }, f, indent=2)

    print(f"\n[+] Report exported to {args.output}")


if __name__ == "__main__":
    main()
