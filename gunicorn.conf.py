# Gunicorn configuration file for production

# Server socket
bind = "127.0.0.1:5000"
backlog = 2048

# Worker processes
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 5

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "/var/log/vitrasa/access.log"
errorlog = "/var/log/vitrasa/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "vitrasa-api"

# Daemon mode
daemon = False
pidfile = "/var/run/vitrasa/vitrasa.pid"

# User/group to run as (change these to your user)
# user = "vitrasa"
# group = "vitrasa"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Performance
preload_app = True
enable_stdio_inheritance = True
