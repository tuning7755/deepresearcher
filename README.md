# Deep Research Agent

A deep research agent built on top of the `deepagents` module that performs comprehensive web research using the Claude Agent Skills standard.

## Overview

This agent leverages:
- **deepagents** module for core agent functionality
- **SkillsMiddleware** for Claude-standard skill support
- **web-research skill** for structured research methodology

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Deep Research Agent                           │
│                   (create_deep_agent)                           │
├─────────────────────────────────────────────────────────────────┤
│  Middleware Stack:                                              │
│  - SkillsMiddleware (Claude Agent Skills standard)              │
│  - TodoListMiddleware                                           │
│  - FilesystemMiddleware                                         │
│  - SubAgentMiddleware (parallel research)                       │
├─────────────────────────────────────────────────────────────────┤
│  Tools:                                                         │
│  - web_search (Tavily)                                          │
│  - fetch_url (deep dive into sources)                           │
│  - write_file, read_file, ls, glob, grep (filesystem)          │
│  - shell (directory operations)                                 │
│  - task (spawn parallel research subagents)                     │
├─────────────────────────────────────────────────────────────────┤
│  Skills (Claude Standard):                                      │
│  - web-research: Structured research methodology                │
│    (plan → delegate → synthesize)                               │
└─────────────────────────────────────────────────────────────────┘
```

## Claude Agent Skills Standard

Skills follow the Anthropic Agent Skills specification:

### Skill Structure
```
skills/
├── skill-name/
│   ├── SKILL.md        # Required: YAML frontmatter + instructions
│   └── helper.py       # Optional: supporting files
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
/workspace/root/deepresearcher/
├── __init__.py          # Package init
├── main.py              # CLI entry point
├── agent.py             # create_research_agent() 
├── prompts.py           # Base system prompt
├── tools.py             # web_search, fetch_url tools
├── requirements.txt     # Dependencies
├── README.md            # This file
└── skills/              # Skills directory (Claude standard)
    └── web-research/    # Copied from ~/.deepagents/agent/skills/
        └── SKILL.md
```

## Usage

```bash
# Run research on a topic
python main.py "What are the latest developments in quantum computing?"

# With custom output directory
python main.py "Research topic" --output ./my_research

# Interactive mode
python main.py --interactive
```

## Requirements

- Python 3.11+
- deepagents >= 0.2.8
- deepagents-cli >= 0.0.12
- tavily-python
- langchain, langgraph

## Installation

```bash
pip install -r requirements.txt
```

## Adding New Skills

Simply copy any Claude-standard skill directory to `skills/`:

```bash
cp -r ~/.deepagents/agent/skills/my-skill ./skills/
```

The skill will be automatically discovered and available to the agent.
