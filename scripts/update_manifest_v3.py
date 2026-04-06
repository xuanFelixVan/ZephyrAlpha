#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System_Manifest.md Layer 9 v3.0蓝图索引更新脚本
"""

from pathlib import Path

def update_system_manifest():
    file_path = Path("d:/ZephyrAlpha/docs/System_Manifest.md")
    
    with open(file_path, 'r', encoding='gbk') as f:
        content = f.read()
    
    print("检测到文件编码: GBK")
    
    new_entry = '''| [完整蓝图v3.0](../09_RESEARCH_INNOVATION/COMPLETE_BLUEPRINT_V3.md) | `docs/09_RESEARCH_INNOVATION/COMPLETE_BLUEPRINT_V3.md` | LAYER9_COMPLETE_V3 | 3.0 | Active | 完整专业级蓝图，覆盖所有8大平台 |
'''
    
    if "LAYER9_COMPLETE_V3" in content:
        print("v3.0蓝图索引已存在，无需更新")
        return
    
    if "LAYER9_COMPLETE_002" not in content:
        print("未找到LAYER9_COMPLETE_002，无法插入")
        return
    
    lines = content.split('\n')
    insert_index = -1
    
    for i, line in enumerate(lines):
        if "LAYER9_COMPLETE_002" in line:
            insert_index = i + 1
            print(f"找到LAYER9_COMPLETE_002在第 {i+1} 行")
            break
    
    if insert_index == -1:
        print("无法找到插入位置")
        return
    
    print(f"将在第 {insert_index} 行后插入v3.0蓝图索引")
    
    new_lines = lines[:insert_index] + [new_entry.strip()] + lines[insert_index:]
    
    new_content = '\n'.join(new_lines)
    
    new_content = new_content.replace("v5.3.1", "v5.3.2")
    
    with open(file_path, 'w', encoding='gbk') as f:
        f.write(new_content)
    
    print("✅ System_Manifest.md 更新完成")
    print(f"   - 已添加Layer 9 v3.0蓝图索引")
    print(f"   - 版本已更新为 v5.3.2")

if __name__ == "__main__":
    update_system_manifest()
