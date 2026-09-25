from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root_endpoint():
    """Root endpoint returns service status."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"service": "Scribe", "status": "running"}


# Section 1: Error case tests (no Gemini calls needed)

def test_summarize_empty_transcript():
    """Empty transcript should return 400."""
    response = client.post("/summarize", json={"transcript": ""})
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_summarize_whitespace_transcript():
    """Whitespace-only transcript should return 400."""
    response = client.post("/summarize", json={"transcript": "   \n\t  "})
    assert response.status_code == 400


def test_actionitem_empty_transcript():
    """Empty transcript on actionitem should return 400."""
    response = client.post("/actionitem", json={"transcript": ""})
    assert response.status_code == 400


def test_actionitem_whitespace_transcript():
    """Whitespace-only transcript on actionitem should return 400."""
    response = client.post("/actionitem", json={"transcript": "   "})
    assert response.status_code == 400


def test_get_meeting_invalid_id():
    """Invalid ObjectId format should return 400."""
    response = client.get("/meetings/notavalidid")
    assert response.status_code == 400

# Section 2: Happy path tests (real Gemini + MongoDB calls)

SAMPLE_TRANSCRIPT = (
    "Sarah: Let's discuss the mobile app launch. "
    "Mike: I think we should push to Q2. "
    "Alex: I'll email QA by Friday to get a firm timeline. "
    "Priya: I'll prepare the launch marketing plan by end of month."
)


def test_summarize_valid_transcript():
    """Valid transcript should return 200 with summary and meeting_id."""
    response = client.post("/summarize", json={"transcript": SAMPLE_TRANSCRIPT})
    assert response.status_code == 200
    data = response.json()
    assert "meeting_id" in data
    assert "summary" in data
    assert len(data["summary"]) > 0
    assert isinstance(data["meeting_id"], str)


def test_actionitem_valid_transcript():
    """Valid transcript should return 200 with action_items and meeting_id."""
    response = client.post("/actionitem", json={"transcript": SAMPLE_TRANSCRIPT})
    assert response.status_code == 200
    data = response.json()
    assert "meeting_id" in data
    assert "action_items" in data
    assert isinstance(data["action_items"], list)
    # Should extract at least one action item from this transcript
    assert len(data["action_items"]) > 0
    # Each action item should have the required fields
    first_item = data["action_items"][0]
    assert "assignee" in first_item
    assert "task" in first_item
    assert "deadline" in first_item


def test_list_meetings():
    """List meetings endpoint should return a list."""
    response = client.get("/meetings")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Should have at least the meetings created by previous tests
    assert len(data) > 0


def test_list_meetings_with_limit():
    """List meetings with limit parameter should respect the limit."""
    response = client.get("/meetings?limit=2")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 2


def test_get_meeting_by_id():
    """Getting a meeting by its ID should return the full meeting doc."""
    # First create a meeting
    create_response = client.post("/summarize", json={"transcript": SAMPLE_TRANSCRIPT})
    assert create_response.status_code == 200
    meeting_id = create_response.json()["meeting_id"]

    # Now retrieve it
    get_response = client.get(f"/meetings/{meeting_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["_id"] == meeting_id
    assert data["transcript"] == SAMPLE_TRANSCRIPT
    assert data["summary"] is not None


def test_get_meeting_nonexistent_id():
    """Valid ObjectId format but nonexistent should return 404."""
    # Valid ObjectId format but doesn't exist
    fake_id = "6ab4af904368f6941fe41999"
    response = client.get(f"/meetings/{fake_id}")
    assert response.status_code == 404