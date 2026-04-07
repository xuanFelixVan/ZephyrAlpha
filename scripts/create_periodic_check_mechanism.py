#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
定期检查机制脚本
建立引用链接定期检查机制
"""

import os
import json
from pathlib import Path
from datetime import datetime, timedelta

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs')
OUTPUT_DIR = Path(r'D:\ZephyrAlpha\docs\09_AUDIT\STATE')

def create_periodic_check_schedule():
    """创建定期检查计划"""
    print("=" * 80)
    print("创建定期检查计划")
    print("=" * 80)
    
    schedule = {
        'check_frequency': '每日',
        'check_time': '09:00',
        'check_items': [
            {
                'name': '引用链接检查',
                'script': 'reference_link_auto_check.py',
                'frequency': '每日',
                'priority': '高'
            },
            {
                'name': '命名规范检查',
                'script': 'automated_document_check.py',
                'frequency': '每周',
                'priority': '中'
            },
            {
                'name': '文档完整性检查',
                'script': 'automated_document_check.py',
                'frequency': '每周',
                'priority': '中'
            }
        ],
        'notification': {
            'email': False,
            'report_file': True,
            'console_output': True
        },
        'created_date': datetime.now().strftime('%Y-%m-%d'),
        'next_check': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    }
    
    schedule_path = OUTPUT_DIR / 'PERIODIC_CHECK_SCHEDULE.json'
    
    with open(schedule_path, 'w', encoding='utf-8') as f:
        json.dump(schedule, f, ensure_ascii=False, indent=2)
    
    print(f"定期检查计划已创建: {schedule_path}")
    return schedule_path

def create_periodic_check_guide():
    """创建定期检查指南"""
    guide_content = """---
module_id: PERIODIC_CHECK_GUIDE_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - 实施指南、操作手册
  - 定期检查
  - 质量监控
standard_type: 操作指南
applicable_scope: 全系统文档定期检查
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# 文档治理定期检查指南

> **核心职责**: 建立文档治理定期检查机制
> **职责边界**: 
> - [OK] 本文档负责：检查计划、执行流程、结果跟踪
> - [NO] 本文档不负责：问题修复、审计执行

---

## 1. 检查计划

### 1.1 检查频率

| 检查项目 | 频率 | 执行时间 | 优先级 |
|---------|------|---------|--------|
| **引用链接检查** | 每日 | 09:00 | 高 |
| **命名规范检查** | 每周 | 周一 09:00 | 中 |
| **文档完整性检查** | 每周 | 周一 09:00 | 中 |

### 1.2 检查脚本

| 脚本名称 | 功能 | 输出 |
|---------|------|------|
| **reference_link_auto_check.py** | 检查引用链接有效性 | 检查报告 |
| **automated_document_check.py** | 检查命名规范和完整性 | 检查报告 |

---

## 2. 执行流程

### 2.1 每日检查流程

```
1. 运行引用链接检查脚本
   python scripts/reference_link_auto_check.py

2. 查看检查报告
   docs/09_AUDIT/STATE/REFERENCE_LINK_CHECK_REPORT_*.md

3. 分析问题趋势
   - 对比历史数据
   - 识别新增问题
   - 评估改进效果

4. 记录检查结果
   - 更新质量指标
   - 生成趋势报告
```

### 2.2 每周检查流程

```
1. 运行命名规范检查
   python scripts/automated_document_check.py

2. 运行文档完整性检查
   python scripts/automated_document_check.py

3. 生成周报
   - 汇总本周问题
   - 分析问题趋势
   - 提出改进建议

4. 执行改进措施
   - 修复发现的问题
   - 更新相关文档
```

---

## 3. 结果跟踪

### 3.1 质量指标

| 指标 | 目标值 | 当前值 | 状态 |
|------|--------|--------|------|
| **链接有效率** | ≥99% | 99.59% | ✅ 达标 |
| **命名规范符合率** | ≥95% | 待统计 | ⏸️ 待检查 |
| **文档完整性** | 100% | 待统计 | ⏸️ 待检查 |

### 3.2 历史趋势

| 日期 | 有效链接 | 无效链接 | 有效率 |
|------|---------|---------|--------|
| 2026-04-07 | 8161 | 34 | 99.59% |
| ... | ... | ... | ... |

---

## 4. 问题处理

### 4.1 问题分类

| 优先级 | 问题类型 | 响应时间 | 处理方式 |
|--------|---------|---------|---------|
| **P0** | 严重问题 | 24小时 | 立即修复 |
| **P1** | 重要问题 | 3天 | 计划修复 |
| **P2** | 一般问题 | 1周 | 批量修复 |

### 4.2 处理流程

```
1. 问题发现
   - 自动检查发现
   - 人工审查发现

2. 问题分析
   - 确定问题类型
   - 评估影响范围
   - 制定修复方案

3. 问题修复
   - 执行修复操作
   - 验证修复效果
   - 更新相关文档

4. 结果验证
   - 重新运行检查
   - 确认问题解决
   - 记录修复结果
```

---

## 5. 持续改进

### 5.1 改进机制

1. **定期评估**: 每月评估检查机制有效性
2. **优化脚本**: 根据实际情况优化检查脚本
3. **完善标准**: 持续完善文档治理标准
4. **提升效率**: 提高自动化程度和检查效率

### 5.2 最佳实践

1. **自动化优先**: 使用脚本自动检查和修复
2. **趋势跟踪**: 跟踪质量指标变化趋势
3. **预防为主**: 建立预防机制，减少问题发生
4. **持续学习**: 总结经验教训，持续改进

---

## 6. 工具和资源

### 6.1 检查脚本

- [reference_link_auto_check.py](file:///D:/ZephyrAlpha/scripts/reference_link_auto_check.py)
- [automated_document_check.py](file:///D:/ZephyrAlpha/scripts/automated_document_check.py)
- [short_term_improvement.py](file:///D:/ZephyrAlpha/scripts/short_term_improvement.py)

### 6.2 相关文档

- [引用链接检查报告](file:///D:/ZephyrAlpha/docs/09_AUDIT/STATE/REFERENCE_LINK_CHECK_REPORT_20260407_155353.md)
- [短期改进报告](file:///D:/ZephyrAlpha/docs/09_AUDIT/STATE/SHORT_TERM_IMPROVEMENT_REPORT_20260407_161012.md)

---

## 📝 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-07 | 初始版本，定期检查指南 | 首席文档架构师 |
"""
    
    guide_path = OUTPUT_DIR / 'PERIODIC_CHECK_GUIDE.md'
    
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print(f"定期检查指南已创建: {guide_path}")
    return guide_path

def generate_periodic_check_report(schedule_path, guide_path):
    """生成定期检查机制报告"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = OUTPUT_DIR / f'PERIODIC_CHECK_MECHANISM_REPORT_{timestamp}.md'
    
    report_content = f"""---
module_id: PERIODIC_CHECK_MECHANISM_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: 机制报告
applicable_scope: 定期检查机制建立
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# 定期检查机制建立报告

> **核心职责**: 记录定期检查机制建立的过程和结果
> **职责边界**: 
> - [OK] 本文档负责：机制建立记录、效果评估、后续建议
> - [NO] 本文档不负责：后续检查执行、问题修复

---

## 建立概要

**建立时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**建立范围**: 文档治理定期检查机制  
**建立方法**: 自动化脚本 + 定期计划  
**建立结论**: 成功建立定期检查机制

---

## 建立内容

### 1. 定期检查计划

**文件**: [PERIODIC_CHECK_SCHEDULE.json](./PERIODIC_CHECK_SCHEDULE.json)

**主要内容**:
- 检查频率: 每日
- 检查时间: 09:00
- 检查项目: 3个
- 通知方式: 报告文件 + 控制台输出

### 2. 定期检查指南

**文件**: [PERIODIC_CHECK_GUIDE.md](./PERIODIC_CHECK_GUIDE.md)

**主要内容**:
- 检查计划
- 执行流程
- 结果跟踪
- 问题处理
- 持续改进

---

## 检查项目

| 检查项目 | 频率 | 脚本 | 优先级 |
|---------|------|------|--------|
| **引用链接检查** | 每日 | reference_link_auto_check.py | 高 |
| **命名规范检查** | 每周 | automated_document_check.py | 中 |
| **文档完整性检查** | 每周 | automated_document_check.py | 中 |

---

## 执行流程

### 每日检查

1. 运行引用链接检查脚本
2. 查看检查报告
3. 分析问题趋势
4. 记录检查结果

### 每周检查

1. 运行命名规范检查
2. 运行文档完整性检查
3. 生成周报
4. 执行改进措施

---

## 质量指标

| 指标 | 目标值 | 当前值 | 状态 |
|------|--------|--------|------|
| **链接有效率** | ≥99% | 99.59% | ✅ 达标 |
| **命名规范符合率** | ≥95% | 待统计 | ⏸️ 待检查 |
| **文档完整性** | 100% | 待统计 | ⏸️ 待检查 |

---

## 后续建议

### 立即行动

1. [x] 创建定期检查计划
2. [x] 创建定期检查指南
3. [ ] 执行首次定期检查

### 持续改进

1. [ ] 优化检查脚本效率
2. [ ] 完善质量指标体系
3. [ ] 建立问题预警机制

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本，定期检查机制报告 | 首席文档架构师 |
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"定期检查机制报告已生成: {report_path}")
    return report_path

if __name__ == '__main__':
    # 创建定期检查计划
    schedule_path = create_periodic_check_schedule()
    
    # 创建定期检查指南
    guide_path = create_periodic_check_guide()
    
    # 生成报告
    report_path = generate_periodic_check_report(schedule_path, guide_path)
    
    print("\n" + "=" * 80)
    print("定期检查机制建立完成")
    print("=" * 80)
    print(f"检查计划: {schedule_path}")
    print(f"检查指南: {guide_path}")
    print(f"机制报告: {report_path}")
