#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
自动化检查机制脚本
功能：定期检查文档治理质量，自动生成检查报告
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
    """检查职责描述"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        has_responsibility = '**核心职责**' in content or '**本文档职责**' in content
        return has_responsibility
    except:
        return False

def check_yaml_header(file_path):
    """检查YAML头部"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        has_yaml = content.startswith('---')
        return has_yaml
    except:
        return False

def check_module_id(file_path):
    """检查module_id"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        has_module_id = 'module_id:' in content
        return has_module_id
    except:
        return False

def check_filename_naming(file_path):
    """检查文件命名规范"""
    file_name = os.path.basename(file_path)
    
    # 检查是否包含中文
    has_chinese = any('\u4e00' <= char <= '\u9fff' for char in file_name)
    
    # 检查是否包含空格
    has_space = ' ' in file_name
    
    # 检查是否符合命名规范（大写字母、数字、下划线）
    is_standard = bool(re.match(r'^[A-Z_0-9]+\.md$', file_name))
    
    return {
        'has_chinese': has_chinese,
        'has_space': has_space,
        'is_standard': is_standard,
        'is_valid': not has_chinese and not has_space and is_standard
    }

def scan_all_files():
    """扫描所有文件"""
    results = {
        'total_files': 0,
        'missing_responsibility': [],
        'missing_yaml': [],
        'missing_module_id': [],
        'naming_issues': [],
        'sparse_directories': []
    }
    
    dir_file_count = {}
    
    for root, dirs, files in os.walk(DOCS_DIR):
        # 排除特定目录
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        
        md_files = [f for f in files if f.endswith('.md')]
        
        # 统计目录文件数
        if md_files:
            dir_file_count[root] = len(md_files)
        
        for file in md_files:
            results['total_files'] += 1
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, DOCS_DIR)
            
            # 检查职责描述
            if not check_responsibility_description(file_path):
                results['missing_responsibility'].append(rel_path)
            
            # 检查YAML头部
            if not check_yaml_header(file_path):
                results['missing_yaml'].append(rel_path)
            
            # 检查module_id
            if not check_module_id(file_path):
                results['missing_module_id'].append(rel_path)
            
            # 检查文件命名
            naming_check = check_filename_naming(file_path)
            if not naming_check['is_valid']:
                results['naming_issues'].append({
                    'path': rel_path,
                    'has_chinese': naming_check['has_chinese'],
                    'has_space': naming_check['has_space'],
                    'is_standard': naming_check['is_standard']
                })
    
    # 检查稀疏目录
    for dir_path, count in dir_file_count.items():
        if count < 3:
            rel_path = os.path.relpath(dir_path, DOCS_DIR)
            results['sparse_directories'].append({
                'path': rel_path,
                'file_count': count
            })
    
    return results

def calculate_compliance_rate(results):
    """计算合规率"""
    total = results['total_files']
    
    if total == 0:
        return 0
    
    # 计算各项合规率
    responsibility_rate = (total - len(results['missing_responsibility'])) / total * 100
    yaml_rate = (total - len(results['missing_yaml'])) / total * 100
    module_id_rate = (total - len(results['missing_module_id'])) / total * 100
    naming_rate = (total - len(results['naming_issues'])) / total * 100
    
    # 总体合规率（平均值）
    overall_rate = (responsibility_rate + yaml_rate + module_id_rate + naming_rate) / 4
    
    return {
        'responsibility_rate': responsibility_rate,
        'yaml_rate': yaml_rate,
        'module_id_rate': module_id_rate,
        'naming_rate': naming_rate,
        'overall_rate': overall_rate
    }

def generate_report(results, compliance_rate):
    """生成检查报告"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = OUTPUT_DIR / f'automated_check_report_{timestamp}.md'
    
    report_content = f"""---
module_id: AUTOMATED_CHECK_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: 自动化检查报告
applicable_scope: 全系统文档治理
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# 自动化检查报告

## 📊 检查概要

**检查时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**检查范围**: 全系统文档  
**检查方法**: 自动化扫描  
**检查结论**: 总体合规率 {compliance_rate['overall_rate']:.1f}%

---

## 📈 合规率统计

| 检查项 | 合规率 | 状态 |
|--------|--------|------|
| **职责描述** | {compliance_rate['responsibility_rate']:.1f}% | {'✅ 达标' if compliance_rate['responsibility_rate'] >= 95 else '⚠️ 需改进'} |
| **YAML头部** | {compliance_rate['yaml_rate']:.1f}% | {'✅ 达标' if compliance_rate['yaml_rate'] >= 95 else '⚠️ 需改进'} |
| **Module ID** | {compliance_rate['module_id_rate']:.1f}% | {'✅ 达标' if compliance_rate['module_id_rate'] >= 95 else '⚠️ 需改进'} |
| **文件命名** | {compliance_rate['naming_rate']:.1f}% | {'✅ 达标' if compliance_rate['naming_rate'] >= 95 else '⚠️ 需改进'} |
| **总体合规率** | {compliance_rate['overall_rate']:.1f}% | {'✅ 达标' if compliance_rate['overall_rate'] >= 95 else '⚠️ 需改进'} |

---

## 📋 问题统计

| 问题类型 | 数量 | 严重程度 |
|---------|------|---------|
| **缺少职责描述** | {len(results['missing_responsibility'])} | {'🟡 中风险' if len(results['missing_responsibility']) > 0 else '✅ 无问题'} |
| **缺少YAML头部** | {len(results['missing_yaml'])} | {'🔴 高风险' if len(results['missing_yaml']) > 0 else '✅ 无问题'} |
| **缺少Module ID** | {len(results['missing_module_id'])} | {'🔴 高风险' if len(results['missing_module_id']) > 0 else '✅ 无问题'} |
| **命名不规范** | {len(results['naming_issues'])} | {'🟡 中风险' if len(results['naming_issues']) > 0 else '✅ 无问题'} |
| **稀疏目录** | {len(results['sparse_directories'])} | {'🟢 低风险' if len(results['sparse_directories']) > 0 else '✅ 无问题'} |

---

## 🔍 详细问题列表

### 1. 缺少职责描述 ({len(results['missing_responsibility'])}个)

"""
    
    if results['missing_responsibility']:
        for i, path in enumerate(results['missing_responsibility'][:20], 1):
            report_content += f"{i}. {path}\n"
        if len(results['missing_responsibility']) > 20:
            report_content += f"... 还有 {len(results['missing_responsibility']) - 20} 个文件\n"
    else:
        report_content += "✅ 无问题\n"
    
    report_content += f"""
### 2. 缺少YAML头部 ({len(results['missing_yaml'])}个)

"""
    
    if results['missing_yaml']:
        for i, path in enumerate(results['missing_yaml'][:20], 1):
            report_content += f"{i}. {path}\n"
        if len(results['missing_yaml']) > 20:
            report_content += f"... 还有 {len(results['missing_yaml']) - 20} 个文件\n"
    else:
        report_content += "✅ 无问题\n"
    
    report_content += f"""
### 3. 缺少Module ID ({len(results['missing_module_id'])}个)

"""
    
    if results['missing_module_id']:
        for i, path in enumerate(results['missing_module_id'][:20], 1):
            report_content += f"{i}. {path}\n"
        if len(results['missing_module_id']) > 20:
            report_content += f"... 还有 {len(results['missing_module_id']) - 20} 个文件\n"
    else:
        report_content += "✅ 无问题\n"
    
    report_content += f"""
### 4. 命名不规范 ({len(results['naming_issues'])}个)

"""
    
    if results['naming_issues']:
        for i, issue in enumerate(results['naming_issues'][:20], 1):
            issues = []
            if issue['has_chinese']:
                issues.append('包含中文')
            if issue['has_space']:
                issues.append('包含空格')
            if not issue['is_standard']:
                issues.append('不符合标准格式')
            report_content += f"{i}. {issue['path']}\n   - 问题: {', '.join(issues)}\n"
        if len(results['naming_issues']) > 20:
            report_content += f"... 还有 {len(results['naming_issues']) - 20} 个文件\n"
    else:
        report_content += "✅ 无问题\n"
    
    report_content += f"""
---

## 💡 改进建议

"""
    
    if compliance_rate['overall_rate'] >= 99:
        report_content += "✅ 文档治理质量优秀，继续保持！\n"
    elif compliance_rate['overall_rate'] >= 95:
        report_content += "✅ 文档治理质量良好，建议持续改进。\n"
    else:
        report_content += "⚠️ 文档治理质量需要改进，建议立即修复发现的问题。\n"
    
    report_content += f"""
---

## 📝 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本，自动化检查报告 | 首席文档架构师 |
"""
    
    # 写入报告
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    return report_path

def main():
    """主函数"""
    print("=" * 80)
    print("自动化检查机制")
    print("=" * 80)
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 扫描所有文件
    print("扫描文档目录...")
    results = scan_all_files()
    print(f"扫描完成: 共 {results['total_files']} 个文件")
    print()
    
    # 计算合规率
    print("计算合规率...")
    compliance_rate = calculate_compliance_rate(results)
    print(f"总体合规率: {compliance_rate['overall_rate']:.1f}%")
    print(f"  - 职责描述: {compliance_rate['responsibility_rate']:.1f}%")
    print(f"  - YAML头部: {compliance_rate['yaml_rate']:.1f}%")
    print(f"  - Module ID: {compliance_rate['module_id_rate']:.1f}%")
    print(f"  - 文件命名: {compliance_rate['naming_rate']:.1f}%")
    print()
    
    # 统计问题
    print("问题统计:")
    print(f"  - 缺少职责描述: {len(results['missing_responsibility'])}个")
    print(f"  - 缺少YAML头部: {len(results['missing_yaml'])}个")
    print(f"  - 缺少Module ID: {len(results['missing_module_id'])}个")
    print(f"  - 命名不规范: {len(results['naming_issues'])}个")
    print(f"  - 稀疏目录: {len(results['sparse_directories'])}个")
    print()
    
    # 生成报告
    print("生成检查报告...")
    report_path = generate_report(results, compliance_rate)
    print(f"报告已保存至: {report_path}")
    
    print()
    print("=" * 80)
    print("检查完成")
    print("=" * 80)
    
    # 保存JSON结果
    json_path = OUTPUT_DIR / f'automated_check_result_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_files': results['total_files'],
            'compliance_rate': compliance_rate,
            'issues': {
                'missing_responsibility': len(results['missing_responsibility']),
                'missing_yaml': len(results['missing_yaml']),
                'missing_module_id': len(results['missing_module_id']),
                'naming_issues': len(results['naming_issues']),
                'sparse_directories': len(results['sparse_directories'])
            }
        }, f, ensure_ascii=False, indent=2)
    
    print(f"JSON结果已保存至: {json_path}")

if __name__ == '__main__':
    main()
