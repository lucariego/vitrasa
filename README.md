# Vitrasa Bus Stop API

A simple Flask API that provides real-time bus stop information from the Vitrasa bus company in Vigo, Spain.

## Features

- 🌐 **Web Interface**: Beautiful, responsive web page to view bus stops
- 📱 **Mobile Friendly**: Works perfectly on phones and tablets
- 🚌 **Real-time Data**: Get current bus arrival times for any Vitrasa bus stop
- 🔄 **Auto-refresh**: Update bus times with a single click
- 📊 **JSON API**: Simple REST API with JSON responses for developers
- ⚡ **Fast & Reliable**: Error handling for invalid stop IDs and network issues
- 💚 **Health Monitoring**: Health check endpoint for monitoring

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the API:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

### Web Interface (Recommended)
Simply open your browser and go to `http://localhost:5000`

- Enter a bus stop number (e.g., `20195`)
- Click "Buscar" or press Enter
- View real-time bus arrival information
- Click "🔄 Actualizar" to refresh the data

### Direct Link
You can also create direct links: `http://localhost:5000/?stop=20195`

## API Endpoints

### Web Interface
```
GET /
```
Main web interface for viewing bus stop information.

### API Documentation
```
GET /api
```

### Get Bus Stop Information
```
GET /api/stop/{stop_id}
```

**Example:**
```bash
curl http://localhost:5000/api/stop/20195
```

**Response:**
```json
{
  "stop_id": "20195",
  "stop_name": "Praza de Compostela (fronte 35)",
  "current_time": "20:24",
  "routes": [
    {
      "line": "5A",
      "route": "NAVIA por FLORIDA",
      "minutes": 5
    },
    {
      "line": "15B",
      "route": "Samil por Beiramar",
      "minutes": 6
    }
  ],
  "last_updated": "2025-10-07T20:24:00",
  "total_routes": 2
}
```

### Health Check
```
GET /api/health
```

### API Documentation
```
GET /
```

## Deployment

For production deployment, you should:

1. Use a production WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

2. Set up a reverse proxy with Nginx
3. Use environment variables for configuration
4. Add rate limiting and caching

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `400`: Invalid stop ID (non-numeric)
- `404`: Stop not found
- `500`: Server error (network issues, parsing errors)

## Data Source

Data is scraped from the official Vitrasa website: `http://infobus.vitrasa.es:8002/`
