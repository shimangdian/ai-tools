"""OCR service for text recognition from images"""
import logging
from typing import Optional
import aiohttp
import base64

logger = logging.getLogger(__name__)


class OCRService:
    """OCR service for extracting text from images using custom OCR API"""

    def __init__(self, max_image_side: int = 8000, api_url: Optional[str] = None, token: Optional[str] = None):
        """
        Initialize OCR service

        Args:
            max_image_side: Maximum side length for images (default 8000)
            api_url: OCR API URL
            token: OCR API Token
        """
        self.max_image_side = max_image_side
        self.api_url = api_url or "https://mcf360b09fl9eeja.aistudio-app.com/ocr"
        self.token = token or "7ebd9752718ec74c29b37950f3960cccb498bdad"
        logger.info(f"OCRService initialized with custom OCR API: {self.api_url}")

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
        Extract text from image bytes using OCR API

        Args:
            image_bytes: Image data in bytes

        Returns:
            Extracted text, or None if failed
        """
        try:
            # Encode image to base64
            file_data = base64.b64encode(image_bytes).decode("ascii")

            headers = {
                "Authorization": f"token {self.token}",
                "Content-Type": "application/json"
            }

            # For images, set fileType to 1
            payload = {
                "file": file_data,
                "fileType": 1,
                "useDocOrientationClassify": False,
                "useDocUnwarping": False,
                "useTextlineOrientation": False,
            }

            logger.info("Calling custom OCR API...")

            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, json=payload, headers=headers, timeout=60) as response:
                    if response.status != 200:
                        logger.error(f"OCR API error: HTTP {response.status}")
                        error_text = await response.text()
                        logger.error(f"Error response: {error_text}")
                        return None

                    result = await response.json()

                    # Extract OCR results
                    ocr_results = result.get("result", {}).get("ocrResults", [])
                    if not ocr_results:
                        logger.warning("No OCR results returned")
                        return None

                    # Combine all pruned results
                    lines = []
                    for res in ocr_results:
                        pruned_result = res.get("prunedResult", "")
                        if pruned_result:
                            lines.append(pruned_result.strip())

                    extracted_text = "\n".join(lines)

                    logger.info(f"OCR extracted {len(lines)} sections, total {len(extracted_text)} characters")
                    if extracted_text:
                        logger.info(f"OCR Text Preview (first 500 chars): {extracted_text[:500]}")

                    return extracted_text if extracted_text else None

        except Exception as e:
            logger.error(f"Error extracting text with OCR API: {str(e)}", exc_info=True)
            return None

    async def extract_text_from_url(self, image_url: str) -> Optional[str]:
        """
        Extract text from image URL

        Args:
            image_url: URL of the image

        Returns:
            Extracted text, or None if failed
        """
        # Download image
        image_bytes = await self.download_image(image_url)
        if not image_bytes:
            return None

        # Extract text
        text = await self.extract_text_from_bytes(image_bytes)
        return text
