# Deep Research Agent - Implementation Plan

## Goal

Build a Deep Research Agent using the `deepagents` module that:
1. Supports Claude Agent Skills standard (just copy skill files to use them)
2. Uses the `web-research` skill for structured research methodology
3. Performs comprehensive web research with parallel subagents

## Tech Stack

- **deepagents** (0.2.8) - Core agent framework with `create_deep_agent()`
- **deepagents-cli** (0.0.12) - Skills middleware, tools (web_search, fetch_url)
- **langgraph** - Agent orchestration
- **langchain** - LLM integration
- **tavily-python** - Web search API

## Key Components from deepagents

### From `deepagents` module:
- `create_deep_agent()` - Creates agent with filesystem, todos, subagents
- `FilesystemMiddleware` - File operations (read, write, edit, ls, glob, grep)
- `SubAgentMiddleware` - Spawn parallel subagents via `task` tool

### From `deepagents_cli` module:
- `SkillsMiddleware` - Claude Agent Skills standard support
- `web_search()` - Tavily web search tool
- `fetch_url()` - Fetch and convert URLs to markdown
- `ShellMiddleware` - Shell command execution

## Implementation Phases

### Phase 1: Project Setup
- [x] Create project directory structure
- [x] Write README.md with architecture overview
- [x] Write PLAN.md (this file)
- [ ] Create requirements.txt
- [ ] Create __init__.py

### Phase 2: Copy Skills
- [ ] Create skills/ directory
- [ ] Copy web-research skill from ~/.deepagents/agent/skills/

### Phase 3: Tools Module
- [ ] Create tools.py
- [ ] Wrap web_search from deepagents_cli.tools
- [ ] Wrap fetch_url from deepagents_cli.tools

### Phase 4: Prompts Module
- [ ] Create prompts.py
- [ ] Write RESEARCH_SYSTEM_PROMPT (base instructions for deep research)

### Phase 5: Agent Module
- [ ] Create agent.py
- [ ] Implement create_research_agent() function
- [ ] Configure SkillsMiddleware for skills/ directory
- [ ] Configure tools (web_search, fetch_url)
- [ ] Use create_deep_agent() with custom middleware

### Phase 6: CLI Entry Point
- [ ] Create main.py
- [ ] Implement CLI argument parsing
- [ ] Implement interactive mode
- [ ] Implement single-query mode

### Phase 7: Testing
- [ ] Test skill loading
- [ ] Test web search functionality
- [ ] Test end-to-end research workflow
- [ ] Test parallel subagent execution

## File Specifications

### requirements.txt
```
deepagents>=0.2.8
deepagents-cli>=0.0.12
tavily-python>=0.7.0
langchain>=1.0.0
langgraph>=1.0.0
```

### tools.py
```python
# Wrap web_search and fetch_url from deepagents_cli.tools
# These tools will be passed to create_deep_agent()
```

### prompts.py
```python
RESEARCH_SYSTEM_PROMPT = """
You are a Deep Research Agent specialized in conducting comprehensive research.

When given a research topic:
1. Check available skills (especially web-research skill)
2. Read the skill instructions
3. Follow the structured research methodology
4. Produce well-sourced reports with citations
...
"""
```

### agent.py
```python
from deepagents import create_deep_agent
from deepagents_cli.skills import SkillsMiddleware
from .tools import web_search, fetch_url
from .prompts import RESEARCH_SYSTEM_PROMPT

def create_research_agent(
    model: str = "anthropic:claude-sonnet-4-5-20250929",
    skills_dir: str = "./skills",
    ...
) -> CompiledStateGraph:
    # Configure SkillsMiddleware
    # Configure tools
    # Call create_deep_agent()
    pass
```

### main.py
```python
# CLI entry point
# Parse arguments
# Create agent
# Run research query
# Display results
```

## Claude Agent Skills Standard Summary

### Directory Structure
```
skills/
└── skill-name/
    ├── SKILL.md      # Required: YAML frontmatter + markdown instructions
    └── *.py          # Optional: supporting scripts
```

### SKILL.md Format
```markdown
---
name: skill-name          # Required: matches directory name
description: What it does # Required: shown in system prompt
---

# Full Instructions

Agent reads this via read_file when skill is relevant...
```

### How SkillsMiddleware Works
1. Scans skills_dir for subdirectories with SKILL.md
2. Parses YAML frontmatter (name, description)
3. Injects skill list into system prompt
4. Agent uses read_file to get full instructions (progressive disclosure)

## Notes

- Skills are self-documenting: just copy the skill folder
- Parallel subagents via `task` tool for efficient research
- File-based communication: subagents write findings to files
- Progressive disclosure: agent reads full skill only when needed
