import requests
import json

def test_endpoints():
    try:
        print("Testing API endpoints...")
        
        # Test basic API connection
        response = requests.get("http://localhost:8000/")
        print(f"Basic API Status: {response.status_code}")
        
        # Test technical indicators endpoint
        print("Testing technical indicators endpoint...")
        response = requests.get("http://localhost:8000/api/technical-indicators/bitcoin", timeout=30)
        print(f"Technical Indicators Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Technical indicators working!")
            print("Sample data:", str(data)[:200] + "...")
        else:
            print(f"❌ Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API - make sure backend is running on port 8000")
    except requests.exceptions.Timeout:
        print("❌ API request timed out")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_endpoints()
