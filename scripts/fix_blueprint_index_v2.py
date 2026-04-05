#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复蓝图INDEX.md的分类问题"""

file_path = r'd:\ZephyrAlpha\docs\05_IMPLEMENTATION\06_CONSTRUCTION_DOCS\01_BLUEPRINTS\INDEX.md'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 定义要添加的新内容
new_section_3_5 = '''### 3.5 风险模型与归因

| 文档名称 | module_id | 版本 | 状态 | 最后更新 | 文档路径 |
|----------|-----------|------|------|----------|----------|
| Barra风险模型蓝图 | BARRA_RISK_MODEL_001 | v1.0.0 | Active | 2026-04-03 | [链接](./BARRA_RISK_MODEL_BLUEPRINT.md) |
| 风险归因系统蓝图 | RISK_ATTRIBUTION_SYSTEM_001 | v1.0.0 | Active | 2026-04-03 | [链接](./RISK_ATTRIBUTION_SYSTEM_BLUEPRINT.md) |

---

## 4. 风险控制层蓝图（Layer 7）
### 4.1 风险对冲与压力测试

| 文档名称 | module_id | 版本 | 状态 | 最后更新 | 文档路径 |
|----------|-----------|------|------|----------|----------|
| 实时风险对冲引擎蓝图 | REALTIME_RISK_HEDGE_ENGINE_BLUEPRINT_001 | v1.0.0 | Active | 2026-04-03 | [链接](./REALTIME_RISK_HEDGE_ENGINE_BLUEPRINT.md) |
| 尾部风险对冲蓝图 | TAIL_RISK_HEDGING_001 | v1.0.0 | Active | 2026-04-03 | [链接](./TAIL_RISK_HEDGING_BLUEPRINT.md) |
| 压力测试系统蓝图 | STRESS_TESTING_SYSTEM_001 | v1.0.0 | Active | 2026-04-03 | [链接](./STRESS_TESTING_SYSTEM_BLUEPRINT.md) |'''

# 要替换的旧内容（从"## 4. 风险控制层蓝图"到压力测试系统蓝图那一行）
old_content = '''## 4. 风险控制层蓝图（Layer 7）
### 4.1 风险模型与归因
| 文档名称 | module_id | 版本 | 状态 | 最后更新 | 文档路径 |
|----------|-----------|------|------|----------|----------|
| Barra风险模型蓝图 | BARRA_RISK_MODEL_001 | v1.0.0 | Active | 2026-04-03 | [链接](./BARRA_RISK_MODEL_BLUEPRINT.md) |
| 风险归因系统蓝图 | RISK_ATTRIBUTION_SYSTEM_001 | v1.0.0 | Active | 2026-04-03 | [链接](./RISK_ATTRIBUTION_SYSTEM_BLUEPRINT.md) |

### 4.2 风险对冲与压力测试
| 文档名称 | module_id | 版本 | 状态 | 最后更新 | 文档路径 |
|----------|-----------|------|------|----------|----------|
| 实时风险对冲引擎蓝图 | REALTIME_RISK_HEDGE_ENGINE_BLUEPRINT_001 | v1.0.0 | Active | 2026-04-03 | [链接](./REALTIME_RISK_HEDGE_ENGINE_BLUEPRINT.md) |
| 尾部风险对冲蓝图 | TAIL_RISK_HEDGING_001 | v1.0.0 | Active | 2026-04-03 | [链接](./TAIL_RISK_HEDGING_BLUEPRINT.md) |
| 压力测试系统蓝图 | STRESS_TESTING_SYSTEM_001 | v1.0.0 | Active | 2026-04-03 | [链接](./STRESS_TESTING_SYSTEM_BLUEPRINT.md) |'''

# 在RL再平衡系统蓝图后面添加新分类
rl_line = '| RL再平衡系统蓝图 | RL_REBALANCING_SYSTEM_001 | v1.0.0 | Active | 2026-04-03 | [链接](./RL_REBALANCING_SYSTEM_BLUEPRINT.md) |'

if old_content in content:
    content = content.replace(old_content, new_section_3_5)
    print('Replaced old content with new section')
else:
    print('Old content not found, trying alternative approach')
    # 尝试在RL再平衡系统蓝图后添加新分类
    if rl_line in content:
        insert_text = '''

### 3.5 风险模型与归因

| 文档名称 | module_id | 版本 | 状态 | 最后更新 | 文档路径 |
|----------|-----------|------|------|----------|----------|
| Barra风险模型蓝图 | BARRA_RISK_MODEL_001 | v1.0.0 | Active | 2026-04-03 | [链接](./BARRA_RISK_MODEL_BLUEPRINT.md) |
| 风险归因系统蓝图 | RISK_ATTRIBUTION_SYSTEM_001 | v1.0.0 | Active | 2026-04-03 | [链接](./RISK_ATTRIBUTION_SYSTEM_BLUEPRINT.md) |'''
        content = content.replace(rl_line, rl_line + insert_text)
        print('Added new section after RL rebalancing')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')
