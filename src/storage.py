import os
import logging
from typing import Optional, List, Dict, Any
import httpx

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

class StorageService:
    def __init__(self):
        self.url = SUPABASE_URL
        self.key = SUPABASE_KEY

    def is_configured(self) -> bool:
        return bool(self.url and self.key)

    async def get_or_create_user(self, user_id: int, username: Optional[str], first_name: Optional[str]) -> Optional[Dict[str, Any]]:
        if not self.is_configured():
            return None
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        url = f"{self.url}/rest/v1/users"
        payload = {"id": user_id, "username": username, "first_name": first_name}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, headers=headers, json=payload)
                if res.status_code in [200, 201]:
                    return res.json()[0]
                # If already exists, fetch
                get_res = await client.get(f"{url}?id=eq.{user_id}", headers=headers)
                data = get_res.json()
                return data[0] if data else None
        except Exception as e:
            logger.error(f"Supabase user error: {e}")
            return None

    async def save_task(self, user_id: int, title: str, due_date: Optional[str] = None, priority: str = "medium", category: str = "Personal") -> bool:
        if not self.is_configured():
            return False
        headers = {"apikey": self.key, "Authorization": f"Bearer {self.key}", "Content-Type": "application/json"}
        url = f"{self.url}/rest/v1/tasks"
        payload = {"user_id": user_id, "title": title, "due_date": due_date, "priority": priority, "category": category}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, headers=headers, json=payload)
                return res.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Error saving task: {e}")
            return False

    async def save_expense(self, user_id: int, merchant: str, amount: float, currency: str = "USD", category: str = "General") -> bool:
        if not self.is_configured():
            return False
        headers = {"apikey": self.key, "Authorization": f"Bearer {self.key}", "Content-Type": "application/json"}
        url = f"{self.url}/rest/v1/expenses"
        payload = {"user_id": user_id, "merchant": merchant, "amount": amount, "currency": currency, "category": category}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, headers=headers, json=payload)
                return res.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Error saving expense: {e}")
            return False

    async def get_recent_tasks(self, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        if not self.is_configured():
            return []
        headers = {"apikey": self.key, "Authorization": f"Bearer {self.key}"}
        url = f"{self.url}/rest/v1/tasks?user_id=eq.{user_id}&completed=eq.false&order=created_at.desc&limit={limit}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(url, headers=headers)
                return res.json() if res.status_code == 200 else []
        except Exception as e:
            logger.error(f"Error fetching tasks: {e}")
            return []

storage = StorageService()
