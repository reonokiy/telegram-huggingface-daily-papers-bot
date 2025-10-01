#!/usr/bin/env fish

# 测试脚本 - 爬取今天的论文并保存到 Parquet

echo "🧪 测试 HuggingFace Papers Bot"
echo "================================"
echo ""

# 激活虚拟环境
source .venv/bin/activate.fish

echo "📅 测试日期: "(date +%Y-%m-%d)
echo ""

# 运行测试
python -c "
import asyncio
from datetime import date
from hf import fetch_huggingface_papers
from storage import PaperStorage

async def test():
    print('🔍 正在爬取今天的论文...')
    today = date.today()
    papers = fetch_huggingface_papers(today)
    print(f'✅ 成功爬取 {len(papers)} 篇论文')
    
    if papers:
        print(f'\\n📝 第一篇论文:')
        print(f'   标题: {papers[0].title}')
        print(f'   作者: {len(papers[0].authors)} 位')
        print(f'   摘要长度: {len(papers[0].abstract)} 字符')
        print(f'   URL: {papers[0].url}')
        
        print(f'\\n💾 正在保存到 Parquet...')
        storage = PaperStorage()
        filepath = storage.save_daily_papers(papers, today)
        
        print(f'\\n📊 存储统计:')
        stats = storage.get_statistics()
        print(f'   总文件数: {stats[\"total_files\"]}')
        print(f'   总大小: {stats[\"total_size_mb\"]} MB')

asyncio.run(test())
"

echo ""
echo "================================"
echo "✅ 测试完成"
