#!/usr/bin/env fish

# 测试 Docker Bake 配置

echo "🧪 测试 Docker Bake 配置"
echo ""

# 检查 docker-bake.hcl 是否存在
if not test -f docker-bake.hcl
    echo "❌ 错误: docker-bake.hcl 文件不存在"
    exit 1
end

echo "✅ docker-bake.hcl 文件存在"
echo ""

# 显示 bake 配置
echo "📋 Bake 配置:"
echo "─────────────────────────────────────────"
docker buildx bake --print
echo "─────────────────────────────────────────"
echo ""

# 测试构建（不推送）
echo "🔨 测试构建（本地）..."
echo ""

docker buildx bake \
    --set "bot.tags=hf-papers-bot:test" \
    --set "bot.platforms=linux/amd64" \
    --load

if test $status -eq 0
    echo ""
    echo "✅ 构建成功！"
    echo ""
    echo "📦 测试镜像已创建: hf-papers-bot:test"
    echo ""
    echo "🚀 运行测试:"
    echo "   docker run --rm hf-papers-bot:test python --version"
    echo ""
else
    echo ""
    echo "❌ 构建失败"
    exit 1
end
