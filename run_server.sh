#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH="src"
uvicorn deepresearcher.api.app:app --reload
