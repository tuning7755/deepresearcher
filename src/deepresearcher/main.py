#!/usr/bin/env python3
"""Deep Research Agent CLI entry point."""

import argparse
import sys
import uuid
from pathlib import Path

from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

from deepresearcher.agent import create_research_agent


def _iter_messages(node_output: dict | None) -> list:
    """Normalize message updates from langgraph stream events."""
    if not node_output:
        return []
    messages = node_output.get("messages")
    if messages is None:
        return []
    if isinstance(messages, (list, tuple)):
        return list(messages)
    # Handle langgraph Update types like Overwrite(value=[...]).
    value = getattr(messages, "value", None)
    if value is not None:
        return list(value) if isinstance(value, (list, tuple)) else [value]
    return [messages]


def run_research(query: str, working_dir: Path, model: str | None = None) -> None:
    """Run a research query and stream the output."""
    print(f"\n🔬 Starting research on: {query}\n")
    print(f"📁 Working directory: {working_dir}\n")
    print("-" * 60)

    agent, _ = create_research_agent(
        model=model,
        working_dir=working_dir,
        auto_approve=True,
    )

    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    for event in agent.stream(
        {"messages": [HumanMessage(content=query)]},
        config=config,
        stream_mode="updates",
    ):
        for node_name, node_output in event.items():
            if node_name == "__interrupt__":
                continue
            for msg in _iter_messages(node_output):
                if hasattr(msg, "content") and msg.content:
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        continue
                    print(f"\n{msg.content}")

    print("\n" + "-" * 60)
    print("✅ Research complete!")


def interactive_mode(working_dir: Path, model: str | None = None) -> None:
    """Run in interactive mode with multiple queries."""
    print("\n🔬 Deep Research Agent - Interactive Mode")
    print("Type 'quit' or 'exit' to end the session.\n")

    agent, _ = create_research_agent(
        model=model,
        working_dir=working_dir,
        auto_approve=True,
    )

    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    while True:
        try:
            query = input("\n📝 Research query: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye!")
            break

        if not query:
            continue
        if query.lower() in ("quit", "exit"):
            print("\nGoodbye!")
            break

        print("\n" + "-" * 60)

        for event in agent.stream(
            {"messages": [HumanMessage(content=query)]},
            config=config,
            stream_mode="updates",
        ):
            for node_name, node_output in event.items():
                if node_name == "__interrupt__":
                    continue
                for msg in _iter_messages(node_output):
                    if hasattr(msg, "content") and msg.content:
                        if hasattr(msg, "tool_calls") and msg.tool_calls:
                            continue
                        print(f"\n{msg.content}")

        print("\n" + "-" * 60)


def main() -> int:
    """Main entry point."""
    load_dotenv()
    parser = argparse.ArgumentParser(
        description="Deep Research Agent - Comprehensive web research powered by AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m deepresearcher "What are the latest developments in quantum computing?"
  python -m deepresearcher --interactive
  python -m deepresearcher "Research topic" --output ./my_research
        """,
    )

    parser.add_argument(
        "query",
        nargs="?",
        help="Research query to investigate",
    )

    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Run in interactive mode",
    )

    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=Path.cwd(),
        help="Output directory for research files (default: current directory)",
    )

    parser.add_argument(
        "-m", "--model",
        type=str,
        default=None,
        help="LLM model to use (default: from environment or Claude Sonnet)",
    )

    args = parser.parse_args()

    output_dir = args.output.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.interactive:
        interactive_mode(output_dir, args.model)
        return 0

    if not args.query:
        parser.print_help()
        print("\nError: Please provide a research query or use --interactive mode.")
        return 1

    run_research(args.query, output_dir, args.model)
    return 0


if __name__ == "__main__":
    sys.exit(main())
