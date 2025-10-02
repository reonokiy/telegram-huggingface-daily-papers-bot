# Markdown V2 转义问题修复

## 问题

Telegram Bot API 使用 Markdown V2 格式时，某些字符是保留字符，必须用反斜杠转义。

常见错误：
```
❌ 推送失败: Can't parse entities: character '|' is reserved and must be escaped with the preceding '\'
```

## 原因

管道符 `|` 在 Markdown V2 中是特殊字符，用于表格分隔等用途，必须转义为 `\|`。

## 修复

在 `main.py` 的 `format_paper_message()` 函数中，所有用作分隔符的管道符都需要转义：

### 修复前

```python
# 统计信息
message += f"📊 {' | '.join(stats_parts)}\n\n"

# 链接
message += f"🔗 *Read More：* {' | '.join(links)}"
```

### 修复后

```python
# 统计信息 - 使用转义的管道符
message += f"📊 {' \\| '.join(stats_parts)}\n\n"

# 链接 - 使用转义的管道符
message += f"🔗 *Read More：* {' \\| '.join(links)}"
```

## Markdown V2 需要转义的字符

完整列表：
```
_ * [ ] ( ) ~ ` > # + - = | { } . !
```

我们的 `escape_markdown()` 函数已经处理了所有这些字符。

## 测试

修复后，消息应该正常发送：

```
📊 👍 118 upvotes \| ⭐ 184 stars

🔗 Read More： HuggingFace \| ArXiv \| GitHub
```

显示效果：
```
📊 👍 118 upvotes | ⭐ 184 stars

🔗 Read More： HuggingFace | ArXiv | GitHub
```

## 参考

- [Telegram Bot API - Formatting Options](https://core.telegram.org/bots/api#formatting-options)
- [Markdown V2 Style](https://core.telegram.org/bots/api#markdownv2-style)
