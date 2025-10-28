"""Telegram Bot - Automated daily paper posting from HuggingFace"""
import asyncio
from datetime import date, datetime
from typing import List, Optional

from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError

from config import Config
from hf import fetch_huggingface_papers, Paper
from cache import PaperCache
from storage import PaperStorage


# Configuration is now handled by the Config class


class HuggingFacePaperBot:
    """HuggingFace daily papers bot"""

    def __init__(self, token: str, channel_id: str, enable_translation: Optional[bool] = None):
        self.bot = Bot(token=token)
        self.channel_id = channel_id

        # Initialize storage (automatically reads config from environment variables)
        self.storage = PaperStorage.from_env()

        # Load all saved paper IDs from storage and initialize cache
        stored_paper_ids = self.storage.load_all_paper_ids()
        self.cache = PaperCache(initial_ids=stored_paper_ids)

        # Use provided enable_translation or fall back to config
        self.enable_translation = enable_translation if enable_translation is not None else Config.ENABLE_AI_TRANSLATION

        # Initialize OpenAI client (if translation is enabled)
        if self.enable_translation:
            if not Config.OPENAI_API_KEY:
                print("Warning: Translation enabled but OPENAI_API_KEY not configured, translation will be disabled")
                self.enable_translation = False
            else:
                try:
                    from openai import OpenAI
                    self.openai_client = OpenAI(
                        api_key=Config.OPENAI_API_KEY,
                        base_url=Config.OPENAI_BASE_URL
                    )
                    print(f"AI translation enabled (model: {Config.OPENAI_MODEL}, target language: {Config.TRANSLATION_TARGET_LANG})")
                except ImportError:
                    print("Warning: openai library not installed, translation will be disabled")
                    print("    Please run: pip install openai")
                    self.enable_translation = False
    
    async def translate_text(self, text: str) -> str:
        """Use AI to translate text"""
        if not self.enable_translation:
            return text
        
        try:
            response = self.openai_client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional translator. Translate the following academic abstract to {Config.TRANSLATION_TARGET_LANG}. Keep technical terms in English when appropriate. Provide only the translation without any explanations."
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
            print(f"Warning: Translation failed: {e}")
            return text  # Return original text if translation fails

    async def summarize_abstract(self, text: str, max_length: int = 300) -> str:
        """Use AI to summarize abstract to specified length

        Args:
        text: Original abstract text
        max_length: Target length (character count)

        Returns:
        Summarized abstract
        """
        # If AI is not enabled or text is already short enough, return as is
        if not self.enable_translation or len(text) <= max_length:
            return text

        try:
            response = self.openai_client.chat.completions.create(
                model=Config.OPENAI_MODEL,
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
            print(f"Warning: Abstract summarization failed: {e}")
            # Fall back to simple truncation on failure
            return text[:max_length] + "..." if len(text) > max_length else text
        
    def format_paper_message(self, paper: Paper, translated_abstract: Optional[str] = None, max_length: Optional[int] = None) -> str:
        """Format paper message

        Args:
            paper: Paper object
            translated_abstract: Translated abstract (optional)
            max_length: Maximum message length (1024 for images, 4096 for text)
        """
        # Escape Markdown special characters
        def escape_markdown(text: str) -> str:
            special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
            for char in special_chars:
                text = text.replace(char, f'\\{char}')
            return text

        # Clean title: remove newlines and extra spaces
        title = paper.title.strip()
        title = ' '.join(title.split())  # Replace all whitespace (including newlines) with single spaces
        title = escape_markdown(title)

        authors = ", ".join(paper.authors[:Config.MAX_AUTHORS_DISPLAY])  # Show only first 5 authors
        if len(paper.authors) > Config.MAX_AUTHORS_DISPLAY:
            authors += f" et al. ({len(paper.authors)} authors)"
        authors = escape_markdown(authors) if authors else "Unknown"
        
        # Use translated abstract if available, otherwise use original
        if translated_abstract:
            abstract = translated_abstract
        else:
            abstract = paper.abstract

        # Note: Abstract length control is done before calling this function via AI summarization
        # This is just a final safety truncation (in case something goes wrong)
        if max_length:
            # Estimate length of other parts (title, authors, links, etc.)
            other_parts_length = len(title) + len(authors) + 200  # 200 is estimate for other fixed text
            available_for_abstract = max_length - other_parts_length

            if available_for_abstract > 100:  # Keep at least 100 characters for abstract
                if len(abstract) > available_for_abstract:
                    # Safe truncation (shouldn't usually get here since AI summarization was done)
                    abstract = abstract[:available_for_abstract - 3] + "..."

        abstract = escape_markdown(abstract) if abstract else "No abstract available"
        
        message = f"*{title}*\n\n"
        message += f"👥 *Authors:* {authors}\n\n"
        message += f"📄 *Abstract:* {abstract}\n\n"
        
        # Add statistics
        stats_parts = []
        if paper.hf_upvotes is not None:
            stats_parts.append(f"👍 {paper.hf_upvotes} upvotes")
        if paper.github_stars is not None:
            stats_parts.append(f"⭐ {paper.github_stars} stars")
        
        if stats_parts:
            message += f"📊 {' \\| '.join(stats_parts)}\n\n"
        
        # Add links
        links = [f"[HuggingFace]({paper.url})"]
        if paper.arxiv_url:
            links.append(f"[ArXiv]({paper.arxiv_url})")
        if paper.github_url:
            links.append(f"[GitHub]({paper.github_url})")
        
        message += f"🔗 *Read More：* {' \\| '.join(links)}"
        
        return message
    
    async def send_paper(self, paper: Paper) -> bool:
        """Send a single paper to the channel"""
        try:
            # Prepare abstract: translate or summarize
            processed_abstract = None

            if self.enable_translation and paper.abstract:
                # If AI is enabled, use intelligent processing
                if paper.hero_image:
                    # With image: summarize to appropriate length first, then translate
                    print("  Using AI to summarize abstract...")
                    summarized = await self.summarize_abstract(paper.abstract, max_length=Config.MAX_ABSTRACT_LENGTH_WITH_IMAGE)
                    print("  Translating abstract...")
                    processed_abstract = await self.translate_text(summarized)
                else:
                    # Text only: translate directly (can be longer)
                    print("  Translating abstract...")
                    summarized = await self.summarize_abstract(paper.abstract, max_length=Config.MAX_ABSTRACT_LENGTH_WITHOUT_IMAGE)
                    processed_abstract = await self.translate_text(summarized)
            elif paper.abstract:
                # No AI enabled, just control length
                if paper.hero_image:
                    processed_abstract = paper.abstract[:Config.MAX_ABSTRACT_LENGTH_WITH_IMAGE] + "..." if len(paper.abstract) > Config.MAX_ABSTRACT_LENGTH_WITH_IMAGE else paper.abstract
                else:
                    processed_abstract = paper.abstract[:Config.MAX_ABSTRACT_LENGTH_WITHOUT_IMAGE] + "..." if len(paper.abstract) > Config.MAX_ABSTRACT_LENGTH_WITHOUT_IMAGE else paper.abstract
            # Format and send message
            if paper.hero_image:
                # Message with image (caption limited to 1024 characters)
                message = self.format_paper_message(paper, processed_abstract, max_length=Config.MAX_MESSAGE_LENGTH_WITH_IMAGE)
                await self.bot.send_photo(
                    chat_id=self.channel_id,
                    photo=str(paper.hero_image),
                    caption=message,
                    parse_mode=ParseMode.MARKDOWN_V2
                )
            else:
                # Text-only message (limited to 4096 characters)
                message = self.format_paper_message(paper, processed_abstract, max_length=Config.MAX_MESSAGE_LENGTH_WITHOUT_IMAGE)
                await self.bot.send_message(
                    chat_id=self.channel_id,
                    text=message,
                    parse_mode=ParseMode.MARKDOWN_V2,
                    disable_web_page_preview=False
                )

            print(f"Posted: {paper.title[:50]}")
            return True

        except TelegramError as e:
            print(f"Error: Posting failed: {e}")
            return False
    
    async def check_and_send_new_papers(self) -> None:
        """Check and send new papers"""
        print(f"\nStarting to check for new papers... {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            # Get today's papers
            today = date.today()
            papers = fetch_huggingface_papers(today)
            print(f"Found {len(papers)} papers")

            # Filter out new papers
            new_papers = [
                paper for paper in papers
                if not self.cache.is_cached(paper.get_paper_id())
            ]

            print(f"Found {len(new_papers)} new papers")

            # Save all paper data to local Parquet files (including new and existing papers)
            if papers:
                self.storage.save_daily_papers(papers, today)
            
            # Send new papers
            sent_papers = []
            for paper in new_papers:
                success = await self.send_paper(paper)
                if success:
                    sent_papers.append(paper)
                    # Avoid sending too quickly
                    await asyncio.sleep(Config.SEND_DELAY)
            
            # Batch add to cache
            if sent_papers:
                self.cache.add_batch([p.get_paper_id() for p in sent_papers])
                print(f"Successfully posted {len(sent_papers)} new papers")
            else:
                print("No new papers")

            # Check if monthly archiving is needed (archive last month on the 1st of each month)
            if today.day == 1:
                last_month = today.month - 1 if today.month > 1 else 12
                last_year = today.year if today.month > 1 else today.year - 1
                print(f"Starting to archive data for {last_year}-{last_month:02d}...")
                self.storage.archive_month(last_year, last_month, delete_daily_files=False)

        except Exception as e:
            print(f"Error while checking papers: {e}")
    
    async def run(self) -> None:
        """Run the bot (scheduled checking)"""
        print("HuggingFace Daily Papers Bot started")
        print(f"Posting channel: {self.channel_id}")
        print(f"Check interval: {Config.CHECK_INTERVAL} seconds")
        print(f"Cached papers count: {self.cache.size()}\n")
        
        # Initial check immediately
        await self.check_and_send_new_papers()

        # Scheduled checks
        while True:
            await asyncio.sleep(Config.CHECK_INTERVAL)
            await self.check_and_send_new_papers()


async def main() -> None:
    """Main function"""
    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        print(f"Error: Configuration error: {e}")
        print("   Please set the required environment variables")
        return
    
    # Start the bot
    bot = HuggingFacePaperBot(
        Config.TELEGRAM_BOT_TOKEN,
        Config.TELEGRAM_CHANNEL_ID,
        enable_translation=Config.ENABLE_AI_TRANSLATION
    )
    await bot.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nBot stopped")

