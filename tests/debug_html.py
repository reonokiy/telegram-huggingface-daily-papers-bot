#!/usr/bin/env python3
"""调试脚本 - 检查 HuggingFace 页面的实际 HTML 结构"""

import requests
from bs4 import BeautifulSoup
from datetime import date

# 测试一个具体的论文页面
test_url = "https://huggingface.co/papers/2509.25541"

print(f"正在访问: {test_url}\n")

response = requests.get(test_url)
soup = BeautifulSoup(response.content, 'html.parser')

# 保存完整HTML用于调试
with open('debug_page.html', 'w', encoding='utf-8') as f:
    f.write(soup.prettify())
print("✅ 完整HTML已保存到 debug_page.html\n")

# 1. 查找所有可能包含作者的链接
print("=" * 60)
print("1. 查找包含 'author' 的所有链接:")
print("=" * 60)
author_links = soup.find_all('a', href=lambda x: x and 'author' in x.lower())
for i, link in enumerate(author_links[:10], 1):
    print(f"{i}. href: {link.get('href')}")
    print(f"   text: {link.get_text(strip=True)}")
    print(f"   class: {link.get('class')}")
    print()

# 2. 查找所有可能的作者区域
print("=" * 60)
print("2. 查找可能的作者区域:")
print("=" * 60)

# 尝试不同的选择器
selectors = [
    ('a[href*="/papers/authors/"]', '包含 /papers/authors/ 的链接'),
    ('a[href*="author"]', '包含 author 的链接'),
    ('.author', 'class 包含 author'),
    ('[data-author]', 'data-author 属性'),
]

for selector, desc in selectors:
    elements = soup.select(selector)
    print(f"{desc}: 找到 {len(elements)} 个")
    for elem in elements[:3]:
        print(f"  - {elem.get_text(strip=True)[:50]}")
    print()

# 3. 查找摘要
print("=" * 60)
print("3. 查找摘要:")
print("=" * 60)

# 尝试找 Abstract
abstract_heading = soup.find('h2', string=lambda x: x and 'Abstract' in str(x))
if abstract_heading:
    print("✅ 找到 Abstract 标题")
    next_elem = abstract_heading.find_next_sibling()
    if next_elem:
        print(f"摘要内容: {next_elem.get_text(strip=True)[:200]}...")
else:
    print("❌ 未找到 Abstract 标题")

# 4. 打印页面主要结构
print("\n" + "=" * 60)
print("4. 页面主要结构:")
print("=" * 60)

# 查找主要的 div 结构
main_divs = soup.find_all('div', class_=lambda x: x and ('container' in ' '.join(x) or 'main' in ' '.join(x)))
print(f"找到 {len(main_divs)} 个主要容器")

# 打印前几个 h1, h2, h3
print("\n标题结构:")
for tag in ['h1', 'h2', 'h3']:
    headers = soup.find_all(tag)
    print(f"  {tag}: {len(headers)} 个")
    for h in headers[:3]:
        print(f"    - {h.get_text(strip=True)[:50]}")

print("\n✅ 调试完成！请检查 debug_page.html 文件")
