#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
定期审计机制脚本
功能：每周执行文档治理审计，及时发现和修复问题
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_DIR = PROJECT_ROOT / "docs/09_AUDIT/STATE"

def check_responsibility_description(file_path):
    """检查文件是否有职责描述"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        has_responsibility = '**核心职责**' in content or '**本文档职责**' in content
        return has_responsibility
    except:
        return False

def check_yaml_header(file_path):
    """检查文件是否有YAML头部"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        has_yaml = content.startswith('---')
        return has_yaml
    except:
        return False

def check_module_id(file_path):
    """检查文件是否有module_id"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        has_module_id = 'module_id:' in content
        return has_module_id
    except:
        return False

def scan_directory(directory):
    """扫描目录并收集问题"""
    issues = {
        'missing_responsibility': [],
        'missing_yaml': [],
        'missing_module_id': [],
        'sparse_directories': []
    }
    
    # 扫描文件
    for root, dirs, files in os.walk(directory):
        # 排除特定目录
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        
        # 检查稀疏目录
        md_files = [f for f in files if f.endswith('.md')]
        if len(md_files) < 3 and len(md_files) > 0:
            rel_path = os.path.relpath(root, directory)
            issues['sparse_directories'].append({
                'path': rel_path,
                'file_count': len(md_files)
            })
        
        # 检查文件
        for file in files:
            if not file.endswith('.md'):
                continue
            
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, directory)
            
            # 检查职责描述
            if not check_responsibility_description(file_path):
                issues['missing_responsibility'].append(rel_path)
            
            # 检查YAML头部
            if not check_yaml_header(file_path):
                issues['missing_yaml'].append(rel_path)
            
            # 检查module_id
            if not check_module_id(file_path):
                issues['missing_module_id'].append(rel_path)
    
    return issues

def generate_report(issues):
    """生成审计报告"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = OUTPUT_DIR / f'weekly_audit_report_{timestamp}.md'
    
    total_issues = (
        len(issues['missing_responsibility']) +
        len(issues['missing_yaml']) +
        len(issues['missing_module_id']) +
        len(issues['sparse_directories'])
    )
    
    report_content = f"""---
module_id: WEEKLY_AUDIT_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: 定期审计报告
applicable_scope: 全系统文档治理
compliance_level: 专业标准
---

# 每周文档治理审计报告

## 📊 审计概要

**审计时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**审计范围**: 全系统文档  
**审计方法**: 自动化扫描  
**审计结论**: 发现 {total_issues} 个问题

---

## 📋 问题统计

| 问题类型 | 数量 | 严重程度 |
|---------|------|---------|
| **缺少职责描述** | {len(issues['missing_responsibility'])} | 🟡 中风险 |
| **缺少YAML头部** | {len(issues['missing_yaml'])} | 🔴 高风险 |
| **缺少module_id** | {len(issues['missing_module_id'])} | 🔴 高风险 |
| **稀疏目录** | {len(issues['sparse_directories'])} | 🟡 中风险 |

---

## 🔍 详细问题列表

### 1. 缺少职责描述 ({len(issues['missing_responsibility'])}个)

"""
    
    if issues['missing_responsibility']:
        for i, path in enumerate(issues['missing_responsibility'][:20], 1):
            report_content += f"{i}. {path}\n"
        if len(issues['missing_responsibility']) > 20:
            report_content += f"... 还有 {len(issues['missing_responsibility']) - 20} 个文件\n"
    else:
        report_content += "✅ 无问题\n"
    
    report_content += f"""
### 2. 缺少YAML头部 ({len(issues['missing_yaml'])}个)

"""
    
    if issues['missing_yaml']:
        for i, path in enumerate(issues['missing_yaml'][:20], 1):
            report_content += f"{i}. {path}\n"
        if len(issues['missing_yaml']) > 20:
            report_content += f"... 还有 {len(issues['missing_yaml']) - 20} 个文件\n"
    else:
        report_content += "✅ 无问题\n"
    
    report_content += f"""
### 3. 缺少module_id ({len(issues['missing_module_id'])}个)

"""
    
    if issues['missing_module_id']:
        for i, path in enumerate(issues['missing_module_id'][:20], 1):
            report_content += f"{i}. {path}\n"
        if len(issues['missing_module_id']) > 20:
            report_content += f"... 还有 {len(issues['missing_module_id']) - 20} 个文件\n"
    else:
        report_content += "✅ 无问题\n"
    
    report_content += f"""
### 4. 稀疏目录 ({len(issues['sparse_directories'])}个)

"""
    
    if issues['sparse_directories']:
        for i, dir_info in enumerate(issues['sparse_directories'][:20], 1):
            report_content += f"{i}. {dir_info['path']} ({dir_info['file_count']}个文件)\n"
        if len(issues['sparse_directories']) > 20:
            report_content += f"... 还有 {len(issues['sparse_directories']) - 20} 个目录\n"
    else:
        report_content += "✅ 无问题\n"
    
    report_content += f"""
---

## 💡 改进建议

### 立即修复（24小时内）

"""
    
    if issues['missing_yaml']:
        report_content += "1. **修复YAML头部缺失**: 为缺少YAML头部的文件补充标准YAML头部\n"
    
    if issues['missing_module_id']:
        report_content += "2. **修复module_id缺失**: 为缺少module_id的文件补充唯一module_id\n"
    
    report_content += """
### 本周修复

1. **补充职责描述**: 为缺少职责描述的文件添加核心职责描述
2. **评估稀疏目录**: 评估稀疏目录是否需要补充内容

### 长期优化

1. **建立自动化检查机制**: 每周执行文档治理审计
2. **建立职责描述规范**: 制定职责描述模板和审查机制

---

## 📝 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本，每周审计报告 | 首席文档架构师 |
"""
    
    # 写入报告
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    return report_path

def main():
    """主函数"""
    print("=" * 80)
    print("每周文档治理审计")
    print("=" * 80)
    print(f"审计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 扫描目录
    print("扫描文档目录...")
    issues = scan_directory(DOCS_DIR)
    
    # 统计问题
    total_issues = (
        len(issues['missing_responsibility']) +
        len(issues['missing_yaml']) +
        len(issues['missing_module_id']) +
        len(issues['sparse_directories'])
    )
    
    print(f"发现 {total_issues} 个问题:")
    print(f"  - 缺少职责描述: {len(issues['missing_responsibility'])}个")
    print(f"  - 缺少YAML头部: {len(issues['missing_yaml'])}个")
    print(f"  - 缺少module_id: {len(issues['missing_module_id'])}个")
    print(f"  - 稀疏目录: {len(issues['sparse_directories'])}个")
    print()
    
    # 生成报告
    print("生成审计报告...")
    report_path = generate_report(issues)
    print(f"报告已保存至: {report_path}")
    
    print()
    print("=" * 80)
    print("审计完成")
    print("=" * 80)
    
    # 保存JSON结果
    json_path = OUTPUT_DIR / f'weekly_audit_result_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_issues': total_issues,
            'issues': issues
        }, f, ensure_ascii=False, indent=2)
    
    print(f"JSON结果已保存至: {json_path}")

if __name__ == '__main__':
    main()
