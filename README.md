# Scribe

A multi-agent meeting assistant that turns multi-speaker transcripts 
into structured summaries, decisions, and action items.

**Status:** in active development (May 2026)

**Stack:** Python, FastAPI, Pydantic, Claude/GPT APIs, async, Modal

## Architecture

Five specialized agents coordinated by a central orchestrator:
- Preprocessor — cleans and segments transcripts
- Summarizer — extracts decisions and topics  
- Action Item Extractor — pulls structured tasks
- Fact Checker — verifies groundedness against source
- Coordinator — orchestrates and resolves conflicts

(More to come as the project develops.)
