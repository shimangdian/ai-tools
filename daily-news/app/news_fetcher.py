"""News fetcher module"""
import logging
from typing import Optional, Dict, Any
import aiohttp

logger = logging.getLogger(__name__)


class NewsFetcher:
    """Fetches daily news from API"""

    def __init__(self, api_url: str):
        """
        Initialize news fetcher

        Args:
            api_url: URL to fetch news from
        """
        self.api_url = api_url

    async def fetch_news(self) -> Optional[Dict[str, Any]]:
        """
        Fetch news data from API

        Returns:
            Dict containing news data with imageUrl, or None if failed
        """
        try:
            logger.info(f"Fetching news from {self.api_url}")

            async with aiohttp.ClientSession() as session:
                async with session.get(self.api_url, timeout=30) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch news: HTTP {response.status}")
                        return None

                    data = await response.json()
                    logger.info(f"Successfully fetched news data: {data}")

                    return data

        except aiohttp.ClientError as e:
            logger.error(f"Network error fetching news: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching news: {str(e)}")
            return None

    def extract_image_url(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Extract imageUrl from news data

        Args:
            data: News data dictionary

        Returns:
            Image URL string, or None if not found
        """
        if not data:
            return None

        # Try different possible keys for image URL
        possible_keys = ["imageUrl", "image_url", "imageURL", "img_url", "imgUrl", "url", "image"]

        for key in possible_keys:
            if key in data and data[key]:
                image_url = data[key]
                logger.info(f"Found image URL: {image_url}")
                return image_url

        logger.error(f"Could not find image URL in data. Available keys: {list(data.keys())}")
        return None

    async def get_daily_news_image(self) -> Optional[str]:
        """
        Get daily news image URL

        Returns:
            Image URL string, or None if failed
        """
        data = await self.fetch_news()
        if not data:
            return None

        return self.extract_image_url(data)
