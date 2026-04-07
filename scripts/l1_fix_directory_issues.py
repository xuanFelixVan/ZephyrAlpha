"""
L1问题修复脚本 - 删除空目录和重构过深目录
用途：修复L1文件系统层问题
创建时间：2026-04-07
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"

class L1IssueFixer:
    def __init__(self):
        self.deleted_dirs = []
        self.moved_files = []
        self.failed_operations = []
        
    def find_empty_dirs(self):
        print("扫描空目录...")
        empty_dirs = []
        
        for root, dirs, files in os.walk(DOCS_DIR, topdown=False):
            root_path = Path(root)
            
            all_files = list(root_path.glob("*"))
            all_subdirs = [f for f in all_files if f.is_dir()]
            all_files = [f for f in all_files if f.is_file()]
            
            if len(all_files) == 0 and len(all_subdirs) == 0:
                empty_dirs.append(root_path)
        
        print(f"发现 {len(empty_dirs)} 个空目录")
        return empty_dirs
    
    def delete_empty_dir(self, dir_path):
        try:
            relative_path = dir_path.relative_to(DOCS_DIR)
            
            shutil.rmtree(dir_path)
            
            self.deleted_dirs.append(str(relative_path))
            
            print(f"  ✅ 删除空目录: {relative_path}")
            
            return True
        
        except Exception as e:
            print(f"  ❌ 删除失败: {dir_path} - {e}")
            self.failed_operations.append({
                "path": str(dir_path.relative_to(DOCS_DIR)),
                "error": str(e)
            })
            return False
    
    def find_deep_dirs(self):
        print("\n扫描过深目录...")
        deep_dirs = []
        
        for root, dirs, files in os.walk(DOCS_DIR):
            root_path = Path(root)
            relative_path = root_path.relative_to(DOCS_DIR)
            depth = len(relative_path.parts)
            
            if depth > 4:
                deep_dirs.append({
                    "path": root_path,
                    "relative_path": str(relative_path),
                    "depth": depth
                })
        
        print(f"发现 {len(deep_dirs)} 个过深目录")
        return deep_dirs
    
    def fix_deep_dir(self, dir_info):
        try:
            dir_path = dir_info["path"]
            relative_path = dir_info["relative_path"]
            depth = dir_info["depth"]
            
            print(f"\n处理过深目录: {relative_path} (深度{depth})")
            
            md_files = list(dir_path.glob("*.md"))
            
            if len(md_files) == 0:
                print(f"  ⚠️ 目录无文件，跳过")
                return False
            
            parent_path = dir_path.parent.parent
            
            for md_file in md_files:
                new_path = parent_path / md_file.name
                
                if new_path.exists():
                    print(f"  ⚠️ 目标文件已存在: {new_path.name}")
                    continue
                
                shutil.move(str(md_file), str(new_path))
                
                self.moved_files.append({
                    "old_path": str(md_file.relative_to(DOCS_DIR)),
                    "new_path": str(new_path.relative_to(DOCS_DIR))
                })
                
                print(f"  ✅ 移动文件: {md_file.name} -> {new_path.relative_to(DOCS_DIR)}")
            
            if len(list(dir_path.glob("*"))) == 0:
                shutil.rmtree(dir_path)
                print(f"  ✅ 删除空目录: {relative_path}")
            
            return True
        
        except Exception as e:
            print(f"  ❌ 修复失败: {dir_info['relative_path']} - {e}")
            self.failed_operations.append({
                "path": dir_info["relative_path"],
                "error": str(e)
            })
            return False
    
    def run(self):
        print("=" * 80)
        print("L1问题修复 - 删除空目录和重构过深目录")
        print("=" * 80)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        empty_dirs = self.find_empty_dirs()
        
        print(f"\n开始删除空目录...")
        for i, dir_path in enumerate(empty_dirs, 1):
            print(f"[{i}/{len(empty_dirs)}] 处理: {dir_path.relative_to(DOCS_DIR)}")
            self.delete_empty_dir(dir_path)
        
        deep_dirs = self.find_deep_dirs()
        
        print(f"\n开始重构过深目录...")
        for i, dir_info in enumerate(deep_dirs, 1):
            print(f"[{i}/{len(deep_dirs)}] 处理: {dir_info['relative_path']}")
            self.fix_deep_dir(dir_info)
        
        print("\n" + "=" * 80)
        print("修复统计")
        print("=" * 80)
        print(f"删除空目录: {len(self.deleted_dirs)}个")
        print(f"移动文件: {len(self.moved_files)}个")
        print(f"失败操作: {len(self.failed_operations)}个")
        
        if self.deleted_dirs:
            print("\n删除的空目录:")
            for path in self.deleted_dirs:
                print(f"  ✅ {path}")
        
        if self.moved_files:
            print("\n移动的文件:")
            for item in self.moved_files:
                print(f"  ✅ {item['old_path']} -> {item['new_path']}")
        
        if self.failed_operations:
            print("\n失败操作:")
            for item in self.failed_operations:
                print(f"  ❌ {item['path']}: {item['error']}")
        
        print("\n" + "=" * 80)
        print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        return {
            "deleted_dirs": len(self.deleted_dirs),
            "moved_files": len(self.moved_files),
            "failed_operations": len(self.failed_operations)
        }

if __name__ == "__main__":
    fixer = L1IssueFixer()
    fixer.run()
