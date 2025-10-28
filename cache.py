"""Cache management module - Records sent papers to avoid duplicates"""
import json
from pathlib import Path
from typing import Set


class PaperCache:
    """Paper cache manager"""

    def __init__(self, cache_file: str = "papers_cache.json", initial_ids: Set[str] = None):
        self.cache_file = Path(cache_file)
        self.cached_ids: Set[str] = self._load_cache()

        # If initial IDs are provided (e.g., loaded from storage), merge them
        if initial_ids:
            self.cached_ids.update(initial_ids)
            self._save_cache()
            print(f"✅ Cache initialized with {len(self.cached_ids)} paper IDs")
    
    def _load_cache(self) -> Set[str]:
        """Load cached paper IDs from file"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(data.get('paper_ids', []))
            except Exception as e:
                print(f"⚠️  Failed to load cache: {e}")
                return set()
        return set()

    def _save_cache(self) -> None:
        """Save cache to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump({'paper_ids': list(self.cached_ids)}, f, indent=2)
        except Exception as e:
            print(f"Failed to save cache: {e}")
    
    def is_cached(self, paper_id: str) -> bool:
        """Check if paper is cached"""
        return paper_id in self.cached_ids

    def add(self, paper_id: str) -> None:
        """Add paper to cache"""
        self.cached_ids.add(paper_id)
        self._save_cache()

    def add_batch(self, paper_ids: list[str]) -> None:
        """Batch add papers to cache"""
        self.cached_ids.update(paper_ids)
        self._save_cache()

    def clear(self) -> None:
        """Clear cache"""
        self.cached_ids.clear()
        self._save_cache()

    def size(self) -> int:
        """Return cache size"""
        return len(self.cached_ids)
