#!/usr/bin/env python3
"""测试 arXiv URL 功能"""

from datetime import date
from hf import fetch_huggingface_papers
from storage import PaperStorage

print("正在爬取论文（只取前5篇测试）...\n")

# 只爬取前5篇进行快速测试
import requests
from bs4 import BeautifulSoup
from hf import fetch_paper_details
import time

url = f"https://huggingface.co/papers/date/2025-10-02"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
paper_cards = soup.find_all('article', class_='relative flex flex-col overflow-hidden rounded-xl border')

print(f"找到 {len(paper_cards)} 篇论文，测试前5篇\n")

papers = []
for i, card in enumerate(paper_cards[:5], 1):
    title_link = card.find('h3').find('a') if card.find('h3') else None
    if not title_link:
        continue
    
    title = title_link.get_text(strip=True)
    paper_url = "https://huggingface.co" + title_link.get('href', '')
    
    print(f"{i}. {title[:50]}...")
    details = fetch_paper_details(paper_url)
    print(f"   作者数: {len(details['authors'])}")
    print(f"   ArXiv URL: {details.get('arxiv_url', 'N/A')}")
    print()
    
    time.sleep(0.5)

print("✅ 测试完成！")
