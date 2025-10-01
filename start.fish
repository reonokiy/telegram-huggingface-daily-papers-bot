#!/usr/bin/env fish

# 启动脚本 - HuggingFace Papers Bot

# 设置环境变量（也可以从 .env 文件加载）
# set -x TELEGRAM_BOT_TOKEN "your_token_here"
# set -x TELEGRAM_CHANNEL_ID "@your_channel"
# set -x CHECK_INTERVAL "3600"

# 加载 .env 文件
if test -f .env
    while read -l line
        if not string match -q "#*" $line
            and not string match -q "" $line
            set -l parts (string split "=" $line)
            set -gx $parts[1] $parts[2]
        end
    end < .env
end

# 激活虚拟环境并运行
source .venv/bin/activate.fish
python main.py
