"""测试 GitHub 链接和统计数据的获取"""
import sys
from pathlib import Path
from datetime import date

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from hf import fetch_huggingface_papers


def test_github_and_stats():
    """测试获取 GitHub 链接、stars 和 upvotes"""
    print("🧪 测试 GitHub 链接和统计数据获取\n")
    
    # 获取今天的论文（只获取前3篇作为测试）
    today = date.today()
    print(f"正在获取 {today} 的论文（前3篇）...\n")
    
    all_papers = fetch_huggingface_papers(today)
    papers = all_papers[:3]  # 只测试前3篇
    
    print(f"\n找到 {len(all_papers)} 篇论文，测试前 {len(papers)} 篇:\n")
    print("=" * 80)
    
    for i, paper in enumerate(papers, 1):
        print(f"\n📄 论文 {i}: {paper.title[:60]}")
        print(f"   URL: {paper.url}")
        print(f"   作者数: {len(paper.authors)}")
        print(f"   摘要长度: {len(paper.abstract)} 字符")
        
        # GitHub 信息
        if paper.github_url:
            print(f"   ✅ GitHub: {paper.github_url}")
            if paper.github_stars is not None:
                print(f"      ⭐ Stars: {paper.github_stars}")
            else:
                print(f"      ⚠️  未获取到 stars 数")
        else:
            print(f"   ❌ 未找到 GitHub 链接")
        
        # HuggingFace upvotes
        if paper.hf_upvotes is not None:
            print(f"   ✅ HF Upvotes: {paper.hf_upvotes}")
        else:
            print(f"   ⚠️  未获取到 upvotes")
        
        # ArXiv
        if paper.arxiv_url:
            print(f"   ✅ ArXiv: {paper.arxiv_url}")
        else:
            print(f"   ❌ 未找到 ArXiv 链接")
        
        print("-" * 80)
    
    # 统计信息
    print("\n📊 统计结果:")
    papers_with_github = sum(1 for p in papers if p.github_url)
    papers_with_stars = sum(1 for p in papers if p.github_stars is not None)
    papers_with_upvotes = sum(1 for p in papers if p.hf_upvotes is not None)
    papers_with_arxiv = sum(1 for p in papers if p.arxiv_url)
    
    print(f"   有 GitHub 链接: {papers_with_github}/{len(papers)}")
    print(f"   有 GitHub stars: {papers_with_stars}/{len(papers)}")
    print(f"   有 HF upvotes: {papers_with_upvotes}/{len(papers)}")
    print(f"   有 ArXiv 链接: {papers_with_arxiv}/{len(papers)}")
    
    print("\n✅ 测试完成！")
    
    return papers


if __name__ == "__main__":
    test_github_and_stats()
