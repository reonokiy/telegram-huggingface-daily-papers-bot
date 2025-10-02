# 存储系统配置更新 - 2025-10-02

## 更新内容

### 1. 环境变量配置

**之前**: 只有 `ARCHIVE_DIR`（可选）
**之后**: 添加 `DATA_DIR` 和 `ARCHIVE_DIR`（都有默认值）

```bash
# .env
DATA_DIR=data              # 默认: data
ARCHIVE_DIR=data/archive   # 默认: data/archive
```

### 2. 文件命名简化

#### 每日文件

**之前**: `papers_2025-10-02.parquet`
**之后**: `20251002.parquet`

优势：
- 更简洁
- 易于排序
- 符合 ISO 8601 日期格式
- 文件名即日期，无需解析

#### 月度归档文件

**之前**: `papers_2025-10_merged.parquet`
**之后**: `202510.parquet`

优势：
- 更简洁
- 一致的命名风格
- 易于识别和查找

### 3. 目录结构独立

**重要变更**: 归档目录和数据目录完全独立

```
# 数据目录 (DATA_DIR)
data/
├── 2025/
│   └── 10/
│       ├── 20251001.parquet
│       ├── 20251002.parquet
│       └── 20251003.parquet

# 归档目录 (ARCHIVE_DIR)
data/archive/
└── 2025/
    └── 202510.parquet
```

**注意**: 归档目录不应设置为数据目录的子目录，避免混淆。

### 4. 代码更新

#### PaperStorage 类

```python
# 之前
storage = PaperStorage(
    local_data_dir="data",
    archive_dir="/path/to/archive"  # 可选
)

# 之后
storage = PaperStorage()  # 使用默认值

# 或自定义
storage = PaperStorage(
    local_data_dir="custom_data",
    archive_dir="custom_archive"
)

# 或从环境变量
storage = PaperStorage.from_env()
```

#### 主要变更点

1. **__init__ 方法**:
   - 参数都改为可选，从环境变量读取默认值
   - `DATA_DIR` 默认 `"data"`
   - `ARCHIVE_DIR` 默认 `"data/archive"`
   - 移除 `archive_enabled` 标志，归档始终启用

2. **from_env() 方法**:
   - 不再需要 `local_data_dir` 参数
   - 自动从环境变量读取所有配置

3. **save_daily_papers()**:
   - 文件名从 `papers_YYYY-MM-DD.parquet` 改为 `YYYYMMDD.parquet`

4. **merge_monthly_data()**:
   - 文件名从 `papers_YYYY-MM_merged.parquet` 改为 `YYYYMM.parquet`
   - 始终保存到归档目录

5. **load_all_paper_ids()**:
   - 更新文件匹配模式，只匹配8位数字的文件名（YYYYMMDD）

## 使用示例

### 基本使用

```python
from storage import PaperStorage
from datetime import date

# 使用默认配置
storage = PaperStorage()

# 保存论文
papers = fetch_huggingface_papers(date.today())
storage.save_daily_papers(papers, date.today())

# 月度归档
storage.archive_month(2025, 10)
```

### 自定义配置

```python
# 方式1: 直接指定
storage = PaperStorage(
    local_data_dir="/mnt/papers/data",
    archive_dir="/mnt/papers/archive"
)

# 方式2: 环境变量
import os
os.environ["DATA_DIR"] = "/mnt/papers/data"
os.environ["ARCHIVE_DIR"] = "/mnt/papers/archive"
storage = PaperStorage.from_env()
```

### 在 main.py 中

```python
class HuggingFacePaperBot:
    def __init__(self):
        # 简化初始化
        self.storage = PaperStorage.from_env()
```

## 文件访问示例

### 读取每日数据

```python
import pandas as pd

# 读取特定日期
df = pd.read_parquet('data/2025/10/20251002.parquet')

# 读取整月
import glob
files = glob.glob('data/2025/10/*.parquet')
dfs = [pd.read_parquet(f) for f in files]
merged = pd.concat(dfs, ignore_index=True)
```

### 读取归档数据

```python
# 读取月度归档
df = pd.read_parquet('data/archive/2025/202510.parquet')

# 读取整年
files = glob.glob('data/archive/2025/*.parquet')
yearly_data = pd.concat([pd.read_parquet(f) for f in files])
```

## 迁移指南

### 从旧格式迁移

如果有旧格式的文件（`papers_YYYY-MM-DD.parquet`），可以使用以下脚本重命名：

```python
from pathlib import Path
import re

def migrate_files(data_dir="data"):
    """将旧文件名格式迁移到新格式"""
    data_path = Path(data_dir)
    
    # 查找所有旧格式文件
    old_pattern = re.compile(r'papers_(\d{4})-(\d{2})-(\d{2})\.parquet')
    
    for file in data_path.rglob('papers_*.parquet'):
        match = old_pattern.match(file.name)
        if match:
            year, month, day = match.groups()
            new_name = f"{year}{month}{day}.parquet"
            new_path = file.parent / new_name
            
            print(f"重命名: {file.name} -> {new_name}")
            file.rename(new_path)
    
    # 处理月度归档文件
    merged_pattern = re.compile(r'papers_(\d{4})-(\d{2})_merged\.parquet')
    
    for file in data_path.rglob('papers_*_merged.parquet'):
        match = merged_pattern.match(file.name)
        if match:
            year, month = match.groups()
            new_name = f"{year}{month}.parquet"
            new_path = file.parent / new_name
            
            print(f"重命名: {file.name} -> {new_name}")
            file.rename(new_path)

# 执行迁移
migrate_files()
```

## 优势总结

### ✅ 简化

- 文件名更短更清晰
- 环境变量配置更直观
- 默认值合理，开箱即用

### ✅ 一致性

- 所有文件名都是纯数字日期
- 统一的命名风格
- 符合国际标准（ISO 8601）

### ✅ 灵活性

- 数据目录和归档目录完全独立
- 可通过环境变量或参数配置
- 便于不同环境部署

### ✅ 可维护性

- 文件名自解释，无需额外文档
- 易于脚本处理和自动化
- glob 模式匹配更简单

## 测试结果

```bash
$ uv run python tests/test_fs_storage.py

=== 测试 1: 本地存储（使用默认配置）===
✓ 数据目录: data
✓ 归档目录: data/archive
✓ OpenDAL 操作器: 已初始化

=== 测试 2: 自定义归档目录 ===
✓ OpenDAL 读写测试成功

=== 测试 3: 从环境变量加载 ===
✓ 环境变量配置正常

=== 测试 4: 存储统计 ===
✓ 文件统计正常

✅ 所有测试完成！
```

## 相关文档

- [FILESYSTEM_STORAGE.md](FILESYSTEM_STORAGE.md) - 文件系统存储详细说明
- [CACHE_STORAGE.md](CACHE_STORAGE.md) - 缓存和存储集成
- [README.md](../README.md) - 项目主文档
