from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import ee
import os
import json
from datetime import datetime, timedelta
import google.oauth2.service_account as service_account
from google.auth.transport.requests import Request

# Read configuration from environment variables
project_id = os.getenv('EE_PROJECT_ID') or os.getenv('GCP_PROJECT') or 'gee-assignment-469904'
service_account_key_file = os.getenv('GOOGLE_APPLICATION_CREDENTIALS') or os.getenv('SERVICE_ACCOUNT_FILE') or 'E:\\gee_assignment_key.json'

app = FastAPI()

# Add CORS middleware to allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Earth Engine
try:
    # Use the service account credentials directly
    credentials = service_account.Credentials.from_service_account_file(
        service_account_key_file,
        scopes=['https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/earthengine']
    )
    
    # Initialize Earth Engine with the authenticated credentials
    ee.Initialize(credentials, project=project_id)
    print("Earth Engine initialized successfully with service account.")
except Exception as e:
    print(f"Failed to initialize Earth Engine: {e}")
    # Handle the case where initialization fails gracefully
    ee.Initialize(project=project_id)
    print("Fallback: Initialized with default credentials (might not work as intended).")

@app.get("/")
def root():
    return {"status": "Backend is running"}

@app.get("/test")
async def test():
    try:
        # Define AOI (NYC)
        aoi = ee.Geometry.Point([-74.006, 40.7128]).buffer(20000)

        # Sentinel-2 collection
        collection = (ee.ImageCollection('COPERNICUS/S2')
                      .filterBounds(aoi)
                      .filterDate('2024-09-01', '2025-08-01')
                      .sort('CLOUDY_PIXEL_PERCENTAGE'))

        image = collection.first()

        # Compute NDVI
        ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')

        # Visualization params
        vis_params = {
            'min': 0,
            'max': 1,
            'palette': ['brown', 'yellow', 'green']
        }

        # Get the map ID and tile URL template
        map_id = ndvi.getMapId(vis_params)
        print('Map ID Info:', map_id)

        if not map_id:
            raise Exception("Failed to get map ID from Earth Engine.")

        # Ensure access token
        access_token = credentials.token if 'credentials' in globals() else None
        if not access_token or (hasattr(credentials, 'expired') and credentials.expired):
            credentials.refresh(Request())
            access_token = credentials.token
            print("Access token refreshed.")
        if not access_token:
            raise Exception("Failed to obtain a valid access token.")

        tile_url = f"https://earthengine.googleapis.com/v1alpha/projects/{project_id}/maps/{map_id['mapid']}/tiles/{{z}}/{{x}}/{{y}}?token={access_token}"

        return JSONResponse(content={
            "tile_url": tile_url,
            "image_count": collection.size().getInfo(),
            "date_range": {
                "start": "2024-09-01",
                "end": "2025-08-01"
            }
        })
    except Exception as e:
        print(f"Error in /test endpoint: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/ndvi-tiles")
def get_ndvi_tiles():
    try:
        nyc = ee.Geometry.Rectangle([-74.25909, 40.477399, -73.700272, 40.917577])
        today = datetime.now()
        start_date = today - timedelta(days=365)
        s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
        s2 = s2.filterBounds(nyc)\
               .filterDate(start_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))\
               .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
        image_count = s2.size().getInfo()
        if image_count == 0:
            start_date = today - timedelta(days=730)
            s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')\
                   .filterBounds(nyc)\
                   .filterDate(start_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))\
                   .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
            image_count = s2.size().getInfo()
        if image_count == 0:
            return {"error": f"No Sentinel-2 images found for NYC in the last 2 years"}

        def maskS2clouds(image):
            qa = image.select('QA60')
            cloudBitMask = 1 << 10
            cirrusBitMask = 1 << 11
            mask = qa.bitwiseAnd(cloudBitMask).eq(0).And(
                qa.bitwiseAnd(cirrusBitMask).eq(0))
            return image.updateMask(mask).divide(10000)

        s2Masked = s2.map(maskS2clouds)
        ndviCollection = s2Masked.map(lambda img: 
            img.normalizedDifference(['B8', 'B4']).rename('NDVI')\
               .copyProperties(img, ['system:time_start'])
        )
        ndviMedian = ndviCollection.median().clip(nyc)
        ndviVis = {
            'min': -0.2,
            'max': 0.8,
            'palette': ['red', 'orange', 'yellow', 'lightgreen', 'green', 'darkgreen']
        }
        map_id = ndviMedian.getMapId(ndviVis)
        if not map_id:
            raise Exception("Failed to get map ID from Earth Engine.")

        # Ensure access token
        access_token = credentials.token if 'credentials' in globals() else None
        if not access_token or (hasattr(credentials, 'expired') and credentials.expired):
            credentials.refresh(Request())
            access_token = credentials.token
            print("Access token refreshed.")
        if not access_token:
            raise Exception("Failed to obtain a valid access token.")

        tile_url = f"https://earthengine.googleapis.com/v1alpha/projects/{project_id}/maps/{map_id['mapid']}/tiles/{{z}}/{{x}}/{{y}}?token={access_token}"

        return {
            "tile_url": tile_url,
            "image_count": image_count,
            "date_range": {
                "start": start_date.strftime('%Y-%m-%d'),
                "end": today.strftime('%Y-%m-%d')
            },
            "auth_method": "service_account_token"
        }
    except Exception as e:
        print(f"Error in get_ndvi_tiles: {e}")
        return {"error": str(e)}

@app.get("/health")
def health_check():
    return {"status": "ok", "gee_initialized": ee.data.getAssetRoots() is not None}

@app.get("/time-series/{lat}/{lng}")
def get_time_series(lat: float, lng: float):
    """Get NDVI time series for a specific point"""
    try:
        # Create point geometry
        point = ee.Geometry.Point([lng, lat])
        
        # Calculate date range: last 12 months
        today = datetime.now()
        start_date = today - timedelta(days=365)
        
        # Load Sentinel-2 Image Collection
        s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
        
        # Filter to point and date window
        s2 = s2.filterBounds(point)\
               .filterDate(start_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))\
               .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
        
        # Function to mask clouds
        def maskS2clouds(image):
            qa = image.select('QA60')
            cloudBitMask = 1 << 10
            cirrusBitMask = 1 << 11
            mask = qa.bitwiseAnd(cloudBitMask).eq(0).And(
                qa.bitwiseAnd(cirrusBitMask).eq(0))
            return image.updateMask(mask).divide(10000)
        
        # Process images and compute NDVI
        s2Masked = s2.map(maskS2clouds)
        ndviCollection = s2Masked.map(lambda img: 
            img.normalizedDifference(['B8', 'B4']).rename('NDVI')\
               .copyProperties(img, ['system:time_start'])
        )
        
        # Sample the point
        time_series = ndviCollection.map(lambda img: 
            img.reduceRegions(
                collection=ee.FeatureCollection([ee.Feature(point)]),
                reducer=ee.Reducer.mean(),
                scale=10
            ).first().set('date', img.date().format('YYYY-MM-dd'))
        )
        
        # Get the time series data
        time_series_data = time_series.getInfo()
        
        # Extract NDVI values and dates
        features = time_series_data.get('features', [])
        time_series_points = []
        
        for feature in features:
            properties = feature.get('properties', {})
            ndvi_value = properties.get('NDVI')
            date = properties.get('date')
            if ndvi_value is not None and date:
                time_series_points.append({
                    'date': date,
                    'ndvi': round(ndvi_value, 3)
                })
        
        # Sort by date
        time_series_points.sort(key=lambda x: x['date'])
        
        return {
            "point": {"lat": lat, "lng": lng},
            "time_series": time_series_points,
            "count": len(time_series_points)
        }
        
    except Exception as e:
        print(f"Error in get_time_series: {e}")
        return {"error": str(e)}

@app.get("/aoi/{aoi_name}")
def get_aoi_data(aoi_name: str):
    """Get NDVI data for different Areas of Interest"""
    try:
        # Define different AOIs
        aois = {
            "nyc": {
                "name": "New York City",
                "geometry": ee.Geometry.Rectangle([-74.25909, 40.477399, -73.700272, 40.917577])
            },
            "amazon": {
                "name": "Amazon Rainforest",
                "geometry": ee.Geometry.Rectangle([-70.0, -10.0, -50.0, 5.0])
            },
            "sahara": {
                "name": "Sahara Desert",
                "geometry": ee.Geometry.Rectangle([-10.0, 15.0, 30.0, 35.0])
            }
        }
        
        if aoi_name not in aois:
            return {"error": f"AOI '{aoi_name}' not found. Available: {list(aois.keys())}"}
        
        aoi = aois[aoi_name]
        
        # Calculate date range: last 12 months
        today = datetime.now()
        start_date = today - timedelta(days=365)
        
        # Load Sentinel-2 Image Collection
        s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
        
        # Filter to AOI and date window
        s2 = s2.filterBounds(aoi["geometry"])\
               .filterDate(start_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))\
               .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
        
        # Check if we have images
        image_count = s2.size().getInfo()
        if image_count == 0:
            return {"error": f"No Sentinel-2 images found for {aoi['name']} in the last 12 months"}
        
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
        
        # Take median NDVI over the collection and clip to AOI
        ndviMedian = ndviCollection.median().clip(aoi["geometry"])
        
        # Visualization parameters
        ndviVis = {
            'min': -0.2,
            'max': 0.8,
            'palette': ['red', 'orange', 'yellow', 'lightgreen', 'green', 'darkgreen']
        }
        
        # Generate Map ID
        map_id = ndviMedian.getMapId(ndviVis)
        
        if not map_id:
            raise Exception("Failed to get map ID from Earth Engine.")
        
        # Get the access token
        access_token = credentials.token
        if not access_token or credentials.expired:
            credentials.refresh(Request())
            access_token = credentials.token
        
        if not access_token:
            raise Exception("Failed to obtain a valid access token.")
        
        # Construct tile URL
        tile_url = f"https://earthengine.googleapis.com/v1alpha/projects/{project_id}/maps/{map_id['mapid']}/tiles/{{z}}/{{x}}/{{y}}?token={access_token}"
        
        return {
            "aoi_name": aoi["name"],
            "tile_url": tile_url,
            "image_count": image_count,
            "date_range": {
                "start": start_date.strftime('%Y-%m-%d'),
                "end": today.strftime('%Y-%m-%d')
            }
        }
        
    except Exception as e:
        print(f"Error in get_aoi_data: {e}")
        return {"error": str(e)}

@app.get("/stats/{lat}/{lng}")
def get_pixel_stats(lat: float, lng: float):
    """Get pixel statistics for a specific point"""
    try:
        # Create point geometry
        point = ee.Geometry.Point([lng, lat])
        
        # Calculate date range: last 12 months
        today = datetime.now()
        start_date = today - timedelta(days=365)
        
        # Load Sentinel-2 Image Collection
        s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
        
        # Filter to point and date window
        s2 = s2.filterBounds(point)\
               .filterDate(start_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))\
               .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
        
        # Function to mask clouds
        def maskS2clouds(image):
            qa = image.select('QA60')
            cloudBitMask = 1 << 10
            cirrusBitMask = 1 << 11
            mask = qa.bitwiseAnd(cloudBitMask).eq(0).And(
                qa.bitwiseAnd(cirrusBitMask).eq(0))
            return image.updateMask(mask).divide(10000)
        
        # Process images and compute NDVI
        s2Masked = s2.map(maskS2clouds)
        ndviCollection = s2Masked.map(lambda img: 
            img.normalizedDifference(['B8', 'B4']).rename('NDVI')\
               .copyProperties(img, ['system:time_start'])
        )
        
        # Calculate statistics
        stats = ndviCollection.reduce(ee.Reducer.mean().combine(
            ee.Reducer.stdDev(), '', True).combine(
            ee.Reducer.minMax(), '', True)
        )
        
        # Sample the point
        point_stats = stats.reduceRegions(
            collection=ee.FeatureCollection([ee.Feature(point)]),
            reducer=ee.Reducer.first(),
            scale=10
        ).first().getInfo()
        
        properties = point_stats.get('properties', {})
        
        return {
            "point": {"lat": lat, "lng": lng},
            "statistics": {
                "mean": round(properties.get('NDVI_mean', 0), 3),
                "std_dev": round(properties.get('NDVI_stdDev', 0), 3),
                "min": round(properties.get('NDVI_min', 0), 3),
                "max": round(properties.get('NDVI_max', 0), 3)
            },
            "image_count": s2.size().getInfo()
        }
        
    except Exception as e:
        print(f"Error in get_pixel_stats: {e}")
        return {"error": str(e)}
