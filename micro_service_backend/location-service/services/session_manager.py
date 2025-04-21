import time
from typing import Dict, Optional, Any

# Simple in-memory session storage
# In a production environment, you would use Redis or a database
sessions: Dict[str, Dict[str, Any]] = {}

# Session expiration time (30 minutes)
SESSION_EXPIRY = 30 * 60  # seconds

def create_session(session_id: str) -> Dict[str, Any]:
    """Create a new session or reset an existing one"""
    session = {
        "created_at": time.time(),
        "last_updated": time.time(),
        "conversation_history": [],
        "last_location": None,
        "last_query_type": None,
        "language": "tr"  # Default to Turkish
    }
    sessions[session_id] = session
    return session

def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get an existing session or create a new one if it doesn't exist"""
    if session_id not in sessions:
        return create_session(session_id)
    
    session = sessions[session_id]
    current_time = time.time()
    
    # Check if session has expired
    if current_time - session["last_updated"] > SESSION_EXPIRY:
        return create_session(session_id)
    
    # Update last activity timestamp
    session["last_updated"] = current_time
    return session

def update_session(session_id: str, data: Dict[str, Any]) -> None:
    """Update session with new data"""
    if session_id in sessions:
        sessions[session_id].update(data)
        sessions[session_id]["last_updated"] = time.time()

def add_to_conversation_history(session_id: str, user_prompt: str, response_data: Dict[str, Any]) -> None:
    """Add conversation entry to the session history"""
    session = get_session(session_id)
    
    # Keep only the last 5 conversation entries to avoid memory bloat
    if len(session["conversation_history"]) >= 5:
        session["conversation_history"].pop(0)
    
    conversation_entry = {
        "prompt": user_prompt,
        "response": response_data,
        "timestamp": time.time()
    }
    
    session["conversation_history"].append(conversation_entry)
    
    # Update last location if available in response
    if "location" in response_data:
        session["last_location"] = response_data["location"]
    
    if "type" in response_data:
        session["last_query_type"] = response_data["type"]
