"""FastAPI application"""
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
import logging
from typing import Optional

from .config import load_config
from .models import MessageRequest, MessageResponse
from .senders.manager import MessageSenderManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Load configuration
config = load_config()

# Initialize message sender manager
sender_manager = MessageSenderManager(config)

# Create FastAPI app
app = FastAPI(
    title="Message Sender Service",
    description="A unified message sending service supporting WeCom, DingTalk, and Feishu",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify API key if configured"""
    api_key = config.get("api", {}).get("api_key")
    if api_key and x_api_key != api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Message Sender Service",
        "version": "1.0.0",
        "available_senders": sender_manager.get_available_senders()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "available_senders": sender_manager.get_available_senders()
    }


@app.post("/send", response_model=MessageResponse)
async def send_message(
    message: MessageRequest,
    _: bool = Depends(verify_api_key)
):
    """
    Send a message via configured senders

    If sender_type is specified, sends only via that sender.
    Otherwise, sends via all configured senders.
    """
    try:
        if message.sender_type:
            # Send to specific sender
            result = await sender_manager.send_to_specific(
                sender_type=message.sender_type,
                title=message.title,
                content=message.content,
                message_type=message.message_type,
                extra=message.extra
            )

            if result.get("success"):
                return MessageResponse(
                    success=True,
                    message=f"Message sent successfully via {message.sender_type}",
                    results=result
                )
            else:
                return MessageResponse(
                    success=False,
                    message=f"Failed to send message via {message.sender_type}: {result.get('error')}",
                    results=result
                )
        else:
            # Send to all senders
            results = await sender_manager.send_to_all(
                title=message.title,
                content=message.content,
                message_type=message.message_type,
                extra=message.extra
            )

            success_count = sum(1 for r in results if r.get("result", {}).get("success"))
            total_count = len(results)

            return MessageResponse(
                success=success_count > 0,
                message=f"Message sent to {success_count}/{total_count} senders",
                results=results
            )

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/senders")
async def get_senders(_: bool = Depends(verify_api_key)):
    """Get list of available senders"""
    return {
        "available_senders": sender_manager.get_available_senders()
    }
