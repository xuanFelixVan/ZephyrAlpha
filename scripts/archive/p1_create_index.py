# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
P1-2问题修复脚本 - 创建INDEX.md
用途：为17个缺少INDEX.md的目录创建导航文件
创建时间：2026-04-07
"""

import os
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"

class P1IndexCreator:
    def __init__(self):
        self.created_indexes = []
        self.failed_indexes = []
        
    def find_missing_index_dirs(self):
        print("扫描缺少INDEX.md的目录...")
        missing_dirs = []
        
        for root, dirs, files in os.walk(DOCS_DIR):
            root_path = Path(root)
            
            index_file = root_path / "INDEX.md"
            if not index_file.exists():
                index_file = root_path / "index.md"
            
            md_files = [f for f in root_path.glob("*.md") if f.name.lower() not in ['index.md', 'readme.md']]
            
            if len(md_files) > 0 and not index_file.exists():
                missing_dirs.append(root_path)
        
        print(f"发现 {len(missing_dirs)} 个缺少INDEX.md的目录")
        return missing_dirs
    
    def create_index(self, dir_path):
        try:
            relative_path = dir_path.relative_to(DOCS_DIR)
            
            md_files = [f for f in dir_path.glob("*.md") if f.name.lower() not in ['index.md', 'readme.md']]
            
            dir_name = dir_path.name
            
            index_content = f"""---
responsibility:
  - 目录导航、文档索引
module_id: INDEX_{dir_name.upper()}_{datetime.now().strftime('%Y%m%d%H%M%S')}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 个人开发者
standard_type: 专业量化机构文档
---

# {dir_name} 目录索引

> **核心职责**: 提供{dir_name}目录下的文档导航
> **职责边界**: 
> - ✅ 本索引负责：{dir_name}目录下的文档导航
> - ❌ 本索引不负责：其他目录内容

---

## 📋 目录概览

**目录路径**: {relative_path}  
**文档数量**: {len(md_files)}个  
**最后更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📚 文档列表

"""
            
            for md_file in sorted(md_files):
                file_name = md_file.stem
                file_relative = md_file.name
                
                index_content += f"- [{file_name}]({file_relative})\n"
            
            index_content += f"""

---

## 📊 统计信息

| 指标 | 数值 |
|------|------|
| **总文档数** | {len(md_files)} |
| **创建时间** | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |

---

**索引生成**: 文档治理优化系统  
**下一步**: 定期更新索引，确保文档完整性
"""
            
            index_path = dir_path / "INDEX.md"
            
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(index_content)
            
            self.created_indexes.append({
                "path": str(relative_path),
                "file_count": len(md_files)
            })
            
            return True
        
        except Exception as e:
            print(f"  ❌ 创建失败: {dir_path} - {e}")
            self.failed_indexes.append({
                "path": str(dir_path.relative_to(DOCS_DIR)),
                "error": str(e)
            })
            return False
    
    def run(self):
        print("=" * 80)
        print("P1-2问题修复 - 创建INDEX.md")
        print("=" * 80)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        missing_dirs = self.find_missing_index_dirs()
        
        print(f"\n开始创建INDEX.md...")
        success_count = 0
        
        for i, dir_path in enumerate(missing_dirs, 1):
            print(f"[{i}/{len(missing_dirs)}] 处理: {dir_path.relative_to(DOCS_DIR)}")
            
            if self.create_index(dir_path):
                success_count += 1
        
        print("\n" + "=" * 80)
        print("修复统计")
        print("=" * 80)
        print(f"总目录数: {len(missing_dirs)}")
        print(f"成功创建: {success_count}")
        print(f"失败: {len(self.failed_indexes)}")
        
        if self.created_indexes:
            print("\n成功创建示例:")
            for item in self.created_indexes[:10]:
                print(f"  ✅ {item['path']} ({item['file_count']}个文档)")
        
        if self.failed_indexes:
            print("\n失败目录:")
            for item in self.failed_indexes[:10]:
                print(f"  ❌ {item['path']}: {item['error']}")
        
        print("\n" + "=" * 80)
        print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        return {
            "total": len(missing_dirs),
            "success": success_count,
            "failed": len(self.failed_indexes),
            "created_indexes": self.created_indexes,
            "failed_indexes": self.failed_indexes
        }

if __name__ == "__main__":
    creator = P1IndexCreator()
    creator.run()
