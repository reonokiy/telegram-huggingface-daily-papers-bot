"""Data persistence module - Store paper data in Parquet format"""
import os
import pandas as pd
from pathlib import Path
from datetime import datetime, date
from typing import List, Optional
import opendal
import json

from hf import Paper


class PaperStorage:
    """Paper data storage manager

    Uses OpenDAL filesystem for data storage, making it easy to extend to cloud storage later.
    Current version only supports local filesystem.
    """
    
    def __init__(
        self,
        local_data_dir: Optional[str] = None,
        archive_dir: Optional[str] = None,
    ):
        """Initialize storage manager

        Args:
        local_data_dir: Local data directory (default read from DATA_DIR env var, otherwise "data")
        archive_dir: Archive directory (default read from ARCHIVE_DIR env var, otherwise "data/archive")
        """
        # Get directories from environment variables or parameters
        if local_data_dir is None:
            local_data_dir = os.getenv("DATA_DIR", "data")
        if archive_dir is None:
            archive_dir = os.getenv("ARCHIVE_DIR", "data/archive")

        self.local_data_dir = Path(local_data_dir)
        self.local_data_dir.mkdir(parents=True, exist_ok=True)

        # Archive directory configuration (always independent of data directory)
        self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        # Initialize OpenDAL filesystem Operator
        try:
            self.operator = opendal.Operator("fs", root=str(self.archive_dir))
            print(f"Data directory: {self.local_data_dir}")
            print(f"Archive directory: {self.archive_dir}")
        except Exception as e:
            print(f"Warning: OpenDAL initialization failed: {e}")
            print("   Will use standard file operations")
            self.operator = None
    
    @classmethod
    def from_env(cls) -> "PaperStorage":
        """Create storage manager from environment variables

        Environment variables:
        DATA_DIR: Data directory path (default: data)
        ARCHIVE_DIR: Archive directory path (optional)
        """
        return cls(
            local_data_dir=os.getenv("DATA_DIR"),
            archive_dir=os.getenv("ARCHIVE_DIR")
        )
    
    def _paper_to_dict(self, paper: Paper) -> dict:
        """Convert Paper object to dictionary"""
        return {
            'paper_id': paper.get_paper_id(),
            'title': paper.title,
            'authors': json.dumps(paper.authors, ensure_ascii=False),  # Convert to JSON string
            'abstract': paper.abstract,
            'url': str(paper.url),
            'hero_image': str(paper.hero_image) if paper.hero_image else None,
            'arxiv_url': str(paper.arxiv_url) if paper.arxiv_url else None,
            'github_url': str(paper.github_url) if paper.github_url else None,
            'github_stars': paper.github_stars,
            'hf_upvotes': paper.hf_upvotes,
            'collected_at': datetime.now().isoformat(),
        }

    def save_daily_papers(self, papers: List[Paper], target_date: date) -> Optional[Path]:
        """Save daily paper data to Parquet file (incremental update)"""
        if not papers:
            print(f"No paper data to save ({target_date})")
            return None

        # Generate file path: data/YYYY/MM/YYYYMMDD.parquet
        year_dir = self.local_data_dir / str(target_date.year)
        month_dir = year_dir / f"{target_date.month:02d}"
        month_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{target_date.strftime('%Y%m%d')}.parquet"
        filepath = month_dir / filename
        
        # Convert new papers to DataFrame
        new_data = [self._paper_to_dict(paper) for paper in papers]
        new_df = pd.DataFrame(new_data)

        # If file exists, load and merge with deduplication
        if filepath.exists():
            try:
                existing_df = pd.read_parquet(filepath)
                # Merge old and new data
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                # Deduplicate (based on paper_id, keep first occurrence)
                combined_df = combined_df.drop_duplicates(subset=['paper_id'], keep='first')
                df = combined_df
                print(f"Merged data: {len(existing_df)} existing + {len(new_df)} new = {len(df)} after deduplication")
            except Exception as e:
                print(f"Warning: Failed to read existing file, will overwrite: {e}")
                df = new_df
        else:
            df = new_df
            print(f"Created new file: {len(df)} papers")

        # Save as Parquet file
        df.to_parquet(filepath, engine='pyarrow', compression='snappy', index=False)
        print(f"Saved to: {filepath}")

        return filepath
    
    def get_monthly_files(self, year: int, month: int) -> List[Path]:
        """Get all Parquet files for the specified month"""
        month_dir = self.local_data_dir / str(year) / f"{month:02d}"
        if not month_dir.exists():
            return []

        return sorted(month_dir.glob("*.parquet"))

    def merge_monthly_data(self, year: int, month: int) -> Optional[Path]:
        """Merge all data for the specified month into one Parquet file"""
        files = self.get_monthly_files(year, month)
        if not files:
            print(f"No data files found for {year}-{month:02d}")
            return None

        # Read all files and merge
        dfs = []
        for file in files:
            df = pd.read_parquet(file)
            dfs.append(df)

        merged_df = pd.concat(dfs, ignore_index=True)

        # Deduplicate (based on paper_id)
        merged_df = merged_df.drop_duplicates(subset=['paper_id'], keep='first')

        # Save merged file to archive directory: YYYYMM.parquet
        merged_filename = f"{year}{month:02d}.parquet"

        # Save to archive directory
        archive_year_dir = self.archive_dir / str(year)
        archive_year_dir.mkdir(parents=True, exist_ok=True)
        merged_path = archive_year_dir / merged_filename

        merged_df.to_parquet(merged_path, engine='pyarrow', compression='snappy', index=False)

        print(f"Merged {len(files)} files, total {len(merged_df)} papers: {merged_path}")
        return merged_path
    
    def archive_month(self, year: int, month: int, delete_daily_files: bool = False) -> bool:
        """Archive monthly data: merge to archive directory

        Args:
        year: Year
        month: Month
        delete_daily_files: Whether to delete daily files

        Returns:
        bool: Whether archiving was successful
        """
        print(f"\n=== Starting archive {year}-{month:02d} ===")

        # 1. Merge monthly data
        merged_path = self.merge_monthly_data(year, month)
        if not merged_path:
            return False

        # 2. Write using OpenDAL (if available)
        if self.operator:
            try:
                # Read merged file
                with open(merged_path, 'rb') as f:
                    content = f.read()

                # Write using OpenDAL
                archive_key = f"{year}/{year}{month:02d}.parquet"
                self.operator.write(archive_key, content)
                print(f"Written to archive via OpenDAL: {archive_key}")
            except Exception as e:
                print(f"Warning: OpenDAL write failed: {e}")
                print("   File saved to local archive directory")

        # 3. Delete daily files (optional)
        if delete_daily_files:
            files = self.get_monthly_files(year, month)
            for file in files:
                try:
                    file.unlink()
                    print(f"Deleted daily file: {file.name}")
                except Exception as e:
                    print(f"Error: Delete failed {file}: {e}")

        print(f"=== Archive completed {year}-{month:02d} ===\n")
        return True
    
    def load_papers_by_date(self, target_date: date) -> List[dict]:
        """Load paper data for the specified date"""
        year_dir = self.local_data_dir / str(target_date.year)
        month_dir = year_dir / f"{target_date.month:02d}"
        filename = f"{target_date.strftime('%Y%m%d')}.parquet"
        filepath = month_dir / filename

        if not filepath.exists():
            return []

        df = pd.read_parquet(filepath)
        return df.to_dict('records')

    def load_all_paper_ids(self) -> set[str]:
        """Load stored paper IDs from all Parquet files"""
        paper_ids = set()
        
        if not self.local_data_dir.exists():
            return paper_ids
        
        # Iterate through all year and month directories
        for year_dir in self.local_data_dir.iterdir():
            if not year_dir.is_dir():
                continue

            for month_dir in year_dir.iterdir():
                if not month_dir.is_dir():
                    continue

                # Read all parquet files for this month (exclude monthly archive files)
                files = [f for f in month_dir.glob("*.parquet") if len(f.stem) == 8]  # YYYYMMDD format
                for file in files:
                    try:
                        df = pd.read_parquet(file, columns=['paper_id'])
                        paper_ids.update(df['paper_id'].tolist())
                    except Exception as e:
                        print(f"Warning: Failed to read file {file}: {e}")

        print(f"Loaded {len(paper_ids)} paper IDs from storage")
        return paper_ids
    
    def get_statistics(self) -> dict:
        """Get storage statistics"""
        stats = {
            'total_files': 0,
            'total_size_mb': 0,
            'months': {}
        }

        for year_dir in self.local_data_dir.iterdir():
            if not year_dir.is_dir():
                continue

            for month_dir in year_dir.iterdir():
                if not month_dir.is_dir():
                    continue

                files = list(month_dir.glob("papers_*.parquet"))
                total_size = sum(f.stat().st_size for f in files)

                month_key = f"{year_dir.name}-{month_dir.name}"
                stats['months'][month_key] = {
                    'files': len(files),
                    'size_mb': round(total_size / 1024 / 1024, 2)
                }
                stats['total_files'] += len(files)
                stats['total_size_mb'] += total_size / 1024 / 1024

        stats['total_size_mb'] = round(stats['total_size_mb'], 2)
        return stats


# Example usage
if __name__ == "__main__":
    from datetime import date
    from hf import fetch_huggingface_papers

    # Initialize storage (load configuration from environment variables)
    storage = PaperStorage.from_env()

    # Get today's papers
    today = date.today()
    print(f"Fetching papers for {today}...")
    papers = fetch_huggingface_papers(today)

    # Save to local storage
    storage.save_daily_papers(papers, today)

    # Display statistics
    stats = storage.get_statistics()
    print("\nStorage statistics:")
    print(f"  Total files: {stats['total_files']}")
    print(f"  Total size: {stats['total_size_mb']} MB")
    for month, info in stats['months'].items():
        print(f"  {month}: {info['files']} files, {info['size_mb']} MB")
