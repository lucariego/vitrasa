# 🚀 Production Deployment Guide

This guide will help you deploy the Vitrasa Bus Stop API to your VPS in production.

## 📋 Prerequisites

- Ubuntu/Debian VPS with root access
- Domain name pointing to your VPS IP address
- Basic familiarity with Linux command line

## 🛠 Quick Deployment (Automated)

1. **Upload your project** to your VPS:
   ```bash
   scp -r vitrasa/ root@your-server-ip:/opt/
   ```

2. **Run the deployment script**:
   ```bash
   ssh root@your-server-ip
   cd /opt/vitrasa
   ./deploy.sh
   ```

3. **Configure your environment**:
   ```bash
   nano /opt/vitrasa-api/.env
   ```
   Update the following values:
   ```env
   SECRET_KEY=your-very-secret-key-here
   FLASK_ENV=production
   FLASK_DEBUG=False
   ```

4. **Restart the service**:
   ```bash
   systemctl restart vitrasa-api
   ```

That's it! Your API should be running at `https://your-domain.com`

## 🔧 Manual Deployment (Step by Step)

### 1. System Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv nginx git ufw certbot python3-certbot-nginx
```

### 2. Application Setup

```bash
# Create application directory
sudo mkdir -p /opt/vitrasa-api
sudo mkdir -p /var/log/vitrasa
sudo mkdir -p /var/run/vitrasa

# Copy your application files
sudo cp -r /path/to/your/vitrasa/* /opt/vitrasa-api/

# Set up Python environment
cd /opt/vitrasa-api
sudo python3 -m venv venv
sudo venv/bin/pip install --upgrade pip
sudo venv/bin/pip install -r requirements.txt

# Configure environment
sudo cp .env.example .env
sudo nano .env  # Edit with your production settings

# Set permissions
sudo chown -R www-data:www-data /opt/vitrasa-api
sudo chown -R www-data:www-data /var/log/vitrasa
sudo chown -R www-data:www-data /var/run/vitrasa
```

### 3. Systemd Service

```bash
# Install service file
sudo cp /opt/vitrasa-api/vitrasa-api.service /etc/systemd/system/

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable vitrasa-api
sudo systemctl start vitrasa-api

# Check status
sudo systemctl status vitrasa-api
```

### 4. Nginx Configuration

```bash
# Backup default config
sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup

# Install our config
sudo cp /opt/vitrasa-api/nginx-vitrasa.conf /etc/nginx/sites-available/vitrasa-api

# Update domain name
sudo sed -i 's/your-domain.com/yourdomain.com/g' /etc/nginx/sites-available/vitrasa-api

# Enable site
sudo ln -sf /etc/nginx/sites-available/vitrasa-api /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test and restart
sudo nginx -t
sudo systemctl restart nginx
```

### 5. SSL Certificate (Let's Encrypt)

```bash
# Configure firewall
sudo ufw --force enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## 🔍 Monitoring & Maintenance

### Check Service Status
```bash
# API service status
sudo systemctl status vitrasa-api

# View API logs
sudo journalctl -u vitrasa-api -f

# Check Nginx status
sudo systemctl status nginx

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Updating the Application
```bash
# Stop service
sudo systemctl stop vitrasa-api

# Update code (if using git)
cd /opt/vitrasa-api
sudo -u www-data git pull origin main

# Update dependencies
sudo -u www-data venv/bin/pip install -r requirements.txt

# Restart service
sudo systemctl start vitrasa-api
```

### Performance Monitoring
```bash
# Check resource usage
htop

# Monitor API performance
curl -s http://localhost:5000/api/health

# Check response times
curl -w "@curl-format.txt" -s -o /dev/null http://localhost:5000/api/stop/20195
```

## 🛡 Security Considerations

- **Firewall**: Only open necessary ports (22, 80, 443)
- **SSL**: Always use HTTPS in production
- **Updates**: Keep system and dependencies updated
- **Monitoring**: Set up log monitoring and alerts
- **Backups**: Regular backups of configuration and logs
- **Rate Limiting**: Nginx config includes rate limiting
- **Security Headers**: App includes security headers

## 📊 Performance Tips

1. **Caching**: Consider adding Redis for caching API responses
2. **Database**: For high traffic, consider storing data in a database
3. **Load Balancing**: Use multiple Gunicorn workers
4. **CDN**: Use a CDN for static assets if you add them
5. **Monitoring**: Set up monitoring with tools like Prometheus/Grafana

## 🐛 Troubleshooting

### Service Won't Start
```bash
# Check logs for errors
sudo journalctl -u vitrasa-api -n 50

# Check if port is in use
sudo netstat -tlnp | grep :5000

# Verify permissions
ls -la /opt/vitrasa-api/
```

### Nginx Configuration Issues
```bash
# Test nginx config
sudo nginx -t

# Check nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### SSL Certificate Issues
```bash
# Check certificate status
sudo certbot certificates

# Renew certificates
sudo certbot renew --dry-run
```

## 📞 Support

If you encounter issues:
1. Check the logs first
2. Verify all configuration files
3. Ensure your domain DNS is properly configured
4. Check firewall settings

Your API should be available at `https://yourdomain.com` once properly configured!
