"""Research tools for the Deep Research Agent."""

from typing import Any, Literal

import requests
from markdownify import markdownify
from tavily import TavilyClient

from deepagents_cli.config import settings

tavily_client = TavilyClient(api_key=settings.tavily_api_key) if settings.has_tavily else None


def web_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
) -> dict[str, Any]:
    """Search the web using Tavily for current information.

    Args:
        query: The search query (be specific and detailed)
        max_results: Number of results to return (default: 5)
        topic: Search topic type - "general" for most queries, "news" for current events
        include_raw_content: Include full page content (warning: uses more tokens)

    Returns:
        Dictionary containing search results with titles, URLs, and content excerpts
    """
    if tavily_client is None:
        return {
            "error": "Tavily API key not configured. Please set TAVILY_API_KEY environment variable.",
            "query": query,
        }

    try:
        return tavily_client.search(
            query,
            max_results=max_results,
            include_raw_content=include_raw_content,
            topic=topic,
        )
    except Exception as e:
        return {"error": f"Web search error: {e!s}", "query": query}


def fetch_url(
    url: str,
    timeout: int = 30,
    max_bytes: int = 1_000_000,
    max_chars: int = 200_000,
) -> dict[str, Any]:
    """Fetch content from a URL and convert HTML to markdown format.

    Args:
        url: The URL to fetch (must be a valid HTTP/HTTPS URL)
        timeout: Request timeout in seconds (default: 30)
        max_bytes: Maximum number of response bytes to read (default: 1,000,000)
        max_chars: Maximum number of markdown characters to return (default: 200,000)

    Returns:
        Dictionary containing the page content converted to markdown
    """
    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "Mozilla/5.0 (compatible; DeepResearcher/1.0)"},
            stream=True,
        )
        response.raise_for_status()

        content = bytearray()
        truncated = False
        for chunk in response.iter_content(chunk_size=65536):
            if not chunk:
                continue
            remaining = max_bytes - len(content)
            if remaining <= 0:
                truncated = True
                break
            if len(chunk) > remaining:
                content.extend(chunk[:remaining])
                truncated = True
                break
            content.extend(chunk)

        encoding = response.encoding or "utf-8"
        text = content.decode(encoding, errors="ignore")
        markdown_content = markdownify(text)
        if len(markdown_content) > max_chars:
            markdown_content = markdown_content[:max_chars] + "[truncated]"
            truncated = True

        return {
            "url": str(response.url),
            "markdown_content": markdown_content,
            "status_code": response.status_code,
            "content_length": len(markdown_content),
            "bytes_read": len(content),
            "truncated": truncated,
        }
    except Exception as e:
        return {"error": f"Fetch URL error: {e!s}", "url": url}


RESEARCH_TOOLS = [web_search]
