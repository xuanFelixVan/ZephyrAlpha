#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复告警功能职责重叠问题
"""

import os

def fix_realtime_quality_monitor():
    """修复REALTIME_QUALITY_MONITOR_BLUEPRINT.md"""
    file_path = r"docs\05_IMPLEMENTATION\06_CONSTRUCTION_DOCS\01_BLUEPRINTS\REALTIME_QUALITY_MONITOR_BLUEPRINT.md"
    
    # 尝试多种编码
    encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'gb18030']
    content = None
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            print(f"成功使用 {encoding} 编码读取文件")
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    if content is None:
        print("无法读取文件，尝试使用二进制模式")
        with open(file_path, 'rb') as f:
            content = f.read().decode('utf-8', errors='ignore')
    
    # 替换职责范围
    old_text = "- **职责范围**: 实时数据质量监控、告警、可视化"
    new_text = "- **职责范围**: 实时数据质量监控和检测（告警功能由[ENHANCED_ALERT_SYSTEM_BLUEPRINT.md](./ENHANCED_ALERT_SYSTEM_BLUEPRINT.md)提供）"
    
    if old_text in content:
        content = content.replace(old_text, new_text)
        print("✅ 已修改职责范围")
    else:
        print("⚠️ 未找到职责范围文本")
    
    # 添加横向依赖
    old_dependencies = """- **上下层接口**:
  - 上层依赖: Layer 2-8（提供质量监控服务）
  - 下层依赖: Layer 0-1（监控数据源和预处理质量）"""
    
    new_dependencies = """- **上下层接口**:
  - 上层依赖: Layer 2-8（提供质量监控服务）
  - 下层依赖: Layer 0-1（监控数据源和预处理质量）
  - 横向依赖: ENHANCED_ALERT_SYSTEM_BLUEPRINT.md（提供告警服务）"""
    
    if old_dependencies in content:
        content = content.replace(old_dependencies, new_dependencies)
        print("✅ 已添加横向依赖")
    else:
        print("⚠️ 未找到依赖关系文本")
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已修改文件: {file_path}")

def fix_enhanced_alert_system():
    """修复ENHANCED_ALERT_SYSTEM_BLUEPRINT.md"""
    file_path = r"docs\05_IMPLEMENTATION\06_CONSTRUCTION_DOCS\01_BLUEPRINTS\ENHANCED_ALERT_SYSTEM_BLUEPRINT.md"
    
    # 尝试多种编码
    encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'gb18030']
    content = None
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            print(f"成功使用 {encoding} 编码读取文件")
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    if content is None:
        print("无法读取文件，尝试使用二进制模式")
        with open(file_path, 'rb') as f:
            content = f.read().decode('utf-8', errors='ignore')
    
    # 在文档开头添加说明
    if "全系统告警增强系统" not in content:
        # 找到"## 一、设计背景与目标"之前的位置
        insert_position = content.find("## 一、设计背景与目标")
        if insert_position > 0:
            clarification = """
> **职责说明**: 本蓝图是全系统告警增强系统，负责接收来自各个系统的告警（包括数据质量监控系统、风险控制系统、执行系统等），提供告警聚合、告警抑制、告警路由、多渠道分发等功能。

"""
            content = content[:insert_position] + clarification + content[insert_position:]
            print("✅ 已添加职责说明")
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已修改文件: {file_path}")

if __name__ == "__main__":
    print("开始修复告警功能职责重叠问题...")
    print("=" * 60)
    
    print("\n1. 修复 REALTIME_QUALITY_MONITOR_BLUEPRINT.md")
    print("-" * 60)
    fix_realtime_quality_monitor()
    
    print("\n2. 修复 ENHANCED_ALERT_SYSTEM_BLUEPRINT.md")
    print("-" * 60)
    fix_enhanced_alert_system()
    
    print("\n" + "=" * 60)
    print("✅ 修复完成！")
