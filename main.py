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

# AI 翻译配置
ENABLE_AI_TRANSLATION = os.getenv("ENABLE_AI_TRANSLATION", "false").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
TRANSLATION_TARGET_LANG = os.getenv("TRANSLATION_TARGET_LANG", "Chinese")  # 目标语言


class HuggingFacePaperBot:
    """HuggingFace论文推送Bot"""
    
    def __init__(self, token: str, channel_id: str, enable_translation: bool = False):
        self.bot = Bot(token=token)
        self.channel_id = channel_id
        
        # 初始化存储（自动从环境变量读取配置）
        self.storage = PaperStorage.from_env()
        
        # 从存储中加载所有已保存的论文 ID，并初始化缓存
        stored_paper_ids = self.storage.load_all_paper_ids()
        self.cache = PaperCache(initial_ids=stored_paper_ids)
        
        self.enable_translation = enable_translation
        
        # 初始化 OpenAI 客户端（如果启用翻译）
        if self.enable_translation:
            if not OPENAI_API_KEY:
                print("⚠️  警告: 启用了翻译但未配置 OPENAI_API_KEY，翻译功能将被禁用")
                self.enable_translation = False
            else:
                try:
                    from openai import OpenAI
                    self.openai_client = OpenAI(
                        api_key=OPENAI_API_KEY,
                        base_url=OPENAI_BASE_URL
                    )
                    print(f"✅ AI 翻译已启用 (模型: {OPENAI_MODEL}, 目标语言: {TRANSLATION_TARGET_LANG})")
                except ImportError:
                    print("⚠️  警告: 未安装 openai 库，翻译功能将被禁用")
                    print("    请运行: pip install openai")
                    self.enable_translation = False
    
    async def translate_text(self, text: str) -> str:
        """使用 AI 翻译文本"""
        if not self.enable_translation:
            return text
        
        try:
            response = self.openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional translator. Translate the following academic abstract to {TRANSLATION_TARGET_LANG}. Keep technical terms in English when appropriate. Provide only the translation without any explanations."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            translation = response.choices[0].message.content.strip()
            return translation
        
        except Exception as e:
            print(f"⚠️  翻译失败: {e}")
            return text  # 翻译失败时返回原文
    
    async def summarize_abstract(self, text: str, max_length: int = 300) -> str:
        """使用 AI 总结摘要到指定长度
        
        Args:
            text: 原始摘要文本
            max_length: 目标长度（字符数）
            
        Returns:
            总结后的摘要
        """
        # 如果没有启用 AI 或者文本已经够短，直接返回
        if not self.enable_translation or len(text) <= max_length:
            return text
        
        try:
            response = self.openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an expert at summarizing academic papers. Summarize the following abstract to approximately {max_length} characters while preserving the key points and technical terms. Be concise but informative."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                temperature=0.3,
                max_tokens=max_length
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
        
        except Exception as e:
            print(f"⚠️  摘要总结失败: {e}")
            # 失败时使用简单截取
            return text[:max_length] + "..." if len(text) > max_length else text
        
    def format_paper_message(self, paper: Paper, translated_abstract: str = None, max_length: int = None) -> str:
        """格式化论文消息
        
        Args:
            paper: 论文对象
            translated_abstract: 翻译后的摘要（可选）
            max_length: 最大消息长度（带图片时使用1024，纯文本时使用4096）
        """
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
        
        # 如果有翻译，使用翻译后的摘要，否则使用原始摘要
        if translated_abstract:
            abstract = translated_abstract
        else:
            abstract = paper.abstract
        
        # 注意：摘要长度控制在调用此函数前通过 AI 总结完成
        # 这里只做最后的安全截取（以防万一）
        if max_length:
            # 预估其他部分的长度（标题、作者、链接等）
            other_parts_length = len(title) + len(authors) + 200  # 200为其他固定文本的估算
            available_for_abstract = max_length - other_parts_length
            
            if available_for_abstract > 100:  # 至少保留100字符给摘要
                if len(abstract) > available_for_abstract:
                    # 安全截取（通常不应该到这一步，因为已经用 AI 总结过了）
                    abstract = abstract[:available_for_abstract - 3] + "..."

        abstract = escape_markdown(abstract) if abstract else "No abstract available"
        
        message = f"*{title}*\n\n"
        message += f"👥 *Authors:* {authors}\n\n"
        message += f"📄 *Abstract:* {abstract}\n\n"
        
        # 添加统计信息
        stats_parts = []
        if paper.hf_upvotes is not None:
            stats_parts.append(f"👍 {paper.hf_upvotes} upvotes")
        if paper.github_stars is not None:
            stats_parts.append(f"⭐ {paper.github_stars} stars")
        
        if stats_parts:
            message += f"📊 {' \\| '.join(stats_parts)}\n\n"
        
        # 添加链接
        links = [f"[HuggingFace]({paper.url})"]
        if paper.arxiv_url:
            links.append(f"[ArXiv]({paper.arxiv_url})")
        if paper.github_url:
            links.append(f"[GitHub]({paper.github_url})")
        
        message += f"🔗 *Read More：* {' \\| '.join(links)}"
        
        return message
    
    async def send_paper(self, paper: Paper):
        """发送单篇论文到频道"""
        try:
            # 准备摘要：翻译或总结
            processed_abstract = None
            
            if self.enable_translation and paper.abstract:
                # 如果启用了 AI，使用智能处理
                if paper.hero_image:
                    # 带图片：先总结到合适长度，再翻译
                    print("  🤖 使用 AI 总结摘要...")
                    summarized = await self.summarize_abstract(paper.abstract, max_length=500)
                    print("  🌐 翻译摘要...")
                    processed_abstract = await self.translate_text(summarized)
                else:
                    # 纯文本：直接翻译（可以更长）
                    print("  🌐 翻译摘要...")
                    summarized = await self.summarize_abstract(paper.abstract, max_length=1000)
                    processed_abstract = await self.translate_text(summarized)
            elif paper.abstract:
                # 没有启用 AI，只做长度控制
                if paper.hero_image:
                    processed_abstract = paper.abstract[:500] + "..." if len(paper.abstract) > 500 else paper.abstract
                else:
                    processed_abstract = paper.abstract[:1000] + "..." if len(paper.abstract) > 1000 else paper.abstract
            
            # 格式化并发送消息
            if paper.hero_image:
                # 带图片消息（caption 限制 1024 字符）
                message = self.format_paper_message(paper, processed_abstract, max_length=1000)
                await self.bot.send_photo(
                    chat_id=self.channel_id,
                    photo=str(paper.hero_image),
                    caption=message,
                    parse_mode=ParseMode.MARKDOWN_V2
                )
            else:
                # 纯文本消息（限制 4096 字符）
                message = self.format_paper_message(paper, processed_abstract, max_length=4000)
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
            
            # 保存所有论文数据到本地 Parquet 文件（包括新论文和已存在的论文）
            if papers:
                self.storage.save_daily_papers(papers, today)
            
            # 发送新论文
            sent_papers = []
            for paper in new_papers:
                success = await self.send_paper(paper)
                if success:
                    sent_papers.append(paper)
                    # 避免发送过快
                    await asyncio.sleep(2)
            
            # 批量添加到缓存
            if sent_papers:
                self.cache.add_batch([p.get_paper_id() for p in sent_papers])
                print(f"✨ 成功推送 {len(sent_papers)} 篇新论文")
            else:
                print("💤 没有新论文")
            
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
    bot = HuggingFacePaperBot(
        TELEGRAM_BOT_TOKEN, 
        TELEGRAM_CHANNEL_ID,
        enable_translation=ENABLE_AI_TRANSLATION
    )
    await bot.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Bot 已停止")

