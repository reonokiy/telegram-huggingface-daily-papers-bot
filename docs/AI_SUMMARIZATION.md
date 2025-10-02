# AI 智能摘要总结

## 功能概述

使用 AI (OpenAI) 智能总结论文摘要到指定长度，而不是简单截取。这样可以：

- ✅ 保留关键信息和技术术语
- ✅ 保持语义完整性
- ✅ 提供更好的阅读体验
- ✅ 自动适应不同的长度限制

## 工作流程

### 1. 带图片的消息（Caption限制1024字符）

```
原始摘要（可能很长）
    ↓
AI 总结到 ~300 字符
    ↓
AI 翻译（如果启用）
    ↓
格式化并发送
```

### 2. 纯文本消息（限制4096字符）

```
原始摘要
    ↓
AI 总结到 ~600 字符
    ↓
AI 翻译（如果启用）
    ↓
格式化并发送
```

## 实现细节

### `summarize_abstract()` 方法

```python
async def summarize_abstract(self, text: str, max_length: int = 300) -> str:
    """使用 AI 总结摘要到指定长度"""
    if not self.enable_translation or len(text) <= max_length:
        return text
    
    response = self.openai_client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": f"Summarize the following abstract to approximately {max_length} characters while preserving key points and technical terms."
            },
            {
                "role": "user",
                "content": text
            }
        ],
        temperature=0.3,
        max_tokens=200
    )
    
    return response.choices[0].message.content.strip()
```

### 智能处理流程

```python
async def send_paper(self, paper: Paper):
    if self.enable_translation and paper.abstract:
        if paper.hero_image:
            # 带图片：总结到300字符 → 翻译
            summarized = await self.summarize_abstract(paper.abstract, max_length=300)
            processed = await self.translate_text(summarized)
        else:
            # 纯文本：总结到600字符 → 翻译
            summarized = await self.summarize_abstract(paper.abstract, max_length=600)
            processed = await self.translate_text(summarized)
```

## 示例对比

### 原始摘要（1500字符）

```
This paper introduces DeepSearch, a novel reinforcement learning framework 
for enhancing reasoning capabilities in large language models. We propose 
a value-based optimization approach that iteratively improves model 
performance through self-play and reward modeling. Our method consists of 
three key components: (1) a policy network that generates candidate 
solutions, (2) a value network that estimates solution quality, and (3) 
a reward model trained on human preferences. We evaluate our approach on 
multiple benchmarks including mathematical reasoning, code generation, 
and natural language understanding tasks. Results show that DeepSearch 
achieves state-of-the-art performance, improving upon GPT-4 by 15% on 
MATH benchmark and 23% on HumanEval. Additionally, we demonstrate strong 
generalization capabilities across diverse problem domains...
[继续很长的内容]
```

### 简单截取（300字符）

```
This paper introduces DeepSearch, a novel reinforcement learning framework 
for enhancing reasoning capabilities in large language models. We propose 
a value-based optimization approach that iteratively improves model 
performance through self-play and reward modeling. Our method consists of 
three key...
```

❌ 问题：句子被截断，信息不完整

### AI 智能总结（300字符）

```
DeepSearch is a reinforcement learning framework that enhances LLM 
reasoning through value-based optimization and self-play. It uses policy 
networks, value networks, and reward models to iteratively improve 
performance. Achieves SOTA results: +15% on MATH, +23% on HumanEval.
```

✅ 优点：保留关键信息，语义完整，更易读

### AI 总结 + 翻译（中文）

```
DeepSearch 是一个强化学习框架，通过基于价值的优化和自我博弈
增强 LLM 推理能力。它使用策略网络、价值网络和奖励模型来迭代
改进性能。实现了最先进的结果：MATH 提升 15%，HumanEval 
提升 23%。
```

✅ 完美：关键信息 + 流畅翻译

## 配置要求

### 必须配置

```bash
# .env
ENABLE_AI_TRANSLATION=true
OPENAI_API_KEY=your_api_key_here
```

### 可选配置

```bash
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
TRANSLATION_TARGET_LANG=Chinese
```

## 性能考虑

### API 调用次数

每篇论文（启用 AI）：
- **带图片**: 2次调用（总结 + 翻译）
- **纯文本**: 2次调用（总结 + 翻译）

### 成本估算

使用 `gpt-4o-mini`：
- 输入: $0.15 / 1M tokens
- 输出: $0.60 / 1M tokens

每篇论文约：
- 输入: ~500 tokens × 2 = 1000 tokens ≈ $0.00015
- 输出: ~200 tokens × 2 = 400 tokens ≈ $0.00024
- **总计**: ~$0.0004 per paper

每天25篇论文：~$0.01/天，~$3.65/年

### 速度优化

```python
# 并行处理（未来可实现）
async def send_paper(self, paper: Paper):
    summarized, translated = await asyncio.gather(
        self.summarize_abstract(paper.abstract, 300),
        self.translate_text(paper.abstract[:500])
    )
```

## 降级策略

如果 AI 调用失败，自动降级到简单截取：

```python
try:
    summary = await self.summarize_abstract(text, max_length)
    return summary
except Exception as e:
    print(f"⚠️  摘要总结失败: {e}")
    # 降级：简单截取
    return text[:max_length] + "..." if len(text) > max_length else text
```

## 优势总结

| 特性 | 简单截取 | AI 智能总结 |
|------|---------|------------|
| 语义完整性 | ❌ | ✅ |
| 关键信息保留 | ❌ | ✅ |
| 可读性 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 技术术语保留 | ❌ | ✅ |
| 自然流畅 | ❌ | ✅ |
| 成本 | 免费 | ~$0.0004/篇 |
| 速度 | 即时 | ~1-2秒 |

## 禁用 AI 总结

如果不想使用 AI 总结，设置：

```bash
ENABLE_AI_TRANSLATION=false
```

系统会自动降级到简单截取策略。

## 调试

查看 AI 总结效果：

```python
# 在控制台会看到：
🤖 使用 AI 总结摘要...
🌐 翻译摘要...
✅ 已推送: DeepSearch: Improving LLM Reasoning
```

## 未来改进

- [ ] 缓存总结结果，避免重复调用
- [ ] 支持自定义总结风格
- [ ] 支持更多 AI 提供商（Claude, Gemini等）
- [ ] 批量总结以提高效率
- [ ] 根据论文类型调整总结策略
