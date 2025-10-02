# GitHub Actions 自动构建 Docker 镜像

## 概述

本项目使用 GitHub Actions 自动构建多平台 Docker 镜像并推送到 GitHub Container Registry (GHCR)。

## 工作流说明

### 触发条件

工作流会在以下情况下自动触发：

1. **推送到 main 分支** - 构建并推送 `latest` 标签
2. **推送标签** - 推送 `v*.*.*` 格式的标签（如 `v1.0.0`）时，构建并推送版本标签和 `latest` 标签
3. **Pull Request** - 仅构建镜像（不推送），用于验证构建是否成功
4. **手动触发** - 通过 GitHub Actions 页面手动触发

### 构建特性

- ✅ **多平台支持**：同时构建 `linux/amd64` 和 `linux/arm64`
- ✅ **Docker Bake**：使用 `docker-bake.hcl` 配置文件
- ✅ **自动标签**：自动生成版本标签和 `latest` 标签
- ✅ **GHCR 集成**：自动推送到 GitHub Container Registry

## 镜像地址

```
ghcr.io/reonokiy/telegram-huggingface-daily-papers-bot:latest
ghcr.io/reonokiy/telegram-huggingface-daily-papers-bot:v1.0.0
```

## 使用方法

### 1. 拉取镜像

```bash
# 拉取最新版本
docker pull ghcr.io/reonokiy/telegram-huggingface-daily-papers-bot:latest

# 拉取特定版本
docker pull ghcr.io/reonokiy/telegram-huggingface-daily-papers-bot:v1.0.0
```

### 2. 运行容器

```bash
docker run -d \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -e TELEGRAM_CHANNEL_ID=@your_channel \
  -e CHECK_INTERVAL=3600 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/papers_cache.json:/app/papers_cache.json \
  ghcr.io/reonokiy/telegram-huggingface-daily-papers-bot:latest
```

### 3. 使用 docker-compose

```yaml
version: '3.8'

services:
  bot:
    image: ghcr.io/reonokiy/telegram-huggingface-daily-papers-bot:latest
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - TELEGRAM_CHANNEL_ID=${TELEGRAM_CHANNEL_ID}
      - CHECK_INTERVAL=3600
    volumes:
      - ./data:/app/data
      - ./papers_cache.json:/app/papers_cache.json
    restart: unless-stopped
```

## 发布新版本

### 方法 1：使用 GitHub Releases（推荐）

1. 在 GitHub 上创建新的 Release
2. 创建新标签，格式：`v1.0.0`、`v1.0.1` 等
3. GitHub Actions 会自动构建并推送镜像

### 方法 2：使用命令行

```bash
# 创建标签
git tag v1.0.0

# 推送标签
git push origin v1.0.0

# GitHub Actions 会自动开始构建
```

### 方法 3：手动触发

1. 进入 GitHub Actions 页面
2. 选择 "Build and Push Docker Image" 工作流
3. 点击 "Run workflow" 按钮
4. 选择分支并运行

## 配置文件

### docker-bake.hcl

定义了镜像构建的配置：

```hcl
variable "TAG" {
  default = "latest"
}

variable "NAME" {
  default = "telegram-huggingface-daily-papers-bot"
}

variable "REGISTRY" {
  default = "ghcr.io/reonokiy"
}

target "bot" {
  dockerfile = "Dockerfile"
  tags = [
    "${REGISTRY}/${NAME}:${TAG}",
    "${REGISTRY}/${NAME}:latest"
  ]
  platforms = [
    "linux/amd64",
    "linux/arm64"
  ]
}
```

### .github/workflows/docker-build.yml

GitHub Actions 工作流配置：

- 设置 QEMU 和 Docker Buildx
- 登录 GHCR
- 使用官方 `docker/bake-action@v5` 构建多平台镜像
- 自动推送到 GHCR

**关键步骤：**

```yaml
- name: Build and push with Docker Bake
  uses: docker/bake-action@v5
  with:
    files: docker-bake.hcl
    push: true
    set: |
      bot.tags=ghcr.io/reonokiy/telegram-huggingface-daily-papers-bot:latest
```

## 查看构建状态

### GitHub Actions 页面

访问：`https://github.com/reonokiy/telegram-huggingface-daily-papers-bot/actions`

### 添加徽章到 README

```markdown
![Docker Build](https://github.com/reonokiy/telegram-huggingface-daily-papers-bot/actions/workflows/docker-build.yml/badge.svg)
```

显示效果：

![Docker Build](https://github.com/reonokiy/telegram-huggingface-daily-papers-bot/actions/workflows/docker-build.yml/badge.svg)

## 镜像权限设置

### 公开镜像

如果你想让镜像公开可访问：

1. 进入：`https://github.com/users/reonokiy/packages/container/telegram-huggingface-daily-papers-bot/settings`
2. 在 "Danger Zone" 中选择 "Change visibility"
3. 设置为 "Public"

### 私有镜像

如果镜像是私有的，需要登录才能拉取：

```bash
# 创建 Personal Access Token (PAT) with read:packages scope
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# 然后拉取镜像
docker pull ghcr.io/reonokiy/telegram-huggingface-daily-papers-bot:latest
```

## 本地测试构建

在推送到 GitHub 之前，可以在本地测试构建：

```bash
# 使用 docker buildx bake
docker buildx bake

# 构建并推送（需要先登录）
docker buildx bake --push

# 指定标签
docker buildx bake --set "bot.tags=ghcr.io/reonokiy/telegram-huggingface-daily-papers-bot:test"
```

## 故障排查

### 构建失败

1. 检查 GitHub Actions 日志
2. 确认 Dockerfile 语法正确
3. 验证 docker-bake.hcl 配置

### 推送失败

1. 检查 `GITHUB_TOKEN` 权限
2. 确认工作流有 `packages: write` 权限
3. 检查网络连接

### 镜像拉取失败

1. 确认镜像已成功推送
2. 检查镜像可见性（公开/私有）
3. 如果是私有镜像，确认已正确登录

## 相关资源

- [GitHub Container Registry 文档](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Docker Buildx Bake 文档](https://docs.docker.com/build/bake/)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
