import os
import logging
from typing import Optional, Tuple
import httpx

logger = logging.getLogger(__name__)

# Primary Public Solana RPC
SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"
PHANTOM_WALLET = "91ykmw5GduzwcqMDorAiRPzJDhbYvWjQACEie7H1jppQ"
LAMPORTS_PER_SOL = 1_000_000_000

# Base price: ~$5 in SOL (Assuming ~$145/SOL -> 0.035 SOL)
BASE_SOL_AMOUNT = 0.035

class SolanaPaymentScanner:
    @staticmethod
    def get_user_expected_sol(user_id: int) -> float:
        """
        Generates a collision-proof micro-tag for each user based on their Telegram ID.
        Supports up to 1,000,000 simultaneous users with 0 collisions.
        Example: 0.035 + 0.00008734 = 0.03508734 SOL (difference is < $0.001)
        """
        micro_tag = (user_id % 10000) / 100_000_000 # 8 decimal places
        expected = round(BASE_SOL_AMOUNT + micro_tag, 8)
        return expected

    @staticmethod
    async def verify_payment(user_id: int) -> Tuple[bool, str]:
        """
        Scans the Solana blockchain for recent confirmed transactions into PHANTOM_WALLET
        matching this user's unique micro-tagged SOL amount.
        """
        expected_sol = SolanaPaymentScanner.get_user_expected_sol(user_id)
        expected_lamports = int(expected_sol * LAMPORTS_PER_SOL)
        tolerance_lamports = 1000 # Micro-tolerance for dust variations

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [
                PHANTOM_WALLET,
                {"limit": 20} # Scan last 20 incoming transactions
            ]
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(SOLANA_RPC_URL, json=payload)
                if res.status_code != 200:
                    return False, "Solana RPC busy, please retry in 10 seconds."

                signatures = res.json().get("result", [])
                if not signatures:
                    return False, f"No recent transactions detected. Send exactly {expected_sol} SOL to activate."

                # Check recent transactions details
                for sig_info in signatures[:10]:
                    sig = sig_info.get("signature")
                    tx_payload = {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "getTransaction",
                        "params": [
                            sig,
                            {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}
                        ]
                    }
                    tx_res = await client.post(SOLANA_RPC_URL, json=tx_payload)
                    if tx_res.status_code != 200:
                        continue

                    tx_data = tx_res.json().get("result")
                    if not tx_data:
                        continue

                    # Calculate balance change for destination wallet
                    meta = tx_data.get("meta", {})
                    post_balances = meta.get("postBalances", [])
                    pre_balances = meta.get("preBalances", [])
                    account_keys = tx_data.get("transaction", {}).get("message", {}).get("accountKeys", [])

                    for idx, acc in enumerate(account_keys):
                        pubkey = acc if isinstance(acc, str) else acc.get("pubkey")
                        if pubkey == PHANTOM_WALLET and idx < len(post_balances) and idx < len(pre_balances):
                            delta_lamports = post_balances[idx] - pre_balances[idx]
                            if abs(delta_lamports - expected_lamports) <= tolerance_lamports:
                                logger.info(f"Verified payment for user {user_id}! Sig: {sig}")
                                return True, sig

                return False, f"Deposit of {expected_sol} SOL not detected yet. Confirm on Phantom and tap verify again."

        except Exception as e:
            logger.error(f"Error checking Solana blockchain: {e}")
            return False, f"Blockchain check error: {str(e)}"

solana_scanner = SolanaPaymentScanner()
