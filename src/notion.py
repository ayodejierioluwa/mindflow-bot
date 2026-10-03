import json
import logging
from typing import Optional, Dict, Any
import httpx

logger = logging.getLogger(__name__)

class NotionService:
    @staticmethod
    async def create_page(api_key: str, database_id: str, title: str, category: str = "General", due_date: Optional[str] = None, priority: str = "medium") -> bool:
        """
        Creates a task or note entry in a user's Notion database.
        Works with standard Notion task/inbox database properties.
        """
        if not api_key or not database_id:
            return False

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }

        # Clean database ID (strip dashes if provided)
        clean_db_id = database_id.replace("-", "").strip()

        payload: Dict[str, Any] = {
            "parent": {"database_id": clean_db_id},
            "properties": {
                "Name": {
                    "title": [
                        {"text": {"content": title}}
                    ]
                }
            }
        }

        # Try to append Status/Category tags if supported by their database
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post("https://api.notion.com/v1/pages", headers=headers, json=payload)
                if res.status_code in [200, 201]:
                    logger.info("Successfully pushed task to Notion!")
                    return True
                else:
                    logger.warning(f"Notion API error: {res.status_code} - {res.text}")
                    return False
        except Exception as e:
            logger.error(f"Error pushing to Notion: {e}")
            return False

notion_service = NotionService()
