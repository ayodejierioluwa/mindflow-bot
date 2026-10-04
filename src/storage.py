import os
import logging
from typing import Optional, List, Dict, Any
import httpx

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://egxktyspvseakunwvbbv.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_jfo26Dh0d56L7w-eyqyxdA_afstPfca")

FREE_MONTHLY_LIMIT = 15
PRO_PRICE_STARS = 250  # 250 Telegram Stars (~$4.99)

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
                    data = res.json()
                    return data[0] if data else None
                # If already exists, fetch
                get_res = await client.get(f"{url}?id=eq.{user_id}", headers=headers)
                data = get_res.json()
                return data[0] if data else None
        except Exception as e:
            logger.error(f"Supabase user error: {e}")
            return None

    async def can_user_execute(self, user_id: int) -> tuple[bool, int, bool]:
        """
        Returns (can_execute, current_count, is_pro)
        """
        if not self.is_configured():
            return True, 0, True
        headers = {"apikey": self.key, "Authorization": f"Bearer {self.key}"}
        url = f"{self.url}/rest/v1/users?id=eq.{user_id}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(url, headers=headers)
                if res.status_code == 200 and res.json():
                    u = res.json()[0]
                    is_pro = u.get("is_pro", False)
                    count = u.get("usage_count", 0) or 0
                    if is_pro:
                        return True, count, True
                    if count < FREE_MONTHLY_LIMIT:
                        return True, count, False
                    return False, count, False
                return True, 0, False
        except Exception as e:
            logger.error(f"Error checking user quota: {e}")
            return True, 0, False

    async def increment_usage(self, user_id: int) -> int:
        if not self.is_configured():
            return 1
        headers = {"apikey": self.key, "Authorization": f"Bearer {self.key}", "Content-Type": "application/json"}
        # Fetch current count
        url = f"{self.url}/rest/v1/users?id=eq.{user_id}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(url, headers=headers)
                if res.status_code == 200 and res.json():
                    current = res.json()[0].get("usage_count", 0) or 0
                    new_count = current + 1
                    await client.patch(url, headers=headers, json={"usage_count": new_count})
                    return new_count
        except Exception as e:
            logger.error(f"Error incrementing usage: {e}")
        return 1

    async def upgrade_user_to_pro(self, user_id: int, telegram_charge_id: str, provider_charge_id: str, stars_amount: int) -> bool:
        if not self.is_configured():
            return False
        headers = {"apikey": self.key, "Authorization": f"Bearer {self.key}", "Content-Type": "application/json"}
        user_url = f"{self.url}/rest/v1/users?id=eq.{user_id}"
        payment_url = f"{self.url}/rest/v1/payments"
        payment_payload = {
            "user_id": user_id,
            "telegram_charge_id": telegram_charge_id,
            "provider_payment_charge_id": provider_charge_id,
            "amount": stars_amount,
            "currency": "XTR",
            "status": "successful"
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.patch(user_url, headers=headers, json={"is_pro": True})
                await client.post(payment_url, headers=headers, json=payment_payload)
                return True
        except Exception as e:
            logger.error(f"Error upgrading user to Pro: {e}")
            return False

    async def update_user_bot_name(self, user_id: int, bot_name: str) -> bool:
        if not self.is_configured():
            return False
        headers = {"apikey": self.key, "Authorization": f"Bearer {self.key}", "Content-Type": "application/json"}
        url = f"{self.url}/rest/v1/users?id=eq.{user_id}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.patch(url, headers=headers, json={"bot_name": bot_name})
                return res.status_code in [200, 204]
        except Exception as e:
            logger.error(f"Error updating bot name: {e}")
            return False

    async def update_user_notion(self, user_id: int, notion_key: str, notion_db: str) -> bool:
        if not self.is_configured():
            return False
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json"
        }
        url = f"{self.url}/rest/v1/users?id=eq.{user_id}"
        payload = {"notion_api_key": notion_key, "notion_database_id": notion_db}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.patch(url, headers=headers, json=payload)
                return res.status_code in [200, 204]
        except Exception as e:
            logger.error(f"Error updating notion config: {e}")
            return False

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

    async def get_recent_tasks(self, user_id: int, limit: int = 8) -> List[Dict[str, Any]]:
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

    async def get_recent_expenses(self, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        if not self.is_configured():
            return []
        headers = {"apikey": self.key, "Authorization": f"Bearer {self.key}"}
        url = f"{self.url}/rest/v1/expenses?user_id=eq.{user_id}&order=created_at.desc&limit={limit}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(url, headers=headers)
                return res.json() if res.status_code == 200 else []
        except Exception as e:
            logger.error(f"Error fetching expenses: {e}")
            return []

storage = StorageService()
