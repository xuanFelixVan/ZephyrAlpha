# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
L1最终修复脚本 - 处理剩余旧架构命名文件
用途：处理10个剩余的旧架构命名文件
创建时间：2026-04-07
"""

import os
import re
import hashlib
import shutil
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"

class L1FinalFixer:
    def __init__(self):
        self.deleted_files = []
        self.renamed_files = []
        self.failed_files = []
        
    def find_old_architecture_files(self):
        print("扫描剩余旧架构文件...")
        old_files = []
        
        for root, dirs, files in os.walk(DOCS_DIR):
            for file in files:
                if file.endswith('.md'):
                    if re.search(r'layer\s*[0-8]', file, re.IGNORECASE):
                        file_path = Path(root) / file
                        old_files.append(file_path)
        
        print(f"发现 {len(old_files)} 个旧架构文件")
        return old_files
    
    def get_file_hash(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return hashlib.md5(content.encode()).hexdigest()
        except:
            return None
    
    def process_file(self, file_path):
        try:
            old_name = file_path.name
            
            new_name = re.sub(r'layer\s*[0-8]+_', '', old_name, flags=re.IGNORECASE)
            
            if old_name == new_name:
                return False
            
            new_path = file_path.parent / new_name
            
            if new_path.exists():
                old_hash = self.get_file_hash(file_path)
                new_hash = self.get_file_hash(new_path)
                
                if old_hash == new_hash:
                    os.remove(file_path)
                    self.deleted_files.append({
                        "path": str(file_path.relative_to(DOCS_DIR)),
                        "reason": "与目标文件内容相同"
                    })
                    print(f"  ✅ 删除重复文件: {file_path.name}")
                    return True
                else:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    unique_name = f"{file_path.stem}_{timestamp}.md"
                    unique_path = file_path.parent / unique_name
                    
                    os.rename(file_path, unique_path)
                    self.renamed_files.append({
                        "old_path": str(file_path.relative_to(DOCS_DIR)),
                        "new_path": str(unique_path.relative_to(DOCS_DIR)),
                        "reason": "内容不同，重命名为唯一名称"
                    })
                    print(f"  ✅ 重命名为唯一名称: {file_path.name} -> {unique_name}")
                    return True
            else:
                os.rename(file_path, new_path)
                self.renamed_files.append({
                    "old_path": str(file_path.relative_to(DOCS_DIR)),
                    "new_path": str(new_path.relative_to(DOCS_DIR)),
                    "reason": "目标文件不存在，直接重命名"
                })
                print(f"  ✅ 重命名: {file_path.name} -> {new_name}")
                return True
        
        except Exception as e:
            print(f"  ❌ 处理失败: {file_path} - {e}")
            self.failed_files.append({
                "path": str(file_path.relative_to(DOCS_DIR)),
                "error": str(e)
            })
            return False
    
    def run(self):
        print("=" * 80)
        print("L1最终修复 - 处理剩余旧架构命名文件")
        print("=" * 80)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        old_files = self.find_old_architecture_files()
        
        print(f"\n开始处理...")
        success_count = 0
        
        for i, file_path in enumerate(old_files, 1):
            print(f"[{i}/{len(old_files)}] 处理: {file_path.name}")
            
            if self.process_file(file_path):
                success_count += 1
        
        print("\n" + "=" * 80)
        print("修复统计")
        print("=" * 80)
        print(f"总文件数: {len(old_files)}")
        print(f"成功处理: {success_count}")
        print(f"删除文件: {len(self.deleted_files)}")
        print(f"重命名文件: {len(self.renamed_files)}")
        print(f"失败: {len(self.failed_files)}")
        
        if self.deleted_files:
            print("\n删除的文件:")
            for item in self.deleted_files:
                print(f"  ✅ {item['path']} ({item['reason']})")
        
        if self.renamed_files:
            print("\n重命名的文件:")
            for item in self.renamed_files:
                print(f"  ✅ {item['old_path']} -> {item['new_path']}")
                print(f"     原因: {item['reason']}")
        
        if self.failed_files:
            print("\n失败文件:")
            for item in self.failed_files:
                print(f"  ❌ {item['path']}: {item['error']}")
        
        print("\n" + "=" * 80)
        print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        return {
            "total": len(old_files),
            "success": success_count,
            "deleted": len(self.deleted_files),
            "renamed": len(self.renamed_files),
            "failed": len(self.failed_files)
        }

if __name__ == "__main__":
    fixer = L1FinalFixer()
    fixer.run()
