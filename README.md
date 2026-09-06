# Agent Failure Tracker

A lightweight CLI pipeline designed to scrape, surface, and categorize production failure signatures (tracebacks, infinite loops, context overflow, and tool call timeouts) from open-source agent frameworks (e.g., LangGraph, CrewAI).

Built to feed real developer postmortems, root-cause analyses, and signal-driven GTM pipelines.

## Motivation
Most agent failures in production happen silently or get lost in verbose runtime logs. This tool scans active framework repositories to detect where developers are breaking multi-agent systems, extracting reproducible bugs to document root causes and evaluate runtime fixes.

## Quickstart

```bash
# Clone the repository
git clone [https://github.com/georgiaeduarda/agent-failure-tracker.git](https://github.com/georgiaeduarda/agent-failure-tracker.git)
cd agent-failure-tracker

# Install dependencies
pip install -r requirements.txt

# Run the tracker across default frameworks
python main.py

# Or target a specific repository
python main.py --repo langchain-ai/langgraph --output langgraph_failures.json
{
  "timestamp": "2026-09-06T03:45:00Z",
  "data": {
    "langchain-ai/langgraph": {
      "scanned_count": 30,
      "flagged_failures": 4,
      "issues": [
        {
          "number": 1420,
          "title": "RecursionError when tool returns empty payload in recursive graph",
          "url": "[https://github.com/langchain-ai/langgraph/issues/1420](https://github.com/langchain-ai/langgraph/issues/1420)",
          "has_stacktrace": true,
          "detected_failure_types": ["infinite loop", "traceback"]
        }
      ]
    }
  }
}
