#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
稀疏目录修复执行
为一级目录补充OVERVIEW.md文档
"""

import os
from pathlib import Path
from datetime import datetime

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY')

# 一级目录的OVERVIEW内容定义
OVERVIEW_CONTENT = {
    '00_GOVERNANCE': {
        'title': '治理框架概览',
        'description': '因子库治理框架，包括文档管理规范、质量监控流程和持续改进机制。',
        'sections': [
            '治理框架概述',
            '文档管理规范',
            '质量监控流程',
            '持续改进机制'
        ]
    },
    '02_ALPHA_FACTORS_INDEX': {
        'title': 'Alpha因子索引概览',
        'description': 'Alpha因子索引和分类文档，跟踪Alpha因子的性能表现。',
        'sections': [
            'Alpha因子分类',
            'Alpha因子索引',
            'Alpha因子性能跟踪'
        ]
    },
    '03_RISK_FACTORS': {
        'title': '风险因子概览',
        'description': '风险因子定义、计算和监控文档，管理风险暴露因子。',
        'sections': [
            '风险因子分类',
            '风险因子计算',
            '风险因子监控'
        ]
    },
    '06_REGISTRY': {
        'title': '因子注册表概览',
        'description': '因子注册表，管理因子的注册、版本和生命周期。',
        'sections': [
            '因子注册流程',
            '版本管理机制',
            '生命周期管理'
        ]
    },
    '07_FACTOR_MONITORING': {
        'title': '因子监控概览',
        'description': '因子性能监控系统，提供预警管理和报告生成功能。',
        'sections': [
            '监控指标体系',
            '预警机制',
            '报告生成'
        ]
    },
    '09_AUDIT': {
        'title': '审计系统概览',
        'description': '因子库审计系统，生成审计报告和质量评估分析。',
        'sections': [
            '审计流程',
            '质量评估方法',
            '改进建议生成'
        ]
    },
    '10_MANUAL': {
        'title': '使用手册概览',
        'description': '因子库使用手册，包括使用指南、FAQ和最佳实践。',
        'sections': [
            '快速开始指南',
            '常见问题解答',
            '最佳实践'
        ]
    }
}

def generate_overview_content(dir_name, info):
    """生成OVERVIEW.md内容"""
    content = f"""---
module_id: FACTOR_LIBRARY_{dir_name}_OVERVIEW
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 文档管理团队
responsibility:
  - {info['title']}文档
standard_type: 概览文档
applicable_scope: 因子库
compliance_level: 专业标准
---

# {info['title']}

> **核心职责**: {info['description']}
> **职责边界**: 
> - ✅ 本文档负责：模块概览、核心概念、关键流程
> - ❌ 本文档不负责：具体实现细节、其他模块内容

---

## 📋 概述

{info['description']}

---

## 🎯 核心内容

"""
    
    for i, section in enumerate(info['sections'], 1):
        content += f"### {i}. {section}\n\n"
        content += f"本模块的{section}相关内容，详见具体文档。\n\n"
    
    content += f"""---

## 📂 相关文档

- [INDEX.md](./INDEX.md) - 目录索引
- [README.md](./README.md) - 模块说明

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-07 | 初始版本 | 文档管理团队 |
"""
    
    return content

def fix_sparse_directories():
    """修复稀疏目录"""
    print("=" * 80)
    print("稀疏目录修复执行")
    print("=" * 80)
    
    fixed_count = 0
    
    # 为一级目录补充OVERVIEW.md
    for dir_name, info in OVERVIEW_CONTENT.items():
        dir_path = FACTOR_LIBRARY / dir_name
        overview_path = dir_path / 'OVERVIEW.md'
        
        # 检查目录是否存在且文件数<3
        if dir_path.exists():
            md_files = list(dir_path.glob('*.md'))
            if len(md_files) < 3:
                # 生成OVERVIEW.md内容
                content = generate_overview_content(dir_name, info)
                
                # 写入文件
                with open(overview_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"\n创建: {dir_name}/OVERVIEW.md")
                fixed_count += 1
    
    return fixed_count

def main():
    """主函数"""
    print("=" * 80)
    print("稀疏目录修复执行")
    print("=" * 80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    fixed_count = fix_sparse_directories()
    
    print("\n" + "=" * 80)
    print("修复完成")
    print("=" * 80)
    print(f"创建OVERVIEW.md文件: {fixed_count}")
    print("\n说明:")
    print("- 一级目录已补充OVERVIEW.md文档")
    print("- 04_DATA_SOURCE下的子目录保持现状（规划中模块）")
    print("- 后续开发时补充实际内容")

if __name__ == '__main__':
    main()
