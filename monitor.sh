#!/bin/bash

# Simple monitoring script for Vitrasa API
# Add to crontab to run every 5 minutes: */5 * * * * /opt/vitrasa-api/monitor.sh

LOG_FILE="/var/log/vitrasa/monitor.log"
API_URL="http://localhost:5000/api/health"
SERVICE_NAME="vitrasa-api"

# Function to log with timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> $LOG_FILE
}

# Check if service is running
if ! systemctl is-active --quiet $SERVICE_NAME; then
    log "ERROR: $SERVICE_NAME service is not running. Attempting to restart..."
    systemctl restart $SERVICE_NAME
    sleep 10
    
    if systemctl is-active --quiet $SERVICE_NAME; then
        log "SUCCESS: $SERVICE_NAME service restarted successfully"
    else
        log "CRITICAL: Failed to restart $SERVICE_NAME service"
        # Send alert email (configure postfix/sendmail first)
        # echo "Vitrasa API service failed to restart" | mail -s "API Alert" admin@yourdomain.com
    fi
fi

# Check API health endpoint
response=$(curl -s -w "%{http_code}" -o /dev/null $API_URL 2>/dev/null)

if [ "$response" != "200" ]; then
    log "WARNING: API health check failed (HTTP $response). Service may be unresponsive."
else
    # Test actual API endpoint
    test_response=$(curl -s -w "%{http_code}" -o /dev/null "http://localhost:5000/api/stop/20195" 2>/dev/null)
    if [ "$test_response" != "200" ]; then
        log "WARNING: API test endpoint failed (HTTP $test_response)"
    fi
fi

# Check disk space
disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$disk_usage" -gt 80 ]; then
    log "WARNING: Disk usage is at ${disk_usage}%"
fi

# Check memory usage
memory_usage=$(free | awk 'NR==2{printf "%.2f", $3*100/$2}')
if (( $(echo "$memory_usage > 90" | bc -l) )); then
    log "WARNING: Memory usage is at ${memory_usage}%"
fi
