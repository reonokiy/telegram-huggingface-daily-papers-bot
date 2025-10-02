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
    github_url: AnyHttpUrl | None = None
    github_stars: int | None = None
    hf_upvotes: int | None = None
    
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
    
    # 提取 GitHub URL
    github_url = None
    github_stars = None
    github_link = soup.find('a', href=lambda x: x and 'github.com' in x)
    if github_link:
        github_url = github_link.get('href')
        # 如果链接不是完整的 URL，补全它
        if github_url and not github_url.startswith('http'):
            github_url = 'https://github.com' + github_url if github_url.startswith('/') else 'https://github.com/' + github_url
        
        # 尝试从链接旁边的文本或元素中提取 stars 数
        # 查找包含 stars 的元素（可能在按钮或 span 中）
        parent = github_link.find_parent()
        if parent:
            # 查找包含数字和 'star' 关键词的文本
            stars_text = parent.get_text()
            import re
            # 匹配数字（可能包含 k, K 等后缀）
            stars_match = re.search(r'(\d+\.?\d*)\s*[kK]?\s*(?:star|★)', stars_text, re.IGNORECASE)
            if stars_match:
                stars_str = stars_match.group(1)
                try:
                    stars_val = float(stars_str)
                    # 如果文本中有 'k' 或 'K'，乘以 1000
                    if 'k' in stars_text.lower():
                        stars_val *= 1000
                    github_stars = int(stars_val)
                except ValueError:
                    pass
        
        # 如果上面没找到，尝试通过 GitHub API 获取
        if github_stars is None and github_url:
            try:
                # 从 URL 提取 owner/repo
                url_parts = github_url.rstrip('/').split('github.com/')[-1].split('/')
                if len(url_parts) >= 2:
                    owner, repo = url_parts[0], url_parts[1]
                    api_url = f'https://api.github.com/repos/{owner}/{repo}'
                    gh_response = requests.get(api_url, timeout=5)
                    if gh_response.status_code == 200:
                        gh_data = gh_response.json()
                        github_stars = gh_data.get('stargazers_count')
            except Exception as e:
                print(f"  获取 GitHub stars 失败: {e}")
    
    # 提取 HuggingFace upvotes
    hf_upvotes = None
    import re
    
    # 查找包含 "Upvote" 文本的元素
    for elem in soup.find_all(['div', 'button', 'span']):
        text = elem.get_text(strip=True)
        # 匹配 "Upvote123" 或 "Upvote 123" 格式
        upvote_match = re.search(r'Upvote\s*(\d+)', text, re.IGNORECASE)
        if upvote_match:
            try:
                hf_upvotes = int(upvote_match.group(1))
                break
            except ValueError:
                pass
    
    return {
        'abstract': abstract,
        'authors': authors,
        'arxiv_url': arxiv_url,
        'github_url': github_url,
        'github_stars': github_stars,
        'hf_upvotes': hf_upvotes
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
            details = {
                'authors': [], 
                'abstract': '', 
                'arxiv_url': None,
                'github_url': None,
                'github_stars': None,
                'hf_upvotes': None
            }
        
        papers.append(Paper(
            title=title,
            authors=details.get('authors', []),
            abstract=details.get('abstract', ''),
            url=paper_url,
            hero_image=hero_image,
            arxiv_url=details.get('arxiv_url'),
            github_url=details.get('github_url'),
            github_stars=details.get('github_stars'),
            hf_upvotes=details.get('hf_upvotes')
        ))
    
    return papers


if __name__ == "__main__":
    print(fetch_huggingface_papers(date(2025, 10, 1)))
