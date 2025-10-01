# 测试脚本

本目录包含项目的测试脚本。

## 测试脚本列表

### test.fish
完整的端到端测试脚本，测试：
- 爬取今天的论文
- 保存到 Parquet 格式
- 显示存储统计

运行：
```bash
./tests/test.fish
```

### test_arxiv.py
测试 arXiv URL 提取功能，快速测试前5篇论文的：
- 作者提取
- ArXiv URL 提取

运行：
```bash
python tests/test_arxiv.py
```

### verify_data.py
验证保存的 Parquet 数据，显示：
- 论文数量
- 前3篇论文的详细信息
- 作者、摘要、URL 等字段

运行：
```bash
python tests/verify_data.py
```

### debug_html.py
调试 HTML 结构的工具，用于：
- 分析 HuggingFace 页面结构
- 查找作者、摘要等元素
- 保存完整 HTML 用于检查

运行：
```bash
python tests/debug_html.py
```

会生成 `tests/debug_page.html` 文件。

## 使用示例

### 完整测试流程
```bash
# 1. 运行完整测试
./tests/test.fish

# 2. 验证保存的数据
python tests/verify_data.py
```

### 调试爬虫问题
```bash
# 1. 生成调试HTML
python tests/debug_html.py

# 2. 检查 HTML 文件
cat tests/debug_page.html | grep -i "author"
```

### 快速测试特定功能
```bash
# 测试 arXiv URL 提取
python tests/test_arxiv.py
```
