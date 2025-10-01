"""Telegram Bot - 定时推送 HuggingFace 每日论文"""
import os
import asyncio
from datetime import date, datetime
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError
from hf import fetch_huggingface_papers, Paper
from cache import PaperCache
from storage import PaperStorage


# 配置参数
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "@your_channel")  # 频道ID或@频道名
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "3600"))  # 检查间隔（秒），默认1小时


class HuggingFacePaperBot:
    """HuggingFace论文推送Bot"""
    
    def __init__(self, token: str, channel_id: str):
        self.bot = Bot(token=token)
        self.channel_id = channel_id
        self.cache = PaperCache()
        self.storage = PaperStorage(
            local_data_dir="data",
            s3_bucket=os.getenv("S3_BUCKET"),
            s3_endpoint=os.getenv("S3_ENDPOINT"),
            s3_access_key=os.getenv("S3_ACCESS_KEY"),
            s3_secret_key=os.getenv("S3_SECRET_KEY"),
        )
        
    def format_paper_message(self, paper: Paper) -> str:
        """格式化论文消息"""
        # 转义Markdown特殊字符
        def escape_markdown(text: str) -> str:
            special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
            for char in special_chars:
                text = text.replace(char, f'\\{char}')
            return text
        
        title = escape_markdown(paper.title.strip())
        authors = ", ".join(paper.authors[:5])  # 只显示前5位作者
        if len(paper.authors) > 5:
            authors += f" et al. ({len(paper.authors)} authors)"
        authors = escape_markdown(authors) if authors else "Unknown"
        
        # 摘要截取前300字符
        abstract = paper.abstract[:300] + "..." if len(paper.abstract) > 300 else paper.abstract
        abstract = escape_markdown(abstract) if abstract else "No abstract available"
        
        message = f"*{title}*\n\n"
        message += f"👥 *Authors:* {authors}\n\n"
        message += f"📄 *Abstract:* {abstract}\n\n"
        message += f"🔗 *Read More：* [HuggingFace]({paper.url})"
        message += f" | [ArXiv]({paper.arxiv_url})" if paper.arxiv_url else ""
        
        return message
    
    async def send_paper(self, paper: Paper):
        """发送单篇论文到频道"""
        try:
            message = self.format_paper_message(paper)
            
            # 如果有缩略图，发送带图片的消息
            if paper.hero_image:
                await self.bot.send_photo(
                    chat_id=self.channel_id,
                    photo=str(paper.hero_image),
                    caption=message,
                    parse_mode=ParseMode.MARKDOWN_V2
                )
            else:
                await self.bot.send_message(
                    chat_id=self.channel_id,
                    text=message,
                    parse_mode=ParseMode.MARKDOWN_V2,
                    disable_web_page_preview=False
                )
            
            print(f"✅ 已推送: {paper.title[:50]}")
            return True
            
        except TelegramError as e:
            print(f"❌ 推送失败: {e}")
            return False
    
    async def check_and_send_new_papers(self):
        """检查并发送新论文"""
        print(f"\n🔍 开始检查新论文... {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # 获取今日论文
            today = date.today()
            papers = fetch_huggingface_papers(today)
            print(f"📚 找到 {len(papers)} 篇论文")
            
            # 过滤出新论文
            new_papers = [
                paper for paper in papers 
                if not self.cache.is_cached(paper.get_paper_id())
            ]
            
            print(f"🆕 发现 {len(new_papers)} 篇新论文")
            
            # 发送新论文
            for paper in new_papers:
                success = await self.send_paper(paper)
                if success:
                    # 添加到缓存
                    self.cache.add(paper.get_paper_id())
                    # 避免发送过快
                    await asyncio.sleep(2)
            
            if new_papers:
                print(f"✨ 成功推送 {len(new_papers)} 篇新论文")
            else:
                print("💤 没有新论文")
            
            # 保存论文数据到本地 Parquet 文件
            if papers:
                self.storage.save_daily_papers(papers, today)
            
            # 检查是否需要月度归档（每月1号执行上个月的归档）
            if today.day == 1:
                last_month = today.month - 1 if today.month > 1 else 12
                last_year = today.year if today.month > 1 else today.year - 1
                print(f"📦 开始归档 {last_year}-{last_month:02d} 的数据...")
                self.storage.archive_month(last_year, last_month, delete_daily_files=False)
                
        except Exception as e:
            print(f"❌ 检查论文时出错: {e}")
    
    async def run(self):
        """运行Bot（定时检查）"""
        print("🤖 HuggingFace Daily Papers Bot 已启动")
        print(f"📢 推送频道: {self.channel_id}")
        print(f"⏱️  检查间隔: {CHECK_INTERVAL} 秒")
        print(f"💾 已缓存论文数: {self.cache.size()}\n")
        
        # 首次立即检查
        await self.check_and_send_new_papers()
        
        # 定时检查
        while True:
            await asyncio.sleep(CHECK_INTERVAL)
            await self.check_and_send_new_papers()


async def main():
    """主函数"""
    # 检查配置
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ 错误: 请设置环境变量 TELEGRAM_BOT_TOKEN")
        print("   export TELEGRAM_BOT_TOKEN='your_bot_token'")
        return
    
    if TELEGRAM_CHANNEL_ID == "@your_channel":
        print("❌ 错误: 请设置环境变量 TELEGRAM_CHANNEL_ID")
        print("   export TELEGRAM_CHANNEL_ID='@your_channel'")
        return
    
    # 启动Bot
    bot = HuggingFacePaperBot(TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID)
    await bot.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Bot 已停止")

