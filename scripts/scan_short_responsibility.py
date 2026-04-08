#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
职责描述过短检测脚本
扫描舆情分析层所有文件，找出职责描述不足20字符的文件
"""

import re
from pathlib import Path
from typing import List, Dict

class ShortResponsibilityScanner:
    """职责描述过短扫描器"""
    
    def __init__(self):
        self.min_length = 20
        self.short_files = []
    
    def scan_file(self, file_path: Path) -> List[Dict]:
        """扫描单个文件"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            content = content.lstrip('\ufeff')
            
            yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            if not yaml_match:
                return issues
            
            yaml_content = yaml_match.group(1)
            
            responsibility_match = re.search(r'responsibility:\s*\n((?:  - .*\n)+)', yaml_content)
            if not responsibility_match:
                return issues
            
            responsibility_text = responsibility_match.group(1)
            
            for line in responsibility_text.split('\n'):
                line = line.strip()
                if line.startswith('- '):
                    resp = line[2:]
                    
                    if len(resp) < self.min_length:
                        issues.append({
                            'file': file_path.name,
                            'responsibility': resp,
                            'length': len(resp)
                        })
            
        except Exception as e:
            pass
        
        return issues
    
    def run(self, docs_dir: Path):
        """执行扫描"""
        print("=== Scanning for Short Responsibilities ===\n")
        
        md_files = list(docs_dir.glob("*.md"))
        
        for md_file in md_files:
            issues = self.scan_file(md_file)
            if issues:
                self.short_files.extend(issues)
        
        print(f"Found {len(self.short_files)} short responsibilities:\n")
        
        for issue in self.short_files:
            print(f"  File: {issue['file']}")
            print(f"    Responsibility: {issue['responsibility']}")
            print(f"    Length: {issue['length']} chars")
            print()
        
        return self.short_files

def main():
    """主函数"""
    docs_dir = Path("D:/ZephyrAlpha/docs/10_ai_workflow")
    scanner = ShortResponsibilityScanner()
    scanner.run(docs_dir)

if __name__ == "__main__":
    main()
