#!/usr/bin/env python3
"""测试文件系统存储配置"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from storage import PaperStorage


def test_local_storage():
    """测试本地存储（使用默认配置）"""
    print("\n=== 测试 1: 本地存储（使用默认配置）===")
    storage = PaperStorage()
    
    print(f"✓ 数据目录: {storage.local_data_dir}")
    print(f"✓ 归档目录: {storage.archive_dir}")
    print(f"✓ OpenDAL 操作器: {'已初始化' if storage.operator else '未初始化'}")
    

def test_archive_storage():
    """测试自定义归档存储配置"""
    print("\n=== 测试 2: 自定义归档目录 ===")
    storage = PaperStorage(
        local_data_dir="data",
        archive_dir="/tmp/test_archive"
    )
    
    print(f"✓ 数据目录: {storage.local_data_dir}")
    print(f"✓ 归档目录: {storage.archive_dir}")
    print(f"✓ OpenDAL 操作器: {'已初始化' if storage.operator else '未初始化'}")
    
    # 测试 OpenDAL 写入
    if storage.operator:
        try:
            test_content = b"Hello OpenDAL FileSystem"
            storage.operator.write("test/hello.txt", test_content)
            print("✓ OpenDAL 写入测试成功")
            
            # 读取验证
            read_content = storage.operator.read("test/hello.txt")
            if read_content == test_content:
                print("✓ OpenDAL 读取验证成功")
            else:
                print("✗ OpenDAL 读取验证失败")
                
            # 清理
            storage.operator.delete("test/hello.txt")
            print("✓ OpenDAL 删除测试成功")
        except Exception as e:
            print(f"✗ OpenDAL 操作失败: {e}")


def test_from_env():
    """测试从环境变量加载"""
    print("\n=== 测试 3: 从环境变量加载 ===")
    import os
    
    # 临时设置环境变量
    os.environ["DATA_DIR"] = "test_data"
    os.environ["ARCHIVE_DIR"] = "/tmp/test_env_archive"
    
    storage = PaperStorage.from_env()
    
    print(f"✓ 数据目录: {storage.local_data_dir}")
    print(f"✓ 归档目录: {storage.archive_dir}")
    
    # 清理环境变量
    del os.environ["DATA_DIR"]
    del os.environ["ARCHIVE_DIR"]


def test_statistics():
    """测试统计功能"""
    print("\n=== 测试 4: 存储统计 ===")
    storage = PaperStorage()
    
    stats = storage.get_statistics()
    print(f"✓ 总文件数: {stats['total_files']}")
    print(f"✓ 总大小: {stats['total_size_mb']} MB")
    
    if stats['months']:
        print("✓ 月度统计:")
        for month, info in stats['months'].items():
            print(f"   - {month}: {info['files']} 文件, {info['size_mb']} MB")


if __name__ == "__main__":
    print("开始测试文件系统存储配置...")
    
    try:
        test_local_storage()
        test_archive_storage()
        test_from_env()
        test_statistics()
        
        print("\n" + "="*60)
        print("✓ 所有测试完成!")
        print("="*60)
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
