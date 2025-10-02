#!/usr/bin/env fish

# GitHub Actions Docker 构建快速参考

echo "🐳 Docker 构建快速参考"
echo "════════════════════════════════════════════════════════"
echo ""

echo "📦 镜像地址:"
echo "   ghcr.io/reonokiy/telegram-huggingface-daily-papers-bot"
echo ""

echo "🏷️  标签策略:"
echo "   • main 分支推送    → :latest"
echo "   • 标签推送 v1.0.0  → :v1.0.0 + :latest"
echo "   • Pull Request     → :pr-{number} (不推送)"
echo ""

echo "🚀 发布新版本:"
echo "   git tag v1.0.0"
echo "   git push origin v1.0.0"
echo "   # GitHub Actions 自动构建并推送"
echo ""

echo "📥 拉取镜像:"
echo "   docker pull ghcr.io/reonokiy/telegram-huggingface-daily-papers-bot:latest"
echo ""

echo "🔧 本地测试:"
echo "   # 查看配置"
echo "   docker buildx bake --print"
echo ""
echo "   # 本地构建"
echo "   docker buildx bake --set \"bot.platforms=linux/amd64\" --load"
echo ""
echo "   # 运行测试脚本"
echo "   ./tests/test_docker_bake.fish"
echo ""

echo "🖥️  支持平台:"
echo "   • linux/amd64  (x86_64)"
echo "   • linux/arm64  (ARM64/Apple Silicon)"
echo ""

echo "📋 查看构建状态:"
echo "   https://github.com/reonokiy/telegram-huggingface-daily-papers-bot/actions"
echo ""

echo "📖 详细文档:"
echo "   • docs/GITHUB_ACTIONS.md      - GitHub Actions 配置"
echo "   • docs/DOCKER_BUILD_SUMMARY.md - 构建总结"
echo "   • docs/DOCKER.md               - Docker 部署指南"
echo ""

echo "════════════════════════════════════════════════════════"
