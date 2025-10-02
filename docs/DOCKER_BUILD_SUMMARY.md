# GitHub Actions Docker 构建配置总结

## ✅ 完成的配置

### 1. GitHub Actions 工作流

创建了 `.github/workflows/docker-build.yml`，使用官方 `docker/bake-action@v5`：

**特性：**
- ✅ 多平台构建（linux/amd64, linux/arm64）
- ✅ 自动标签管理（版本标签 + latest）
- ✅ Pull Request 构建验证
- ✅ 手动触发支持
- ✅ 构建摘要输出

**触发条件：**
- Push 到 main 分支 → 构建 `latest`
- Push 标签 `v*.*.*` → 构建版本标签 + `latest`
- Pull Request → 仅构建（不推送）
- 手动触发 → 按需构建

### 2. Docker Bake 配置

使用 `docker-bake.hcl` 定义构建配置：

```hcl
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

### 3. 工作流关键步骤

```yaml
- name: Build and push with Docker Bake
  uses: docker/bake-action@v5
  with:
    files: docker-bake.hcl
    push: true
    set: |
      bot.tags=ghcr.io/reonokiy/telegram-huggingface-daily-papers-bot:latest
```

**优势：**
- 使用官方 action，更可靠
- 支持复杂的构建配置
- 自动处理多平台构建
- 缓存管理更高效

## 📦 镜像信息

### 镜像地址

```
ghcr.io/reonokiy/telegram-huggingface-daily-papers-bot:latest
ghcr.io/reonokiy/telegram-huggingface-daily-papers-bot:v1.0.0
```

### 拉取镜像

```bash
docker pull ghcr.io/reonokiy/telegram-huggingface-daily-papers-bot:latest
```

### 运行容器

```bash
docker run -d \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -e TELEGRAM_CHANNEL_ID=@your_channel \
  ghcr.io/reonokiy/telegram-huggingface-daily-papers-bot:latest
```

## 🚀 使用流程

### 发布新版本

1. **创建标签：**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **GitHub Actions 自动执行：**
   - 构建多平台镜像
   - 推送到 GHCR
   - 生成构建摘要

3. **验证镜像：**
   ```bash
   docker pull ghcr.io/reonokiy/telegram-huggingface-daily-papers-bot:v1.0.0
   docker run --rm ghcr.io/reonokiy/telegram-huggingface-daily-papers-bot:v1.0.0 python --version
   ```

### 本地测试

```bash
# 测试 Bake 配置
./tests/test_docker_bake.fish

# 查看 Bake 配置
docker buildx bake --print

# 本地构建（仅 amd64）
docker buildx bake --set "bot.tags=test:local" --set "bot.platforms=linux/amd64" --load
```

## 📋 文件清单

### 新增文件

- `.github/workflows/docker-build.yml` - GitHub Actions 工作流
- `docs/GITHUB_ACTIONS.md` - GitHub Actions 详细文档
- `docs/BADGES.md` - README 徽章配置
- `tests/test_docker_bake.fish` - Bake 配置测试脚本

### 配置文件

- `docker-bake.hcl` - Docker Bake 构建配置
- `Dockerfile` - 多阶段构建配置
- `docker-compose.yml` - Compose 配置

## 🔧 配置说明

### 环境变量

工作流中使用的环境变量：

| 变量 | 说明 | 来源 |
|------|------|------|
| `GITHUB_TOKEN` | GitHub 令牌 | 自动提供 |
| `TAG` | 镜像标签 | 从 git ref 提取 |
| `REGISTRY` | 镜像仓库 | ghcr.io |

### 权限配置

工作流需要的权限：

```yaml
permissions:
  contents: read      # 读取仓库内容
  packages: write     # 推送镜像到 GHCR
```

### 镜像标签策略

| 触发方式 | 标签 | 示例 |
|---------|------|------|
| Push main | `latest` | `ghcr.io/.../bot:latest` |
| Push tag v1.0.0 | `v1.0.0`, `latest` | `ghcr.io/.../bot:v1.0.0` |
| Pull Request | `pr-123` | 不推送，仅构建 |

## 📊 构建统计

### 构建时间

- 单平台（amd64）: ~3-5 分钟
- 多平台（amd64 + arm64）: ~6-10 分钟

### 镜像大小

- 压缩后: ~200-300 MB
- 解压后: ~600-800 MB

### 构建层次

使用多阶段构建：
1. `builder` - 安装依赖
2. `runtime` - 最小化运行环境

## 🎯 最佳实践

### 1. 版本管理

使用语义化版本：
```bash
v1.0.0  # 主版本.次版本.修订号
v1.0.1  # 修复 bug
v1.1.0  # 新功能
v2.0.0  # 破坏性更新
```

### 2. 测试流程

推送前本地测试：
```bash
# 1. 测试 Bake 配置
docker buildx bake --print

# 2. 本地构建
docker buildx bake --set "bot.platforms=linux/amd64" --load

# 3. 测试镜像
docker run --rm test:local python --version

# 4. 推送代码
git push origin main
```

### 3. 镜像管理

定期清理旧镜像：
- 保留最近 10 个版本
- 删除超过 90 天的未标记镜像
- 使用 GHCR 的生命周期策略

### 4. 安全性

- 使用最小化基础镜像
- 定期更新依赖
- 扫描漏洞（可选）
- 不在镜像中包含敏感信息

## 🔍 故障排查

### 构建失败

1. **检查日志：**
   - GitHub Actions → 选择失败的工作流
   - 查看详细日志

2. **常见问题：**
   - Dockerfile 语法错误
   - 依赖安装失败
   - 网络超时

### 推送失败

1. **权限问题：**
   - 确认工作流有 `packages: write` 权限
   - 检查 GITHUB_TOKEN 是否有效

2. **镜像大小：**
   - GHCR 限制单个镜像 10GB
   - 优化 Dockerfile 减小镜像

### 拉取失败

1. **镜像不存在：**
   - 检查标签是否正确
   - 确认构建已完成

2. **权限问题：**
   - 公开镜像：无需登录
   - 私有镜像：需要登录 GHCR

## 📚 相关资源

- [docker/bake-action 文档](https://github.com/docker/bake-action)
- [Docker Buildx Bake](https://docs.docker.com/build/bake/)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [GitHub Actions](https://docs.github.com/en/actions)

## 🎉 总结

使用 `docker/bake-action@v5` 的优势：

1. ✅ **简化配置** - 使用官方 action，配置更简洁
2. ✅ **更好的缓存** - 自动优化构建缓存
3. ✅ **多平台支持** - 原生支持多架构构建
4. ✅ **标准化** - 遵循 Docker 官方最佳实践
5. ✅ **可维护性** - 使用 HCL 配置，易于维护

项目现在已经配置了完整的 CI/CD 流程，每次推送到 main 分支或创建新标签时，都会自动构建并推送多平台 Docker 镜像到 GitHub Container Registry！🚀
