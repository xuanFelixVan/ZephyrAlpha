#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
第二十三次深度审计工具
功能：全面审计Alpha因子层，重点检查重复内容和职责不清楚的问题
"""

import os
import re
import hashlib
from collections import defaultdict
from datetime import datetime
from pathlib import Path

def calculate_file_hash(file_path):
    """计算文件内容哈希值"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        # 移除YAML头部后计算哈希
        content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    except Exception as e:
        return None

def extract_title(file_path):
    """提取文档标题"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 提取第一个标题
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return None
    except:
        return None

def extract_responsibility(file_path):
    """提取职责描述"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 提取核心职责
        match = re.search(r'\*\*核心职责\*\*:\s*(.+)', content)
        if match:
            return match.group(1).strip()
        return None
    except:
        return None

def check_l1_file_system(root_path):
    """L1文件系统层审计"""
    results = {
        'directory_structure': {
            'sparse_dirs': [],
            'empty_dirs': [],
            'deep_dirs': []
        },
        'file_naming': {
            'non_standard_names': [],
            'special_chars': []
        },
        'path_references': {
            'broken_links': [],
            'redundant_paths': []
        }
    }
    
    # 检查目录结构
    for root, dirs, files in os.walk(root_path):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        
        if root == root_path:
            continue
        
        rel_path = os.path.relpath(root, root_path)
        depth = rel_path.count(os.sep)
        
        # 检查稀疏目录
        md_files = [f for f in files if f.endswith('.md')]
        if len(md_files) < 3 and len(md_files) > 0:
            results['directory_structure']['sparse_dirs'].append({
                'path': rel_path,
                'file_count': len(md_files)
            })
        
        # 检查空目录
        if len(files) == 0 and len(dirs) == 0:
            results['directory_structure']['empty_dirs'].append(rel_path)
        
        # 检查层级过深
        if depth > 4:
            results['directory_structure']['deep_dirs'].append({
                'path': rel_path,
                'depth': depth
            })
    
    return results

def check_l2_document_content(root_path):
    """L2文档内容层审计"""
    results = {
        'responsibility': {
            'unclear': [],
            'overlap': [],
            'missing': []
        },
        'index': {
            'missing_index': [],
            'incomplete_index': []
        },
        'version': {
            'duplicates': [],
            'old_versions': []
        },
        'content_duplicates': {
            'hash_duplicates': [],
            'title_duplicates': []
        }
    }
    
    # 收集所有文档信息
    docs_info = []
    hash_map = defaultdict(list)
    title_map = defaultdict(list)
    responsibilities = []
    
    for root, dirs, files in os.walk(root_path):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        
        for file in files:
            if not file.endswith('.md'):
                continue
            
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, root_path)
            
            # 计算哈希
            file_hash = calculate_file_hash(file_path)
            if file_hash:
                hash_map[file_hash].append(rel_path)
            
            # 提取标题
            title = extract_title(file_path)
            if title:
                title_map[title].append(rel_path)
            
            # 提取职责
            responsibility = extract_responsibility(file_path)
            if responsibility:
                responsibilities.append({
                    'path': rel_path,
                    'responsibility': responsibility
                })
            
            docs_info.append({
                'path': rel_path,
                'title': title,
                'responsibility': responsibility,
                'hash': file_hash
            })
    
    # 检查内容重复
    for file_hash, paths in hash_map.items():
        if len(paths) > 1:
            results['content_duplicates']['hash_duplicates'].append({
                'hash': file_hash,
                'files': paths
            })
    
    # 检查标题重复
    for title, paths in title_map.items():
        if len(paths) > 1:
            results['content_duplicates']['title_duplicates'].append({
                'title': title,
                'files': paths
            })
    
    # 检查职责重叠
    for i, r1 in enumerate(responsibilities):
        for j, r2 in enumerate(responsibilities[i+1:], i+1):
            keywords1 = set(re.findall(r'[\u4e00-\u9fa5]+', r1['responsibility']))
            keywords2 = set(re.findall(r'[\u4e00-\u9fa5]+', r2['responsibility']))
            
            overlap = keywords1 & keywords2
            if len(overlap) > 2:
                results['responsibility']['overlap'].append({
                    'file1': r1['path'],
                    'file2': r2['path'],
                    'overlap_keywords': list(overlap)
                })
    
    # 检查缺少职责描述的文档
    for doc in docs_info:
        if not doc['responsibility'] and doc['title']:
            # 排除索引文件和蓝图文件
            if 'INDEX.md' not in doc['path'] and 'BLUEPRINT.md' not in doc['path']:
                results['responsibility']['missing'].append(doc['path'])
    
    # 检查索引文件
    for root, dirs, files in os.walk(root_path):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        
        if root == root_path:
            continue
        
        if 'INDEX.md' not in files:
            rel_path = os.path.relpath(root, root_path)
            results['index']['missing_index'].append(rel_path)
    
    return results

def check_l3_professional_standards(root_path):
    """L3专业标准层审计"""
    results = {
        'five_principles': {
            'responsibility_violations': [],
            'index_violations': [],
            'version_violations': [],
            'naming_violations': []
        },
        'module_id': {
            'missing': [],
            'duplicates': [],
            'non_standard': []
        },
        'yaml_header': {
            'missing': [],
            'incomplete': []
        }
    }
    
    module_ids = defaultdict(list)
    
    for root, dirs, files in os.walk(root_path):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        
        for file in files:
            if not file.endswith('.md'):
                continue
            
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, root_path)
            
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                # 检查YAML头部
                if not content.startswith('---'):
                    results['yaml_header']['missing'].append(rel_path)
                    continue
                
                # 提取YAML头部
                yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
                if not yaml_match:
                    results['yaml_header']['missing'].append(rel_path)
                    continue
                
                yaml_content = yaml_match.group(1)
                
                # 检查必要字段
                required_fields = ['module_id', 'version', 'status', 'owner']
                missing_fields = []
                for field in required_fields:
                    if field not in yaml_content:
                        missing_fields.append(field)
                
                if missing_fields:
                    results['yaml_header']['incomplete'].append({
                        'path': rel_path,
                        'missing_fields': missing_fields
                    })
                
                # 检查module_id
                module_id_match = re.search(r'module_id:\s*(\S+)', yaml_content)
                if module_id_match:
                    module_id = module_id_match.group(1)
                    module_ids[module_id].append(rel_path)
                    
                    # 检查module_id格式
                    if not re.match(r'^[A-Z_0-9]+$', module_id):
                        results['module_id']['non_standard'].append({
                            'path': rel_path,
                            'module_id': module_id
                        })
                else:
                    results['module_id']['missing'].append(rel_path)
                
            except Exception as e:
                print(f"  ⚠️ 读取失败: {rel_path} - {e}")
    
    # 检查module_id重复
    for module_id, paths in module_ids.items():
        if len(paths) > 1:
            results['module_id']['duplicates'].append({
                'module_id': module_id,
                'files': paths
            })
    
    return results

def generate_audit_report(l1_results, l2_results, l3_results, output_path):
    """生成审计报告"""
    report = f"""---
module_id: LAYER2_ALPHA_FACTOR_DEEP_AUDIT_REPORT_V23_20260407
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
standard_type: 深度审计报告
applicable_scope: Alpha因子层全面审计
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# Alpha因子层第二十三次深度审计报告

## 📋 审计概要

**审计时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**审计范围**: Alpha因子层（02_FACTOR_LIBRARY）全量文档  
**审计方法**: 三层审计（L1文件系统层 + L2文档内容层 + L3专业标准层）  
**审计重点**: 重复内容检测、职责清晰度检查  
**审计结论**: 待分析

---

## 📊 L1 文件系统层审计结果

### 1.1 目录结构检查

| 问题类型 | 数量 | 严重程度 |
|---------|------|---------|
| **稀疏目录** | {len(l1_results['directory_structure']['sparse_dirs'])} | 🟡 中风险 |
| **空目录** | {len(l1_results['directory_structure']['empty_dirs'])} | 🟡 中风险 |
| **层级过深** | {len(l1_results['directory_structure']['deep_dirs'])} | 🟢 低风险 |

"""

    if l1_results['directory_structure']['sparse_dirs']:
        report += "#### 稀疏目录列表\n\n"
        for d in l1_results['directory_structure']['sparse_dirs'][:10]:
            report += f"- **{d['path']}** ({d['file_count']}个文件)\n"
        if len(l1_results['directory_structure']['sparse_dirs']) > 10:
            report += f"- ... 还有{len(l1_results['directory_structure']['sparse_dirs']) - 10}个\n"
        report += "\n"
    
    report += f"""---

## 📊 L2 文档内容层审计结果

### 2.1 内容重复检查

| 问题类型 | 数量 | 严重程度 |
|---------|------|---------|
| **内容哈希重复** | {len(l2_results['content_duplicates']['hash_duplicates'])} | 🔴 高风险 |
| **标题重复** | {len(l2_results['content_duplicates']['title_duplicates'])} | 🔴 高风险 |

"""

    if l2_results['content_duplicates']['hash_duplicates']:
        report += "#### 🔴 内容哈希重复\n\n"
        for dup in l2_results['content_duplicates']['hash_duplicates']:
            report += f"**哈希值**: {dup['hash'][:16]}...\n"
            for f in dup['files']:
                report += f"  - {f}\n"
            report += "\n"
    
    if l2_results['content_duplicates']['title_duplicates']:
        report += "#### 🔴 标题重复\n\n"
        for dup in l2_results['content_duplicates']['title_duplicates']:
            report += f"**标题**: {dup['title']}\n"
            for f in dup['files']:
                report += f"  - {f}\n"
            report += "\n"
    
    report += f"""### 2.2 职责清晰度检查

| 问题类型 | 数量 | 严重程度 |
|---------|------|---------|
| **职责重叠** | {len(l2_results['responsibility']['overlap'])} | 🟡 中风险 |
| **缺少职责描述** | {len(l2_results['responsibility']['missing'])} | 🟡 中风险 |

"""

    if l2_results['responsibility']['overlap']:
        report += "#### 🟡 职责重叠\n\n"
        for overlap in l2_results['responsibility']['overlap']:
            report += f"**{overlap['file1']}** vs **{overlap['file2']}**\n"
            report += f"重叠关键词: {', '.join(overlap['overlap_keywords'])}\n\n"
    
    if l2_results['responsibility']['missing']:
        report += "#### 🟡 缺少职责描述\n\n"
        for f in l2_results['responsibility']['missing'][:10]:
            report += f"- {f}\n"
        if len(l2_results['responsibility']['missing']) > 10:
            report += f"- ... 还有{len(l2_results['responsibility']['missing']) - 10}个\n"
        report += "\n"
    
    report += f"""### 2.3 索引完备性检查

| 问题类型 | 数量 | 严重程度 |
|---------|------|---------|
| **缺少INDEX.md** | {len(l2_results['index']['missing_index'])} | 🟡 中风险 |

"""

    if l2_results['index']['missing_index']:
        report += "#### 缺少索引文件的目录\n\n"
        for d in l2_results['index']['missing_index'][:10]:
            report += f"- {d}\n"
        if len(l2_results['index']['missing_index']) > 10:
            report += f"- ... 还有{len(l2_results['index']['missing_index']) - 10}个\n"
        report += "\n"
    
    report += f"""---

## 📊 L3 专业标准层审计结果

### 3.1 module_id检查

| 问题类型 | 数量 | 严重程度 |
|---------|------|---------|
| **module_id重复** | {len(l3_results['module_id']['duplicates'])} | 🔴 高风险 |
| **module_id缺失** | {len(l3_results['module_id']['missing'])} | 🔴 高风险 |
| **module_id不规范** | {len(l3_results['module_id']['non_standard'])} | 🟡 中风险 |

"""

    if l3_results['module_id']['duplicates']:
        report += "#### 🔴 module_id重复\n\n"
        for dup in l3_results['module_id']['duplicates']:
            report += f"**{dup['module_id']}**:\n"
            for f in dup['files']:
                report += f"  - {f}\n"
            report += "\n"
    
    if l3_results['module_id']['missing']:
        report += "#### 🔴 module_id缺失\n\n"
        for f in l3_results['module_id']['missing'][:10]:
            report += f"- {f}\n"
        if len(l3_results['module_id']['missing']) > 10:
            report += f"- ... 还有{len(l3_results['module_id']['missing']) - 10}个\n"
        report += "\n"
    
    report += f"""### 3.2 YAML头部检查

| 问题类型 | 数量 | 严重程度 |
|---------|------|---------|
| **YAML头部缺失** | {len(l3_results['yaml_header']['missing'])} | 🔴 高风险 |
| **YAML字段不完整** | {len(l3_results['yaml_header']['incomplete'])} | 🟡 中风险 |

"""

    if l3_results['yaml_header']['missing']:
        report += "#### 🔴 YAML头部缺失\n\n"
        for f in l3_results['yaml_header']['missing'][:10]:
            report += f"- {f}\n"
        if len(l3_results['yaml_header']['missing']) > 10:
            report += f"- ... 还有{len(l3_results['yaml_header']['missing']) - 10}个\n"
        report += "\n"
    
    if l3_results['yaml_header']['incomplete']:
        report += "#### 🟡 YAML字段不完整\n\n"
        for item in l3_results['yaml_header']['incomplete'][:10]:
            report += f"- **{item['path']}**: 缺少 {', '.join(item['missing_fields'])}\n"
        if len(l3_results['yaml_header']['incomplete']) > 10:
            report += f"- ... 还有{len(l3_results['yaml_header']['incomplete']) - 10}个\n"
        report += "\n"
    
    # 计算合规率
    total_files = 0
    for root, dirs, files in os.walk(r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY'):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        total_files += len([f for f in files if f.endswith('.md')])
    
    l1_issues = (len(l1_results['directory_structure']['sparse_dirs']) + 
                 len(l1_results['directory_structure']['empty_dirs']))
    l2_issues = (len(l2_results['content_duplicates']['hash_duplicates']) + 
                 len(l2_results['content_duplicates']['title_duplicates']) +
                 len(l2_results['responsibility']['overlap']))
    l3_issues = (len(l3_results['module_id']['duplicates']) + 
                 len(l3_results['module_id']['missing']) +
                 len(l3_results['yaml_header']['missing']))
    
    total_issues = l1_issues + l2_issues + l3_issues
    
    report += f"""---

## 📈 审计总结

### 问题统计

| 层级 | 问题数量 | 严重程度 |
|------|---------|---------|
| **L1文件系统层** | {l1_issues} | 🟡 中风险 |
| **L2文档内容层** | {l2_issues} | 🔴 高风险 |
| **L3专业标准层** | {l3_issues} | 🔴 高风险 |
| **总计** | {total_issues} | - |

### 合规率评估

- **总文件数**: {total_files}
- **问题文件数**: {min(total_issues, total_files)}
- **合规率**: {max(0, (total_files - min(total_issues, total_files)) / total_files * 100):.1f}%

### 高风险问题（需立即修复）

"""

    high_risk_issues = []
    
    if l2_results['content_duplicates']['hash_duplicates']:
        high_risk_issues.append("内容哈希重复")
    if l2_results['content_duplicates']['title_duplicates']:
        high_risk_issues.append("标题重复")
    if l3_results['module_id']['duplicates']:
        high_risk_issues.append("module_id重复")
    if l3_results['module_id']['missing']:
        high_risk_issues.append("module_id缺失")
    if l3_results['yaml_header']['missing']:
        high_risk_issues.append("YAML头部缺失")
    
    if high_risk_issues:
        for issue in high_risk_issues:
            report += f"1. {issue}\n"
    else:
        report += "✅ 未发现高风险问题\n"
    
    report += f"""

### 中风险问题（建议本周修复）

"""

    medium_risk_issues = []
    
    if l1_results['directory_structure']['sparse_dirs']:
        medium_risk_issues.append("稀疏目录")
    if l2_results['responsibility']['overlap']:
        medium_risk_issues.append("职责重叠")
    if l2_results['responsibility']['missing']:
        medium_risk_issues.append("缺少职责描述")
    if l3_results['yaml_header']['incomplete']:
        medium_risk_issues.append("YAML字段不完整")
    
    if medium_risk_issues:
        for issue in medium_risk_issues:
            report += f"1. {issue}\n"
    else:
        report += "✅ 未发现中风险问题\n"
    
    report += f"""

---

## 📝 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本 |
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return report

def main():
    """主函数"""
    root_path = r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY'
    output_dir = r'D:\ZephyrAlpha\docs\05_IMPLEMENTATION\04_OPERATIONS\audit_state'
    
    print("=" * 80)
    print("第二十三次深度审计 - Alpha因子层")
    print("=" * 80)
    print()
    
    # L1文件系统层审计
    print("1. 执行L1文件系统层审计...")
    l1_results = check_l1_file_system(root_path)
    print(f"  稀疏目录: {len(l1_results['directory_structure']['sparse_dirs'])}个")
    print(f"  空目录: {len(l1_results['directory_structure']['empty_dirs'])}个")
    print(f"  层级过深: {len(l1_results['directory_structure']['deep_dirs'])}个")
    print()
    
    # L2文档内容层审计
    print("2. 执行L2文档内容层审计...")
    l2_results = check_l2_document_content(root_path)
    print(f"  内容哈希重复: {len(l2_results['content_duplicates']['hash_duplicates'])}个")
    print(f"  标题重复: {len(l2_results['content_duplicates']['title_duplicates'])}个")
    print(f"  职责重叠: {len(l2_results['responsibility']['overlap'])}个")
    print(f"  缺少职责描述: {len(l2_results['responsibility']['missing'])}个")
    print()
    
    # L3专业标准层审计
    print("3. 执行L3专业标准层审计...")
    l3_results = check_l3_professional_standards(root_path)
    print(f"  module_id重复: {len(l3_results['module_id']['duplicates'])}个")
    print(f"  module_id缺失: {len(l3_results['module_id']['missing'])}个")
    print(f"  YAML头部缺失: {len(l3_results['yaml_header']['missing'])}个")
    print()
    
    # 生成报告
    report_path = os.path.join(output_dir, 'LAYER2_ALPHA_FACTOR_DEEP_AUDIT_REPORT_V23_20260407.md')
    generate_audit_report(l1_results, l2_results, l3_results, report_path)
    print(f"✅ 审计报告已生成: {report_path}")
    print()
    print("=" * 80)
    print("审计完成")
    print("=" * 80)

if __name__ == '__main__':
    main()
