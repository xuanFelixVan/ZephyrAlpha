#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 8 索引完整性检查脚本
检查所有BLUEPRINT文件是否被主索引正确列出
"""

import os
import re
from pathlib import Path

BASE_DIR = Path("D:/ZephyrAlpha/docs/08_HUMAN_AI_INTERFACE")

def check_index_completeness():
    """检查索引完整性"""
    print("=" * 80)
    print("Layer 8 索引完整性检查")
    print("=" * 80)
    
    # 读取主索引文件
    main_index = BASE_DIR / "index.md"
    if not main_index.exists():
        print("[错误] 主索引文件不存在！")
        return
    
    with open(main_index, 'r', encoding='utf-8') as f:
        index_content = f.read()
    
    # 获取所有BLUEPRINT文件
    blueprint_files = []
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith('_BLUEPRINT.md'):
                file_path = Path(root) / file
                rel_path = file_path.relative_to(BASE_DIR)
                blueprint_files.append(str(rel_path).replace('\\', '/'))
    
    print(f"\n[信息] 找到 {len(blueprint_files)} 个BLUEPRINT文件")
    
    # 检查每个BLUEPRINT文件是否被索引
    indexed_files = []
    unindexed_files = []
    
    for blueprint in blueprint_files:
        # 检查文件名是否在索引中
        file_name = Path(blueprint).stem
        if file_name in index_content or blueprint in index_content:
            indexed_files.append(blueprint)
        else:
            unindexed_files.append(blueprint)
    
    print(f"\n[结果] 已索引: {len(indexed_files)} 个文件")
    print(f"[结果] 未索引: {len(unindexed_files)} 个文件")
    
    if unindexed_files:
        print("\n[未索引文件列表]:")
        for file in unindexed_files:
            print(f"  - {file}")
    else:
        print("\n[OK] 所有BLUEPRINT文件都已被索引！")
    
    # 检查链接格式
    print("\n[检查] 链接格式...")
    links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', index_content)
    blueprint_links = [link for link in links if link[1].endswith('_BLUEPRINT.md')]
    
    print(f"[信息] 找到 {len(blueprint_links)} 个BLUEPRINT链接")
    
    # 检查链接是否有效
    invalid_links = []
    for link_text, link_path in blueprint_links:
        full_path = BASE_DIR / link_path
        if not full_path.exists():
            invalid_links.append((link_text, link_path))
    
    if invalid_links:
        print(f"\n[警告] 发现 {len(invalid_links)} 个无效链接:")
        for link_text, link_path in invalid_links:
            print(f"  - [{link_text}]({link_path})")
    else:
        print("[OK] 所有链接都有效！")
    
    print("\n" + "=" * 80)
    print("检查完成！")
    print("=" * 80)

if __name__ == "__main__":
    check_index_completeness()
