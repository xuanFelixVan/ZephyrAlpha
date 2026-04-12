#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
Layer 4总索引链接有效性检查脚本
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

class LinkValidator:
    def __init__(self):
        self.project_root = Path(r"D:\ZephyrAlpha")
        self.docs_root = self.project_root / "docs"
        self.layer4_index_path = self.docs_root / "LAYER4_MASTER_INDEX.md"
        self.results = {
            "total_links": 0,
            "valid_links": 0,
            "invalid_links": 0,
            "missing_files": [],
            "valid_files": []
        }
    
    def extract_links(self, content: str) -> List[Tuple[str, str]]:
        pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        matches = re.findall(pattern, content)
        return matches
    
    def validate_link(self, link_text: str, link_path: str) -> Dict:
        if link_path.startswith('http://') or link_path.startswith('https://'):
            return {
                "text": link_text,
                "path": link_path,
                "status": "external",
                "valid": True
            }
        
        if link_path.startswith('#'):
            return {
                "text": link_text,
                "path": link_path,
                "status": "anchor",
                "valid": True
            }
        
        full_path = self.docs_root / link_path
        
        if full_path.exists():
            return {
                "text": link_text,
                "path": link_path,
                "status": "internal",
                "valid": True
            }
        else:
            return {
                "text": link_text,
                "path": link_path,
                "status": "internal",
                "valid": False
            }
    
    def run(self):
        print("=" * 80)
        print("Layer 4总索引链接有效性检查")
        print("=" * 80)
        
        if not self.layer4_index_path.exists():
            print(f"✗ Layer 4总索引文件不存在: {self.layer4_index_path}")
            return
        
        with open(self.layer4_index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        links = self.extract_links(content)
        
        print(f"\n发现 {len(links)} 个链接")
        print("-" * 80)
        
        for i, (link_text, link_path) in enumerate(links, 1):
            result = self.validate_link(link_text, link_path)
            self.results['total_links'] += 1
            
            if result['valid']:
                self.results['valid_links'] += 1
                self.results['valid_files'].append(result)
                print(f"[{i}/{len(links)}] ✓ {link_text} -> {link_path}")
            else:
                self.results['invalid_links'] += 1
                self.results['missing_files'].append(result)
                print(f"[{i}/{len(links)}] ✗ {link_text} -> {link_path} (文件不存在)")
        
        print("\n" + "=" * 80)
        print("链接有效性检查完成")
        print("=" * 80)
        print(f"总链接数: {self.results['total_links']}")
        print(f"有效链接: {self.results['valid_links']}")
        print(f"无效链接: {self.results['invalid_links']}")
        
        if self.results['total_links'] > 0:
            validity_rate = self.results['valid_links'] / self.results['total_links'] * 100
            print(f"有效率: {validity_rate:.2f}%")
        
        if self.results['missing_files']:
            print("\n缺失文件列表:")
            for missing in self.results['missing_files']:
                print(f"  - {missing['path']}")
        
        print("=" * 80)

if __name__ == "__main__":
    validator = LinkValidator()
    validator.run()
