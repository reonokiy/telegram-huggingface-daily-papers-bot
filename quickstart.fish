#!/usr/bin/env fish

# 🚀 快速启动脚本

echo "🤖 HuggingFace Daily Papers Bot - 快速启动"
echo "=========================================="
echo ""

# 检查虚拟环境
if not test -d .venv
    echo "⚠️  虚拟环境不存在，正在创建..."
    uv sync
    echo "✅ 虚拟环境创建完成"
else
    echo "✅ 虚拟环境已存在"
end

# 激活虚拟环境
source .venv/bin/activate.fish

# 检查环境变量
if not test -f .env
    echo ""
    echo "⚠️  .env 文件不存在"
    if test -f .env.example
        echo "📝 从 .env.example 复制..."
        cp .env.example .env
        echo "✅ 已创建 .env 文件"
        echo ""
        echo "⚠️  请编辑 .env 文件，填入你的配置："
        echo "   - TELEGRAM_BOT_TOKEN"
        echo "   - TELEGRAM_CHANNEL_ID"
        echo ""
        echo "编辑完成后，再次运行此脚本启动 Bot"
        exit 1
    else
        echo "❌ 未找到 .env.example 文件"
        exit 1
    end
end

# 加载环境变量
echo "📥 加载环境变量..."
set -l env_loaded 0
while read -l line
    if not string match -q "#*" $line
        and not string match -q "" $line
        set -l parts (string split "=" $line)
        if test (count $parts) -eq 2
            set -gx $parts[1] $parts[2]
            set env_loaded 1
        end
    end
end < .env

if test $env_loaded -eq 0
    echo "⚠️  环境变量加载失败，请检查 .env 文件"
    exit 1
end

# 检查必需的环境变量
if not set -q TELEGRAM_BOT_TOKEN
    echo "❌ 缺少 TELEGRAM_BOT_TOKEN，请在 .env 中配置"
    exit 1
end

if not set -q TELEGRAM_CHANNEL_ID
    echo "❌ 缺少 TELEGRAM_CHANNEL_ID，请在 .env 中配置"
    exit 1
end

echo "✅ 环境变量配置正确"
echo ""

# 创建数据目录
if not test -d data
    mkdir -p data
    echo "✅ 创建数据目录"
end

# 显示配置
echo "📋 当前配置："
echo "   Bot Token: "(string sub -l 10 $TELEGRAM_BOT_TOKEN)"..."
echo "   Channel ID: $TELEGRAM_CHANNEL_ID"
echo "   Check Interval: "(set -q CHECK_INTERVAL; and echo $CHECK_INTERVAL; or echo "3600")" 秒"
echo ""

# 询问运行模式
echo "请选择运行模式："
echo "  1) 测试爬虫（不推送）"
echo "  2) 单次运行（测试推送）"
echo "  3) 持续运行（生产模式）"
echo ""
read -P "请输入选项 (1/2/3): " choice

switch $choice
    case 1
        echo ""
        echo "🧪 运行测试..."
        ./tests/test.fish
    case 2
        echo ""
        echo "🔄 单次运行模式..."
        python main.py --once
    case 3
        echo ""
        echo "🚀 启动 Bot（持续运行）..."
        echo "按 Ctrl+C 停止"
        echo ""
        python main.py
    case '*'
        echo "❌ 无效选项"
        exit 1
end
