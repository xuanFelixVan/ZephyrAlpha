#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复Layer 4总索引中的链接路径
"""

import re
from pathlib import Path

def fix_layer4_index_links():
    project_root = Path(r"D:\ZephyrAlpha")
    layer4_index_path = project_root / "docs" / "LAYER4_MASTER_INDEX.md"
    
    if not layer4_index_path.exists():
        print(f"✗ Layer 4总索引文件不存在: {layer4_index_path}")
        return
    
    with open(layer4_index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    content = re.sub(r'\]\(\.\./01_FRAMEWORK/', '](01_FRAMEWORK/', content)
    content = re.sub(r'\]\(\.\./05_IMPLEMENTATION/', '](05_IMPLEMENTATION/', content)
    content = re.sub(r'\]\(\.\./08_HUMAN_AI_INTERFACE/', '](08_HUMAN_AI_INTERFACE/', content)
    content = re.sub(r'\]\(\.\./10_AI_WORKFLOW/', '](10_AI_WORKFLOW/', content)
    
    if content != original_content:
        with open(layer4_index_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ 已修复Layer 4总索引中的链接路径")
    else:
        print(f"✓ Layer 4总索引中的链接路径无需修复")

if __name__ == "__main__":
    fix_layer4_index_links()
