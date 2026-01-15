# Project Overview

## Purpose
Deep Research Agent is a Python CLI that runs structured, multi-source web research using the deepagents framework and Claude Agent Skills. It emphasizes parallel subagents and a repeatable research workflow.

## Key Capabilities
- Runs one-off or interactive research sessions.
- Loads Claude-standard skills from `skills/` at startup.
- Uses `web_search` and `fetch_url` tools for discovery and source capture.
- Writes research outputs to a topic folder (plan, findings, report).

## Architecture Notes
- Entry points: `main.py` (CLI), `__main__.py` (module execution).
- Core wiring: `agent.py` (agent creation), `prompts.py` (system prompt), `tools.py` (tool wrappers).
- Skills: `skills/<skill-name>/SKILL.md` with YAML frontmatter and instructions.

## Typical Usage
- `python main.py "Research topic"`
- `python main.py --interactive`
- `python main.py "Topic" --output ./my_research`
