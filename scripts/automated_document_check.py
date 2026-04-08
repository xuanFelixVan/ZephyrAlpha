#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动化文档检查机制
"""

import os
import re
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"
FACTOR_LIBRARY = DOCS_DIR / "02_FACTOR_LIBRARY"
REPORT_DIR = DOCS_DIR / "09_AUDIT" / "STATE"

def check_naming_conventions():
    print("检查命名规范...")
    issues = []
    
    naming_pattern = re.compile(r'^[A-Z][A-Z0-9_]*\.md$')
    exceptions = ['INDEX.md', 'README.md', 'SITEMAP.md', 'BLUEPRINT.md', 'FAQ.md']
    
    for file_path in FACTOR_LIBRARY.rglob('*.md'):
        if file_path.name in exceptions:
            continue
        
        if not naming_pattern.match(file_path.name):
            issues.append({
                'file': str(file_path.relative_to(FACTOR_LIBRARY)),
                'issue': '命名不规范',
                'current': file_path.name
            })
    
    print(f"  发现 {len(issues)} 个命名问题")
    return issues

def check_responsibility_descriptions():
    print("检查职责描述...")
    issues = []
    
    for file_path in FACTOR_LIBRARY.rglob('*.md'):
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            resp_match = re.search(r'\*\*核心职责\*\*:\s*(.+)', content)
            
            if not resp_match:
                issues.append({
                    'file': str(file_path.relative_to(FACTOR_LIBRARY)),
                    'issue': '缺少职责描述'
                })
            else:
                responsibility = resp_match.group(1).strip()
                if len(responsibility) < 15:
                    issues.append({
                        'file': str(file_path.relative_to(FACTOR_LIBRARY)),
                        'issue': f'职责描述过短 ({len(responsibility)}字符)',
                        'responsibility': responsibility
                    })
        
        except Exception as e:
            pass
    
    print(f"  发现 {len(issues)} 个职责问题")
    return issues

def check_index_completeness():
    print("检查索引完备性...")
    issues = []
    
    if not (FACTOR_LIBRARY / 'INDEX.md').exists():
        issues.append({
            'file': 'INDEX.md',
            'issue': '根目录缺少INDEX.md'
        })
    
    for item in FACTOR_LIBRARY.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            if not (item / 'INDEX.md').exists():
                issues.append({
                    'directory': item.name,
                    'issue': '子目录缺少INDEX.md'
                })
    
    print(f"  发现 {len(issues)} 个索引问题")
    return issues

def check_dead_links():
    print("检查死链接...")
    issues = []
    
    for file_path in FACTOR_LIBRARY.rglob('*.md'):
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
            
            for link_text, link_path in links:
                if link_path.startswith('http') or link_path.startswith('#'):
                    continue
                
                target_path = file_path.parent / link_path
                if not target_path.exists():
                    issues.append({
                        'file': str(file_path.relative_to(FACTOR_LIBRARY)),
                        'issue': f'死链接: {link_path}',
                        'link_text': link_text
                    })
        
        except Exception as e:
            pass
    
    print(f"  发现 {len(issues)} 个死链接")
    return issues

def check_yaml_completeness():
    print("检查YAML完整性...")
    issues = []
    
    required_fields = ['module_id', 'version', 'status', 'created_date', 'owner']
    
    for file_path in FACTOR_LIBRARY.rglob('*.md'):
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            if not content.startswith('---'):
                issues.append({
                    'file': str(file_path.relative_to(FACTOR_LIBRARY)),
                    'issue': '缺少YAML头部'
                })
            else:
                yaml_content = content.split('---')[1]
                missing_fields = []
                
                for field in required_fields:
                    if f'{field}:' not in yaml_content:
                        missing_fields.append(field)
                
                if missing_fields:
                    issues.append({
                        'file': str(file_path.relative_to(FACTOR_LIBRARY)),
                        'issue': f'YAML缺少字段: {", ".join(missing_fields)}'
                    })
        
        except Exception as e:
            pass
    
    print(f"  发现 {len(issues)} 个YAML问题")
    return issues

def main():
    print("=" * 80)
    print("自动化文档检查")
    print("=" * 80)
    
    naming_issues = check_naming_conventions()
    resp_issues = check_responsibility_descriptions()
    index_issues = check_index_completeness()
    dead_links = check_dead_links()
    yaml_issues = check_yaml_completeness()
    
    total = len(naming_issues) + len(resp_issues) + len(index_issues) + len(dead_links) + len(yaml_issues)
    
    print("\n" + "=" * 80)
    print("检查完成")
    print("=" * 80)
    print(f"总问题数: {total}")

if __name__ == '__main__':
    main()
