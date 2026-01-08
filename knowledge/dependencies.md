# Dependencies and Runtime

## Runtime Requirements
- Python 3.11+
- deepagents >= 0.2.8
- deepagents-cli >= 0.0.12
- tavily-python >= 0.7.0
- langchain >= 1.0.0
- langgraph >= 1.0.0
- langchain-openai >= 1.0.0
- langchain-anthropic >= 1.0.0

## Install
- `pip install -r requirements.txt`

## External Services
- Tavily for web search via `web_search`.
- LLM backends via LangChain providers (OpenAI, Anthropic).

## Configuration Tips
- Use environment variables for API keys (e.g., `TAVILY_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`).
- Keep generated research output and local artifacts out of version control.
