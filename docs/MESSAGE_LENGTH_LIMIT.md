# Telegram 消息长度限制处理

## 问题

Telegram Bot API 对消息长度有严格限制：

```
❌ Message caption is too long
```

## Telegram 消息长度限制

1. **带图片的消息（Caption）**: 最大 **1024** 字符
2. **纯文本消息（Text）**: 最大 **4096** 字符

## 解决方案

### 智能长度控制

代码自动根据消息类型设置不同的长度限制：

```python
# 带图片的消息
if paper.hero_image:
    message = self.format_paper_message(paper, translated_abstract, max_length=1000)
    await self.bot.send_photo(...)

# 纯文本消息
else:
    message = self.format_paper_message(paper, translated_abstract, max_length=4000)
    await self.bot.send_message(...)
```

### 摘要截取策略

`format_paper_message()` 函数会智能截取摘要：

1. 预估其他部分长度（标题、作者、链接等约200字符）
2. 计算摘要可用空间
3. 如果摘要过长，截取并添加 "..."

```python
if max_length:
    other_parts_length = len(title) + len(authors) + 200
    available_for_abstract = max_length - other_parts_length
    
    if available_for_abstract > 100:
        if len(abstract) > available_for_abstract:
            abstract = abstract[:available_for_abstract - 3] + "..."
```

## 长度分配

对于带图片的消息（1024字符限制）：

| 部分 | 估算长度 | 说明 |
|------|---------|------|
| 标题 | 50-200 | 论文标题（转义后） |
| 作者 | 50-150 | 最多5位作者 |
| 摘要 | 400-600 | 动态调整 |
| 链接 | 100-150 | HuggingFace + ArXiv + GitHub |
| 统计 | 30-50 | Upvotes + Stars |
| 格式字符 | 50-100 | Markdown标记、换行等 |

**总计**: ~1000字符（留有余量）

## 示例

### 原始摘要（很长）

```
This paper presents a comprehensive study of reinforcement learning 
algorithms applied to large language models... [2000+ characters]
```

### 截取后（适合Caption）

```
This paper presents a comprehensive study of reinforcement learning 
algorithms applied to large language models for improving reasoning 
capabilities through iterative self-improvement and value-based 
optimization frameworks...
```

### 显示效果

```
*DeepSearch: Improving LLM Reasoning*

👥 Authors: John Doe, Jane Smith, et al. (8 authors)

📄 Abstract: This paper presents a comprehensive study of 
reinforcement learning algorithms applied to large language 
models for improving reasoning capabilities...

📊 👍 118 upvotes | ⭐ 184 stars

🔗 Read More： HuggingFace | ArXiv | GitHub
```

## 优势

✅ **自动适配**: 根据是否有图片自动调整长度
✅ **智能截取**: 优先保留完整的标题和作者信息
✅ **用户友好**: 截取处添加"..."提示有省略
✅ **稳定可靠**: 预留安全余量，避免边界情况

## 如果仍然过长

如果某些论文的标题或作者名单特别长，导致消息仍然超长：

1. **增加截取**: 可以调整 `max_length` 为更小的值（如900）
2. **简化作者**: 减少显示的作者数量（如前3位）
3. **移除图片**: 对超长内容使用纯文本模式

## 调试

如果需要调试消息长度：

```python
message = self.format_paper_message(paper, translated_abstract, max_length=1000)
print(f"消息长度: {len(message)} 字符")
print(f"是否超限: {len(message) > 1024}")
```

## 参考

- [Telegram Bot API - sendPhoto](https://core.telegram.org/bots/api#sendphoto)
- [Telegram Bot API - sendMessage](https://core.telegram.org/bots/api#sendmessage)
- Caption长度限制: 1024字符
- Message长度限制: 4096字符
