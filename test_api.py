import requests
import json

def test_api():
    """Test the FastAPI backend endpoints"""
    base_url = "http://localhost:8000"
    
    try:
        # Test health endpoint
        print("Testing health endpoint...")
        response = requests.get(f"{base_url}/health")
        print(f"Health status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        
        # Test NDVI tiles endpoint
        print("\nTesting NDVI tiles endpoint...")
        response = requests.get(f"{base_url}/ndvi-tiles")
        print(f"NDVI tiles status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ API is working!")
            print(f"Image count: {data.get('image_count', 'N/A')}")
            print(f"Date range: {data.get('date_range', 'N/A')}")
            print(f"Tile URL: {data.get('tile_url', 'N/A')[:100]}...")
        else:
            print(f"✗ API error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to backend. Make sure it's running on port 8000")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    test_api()
