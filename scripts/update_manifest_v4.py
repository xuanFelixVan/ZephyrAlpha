#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System_Manifest.md Layer 9 v4.0蓝图索引更新脚本
"""

from pathlib import Path

def update_system_manifest():
    file_path = Path("d:/ZephyrAlpha/docs/System_Manifest.md")
    
    with open(file_path, 'r', encoding='gbk') as f:
        content = f.read()
    
    print("检测到文件编码: GBK")
    
    new_entry = '''| [关键缺失模块补充v4.0](../09_RESEARCH_INNOVATION/CRITICAL_MISSING_V4.md) | `docs/09_RESEARCH_INNOVATION/CRITICAL_MISSING_V4.md` | LAYER9_CRITICAL_V4 | 4.0 | Active | 10个关键缺失模块：RD-Agent、时间泄漏控制、数据契约等 |'''
    
    if "LAYER9_CRITICAL_V4" in content:
        print("v4.0蓝图索引已存在，无需更新")
        return
    
    lines = content.split('\n')
    insert_index = -1
    
    for i, line in enumerate(lines):
        if "LAYER9_COMPLETE_V3" in line:
            insert_index = i + 1
            print(f"找到LAYER9_COMPLETE_V3在第 {i+1} 行")
            break
    
    if insert_index == -1:
        print("无法找到插入位置")
        return
    
    print(f"将在第 {insert_index} 行后插入v4.0蓝图索引")
    
    new_lines = lines[:insert_index] + [new_entry] + lines[insert_index:]
    
    new_content = '\n'.join(new_lines)
    
    new_content = new_content.replace("v5.3.2", "v5.3.3")
    
    with open(file_path, 'w', encoding='gbk') as f:
        f.write(new_content)
    
    print("✅ System_Manifest.md 更新完成")
    print(f"   - 已添加Layer 9 v4.0蓝图索引")
    print(f"   - 版本已更新为 v5.3.3")

if __name__ == "__main__":
    update_system_manifest()
