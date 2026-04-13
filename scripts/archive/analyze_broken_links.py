#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
死链接分析和修复脚本
用途: 分析死链接模式并生成修复建议
版本: v1.0.0
创建日期: 2026-04-07
"""

import os
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"

def find_broken_links():
    """扫描所有死链接"""
    broken_links = []
    
    for root, dirs, files in os.walk(DOCS_DIR):
        for file in files:
            if file.endswith('.md'):
                file_path = Path(root) / file
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    relative_path = file_path.relative_to(DOCS_DIR)
                    
                    links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
                    
                    for link_text, link_path in links:
                        if link_path.startswith('http') or link_path.startswith('#'):
                            continue
                        
                        if not link_path.startswith('/'):
                            target_path = (file_path.parent / link_path).resolve()
                            
                            if not target_path.exists():
                                broken_links.append({
                                    "file": str(relative_path),
                                    "link": link_path,
                                    "text": link_text
                                })
                
                except Exception as e:
                    pass
    
    return broken_links

def analyze_broken_links(broken_links):
    """分析死链接模式"""
    patterns = defaultdict(list)
    
    for link_info in broken_links:
        link = link_info["link"]
        
        if "FACTOR_REGISTRY" in link:
            patterns["FACTOR_REGISTRY缺失"].append(link_info)
        elif "ARCHITECTURE_DECISIONS" in link:
            patterns["ARCHITECTURE_DECISIONS目录缺失"].append(link_info)
        elif "LAYER4_DEEP_AUDIT_REPORT" in link:
            patterns["LAYER4审计报告缺失"].append(link_info)
        elif "INTELLIGENT_SCHEDULER" in link:
            patterns["INTELLIGENT_SCHEDULER蓝图缺失"].append(link_info)
        elif "LAYER4_MISSING_MODULES" in link:
            patterns["LAYER4_MISSING_MODULES蓝图缺失"].append(link_info)
        elif "00_GOVERNANCE" in link:
            patterns["00_GOVERNANCE目录缺失"].append(link_info)
        elif "../" in link:
            patterns["相对路径问题"].append(link_info)
        else:
            patterns["其他"].append(link_info)
    
    return patterns

def generate_fix_suggestions(patterns):
    """生成修复建议"""
    suggestions = []
    
    for pattern, links in patterns.items():
        if pattern == "FACTOR_REGISTRY缺失":
            suggestions.append({
                "pattern": pattern,
                "count": len(links),
                "suggestion": "创建FACTOR_REGISTRY.md文件或更新链接指向现有的因子管理文档",
                "example_files": [link["file"] for link in links[:3]]
            })
        elif pattern == "ARCHITECTURE_DECISIONS目录缺失":
            suggestions.append({
                "pattern": pattern,
                "count": len(links),
                "suggestion": "创建ARCHITECTURE_DECISIONS目录或更新链接指向现有的架构文档",
                "example_files": [link["file"] for link in links[:3]]
            })
        elif pattern == "LAYER4审计报告缺失":
            suggestions.append({
                "pattern": pattern,
                "count": len(links),
                "suggestion": "更新链接指向现有的审计报告或删除链接",
                "example_files": [link["file"] for link in links[:3]]
            })
        elif pattern == "INTELLIGENT_SCHEDULER蓝图缺失":
            suggestions.append({
                "pattern": pattern,
                "count": len(links),
                "suggestion": "创建INTELLIGENT_SCHEDULER_BLUEPRINT.md或更新链接",
                "example_files": [link["file"] for link in links[:3]]
            })
        elif pattern == "LAYER4_MISSING_MODULES蓝图缺失":
            suggestions.append({
                "pattern": pattern,
                "count": len(links),
                "suggestion": "更新链接指向MISSING_MODULES_BLUEPRINT.md",
                "example_files": [link["file"] for link in links[:3]]
            })
        elif pattern == "00_GOVERNANCE目录缺失":
            suggestions.append({
                "pattern": pattern,
                "count": len(links),
                "suggestion": "创建00_GOVERNANCE目录或更新链接",
                "example_files": [link["file"] for link in links[:3]]
            })
        elif pattern == "相对路径问题":
            suggestions.append({
                "pattern": pattern,
                "count": len(links),
                "suggestion": "修复相对路径引用，使用正确的相对路径",
                "example_files": [link["file"] for link in links[:3]]
            })
        else:
            suggestions.append({
                "pattern": pattern,
                "count": len(links),
                "suggestion": "需要手动审查和修复",
                "example_files": [link["file"] for link in links[:3]]
            })
    
    return suggestions

def main():
    print("=" * 80)
    print("死链接分析和修复建议")
    print("=" * 80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    print("\n扫描死链接...")
    broken_links = find_broken_links()
    print(f"发现 {len(broken_links)} 个死链接")
    
    print("\n分析死链接模式...")
    patterns = analyze_broken_links(broken_links)
    
    print("\n" + "=" * 80)
    print("死链接模式分析")
    print("=" * 80)
    
    for pattern, links in sorted(patterns.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"\n{pattern}: {len(links)}个")
        for link in links[:3]:
            print(f"  - {link['file']} -> {link['link']}")
    
    print("\n" + "=" * 80)
    print("修复建议")
    print("=" * 80)
    
    suggestions = generate_fix_suggestions(patterns)
    
    for suggestion in sorted(suggestions, key=lambda x: x["count"], reverse=True):
        print(f"\n{suggestion['pattern']}: {suggestion['count']}个")
        print(f"  建议: {suggestion['suggestion']}")
        print(f"  示例文件: {', '.join(suggestion['example_files'])}")
    
    print("\n" + "=" * 80)
    print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

if __name__ == "__main__":
    main()
