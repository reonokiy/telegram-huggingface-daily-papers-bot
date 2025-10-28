import json
import re
import time
from typing import Dict, List, Optional, Any

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, AnyHttpUrl
from datetime import date

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
        """Extract paper ID from URL as unique identifier"""
        return str(self.url).split('/')[-1]


PaperDetails = Dict[str, Any]

def fetch_paper_details(paper_url: str) -> PaperDetails:
    """Fetch detailed information for a single paper (full abstract and author list)"""
    response = requests.get(paper_url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract full abstract
    abstract = ""
    abstract_section = soup.find('div', class_='pb-8 pr-4 md:pr-16')
    if abstract_section:
        # Find content after Abstract heading
        abstract_heading = abstract_section.find('h2', string=lambda x: x and 'Abstract' in x)
        if abstract_heading:
            # Get the paragraph immediately following
            next_elem = abstract_heading.find_next_sibling()
            if next_elem:
                abstract = next_elem.get_text(strip=True)

    # If the above method didn't find it, try another approach
    if not abstract:
        abstract_div = soup.find('div', {'class': lambda x: x and 'prose' in x})
        if abstract_div:
            paragraphs = abstract_div.find_all('p')
            if paragraphs:
                abstract = paragraphs[0].get_text(strip=True)
    
    # Extract full author list
    authors = []
    # Method 1: Find elements with class="author"
    author_elements = soup.find_all('span', class_='author')
    for author_elem in author_elements:
        # Extract author name (may be in button or a tag)
        name_elem = author_elem.find('button') or author_elem.find('a')
        if name_elem:
            author_name = name_elem.get_text(strip=True)
        else:
            # Extract directly from span
            author_name = author_elem.get_text(strip=True).replace(',', '').strip()

        if author_name and author_name not in authors and author_name != ',':
            authors.append(author_name)

    # Method 2: If not found above, try extracting from data-props JSON
    if not authors:
        # Find script or div containing author information
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
    
    # Extract arXiv URL
    arxiv_url = None
    arxiv_link = soup.find('a', href=lambda x: x and 'arxiv.org/abs/' in x)
    if arxiv_link:
        arxiv_url = arxiv_link.get('href')
    
    # Extract GitHub URL
    github_url = None
    github_stars = None
    github_link = soup.find('a', href=lambda x: x and 'github.com' in x)
    if github_link:
        github_url = github_link.get('href')
        # Complete the URL if it's not a full URL
        if github_url and not github_url.startswith('http'):
            github_url = 'https://github.com' + github_url if github_url.startswith('/') else 'https://github.com/' + github_url

        # Try to extract star count from text or elements near the link
        # Find elements containing stars (may be in button or span)
        parent = github_link.find_parent()
        if parent:
            # Find text containing numbers and 'star' keyword
            stars_text = parent.get_text()
            # Match numbers (may include k, K suffix)
            stars_match = re.search(r'(\d+\.?\d*)\s*[kK]?\s*(?:star|★)', stars_text, re.IGNORECASE)
            if stars_match:
                stars_str = stars_match.group(1)
                try:
                    stars_val = float(stars_str)
                    # If text contains 'k' or 'K', multiply by 1000
                    if 'k' in stars_text.lower():
                        stars_val *= 1000
                    github_stars = int(stars_val)
                except ValueError:
                    pass

        # If not found above, try fetching via GitHub API
        if github_stars is None and github_url:
            try:
                # Extract owner/repo from URL
                url_parts = github_url.rstrip('/').split('github.com/')[-1].split('/')
                if len(url_parts) >= 2:
                    owner, repo = url_parts[0], url_parts[1]
                    api_url = f'https://api.github.com/repos/{owner}/{repo}'
                    gh_response = requests.get(api_url, timeout=5)
                    if gh_response.status_code == 200:
                        gh_data = gh_response.json()
                        github_stars = gh_data.get('stargazers_count')
            except Exception as e:
                print(f"  Failed to fetch GitHub stars: {e}")
    
    # Extract HuggingFace upvotes
    hf_upvotes = None

    # Find elements containing "Upvote" text
    for elem in soup.find_all(['div', 'button', 'span']):
        text = elem.get_text(strip=True)
        # Match "Upvote123" or "Upvote 123" format
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

def fetch_huggingface_papers(target_date: date) -> List[Paper]:
    url = f"https://huggingface.co/papers/date/{target_date.strftime('%Y-%m-%d')}"
    response = requests.get(url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    papers = []
    
    # Find all paper cards
    paper_cards = soup.find_all('article', class_='relative flex flex-col overflow-hidden rounded-xl border')

    for card in paper_cards:
        # Extract title and URL
        title_link = card.find('h3').find('a') if card.find('h3') else None
        if not title_link:
            continue
            
        title = title_link.get_text(strip=True)
        paper_url = "https://huggingface.co" + title_link.get('href', '')
        
        # Extract thumbnail
        hero_image = None
        img_elem = card.find('img')
        if img_elem and img_elem.get('src'):
            hero_image = img_elem.get('src')
            if hero_image.startswith('/'):
                hero_image = "https://huggingface.co" + hero_image

        # Fetch paper details (full abstract and authors)
        print(f"Fetching paper details: {title[:50]}...")
        try:
            details = fetch_paper_details(paper_url)
            time.sleep(0.5)  # Avoid making requests too quickly
        except Exception as e:
            print(f"Failed to fetch paper details: {e}")
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
