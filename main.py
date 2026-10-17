from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from summarizer import summarize_transcript
from extractor import extract_action_items
from database import save_meeting, get_meeting, list_meetings
import json


app = FastAPI()

class SummarizeRequest(BaseModel):
    transcript: str

class SummarizeResponse(BaseModel):
    meeting_id: str
    summary: str

class ActionItemRequest(BaseModel):
    transcript: str

class ActionItem(BaseModel):
    assignee: str
    task: str
    deadline: str 

class ActionItemResponse(BaseModel):
    meeting_id: str
    action_items: list[ActionItem]

@app.post("/summarize")
def summarize(request: SummarizeRequest):
    if not request.transcript.strip():
        raise HTTPException(status_code=400, detail="Transcript cannot be empty")
    
    try:
        result = summarize_transcript(request.transcript)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gemini API error: {str(e)}")
    
    try:
        meeting_id = save_meeting(
            transcript=request.transcript,
            summary=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return SummarizeResponse(meeting_id = meeting_id, summary=result)

@app.post("/actionitem")
def actionitem(request: ActionItemRequest):
    if not request.transcript.strip():
        raise HTTPException(status_code=400, detail="Transcript cannot be empty")
    
    try:
        result_str = extract_action_items(request.transcript)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gemini API error: {str(e)}")
    
    try:
        parsed = json.loads(result_str)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=502, detail=f"Failed to parse Gemini response: {str(e)}")
    
    try:
        meeting_id = save_meeting(
            transcript= request.transcript,
            action_items=parsed
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return ActionItemResponse(meeting_id= meeting_id, action_items=parsed)

@app.get("/meetings/{meeting_id}")
def get_meeting_endpoint(meeting_id: str):
    try:
        meeting = get_meeting(meeting_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid meeting ID: {str(e)}")
    
    if meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    return meeting

@app.get("/meetings")
def list_meetings_endpoint(limit: int = 20):
    return list_meetings(limit=limit)


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Scribe — LLM Meeting Assistant</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                max-width: 720px;
                margin: 60px auto;
                padding: 0 24px;
                color: #1a1a1a;
                line-height: 1.6;
                background: #fafafa;
            }
            h1 {
                font-size: 2.5em;
                margin-bottom: 8px;
                color: #0a0a0a;
            }
            .subtitle {
                color: #666;
                font-size: 1.15em;
                margin-bottom: 32px;
            }
            h2 {
                margin-top: 36px;
                border-bottom: 1px solid #e5e5e5;
                padding-bottom: 8px;
            }
            .stack {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin: 16px 0;
            }
            .tag {
                background: #0a0a0a;
                color: white;
                padding: 4px 12px;
                border-radius: 4px;
                font-size: 0.85em;
                font-family: 'SF Mono', Monaco, monospace;
            }
            a {
                color: #0066cc;
                text-decoration: none;
                font-weight: 500;
            }
            a:hover {
                text-decoration: underline;
            }
            .cta {
                display: inline-block;
                background: #0a0a0a;
                color: white;
                padding: 12px 20px;
                border-radius: 6px;
                margin: 8px 12px 8px 0;
                font-weight: 600;
            }
            .cta:hover {
                background: #333;
                text-decoration: none;
            }
            .cta.secondary {
                background: white;
                color: #0a0a0a;
                border: 1px solid #0a0a0a;
            }
            .endpoint {
                background: white;
                border: 1px solid #e5e5e5;
                padding: 12px 16px;
                border-radius: 6px;
                margin: 8px 0;
                font-family: 'SF Mono', Monaco, monospace;
                font-size: 0.9em;
            }
            .method {
                background: #0066cc;
                color: white;
                padding: 2px 8px;
                border-radius: 3px;
                font-weight: 600;
                margin-right: 8px;
                font-size: 0.85em;
            }
            .method.get {
                background: #28a745;
            }
            footer {
                margin-top: 60px;
                padding-top: 20px;
                border-top: 1px solid #e5e5e5;
                color: #888;
                font-size: 0.9em;
            }
        </style>
    </head>
    <body>
        <h1>Scribe</h1>
        <p class="subtitle">LLM-powered meeting summarization and action-item extraction, served as a REST API.</p>

        <div>
            <a href="/docs" class="cta">Try the API →</a>
            <a href="https://github.com/saswata0502/scribe" class="cta secondary">View code on GitHub</a>
        </div>

        <h2>What it does</h2>
        <p>Scribe takes a meeting transcript and returns either a concise summary or a structured list of action items (assignee, task, deadline) extracted by Google Gemini. Results persist to MongoDB Atlas for later retrieval.</p>

        <h2>Stack</h2>
        <div class="stack">
            <span class="tag">Python</span>
            <span class="tag">FastAPI</span>
            <span class="tag">Pydantic</span>
            <span class="tag">MongoDB Atlas</span>
            <span class="tag">Google Gemini API</span>
            <span class="tag">Pytest</span>
            <span class="tag">Render</span>
        </div>

        <h2>Endpoints</h2>
        <div class="endpoint"><span class="method">POST</span> /summarize — generate meeting summary</div>
        <div class="endpoint"><span class="method">POST</span> /actionitem — extract structured action items</div>
        <div class="endpoint"><span class="method get">GET</span> /meetings — list persisted meetings</div>
        <div class="endpoint"><span class="method get">GET</span> /meetings/{id} — retrieve a specific meeting</div>

        <h2>Design notes</h2>
        <p>Type-safe request/response contracts via Pydantic. Typed HTTP error handling distinguishes input validation (400), upstream LLM failures (502), and database errors (500) — each pointing a client at the right system to investigate. 12 pytest cases cover happy paths and error cases.</p>

        <footer>
            Built by <a href="https://www.linkedin.com/in/saswata-lahiri-1a967018b/">Saswata Lahiri</a> ·
            <a href="https://github.com/saswata0502/scribe">GitHub</a> ·
            <a href="/docs">API Docs</a>
        </footer>
    </body>
    </html>
    """


@app.get("/health")
def health():
    return {"service": "Scribe", "status": "running"}