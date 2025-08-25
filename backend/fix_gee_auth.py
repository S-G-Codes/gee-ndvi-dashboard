import ee
import json
import os
from datetime import datetime, timedelta

def test_gee_authentication():
    """Test different Earth Engine authentication methods"""
    print("🔍 Testing Earth Engine Authentication Methods...")
    print("=" * 50)
    
    # Method 1: Service Account
    print("\n1️⃣ Testing Service Account Authentication:")
    try:
        SERVICE_ACCOUNT = 'earthengine-sa@gee-assignment-469904.iam.gserviceaccount.com'
        KEY_FILE = 'E:\\gee_assignment_key.json'
        
        if os.path.exists(KEY_FILE):
            print(f"✓ Key file found: {KEY_FILE}")
            credentials = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY_FILE)
            ee.Initialize(credentials)
            print("✓ Service account authentication successful")
            
            # Test token generation
            test_image = ee.Image(1)
            map_id = test_image.getMapId({'min': 0, 'max': 1})
            print(f"✓ Token generated: {map_id.get('token', 'NO_TOKEN')[:20]}...")
            
            return True
        else:
            print(f"✗ Key file not found: {KEY_FILE}")
    except Exception as e:
        print(f"✗ Service account failed: {e}")
    
    # Method 2: Default Authentication
    print("\n2️⃣ Testing Default Authentication:")
    try:
        ee.Initialize(opt_url='https://earthengine.googleapis.com', project='gee-assignment-469904')
        print("✓ Default authentication successful")
        
        # Test token generation
        test_image = ee.Image(1)
        map_id = test_image.getMapId({'min': 0, 'max': 1})
        print(f"✓ Token generated: {map_id.get('token', 'NO_TOKEN')[:20]}...")
        
        return True
    except Exception as e:
        print(f"✗ Default authentication failed: {e}")
    
    # Method 3: Manual Authentication
    print("\n3️⃣ Testing Manual Authentication:")
    try:
        ee.Initialize()
        print("✓ Manual authentication successful")
        
        # Test token generation
        test_image = ee.Image(1)
        map_id = test_image.getMapId({'min': 0, 'max': 1})
        print(f"✓ Token generated: {map_id.get('token', 'NO_TOKEN')[:20]}...")
        
        return True
    except Exception as e:
        print(f"✗ Manual authentication failed: {e}")
    
    return False

def check_gee_permissions():
    """Check Earth Engine permissions"""
    print("\n🔐 Checking Earth Engine Permissions...")
    print("=" * 50)
    
    try:
        # Check if we can access assets
        assets = ee.data.getAssetRoots()
        print(f"✓ Asset roots accessible: {len(assets)} found")
        
        # Check if we can access public datasets
        s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
        count = s2.size().getInfo()
        print(f"✓ Public datasets accessible: {count} Sentinel-2 images found")
        
        # Test map ID generation with real data
        nyc = ee.Geometry.Rectangle([-74.25909, 40.477399, -73.700272, 40.917577])
        s2_filtered = s2.filterBounds(nyc).limit(1)
        
        if s2_filtered.size().getInfo() > 0:
            image = s2_filtered.first()
            ndvi = image.normalizedDifference(['B8', 'B4'])
            map_id = ndvi.getMapId({'min': -0.2, 'max': 0.8})
            
            print(f"✓ Map ID generation successful")
            print(f"  Map ID: {map_id['mapid']}")
            print(f"  Token: {map_id.get('token', 'NO_TOKEN')[:50] if map_id.get('token') else 'NO_TOKEN'}...")
            
            if not map_id.get('token'):
                print("⚠️  WARNING: Token is empty! This will cause 404 errors.")
                print("   This usually means the service account doesn't have proper Earth Engine permissions.")
            else:
                print("✅ Token is valid!")
                
        return True
        
    except Exception as e:
        print(f"✗ Permission check failed: {e}")
        return False

def provide_solutions():
    """Provide solutions for authentication issues"""
    print("\n💡 Solutions for Earth Engine Authentication Issues:")
    print("=" * 50)
    
    print("\n🔧 If token is empty, try these solutions:")
    print("\n1. Enable Earth Engine API:")
    print("   - Go to Google Cloud Console")
    print("   - Navigate to APIs & Services > Library")
    print("   - Search for 'Earth Engine' and enable it")
    
    print("\n2. Grant Earth Engine permissions to service account:")
    print("   - Go to https://signup.earthengine.google.com/")
    print("   - Sign up for Earth Engine if not already done")
    print("   - Go to https://code.earthengine.google.com/")
    print("   - Click on 'Settings' (gear icon)")
    print("   - Go to 'Service Accounts' tab")
    print("   - Add your service account email: earthengine-sa@gee-assignment-469904.iam.gserviceaccount.com")
    print("   - Grant 'Viewer' or 'Editor' permissions")
    
    print("\n3. Alternative: Use API Key method:")
    print("   - The backend will automatically fall back to API key if token is empty")
    print("   - This should work for basic tile requests")
    
    print("\n4. Check service account permissions in GCP:")
    print("   - Go to IAM & Admin > IAM")
    print("   - Find your service account")
    print("   - Ensure it has these roles:")
    print("     * Earth Engine Resource Viewer")
    print("     * Earth Engine Resource User")
    print("     * Service Account Token Creator")

if __name__ == "__main__":
    print("🌍 Earth Engine Authentication Diagnostic Tool")
    print("=" * 50)
    
    # Test authentication
    auth_success = test_gee_authentication()
    
    if auth_success:
        # Check permissions
        perm_success = check_gee_permissions()
        
        if perm_success:
            print("\n✅ Authentication and permissions are working!")
        else:
            print("\n⚠️  Authentication works but permissions may be limited")
    else:
        print("\n❌ Authentication failed")
    
    # Always provide solutions
    provide_solutions()
