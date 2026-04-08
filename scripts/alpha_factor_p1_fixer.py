#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Alpha因子层P1级别问题修复
优化INDEX文件内容，为每个目录创建差异化的INDEX
"""

import re
from pathlib import Path
from datetime import datetime

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY')

# 定义每个目录的具体职责和描述
DIRECTORY_INFO = {
    '00_GOVERNANCE': {
        'title': '治理文档',
        'description': '因子库治理框架、规范和流程文档',
        'responsibilities': ['因子库治理框架制定', '文档管理规范', '质量监控流程'],
        'modules': ['README.md - 治理框架概述']
    },
    '01_STANDARDS': {
        'title': '标准文档',
        'description': '因子定义、分类、注册等标准规范',
        'responsibilities': ['因子定义标准', '因子分类体系', '因子注册规范'],
        'modules': ['FACTOR_REGISTRY.md - 因子注册表', 'FACTOR_TAXONOMY.md - 因子分类体系']
    },
    '02_ALPHA_FACTORS_INDEX': {
        'title': 'Alpha因子索引',
        'description': 'Alpha因子的索引和分类文档',
        'responsibilities': ['Alpha因子索引维护', 'Alpha因子分类管理', 'Alpha因子性能跟踪'],
        'modules': ['README.md - Alpha因子概述']
    },
    '03_RISK_FACTORS': {
        'title': '风险因子',
        'description': '风险因子定义、计算和监控文档',
        'responsibilities': ['风险因子定义', '风险因子计算', '风险因子监控'],
        'modules': ['README.md - 风险因子概述', 'INDEX.md - 风险因子索引']
    },
    '05_BACKTEST': {
        'title': '回测系统',
        'description': '因子回测框架、流程和结果分析',
        'responsibilities': ['回测框架设计', '回测流程管理', '回测结果分析'],
        'modules': ['BACKTEST_REORGANIZATION.md - 回测重组方案', 'README.md - 回测系统概述']
    },
    '06_REGISTRY': {
        'title': '因子注册表',
        'description': '因子注册、版本管理和生命周期管理',
        'responsibilities': ['因子注册管理', '因子版本控制', '因子生命周期管理'],
        'modules': ['README.md - 因子注册表概述']
    },
    '07_FACTOR_MONITORING': {
        'title': '因子监控',
        'description': '因子性能监控、预警和报告',
        'responsibilities': ['因子性能监控', '因子预警管理', '因子报告生成'],
        'modules': ['README.md - 因子监控概述']
    },
    '09_AUDIT': {
        'title': '审计文档',
        'description': '因子库审计报告、质量评估和改进建议',
        'responsibilities': ['审计报告生成', '质量评估分析', '改进建议制定'],
        'modules': ['README.md - 审计系统概述']
    },
    '10_MANUAL': {
        'title': '使用手册',
        'description': '因子库使用指南、FAQ和最佳实践',
        'responsibilities': ['使用指南编写', 'FAQ维护', '最佳实践总结'],
        'modules': ['FAQ.md - 常见问题解答', 'README.md - 使用手册概述']
    }
}

def generate_index_content(dir_name, dir_info):
    """生成差异化的INDEX内容"""
    
    content = f"""---
module_id: FACTOR_LIBRARY_{dir_name}_INDEX
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 文档管理团队
responsibility:
"""
    
    for resp in dir_info['responsibilities']:
        content += f"  - {resp}\n"
    
    content += f"""standard_type: 索引文档
applicable_scope: 因子库
compliance_level: 专业标准
---

# {dir_name} {dir_info['title']}

> **核心职责**: {dir_info['description']}
> **职责边界**: 
> - ✅ 本文档负责：目录导航、模块索引、职责协调
> - ❌ 本文档不负责：具体实现细节、其他模块内容

---

## 📋 概述

{dir_info['description']}

## 📂 目录结构

"""
    
    for module in dir_info['modules']:
        content += f"- {module}\n"
    
    content += f"""
---

## 🎯 核心职责

"""
    
    for i, resp in enumerate(dir_info['responsibilities'], 1):
        content += f"{i}. **{resp}**\n"
    
    content += f"""
---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-07 | 初始版本，创建差异化索引内容 | 文档管理团队 |
"""
    
    return content

def optimize_index_files():
    """优化INDEX文件"""
    print("=" * 80)
    print("优化INDEX文件内容")
    print("=" * 80)
    
    updated_count = 0
    
    for dir_name, dir_info in DIRECTORY_INFO.items():
        dir_path = FACTOR_LIBRARY / dir_name
        index_path = dir_path / 'INDEX.md'
        
        if index_path.exists():
            # 生成新的INDEX内容
            new_content = generate_index_content(dir_name, dir_info)
            
            # 写入文件
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"\n更新: {dir_name}/INDEX.md")
            updated_count += 1
    
    print(f"\n更新INDEX文件: {updated_count}")
    return updated_count

def main():
    """主函数"""
    print("=" * 80)
    print("Alpha因子层P1级别问题修复 - 优化INDEX文件")
    print("=" * 80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    updated_count = optimize_index_files()
    
    print("\n" + "=" * 80)
    print("修复完成")
    print("=" * 80)
    print(f"更新INDEX文件: {updated_count}")

if __name__ == '__main__':
    main()
