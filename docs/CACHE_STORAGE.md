# 缓存和存储集成说明

## 概述

本项目将缓存系统与 Parquet 文件存储紧密集成，实现了高效的去重和数据管理。

## 工作原理

### 1. 初始化流程

```python
# 1. 首先初始化存储
storage = PaperStorage(local_data_dir="data")

# 2. 从所有 Parquet 文件中加载已存储的论文 ID
stored_paper_ids = storage.load_all_paper_ids()

# 3. 使用加载的 ID 初始化缓存
cache = PaperCache(initial_ids=stored_paper_ids)
```

这样做的好处：
- **自动恢复**：即使缓存文件（`papers_cache.json`）丢失，也能从 Parquet 文件恢复
- **统一来源**：Parquet 文件作为唯一的真实数据源
- **避免重复**：确保已保存的论文不会被重复推送

### 2. 数据流程

```
爬取论文 → 检查缓存 → 推送新论文 → 保存到 Parquet → 更新缓存
    ↑                                      ↓
    └──────────── 从 Parquet 初始化 ←──────┘
```

### 3. 增量保存

`storage.save_daily_papers()` 支持增量更新：

```python
# 如果当天的文件已存在
if filepath.exists():
    # 加载现有数据
    existing_df = pd.read_parquet(filepath)
    # 合并新旧数据
    combined_df = pd.concat([existing_df, new_df])
    # 去重（基于 paper_id）
    combined_df = combined_df.drop_duplicates(subset=['paper_id'], keep='first')
```

优势：
- **支持多次运行**：同一天可以多次检查并保存新论文
- **自动去重**：基于 `paper_id` 确保唯一性
- **数据完整性**：保留第一次出现的记录

### 4. 缓存更新策略

```python
# 批量添加到缓存（而不是每篇论文单独添加）
sent_papers = []
for paper in new_papers:
    if await send_paper(paper):
        sent_papers.append(paper)

# 所有论文推送完成后批量更新缓存
cache.add_batch([p.get_paper_id() for p in sent_papers])
```

优势：
- **减少 I/O**：批量写入而不是频繁保存
- **原子性**：要么全部更新，要么都不更新
- **性能优化**：减少文件操作次数

## 数据结构

### Parquet 文件格式

每个论文记录包含：

| 字段 | 类型 | 说明 |
|------|------|------|
| `paper_id` | string | 唯一标识符（从 URL 提取） |
| `title` | string | 论文标题 |
| `authors` | string | 作者列表（JSON 数组） |
| `abstract` | string | 论文摘要 |
| `url` | string | HuggingFace URL |
| `hero_image` | string | 缩略图 URL |
| `arxiv_url` | string | arXiv URL |
| `collected_at` | string | 收集时间（ISO 8601） |

### 缓存文件格式

`papers_cache.json`:

```json
{
  "paper_ids": [
    "2509.25541",
    "2509.25760",
    "..."
  ]
}
```

## 关键方法

### storage.load_all_paper_ids()

从所有 Parquet 文件中提取论文 ID：

```python
def load_all_paper_ids(self) -> set:
    """从所有 Parquet 文件中加载已存储的论文 ID"""
    paper_ids = set()
    
    # 遍历 data/YYYY/MM/*.parquet
    for year_dir in self.local_data_dir.iterdir():
        for month_dir in year_dir.iterdir():
            files = list(month_dir.glob("papers_*.parquet"))
            for file in files:
                df = pd.read_parquet(file, columns=['paper_id'])
                paper_ids.update(df['paper_id'].tolist())
    
    return paper_ids
```

特点：
- **只读取 paper_id 列**：优化性能，不加载完整数据
- **遍历所有文件**：确保不遗漏任何历史数据
- **返回集合**：自动去重

### cache.__init__(initial_ids)

支持从外部数据初始化：

```python
def __init__(self, cache_file: str = "papers_cache.json", initial_ids: Set[str] = None):
    # 先加载 JSON 缓存文件
    self.cached_ids = self._load_cache()
    
    # 合并从存储加载的 ID
    if initial_ids:
        self.cached_ids.update(initial_ids)
        self._save_cache()
```

## 使用示例

### 测试集成

```bash
python tests/test_cache_storage.py
```

输出：
```
🧪 测试缓存和存储集成

步骤 1: 从存储加载论文 ID
📚 从存储中加载了 57 个论文 ID
  ✓ 加载了 57 个论文 ID

步骤 2: 用存储数据初始化缓存
✅ 缓存已初始化，共 57 个论文 ID
  ✓ 缓存大小: 57

步骤 3: 测试缓存查询
  测试 ID: 2509.25541
  是否在缓存中: True
  测试假 ID: fake_paper_id_12345
  是否在缓存中: False

✅ 测试完成！
```

## 优势总结

1. **数据一致性**：Parquet 文件是唯一的数据源
2. **自动恢复**：缓存丢失时自动从存储重建
3. **增量更新**：支持多次运行，自动去重
4. **性能优化**：批量操作，减少 I/O
5. **长期存储**：Parquet 格式高效压缩（57 篇论文仅 0.07 MB）
6. **易于维护**：清晰的数据流程和职责分离

## 故障恢复

如果缓存文件损坏或丢失：

```bash
# 删除缓存文件
rm papers_cache.json

# 重新启动 Bot，自动从 Parquet 文件恢复
python main.py
```

输出：
```
📚 从存储中加载了 57 个论文 ID
✅ 缓存已初始化，共 57 个论文 ID
```

## 未来优化

- [ ] 添加定期清理旧缓存的机制
- [ ] 支持从 S3 远程加载论文 ID
- [ ] 实现分布式缓存（Redis）
- [ ] 添加缓存预热功能
