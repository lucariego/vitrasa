#!/bin/bash

# Vitrasa API Setup Script

echo "Setting up Vitrasa Bus Stop API..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Setup complete!"
echo ""
echo "To run the API:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the application: python app.py"
echo "3. The API will be available at http://localhost:5000"
echo ""
echo "Example usage:"
echo "curl http://localhost:5000/api/stop/20195"
