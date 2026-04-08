#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量修复旧架构命名残留
将"Layer 0-8"更新为"Layer 0-11"架构
"""

import os
import re
from pathlib import Path

def fix_layer_naming(file_path):
    """修复单个文件的Layer命名"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        original_content = content
        
        # 修复Layer引用
        # 1. 修复"Layer 0-8" -> "Layer 0-11"
        content = re.sub(r'Layer\s+0-8', 'Layer 0-11', content)
        
        # 2. 修复单独的"Layer 0"到"Layer 8"引用（保留Layer 9-11）
        # 注意：这里需要小心，不要误改已经是Layer 9-11的内容
        # 只修复明确标注为旧架构的内容
        
        # 3. 修复applicable_scope中的Layer引用
        content = re.sub(r'applicable_scope:\s*Layer\s+(\d)', 
                        lambda m: f'applicable_scope: Layer {m.group(1)}', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8-sig') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """主函数"""
    docs_dir = Path("D:/ZephyrAlpha/docs")
    
    # 统计
    total_files = 0
    fixed_files = 0
    
    # 遍历所有Markdown文件
    for md_file in docs_dir.rglob("*.md"):
        total_files += 1
        if fix_layer_naming(md_file):
            fixed_files += 1
            print(f"Fixed: {md_file.relative_to(docs_dir)}")
    
    print(f"\n=== 修复完成 ===")
    print(f"总文件数: {total_files}")
    print(f"修复文件数: {fixed_files}")
    print(f"修复率: {fixed_files/total_files*100:.2f}%")

if __name__ == "__main__":
    main()
