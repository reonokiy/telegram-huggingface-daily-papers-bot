"""测试缓存和存储的集成"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from storage import PaperStorage
from cache import PaperCache


def test_cache_storage_integration():
    """测试缓存从存储中初始化"""
    print("🧪 测试缓存和存储集成\n")
    
    # 1. 初始化存储
    storage = PaperStorage(local_data_dir="data")
    
    # 2. 从存储加载所有论文 ID
    print("步骤 1: 从存储加载论文 ID")
    stored_ids = storage.load_all_paper_ids()
    print(f"  ✓ 加载了 {len(stored_ids)} 个论文 ID\n")
    
    # 3. 使用加载的 ID 初始化缓存
    print("步骤 2: 用存储数据初始化缓存")
    cache = PaperCache(cache_file="test_cache.json", initial_ids=stored_ids)
    print(f"  ✓ 缓存大小: {cache.size()}\n")
    
    # 4. 测试缓存查询
    print("步骤 3: 测试缓存查询")
    if stored_ids:
        test_id = next(iter(stored_ids))
        print(f"  测试 ID: {test_id}")
        print(f"  是否在缓存中: {cache.is_cached(test_id)}")
        
        fake_id = "fake_paper_id_12345"
        print(f"  测试假 ID: {fake_id}")
        print(f"  是否在缓存中: {cache.is_cached(fake_id)}\n")
    
    # 5. 显示存储统计
    print("步骤 4: 存储统计信息")
    stats = storage.get_statistics()
    print(f"  总文件数: {stats['total_files']}")
    print(f"  总大小: {stats['total_size_mb']} MB")
    for month, info in sorted(stats['months'].items()):
        print(f"  {month}: {info['files']} 文件, {info['size_mb']} MB")
    
    print("\n✅ 测试完成！")


if __name__ == "__main__":
    test_cache_storage_integration()
