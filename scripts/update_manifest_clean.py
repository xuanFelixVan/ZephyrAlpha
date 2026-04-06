#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System_Manifest.md Layer 9索引清理脚本
清理重复的Layer 9条目，只保留主蓝图和实施方案
"""

from pathlib import Path
import re

def update_system_manifest():
    file_path = Path("d:/ZephyrAlpha/docs/System_Manifest.md")
    
    with open(file_path, 'r', encoding='gbk') as f:
        content = f.read()
    
    print("检测到文件编码: GBK")
    
    # 定义要删除的旧条目模式
    old_patterns = [
        r'\| \[缺失模块补充设计\].*?LAYER9_SUPPLEMENT_001.*?\n',
        r'\| \[完整缺失模块补充方案v2\.0\].*?LAYER9_COMPLETE_002.*?\n',
        r'\| \[完整蓝图v3\.0\].*?LAYER9_COMPLETE_V3.*?\n',
        r'\| \[关键缺失模块补充v4\.0\].*?LAYER9_CRITICAL_V4.*?\n',
        r'\| \[完整实施方案v5\.0\].*?LAYER9_IMPLEMENTATION_V5.*?\n',
    ]
    
    # 删除旧条目
    for pattern in old_patterns:
        content = re.sub(pattern, '', content)
    
    # 更新主蓝图条目
    old_blueprint = r'\| \[研究与创断层蓝图\].*?RESEARCH_INNOVATION_001.*?\n'
    new_blueprint = '| [研究与创断层蓝图](../09_RESEARCH_INNOVATION/BLUEPRINT.md) | `docs/09_RESEARCH_INNOVATION/BLUEPRINT.md` | RESEARCH_INNOVATION_001 | 1.0 | Active | AI虚拟研究实验室、创新孵化器、学术跟踪、知识管理 |\n'
    content = re.sub(old_blueprint, new_blueprint, content)
    
    # 在主蓝图条目后添加实施方案条目
    insert_pattern = r'(\| \[研究与创断层蓝图\].*?RESEARCH_INNOVATION_001.*?\n)'
    insert_after = r'\1| [实施方案](../09_RESEARCH_INNOVATION/IMPLEMENTATION_GUIDE.md) | `docs/09_RESEARCH_INNOVATION/IMPLEMENTATION_GUIDE.md` | LAYER9_IMPL_001 | 1.0 | Active | 个人开发+AI维护完整方案，80%开源+专业治理 |\n'
    content = re.sub(insert_pattern, insert_after, content)
    
    # 更新版本号
    content = content.replace("v5.3.4", "v5.3.5")
    
    with open(file_path, 'w', encoding='gbk') as f:
        f.write(content)
    
    print("✅ System_Manifest.md 更新完成")
    print(f"   - 已删除5个重复的Layer 9条目")
    print(f"   - 已添加实施方案条目")
    print(f"   - 版本已更新为 v5.3.5")

if __name__ == "__main__":
    update_system_manifest()
