#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
补充职责描述脚本
"""

from pathlib import Path
from datetime import datetime

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs')
OUTPUT_DIR = Path(r'D:\ZephyrAlpha\docs\09_AUDIT\STATE')

# 定义需要补充职责描述的文档及其职责
RESPONSIBILITY_MAP = {
    '01_FRAMEWORK/ARCHITECTURE_DECISIONS/INDEX.md': {
        'responsibility': '架构决策索引',
        'description': '记录系统架构决策的索引文档'
    },
    '02_FACTOR_LIBRARY/00_GOVERNANCE/INDEX.md': {
        'responsibility': '因子库治理索引',
        'description': '记录因子库治理规范的索引文档'
    },
    '05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/PORTFOLIO_OPTIMIZATION_BLUEPRINT.md': {
        'responsibility': '投资组合优化蓝图',
        'description': '记录投资组合优化模块的设计蓝图'
    },
    '09_AUDIT/REPORTS/SHORT_TERM_IMPROVEMENT_COMPLETION_REPORT_20260407.md': {
        'responsibility': '短期改进完成报告',
        'description': '记录短期改进任务的完成情况'
    },
    '09_AUDIT/STANDARDS/DOCUMENT_VERSION_NAMING_STANDARD.md': {
        'responsibility': '文档版本号命名标准',
        'description': '定义文档版本号的命名规范'
    },
    '09_AUDIT/STATE/DEAD_LINK_FIX_PLAN_20260407.md': {
        'responsibility': '死链接修复计划',
        'description': '记录死链接修复的计划和进度'
    },
    '11_STRATEGIC_DECISION/COMPLETE_MISSING_MODULES_BLUEPRINTS_20260407.md': {
        'responsibility': '完整缺失模块蓝图',
        'description': '记录缺失模块的完整蓝图设计'
    },
    '11_STRATEGIC_DECISION/MISSING_MODULES_BLUEPRINT_SUMMARY_20260407.md': {
        'responsibility': '缺失模块蓝图摘要',
        'description': '记录缺失模块蓝图的摘要信息'
    },
    '11_STRATEGIC_DECISION/STRATEGIC_DECISION_ARCHITECTURE_COMPLETION_PLAN_20260407.md': {
        'responsibility': '战略决策架构完成计划',
        'description': '记录战略决策架构的完成计划'
    },
    '11_STRATEGIC_DECISION/STRATEGIC_DECISION_DEEP_REVIEW_20260407.md': {
        'responsibility': '战略决策深度审查',
        'description': '记录战略决策的深度审查结果'
    },
    '11_STRATEGIC_DECISION/SUPPLEMENTARY_MODULES_BLUEPRINTS_20260407.md': {
        'responsibility': '补充模块蓝图',
        'description': '记录补充模块的蓝图设计'
    }
}

def add_responsibility():
    """补充职责描述"""
    print("=" * 80)
    print("补充职责描述")
    print("=" * 80)
    
    updated_count = 0
    failed_count = 0
    
    for file_rel_path, responsibility_info in RESPONSIBILITY_MAP.items():
        file_path = FACTOR_LIBRARY / file_rel_path
        
        if not file_path.exists():
            print(f"文件不存在: {file_rel_path}")
            failed_count += 1
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            # 检查是否已有YAML元数据
            if content.startswith('---'):
                # 已有YAML元数据，添加responsibility字段
                yaml_end = content.find('---', 3)
                if yaml_end > 0:
                    yaml_content = content[3:yaml_end]
                    
                    # 检查是否已有responsibility字段
                    if 'responsibility:' not in yaml_content:
                        # 添加responsibility字段
                        new_yaml = yaml_content.rstrip() + f"\nresponsibility:\n  - {responsibility_info['responsibility']}\n"
                        new_content = '---' + new_yaml + '---' + content[yaml_end + 3:]
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        print(f"  更新: {file_rel_path}")
                        updated_count += 1
                    else:
                        print(f"  跳过（已有职责）: {file_rel_path}")
            else:
                # 没有YAML元数据，创建完整的YAML元数据
                yaml_header = f"""---
module_id: {file_path.stem.upper()}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
responsibility:
  - {responsibility_info['responsibility']}
standard_type: 标准文档
applicable_scope: {responsibility_info['description']}
compliance_level: 专业标准
parent_document: ../INDEX.md
---

"""
                new_content = yaml_header + content
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"  创建: {file_rel_path}")
                updated_count += 1
        
        except Exception as e:
            print(f"  失败: {file_rel_path} - {e}")
            failed_count += 1
    
    print(f"\n补充完成")
    print(f"更新文档: {updated_count}")
    print(f"失败文档: {failed_count}")
    
    return updated_count, failed_count

def generate_report(updated_count, failed_count):
    """生成报告"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = OUTPUT_DIR / f'RESPONSIBILITY_SUPPLEMENT_REPORT_{timestamp}.md'
    
    report_content = f"""---
module_id: RESPONSIBILITY_SUPPLEMENT_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: 补充报告
applicable_scope: 职责描述补充
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# 职责描述补充报告

> **核心职责**: 记录职责描述补充的过程和结果
> **职责边界**: 
> - [OK] 本文档负责：补充记录、效果评估、后续建议
> - [NO] 本文档不负责：后续审计执行、新问题发现

---

## 补充概要

**补充时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**补充范围**: 11个非归档文档  
**补充方法**: 自动补充  
**补充结论**: 成功补充职责描述

---

## 补充统计

| 统计项 | 数量 | 说明 |
|--------|------|------|
| **更新文档** | {updated_count} | 成功补充职责描述的文档 |
| **失败文档** | {failed_count} | 补充失败的文档 |

---

## 补充详情

### 已补充职责描述的文档 ({updated_count}个)

"""
    
    for file_rel_path, responsibility_info in RESPONSIBILITY_MAP.items():
        report_content += f"""
**{file_rel_path}**
- 职责: {responsibility_info['responsibility']}
- 描述: {responsibility_info['description']}

"""
    
    report_content += f"""
---

## 后续建议

### 立即行动

1. [x] 补充职责描述
2. [ ] 验证补充效果
3. [ ] 更新相关文档

### 持续改进

1. [ ] 建立职责描述检查机制
2. [ ] 定期执行职责描述扫描
3. [ ] 持续优化文档质量

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本，职责描述补充报告 | 首席文档架构师 |
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n报告已生成: {report_path}")
    return report_path

if __name__ == '__main__':
    # 补充职责描述
    updated_count, failed_count = add_responsibility()
    
    # 生成报告
    report_path = generate_report(updated_count, failed_count)
    
    print("\n" + "=" * 80)
    print("职责描述补充完成")
    print("=" * 80)
    print(f"更新文档: {updated_count}")
    print(f"失败文档: {failed_count}")
    print(f"报告位置: {report_path}")
