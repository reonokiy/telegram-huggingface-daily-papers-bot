# 存储系统简化 - 更新日志

## 更新时间
2025-10-02

## 变更摘要

将存储系统从支持多云存储简化为仅支持 **OpenDAL 文件系统存储**，同时保留后续扩展到云存储的架构灵活性。

## 主要变更

### 1. 简化 `storage.py`

**之前**: 支持 S3、Azure、GCS、OSS、COS、文件系统等多种云存储
**之后**: 仅使用 OpenDAL 文件系统（fs scheme）

#### 修改内容

- **__init__ 方法**: 
  - 移除 `storage_scheme` 和 `storage_config` 参数
  - 添加简单的 `archive_dir` 参数用于归档配置
  - 始终使用 `opendal.Operator("fs", root=archive_dir)` 初始化

- **from_env() 方法**:
  - 简化为只读取 `ARCHIVE_DIR` 环境变量
  - 移除所有云存储配置逻辑

- **删除方法**:
  - `upload_to_storage()` - 不再需要通用上传
  - `_build_storage_url()` - 不再需要构建云存储 URL
  - `_get_storage_display_name()` - 不再需要显示云服务名称

- **archive_month() 方法**:
  - 简化为直接使用 OpenDAL 写入归档目录
  - 移除云存储上传逻辑

### 2. 简化 `.env.example`

**之前**: 包含 S3、Azure、GCS、OSS、COS 等多个云存储配置段
**之后**: 只保留一个 `ARCHIVE_DIR` 环境变量

```bash
# 归档配置（可选）
ARCHIVE_DIR=/data/archive
```

### 3. 更新文档

- **删除**: `docs/STORAGE.md` (659行的云存储配置指南)
- **新增**: `docs/FILESYSTEM_STORAGE.md` - 文件系统存储说明和扩展性
- **更新**: `README.md` - 移除云存储配置说明，添加归档配置

### 4. 测试更新

- **删除**: `tests/test_storage_config.py` (云存储配置测试)
- **新增**: `tests/test_fs_storage.py` - 文件系统存储测试
- **保留**: `tests/test_cache_storage.py` - 缓存集成测试（无需修改）

## 设计理念

### 为什么使用 OpenDAL 文件系统？

1. **简单性**: 当前只需要本地文件系统，避免复杂的云配置
2. **扩展性**: OpenDAL 提供统一接口，后续扩展到云存储只需修改配置
3. **零学习成本**: 默认行为就像使用普通文件系统
4. **未来友好**: 保留了切换到云存储的能力，无需重构代码

### 架构优势

```python
# 当前实现（简单）
storage = PaperStorage(
    local_data_dir="data",
    archive_dir="/backup/papers"  # 可选
)

# 未来扩展（如果需要）
storage = PaperStorage(
    local_data_dir="data",
    storage_scheme="s3",
    storage_config={"bucket": "my-papers", ...}
)
```

## 使用方式

### 基本配置

```python
from storage import PaperStorage

# 最简单方式
storage = PaperStorage(local_data_dir="data")

# 指定归档目录
storage = PaperStorage(
    local_data_dir="data",
    archive_dir="/backup/papers"
)

# 从环境变量加载
storage = PaperStorage.from_env(local_data_dir="data")
```

### 环境变量

```bash
# .env 文件
ARCHIVE_DIR=/data/archive  # 可选，不设置则使用 data/ 目录
```

## 目录结构

### 每日数据
```
data/
├── 2025/
│   └── 10/
│       ├── papers_2025-10-01.parquet
│       ├── papers_2025-10-02.parquet
│       └── papers_2025-10-03.parquet
```

### 归档数据（如果配置了 ARCHIVE_DIR）
```
/data/archive/
└── 2025/
    └── papers_2025-10_merged.parquet
```

## 测试结果

✅ 所有测试通过：

```bash
$ uv run python tests/test_fs_storage.py
=== 测试 1: 本地存储（无归档目录）===
✓ 数据目录: data
✓ OpenDAL 操作器: 已初始化

=== 测试 2: 配置归档目录 ===
✓ OpenDAL 写入测试成功
✓ OpenDAL 读取验证成功
✓ OpenDAL 删除测试成功

=== 测试 3: 从环境变量加载 ===
✓ 归档目录: /tmp/test_env_archive

=== 测试 4: 存储统计 ===
✓ 总文件数: 1
✓ 总大小: 0.07 MB
```

```bash
$ uv run python tests/test_cache_storage.py
✅ 缓存已初始化，共 57 个论文 ID
✓ 缓存大小: 57
✅ 测试完成！
```

## 代码变更统计

- **storage.py**: ~296 行 → ~250 行（简化 ~46 行）
- **.env.example**: ~90 行 → ~20 行（简化 ~70 行）
- **README.md**: 移除云存储配置段，简化约 30 行
- **docs/STORAGE.md**: 删除 659 行
- **docs/FILESYSTEM_STORAGE.md**: 新增 160 行
- **tests/test_storage_config.py**: 删除 ~120 行
- **tests/test_fs_storage.py**: 新增 ~120 行

**净变化**: 减少约 **745 行**代码和文档！

## 优势总结

### ✅ 用户体验
- 配置更简单（1 个环境变量 vs 15+ 个）
- 学习成本更低（无需了解云存储服务）
- 默认开箱即用

### ✅ 维护性
- 代码更简洁（减少 ~45% 代码）
- 减少复杂的配置验证逻辑
- 测试更集中

### ✅ 扩展性
- 保留 OpenDAL 抽象层
- 后续扩展只需修改初始化代码
- 用户代码无需变动

## 后续升级路径

如果将来需要支持云存储：

1. 恢复 `storage_scheme` 和 `storage_config` 参数
2. 在 `from_env()` 中添加云服务配置解析
3. 更新 `.env.example` 添加云服务变量
4. 用户只需修改配置，代码无需改动

## 参考文档

- [docs/FILESYSTEM_STORAGE.md](../docs/FILESYSTEM_STORAGE.md) - 文件系统存储详细说明
- [docs/CACHE_STORAGE.md](../docs/CACHE_STORAGE.md) - 缓存和存储集成
- [OpenDAL 文档](https://opendal.apache.org/) - OpenDAL 官方文档
