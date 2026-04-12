#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
YAML头部重复修复脚本
删除舆情分析层所有文件的第一个YAML头部，保留第二个YAML头部
"""

import re
from pathlib import Path
from typing import List, Tuple

class YAMLHeaderFixer:
    """YAML头部修复器"""
    
    def __init__(self):
        self.fixed_count = 0
        self.total_count = 0
        self.error_count = 0
    
    def detect_double_yaml_headers(self, content: str) -> Tuple[bool, str]:
        """检测是否有两个YAML头部"""
        pattern = r'^---\s*\n(.*?)\n---\s*\n\s*---\s*\n(.*?)\n---'
        match = re.match(pattern, content, re.DOTALL)
        
        if match:
            first_yaml = match.group(1)
            second_yaml = match.group(2)
            return True, second_yaml
        
        return False, ""
    
    def fix_yaml_header(self, file_path: Path) -> bool:
        """修复单个文件的YAML头部"""
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            has_double, second_yaml = self.detect_double_yaml_headers(content)
            
            if not has_double:
                return False
            
            new_content = re.sub(
                r'^---\s*\n.*?\n---\s*\n\s*---\s*\n',
                '---\n',
                content,
                count=1,
                flags=re.DOTALL
            )
            
            with open(file_path, 'w', encoding='utf-8-sig') as f:
                f.write(new_content)
            
            return True
            
        except Exception as e:
            print(f"  [ERROR] 修复失败: {file_path.name} - {e}")
            self.error_count += 1
            return False
    
    def run(self, docs_dir: Path):
        """执行修复"""
        print("=== 开始修复YAML头部重复 ===\n")
        
        md_files = list(docs_dir.glob("**/*.md"))
        
        for md_file in md_files:
            if any(keyword in str(md_file) for keyword in ['06_ARCHIVE', '09_ARCHIVE', '99_ARCHIVE', 'archive']):
                continue
            
            self.total_count += 1
            
            if self.fix_yaml_header(md_file):
                self.fixed_count += 1
                print(f"  [OK] 修复: {md_file.name}")
        
        print(f"\n=== 修复完成 ===")
        print(f"总文件数: {self.total_count}")
        print(f"修复文件数: {self.fixed_count}")
        print(f"错误文件数: {self.error_count}")
        if self.total_count > 0:
            print(f"修复率: {self.fixed_count/self.total_count*100:.2f}%")

def main():
    """主函数"""
    docs_dir = Path("D:/ZephyrAlpha/docs/10_AI_WORKFLOW")
    fixer = YAMLHeaderFixer()
    fixer.run(docs_dir)

if __name__ == "__main__":
    main()
