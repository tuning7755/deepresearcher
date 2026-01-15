# Deep Research Agent

A deep research agent built on top of the `deepagents` module that performs comprehensive web research using the Claude Agent Skills standard.

## Overview

This agent leverages:
- **deepagents** module for core agent functionality
- **SkillsMiddleware** for Claude-standard skill support
- **web-research skill** for structured research methodology

## Product Requirements (Web UI)

Goal: provide a FastAPI-powered web experience where users can start a research task, chat with the agent, and watch the research process unfold live.

Key interaction layout:
- Left panel: user chat window, input a research topic, ask follow-up questions, and view assistant replies.
- Right panel: real-time research process, including intermediate activities and the final report.
- Two primary tabs on the right: `Activities` (streaming steps, sources, artifacts) and `Report` (final structured output).

Expected behavior:
- The research run starts from a single user question and can continue as a conversation.
- The right panel updates while the agent is working; the final report remains accessible and scrollable.
- The UI prioritizes clarity: progress first, report second, with minimal friction to switch between them.


## Architecture

```
┌─────────────────────────────────────────────────────────────────�?
�?                   Deep Research Agent                           �?
�?                  (create_deep_agent)                           �?
├─────────────────────────────────────────────────────────────────�?
�? Middleware Stack:                                              �?
�? - SkillsMiddleware (Claude Agent Skills standard)              �?
�? - TodoListMiddleware                                           �?
�? - FilesystemMiddleware                                         �?
�? - SubAgentMiddleware (parallel research)                       �?
├─────────────────────────────────────────────────────────────────�?
�? Tools:                                                         �?
�? - web_search (Tavily)                                          �?
�? - fetch_url (deep dive into sources)                           �?
�? - write_file, read_file, ls, glob, grep (filesystem)          �?
�? - shell (directory operations)                                 �?
�? - task (spawn parallel research subagents)                     �?
├─────────────────────────────────────────────────────────────────�?
�? Skills (Claude Standard):                                      �?
�? - web-research: Structured research methodology                �?
�?   (plan �?delegate �?synthesize)                               �?
└─────────────────────────────────────────────────────────────────�?
```

## Claude Agent Skills Standard

Skills follow the Anthropic Agent Skills specification:

### Skill Structure
```
skills/
├── skill-name/
�?  ├── SKILL.md        # Required: YAML frontmatter + instructions
�?  └── helper.py       # Optional: supporting files
```

### SKILL.md Format
```markdown
---
name: skill-name          # Required: lowercase, alphanumeric, hyphens only (max 64 chars)
description: What it does # Required: max 1024 chars
license: MIT              # Optional
compatibility: python3    # Optional
allowed-tools: web_search # Optional
---

# Skill Instructions

Markdown content the agent reads when using the skill...
```

### How Skills Work (Progressive Disclosure)
1. **SkillsMiddleware** scans skills directory at session start
2. Parses YAML frontmatter from each `SKILL.md`
3. Injects skill names + descriptions into system prompt
4. Agent uses `read_file` to read full `SKILL.md` when needed

## Research Workflow (from web-research skill)

1. **Create research folder** - `research_[topic_name]/`
2. **Write research plan** - `research_plan.md` with subtopics
3. **Spawn parallel subagents** - Each researches one subtopic
4. **Subagents write findings** - `findings_[subtopic].md`
5. **Synthesize final report** - `research_report.md`

## Project Structure

```
/workspace/root/
|-- src/
|   `-- deepresearcher/
|       |-- __init__.py
|       |-- __main__.py
|       |-- main.py           # CLI entry point (package)
|       |-- agent.py          # create_research_agent()
|       |-- prompts.py        # Base system prompt
|       |-- tools.py          # web_search, fetch_url tools
|       |-- api/              # FastAPI + SSE backend
|       |   `-- app.py
|       |-- web/              # Web UI assets
|       |   |-- index.html
|       |   `-- static/
|       |       |-- app.js
|       |       `-- styles.css
|       |-- skills/           # Skills directory (Claude standard)
|       |   `-- web-research/
|       |       `-- SKILL.md
|       `-- knowledge/
|-- main.py                   # CLI wrapper for src layout
|-- requirements.txt
`-- README.md
```


## Usage

```bash
# Run research on a topic
python main.py "What are the latest developments in quantum computing?"

# With custom output directory
python main.py "Research topic" --output ./my_research

# Interactive mode
python main.py --interactive

# Or run as a module (ensure src is on PYTHONPATH)
PYTHONPATH=src python -m deepresearcher "Research topic"

# Or run the web UI (FastAPI)
PYTHONPATH=src uvicorn deepresearcher.api.app:app --reload
```

## Manual Verification

- Run `python main.py --interactive` and confirm the CLI responds.
- Run `PYTHONPATH=src uvicorn deepresearcher.api.app:app --reload` and open `http://127.0.0.1:8000`.
- Submit a topic and confirm chat, activities, and report updates.

## Requirements

- Python 3.11+
- deepagents >= 0.2.8
- deepagents-cli >= 0.0.12
- tavily-python
- langchain, langgraph
- fastapi
- uvicorn

## Installation

```bash
pip install -r requirements.txt
```

## Adding New Skills

Simply copy any Claude-standard skill directory to `skills/`:

```bash
cp -r ~/.deepagents/agent/skills/my-skill ./src/deepresearcher/skills/
```

The skill will be automatically discovered and available to the agent.



## User Stories & Acceptance Criteria

User stories:
- As a user, I can start a research task by entering a topic and see the agent respond in the left chat panel.
- As a user, I can watch the research process unfold in real time on the right, without interrupting the chat.
- As a user, I can switch between Activities and Report to review progress or the final deliverable.
- As a user, I can continue asking follow-up questions and keep a single research thread.

Acceptance criteria:
- The UI renders a two-column layout: chat on the left, research process on the right.
- The right panel streams intermediate steps while the agent is running and shows the final report when ready.
- The Activities and Report tabs are both accessible; switching does not reset ongoing progress.
- The chat input remains available during research, and new messages continue the same session.
