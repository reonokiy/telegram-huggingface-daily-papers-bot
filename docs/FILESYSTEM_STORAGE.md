# 文件系统存储说明

## 概述

本项目使用 **OpenDAL 文件系统存储** 来管理论文数据，这为后续扩展到云存储提供了灵活的架构，同时保持当前的简单性。

## 设计理念

### 为什么使用 OpenDAL 文件系统？

1. **统一接口**: OpenDAL 提供统一的存储抽象层，无论是本地文件系统还是云存储，都使用相同的 API
2. **便于升级**: 当需要迁移到云存储时，只需修改配置，无需改动代码逻辑
3. **零学习成本**: 对用户来说，默认配置下就像使用普通文件系统一样简单
4. **性能优化**: OpenDAL 针对各种存储后端进行了优化

### 当前实现

- 默认使用本地文件系统（`fs` scheme）
- 数据存储在 `data/` 目录
- 可选配置归档目录用于月度合并文件

## 配置方式

### 基本配置（无归档）

```python
from storage import PaperStorage

# 最简单的方式，所有数据都在 data/ 目录
storage = PaperStorage(local_data_dir="data")
```

### 配置归档目录

```python
# 分离每日数据和归档数据
storage = PaperStorage(
    local_data_dir="data",      # 每日数据
    archive_dir="/backup/papers"  # 月度归档
)
```

### 从环境变量加载

```bash
# .env 文件
ARCHIVE_DIR=/backup/papers
```

```python
# Python 代码
storage = PaperStorage.from_env(local_data_dir="data")
```

## 目录结构

### 每日数据

```
data/
├── 2025/
│   ├── 10/
│   │   ├── papers_2025-10-01.parquet
│   │   ├── papers_2025-10-02.parquet
│   │   └── papers_2025-10-03.parquet
│   └── 11/
│       └── papers_2025-11-01.parquet
```

### 月度归档

如果配置了 `ARCHIVE_DIR`：

```
/backup/papers/
├── 2025/
│   ├── papers_2025-10_merged.parquet
│   └── papers_2025-11_merged.parquet
```

## OpenDAL 使用示例

```python
# 写入文件
storage.operator.write("test.txt", b"Hello World")

# 读取文件
content = storage.operator.read("test.txt")

# 删除文件
storage.operator.delete("test.txt")

# 列出目录
entries = storage.operator.list("2025/")
```

## 后续扩展

如果将来需要支持云存储（S3、Azure、GCS 等），只需：

1. 更新 `__init__` 方法接受存储配置
2. 修改 OpenDAL 初始化参数
3. 用户端只需改配置，代码无需变动

### 扩展示例（未来）

```python
# S3 存储（未来可能的实现）
storage = PaperStorage(
    local_data_dir="data",
    storage_scheme="s3",
    storage_config={
        "bucket": "my-papers",
        "region": "us-east-1",
        "access_key_id": "xxx",
        "secret_access_key": "xxx"
    }
)
```

## 特点

### ✅ 当前优势

- **简单**: 默认配置无需任何云服务
- **灵活**: 支持自定义归档目录
- **可靠**: 使用成熟的 Parquet 格式
- **高效**: Snappy 压缩，节省空间

### 🚀 未来扩展性

- 无缝切换到云存储
- 支持多种云服务商
- 统一的存储接口
- 便于迁移和备份

## 测试

运行存储测试：

```bash
uv run python tests/test_fs_storage.py
```

测试内容：
- ✅ 本地存储初始化
- ✅ 归档目录配置
- ✅ 环境变量加载
- ✅ OpenDAL 读写操作
- ✅ 存储统计信息

## 相关文档

- [缓存和存储集成](CACHE_STORAGE.md)
- [存储实现总结](IMPLEMENTATION_SUMMARY.md)
- [OpenDAL 官方文档](https://opendal.apache.org/)
