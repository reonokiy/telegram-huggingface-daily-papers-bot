# Telegram 频道配置指南

## 问题：推送失败 "Not Found"

如果你看到这个错误：
```
❌ 推送失败: Not Found
```

这说明 Bot 无法找到你配置的频道。请按照以下步骤检查和修复。

## 解决步骤

### 1. 创建 Telegram 频道

1. 打开 Telegram
2. 点击菜单 → "New Channel"
3. 输入频道名称和描述
4. 选择频道类型：
   - **公开频道**: 有一个 @username
   - **私有频道**: 通过链接邀请

### 2. 获取频道 ID

#### 方法 A: 公开频道（推荐）

如果你的频道是公开的：

1. 给频道设置一个用户名（例如：`my_papers_channel`）
2. 频道 ID 就是：`@my_papers_channel`

```bash
# .env
TELEGRAM_CHANNEL_ID=@my_papers_channel
```

#### 方法 B: 私有频道

如果你的频道是私有的，需要获取数字 ID：

1. 将 Bot 添加到频道（见第3步）
2. 使用 `@userinfobot` 或 `@raw_data_bot` 获取频道 ID
3. 转发频道的任意消息给这些 bot
4. Bot 会返回频道信息，包括 ID（格式：`-100xxxxxxxxxx`）

```bash
# .env
TELEGRAM_CHANNEL_ID=-1001234567890
```

### 3. 将 Bot 添加到频道

这是最关键的一步！

1. 打开你的频道
2. 点击频道名称 → "Administrators"
3. 点击 "Add Administrator"
4. 搜索你的 Bot 名称
5. 添加 Bot 为管理员
6. **必须授予以下权限**：
   - ✅ Post Messages（发送消息）
   - ✅ Edit Messages（可选）
   - ✅ Delete Messages（可选）

### 4. 验证配置

运行 Bot 时，它会自动验证频道访问权限：

```bash
uv run python main.py
```

你应该看到：

```
🔍 正在验证频道访问权限...
✅ 频道验证成功
   频道名称: My Papers Channel
   频道类型: channel
   频道ID: -1001234567890
   Bot状态: administrator
```

## 完整配置示例

### .env 文件

```bash
# Telegram Bot Token (从 @BotFather 获取)
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# 公开频道
TELEGRAM_CHANNEL_ID=@my_papers_channel

# 或私有频道
# TELEGRAM_CHANNEL_ID=-1001234567890

# 检查间隔（秒）
CHECK_INTERVAL=3600
```

## 常见问题

### Q: "Not Found" 错误

**原因**：
1. 频道 ID 错误
2. Bot 未被添加到频道
3. Bot 不是频道管理员

**解决**：
- 检查频道 ID 格式
- 确保 Bot 已添加到频道
- 确保 Bot 是管理员且有发送消息权限

### Q: 公开频道 vs 私有频道

**公开频道**：
- ✅ 配置简单（使用 @username）
- ✅ 任何人都可以搜索和加入
- ❌ 内容公开可见

**私有频道**：
- ✅ 需要邀请链接才能加入
- ✅ 内容仅对成员可见
- ❌ 配置稍复杂（需要获取数字 ID）

### Q: Bot 发送消息失败

确保 Bot 有以下权限：
1. 是频道的管理员
2. 有 "Post Messages" 权限
3. 频道没有限制 Bot 发送消息

### Q: 如何测试 Bot？

```bash
# 1. 启动 Bot
uv run python main.py

# 2. 观察日志
# 应该看到频道验证成功
# 然后开始检查和推送论文

# 3. 如果失败，查看错误信息
# Bot 会显示详细的诊断信息
```

## 创建 Bot 的完整流程

### 1. 创建 Bot

1. 在 Telegram 中搜索 `@BotFather`
2. 发送 `/newbot`
3. 按照提示设置 Bot 名称和用户名
4. 获取 Bot Token：`1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

### 2. 创建频道

1. 创建新频道
2. 设置为公开频道（设置用户名）
3. 记录频道 ID：`@your_channel`

### 3. 配置 Bot 权限

1. 进入频道设置
2. 添加 Bot 为管理员
3. 授予 "Post Messages" 权限

### 4. 配置环境变量

创建 `.env` 文件：

```bash
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHANNEL_ID=@your_channel
```

### 5. 启动 Bot

```bash
uv run python main.py
```

## 验证清单

在启动 Bot 之前，请确认：

- [ ] 已从 @BotFather 创建 Bot
- [ ] 已获取 Bot Token
- [ ] 已创建 Telegram 频道
- [ ] 已获取频道 ID（@username 或数字）
- [ ] Bot 已被添加到频道
- [ ] Bot 是频道管理员
- [ ] Bot 有 "Post Messages" 权限
- [ ] 已配置 .env 文件
- [ ] TOKEN 和 CHANNEL_ID 都正确填写

## 获取帮助

如果问题仍然存在：

1. 查看 Bot 启动时的验证信息
2. 确认频道 ID 格式正确
3. 尝试重新添加 Bot 到频道
4. 检查 Bot Token 是否正确
5. 查看 Telegram 是否有任何限制

## 测试命令

```bash
# 测试 Bot 连接
uv run python -c "
import asyncio
from telegram import Bot
bot = Bot('YOUR_BOT_TOKEN')
print(asyncio.run(bot.get_me()))
"

# 测试频道访问
uv run python -c "
import asyncio
from telegram import Bot
bot = Bot('YOUR_BOT_TOKEN')
print(asyncio.run(bot.get_chat('@your_channel')))
"
```

这些命令可以帮助你快速诊断问题。
