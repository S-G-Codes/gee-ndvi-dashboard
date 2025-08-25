import ee
import requests
from datetime import datetime, timedelta

def test_tile_generation():
    """Test tile URL generation and make sample requests"""
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

        # Define AOI: NYC bounding box
        nyc = ee.Geometry.Rectangle([-74.25909, 40.477399, -73.700272, 40.917577])
        
        # Calculate date range: last 12 months
        today = datetime.now()
        start_date = today - timedelta(days=365)
        
        # Load Sentinel-2 Image Collection
        s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
        
        # Filter to NYC and date window
        s2 = s2.filterBounds(nyc)\
               .filterDate(start_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))\
               .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
        
        image_count = s2.size().getInfo()
        print(f"Found {image_count} images")
        
        if image_count == 0:
            print("No images found, trying last 2 years...")
            start_date = today - timedelta(days=730)
            s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')\
                   .filterBounds(nyc)\
                   .filterDate(start_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))\
                   .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
            image_count = s2.size().getInfo()
        
        if image_count == 0:
            print("❌ No images found")
            return False
        
        # Function to mask clouds
        def maskS2clouds(image):
            qa = image.select('QA60')
            cloudBitMask = 1 << 10
            cirrusBitMask = 1 << 11
            mask = qa.bitwiseAnd(cloudBitMask).eq(0).And(
                qa.bitwiseAnd(cirrusBitMask).eq(0))
            return image.updateMask(mask).divide(10000)
        
        # Process images
        s2Masked = s2.map(maskS2clouds)
        ndviCollection = s2Masked.map(lambda img: 
            img.normalizedDifference(['B8', 'B4']).rename('NDVI')\
               .copyProperties(img, ['system:time_start'])
        )
        ndviMedian = ndviCollection.median().clip(nyc)
        
        # Visualization parameters
        ndviVis = {
            'min': -0.2,
            'max': 0.8,
            'palette': ['red', 'orange', 'yellow', 'lightgreen', 'green', 'darkgreen']
        }
        
        # Generate Map ID
        map_id = ndviMedian.getMapId(ndviVis)
        
        print(f"Map ID: {map_id['mapid']}")
        print(f"Token: {map_id['token'][:50]}...")
        
        # Build tile URL
        mapid_parts = map_id['mapid'].split('/')
        if len(mapid_parts) > 1:
            project_id = mapid_parts[0]
            map_id_short = mapid_parts[-1]
            tile_url = f"https://earthengine.googleapis.com/v1alpha/projects/{project_id}/maps/{map_id_short}/tiles/{{z}}/{{x}}/{{y}}?token={map_id['token']}"
        else:
            tile_url = f"https://earthengine.googleapis.com/v1alpha/projects/earthengine-legacy/maps/{map_id['mapid']}/tiles/{{z}}/{{x}}/{{y}}?token={map_id['token']}"
        
        print(f"Tile URL template: {tile_url}")
        
        # Test a few tile requests
        test_tiles = [
            (10, 301, 384),  # NYC area
            (10, 302, 384),
            (10, 301, 385),
        ]
        
        for z, x, y in test_tiles:
            test_url = tile_url.format(z=z, x=x, y=y)
            print(f"\nTesting tile {z}/{x}/{y}:")
            print(f"URL: {test_url[:100]}...")
            
            try:
                response = requests.get(test_url, timeout=10)
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    print("✓ Tile loaded successfully")
                else:
                    print(f"✗ Failed: {response.status_code}")
            except Exception as e:
                print(f"✗ Error: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Tile Generation...")
    success = test_tile_generation()
    if success:
        print("\n🎉 Tile generation test completed!")
    else:
        print("\n❌ Tile generation test failed.")
