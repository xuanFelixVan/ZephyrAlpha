#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YAML元数据检查器
检查文档的YAML头部元数据是否完整和规范
"""

import re
import yaml
from pathlib import Path
from datetime import datetime

class YAMLMetadataChecker:
    def __init__(self):
        self.required_fields = [
            'module_id',
            'version',
            'status',
            'created_date',
            'last_updated',
            'owner',
            'responsibility',
            'standard_type',
            'applicable_scope',
            'compliance_level'
        ]
        
        self.stats = {
            'total_files': 0,
            'valid_files': 0,
            'invalid_files': 0,
            'missing_fields': {},
            'errors': []
        }
    
    def check_all(self):
        """检查所有markdown文件的YAML元数据"""
        print("=" * 80)
        print("YAML元数据检查")
        print("=" * 80)
        
        docs_path = Path("docs")
        md_files = list(docs_path.rglob("*.md"))
        self.stats['total_files'] = len(md_files)
        
        print(f"找到 {len(md_files)} 个markdown文件")
        print()
        
        for md_file in md_files:
            self.check_file(md_file)
        
        self.print_stats()
    
    def check_file(self, md_file):
        """检查单个文件的YAML元数据"""
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取YAML头部
            yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            
            if not yaml_match:
                self.stats['invalid_files'] += 1
                self.stats['errors'].append({
                    'file': str(md_file),
                    'error': '缺少YAML头部'
                })
                print(f"[X] {md_file.relative_to('docs')}: 缺少YAML头部")
                return
            
            # 解析YAML
            try:
                yaml_content = yaml.safe_load(yaml_match.group(1))
            except yaml.YAMLError as e:
                self.stats['invalid_files'] += 1
                self.stats['errors'].append({
                    'file': str(md_file),
                    'error': f'YAML解析错误: {e}'
                })
                print(f"[X] {md_file.relative_to('docs')}: YAML解析错误")
                return
            
            # 检查必需字段
            missing_fields = []
            for field in self.required_fields:
                if field not in yaml_content:
                    missing_fields.append(field)
            
            if missing_fields:
                self.stats['invalid_files'] += 1
                for field in missing_fields:
                    if field not in self.stats['missing_fields']:
                        self.stats['missing_fields'][field] = []
                    self.stats['missing_fields'][field].append(str(md_file))
                
                print(f"[!] {md_file.relative_to('docs')}: 缺少字段 {missing_fields}")
            else:
                self.stats['valid_files'] += 1
                print(f"[OK] {md_file.relative_to('docs')}")
            
        except Exception as e:
            self.stats['errors'].append({
                'file': str(md_file),
                'error': str(e)
            })
            print(f"[X] {md_file.relative_to('docs')}: {e}")
    
    def print_stats(self):
        """输出统计信息"""
        print()
        print("=" * 80)
        print("检查统计")
        print("=" * 80)
        print(f"总文件数: {self.stats['total_files']}")
        print(f"有效文件数: {self.stats['valid_files']}")
        print(f"无效文件数: {self.stats['invalid_files']}")
        print(f"错误数: {len(self.stats['errors'])}")
        
        if self.stats['missing_fields']:
            print()
            print("缺失字段统计:")
            for field, files in self.stats['missing_fields'].items():
                print(f"  - {field}: {len(files)}个文件")
        
        if self.stats['errors']:
            print()
            print("错误详情:")
            for error in self.stats['errors'][:10]:  # 只显示前10个错误
                print(f"  - {error['file']}: {error['error']}")


def main():
    checker = YAMLMetadataChecker()
    checker.check_all()
    
    print()
    print("=" * 80)
    print("检查完成！")
    print("=" * 80)


if __name__ == '__main__':
    main()
