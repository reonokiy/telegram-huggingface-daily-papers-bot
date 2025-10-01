# 🐳 Docker 部署指南

本文档介绍如何使用 Docker 部署 HuggingFace Daily Papers Bot。

## 快速开始

### 1. 准备环境变量

创建 `.env` 文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的配置：

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=@your_channel
CHECK_INTERVAL=3600

# 可选：S3 配置
S3_BUCKET=hf-papers
S3_ENDPOINT=https://s3.amazonaws.com
S3_REGION=us-east-1
S3_ACCESS_KEY=your_access_key
S3_SECRET_KEY=your_secret_key
```

### 2. 使用 Docker Compose（推荐）

启动服务：

```bash
docker-compose up -d
```

查看日志：

```bash
docker-compose logs -f
```

停止服务：

```bash
docker-compose down
```

### 3. 使用 Docker 命令

构建镜像：

```bash
docker build -t hf-papers-bot .
```

运行容器：

```bash
docker run -d \
  --name hf-papers-bot \
  --restart unless-stopped \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  hf-papers-bot
```

查看日志：

```bash
docker logs -f hf-papers-bot
```

停止容器：

```bash
docker stop hf-papers-bot
docker rm hf-papers-bot
```

## 多平台构建

使用 Docker Buildx 构建多平台镜像：

### 创建 Builder

```bash
docker buildx create --name mybuilder --use
docker buildx inspect --bootstrap
```

### 使用 Docker Bake

```bash
# 构建本地镜像
docker buildx bake bot-local

# 构建并推送多平台镜像
docker buildx bake bot --push
```

### 指定版本标签

```bash
TAG=v1.0.0 docker buildx bake bot --push
```

## 数据持久化

容器会将数据存储在 `/app/data` 目录，通过 Volume 映射到宿主机：

```yaml
volumes:
  - ./data:/app/data
```

数据目录结构：

```
data/
├── papers_cache.json          # 论文缓存
└── YYYY/                      # 按年份分类
    └── MM/                    # 按月份分类
        ├── papers_YYYY-MM-DD.parquet  # 每日数据
        └── papers_YYYY-MM_merged.parquet  # 月度归档
```

## 资源限制

在 `docker-compose.yml` 中配置了资源限制：

```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'      # 最多使用 1 个 CPU
      memory: 512M     # 最多使用 512MB 内存
    reservations:
      cpus: '0.5'      # 保留 0.5 个 CPU
      memory: 256M     # 保留 256MB 内存
```

可以根据实际需求调整。

## 日志管理

Docker Compose 配置了日志轮转：

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"   # 单个日志文件最大 10MB
    max-file: "3"     # 保留最近 3 个日志文件
```

查看日志：

```bash
# 实时查看日志
docker-compose logs -f

# 查看最近 100 行
docker-compose logs --tail=100

# 查看特定时间段
docker-compose logs --since 2025-10-01T00:00:00
```

## 健康检查

容器配置了健康检查：

```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
  interval: 5m        # 每 5 分钟检查一次
  timeout: 10s        # 超时时间 10 秒
  retries: 3          # 重试 3 次
  start_period: 30s   # 启动后 30 秒开始检查
```

查看健康状态：

```bash
docker ps
# 或
docker inspect hf-papers-bot | grep -A 10 Health
```

## 故障排查

### 容器无法启动

1. 检查环境变量配置：
   ```bash
   docker-compose config
   ```

2. 查看详细日志：
   ```bash
   docker-compose logs
   ```

3. 检查权限问题：
   ```bash
   ls -la data/
   ```

### 无法推送到 Telegram

1. 进入容器检查：
   ```bash
   docker exec -it hf-papers-bot /bin/bash
   python -c "import os; print(os.getenv('TELEGRAM_BOT_TOKEN'))"
   ```

2. 测试网络连接：
   ```bash
   docker exec -it hf-papers-bot curl https://api.telegram.org
   ```

### 数据没有保存

1. 检查 Volume 挂载：
   ```bash
   docker inspect hf-papers-bot | grep -A 10 Mounts
   ```

2. 检查容器内文件：
   ```bash
   docker exec -it hf-papers-bot ls -la /app/data
   ```

## 生产环境部署

### 使用 Docker Swarm

创建 Docker Swarm 服务：

```bash
docker swarm init

docker stack deploy -c docker-compose.yml hf-papers
```

查看服务状态：

```bash
docker service ls
docker service logs -f hf-papers_bot
```

### 使用 Kubernetes

创建 Deployment：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hf-papers-bot
spec:
  replicas: 1
  selector:
    matchLabels:
      app: hf-papers-bot
  template:
    metadata:
      labels:
        app: hf-papers-bot
    spec:
      containers:
      - name: bot
        image: ghcr.io/yourusername/hf-papers-bot:latest
        envFrom:
        - secretRef:
            name: hf-papers-secrets
        volumeMounts:
        - name: data
          mountPath: /app/data
        resources:
          limits:
            cpu: "1"
            memory: "512Mi"
          requests:
            cpu: "500m"
            memory: "256Mi"
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: hf-papers-data
```

创建 Secret：

```bash
kubectl create secret generic hf-papers-secrets \
  --from-literal=TELEGRAM_BOT_TOKEN=your_token \
  --from-literal=TELEGRAM_CHANNEL_ID=@your_channel
```

## 自动化部署

### GitHub Actions

创建 `.github/workflows/docker.yml`：

```yaml
name: Docker Build and Push

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to GitHub Container Registry
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push
        run: |
          TAG=${GITHUB_REF#refs/tags/}
          docker buildx bake bot --push --set bot.tags=ghcr.io/${{ github.repository }}:${TAG}
```

## 监控和告警

### Prometheus 监控

可以添加自定义的健康检查端点来支持 Prometheus 监控。

### 日志聚合

将日志发送到 ELK Stack 或其他日志平台：

```yaml
logging:
  driver: "syslog"
  options:
    syslog-address: "tcp://logserver:514"
    tag: "hf-papers-bot"
```

## 备份策略

### 数据备份

定期备份 data 目录：

```bash
# 手动备份
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# 自动备份脚本（crontab）
0 2 * * * cd /path/to/bot && tar -czf backups/backup-$(date +\%Y\%m\%d).tar.gz data/
```

### 恢复数据

```bash
tar -xzf backup-20251002.tar.gz
docker-compose restart
```

## 更新和维护

### 更新镜像

```bash
# 拉取最新镜像
docker-compose pull

# 重启服务
docker-compose up -d
```

### 清理旧镜像

```bash
docker image prune -a
```

## 性能优化

### 减小镜像大小

当前 Dockerfile 使用了多阶段构建，已经相对优化。可以进一步优化：

1. 使用 Alpine 基础镜像（需要处理依赖问题）
2. 移除不必要的依赖
3. 压缩 Python 字节码

### 提升启动速度

1. 使用镜像缓存
2. 预热数据
3. 优化依赖安装顺序

## 安全建议

1. **不要在镜像中包含敏感信息**：使用环境变量或 Secret
2. **使用非 root 用户运行**：Dockerfile 已配置
3. **定期更新基础镜像**：修复安全漏洞
4. **限制容器权限**：使用 `--read-only` 等选项
5. **扫描镜像漏洞**：使用 `docker scan` 或 Trivy

```bash
docker scan hf-papers-bot
```

## 总结

使用 Docker 部署的优势：

- ✅ 环境一致性
- ✅ 快速部署
- ✅ 易于扩展
- ✅ 资源隔离
- ✅ 便于维护

推荐使用 Docker Compose 进行部署，简单且强大！
