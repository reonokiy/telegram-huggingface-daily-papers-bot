"""缓存管理模块 - 用于记录已推送的论文，避免重复推送"""
import json
from pathlib import Path
from typing import Set


class PaperCache:
    """论文缓存管理器"""
    
    def __init__(self, cache_file: str = "papers_cache.json"):
        self.cache_file = Path(cache_file)
        self.cached_ids: Set[str] = self._load_cache()
    
    def _load_cache(self) -> Set[str]:
        """从文件加载已缓存的论文ID"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(data.get('paper_ids', []))
            except Exception as e:
                print(f"加载缓存失败: {e}")
                return set()
        return set()
    
    def _save_cache(self):
        """保存缓存到文件"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump({'paper_ids': list(self.cached_ids)}, f, indent=2)
        except Exception as e:
            print(f"保存缓存失败: {e}")
    
    def is_cached(self, paper_id: str) -> bool:
        """检查论文是否已缓存"""
        return paper_id in self.cached_ids
    
    def add(self, paper_id: str):
        """添加论文到缓存"""
        self.cached_ids.add(paper_id)
        self._save_cache()
    
    def add_batch(self, paper_ids: list[str]):
        """批量添加论文到缓存"""
        self.cached_ids.update(paper_ids)
        self._save_cache()
    
    def clear(self):
        """清空缓存"""
        self.cached_ids.clear()
        self._save_cache()
    
    def size(self) -> int:
        """返回缓存大小"""
        return len(self.cached_ids)
