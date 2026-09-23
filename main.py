from fastapi import FastAPI
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
    result = summarize_transcript(request.transcript)
    return SummarizeResponse(summary=result)

@app.post("/actionitem")
def actionitem(request: ActionItemRequest):
    result_str = extract_action_items(request.transcript)
    parsed = json.loads(result_str)
    return ActionItemResponse(action_items=parsed)


@app.get("/")
def root():
    return {"service": "Scribe", "status": "running"}