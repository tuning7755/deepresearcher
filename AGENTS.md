# Repository Guidelines

## Project Structure & Module Organization
- `src/deepresearcher/main.py` and `src/deepresearcher/__main__.py` provide the CLI entry points for running the agent.
- `src/deepresearcher/agent.py`, `src/deepresearcher/prompts.py`, and `src/deepresearcher/tools.py` hold core agent wiring, prompts, and tool definitions.
- `src/deepresearcher/skills/` contains Claude-style skills; each skill lives in its own folder with a `SKILL.md`.
- `requirements.txt` lists runtime dependencies.

## Build, Test, and Development Commands
- `pip install -r requirements.txt` installs dependencies for local development.
- `python main.py "Research topic"` runs a one-off research task (wrapper adds `src` to `PYTHONPATH`).
- `python main.py --interactive` starts interactive mode.
- `python main.py "Topic" --output ./my_research` writes outputs to a custom directory.

## Coding Style & Naming Conventions
- Python code follows PEP 8 with 4-space indentation.
- Use `snake_case` for functions/variables, `CapWords` for classes.
- Skill folders and `SKILL.md` metadata use lowercase names with hyphens (e.g., `web-research`).
- No formatter or linter is configured; keep diffs minimal and consistent with nearby code.

## Testing Guidelines
- No test suite is currently present.
- If adding tests, prefer `pytest` with `tests/` and names like `test_*.py`.
- Include a short note in PRs describing how you validated changes.

## Commit & Pull Request Guidelines
- Commit messages follow Conventional Commits (e.g., `feat(cli): add flag`, `docs: update README`).
- PRs should include a clear summary, rationale, and any new commands or flags.
- Link relevant issues and note test status or manual verification steps.

## Security & Configuration Tips
- Store API keys in environment variables (for example `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `TAVILY_API_KEY`).
- Do not commit credentials, generated research outputs, or local artifacts.
