import asyncio
import aiohttp
import json

async def test_specific_question():
    """Test the specific problematic question"""
    
    url = "http://localhost:8000/api/chat"
    
    question = "what is bitcoin explain in brief"
    print(f"🧪 Testing: '{question}'")
    
    payload = {
        "message": question,
        "conversation_history": [],
        "user_context": {}
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    response_text = result.get('response', '')
                    print(f"✅ Response: {response_text}")
                    
                    # Check for live price
                    if "$111," in response_text or "$110," in response_text or "$112," in response_text:
                        print("✅ Contains LIVE price data!")
                    elif "$19," in response_text or "$23," in response_text:
                        print("❌ Contains OLD/FAKE price data")
                    else:
                        print("❓ No clear price data found")
                else:
                    print(f"❌ HTTP Error: {response.status}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_specific_question())