import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def extract_action_items(transcript):
    model = genai.GenerativeModel('gemini-3.6-flash')

    prompt = f"""You are an action item extractor. Given a meeting transcript, identify all action items (tasks that someone committed to doing) and return them as a JSON array.

For each action item, extract:
- "assignee": the person responsible (or "unassigned" if unclear)
- "task": what needs to be done (concise, one line)
- "deadline": when it's due (or "no deadline" if not mentioned)

Return ONLY the JSON array, no other text. If there are no action items, return an empty array [].

Example format:
[
  {{"assignee": "Alex", "task": "email QA about testing timeline", "deadline": "Friday"}},
  {{"assignee": "Priya", "task": "prepare launch marketing plan", "deadline": "end of month"}}
]
    Transcript:
    {transcript}"""

    response = model.generate_content(prompt)

    return response.text

if __name__ == "__main__":
    test_transcript = """
    Sarah: Okay everyone, let's get started. Today we need to decide on the launch date for the mobile app.
    
    Mike: I think we should push it to Q2 because the QA team hasn't finished testing the payment flow.
    
    Sarah: Fair point. Alex, can you follow up with QA on their timeline?
    
    Alex: Yes, I'll email them today and get a firm date by Friday.
    
    Sarah: Also, Priya, please prepare the launch marketing plan by end of month. We'll review it in the next meeting.
    
    Priya: Sounds good, I'll have a draft ready.
    
    Mike: One more thing — we should probably do a soft launch with beta users first. Can I own that decision?
    
    Sarah: Yes, Mike, please put together a soft launch proposal by next Wednesday.
    
    Mike: Will do.
    
    Sarah: Great. Let's wrap up. Thanks everyone.
    """
    
    result = extract_action_items(test_transcript)
    print(result)

