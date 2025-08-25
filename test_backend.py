import requests
import json

def test_backend():
    """Test the backend API endpoints"""
    try:
        # Test health endpoint
        print("Testing health endpoint...")
        response = requests.get("http://localhost:8000/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        
        # Test NDVI tiles endpoint
        print("\nTesting NDVI tiles endpoint...")
        response = requests.get("http://localhost:8000/ndvi-tiles")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "error" in data:
                print(f"❌ Backend error: {data['error']}")
            else:
                print("✅ Backend is working!")
                print(f"Image count: {data.get('image_count', 'N/A')}")
                print(f"Date range: {data.get('date_range', 'N/A')}")
                print(f"Tile URL: {data.get('tile_url', 'N/A')[:80]}...")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure it's running on port 8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_backend()
