#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
检查文件编码和YAML内容
"""

import re
from pathlib import Path

file_path = Path("D:/ZephyrAlpha/docs/08_HUMAN_AI_INTERFACE/BLUEPRINT_CHAPTER_NAMING_STANDARD.md")

# 尝试不同编码读取文件
encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312']

for encoding in encodings:
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            content = f.read()
        
        print(f"\n{'='*60}")
        print(f"编码: {encoding}")
        print(f"{'='*60}")
        
        # 提取YAML头部
        yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        
        if yaml_match:
            yaml_content = yaml_match.group(1)
            print("\nYAML内容:")
            print(yaml_content)
            
            # 检查responsibility字段
            resp_match = re.search(r'responsibility:\s*\n((?:\s+-.*\n)+)', yaml_content)
            if resp_match:
                print("\n✅ 找到responsibility字段:")
                print(resp_match.group(0))
            else:
                print("\n❌ 未找到responsibility字段")
        else:
            print("\n❌ 未找到YAML头部")
        
        break
        
    except Exception as e:
        print(f"\n编码 {encoding} 读取失败: {e}")
