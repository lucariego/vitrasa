#!/bin/bash

# Vitrasa API Production Deployment Script
# Run this script on your VPS as root or with sudo

set -e

echo "🚀 Starting Vitrasa API deployment..."

# Configuration
APP_NAME="vitrasa-api"
APP_USER="www-data"
APP_DIR="/opt/$APP_NAME"
REPO_URL="https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git"  # Replace with your actual repo URL
DOMAIN="YOUR_DOMAIN.com"  # Replace with your actual domain

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

print_status "Updating system packages..."
apt update && apt upgrade -y

print_status "Installing required packages..."
apt install -y python3 python3-pip python3-venv nginx git ufw certbot python3-certbot-nginx

print_status "Creating application directory..."
mkdir -p $APP_DIR
mkdir -p /var/log/vitrasa
mkdir -p /var/run/vitrasa

print_status "Setting up application files..."
if [ ! -d "$APP_DIR/.git" ]; then
    print_warning "Cloning repository... (Make sure to push your code to GitHub first!)"
    # For now, we'll copy the local files
    cp -r /home/*/Documentos/lucariego/vitrasa/* $APP_DIR/ 2>/dev/null || {
        print_error "Could not find source files. Please upload your project to $APP_DIR manually."
        exit 1
    }
else
    print_status "Updating existing repository..."
    cd $APP_DIR
    git pull origin main
fi

cd $APP_DIR

print_status "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

print_status "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    print_warning "Please edit .env file with your production settings!"
    print_warning "Generate a secure SECRET_KEY for production!"
fi

print_status "Setting up permissions..."
chown -R $APP_USER:$APP_USER $APP_DIR
chown -R $APP_USER:$APP_USER /var/log/vitrasa
chown -R $APP_USER:$APP_USER /var/run/vitrasa
chmod +x $APP_DIR/deploy.sh

print_status "Installing systemd service..."
cp $APP_DIR/vitrasa-api.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable vitrasa-api

print_status "Configuring Nginx..."
# Backup existing nginx config if it exists
if [ -f "/etc/nginx/sites-available/default" ]; then
    cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup
fi

# Copy our nginx config
cp $APP_DIR/nginx-vitrasa.conf /etc/nginx/sites-available/vitrasa-api
sed -i "s/your-domain.com/$DOMAIN/g" /etc/nginx/sites-available/vitrasa-api

# Enable the site
ln -sf /etc/nginx/sites-available/vitrasa-api /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
nginx -t

print_status "Configuring firewall..."
ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp

print_status "Starting services..."
systemctl start vitrasa-api
systemctl restart nginx

print_status "Checking service status..."
if systemctl is-active --quiet vitrasa-api; then
    print_status "✅ Vitrasa API service is running"
else
    print_error "❌ Vitrasa API service failed to start"
    systemctl status vitrasa-api
    exit 1
fi

if systemctl is-active --quiet nginx; then
    print_status "✅ Nginx is running"
else
    print_error "❌ Nginx failed to start"
    systemctl status nginx
    exit 1
fi

print_status "Setting up SSL certificate with Let's Encrypt..."
print_warning "Make sure your domain $DOMAIN points to this server's IP address!"
read -p "Press Enter to continue with SSL setup, or Ctrl+C to skip..."

certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

print_status "🎉 Deployment completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit $APP_DIR/.env with your production settings"
echo "2. Update the domain name in the Nginx config if needed"
echo "3. Your API should be available at: https://$DOMAIN"
echo "4. Monitor logs with: journalctl -u vitrasa-api -f"
echo ""
echo "🔧 Useful commands:"
echo "- Restart API: sudo systemctl restart vitrasa-api"
echo "- Restart Nginx: sudo systemctl restart nginx"
echo "- View API logs: sudo journalctl -u vitrasa-api -f"
echo "- View Nginx logs: sudo tail -f /var/log/nginx/access.log"
