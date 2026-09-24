from fastapi import FastAPI, HTTPException
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


@app.get("/")
def root():
    return {"service": "Scribe", "status": "running"}