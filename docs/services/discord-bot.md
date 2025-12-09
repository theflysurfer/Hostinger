# Discord Voice Bot

**Status:** Production
**Type:** Shared Service / Bot
**Container:** `discord-voice-bot`
**Image:** `discord-bot_discord-bot:latest` (617 MB)
**Uptime:** 3+ weeks
**Health:** ⚠️ Unhealthy (requires investigation)

---

## Overview

Bot Discord pour automatisation vocale et interactions avec les serveurs Discord.

---

## Technical Details

### Container Configuration

```yaml
Container Name: discord-voice-bot
Image: discord-bot_discord-bot:latest
Image Size: 617 MB
Network: Internal only (no exposed ports)
Status: Running (unhealthy)
Restart Policy: Auto-restart
```

### Ports

- **No external ports** - Bot connects to Discord API

### Environment

- Discord Bot Token (configured via environment variables)
- Voice processing capabilities

---

## Deployment

### Docker Compose

Location: `/opt/discord-bot/` (to be confirmed)

```yaml
version: '3.8'
services:
  discord-voice-bot:
    image: discord-bot_discord-bot:latest
    container_name: discord-voice-bot
    restart: unless-stopped
    environment:
      - DISCORD_TOKEN=${DISCORD_TOKEN}
    # Add other configuration as needed
```

### Start/Stop

```bash
# Start
docker start discord-voice-bot

# Stop
docker stop discord-voice-bot

# Restart
docker restart discord-voice-bot

# Logs
docker logs -f discord-voice-bot
```

---

## Health Check

**Current Status:** ⚠️ Unhealthy

### Troubleshooting

```bash
# Check container status
docker ps -a | grep discord

# View logs
docker logs --tail 100 discord-voice-bot

# Check health
docker inspect discord-voice-bot | grep -A 10 Health
```

### Common Issues

1. **Bot Token Expired**
   - Verify token in Discord Developer Portal
   - Update environment variable

2. **Voice Connection Issues**
   - Check network connectivity
   - Verify voice permissions

3. **Memory Issues**
   - Monitor container memory usage
   - Adjust resource limits if needed

---

## Maintenance

### Regular Tasks

- **Daily:** Monitor health status
- **Weekly:** Check logs for errors
- **Monthly:** Update Discord.py and dependencies

### Updates

```bash
# Pull latest image
docker pull discord-bot_discord-bot:latest

# Restart with new image
docker stop discord-voice-bot
docker rm discord-voice-bot
docker-compose up -d
```

---

## Monitoring

### Key Metrics

- Container uptime
- Memory usage
- Discord API latency
- Voice connection status

### Logs Location

```bash
docker logs discord-voice-bot
```

---

## Dependencies

- Discord API
- Voice processing libraries
- Python runtime

---

## Security

- Bot token stored in environment variables
- No external port exposure
- Internal Docker network only

---

## Related Documentation

- [Telegram Bot](telegram-bot.md) - Similar bot for Telegram
- [Registry](../applications/registry.yml) - Application registry

---

## Action Items

- [ ] Investigate unhealthy status
- [ ] Document Discord server connections
- [ ] Add health check configuration
- [ ] Confirm deployment location
- [ ] Add to registry.yml

---

**Last Updated:** 2025-12-04
**Maintainer:** DevOps Team
