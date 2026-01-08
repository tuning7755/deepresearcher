# Implementation Plan (Reference)

## Goal
Build a Deep Research Agent that supports Claude Agent Skills and runs a structured research workflow with parallel subagents.

## Core Components
- `create_deep_agent()` from deepagents with filesystem, todos, and subagent support.
- SkillsMiddleware from deepagents-cli to load skills in `skills/`.
- Tool wrappers (`web_search`, `fetch_url`) in `tools.py`.

## Phases (Original)
1. Project setup and scaffolding.
2. Copy skills into `skills/`.
3. Implement tools module wrappers.
4. Define base system prompt.
5. Build agent creation with middleware and tools.
6. Add CLI entry point and modes.
7. Validate end-to-end flow.

## Skills Standard Summary
- `skills/<skill-name>/SKILL.md` must include YAML frontmatter with `name` and `description`.
- Skills are discovered at startup and loaded on demand (progressive disclosure).
- Subagents write findings to files; the main agent synthesizes a final report.
