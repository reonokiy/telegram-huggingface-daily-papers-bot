#!/usr/bin/env python3
"""验证脚本 - 检查保存的 Parquet 数据"""

import pandas as pd
import json

df = pd.read_parquet('data/2025/10/papers_2025-10-02.parquet')
print(f'论文数量: {len(df)}')
print('\n前3篇论文:')

for i in range(min(3, len(df))):
    row = df.iloc[i]
    authors = json.loads(row['authors'])
    print(f'\n{i+1}. {row["title"][:50]}...')
    print(f'   作者数: {len(authors)}')
    print(f'   作者: {", ".join(authors[:3])}{"..." if len(authors) > 3 else ""}')
    print(f'   摘要长度: {len(row["abstract"])} 字符')
    print(f'   HF URL: {row["url"]}')
    if 'arxiv_url' in row and row['arxiv_url']:
        print(f'   ArXiv: {row["arxiv_url"]}')
