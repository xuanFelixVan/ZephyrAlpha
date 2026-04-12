#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
稀疏目录治理脚本
功能：评估稀疏目录并生成治理建议
"""

import os
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_DIR = PROJECT_ROOT / "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state"

def is_blueprint_stage_directory(dir_path):
    """判断是否为蓝图阶段目录"""
    blueprint_indicators = [
        'BLUEPRINT',
        'DESIGN',
        'PLAN',
        'DRAFT',
        'PROTOTYPE'
    ]
    
    dir_name = os.path.basename(dir_path).upper()
    
    for indicator in blueprint_indicators:
        if indicator in dir_name:
            return True
    
    return False

def evaluate_sparse_directory(dir_path, file_count):
    """评估稀疏目录"""
    evaluation = {
        'path': dir_path,
        'file_count': file_count,
        'is_blueprint_stage': is_blueprint_stage_directory(dir_path),
        'recommendation': '',
        'reason': ''
    }
    
    # 蓝图阶段目录
    if evaluation['is_blueprint_stage']:
        evaluation['recommendation'] = '保持现状'
        evaluation['reason'] = '蓝图阶段目录，内容将在后续开发中补充'
        return evaluation
    
    # 根据目录特征判断
    dir_name = os.path.basename(dir_path).upper()
    
    # 数据源子目录
    if 'DATA_SOURCE' in dir_path.upper():
        evaluation['recommendation'] = '保持现状'
        evaluation['reason'] = '数据源模块子目录，蓝图阶段特征明显'
        return evaluation
    
    # 资源目录
    if 'RESOURCES' in dir_name or 'PLATFORM_DOCS' in dir_name:
        evaluation['recommendation'] = '保持现状'
        evaluation['reason'] = '资源目录，内容按需补充'
        return evaluation
    
    # 架构决策目录
    if 'ARCHITECTURE_DECISIONS' in dir_name:
        evaluation['recommendation'] = '保持现状'
        evaluation['reason'] = '架构决策目录，记录重要决策即可'
        return evaluation
    
    # 其他目录
    evaluation['recommendation'] = '评估补充'
    evaluation['reason'] = '需要评估是否补充内容或整合到父目录'
    return evaluation

def scan_sparse_directories():
    """扫描稀疏目录"""
    sparse_dirs = []
    
    for root, dirs, files in os.walk(DOCS_DIR):
        # 排除特定目录
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        
        md_files = [f for f in files if f.endswith('.md')]
        
        if len(md_files) < 3 and len(md_files) > 0:
            rel_path = os.path.relpath(root, DOCS_DIR)
            sparse_dirs.append({
                'path': rel_path,
                'file_count': len(md_files)
            })
    
    return sparse_dirs

def generate_governance_report(sparse_dirs):
    """生成治理报告"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = OUTPUT_DIR / f'SPARSE_DIRECTORY_GOVERNANCE_REPORT_{timestamp}.md'
    
    # 评估所有稀疏目录
    evaluations = []
    for dir_info in sparse_dirs:
        evaluation = evaluate_sparse_directory(dir_info['path'], dir_info['file_count'])
        evaluations.append(evaluation)
    
    # 统计
    keep_count = sum(1 for e in evaluations if e['recommendation'] == '保持现状')
    evaluate_count = sum(1 for e in evaluations if e['recommendation'] == '评估补充')
    
    report_content = f"""---
module_id: SPARSE_DIRECTORY_GOVERNANCE_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: 稀疏目录治理报告
applicable_scope: 全系统稀疏目录
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# 稀疏目录治理报告

## 📊 治理概要

**治理时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**治理范围**: 全系统稀疏目录  
**治理方法**: 蓝图阶段特征评估  
**治理结论**: {keep_count}个目录保持现状，{evaluate_count}个目录需要评估补充

---

## 📈 治理统计

| 统计项 | 数量 |
|--------|------|
| **稀疏目录总数** | {len(sparse_dirs)} |
| **保持现状** | {keep_count} |
| **评估补充** | {evaluate_count} |
| **蓝图阶段目录** | {sum(1 for e in evaluations if e['is_blueprint_stage'])} |

---

## 📋 治理建议

### 1. 保持现状的目录 ({keep_count}个)

"""
    
    keep_dirs = [e for e in evaluations if e['recommendation'] == '保持现状']
    for i, e in enumerate(keep_dirs[:50], 1):
        report_content += f"{i}. {e['path']} ({e['file_count']}个文件)\n   - 原因: {e['reason']}\n"
    
    if len(keep_dirs) > 50:
        report_content += f"... 还有 {len(keep_dirs) - 50} 个目录\n"
    
    report_content += f"""
### 2. 需要评估补充的目录 ({evaluate_count}个)

"""
    
    evaluate_dirs = [e for e in evaluations if e['recommendation'] == '评估补充']
    for i, e in enumerate(evaluate_dirs, 1):
        report_content += f"{i}. {e['path']} ({e['file_count']}个文件)\n   - 原因: {e['reason']}\n"
    
    report_content += f"""
---

## 💡 治理建议

### 立即执行

1. **保持现状**: {keep_count}个蓝图阶段目录无需处理
2. **评估补充**: {evaluate_count}个目录需要人工评估

### 本周执行

1. **人工评估**: 对{evaluate_count}个需要评估的目录进行人工审查
2. **补充内容**: 根据评估结果补充必要内容

### 长期优化

1. **定期检查**: 每月检查稀疏目录状态
2. **动态调整**: 根据项目进展调整目录结构

---

## 📝 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本，稀疏目录治理报告 | 首席文档架构师 |
"""
    
    # 写入报告
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    return report_path, evaluations

def main():
    """主函数"""
    print("=" * 80)
    print("稀疏目录治理")
    print("=" * 80)
    print(f"治理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 扫描稀疏目录
    print("扫描稀疏目录...")
    sparse_dirs = scan_sparse_directories()
    print(f"发现 {len(sparse_dirs)} 个稀疏目录")
    print()
    
    # 生成治理报告
    print("生成治理报告...")
    report_path, evaluations = generate_governance_report(sparse_dirs)
    print(f"报告已保存至: {report_path}")
    
    print()
    print("=" * 80)
    print("治理完成")
    print("=" * 80)
    
    # 保存JSON结果
    json_path = OUTPUT_DIR / f'sparse_directory_governance_result_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_sparse_dirs': len(sparse_dirs),
            'evaluations': evaluations
        }, f, ensure_ascii=False, indent=2)
    
    print(f"JSON结果已保存至: {json_path}")

if __name__ == '__main__':
    main()
