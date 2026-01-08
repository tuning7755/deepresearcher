"""Deep Research Agent creation and configuration."""

import os
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend
from deepagents.backends.filesystem import FilesystemBackend
from langchain_core.language_models import BaseChatModel
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.state import CompiledStateGraph

from deepagents_cli.skills import SkillsMiddleware
from deepagents_cli.shell import ShellMiddleware

from deepresearcher.prompts import RESEARCH_SYSTEM_PROMPT
from deepresearcher.tools import RESEARCH_TOOLS


def get_base_system_prompt(working_dir: Path, skills_dir: Path) -> str:
    """Generate the base system prompt with environment info."""
    return f"""<env>
Working directory: {working_dir}
Skills directory: {skills_dir}
</env>

### File System and Paths

**IMPORTANT - Path Handling:**
- All file paths must be absolute paths (e.g., `{working_dir}/file.txt`)
- Use the working directory from <env> to construct absolute paths
- Research outputs should go in `{working_dir}/research_[topic]/`

### Web Search Tool Usage

When you use the web_search tool:
1. The tool will return search results with titles, URLs, and content excerpts
2. Read and process these results, then respond naturally
3. Synthesize information from multiple sources into a coherent answer
4. Cite sources by mentioning page titles or URLs when relevant

{RESEARCH_SYSTEM_PROMPT}
"""


def create_research_agent(
    model: str | BaseChatModel | None = None,
    *,
    working_dir: str | Path | None = None,
    skills_dir: str | Path | None = None,
    auto_approve: bool = True,
) -> tuple[CompiledStateGraph, CompositeBackend]:
    """Create a Deep Research Agent.

    Args:
        model: LLM model to use. Defaults to environment config or Claude Sonnet.
        working_dir: Working directory for research outputs. Defaults to current directory.
        skills_dir: Directory containing skills. Defaults to ./skills relative to this module.
        auto_approve: If True, auto-approve all tool calls. Defaults to True for research.

    Returns:
        Tuple of (agent, backend) - the compiled agent and its filesystem backend.
    """
    if model is None:
        openai_model = os.environ.get("OPENAI_MODEL")
        if os.environ.get("OPENAI_API_KEY") or openai_model:
            model = f"openai:{openai_model or 'gpt-4o-mini'}"
        elif os.environ.get("ANTHROPIC_API_KEY"):
            model = "anthropic:claude-sonnet-4-5-20250929"
    if working_dir is None:
        working_dir = Path.cwd()
    else:
        working_dir = Path(working_dir).resolve()

    if skills_dir is None:
        skills_dir = Path(__file__).parent / "skills"
    else:
        skills_dir = Path(skills_dir).resolve()

    skills_dir.mkdir(parents=True, exist_ok=True)

    backend = CompositeBackend(
        default=FilesystemBackend(),
        routes={},
    )

    shell_env = os.environ.copy()
    middleware = [
        SkillsMiddleware(
            skills_dir=skills_dir,
            assistant_id="deep-researcher",
        ),
        ShellMiddleware(
            workspace_root=str(working_dir),
            env=shell_env,
        ),
    ]

    system_prompt = get_base_system_prompt(working_dir, skills_dir)

    interrupt_on = {} if auto_approve else None

    agent = create_deep_agent(
        model=model,
        system_prompt=system_prompt,
        tools=RESEARCH_TOOLS,
        backend=backend,
        middleware=middleware,
        interrupt_on=interrupt_on,
        checkpointer=InMemorySaver(),
    )

    return agent, backend
