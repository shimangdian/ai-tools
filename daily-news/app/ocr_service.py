"""OCR service for text recognition from images"""
import logging
from typing import Optional
import aiohttp
import asyncio
import json
import os
import re
from pathlib import Path

logger = logging.getLogger(__name__)


class OCRService:
    """OCR service for extracting text from images using Node.js Tesseract.js"""

    def __init__(self, max_image_side: int = 8000, api_url: Optional[str] = None, token: Optional[str] = None):
        """
        Initialize OCR service

        Args:
            max_image_side: Maximum side length for images (default 8000) - not used with Tesseract.js
            api_url: Deprecated, kept for compatibility
            token: Deprecated, kept for compatibility
        """
        self.max_image_side = max_image_side
        # Get the path to the Node.js OCR service script
        self.script_path = Path(__file__).parent.parent / "ocr_service.js"
        logger.info(f"OCRService initialized with Node.js Tesseract.js: {self.script_path}")

    def format_ocr_text(self, text: str) -> str:
        """
        Format OCR extracted text to improve readability

        Args:
            text: Raw OCR text

        Returns:
            Formatted text
        """
        if not text:
            return text

        # First, replace all newlines with spaces to flatten the text
        text = text.replace('\n', ' ')

        # Remove excessive spaces between Chinese characters
        text = re.sub(r'([\u4e00-\u9fff])\s+([\u4e00-\u9fff])', r'\1\2', text)

        # Keep single space between Chinese and English/numbers
        text = re.sub(r'([\u4e00-\u9fff])\s+([a-zA-Z0-9])', r'\1 \2', text)
        text = re.sub(r'([a-zA-Z0-9])\s+([\u4e00-\u9fff])', r'\1 \2', text)

        # Remove spaces around punctuation
        text = re.sub(r'\s+([,，.。;；:：!！?？、])\s+', r'\1', text)
        text = re.sub(r'\s+([,，.。;；:：!！?？、])', r'\1', text)

        # Normalize multiple spaces to single space
        text = re.sub(r' {2,}', ' ', text)

        # Add double line break after 【每天...读世界】...!
        # Match the entire title line including date and greeting
        text = re.sub(r'(【每天[^】]*读世界[^】]*】[^1]*?[!！])\s*', r'\1\n\n', text)

        # Add line break before the first news item (1、) if not already added
        text = re.sub(r'([!！])\s*(1、)', r'\1\n\2', text)

        # Add double line break after semicolon followed by number with 顿号
        # This creates a blank line between news items
        # Match patterns like: ";数字、" or "；数字、"
        text = re.sub(r'([;；])\s*(\d+、)', r'\1\n\n\2', text)

        # Add double line break before 【每日微语】
        text = re.sub(r'([;；。])\s*(【每日微语】)', r'\1\n\n\2', text)

        # Remove spaces at the beginning of lines
        text = re.sub(r'^\s+', '', text, flags=re.MULTILINE)

        # Remove trailing spaces
        text = re.sub(r'\s+$', '', text, flags=re.MULTILINE)

        # Ensure no more than 2 consecutive newlines (1 blank line)
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()

    async def download_image(self, image_url: str) -> Optional[bytes]:
        """
        Download image from URL

        Args:
            image_url: URL of the image

        Returns:
            Image bytes, or None if failed
        """
        try:
            logger.info(f"Downloading image from {image_url}")
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url, timeout=30) as response:
                    if response.status != 200:
                        logger.error(f"Failed to download image: HTTP {response.status}")
                        return None

                    image_bytes = await response.read()
                    logger.info(f"Downloaded image, size: {len(image_bytes)} bytes")
                    return image_bytes

        except aiohttp.ClientError as e:
            logger.error(f"Network error downloading image: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading image: {str(e)}")
            return None

    async def extract_text_from_bytes(self, image_bytes: bytes) -> Optional[str]:
        """
        Extract text from image bytes using Node.js Tesseract.js
        Note: This method is not used when calling via URL directly

        Args:
            image_bytes: Image data in bytes

        Returns:
            Extracted text, or None if failed
        """
        # For Tesseract.js, we'll pass the URL directly instead of bytes
        # This method is kept for interface compatibility
        logger.warning("extract_text_from_bytes is not recommended with Node.js service, use extract_text_from_url instead")
        return None

    async def extract_text_from_url(self, image_url: str) -> Optional[str]:
        """
        Extract text from image URL using Node.js Tesseract.js

        Args:
            image_url: URL of the image

        Returns:
            Extracted text, or None if failed
        """
        try:
            logger.info(f"Calling Node.js OCR service for {image_url}")

            # Call Node.js script
            process = await asyncio.create_subprocess_exec(
                'node',
                str(self.script_path),
                image_url,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = stderr.decode('utf-8') if stderr else 'Unknown error'
                logger.error(f"Node.js OCR service failed: {error_msg}")
                return None

            # Parse JSON result
            result = json.loads(stdout.decode('utf-8'))

            if result.get('success'):
                text = result.get('text', '').strip()

                # Format the text to improve readability
                text = self.format_ocr_text(text)

                logger.info(f"OCR extracted {len(text)} characters")
                if text:
                    logger.info(f"OCR Text Preview (first 500 chars): {text[:500]}")
                return text if text else None
            else:
                logger.error(f"OCR failed: {result.get('error')}")
                return None

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OCR result: {str(e)}")
            return None
        except FileNotFoundError:
            logger.error("Node.js not found. Please install Node.js first.")
            return None
        except Exception as e:
            logger.error(f"Error calling Node.js OCR service: {str(e)}", exc_info=True)
            return None
