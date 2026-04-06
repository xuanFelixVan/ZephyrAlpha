#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System_Manifest.md Layer 9索引更新脚本 v2
"""

import os
from pathlib import Path

def update_system_manifest():
    file_path = Path("d:/ZephyrAlpha/docs/System_Manifest.md")
    
    with open(file_path, 'r', encoding='gbk') as f:
        content = f.read()
    
    print("检测到文件编码: GBK")
    
    layer9_entries = '''
| **Layer 9: 研究与创新层** | | | | | |
| [研究与创新层蓝图](../09_RESEARCH_INNOVATION/BLUEPRINT.md) | `docs/09_RESEARCH_INNOVATION/BLUEPRINT.md` | RESEARCH_INNOVATION_001 | 1.0 | Active | AI虚拟研究实验室、创新孵化器、学术跟踪、知识管理 |
| [缺失模块补充设计](../09_RESEARCH_INNOVATION/MISSING_MODULES_SUPPLEMENT.md) | `docs/09_RESEARCH_INNOVATION/MISSING_MODULES_SUPPLEMENT.md` | LAYER9_SUPPLEMENT_001 | 1.0 | Active | 特征存储、模型注册表、研究仪表板 |
| [完整缺失模块补充方案v2.0](../09_RESEARCH_INNOVATION/COMPLETE_SUPPLEMENT_v2.md) | `docs/09_RESEARCH_INNOVATION/COMPLETE_SUPPLEMENT_v2.md` | LAYER9_COMPLETE_002 | 2.0 | Active | 数据版本控制、超参数优化、模型解释性、A/B测试、审计日志、成本管理 |
'''
    
    if "LAYER9_SUPPLEMENT_001" in content:
        print("Layer 9蓝图索引已存在，无需更新")
        return
    
    lines = content.split('\n')
    insert_index = -1
    
    for i, line in enumerate(lines):
        if "FINANCING_BLUEPRINT" in line:
            insert_index = i + 1
            print(f"找到FINANCING_BLUEPRINT在第 {i+1} 行")
            break
    
    if insert_index == -1:
        print("无法找到插入位置")
        return
    
    print(f"将在第 {insert_index} 行后插入Layer 9索引")
    
    new_lines = lines[:insert_index] + layer9_entries.strip().split('\n') + lines[insert_index:]
    
    new_content = '\n'.join(new_lines)
    
    new_content = new_content.replace("2026-04-03", "2026-04-06")
    new_content = new_content.replace("v5.3.0", "v5.3.1")
    
    with open(file_path, 'w', encoding='gbk') as f:
        f.write(new_content)
    
    print("✅ System_Manifest.md 更新完成")
    print(f"   - 已添加Layer 9索引条目")
    print(f"   - 版本已更新为 v5.3.1")
    print(f"   - 日期已更新为 2026-04-06")

if __name__ == "__main__":
    update_system_manifest()
