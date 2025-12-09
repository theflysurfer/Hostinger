# Services Status - Docker Containers

**Auto-généré** : État actuel des conteneurs Docker sur srv759970.

---

## 🟢 Conteneurs Actifs

```
NAMES                        STATUS                    PORTS
nervous_carver               Up 26 seconds             
downto40-streamlit           Up 3 hours                0.0.0.0:8509->8501/tcp, [::]:8509->8501/tcp
memvid-worker                Up 21 hours (unhealthy)   8503/tcp
memvid-ui                    Up 21 hours (healthy)     0.0.0.0:8507->8501/tcp, [::]:8507->8501/tcp
memvid-api                   Up 21 hours (healthy)     0.0.0.0:8506->8503/tcp, [::]:8506->8503/tcp
ragflow-server               Up 23 hours               0.0.0.0:5678-5679->5678-5679/tcp, [::]:5678-5679->5678-5679/tcp, 0.0.0.0:9382->9382/tcp, [::]:9382->9382/tcp, 0.0.0.0:9504->80/tcp, [::]:9504->80/tcp, 0.0.0.0:9500->9380/tcp, [::]:9500->9380/tcp, 0.0.0.0:9501->9381/tcp, [::]:9501->9381/tcp
ragflow-es-01                Up 23 hours (healthy)     9300/tcp, 0.0.0.0:1220->9200/tcp, [::]:1220->9200/tcp
ragflow-minio                Up 23 hours (healthy)     0.0.0.0:9502->9000/tcp, [::]:9502->9000/tcp, 0.0.0.0:9503->9001/tcp, [::]:9503->9001/tcp
ragflow-mysql                Up 23 hours (healthy)     33060/tcp, 0.0.0.0:5456->3306/tcp, [::]:5456->3306/tcp
ragflow-redis                Up 23 hours (healthy)     0.0.0.0:6381->6379/tcp, [::]:6381->6379/tcp
dashy                        Up 29 hours (healthy)     0.0.0.0:4000->8080/tcp, [::]:4000->8080/tcp
langchain-service            Up 3 days (healthy)       0.0.0.0:5000->5000/tcp, [::]:5000->5000/tcp
telegram-voice-bot           Up 4 days (healthy)       
human-chain-frontend         Up 4 days (healthy)       0.0.0.0:3333->80/tcp, [::]:3333->80/tcp
human-chain-backend          Up 4 days (unhealthy)     0.0.0.0:8888->8000/tcp, [::]:8888->8000/tcp
discord-voice-bot            Up 4 days (unhealthy)     
portainer                    Up 4 days                 127.0.0.1:9000->9000/tcp, 8000/tcp, 127.0.0.1:9443->9443/tcp
mkdocs                       Up 4 days                 0.0.0.0:8005->8000/tcp, [::]:8005->8000/tcp
nginx-clemence               Up 6 hours                0.0.0.0:9002->80/tcp, [::]:9002->80/tcp
wp-cli-clemence              Up 6 hours                
wordpress-clemence           Up 6 hours                9000/tcp
mysql-clemence               Up 6 hours                3306/tcp, 33060/tcp
glances                      Up 4 days                 127.0.0.1:61208->61208/tcp, 61209/tcp
postgres-exporter            Up 4 days                 127.0.0.1:9187->9187/tcp
postgresql-shared            Up 4 days (healthy)       127.0.0.1:5432->5432/tcp
redis-shared                 Up 4 days (healthy)       127.0.0.1:6379->6379/tcp
rq-exporter-whisperx         Up 4 days                 0.0.0.0:9726->9726/tcp, [::]:9726->9726/tcp
rq-exporter-faster-whisper   Up 4 days                 0.0.0.0:9727->9726/tcp, [::]:9727->9726/tcp
faster-whisper-worker        Up 4 days                 8003/tcp
```

**Total conteneurs actifs**: 0

## 📊 Statistiques

```
NAME                         CPU %     MEM USAGE / LIMIT
nervous_carver               280.38%   742.1MiB / 15.62GiB
downto40-streamlit           0.00%     98.37MiB / 15.62GiB
memvid-worker                0.06%     39.73MiB / 15.62GiB
memvid-ui                    0.00%     34.5MiB / 15.62GiB
memvid-api                   0.17%     565.4MiB / 15.62GiB
ragflow-server               0.22%     1.914GiB / 15.62GiB
ragflow-es-01                0.30%     918.7MiB / 1GiB
ragflow-minio                0.02%     222.5MiB / 15.62GiB
ragflow-mysql                0.71%     378MiB / 15.62GiB
ragflow-redis                2.96%     5.246MiB / 15.62GiB
dashy                        0.03%     132MiB / 15.62GiB
langchain-service            0.15%     69.01MiB / 1GiB
telegram-voice-bot           0.00%     36.63MiB / 512MiB
human-chain-frontend         0.00%     6.008MiB / 15.62GiB
human-chain-backend          0.16%     56.08MiB / 15.62GiB
discord-voice-bot            2.40%     35.51MiB / 512MiB
portainer                    0.04%     20.91MiB / 15.62GiB
mkdocs                       0.06%     52.41MiB / 15.62GiB
nginx-clemence               0.00%     4.941MiB / 15.62GiB
```

## 🔴 Conteneurs Arrêtés (5 derniers)

```
NAMES                   STATUS
xtts-streamlit          Exited (137) 2 hours ago
xtts-api                Exited (0) 2 hours ago
wp-cli-solidarlink      Exited (137) 7 hours ago
nginx-solidarlink       Exited (0) 7 hours ago
wordpress-solidarlink   Exited (0) 7 hours ago
```
