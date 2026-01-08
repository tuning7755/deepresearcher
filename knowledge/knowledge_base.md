# Deepresearcher Knowledge Base

## Project Overview
Deep Research Agent is a Python CLI that runs structured, multi-source web research using the deepagents framework and Claude Agent Skills. It emphasizes parallel subagents and a repeatable research workflow.

### Key Capabilities
- Runs one-off or interactive research sessions.
- Loads Claude-standard skills from `skills/` at startup.
- Uses `web_search` and `fetch_url` tools for discovery and source capture.
- Writes research outputs to a topic folder (plan, findings, report).

### Architecture Notes
- Entry points: `main.py` (CLI), `__main__.py` (module execution).
- Core wiring: `agent.py` (agent creation), `prompts.py` (system prompt), `tools.py` (tool wrappers).
- Skills: `skills/<skill-name>/SKILL.md` with YAML frontmatter and instructions.

### Typical Usage
- `python main.py "Research topic"`
- `python main.py --interactive`
- `python main.py "Topic" --output ./my_research`

## Dependencies and Runtime

### Runtime Requirements
- Python 3.11+
- deepagents >= 0.2.8
- deepagents-cli >= 0.0.12
- tavily-python >= 0.7.0
- langchain >= 1.0.0
- langgraph >= 1.0.0
- langchain-openai >= 1.0.0
- langchain-anthropic >= 1.0.0

### Install
- `pip install -r requirements.txt`

### External Services
- Tavily for web search via `web_search`.
- LLM backends via LangChain providers (OpenAI, Anthropic).

### Configuration Tips
- Use environment variables for API keys (e.g., `TAVILY_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`).
- Keep generated research output and local artifacts out of version control.

## Implementation Plan (Reference)

### Goal
Build a Deep Research Agent that supports Claude Agent Skills and runs a structured research workflow with parallel subagents.

### Core Components
- `create_deep_agent()` from deepagents with filesystem, todos, and subagent support.
- SkillsMiddleware from deepagents-cli to load skills in `skills/`.
- Tool wrappers (`web_search`, `fetch_url`) in `tools.py`.

### Phases (Original)
1. Project setup and scaffolding.
2. Copy skills into `skills/`.
3. Implement tools module wrappers.
4. Define base system prompt.
5. Build agent creation with middleware and tools.
6. Add CLI entry point and modes.
7. Validate end-to-end flow.

### Skills Standard Summary
- `skills/<skill-name>/SKILL.md` must include YAML frontmatter with `name` and `description`.
- Skills are discovered at startup and loaded on demand (progressive disclosure).
- Subagents write findings to files; the main agent synthesizes a final report.
