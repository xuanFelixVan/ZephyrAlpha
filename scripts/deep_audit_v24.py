#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
第二十四次深度审计脚本
功能：全面审计Alpha因子层文档，重点检查重复内容和职责不清楚的内容
"""

import os
import re
import json
import hashlib
from datetime import datetime
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_DIR = PROJECT_ROOT / "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state"

def calculate_content_hash(content):
    """计算内容哈希值"""
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def extract_module_id(content):
    """提取module_id"""
    match = re.search(r'module_id:\s*(\S+)', content)
    return match.group(1) if match else None

def extract_responsibility(content):
    """提取职责描述"""
    patterns = [
        r'\*\*核心职责\*\*:\s*(.+?)(?:\n|$)',
        r'\*\*本文档职责\*\*[：:]\s*(.+?)(?:\n|$)',
        r'核心职责[：:]\s*(.+?)(?:\n|$)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            return match.group(1).strip()
    
    return None

def check_yaml_header(content):
    """检查YAML头部"""
    return content.startswith('---')

def scan_all_files(directory):
    """扫描所有文件"""
    files_info = []
    
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        
        for file in files:
            if not file.endswith('.md'):
                continue
            
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, directory)
            
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                files_info.append({
                    'path': rel_path,
                    'abs_path': file_path,
                    'content': content,
                    'content_hash': calculate_content_hash(content),
                    'module_id': extract_module_id(content),
                    'responsibility': extract_responsibility(content),
                    'has_yaml': check_yaml_header(content),
                    'file_size': len(content),
                    'line_count': content.count('\n') + 1
                })
            except Exception as e:
                print(f"读取文件失败: {rel_path}, 错误: {str(e)}")
    
    return files_info

def l1_file_system_audit(files_info):
    """L1文件系统层审计"""
    issues = {
        'sparse_directories': [],
        'naming_issues': [],
        'path_issues': []
    }
    
    # 检查稀疏目录
    dir_file_count = defaultdict(int)
    for file_info in files_info:
        dir_path = os.path.dirname(file_info['path'])
        dir_file_count[dir_path] += 1
    
    for dir_path, count in dir_file_count.items():
        if count < 3 and count > 0:
            issues['sparse_directories'].append({
                'path': dir_path,
                'file_count': count
            })
    
    # 检查命名问题
    for file_info in files_info:
        file_name = os.path.basename(file_info['path'])
        
        # 检查旧架构命名
        if re.search(r'Layer\s*[0-9]', file_name):
            issues['naming_issues'].append({
                'path': file_info['path'],
                'issue': '旧架构命名残留',
                'detail': f'文件名包含旧架构关键词: {file_name}'
            })
        
        # 检查特殊字符
        if re.search(r'[\s\u4e00-\u9fff]', file_name):
            issues['naming_issues'].append({
                'path': file_info['path'],
                'issue': '特殊字符问题',
                'detail': f'文件名包含空格或中文: {file_name}'
            })
    
    return issues

def l2_document_content_audit(files_info):
    """L2文档内容层审计"""
    issues = {
        'responsibility_issues': [],
        'index_issues': [],
        'version_issues': [],
        'code_doc_issues': []
    }
    
    # 检查职责问题
    for file_info in files_info:
        # 检查职责描述缺失
        if not file_info['responsibility']:
            issues['responsibility_issues'].append({
                'path': file_info['path'],
                'issue': '职责描述缺失',
                'detail': '文档缺少核心职责描述'
            })
    
    # 检查职责重叠
    responsibility_map = defaultdict(list)
    for file_info in files_info:
        if file_info['responsibility']:
            responsibility_map[file_info['responsibility']].append(file_info['path'])
    
    for responsibility, paths in responsibility_map.items():
        if len(paths) > 1:
            issues['responsibility_issues'].append({
                'paths': paths,
                'issue': '职责重叠',
                'detail': f'多个文档具有相同职责: {responsibility}'
            })
    
    # 检查module_id重复
    module_id_map = defaultdict(list)
    for file_info in files_info:
        if file_info['module_id']:
            module_id_map[file_info['module_id']].append(file_info['path'])
    
    for module_id, paths in module_id_map.items():
        if len(paths) > 1:
            issues['version_issues'].append({
                'paths': paths,
                'issue': 'module_id重复',
                'detail': f'多个文档使用相同module_id: {module_id}'
            })
    
    # 检查YAML头部缺失
    for file_info in files_info:
        if not file_info['has_yaml']:
            issues['index_issues'].append({
                'path': file_info['path'],
                'issue': 'YAML头部缺失',
                'detail': '文档缺少标准YAML元数据'
            })
    
    return issues

def l3_professional_standard_audit(files_info):
    """L3专业标准层审计"""
    issues = {
        'principle_violations': [],
        'classification_issues': [],
        'numbering_issues': [],
        'quality_issues': []
    }
    
    # 检查五大原则符合性
    for file_info in files_info:
        violations = []
        
        # 职责驱动原则
        if not file_info['responsibility']:
            violations.append('职责驱动原则违反: 缺少职责描述')
        
        # 版本隔离原则
        if not file_info['module_id']:
            violations.append('版本隔离原则违反: 缺少module_id')
        
        # 命名规范原则
        file_name = os.path.basename(file_info['path'])
        if not re.match(r'^[A-Z_0-9]+\.md$', file_name):
            violations.append('命名规范原则违反: 文件名不符合标准')
        
        if violations:
            issues['principle_violations'].append({
                'path': file_info['path'],
                'violations': violations
            })
    
    # 检查编号体系
    for file_info in files_info:
        if not file_info['module_id']:
            issues['numbering_issues'].append({
                'path': file_info['path'],
                'issue': '编号缺失',
                'detail': '文档缺少module_id编号'
            })
    
    # 检查文档质量
    for file_info in files_info:
        quality_issues = []
        
        # 检查文档大小
        if file_info['file_size'] < 500:
            quality_issues.append('文档内容过少')
        
        # 检查行数
        if file_info['line_count'] < 20:
            quality_issues.append('文档行数过少')
        
        if quality_issues:
            issues['quality_issues'].append({
                'path': file_info['path'],
                'issues': quality_issues
            })
    
    return issues

def check_content_duplication(files_info):
    """检查内容重复"""
    duplicates = []
    content_map = defaultdict(list)
    
    for file_info in files_info:
        content_map[file_info['content_hash']].append(file_info['path'])
    
    for content_hash, paths in content_map.items():
        if len(paths) > 1:
            duplicates.append({
                'paths': paths,
                'content_hash': content_hash,
                'issue': '内容完全重复'
            })
    
    return duplicates

def generate_audit_report(l1_issues, l2_issues, l3_issues, duplicates, files_info):
    """生成审计报告"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = OUTPUT_DIR / f'DEEP_AUDIT_REPORT_V24_{timestamp}.md'
    
    total_files = len(files_info)
    total_issues = (
        len(l1_issues['sparse_directories']) +
        len(l1_issues['naming_issues']) +
        len(l2_issues['responsibility_issues']) +
        len(l2_issues['index_issues']) +
        len(l2_issues['version_issues']) +
        len(l3_issues['principle_violations']) +
        len(l3_issues['numbering_issues']) +
        len(l3_issues['quality_issues']) +
        len(duplicates)
    )
    
    report_content = f"""---
module_id: DEEP_AUDIT_REPORT_V24_{timestamp}
version: 24.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: 深度审计报告
applicable_scope: Alpha因子层全系统文档
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# 第二十四次深度审计报告

## 📊 审计概要

**审计时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**审计范围**: Alpha因子层全系统文档  
**审计方法**: 三层审计方法论（L1-L3）  
**审计重点**: 重复内容、职责不清楚  
**审计结论**: 发现 {total_issues} 个问题

---

## 📈 审计统计

| 统计项 | 数量 |
|--------|------|
| **审计文件总数** | {total_files} |
| **发现问题总数** | {total_issues} |
| **L1文件系统层问题** | {len(l1_issues['sparse_directories']) + len(l1_issues['naming_issues'])} |
| **L2文档内容层问题** | {len(l2_issues['responsibility_issues']) + len(l2_issues['index_issues']) + len(l2_issues['version_issues'])} |
| **L3专业标准层问题** | {len(l3_issues['principle_violations']) + len(l3_issues['numbering_issues']) + len(l3_issues['quality_issues'])} |
| **内容重复问题** | {len(duplicates)} |

---

## 🔴 L1 文件系统层审计结果

### 1.1 稀疏目录 ({len(l1_issues['sparse_directories'])}个)

"""
    
    if l1_issues['sparse_directories']:
        for i, dir_info in enumerate(l1_issues['sparse_directories'][:20], 1):
            report_content += f"{i}. {dir_info['path']} ({dir_info['file_count']}个文件)\n"
        if len(l1_issues['sparse_directories']) > 20:
            report_content += f"... 还有 {len(l1_issues['sparse_directories']) - 20} 个目录\n"
    else:
        report_content += "✅ 无问题\n"
    
    report_content += f"""
### 1.2 命名问题 ({len(l1_issues['naming_issues'])}个)

"""
    
    if l1_issues['naming_issues']:
        for i, naming_issue in enumerate(l1_issues['naming_issues'][:20], 1):
            report_content += f"{i}. {naming_issue['path']}\n   - 问题: {naming_issue['issue']}\n   - 详情: {naming_issue['detail']}\n"
        if len(l1_issues['naming_issues']) > 20:
            report_content += f"... 还有 {len(l1_issues['naming_issues']) - 20} 个问题\n"
    else:
        report_content += "✅ 无问题\n"
    
    report_content += f"""
---

## 🟡 L2 文档内容层审计结果

### 2.1 职责问题 ({len(l2_issues['responsibility_issues'])}个)

"""
    
    if l2_issues['responsibility_issues']:
        for i, resp_issue in enumerate(l2_issues['responsibility_issues'][:20], 1):
            if 'paths' in resp_issue:
                report_content += f"{i}. 职责重叠问题:\n"
                for path in resp_issue['paths']:
                    report_content += f"   - {path}\n"
                report_content += f"   - 详情: {resp_issue['detail']}\n"
            else:
                report_content += f"{i}. {resp_issue['path']}\n   - 问题: {resp_issue['issue']}\n   - 详情: {resp_issue['detail']}\n"
        if len(l2_issues['responsibility_issues']) > 20:
            report_content += f"... 还有 {len(l2_issues['responsibility_issues']) - 20} 个问题\n"
    else:
        report_content += "✅ 无问题\n"
    
    report_content += f"""
### 2.2 索引问题 ({len(l2_issues['index_issues'])}个)

"""
    
    if l2_issues['index_issues']:
        for i, index_issue in enumerate(l2_issues['index_issues'][:20], 1):
            report_content += f"{i}. {index_issue['path']}\n   - 问题: {index_issue['issue']}\n   - 详情: {index_issue['detail']}\n"
        if len(l2_issues['index_issues']) > 20:
            report_content += f"... 还有 {len(l2_issues['index_issues']) - 20} 个问题\n"
    else:
        report_content += "✅ 无问题\n"
    
    report_content += f"""
### 2.3 版本问题 ({len(l2_issues['version_issues'])}个)

"""
    
    if l2_issues['version_issues']:
        for i, version_issue in enumerate(l2_issues['version_issues'][:20], 1):
            report_content += f"{i}. {version_issue['issue']}:\n"
            for path in version_issue['paths']:
                report_content += f"   - {path}\n"
            report_content += f"   - 详情: {version_issue['detail']}\n"
        if len(l2_issues['version_issues']) > 20:
            report_content += f"... 还有 {len(l2_issues['version_issues']) - 20} 个问题\n"
    else:
        report_content += "✅ 无问题\n"
    
    report_content += f"""
---

## 🟢 L3 专业标准层审计结果

### 3.1 五大原则违反 ({len(l3_issues['principle_violations'])}个)

"""
    
    if l3_issues['principle_violations']:
        for i, violation in enumerate(l3_issues['principle_violations'][:20], 1):
            report_content += f"{i}. {violation['path']}\n"
            for v in violation['violations']:
                report_content += f"   - {v}\n"
        if len(l3_issues['principle_violations']) > 20:
            report_content += f"... 还有 {len(l3_issues['principle_violations']) - 20} 个问题\n"
    else:
        report_content += "✅ 无问题\n"
    
    report_content += f"""
### 3.2 编号问题 ({len(l3_issues['numbering_issues'])}个)

"""
    
    if l3_issues['numbering_issues']:
        for i, numbering_issue in enumerate(l3_issues['numbering_issues'][:20], 1):
            report_content += f"{i}. {numbering_issue['path']}\n   - 问题: {numbering_issue['issue']}\n   - 详情: {numbering_issue['detail']}\n"
        if len(l3_issues['numbering_issues']) > 20:
            report_content += f"... 还有 {len(l3_issues['numbering_issues']) - 20} 个问题\n"
    else:
        report_content += "✅ 无问题\n"
    
    report_content += f"""
### 3.3 质量问题 ({len(l3_issues['quality_issues'])}个)

"""
    
    if l3_issues['quality_issues']:
        for i, quality_issue in enumerate(l3_issues['quality_issues'][:20], 1):
            report_content += f"{i}. {quality_issue['path']}\n"
            for issue in quality_issue['issues']:
                report_content += f"   - {issue}\n"
        if len(l3_issues['quality_issues']) > 20:
            report_content += f"... 还有 {len(l3_issues['quality_issues']) - 20} 个问题\n"
    else:
        report_content += "✅ 无问题\n"
    
    report_content += f"""
---

## 🔍 内容重复检查结果

### 重复内容 ({len(duplicates)}组)

"""
    
    if duplicates:
        for i, dup in enumerate(duplicates[:20], 1):
            report_content += f"{i}. 内容完全重复:\n"
            for path in dup['paths']:
                report_content += f"   - {path}\n"
            report_content += f"   - 哈希: {dup['content_hash'][:16]}...\n"
        if len(duplicates) > 20:
            report_content += f"... 还有 {len(duplicates) - 20} 组重复\n"
    else:
        report_content += "✅ 无问题\n"
    
    report_content += f"""
---

## 💡 改进建议

### 立即修复（24小时内）

"""
    
    high_priority_issues = []
    
    if l2_issues['version_issues']:
        high_priority_issues.append("1. **修复module_id重复**: 为重复的module_id重新分配唯一编号")
    
    if duplicates:
        high_priority_issues.append("2. **处理内容重复**: 删除或合并重复文档")
    
    if l2_issues['index_issues']:
        high_priority_issues.append("3. **补充YAML头部**: 为缺少YAML头部的文档补充标准元数据")
    
    if high_priority_issues:
        report_content += "\n".join(high_priority_issues)
    else:
        report_content += "✅ 无高风险问题\n"
    
    report_content += f"""
### 本周修复

1. **补充职责描述**: 为缺少职责描述的文档添加核心职责描述
2. **治理稀疏目录**: 评估稀疏目录是否需要补充内容或整合
3. **修复命名问题**: 修正不符合命名规范的文件名

### 长期优化

1. **建立自动化检查机制**: 定期执行文档治理审计
2. **建立职责描述规范**: 制定职责描述模板和审查机制
3. **持续改进机制**: 每周执行文档治理审计，及时发现和修复问题

---

## 📝 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v24.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 第二十四次深度审计报告 | 首席文档架构师 |
"""
    
    # 写入报告
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    return report_path

def main():
    """主函数"""
    print("=" * 80)
    print("第二十四次深度审计")
    print("=" * 80)
    print(f"审计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 扫描所有文件
    print("扫描文档目录...")
    files_info = scan_all_files(DOCS_DIR)
    print(f"扫描完成: 共 {len(files_info)} 个文件")
    print()
    
    # 执行三层审计
    print("执行L1文件系统层审计...")
    l1_issues = l1_file_system_audit(files_info)
    print(f"  - 稀疏目录: {len(l1_issues['sparse_directories'])}个")
    print(f"  - 命名问题: {len(l1_issues['naming_issues'])}个")
    
    print("执行L2文档内容层审计...")
    l2_issues = l2_document_content_audit(files_info)
    print(f"  - 职责问题: {len(l2_issues['responsibility_issues'])}个")
    print(f"  - 索引问题: {len(l2_issues['index_issues'])}个")
    print(f"  - 版本问题: {len(l2_issues['version_issues'])}个")
    
    print("执行L3专业标准层审计...")
    l3_issues = l3_professional_standard_audit(files_info)
    print(f"  - 原则违反: {len(l3_issues['principle_violations'])}个")
    print(f"  - 编号问题: {len(l3_issues['numbering_issues'])}个")
    print(f"  - 质量问题: {len(l3_issues['quality_issues'])}个")
    
    print("检查内容重复...")
    duplicates = check_content_duplication(files_info)
    print(f"  - 重复内容: {len(duplicates)}组")
    print()
    
    # 生成报告
    print("生成审计报告...")
    report_path = generate_audit_report(l1_issues, l2_issues, l3_issues, duplicates, files_info)
    print(f"报告已保存至: {report_path}")
    
    print()
    print("=" * 80)
    print("审计完成")
    print("=" * 80)
    
    # 保存JSON结果
    json_path = OUTPUT_DIR / f'deep_audit_result_v24_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_files': len(files_info),
            'l1_issues': l1_issues,
            'l2_issues': l2_issues,
            'l3_issues': l3_issues,
            'duplicates': duplicates
        }, f, ensure_ascii=False, indent=2)
    
    print(f"JSON结果已保存至: {json_path}")

if __name__ == '__main__':
    main()
