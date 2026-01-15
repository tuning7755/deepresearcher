@echo off
setlocal

set "PYTHONPATH=src"
uvicorn deepresearcher.api.app:app --reload
