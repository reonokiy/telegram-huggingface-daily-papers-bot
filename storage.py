"""数据持久化模块 - 将论文数据存储为 Parquet 格式并上传到 S3"""
import os
import pandas as pd
from pathlib import Path
from datetime import datetime, date
from typing import List
import opendal
import json

from hf import Paper


class PaperStorage:
    """论文数据存储管理器"""
    
    def __init__(
        self,
        local_data_dir: str = "data",
        s3_bucket: str = None,
        s3_endpoint: str = None,
        s3_region: str = "us-east-1",
        s3_access_key: str = None,
        s3_secret_key: str = None,
    ):
        self.local_data_dir = Path(local_data_dir)
        self.local_data_dir.mkdir(parents=True, exist_ok=True)
        
        # S3 配置
        self.s3_bucket = s3_bucket
        self.s3_enabled = bool(s3_bucket and s3_access_key and s3_secret_key)
        
        # 初始化 OpenDAL
        self.operator = None
        if self.s3_enabled:
            try:
                self.operator = opendal.Operator(
                    "s3",
                    bucket=s3_bucket,
                    endpoint=s3_endpoint or "",
                    region=s3_region,
                    access_key_id=s3_access_key,
                    secret_access_key=s3_secret_key,
                )
                print(f"✓ S3 存储已配置: {s3_bucket}")
            except Exception as e:
                print(f"✗ S3 配置失败: {e}")
                self.s3_enabled = False
    
    def _paper_to_dict(self, paper: Paper) -> dict:
        """将 Paper 对象转换为字典"""
        return {
            'paper_id': paper.get_paper_id(),
            'title': paper.title,
            'authors': json.dumps(paper.authors, ensure_ascii=False),  # 转为 JSON 字符串
            'abstract': paper.abstract,
            'url': str(paper.url),
            'hero_image': str(paper.hero_image) if paper.hero_image else None,
            'arxiv_url': str(paper.arxiv_url) if paper.arxiv_url else None,
            'collected_at': datetime.now().isoformat(),
        }
    
    def save_daily_papers(self, papers: List[Paper], target_date: date):
        """保存每日论文数据到 Parquet 文件（增量更新）"""
        if not papers:
            print(f"没有论文数据需要保存 ({target_date})")
            return None
        
        # 生成文件路径：data/YYYY/MM/papers_YYYY-MM-DD.parquet
        year_dir = self.local_data_dir / str(target_date.year)
        month_dir = year_dir / f"{target_date.month:02d}"
        month_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"papers_{target_date.strftime('%Y-%m-%d')}.parquet"
        filepath = month_dir / filename
        
        # 转换新论文为 DataFrame
        new_data = [self._paper_to_dict(paper) for paper in papers]
        new_df = pd.DataFrame(new_data)
        
        # 如果文件已存在，加载并合并去重
        if filepath.exists():
            try:
                existing_df = pd.read_parquet(filepath)
                # 合并新旧数据
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                # 去重（基于 paper_id，保留第一次出现的）
                combined_df = combined_df.drop_duplicates(subset=['paper_id'], keep='first')
                df = combined_df
                print(f"✓ 合并数据: 原有 {len(existing_df)} 篇 + 新增 {len(new_df)} 篇 = 去重后 {len(df)} 篇")
            except Exception as e:
                print(f"⚠️  读取现有文件失败，将覆盖: {e}")
                df = new_df
        else:
            df = new_df
            print(f"✓ 创建新文件: {len(df)} 篇论文")
        
        # 保存为 Parquet 文件
        df.to_parquet(filepath, engine='pyarrow', compression='snappy', index=False)
        print(f"✓ 已保存到: {filepath}")
        
        return filepath
    
    def get_monthly_files(self, year: int, month: int) -> List[Path]:
        """获取指定月份的所有 Parquet 文件"""
        month_dir = self.local_data_dir / str(year) / f"{month:02d}"
        if not month_dir.exists():
            return []
        
        return sorted(month_dir.glob("papers_*.parquet"))
    
    def merge_monthly_data(self, year: int, month: int) -> Path:
        """合并指定月份的所有数据到一个 Parquet 文件"""
        files = self.get_monthly_files(year, month)
        if not files:
            print(f"没有找到 {year}-{month:02d} 的数据文件")
            return None
        
        # 读取所有文件并合并
        dfs = []
        for file in files:
            df = pd.read_parquet(file)
            dfs.append(df)
        
        merged_df = pd.concat(dfs, ignore_index=True)
        
        # 去重（基于 paper_id）
        merged_df = merged_df.drop_duplicates(subset=['paper_id'], keep='first')
        
        # 保存合并后的文件
        merged_filename = f"papers_{year}-{month:02d}_merged.parquet"
        merged_path = self.local_data_dir / str(year) / merged_filename
        merged_df.to_parquet(merged_path, engine='pyarrow', compression='snappy', index=False)
        
        print(f"✓ 已合并 {len(files)} 个文件，共 {len(merged_df)} 篇论文: {merged_path}")
        return merged_path
    
    def upload_to_s3(self, local_path: Path, s3_key: str = None) -> bool:
        """上传文件到 S3"""
        if not self.s3_enabled:
            print("S3 未配置，跳过上传")
            return False
        
        if not local_path.exists():
            print(f"文件不存在: {local_path}")
            return False
        
        # 生成 S3 key
        if s3_key is None:
            s3_key = str(local_path.relative_to(self.local_data_dir))
        
        try:
            # 读取文件内容
            with open(local_path, 'rb') as f:
                content = f.read()
            
            # 上传到 S3
            self.operator.write(s3_key, content)
            print(f"✓ 已上传到 S3: s3://{self.s3_bucket}/{s3_key}")
            return True
        
        except Exception as e:
            print(f"✗ 上传失败: {e}")
            return False
    
    def archive_month(self, year: int, month: int, delete_daily_files: bool = False) -> bool:
        """归档月度数据：合并并上传到 S3"""
        print(f"\n=== 开始归档 {year}-{month:02d} ===")
        
        # 1. 合并月度数据
        merged_path = self.merge_monthly_data(year, month)
        if not merged_path:
            return False
        
        # 2. 上传到 S3
        if self.s3_enabled:
            s3_key = f"papers/{year}/{month:02d}/papers_{year}-{month:02d}_merged.parquet"
            success = self.upload_to_s3(merged_path, s3_key)
            
            if success and delete_daily_files:
                # 3. 删除每日文件（可选）
                files = self.get_monthly_files(year, month)
                for file in files:
                    try:
                        file.unlink()
                        print(f"✓ 已删除: {file}")
                    except Exception as e:
                        print(f"✗ 删除失败 {file}: {e}")
        
        print(f"=== 归档完成 {year}-{month:02d} ===\n")
        return True
    
    def load_papers_by_date(self, target_date: date) -> List[dict]:
        """加载指定日期的论文数据"""
        year_dir = self.local_data_dir / str(target_date.year)
        month_dir = year_dir / f"{target_date.month:02d}"
        filename = f"papers_{target_date.strftime('%Y-%m-%d')}.parquet"
        filepath = month_dir / filename
        
        if not filepath.exists():
            return []
        
        df = pd.read_parquet(filepath)
        return df.to_dict('records')
    
    def load_all_paper_ids(self) -> set:
        """从所有 Parquet 文件中加载已存储的论文 ID"""
        paper_ids = set()
        
        if not self.local_data_dir.exists():
            return paper_ids
        
        # 遍历所有年份和月份目录
        for year_dir in self.local_data_dir.iterdir():
            if not year_dir.is_dir():
                continue
            
            for month_dir in year_dir.iterdir():
                if not month_dir.is_dir():
                    continue
                
                # 读取该月份的所有 parquet 文件
                files = list(month_dir.glob("papers_*.parquet"))
                for file in files:
                    try:
                        df = pd.read_parquet(file, columns=['paper_id'])
                        paper_ids.update(df['paper_id'].tolist())
                    except Exception as e:
                        print(f"⚠️  读取文件失败 {file}: {e}")
        
        print(f"📚 从存储中加载了 {len(paper_ids)} 个论文 ID")
        return paper_ids
    
    def get_statistics(self) -> dict:
        """获取存储统计信息"""
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


# 示例用法
if __name__ == "__main__":
    from datetime import date
    from hf import fetch_huggingface_papers
    
    # 初始化存储（不使用 S3）
    storage = PaperStorage(
        local_data_dir="data",
        s3_bucket=os.getenv("S3_BUCKET"),
        s3_endpoint=os.getenv("S3_ENDPOINT"),
        s3_access_key=os.getenv("S3_ACCESS_KEY"),
        s3_secret_key=os.getenv("S3_SECRET_KEY"),
    )
    
    # 获取今天的论文
    today = date.today()
    print(f"正在获取 {today} 的论文...")
    papers = fetch_huggingface_papers(today)
    
    # 保存到本地
    storage.save_daily_papers(papers, today)
    
    # 显示统计信息
    stats = storage.get_statistics()
    print("\n存储统计:")
    print(f"  总文件数: {stats['total_files']}")
    print(f"  总大小: {stats['total_size_mb']} MB")
    for month, info in stats['months'].items():
        print(f"  {month}: {info['files']} 文件, {info['size_mb']} MB")
