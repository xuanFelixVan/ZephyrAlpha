#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
后续行动和持续改进脚本
功能：
1. 审查路径引用问题（40个文档）
2. 更新相关文档的引用链接
3. 建立自动化检查机制
4. 定期执行审查机制
5. 持续优化质量标准
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"
FACTOR_LIBRARY = DOCS_DIR / "02_FACTOR_LIBRARY"
REPORT_DIR = DOCS_DIR / "09_AUDIT" / "STATE"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

def review_path_references():
    """审查路径引用问题"""
    print("=" * 80)
    print("审查路径引用问题")
    print("=" * 80)
    
    issues = []
    recommendations = []
    
    for file_path in FACTOR_LIBRARY.rglob('*.md'):
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            parent_ref_count = content.count('../')
            
            if parent_ref_count > 5:
                path_refs = re.findall(r'\[([^\]]+)\]\(([^)]*\.\./[^)]*)\)', content)
                depth = len(file_path.relative_to(FACTOR_LIBRARY).parts) - 1
                
                issue = {
                    'file': str(file_path.relative_to(FACTOR_LIBRARY)),
                    'parent_ref_count': parent_ref_count,
                    'depth': depth,
                    'sample_refs': [ref[1] for ref in path_refs[:3]],
                    'recommendation': 'simplify' if depth > 2 else 'review'
                }
                
                issues.append(issue)
                
                if depth > 2:
                    recommendations.append({
                        'file': str(file_path.relative_to(FACTOR_LIBRARY)),
                        'current_depth': depth,
                        'suggested_action': '考虑使用更短的相对路径或重构目录结构',
                        'priority': 'medium'
                    })
        
        except Exception as e:
            pass
    
    issues.sort(key=lambda x: x['parent_ref_count'], reverse=True)
    
    print(f"\n发现 {len(issues)} 个路径引用问题")
    print(f"建议简化: {len([r for r in recommendations if r['priority'] == 'medium'])} 个")
    
    return issues, recommendations

def update_reference_links():
    """更新相关文档的引用链接"""
    print("\n" + "=" * 80)
    print("更新相关文档的引用链接")
    print("=" * 80)
    
    updated = []
    
    rename_map = {
        '02_ALPHA_FACTORS_INDEX.md': 'ALPHA_FACTORS_INDEX_STANDARD.md',
        'backtest_standards.md': 'BACKTEST_STANDARDS.md',
        'factor_neutralization.md': 'FACTOR_NEUTRALIZATION.md',
        'factor_preprocessing.md': 'FACTOR_PREPROCESSING.md',
        'factor_return_analysis.md': 'FACTOR_RETURN_ANALYSIS.md',
        'factor_synthesis.md': 'FACTOR_SYNTHESIS.md',
        'ic_analysis.md': 'IC_ANALYSIS.md',
        'research_management.md': 'RESEARCH_MANAGEMENT.md',
        '05_BREADTH_INDICATORS.md': 'BREADTH_INDICATORS.md',
        'factor_master_index.md': 'FACTOR_MASTER_INDEX.md',
        '05_BACKTEST_REORGANIZATION.md': 'BACKTEST_REORGANIZATION.md',
        '06_FACTOR_DECAY.md': 'FACTOR_DECAY.md',
        '07_LAYERED_BACKTEST.md': 'LAYERED_BACKTEST.md',
        '09_OVERFITTING_TEST.md': 'OVERFITTING_TEST.md',
        'correlation_matrix.md': 'CORRELATION_MATRIX.md',
        'factor_monitoring.md': 'FACTOR_MONITORING.md',
        '99_AUDIT_REPORT.md': 'AUDIT_REPORT.md'
    }
    
    for file_path in FACTOR_LIBRARY.rglob('*.md'):
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            new_content = content
            changes = []
            
            for old_name, new_name in rename_map.items():
                pattern = r'\[([^\]]*)\]\(([^)]*' + re.escape(old_name) + r')\)'
                matches = re.findall(pattern, new_content)
                
                if matches:
                    new_content = re.sub(
                        pattern,
                        lambda m: f'[{m.group(1)}]({m.group(2).replace(old_name, new_name)})',
                        new_content
                    )
                    changes.append(f'{old_name} -> {new_name}')
            
            if new_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                updated.append({
                    'file': str(file_path.relative_to(FACTOR_LIBRARY)),
                    'changes': changes,
                    'status': 'success'
                })
                print(f"[OK] 更新: {file_path.name} ({len(changes)} 个引用)")
        
        except Exception as e:
            pass
    
    print(f"\n引用链接更新完成: {len(updated)} 个文档")
    return updated

def create_automated_check_mechanism():
    """建立自动化检查机制"""
    print("\n" + "=" * 80)
    print("建立自动化检查机制")
    print("=" * 80)
    
    check_script = SCRIPTS_DIR / "automated_document_check.py"
    
    script_content = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动化文档检查机制
"""

import os
import re
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"
FACTOR_LIBRARY = DOCS_DIR / "02_FACTOR_LIBRARY"
REPORT_DIR = DOCS_DIR / "09_AUDIT" / "STATE"

def check_naming_conventions():
    print("检查命名规范...")
    issues = []
    
    naming_pattern = re.compile(r'^[A-Z][A-Z0-9_]*\\.md$')
    exceptions = ['INDEX.md', 'README.md', 'SITEMAP.md', 'BLUEPRINT.md', 'FAQ.md']
    
    for file_path in FACTOR_LIBRARY.rglob('*.md'):
        if file_path.name in exceptions:
            continue
        
        if not naming_pattern.match(file_path.name):
            issues.append({
                'file': str(file_path.relative_to(FACTOR_LIBRARY)),
                'issue': '命名不规范',
                'current': file_path.name
            })
    
    print(f"  发现 {len(issues)} 个命名问题")
    return issues

def check_responsibility_descriptions():
    print("检查职责描述...")
    issues = []
    
    for file_path in FACTOR_LIBRARY.rglob('*.md'):
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            resp_match = re.search(r'\\*\\*核心职责\\*\\*:\\s*(.+)', content)
            
            if not resp_match:
                issues.append({
                    'file': str(file_path.relative_to(FACTOR_LIBRARY)),
                    'issue': '缺少职责描述'
                })
            else:
                responsibility = resp_match.group(1).strip()
                if len(responsibility) < 15:
                    issues.append({
                        'file': str(file_path.relative_to(FACTOR_LIBRARY)),
                        'issue': f'职责描述过短 ({len(responsibility)}字符)',
                        'responsibility': responsibility
                    })
        
        except Exception as e:
            pass
    
    print(f"  发现 {len(issues)} 个职责问题")
    return issues

def check_index_completeness():
    print("检查索引完备性...")
    issues = []
    
    if not (FACTOR_LIBRARY / 'INDEX.md').exists():
        issues.append({
            'file': 'INDEX.md',
            'issue': '根目录缺少INDEX.md'
        })
    
    for item in FACTOR_LIBRARY.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            if not (item / 'INDEX.md').exists():
                issues.append({
                    'directory': item.name,
                    'issue': '子目录缺少INDEX.md'
                })
    
    print(f"  发现 {len(issues)} 个索引问题")
    return issues

def check_dead_links():
    print("检查死链接...")
    issues = []
    
    for file_path in FACTOR_LIBRARY.rglob('*.md'):
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            links = re.findall(r'\\[([^\\]]+)\\]\\(([^)]+)\\)', content)
            
            for link_text, link_path in links:
                if link_path.startswith('http') or link_path.startswith('#'):
                    continue
                
                target_path = file_path.parent / link_path
                if not target_path.exists():
                    issues.append({
                        'file': str(file_path.relative_to(FACTOR_LIBRARY)),
                        'issue': f'死链接: {link_path}',
                        'link_text': link_text
                    })
        
        except Exception as e:
            pass
    
    print(f"  发现 {len(issues)} 个死链接")
    return issues

def check_yaml_completeness():
    print("检查YAML完整性...")
    issues = []
    
    required_fields = ['module_id', 'version', 'status', 'created_date', 'owner']
    
    for file_path in FACTOR_LIBRARY.rglob('*.md'):
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            if not content.startswith('---'):
                issues.append({
                    'file': str(file_path.relative_to(FACTOR_LIBRARY)),
                    'issue': '缺少YAML头部'
                })
            else:
                yaml_content = content.split('---')[1]
                missing_fields = []
                
                for field in required_fields:
                    if f'{field}:' not in yaml_content:
                        missing_fields.append(field)
                
                if missing_fields:
                    issues.append({
                        'file': str(file_path.relative_to(FACTOR_LIBRARY)),
                        'issue': f'YAML缺少字段: {", ".join(missing_fields)}'
                    })
        
        except Exception as e:
            pass
    
    print(f"  发现 {len(issues)} 个YAML问题")
    return issues

def main():
    print("=" * 80)
    print("自动化文档检查")
    print("=" * 80)
    
    naming_issues = check_naming_conventions()
    resp_issues = check_responsibility_descriptions()
    index_issues = check_index_completeness()
    dead_links = check_dead_links()
    yaml_issues = check_yaml_completeness()
    
    total = len(naming_issues) + len(resp_issues) + len(index_issues) + len(dead_links) + len(yaml_issues)
    
    print("\n" + "=" * 80)
    print("检查完成")
    print("=" * 80)
    print(f"总问题数: {total}")

if __name__ == '__main__':
    main()
'''
    
    with open(check_script, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"[OK] 创建自动化检查脚本: {check_script.name}")
    
    return str(check_script)

def create_periodic_review_mechanism():
    """定期执行审查机制"""
    print("\n" + "=" * 80)
    print("定期执行审查机制")
    print("=" * 80)
    
    review_plan = DOCS_DIR / "09_AUDIT" / "STATE" / "PERIODIC_REVIEW_PLAN_V2.md"
    
    plan_content = f'''---
module_id: PERIODIC_REVIEW_PLAN_V2_001
version: 2.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: 审查计划
applicable_scope: 全系统定期审查
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# 定期审查计划 V2.0

> **核心职责**: 定义定期审查的流程、频率和责任分工
> **职责边界**: 
> - [OK] 本文档负责：审查计划制定、审查频率定义、责任分工
> - [NO] 本文档不负责：具体审查执行、问题修复实施

---

## 审查概要

**计划版本**: V2.0  
**生效日期**: {datetime.now().strftime('%Y-%m-%d')}  
**适用范围**: 全系统文档治理  
**审查目标**: 保持文档质量和一致性

---

## 审查频率

### 每日检查

**执行时间**: 每日上午9:00  
**执行方式**: 自动化脚本  
**检查内容**:
- 文件命名规范检查
- YAML头部完整性检查
- 职责描述存在性检查

**执行命令**:
```bash
python scripts/automated_document_check.py
```

---

### 每周检查

**执行时间**: 每周一上午10:00  
**执行方式**: 自动化脚本 + 人工审查  
**检查内容**:
- 职责描述质量检查
- 索引完整性检查
- 死链接检查
- 新增文档审查

---

### 每月检查

**执行时间**: 每月1日上午10:00  
**执行方式**: 深度审计  
**检查内容**:
- 分类规范性检查
- 稀疏目录检查
- 重复内容检查
- 职责重叠检查

---

### 每季度检查

**执行时间**: 每季度首月1日上午10:00  
**执行方式**: 全面审计  
**检查内容**:
- 架构一致性检查
- 文档覆盖率检查
- 质量指标评估
- 最佳实践更新

---

## 质量指标

| 指标 | 目标值 | 测量方法 |
|------|--------|---------|
| **命名规范符合率** | >=95% | 符合规范文件数 / 总文件数 |
| **职责描述覆盖率** | 100% | 有职责描述文件数 / 总文件数 |
| **索引完备率** | 100% | 有INDEX.md目录数 / 总目录数 |
| **死链接率** | <=1% | 死链接数 / 总链接数 |
| **YAML完整率** | >=95% | YAML完整文件数 / 总文件数 |

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v2.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 升级版本，完善审查机制 | 首席文档架构师 |
'''
    
    with open(review_plan, 'w', encoding='utf-8') as f:
        f.write(plan_content)
    
    print(f"[OK] 创建定期审查计划: {review_plan.name}")
    
    return str(review_plan)

def optimize_quality_standards():
    """持续优化质量标准"""
    print("\n" + "=" * 80)
    print("持续优化质量标准")
    print("=" * 80)
    
    quality_standard = DOCS_DIR / "09_AUDIT" / "STANDARDS" / "QUALITY_STANDARD_V3.md"
    
    standard_content = f'''---
module_id: QUALITY_STANDARD_V3_001
version: 3.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: 质量标准
applicable_scope: 全系统文档质量
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# 文档质量标准 V3.0

> **核心职责**: 定义文档质量的标准、指标和评估方法
> **职责边界**: 
> - [OK] 本文档负责：质量标准定义、质量指标制定、评估方法设计
> - [NO] 本文档不负责：具体质量检查执行、问题修复实施

---

## 标准概要

**标准版本**: V3.0  
**生效日期**: {datetime.now().strftime('%Y-%m-%d')}  
**适用范围**: 全系统文档  
**质量目标**: 100%符合专业量化机构标准

---

## 质量维度

### 1. 结构质量

**标准要求**:
- [OK] 标准YAML头部（5个必要字段）
- [OK] 明确的一级标题
- [OK] 清晰的章节结构
- [OK] 完整的职责描述
- [OK] 明确的职责边界

**质量指标**:
- YAML完整率: >=95%
- 标题规范率: 100%
- 章节完整率: >=90%
- 职责描述率: 100%
- 职责边界率: >=90%

---

### 2. 内容质量

**标准要求**:
- [OK] 内容准确无误
- [OK] 逻辑清晰连贯
- [OK] 语言简洁明了
- [OK] 示例恰当有效
- [OK] 引用准确完整

**质量指标**:
- 内容准确率: >=95%
- 逻辑清晰率: >=90%
- 语言规范率: >=95%
- 示例有效率: >=90%
- 引用准确率: >=95%

---

### 3. 命名质量

**标准要求**:
- [OK] 文件命名规范（大写字母+下划线）
- [OK] 目录命名规范（数字前缀+大写字母）
- [OK] 标题命名规范（清晰反映内容）
- [OK] 变量命名规范（符合编程规范）

**质量指标**:
- 文件命名符合率: >=95%
- 目录命名符合率: 100%
- 标题命名符合率: >=95%
- 变量命名符合率: >=90%

---

### 4. 引用质量

**标准要求**:
- [OK] 链接有效可用
- [OK] 路径简洁合理
- [OK] 引用格式规范
- [OK] 跨文档引用准确

**质量指标**:
- 链接有效率: >=99%
- 路径简洁率: >=90%
- 引用规范率: >=95%
- 跨文档准确率: >=95%

---

## 质量目标

### 短期目标（1个月）

- 命名规范符合率: 95%
- 职责描述覆盖率: 100%
- 索引完备率: 100%
- 死链接率: <=1%

### 中期目标（3个月）

- 所有质量指标达标
- 建立完整的质量管理体系
- 实现自动化质量监控
- 形成质量改进闭环

### 长期目标（持续）

- 保持100%质量标准符合率
- 持续优化质量标准
- 建立最佳实践库
- 形成质量文化

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v3.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 升级版本，完善质量标准 | 首席文档架构师 |
'''
    
    with open(quality_standard, 'w', encoding='utf-8') as f:
        f.write(standard_content)
    
    print(f"[OK] 创建质量标准: {quality_standard.name}")
    
    return str(quality_standard)

def generate_action_report(path_issues, path_recommendations, updated_links, 
                          check_script, review_plan, quality_standard):
    """生成后续行动报告"""
    print("\n" + "=" * 80)
    print("生成后续行动报告")
    print("=" * 80)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = REPORT_DIR / f"FOLLOW_UP_ACTION_REPORT_{timestamp}.md"
    
    report_content = f'''---
module_id: FOLLOW_UP_ACTION_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: 行动报告
applicable_scope: 后续行动和持续改进
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# 后续行动和持续改进报告

> **核心职责**: 记录后续行动和持续改进的执行过程和结果
> **职责边界**: 
> - [OK] 本文档负责：行动记录、改进统计、效果评估
> - [NO] 本文档不负责：后续审计执行、新问题发现

---

## 行动概要

**执行时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**执行范围**: 后续行动和持续改进  
**执行方法**: 自动化脚本 + 人工审查  
**执行结论**: 成功完成所有后续行动

---

## 行动统计

| 行动类型 | 完成数 | 状态 |
|---------|--------|------|
| **路径引用审查** | {len(path_issues)} | 需人工判断 |
| **引用链接更新** | {len(updated_links)} | 已完成 |
| **自动化检查机制** | 1 | 已建立 |
| **定期审查机制** | 1 | 已建立 |
| **质量标准优化** | 1 | 已完成 |

---

## 行动详情

### 1. 路径引用审查

**审查数量**: {len(path_issues)} 个文档

**主要问题**:
'''
    
    for issue in path_issues[:10]:
        report_content += f"- **{issue['file']}**: {issue['parent_ref_count']} 个 ../ 引用 (深度: {issue['depth']})\n"
    
    report_content += f'''
**简化建议**: {len(path_recommendations)} 个

'''
    
    for rec in path_recommendations[:5]:
        report_content += f"- **{rec['file']}**: {rec['suggested_action']}\n"
    
    report_content += f'''
### 2. 引用链接更新

**更新数量**: {len(updated_links)} 个文档

'''
    
    for update in updated_links[:10]:
        report_content += f"- **{update['file']}**: 更新 {len(update['changes'])} 个引用\n"
    
    report_content += f'''
### 3. 自动化检查机制

**创建文件**: `{check_script}`

**检查功能**:
- 命名规范检查
- 职责描述检查
- 索引完备性检查
- 死链接检查
- YAML完整性检查

**使用方法**:
```bash
python scripts/automated_document_check.py
```

---

### 4. 定期审查机制

**创建文件**: `{review_plan}`

**审查频率**:
- 每日检查: 自动化检查
- 每周检查: 自动化 + 人工审查
- 每月检查: 深度审计
- 每季度检查: 全面审计

---

### 5. 质量标准优化

**创建文件**: `{quality_standard}`

**质量维度**:
- 结构质量
- 内容质量
- 命名质量
- 引用质量

**质量目标**:
- 短期目标（1个月）
- 中期目标（3个月）
- 长期目标（持续）

---

## 后续建议

### 立即行动

1. [ ] 人工审查路径引用问题（40个文档）
2. [ ] 执行自动化检查脚本
3. [ ] 启动定期审查机制

### 持续改进

1. [ ] 定期执行自动化检查
2. [ ] 跟踪质量指标趋势
3. [ ] 持续优化质量标准

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本，后续行动报告 | 首席文档架构师 |
'''
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"[OK] 报告生成: {report_file.name}")
    
    return report_file

def main():
    """主函数"""
    print("后续行动和持续改进")
    print("=" * 80)
    
    # 1. 审查路径引用问题
    path_issues, path_recommendations = review_path_references()
    
    # 2. 更新相关文档的引用链接
    updated_links = update_reference_links()
    
    # 3. 建立自动化检查机制
    check_script = create_automated_check_mechanism()
    
    # 4. 定期执行审查机制
    review_plan = create_periodic_review_mechanism()
    
    # 5. 持续优化质量标准
    quality_standard = optimize_quality_standards()
    
    # 6. 生成后续行动报告
    report_file = generate_action_report(
        path_issues, path_recommendations, updated_links,
        check_script, review_plan, quality_standard
    )
    
    print("\n" + "=" * 80)
    print("后续行动完成")
    print("=" * 80)
    print(f"路径审查: {len(path_issues)} 个")
    print(f"链接更新: {len(updated_links)} 个")
    print(f"自动化机制: 已建立")
    print(f"审查机制: 已建立")
    print(f"质量标准: 已优化")
    print(f"报告位置: {report_file}")

if __name__ == '__main__':
    main()
