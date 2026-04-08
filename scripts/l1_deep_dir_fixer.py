"""
L1目录层级过深修复脚本
用途：修复目录层级过深问题
创建时间：2026-04-07
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"

class L1DeepDirFixer:
    def __init__(self):
        self.moved_files = []
        self.deleted_dirs = []
        self.failed_operations = []
        
        self.deep_dir = DOCS_DIR / "05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/05_DESIGN_DOCS/ui_design/04_NOZYIO"
        self.target_dir = DOCS_DIR / "05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/05_DESIGN_DOCS/ui_design"
    
    def move_files(self):
        print("移动文件...")
        
        if not self.deep_dir.exists():
            print(f"  ⚠️ 目录不存在: {self.deep_dir}")
            return False
        
        files = list(self.deep_dir.glob("*.md"))
        
        for file_path in files:
            try:
                target_path = self.target_dir / file_path.name
                
                if target_path.exists():
                    print(f"  ⚠️ 目标文件已存在，跳过: {file_path.name}")
                    continue
                
                shutil.move(str(file_path), str(target_path))
                self.moved_files.append({
                    "from": str(file_path.relative_to(DOCS_DIR)),
                    "to": str(target_path.relative_to(DOCS_DIR))
                })
                print(f"  ✅ 移动: {file_path.name}")
            
            except Exception as e:
                print(f"  ❌ 移动失败: {file_path} - {e}")
                self.failed_operations.append({
                    "operation": "move",
                    "file": str(file_path.relative_to(DOCS_DIR)),
                    "error": str(e)
                })
        
        return True
    
    def delete_empty_dir(self):
        print("\n删除空目录...")
        
        try:
            remaining_files = list(self.deep_dir.glob("*"))
            
            if remaining_files:
                print(f"  ⚠️ 目录非空，跳过删除: {self.deep_dir}")
                return False
            
            shutil.rmtree(self.deep_dir)
            self.deleted_dirs.append(str(self.deep_dir.relative_to(DOCS_DIR)))
            print(f"  ✅ 删除目录: {self.deep_dir.name}")
            return True
        
        except Exception as e:
            print(f"  ❌ 删除失败: {self.deep_dir} - {e}")
            self.failed_operations.append({
                "operation": "delete",
                "dir": str(self.deep_dir.relative_to(DOCS_DIR)),
                "error": str(e)
            })
            return False
    
    def run(self):
        print("=" * 80)
        print("L1目录层级过深修复")
        print("=" * 80)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        print(f"\n处理目录: {self.deep_dir.relative_to(DOCS_DIR)}")
        print(f"目标目录: {self.target_dir.relative_to(DOCS_DIR)}")
        
        self.move_files()
        self.delete_empty_dir()
        
        print("\n" + "=" * 80)
        print("修复统计")
        print("=" * 80)
        print(f"移动文件: {len(self.moved_files)}")
        print(f"删除目录: {len(self.deleted_dirs)}")
        print(f"失败操作: {len(self.failed_operations)}")
        
        if self.moved_files:
            print("\n移动的文件:")
            for item in self.moved_files:
                print(f"  ✅ {item['from']} -> {item['to']}")
        
        if self.deleted_dirs:
            print("\n删除的目录:")
            for dir_path in self.deleted_dirs:
                print(f"  ✅ {dir_path}")
        
        if self.failed_operations:
            print("\n失败操作:")
            for item in self.failed_operations:
                print(f"  ❌ {item}")
        
        print("\n" + "=" * 80)
        print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        return {
            "moved_files": len(self.moved_files),
            "deleted_dirs": len(self.deleted_dirs),
            "failed_operations": len(self.failed_operations)
        }

if __name__ == "__main__":
    fixer = L1DeepDirFixer()
    fixer.run()
