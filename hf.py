import requests
from pydantic import BaseModel, AnyHttpUrl
from datetime import date
from bs4 import BeautifulSoup
import time

class Paper(BaseModel):
    title: str
    authors: list[str]
    abstract: str
    url: AnyHttpUrl
    hero_image: AnyHttpUrl | None = None
    arxiv_url: AnyHttpUrl | None = None
    
    def get_paper_id(self) -> str:
        """从URL中提取论文ID作为唯一标识"""
        return str(self.url).split('/')[-1]

def fetch_paper_details(paper_url: str) -> dict:
    """获取单篇论文的详细信息（完整摘要和作者列表）"""
    response = requests.get(paper_url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 提取完整摘要
    abstract = ""
    abstract_section = soup.find('div', class_='pb-8 pr-4 md:pr-16')
    if abstract_section:
        # 查找 Abstract 标题后的内容
        abstract_heading = abstract_section.find('h2', string=lambda x: x and 'Abstract' in x)
        if abstract_heading:
            # 获取紧随其后的段落
            next_elem = abstract_heading.find_next_sibling()
            if next_elem:
                abstract = next_elem.get_text(strip=True)
    
    # 如果上面的方法没找到，尝试另一种方式
    if not abstract:
        abstract_div = soup.find('div', {'class': lambda x: x and 'prose' in x})
        if abstract_div:
            paragraphs = abstract_div.find_all('p')
            if paragraphs:
                abstract = paragraphs[0].get_text(strip=True)
    
    # 提取完整作者列表
    authors = []
    # 方法1: 查找 class="author" 的元素
    author_elements = soup.find_all('span', class_='author')
    for author_elem in author_elements:
        # 提取作者名字（可能在 button 或 a 标签中）
        name_elem = author_elem.find('button') or author_elem.find('a')
        if name_elem:
            author_name = name_elem.get_text(strip=True)
        else:
            # 直接从 span 中提取
            author_name = author_elem.get_text(strip=True).replace(',', '').strip()
        
        if author_name and author_name not in authors and author_name != ',':
            authors.append(author_name)
    
    # 方法2: 如果上面没找到，尝试从 data-props 的 JSON 中提取
    if not authors:
        import json
        # 查找包含作者信息的 script 或 div
        for elem in soup.find_all(['div', 'script']):
            if 'data-props' in elem.attrs:
                try:
                    props_str = elem['data-props']
                    props_data = json.loads(props_str)
                    if 'paper' in props_data and 'authors' in props_data['paper']:
                        for author in props_data['paper']['authors']:
                            if 'name' in author:
                                authors.append(author['name'])
                except Exception:
                    pass
    
    # 提取 arXiv URL
    arxiv_url = None
    arxiv_link = soup.find('a', href=lambda x: x and 'arxiv.org/abs/' in x)
    if arxiv_link:
        arxiv_url = arxiv_link.get('href')
    
    return {
        'abstract': abstract,
        'authors': authors,
        'arxiv_url': arxiv_url
    }

def fetch_huggingface_papers(target_date: date):
    url = f"https://huggingface.co/papers/date/{target_date.strftime('%Y-%m-%d')}"
    response = requests.get(url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    papers = []
    
    # 查找所有论文卡片
    paper_cards = soup.find_all('article', class_='relative flex flex-col overflow-hidden rounded-xl border')
    
    for card in paper_cards:
        # 提取标题和URL
        title_link = card.find('h3').find('a') if card.find('h3') else None
        if not title_link:
            continue
            
        title = title_link.get_text(strip=True)
        paper_url = "https://huggingface.co" + title_link.get('href', '')
        
        # 提取缩略图
        hero_image = None
        img_elem = card.find('img')
        if img_elem and img_elem.get('src'):
            hero_image = img_elem.get('src')
            if hero_image.startswith('/'):
                hero_image = "https://huggingface.co" + hero_image
        
        # 获取论文详细信息（完整摘要和作者）
        print(f"正在获取论文详情: {title[:50]}...")
        try:
            details = fetch_paper_details(paper_url)
            time.sleep(0.5)  # 避免请求过快
        except Exception as e:
            print(f"获取论文详情失败: {e}")
            details = {'authors': [], 'abstract': '', 'arxiv_url': None}
        
        papers.append(Paper(
            title=title,
            authors=details.get('authors', []),
            abstract=details.get('abstract', ''),
            url=paper_url,
            hero_image=hero_image,
            arxiv_url=details.get('arxiv_url')
        ))
    
    return papers


if __name__ == "__main__":
    print(fetch_huggingface_papers(date(2025, 10, 1)))
