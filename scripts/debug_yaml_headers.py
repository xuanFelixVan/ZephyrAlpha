#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
YAML头部重复调试脚本
分析文件结构，找出修复失败的原因
"""

from pathlib import Path

def analyze_file(file_path: Path):
    """分析单个文件的结构"""
    print(f"\n=== 分析文件: {file_path.name} ===")
    
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    content = content.lstrip('\ufeff')
    
    parts = content.split('---')
    
    print(f"分割后的部分数: {len(parts)}")
    
    for i, part in enumerate(parts[:5]):
        print(f"\n--- Part {i} ---")
        print(f"长度: {len(part)}")
        print(f"前100个字符: {part[:100]}")
        print(f"是否以module_id开头: {part.strip().startswith('module_id')}")

def main():
    """主函数"""
    docs_dir = Path("D:/ZephyrAlpha/docs/10_AI_WORKFLOW")
    
    md_files = list(docs_dir.glob("SENTIMENT_ANALYSIS_MEDIUM_TERM_TECHNICAL_SPECIFICATION.md"))
    
    for md_file in md_files:
        analyze_file(md_file)

if __name__ == "__main__":
    main()
