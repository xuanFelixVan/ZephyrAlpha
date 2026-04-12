#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
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
                blueprint_files.append({
                    'name': file.replace('_BLUEPRINT.md', ''),
                    'path': str(rel_path).replace('\\', '/'),
                    'file': file
                })
    
    print(f"\n[信息] 找到 {len(blueprint_files)} 个BLUEPRINT文件")
    
    # 检查每个BLUEPRINT文件是否被索引
    indexed_count = 0
    unindexed_files = []
    
    for bp in blueprint_files:
        # 检查文件名或路径是否在索引中
        if bp['name'] in index_content or bp['path'] in index_content:
            indexed_count += 1
        else:
            unindexed_files.append(bp)
    
    print(f"[信息] 已索引: {indexed_count} 个文件")
    print(f"[信息] 未索引: {len(unindexed_files)} 个文件")
    
    if unindexed_files:
        print("\n[未索引文件列表]:")
        for bp in unindexed_files:
            print(f"  - {bp['path']}")
    else:
        print("\n[OK] 所有BLUEPRINT文件都已被索引！")
    
    print("\n" + "=" * 80)
    print("检查完成！")
    print("=" * 80)

if __name__ == "__main__":
    check_index_completeness()
