"""API models"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class MessageRequest(BaseModel):
    """Message request model"""
    title: str = Field(..., description="Message title", min_length=1, max_length=200)
    content: str = Field(..., description="Message content", min_length=1)
    message_type: str = Field(default="text", description="Message type (text, markdown, post)")
    sender_type: Optional[str] = Field(default=None, description="Specific sender type (wecom, dingtalk, feishu). If not specified, send to all.")
    extra: Optional[Dict[str, Any]] = Field(default=None, description="Extra parameters for specific sender")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "System Alert",
                "content": "Server CPU usage is above 80%",
                "message_type": "text",
                "sender_type": "wecom",
                "extra": {
                    "mentioned_list": ["@all"]
                }
            }
        }


class MessageResponse(BaseModel):
    """Message response model"""
    success: bool
    message: str
    results: Optional[Any] = None
