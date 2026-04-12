#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
索引链接有效性验证脚本
验证所有INDEX.md文件中的链接是否有效
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple

class IndexLinkValidator:
    def __init__(self, docs_root: str):
        self.docs_root = Path(docs_root)
        self.results = {
            'total_links': 0,
            'valid_links': 0,
            'invalid_links': 0,
            'invalid_details': []
        }
    
    def find_all_index_files(self) -> List[Path]:
        """查找所有INDEX.md文件"""
        index_files = []
        for root, dirs, files in os.walk(self.docs_root):
            for file in files:
                if file == 'INDEX.md':
                    index_files.append(Path(root) / file)
        return index_files
    
    def extract_links(self, file_path: Path) -> List[Tuple[str, int]]:
        """从文件中提取所有链接"""
        links = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # 匹配Markdown链接格式 [text](url)
                matches = re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', line)
                for match in matches:
                    text, url = match.groups()
                    links.append((url, line_num, text))
        return links
    
    def validate_link(self, link: str, source_file: Path) -> Tuple[bool, str]:
        """验证单个链接是否有效"""
        # 跳过外部链接和锚点链接
        if link.startswith('http://') or link.startswith('https://'):
            return True, 'External link'
        if link.startswith('#'):
            return True, 'Anchor link'
        
        # 处理相对路径
        if link.startswith('./'):
            target_path = source_file.parent / link[2:]
        elif link.startswith('../'):
            target_path = source_file.parent / link
        else:
            target_path = source_file.parent / link
        
        # 规范化路径
        try:
            target_path = target_path.resolve()
        except:
            return False, f'Invalid path: {link}'
        
        # 检查文件是否存在
        if target_path.exists():
            return True, 'Valid'
        else:
            return False, f'File not found: {target_path.relative_to(self.docs_root)}'
    
    def validate_index_file(self, index_file: Path) -> Dict:
        """验证单个INDEX.md文件"""
        file_result = {
            'file': str(index_file.relative_to(self.docs_root)),
            'total': 0,
            'valid': 0,
            'invalid': 0,
            'invalid_links': []
        }
        
        links = self.extract_links(index_file)
        file_result['total'] = len(links)
        
        for url, line_num, text in links:
            is_valid, message = self.validate_link(url, index_file)
            if is_valid:
                file_result['valid'] += 1
            else:
                file_result['invalid'] += 1
                file_result['invalid_links'].append({
                    'line': line_num,
                    'text': text,
                    'url': url,
                    'message': message
                })
        
        return file_result
    
    def run_validation(self) -> Dict:
        """运行完整验证"""
        print("=" * 80)
        print("索引链接有效性验证")
        print("=" * 80)
        print(f"文档根目录: {self.docs_root}")
        print()
        
        index_files = self.find_all_index_files()
        print(f"找到 {len(index_files)} 个INDEX.md文件")
        print()
        
        all_results = []
        
        for index_file in index_files:
            result = self.validate_index_file(index_file)
            all_results.append(result)
            
            self.results['total_links'] += result['total']
            self.results['valid_links'] += result['valid']
            self.results['invalid_links'] += result['invalid']
            
            if result['invalid'] > 0:
                self.results['invalid_details'].append(result)
        
        # 打印摘要
        print("=" * 80)
        print("验证摘要")
        print("=" * 80)
        print(f"总链接数: {self.results['total_links']}")
        print(f"有效链接: {self.results['valid_links']}")
        print(f"无效链接: {self.results['invalid_links']}")
        
        if self.results['total_links'] > 0:
            validity_rate = (self.results['valid_links'] / self.results['total_links']) * 100
            print(f"链接有效率: {validity_rate:.1f}%")
        
        print()
        
        # 打印无效链接详情
        if self.results['invalid_details']:
            print("=" * 80)
            print("无效链接详情")
            print("=" * 80)
            
            for detail in self.results['invalid_details']:
                print(f"\n文件: {detail['file']}")
                print(f"无效链接数: {detail['invalid']}")
                
                for link in detail['invalid_links']:
                    print(f"  行 {link['line']}: [{link['text']}]({link['url']})")
                    print(f"    原因: {link['message']}")
        
        print()
        print("=" * 80)
        
        if self.results['invalid_links'] == 0:
            print("✅ 所有索引链接均有效！")
        else:
            print(f"⚠️ 发现 {self.results['invalid_links']} 个无效链接，请修复")
        
        return self.results

def main():
    docs_root = r"D:\ZephyrAlpha\docs"
    validator = IndexLinkValidator(docs_root)
    results = validator.run_validation()
    
    # 返回退出码
    exit(0 if results['invalid_links'] == 0 else 1)

if __name__ == "__main__":
    main()
