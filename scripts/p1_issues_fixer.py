#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
P1级别问题修复脚本
修复旧架构命名残留、职责缺失、YAML字段缺失
"""

import re
from pathlib import Path
from datetime import datetime

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY')

def fix_sitemap():
    """修复SITEMAP.md中的旧架构命名"""
    sitemap_path = FACTOR_LIBRARY / 'SITEMAP.md'
    
    with open(sitemap_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    # 替换Layer 0-11为新架构描述
    content = re.sub(r'Layer 0-11', '系统架构层级', content)
    content = re.sub(r'Layer\s+[0-9]+', '架构层级', content)
    
    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("修复: SITEMAP.md - 移除旧架构命名残留")

def fix_faq():
    """修复FAQ.md中的旧架构命名"""
    faq_path = FACTOR_LIBRARY / '10_MANUAL' / 'FAQ.md'
    
    with open(faq_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    # 替换Layer 0-11为新架构描述
    content = re.sub(r'Layer 0-11', '系统架构层级', content)
    content = re.sub(r'Layer\s+[0-9]+', '架构层级', content)
    
    with open(faq_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("修复: 10_MANUAL/FAQ.md - 移除旧架构命名残留")

def fix_factor_registry():
    """修复FACTOR_REGISTRY.md的YAML字段和职责"""
    registry_path = FACTOR_LIBRARY / '01_STANDARDS' / 'FACTOR_REGISTRY.md'
    
    new_content = """---
module_id: FACTOR_LIBRARY_01_STANDARDS_FACTOR_REGISTRY
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 文档管理团队
responsibility:
  - 因子注册表维护
  - 因子元数据管理
  - 因子版本控制
  - 因子生命周期管理
standard_type: 标准文档
applicable_scope: 因子库标准层
compliance_level: 专业标准
parent_document: ./INDEX.md
---

# 因子注册表 (FACTOR_REGISTRY)

> **核心职责**: 维护因子注册表，管理因子元数据、版本和生命周期
> **职责边界**: 
> - ✅ 本文档负责：因子注册、元数据管理、版本控制、生命周期管理
> - ❌ 本文档不负责：具体因子实现、因子计算逻辑

---

## 📋 概述

本文档定义了清风量化系统的因子注册表，包括因子元数据标准、注册流程和生命周期管理。

## 🏗️ 因子注册表结构

### 因子元数据字段

每个因子必须包含以下元数据：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| factor_id | string | 是 | 因子唯一标识符 |
| factor_name | string | 是 | 因子名称 |
| factor_type | string | 是 | 因子类型（Alpha/Risk/Liquidity） |
| version | string | 是 | 因子版本号 |
| status | enum | 是 | 因子状态（Active/Deprecated/Testing） |
| created_date | date | 是 | 创建日期 |
| last_updated | date | 是 | 最后更新日期 |
| owner | string | 是 | 因子负责人 |
| description | string | 是 | 因子描述 |
| formula | string | 否 | 因子计算公式 |
| data_requirements | list | 是 | 数据需求列表 |
| performance_metrics | dict | 否 | 性能指标 |

---

## 📝 注册流程

### 1. 因子定义
- 定义因子计算公式
- 确定数据需求
- 编写因子文档

### 2. 因子验证
- 单元测试验证
- 回测验证
- 风险评估

### 3. 因子注册
- 分配factor_id
- 录入元数据
- 更新注册表

### 4. 因子发布
- 标记为Active状态
- 通知相关团队
- 更新文档索引

---

## 🔄 生命周期管理

### 因子状态

- **Testing**: 测试中，未正式发布
- **Active**: 活跃状态，正常使用
- **Deprecated**: 已废弃，不再维护
- **Archived**: 已归档，历史记录

### 状态转换规则

```
Testing -> Active (通过验证)
Active -> Deprecated (不再使用)
Deprecated -> Archived (归档处理)
```

---

## 📊 因子分类

### Alpha因子
- 动量因子
- 价值因子
- 成长因子
- 质量因子

### 风险因子
- 市场Beta
- 行业因子
- 规模因子
- 波动率因子

### 流动性因子
- 成交量因子
- 换手率因子
- 价差因子

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-07 | 初始版本，补充完整YAML元数据和职责描述 | 文档管理团队 |
"""
    
    with open(registry_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("修复: 01_STANDARDS/FACTOR_REGISTRY.md - 补充YAML字段和职责描述")

def main():
    """主函数"""
    print("=" * 80)
    print("P1级别问题修复")
    print("=" * 80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 修复旧架构命名残留
    print("\n修复旧架构命名残留...")
    fix_sitemap()
    fix_faq()
    
    # 修复YAML字段和职责
    print("\n修复YAML字段和职责...")
    fix_factor_registry()
    
    print("\n" + "=" * 80)
    print("修复完成")
    print("=" * 80)
    print("修复文件数: 3")

if __name__ == '__main__':
    main()
