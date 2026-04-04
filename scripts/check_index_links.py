#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INDEX.md链接检查脚本

快速检查INDEX.md中的所有链接是否有效
"""

import re
from pathlib import Path

def check_index_links():
    """检查INDEX.md中的所有链接"""
    
    index_file = Path("docs/INDEX.md")
    docs_root = Path("docs")
    
    if not index_file.exists():
        print(f"错误: {index_file} 不存在")
        return
    
    # 读取INDEX.md
    with open(index_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取所有相对路径链接
    pattern = r'\]\(\.\/([^)]+)\)'
    matches = re.findall(pattern, content)
    
    # 去重
    unique_links = set(matches)
    
    print(f"INDEX.md中共发现 {len(matches)} 个链接，其中 {len(unique_links)} 个唯一链接\n")
    
    # 检查每个链接
    broken_links = []
    valid_links = []
    
    for link in sorted(unique_links):
        target_path = docs_root / link
        
        if target_path.exists():
            valid_links.append(link)
        else:
            broken_links.append(link)
    
    # 输出结果
    print("=" * 80)
    print(f"✅ 有效链接: {len(valid_links)}")
    print("=" * 80)
    
    if broken_links:
        print("\n" + "=" * 80)
        print(f"❌ 失效链接: {len(broken_links)}")
        print("=" * 80)
        for link in sorted(broken_links):
            print(f"  - {link}")
    else:
        print("\n✅ 所有链接均有效！")
    
    return broken_links

if __name__ == '__main__':
    broken_links = check_index_links()
    
    if broken_links:
        exit(1)
    else:
        exit(0)
