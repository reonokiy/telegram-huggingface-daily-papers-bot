"""调试 HuggingFace upvotes 的 HTML 结构"""
import requests
from bs4 import BeautifulSoup


def debug_upvotes():
    """查看论文页面的 upvote 元素"""
    # 使用一个测试 URL
    test_url = "https://huggingface.co/papers/2509.24002"
    
    print(f"🔍 调试 URL: {test_url}\n")
    
    response = requests.get(test_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 保存 HTML 用于分析
    with open('debug_upvote.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print("✅ HTML 已保存到 debug_upvote.html\n")
    
    # 查找所有可能包含 upvote 的元素
    print("=" * 80)
    print("查找包含数字的按钮:")
    print("=" * 80)
    
    for button in soup.find_all('button'):
        text = button.get_text(strip=True)
        classes = button.get('class', [])
        if any(char.isdigit() for char in text):
            print(f"\n按钮文本: '{text}'")
            print(f"  类名: {classes}")
            print(f"  父元素: {button.parent.name if button.parent else 'None'}")
    
    print("\n" + "=" * 80)
    print("查找包含 'like' 或 'vote' 的元素:")
    print("=" * 80)
    
    for elem in soup.find_all(['button', 'div', 'span']):
        classes = ' '.join(elem.get('class', []))
        text = elem.get_text(strip=True)
        
        if 'like' in classes.lower() or 'vote' in classes.lower():
            print(f"\n元素: {elem.name}")
            print(f"  文本: '{text[:50]}'")
            print(f"  类名: {classes}")
    
    print("\n" + "=" * 80)
    print("查找所有包含向上箭头图标的元素:")
    print("=" * 80)
    
    # 查找 SVG 或图标
    for svg in soup.find_all('svg'):
        parent = svg.parent
        if parent:
            text = parent.get_text(strip=True)
            classes = parent.get('class', [])
            if any(char.isdigit() for char in text):
                print(f"\nSVG 父元素: {parent.name}")
                print(f"  文本: '{text}'")
                print(f"  类名: {classes}")
    
    print("\n✅ 调试完成！")


if __name__ == "__main__":
    debug_upvotes()
