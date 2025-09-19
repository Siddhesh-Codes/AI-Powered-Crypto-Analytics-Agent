import asyncio
import aiohttp
import sys
import json

async def test_coingecko_api():
    """Test if CoinGecko API is accessible"""
    try:
        async with aiohttp.ClientSession() as session:
            # Test basic price endpoint
            url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ CoinGecko API accessible")
                    print("Sample data:", json.dumps(data, indent=2))
                    return True
                else:
                    print(f"❌ CoinGecko API error: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ CoinGecko API connection error: {e}")
        return False

async def test_historical_data():
    """Test historical data endpoint"""
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=30&interval=daily"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Historical data accessible")
                    print("Price points:", len(data.get('prices', [])))
                    return True
                else:
                    print(f"❌ Historical data error: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Historical data connection error: {e}")
        return False

async def main():
    print("🔍 Testing CoinGecko API connectivity...")
    
    # Test basic API
    basic_ok = await test_coingecko_api()
    
    # Test historical data
    historical_ok = await test_historical_data()
    
    if basic_ok and historical_ok:
        print("✅ All API tests passed!")
    else:
        print("❌ Some API tests failed")

if __name__ == "__main__":
    asyncio.run(main())
