from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

# Connect once at module load
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["scribe"]           # database name
meetings = db["meetings"]        # collection

def save_meeting(transcript: str, summary: str = None, action_items: list = None):
    """Save a meeting to MongoDB. Returns the inserted document's ID."""
    doc = {
        "transcript": transcript,
        "summary": summary,
        "action_items": action_items,
        "created_at": datetime.utcnow()
    }
    result = meetings.insert_one(doc)
    return str(result.inserted_id)

def get_meeting(meeting_id: str):
    """Fetch a meeting by ID."""
    from bson import ObjectId
    doc = meetings.find_one({"_id": ObjectId(meeting_id)})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc

def list_meetings(limit: int = 20):
    """List recent meetings, newest first."""
    docs = list(meetings.find().sort("created_at", -1).limit(limit))
    for doc in docs:
        doc["_id"] = str(doc["_id"])
    return docs