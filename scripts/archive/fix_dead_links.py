#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
Layer 11死链接修复工具
用途：检测和修复Layer 11文档中的死链接
版本：v1.0
创建日期：2026-04-06
"""

import os
import re
from pathlib import Path
from typing import List, Tuple, Dict

LAYER11_DIR = Path("docs/11_STRATEGIC_DECISION")

DEAD_LINK_REPLACEMENTS = {
    "./RISK_BUDGET_BLUEPRINT.md": "./CAPITAL_ALLOCATION_BLUEPRINT.md",
    "./RISK_BUDGET_SYSTEM_BLUEPRINT.md": "./CAPITAL_ALLOCATION_BLUEPRINT.md",
    "./资产配置模型.md": "./CAPITAL_ALLOCATION_BLUEPRINT.md",
    "./风险预算框架.md": "./CAPITAL_ALLOCATION_BLUEPRINT.md",
    "./策略选择框架.md": "./MULTI_STRATEGY_COORDINATION_BLUEPRINT.md",
    "./配置优化方法.md": "./REBALANCING_BLUEPRINT.md",
    "./策略组合优化.md": "./MULTI_STRATEGY_COORDINATION_BLUEPRINT.md",
}


def find_all_links(content: str) -> List[Tuple[str, int]]:
    """查找文档中的所有链接"""
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    matches = re.finditer(pattern, content)
    links = []
    for match in matches:
        link_text = match.group(1)
        link_url = match.group(2)
        line_num = content[:match.start()].count('\n') + 1
        links.append((link_url, line_num, link_text))
    return links


def check_link_valid(link_url: str, file_path: Path) -> bool:
    """检查链接是否有效"""
    if link_url.startswith('http://') or link_url.startswith('https://'):
        return True
    
    if link_url.startswith('#'):
        return True
    
    if link_url.startswith('../'):
        target_path = file_path.parent.parent / link_url[3:]
    elif link_url.startswith('./'):
        target_path = file_path.parent / link_url[2:]
    else:
        target_path = file_path.parent / link_url
    
    return target_path.exists()


def fix_dead_links(file_path: Path) -> Tuple[int, List[str]]:
    """修复文档中的死链接"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        fixed_count = 0
        fixes = []
        
        for dead_link, replacement in DEAD_LINK_REPLACEMENTS.items():
            if dead_link in content:
                content = content.replace(dead_link, replacement)
                fixed_count += content.count(replacement) - original_content.count(replacement)
                fixes.append(f"{dead_link} -> {replacement}")
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ {file_path.name}: 修复 {fixed_count} 个死链接")
            for fix in fixes:
                print(f"  - {fix}")
            return fixed_count, fixes
        else:
            return 0, []
    
    except Exception as e:
        print(f"✗ {file_path.name}: 处理失败 - {e}")
        return 0, []


def scan_dead_links(file_path: Path) -> List[Tuple[str, int, str]]:
    """扫描文档中的死链接"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        links = find_all_links(content)
        dead_links = []
        
        for link_url, line_num, link_text in links:
            if not check_link_valid(link_url, file_path):
                dead_links.append((link_url, line_num, link_text))
        
        return dead_links
    
    except Exception as e:
        print(f"✗ {file_path.name}: 扫描失败 - {e}")
        return []


def main():
    """主函数"""
    print("=" * 80)
    print("Layer 11死链接修复工具")
    print("=" * 80)
    print()
    
    if not LAYER11_DIR.exists():
        print(f"✗ 目录不存在: {LAYER11_DIR}")
        return
    
    md_files = list(LAYER11_DIR.glob("*.md"))
    
    print(f"发现 {len(md_files)} 个Markdown文件")
    print()
    
    print("=" * 80)
    print("第一阶段：扫描死链接")
    print("=" * 80)
    print()
    
    total_dead_links = 0
    files_with_dead_links = []
    
    for md_file in sorted(md_files):
        dead_links = scan_dead_links(md_file)
        if dead_links:
            files_with_dead_links.append((md_file, dead_links))
            total_dead_links += len(dead_links)
            print(f"⚠️ {md_file.name}: 发现 {len(dead_links)} 个死链接")
            for link_url, line_num, link_text in dead_links:
                print(f"  - 行 {line_num}: [{link_text}]({link_url})")
    
    print()
    print(f"总计发现 {total_dead_links} 个死链接")
    print()
    
    print("=" * 80)
    print("第二阶段：修复死链接")
    print("=" * 80)
    print()
    
    total_fixed = 0
    total_fixes = []
    
    for md_file in sorted(md_files):
        fixed_count, fixes = fix_dead_links(md_file)
        total_fixed += fixed_count
        total_fixes.extend(fixes)
    
    print()
    print("=" * 80)
    print("修复总结")
    print("=" * 80)
    print(f"总计修复: {total_fixed} 个死链接")
    print()
    
    if total_fixes:
        print("修复详情:")
        for fix in total_fixes:
            print(f"  - {fix}")
    
    print()
    print("=" * 80)
    print("第三阶段：验证修复结果")
    print("=" * 80)
    print()
    
    remaining_dead_links = 0
    for md_file in sorted(md_files):
        dead_links = scan_dead_links(md_file)
        if dead_links:
            remaining_dead_links += len(dead_links)
            print(f"⚠️ {md_file.name}: 仍有 {len(dead_links)} 个死链接")
            for link_url, line_num, link_text in dead_links:
                print(f"  - 行 {line_num}: [{link_text}]({link_url})")
    
    print()
    print(f"剩余死链接: {remaining_dead_links} 个")
    print("=" * 80)


if __name__ == "__main__":
    main()
