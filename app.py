#!/usr/bin/env python3
"""
Vitrasa Bus Stop API

A simple Flask API that provides bus stop information from Vitrasa.
Usage: GET /api/stop/{stop_id}
Example: GET /api/stop/20195
"""

from flask import Flask, jsonify, request, render_template
import requests
from bs4 import BeautifulSoup
import re
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Production configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
app.config['REQUEST_TIMEOUT'] = int(os.getenv('REQUEST_TIMEOUT', '10'))
app.config['CACHE_TIMEOUT'] = int(os.getenv('CACHE_TIMEOUT', '60'))

# Configure logging for production
if not app.debug:
    logging.basicConfig(
        level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
        format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )

class VitrasaScraper:
    """Scraper class for extracting bus stop information from Vitrasa website."""
    
    BASE_URL = "http://infobus.vitrasa.es:8002/Default.aspx"
    
    def __init__(self, timeout=10):
        self.session = requests.Session()
        self.timeout = timeout
        # Set a user agent to avoid being blocked
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36'
        })
    
    def get_stop_info(self, stop_id):
        """
        Fetch and parse bus stop information.
        
        Args:
            stop_id (str): The bus stop ID
            
        Returns:
            dict: Parsed bus stop information or None if error
        """
        try:
            # Make request to the bus stop page
            url = f"{self.BASE_URL}?parada={stop_id}"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract stop information
            stop_info = self._parse_stop_info(soup, stop_id)
            
            return stop_info
            
        except requests.RequestException as e:
            print(f"Request error for stop {stop_id}: {e}")
            return None
        except Exception as e:
            print(f"Parsing error for stop {stop_id}: {e}")
            return None
    
    def _parse_stop_info(self, soup, stop_id):
        """Parse the HTML soup to extract stop information."""
        
        # Extract stop name
        stop_name_elem = soup.find('span', {'id': 'lblNombre'})
        stop_name = stop_name_elem.text.strip() if stop_name_elem else "Unknown"
        
        # Extract current time
        time_elem = soup.find('span', {'id': 'lblHora'})
        current_time = None
        if time_elem:
            time_text = time_elem.text.strip()
            # Extract time from "Hora: XX:XX" format
            time_match = re.search(r'(\d{2}:\d{2})', time_text)
            if time_match:
                current_time = time_match.group(1)
        
        # Extract bus routes from the table
        routes = []
        table = soup.find('table', {'id': 'GridView1'})
        
        if table:
            # Find all data rows (skip header and pagination)
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) == 3:  # Line, Route, Minutes
                    line = cells[0].text.strip()
                    route = cells[1].text.strip()
                    minutes_text = cells[2].text.strip()
                    
                    # Try to convert minutes to integer
                    try:
                        minutes = int(minutes_text)
                    except ValueError:
                        minutes = minutes_text  # Keep as string if not a number
                    
                    routes.append({
                        'line': line,
                        'route': route,
                        'minutes': minutes
                    })
        
        return {
            'stop_id': stop_id,
            'stop_name': stop_name,
            'current_time': current_time,
            'routes': routes,
            'last_updated': datetime.now().isoformat(),
            'total_routes': len(routes)
        }

# Initialize scraper with timeout from config
scraper = VitrasaScraper(timeout=app.config['REQUEST_TIMEOUT'])

# Add security headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

@app.route('/')
def home():
    """Serve the web interface."""
    return render_template('index.html')

@app.route('/api')
def api_docs():
    """API documentation endpoint."""
    return jsonify({
        "name": "Vitrasa Bus Stop API",
        "description": "Get real-time bus stop information from Vitrasa",
        "version": "1.0.0",
        "endpoints": {
            "GET /": "Web interface for viewing bus stops",
            "GET /api": "API documentation",
            "GET /api/stop/{stop_id}": "Get information for a specific bus stop",
            "GET /api/health": "Health check endpoint"
        },
        "example": "/api/stop/20195"
    })

@app.route('/api/health')
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/stop/<stop_id>')
def get_stop_info(stop_id):
    """
    Get bus stop information.
    
    Args:
        stop_id (str): The bus stop ID
        
    Returns:
        JSON response with stop information
    """
    # Validate stop_id (should be numeric)
    if not stop_id.isdigit():
        return jsonify({
            "error": "Invalid stop ID",
            "message": "Stop ID must be numeric",
            "stop_id": stop_id
        }), 400
    
    # Get stop information
    stop_info = scraper.get_stop_info(stop_id)
    
    if stop_info is None:
        return jsonify({
            "error": "Failed to fetch stop information",
            "message": "Could not retrieve data from Vitrasa website",
            "stop_id": stop_id
        }), 500
    
    # Check if stop exists (no routes might indicate invalid stop)
    if stop_info['total_routes'] == 0:
        return jsonify({
            "error": "Stop not found",
            "message": "No bus routes found for this stop ID",
            "stop_id": stop_id
        }), 404
    
    return jsonify(stop_info)

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "error": "Endpoint not found",
        "message": "The requested endpoint does not exist",
        "available_endpoints": ["/", "/api", "/api/health", "/api/stop/{stop_id}"]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500

if __name__ == '__main__':
    # Run the development server
    app.run(host='0.0.0.0', port=5000, debug=True)
