import ee
import os
from datetime import datetime, timedelta

def test_gee_connection():
    """Test GEE connection and basic functionality"""
    try:
        # Initialize Earth Engine
        SERVICE_ACCOUNT = 'earthengine-sa@gee-assignment-469904.iam.gserviceaccount.com'
        KEY_FILE = 'E:\\gee_assignment_key.json'
        
        try:
            credentials = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY_FILE)
            ee.Initialize(credentials)
            print("✓ Initialized with service account")
        except Exception as e:
            print(f"✗ Service account initialization failed: {e}")
            ee.Initialize(opt_url='https://earthengine.googleapis.com', project='gee-assignment-469904')
            print("✓ Initialized with default credentials")

        # Test basic functionality
        print("✓ Earth Engine initialized successfully")
        
        # Test asset access
        assets = ee.data.getAssetRoots()
        print(f"✓ Asset roots: {len(assets)} found")
        
        # Test image collection access (using newer harmonized dataset)
        s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
        print(f"✓ Sentinel-2 harmonized collection accessible: {s2.size().getInfo()} images total")
        
        # Test NYC area
        nyc = ee.Geometry.Rectangle([-74.25909, 40.477399, -73.700272, 40.917577])
        print("✓ NYC geometry created")
        
        # Test date filtering
        today = datetime.now()
        start_date = today - timedelta(days=365)
        
        s2_filtered = s2.filterBounds(nyc)\
                       .filterDate(start_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))\
                       .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
        
        image_count = s2_filtered.size().getInfo()
        print(f"✓ Found {image_count} images for NYC in last 12 months")
        
        if image_count > 0:
            # Test NDVI calculation
            first_image = s2_filtered.first()
            ndvi = first_image.normalizedDifference(['B8', 'B4']).rename('NDVI')
            print("✓ NDVI calculation successful")
            
            # Test map ID generation
            map_id = ndvi.getMapId({
                'min': -0.2,
                'max': 0.8,
                'palette': ['brown', 'yellow', 'green']
            })
            print(f"✓ Map ID generated: {map_id['mapid']}")
            
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing GEE Connection...")
    success = test_gee_connection()
    if success:
        print("\n🎉 All tests passed! GEE is working correctly.")
    else:
        print("\n❌ Tests failed. Check your GEE setup.")
