"""
Conversation management system that doesn't rely on cookies or sessions.
Uses an in-memory store with conversation IDs that can be passed directly in the API.
"""

import time
from typing import Dict, List, Any, Optional
import uuid

# Global conversation store
# In a production system, this would be a database or Redis
conversations: Dict[str, Dict[str, Any]] = {}

# Conversation expiration time (30 minutes)
CONVERSATION_EXPIRY = 30 * 60  # seconds

def create_conversation() -> str:
    """Create a new conversation and return its ID"""
    conversation_id = str(uuid.uuid4())
    
    conversations[conversation_id] = {
        "created_at": time.time(),
        "last_updated": time.time(),
        "messages": [],
        "last_location": None,
        "language": "tr"  # Default to Turkish
    }
    
    print(f"Created new conversation with ID: {conversation_id}")
    return conversation_id

def get_conversation(conversation_id: Optional[str] = None) -> tuple[str, Dict[str, Any]]:
    """Get an existing conversation or create a new one"""
    if not conversation_id or conversation_id not in conversations:
        conversation_id = create_conversation()
        return conversation_id, conversations[conversation_id]
    
    conversation = conversations[conversation_id]
    current_time = time.time()
    
    # Check if conversation has expired
    if current_time - conversation["last_updated"] > CONVERSATION_EXPIRY:
        print(f"Conversation {conversation_id} expired, creating new one")
        conversation_id = create_conversation()
        return conversation_id, conversations[conversation_id]
    
    # Update last activity timestamp
    conversation["last_updated"] = current_time
    return conversation_id, conversation

def add_message(conversation_id: str, user_message: str, system_response: Dict[str, Any]) -> None:
    """Add a message to the conversation history"""
    _, conversation = get_conversation(conversation_id)
    
    # Keep only the last 5 conversation entries to avoid memory bloat
    if len(conversation["messages"]) >= 5:
        conversation["messages"].pop(0)
    
    message_entry = {
        "user": user_message,
        "system": system_response,
        "timestamp": time.time()
    }
    
    conversation["messages"].append(message_entry)
    
    # Update last location if available in response
    if "location" in system_response and "error" not in system_response:
        conversation["last_location"] = system_response["location"]

def get_messages(conversation_id: str) -> List[Dict[str, Any]]:
    """Get all messages in a conversation"""
    _, conversation = get_conversation(conversation_id)
    return conversation["messages"]

def get_last_location(conversation_id: str) -> Optional[Dict[str, Any]]:
    """Get the last location from a conversation"""
    _, conversation = get_conversation(conversation_id)
    return conversation.get("last_location")
