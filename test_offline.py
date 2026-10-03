import asyncio
from src.router import router
from src.models import IntentType

async def test_scenarios():
    test_cases = [
        "Remember to email David the updated slide deck tomorrow before 3pm",
        "Spent $28.50 on dinner with clients at Chipotle",
        "Idea for marketing: we should partner with micro-influencers on TikTok to showcase voice-to-notion workflows"
    ]
    
    print("=" * 60)
    print("🧪 TESTING SECOND BRAIN INTENT EXTRACTION & ROUTING")
    print("=" * 60)
    
    for text in test_cases:
        print(f"\n📥 INPUT: \"{text}\"")
        result = await router.parse_text(text)
        print(f"🎯 INTENT DETECTED: {result.intent.value.upper()}")
        print(f"💬 CONFIRMATION: {result.summary_message}")
        if result.task:
            print(f"   Task: {result.task.title} | Due: {result.task.due_date} | Priority: {result.task.priority}")
        if result.expense:
            print(f"   Expense: {result.expense.merchant} | {result.expense.currency} {result.expense.amount} | Cat: {result.expense.category}")
        if result.note:
            print(f"   Note: {result.note.title} | Tags: {result.note.tags}")
        print("-" * 60)

if __name__ == "__main__":
    asyncio.run(test_scenarios())
