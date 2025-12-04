# Nginx Debugging & Diagnostics

Quick reference for troubleshooting Nginx issues.

## Testing Configuration

```bash
# Test configuration syntax
nginx -t

# View compiled configuration (all sites)
nginx -T

# View specific site configuration
nginx -T | grep -A 50 'server_name mon-site.srv759970.hstgr.cloud'

# View which server block handles a domain
nginx -T | grep -B 10 'server_name mon-site.srv759970.hstgr.cloud'
```

## Viewing Logs

```bash
# Real-time access and error logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Combined logs
tail -f /var/log/nginx/access.log /var/log/nginx/error.log

# Site-specific logs
tail -f /var/log/nginx/mon-site-access.log

# Filter by domain
tail -f /var/log/nginx/access.log | grep 'mon-site.srv759970.hstgr.cloud'
```

## Diagnostic Commands

### Configuration Validation

```bash
# List available sites
ls -la /etc/nginx/sites-available/

# List enabled sites (symlinks)
ls -la /etc/nginx/sites-enabled/

# View all server names
nginx -T | grep 'server_name' | grep -v '#' | sort | uniq

# View all proxy_pass entries (backend ports)
nginx -T | grep 'proxy_pass' | sort | uniq

# View all listen directives
nginx -T | grep 'listen' | grep -v '#' | sort | uniq
```

### Process Status

```bash
# Check service status
systemctl status nginx

# Reload configuration (no interruption)
systemctl reload nginx

# Restart service (brief interruption)
systemctl restart nginx
```

### Connection Testing

```bash
# Test site with Host header
curl -I -H 'Host: mon-site.srv759970.hstgr.cloud' http://localhost/

# Follow HTTP redirections
curl -L -I http://mon-site.srv759970.hstgr.cloud/

# View response headers
curl -v http://mon-site.srv759970.hstgr.cloud/
```

### SSL Certificate Checking

```bash
# View served certificate
openssl s_client -connect mon-site.srv759970.hstgr.cloud:443 -servername mon-site.srv759970.hstgr.cloud | openssl x509 -noout -subject -issuer

# List installed certificates
ls -la /etc/letsencrypt/live/
```

### Network Analysis

```bash
# Monitor incoming requests on port 80
tcpdump -i any port 80 -A

# Watch logs while making request
tail -f /var/log/nginx/access.log &
curl http://mon-site.srv759970.hstgr.cloud/
```

## Advanced Debugging

### Enable Debug Logs

Add to nginx configuration:

```nginx
error_log /var/log/nginx/error.log debug;
```

Then reload: `systemctl reload nginx`

## See Also

- [Configuration Reference](proxy-config.md)
- [../../infrastructure/nginx.md](../../infrastructure/nginx.md)
- [../../guides/infrastructure/nginx-troubleshooting.md](../../guides/infrastructure/nginx-troubleshooting.md)
