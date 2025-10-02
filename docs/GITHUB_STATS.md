# GitHub 和统计信息获取功能

## 功能说明

Bot 现在会自动获取每篇论文的以下统计信息：

1. **GitHub 链接** - 论文相关的代码仓库
2. **GitHub Stars** - 仓库的 star 数量
3. **HuggingFace Upvotes** - 论文在 HuggingFace 上的点赞数

## 数据模型

### Paper 模型新增字段

```python
class Paper(BaseModel):
    title: str
    authors: list[str]
    abstract: str
    url: AnyHttpUrl
    hero_image: AnyHttpUrl | None = None
    arxiv_url: AnyHttpUrl | None = None
    github_url: AnyHttpUrl | None = None      # 新增
    github_stars: int | None = None           # 新增
    hf_upvotes: int | None = None             # 新增
```

### 存储字段

在 Parquet 文件中新增三个字段：

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `github_url` | string | GitHub 仓库链接 | `https://github.com/eval-sys/mcpmark` |
| `github_stars` | int | GitHub stars 数量 | `184` |
| `hf_upvotes` | int | HuggingFace upvotes | `118` |

## 获取逻辑

### 1. GitHub 链接提取

```python
# 从论文页面的 HTML 中查找 GitHub 链接
github_link = soup.find('a', href=lambda x: x and 'github.com' in x)
if github_link:
    github_url = github_link.get('href')
```

### 2. GitHub Stars 获取

优先级策略：

1. **从页面提取** - 查找 GitHub 链接旁边的 stars 数字
2. **GitHub API** - 如果页面上没有，通过 GitHub API 获取：

```python
# 从 URL 提取 owner/repo
owner, repo = url_parts[0], url_parts[1]
api_url = f'https://api.github.com/repos/{owner}/{repo}'
response = requests.get(api_url, timeout=5)
github_stars = response.json().get('stargazers_count')
```

### 3. HuggingFace Upvotes 提取

从页面查找包含 "Upvote" 文本的元素：

```python
# 匹配 "Upvote123" 或 "Upvote 123" 格式
upvote_match = re.search(r'Upvote\s*(\d+)', text, re.IGNORECASE)
if upvote_match:
    hf_upvotes = int(upvote_match.group(1))
```

## 消息显示

在 Telegram 消息中显示统计信息：

```
*Paper Title*

👥 *Authors:* Author1, Author2, ...

📄 *Abstract:* ...

📊 👍 118 upvotes | ⭐ 184 stars

🔗 *Read More：* HuggingFace | ArXiv | GitHub
```

## 测试结果

运行测试脚本：

```bash
python tests/test_github_stats.py
```

测试结果（2025-10-02 前 3 篇论文）：

```
📄 论文 1: MCPMark: A Benchmark for Stress-Testing...
   ✅ GitHub: https://github.com/eval-sys/mcpmark
      ⭐ Stars: 184
   ✅ HF Upvotes: 118
   ✅ ArXiv: https://arxiv.org/abs/2509.24002

📄 论文 2: The Dragon Hatchling...
   ✅ GitHub: https://github.com/pathwaycom/bdh
      ⭐ Stars: 443
   ✅ HF Upvotes: 103
   ✅ ArXiv: https://arxiv.org/abs/2509.26507

📄 论文 3: Vision-Zero...
   ✅ GitHub: https://github.com/wangqinsi1/Vision-Zero
      ⭐ Stars: 22
   ✅ HF Upvotes: 95
   ✅ ArXiv: https://arxiv.org/abs/2509.25541

📊 统计结果:
   有 GitHub 链接: 3/3
   有 GitHub stars: 3/3
   有 HF upvotes: 3/3
   有 ArXiv 链接: 3/3
```

## 性能优化

### 限速处理

爬取时已经包含延迟：

```python
time.sleep(0.5)  # 每篇论文之间延迟 0.5 秒
```

如果遇到 429 错误（请求过多），Bot 会自动跳过该论文并继续。

### GitHub API 限制

- **未认证**: 60 次/小时
- **已认证**: 5000 次/小时

如果需要更高的速率，可以设置 GitHub Token：

```python
headers = {'Authorization': f'token {GITHUB_TOKEN}'}
response = requests.get(api_url, headers=headers, timeout=5)
```

## 数据示例

### Parquet 文件记录

```json
{
  "paper_id": "2509.24002",
  "title": "MCPMark: A Benchmark for Stress-Testing...",
  "authors": "[\"Author1\", \"Author2\", ...]",
  "abstract": "...",
  "url": "https://huggingface.co/papers/2509.24002",
  "hero_image": "https://cdn-thumbnails.huggingface.co/...",
  "arxiv_url": "https://arxiv.org/abs/2509.24002",
  "github_url": "https://github.com/eval-sys/mcpmark",
  "github_stars": 184,
  "hf_upvotes": 118,
  "collected_at": "2025-10-02T12:34:56.789012"
}
```

## 统计分析

基于这些数据，可以进行有趣的分析：

1. **热门度排序** - 按 upvotes 或 stars 排序
2. **趋势分析** - 跟踪 stars 增长趋势
3. **相关性分析** - HF upvotes 与 GitHub stars 的相关性
4. **代码可用性** - 有多少论文提供了代码

示例查询（使用 pandas）：

```python
import pandas as pd

# 读取数据
df = pd.read_parquet('data/2025/10/papers_2025-10-02.parquet')

# 按 upvotes 排序
top_upvoted = df.nlargest(10, 'hf_upvotes')[['title', 'hf_upvotes', 'github_stars']]

# 有 GitHub 代码的论文比例
has_github = (df['github_url'].notna()).sum() / len(df) * 100
print(f"有代码的论文: {has_github:.1f}%")

# upvotes 和 stars 的相关性
correlation = df[['hf_upvotes', 'github_stars']].corr()
print(correlation)
```

## 未来改进

- [ ] 定期更新 stars 数（后台任务）
- [ ] 添加 GitHub issues/PRs 数量
- [ ] 添加论文引用数（Google Scholar）
- [ ] 支持其他代码托管平台（GitLab, Bitbucket）
- [ ] 添加更多社交媒体指标（Twitter mentions, Reddit posts）
