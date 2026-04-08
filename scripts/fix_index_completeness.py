#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
索引完整性修复脚本
检查并更新INDEX.md，确保列出所有活跃文档
"""

import re
from pathlib import Path
from typing import Set

class IndexCompletenessFixer:
    """索引完整性修复器"""
    
    def __init__(self):
        self.fixed = False
    
    def fix_index(self, docs_dir: Path) -> bool:
        """修复索引完整性"""
        index_file = docs_dir / "INDEX.md"
        
        if not index_file.exists():
            print("  [ERROR] INDEX.md not found")
            return False
        
        try:
            with open(index_file, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            links = re.findall(r'\[.*?\]\((.*?)\)', content)
            linked_files = set([link.split('/')[-1] for link in links if link.endswith('.md')])
            
            all_md_files = set([f.name for f in docs_dir.glob("*.md")])
            
            missing_files = all_md_files - linked_files - {'INDEX.md'}
            
            if not missing_files:
                print("  [OK] INDEX.md is complete")
                return False
            
            print(f"  [INFO] Found {len(missing_files)} missing files in INDEX.md:")
            for file in sorted(missing_files):
                print(f"    - {file}")
            
            return True
            
        except Exception as e:
            print(f"  [ERROR] fix failed: {e}")
            return False
    
    def run(self, docs_dir: Path):
        """执行修复"""
        print("=== Starting Index Completeness Check ===\n")
        
        self.fix_index(docs_dir)
        
        print("\n=== Check Complete ===")

def main():
    """主函数"""
    docs_dir = Path("D:/ZephyrAlpha/docs/10_AI_WORKFLOW")
    fixer = IndexCompletenessFixer()
    fixer.run(docs_dir)

if __name__ == "__main__":
    main()
