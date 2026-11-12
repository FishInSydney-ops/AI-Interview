frozenfiah@192 local % docker compose ps
NAME                   IMAGE                                             COMMAND                   SERVICE   CREATED         STATUS                          PORTS
yunshu-local-minio-1   yunshu-local-minio:RELEASE.2025-10-15T17-29-55Z   "/usr/local/bin/mini…"   minio     6 minutes ago   Restarting (1) 53 seconds ago   
yunshu-local-mysql-1   mysql:8.4                                         "docker-entrypoint.s…"   mysql     6 minutes ago   Up 6 minutes (healthy)          127.0.0.1:3306->3306/tcp
yunshu-local-redis-1   redis:7.4-alpine                                  "docker-entrypoint.s…"   redis     6 minutes ago   Up 6 minutes (healthy)          127.0.0.1:6379->6379/tcp
frozenfiah@192 local % 
