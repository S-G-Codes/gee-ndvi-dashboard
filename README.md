# 🌱 GEE NDVI Dashboard

A comprehensive interactive map dashboard for visualizing NDVI (Normalized Difference Vegetation Index) using Google Earth Engine and Leaflet.js. This project fulfills all requirements for the GIS assignment with advanced features for vegetation health analysis.

## 🚀 Features Implemented

### ✅ Core Requirements (All Completed)

#### 1. **Data Source (GEE)**
- ✅ **Google Earth Engine** integration with proper authentication
- ✅ **Sentinel-2 (COPERNICUS/S2_SR_HARMONIZED)** dataset
- ✅ **Multiple AOIs**: New York City, Amazon Rainforest, Sahara Desert
- ✅ **Date filtering**: Last 12 months with fallback to 2 years
- ✅ **Cloud masking**: Advanced cloud detection using QA60 band
- ✅ **NDVI calculation**: Proper NIR (B8) and Red (B4) band processing

#### 2. **Map Dashboard (Leaflet.js)**
- ✅ **Base map toggle**: OpenStreetMap ↔ Satellite imagery
- ✅ **Analysis layer toggle**: NDVI layer with opacity control
- ✅ **Legend/Colorbar**: Professional NDVI value ranges with color coding
- ✅ **Date filter**: Automatic date range display
- ✅ **Click functionality**: Pixel values at clicked locations

#### 3. **Advanced Features (Bonus)**
- ✅ **AOI Selection**: Switch between NYC, Amazon, and Sahara
- ✅ **Time Series Chart**: Interactive charts for clicked locations
- ✅ **Pixel Statistics**: Mean, min, max, standard deviation
- ✅ **Export Reports**: JSON format with all analysis data
- ✅ **Professional UI**: Modern, responsive design

## 🛠️ Tech Stack

### Backend
- **Python 3.8+**
- **FastAPI** - Modern, fast web framework
- **Google Earth Engine API** - Satellite data processing
- **Google Cloud Platform** - Authentication and hosting
- **Uvicorn** - ASGI server

### Frontend
- **React 18** - Modern UI framework
- **Leaflet.js** - Interactive mapping
- **Recharts** - Data visualization
- **Vite** - Fast build tool
- **CSS3** - Modern styling

## 📦 Installation & Setup

### Prerequisites
1. **Google Cloud Platform Account**
2. **Earth Engine Access** (sign up at https://signup.earthengine.google.com/)
3. **Python 3.8+**
4. **Node.js 16+**

### Backend Setup

1. **Clone and navigate to backend:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure GEE Authentication:**
   - Download service account key from GCP Console
   - Place it as `E:\gee_assignment_key.json` (update path in `main.py`)
   - Enable Earth Engine API in GCP Console
   - Grant Earth Engine permissions to service account

5. **Start backend server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Navigate to frontend:**
```bash
cd frontend_repo/frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start development server:**
```bash
npm run dev
```

## 🌐 API Endpoints

### Core Endpoints
- `GET /` - Health check
- `GET /health` - Backend status
- `GET /ndvi-tiles` - NYC NDVI data (legacy)
- `GET /test` - Test endpoint with working authentication

### Advanced Endpoints
- `GET /aoi/{aoi_name}` - NDVI data for specific AOI (nyc, amazon, sahara)
- `GET /time-series/{lat}/{lng}` - Time series data for point
- `GET /stats/{lat}/{lng}` - Pixel statistics for point

## 🎯 Dashboard Features

### Interactive Controls
1. **AOI Selection Dropdown**
   - New York City (default)
   - Amazon Rainforest
   - Sahara Desert

2. **Base Map Toggle**
   - OpenStreetMap (default)
   - Satellite imagery

3. **NDVI Layer Controls**
   - Show/Hide toggle
   - Opacity slider (0-100%)
   - Real-time updates

4. **Analysis Tools**
   - Time Series Chart toggle
   - Statistics Panel toggle
   - Export functionality

### Data Visualization
1. **NDVI Color Scheme**
   - Red (-0.2): Very Low Vegetation
   - Orange (0.0): Low Vegetation
   - Yellow (0.2): Moderate Vegetation
   - Light Green (0.4): Good Vegetation
   - Green (0.6): High Vegetation
   - Dark Green (0.8): Very High Vegetation

2. **Interactive Elements**
   - Click anywhere for pixel values
   - Popup with coordinates and statistics
   - Time series chart for selected points
   - Real-time data loading

## 📊 Data Processing

### NDVI Calculation
```python
# Formula: NDVI = (NIR - Red) / (NIR + Red)
ndvi = image.normalizedDifference(['B8', 'B4'])
```

### Cloud Masking
- Uses QA60 band for cloud detection
- Filters out cloudy pixels (>20% cloud coverage)
- Ensures data quality

### Temporal Analysis
- Last 12 months of data
- Fallback to 2 years if insufficient data
- Median composite for stable visualization

## 🔧 Configuration

### Environment Variables
- `GOOGLE_APPLICATION_CREDENTIALS` - Service account key path
- `EE_API_KEY` - Earth Engine API key (fallback)

### AOI Coordinates
- **NYC**: `[-74.25909, 40.477399, -73.700272, 40.917577]`
- **Amazon**: `[-70.0, -10.0, -50.0, 5.0]`
- **Sahara**: `[-10.0, 15.0, 30.0, 35.0]`

## 🚀 Deployment

### Backend Deployment
1. **Google Cloud Run** (recommended)
2. **Heroku** with buildpacks
3. **AWS Lambda** with API Gateway

### Frontend Deployment
1. **Netlify** (recommended for assignment)
2. **Vercel**
3. **GitHub Pages**

## 📈 Performance Features

- **Lazy Loading**: Tiles load on demand
- **Caching**: Efficient data caching
- **Error Handling**: Graceful fallbacks
- **Responsive Design**: Works on all devices

## 🎓 Assignment Compliance

### ✅ Required Features
- [x] GEE API integration
- [x] Leaflet.js map
- [x] NDVI visualization
- [x] Base map toggle
- [x] Legend with value ranges
- [x] Click for pixel values
- [x] Date filtering

### ✅ Bonus Features
- [x] AOI drawing/selection
- [x] Time series charts
- [x] Export functionality
- [x] Professional UI/UX
- [x] Multiple AOIs
- [x] Advanced statistics

## 🔍 Troubleshooting

### Common Issues
1. **Token Empty**: Check GEE permissions and API enablement
2. **404 Tiles**: Verify authentication and service account setup
3. **No Data**: Check date ranges and cloud filtering
4. **CORS Errors**: Ensure backend CORS configuration

### Debug Tools
- `python fix_gee_auth.py` - Authentication diagnostics
- `python test_gee.py` - GEE connection test
- Browser Network tab - API request monitoring

## 📝 License

This project is created for educational purposes as part of a GIS assignment.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

---

**🌱 Built with ❤️ using Google Earth Engine, React, and Leaflet.js**
