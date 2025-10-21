# Headers Proxy Standards

Configuration des headers HTTP pour reverse proxy Nginx.

## Headers de Base

```nginx
proxy_http_version 1.1;
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_set_header X-Forwarded-Host $host;
```

## Headers pour WebSocket

```nginx
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
proxy_buffering off;
```

## Headers pour Upload de Fichiers

```nginx
client_max_body_size 500M;
proxy_request_buffering off;
```

## Timeouts Longs (API transcription, etc.)

```nginx
proxy_read_timeout 1800;      # 30 minutes
proxy_connect_timeout 300;    # 5 minutes
proxy_send_timeout 300;       # 5 minutes
```

## Exemple Complet

```nginx
location / {
    # Headers de base
    proxy_pass http://localhost:8080;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host $host;

    # Support WebSocket
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_buffering off;

    # Upload de fichiers volumineux
    client_max_body_size 500M;

    # Timeouts
    proxy_read_timeout 1800;
    proxy_connect_timeout 300;
    proxy_send_timeout 300;
}
```

## Utilisé dans

- WhisperX API
- Faster-Whisper API
- Dashy
- Dozzle
- Grafana
- Tous les services derrière reverse proxy
