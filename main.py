from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from summarizer import summarize_transcript
from extractor import extract_action_items
import json


app = FastAPI()

class SummarizeRequest(BaseModel):
    transcript: str

class SummarizeResponse(BaseModel):
    summary: str

class ActionItemRequest(BaseModel):
    transcript: str

class ActionItem(BaseModel):
    assignee: str
    task: str
    deadline: str 

class ActionItemResponse(BaseModel):
    action_items: list[ActionItem]

@app.post("/summarize")
def summarize(request: SummarizeRequest):
    if not request.transcript.strip():
        raise HTTPException(status_code=400, detail="Transcript cannot be empty")
    
    try:
        result = summarize_transcript(request.transcript)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gemini API error: {str(e)}")

    return SummarizeResponse(summary=result)

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

    return ActionItemResponse(action_items=parsed)


@app.get("/")
def root():
    return {"service": "Scribe", "status": "running"}