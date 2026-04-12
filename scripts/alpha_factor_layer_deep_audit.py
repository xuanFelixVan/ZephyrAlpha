#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
Alpha因子层深度审计脚本
审计每一个文档的每一个内容
"""

import os
import re
import json
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY')
OUTPUT_DIR = Path(r'D:\ZephyrAlpha\docs\09_AUDIT\STATE')

def get_file_hash(file_path):
    """计算文件内容哈希"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    except:
        return None

def extract_yaml_metadata(content):
    """提取YAML元数据"""
    if not content.startswith('---'):
        return {}
    
    yaml_end = content.find('---', 3)
    if yaml_end < 0:
        return {}
    
    yaml_content = content[3:yaml_end]
    metadata = {}
    
    # 提取module_id
    match = re.search(r'module_id:\s*(.+)', yaml_content)
    if match:
        metadata['module_id'] = match.group(1).strip()
    
    # 提取version
    match = re.search(r'version:\s*(.+)', yaml_content)
    if match:
        metadata['version'] = match.group(1).strip()
    
    # 提取status
    match = re.search(r'status:\s*(.+)', yaml_content)
    if match:
        metadata['status'] = match.group(1).strip()
    
    # 提取responsibility
    match = re.search(r'responsibility:\s*\n((?:\s+-\s+.+\n)*)', yaml_content)
    if match:
        resp_text = match.group(1)
        responsibilities = re.findall(r'-\s+(.+)', resp_text)
        metadata['responsibility'] = responsibilities
    
    return metadata

def extract_title(content):
    """提取文档标题"""
    # 跳过YAML头部
    if content.startswith('---'):
        yaml_end = content.find('---', 3)
        if yaml_end > 0:
            content = content[yaml_end + 3:]
    
    # 查找第一个标题
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    
    return None

def extract_summary(content):
    """提取文档摘要"""
    # 跳过YAML头部
    if content.startswith('---'):
        yaml_end = content.find('---', 3)
        if yaml_end > 0:
            content = content[yaml_end + 3:]
    
    # 查找摘要块
    match = re.search(r'>\s*\*\*核心职责\*\*:\s*(.+)', content)
    if match:
        return match.group(1).strip()
    
    # 查找第一段非空内容
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('>') and not line.startswith('|') and not line.startswith('-') and not line.startswith('*'):
            if len(line) > 20:
                return line[:200]
    
    return None

def extract_all_links(content):
    """提取所有链接"""
    links = []
    # 标准链接格式
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    for match in re.finditer(pattern, content):
        links.append({
            'text': match.group(1),
            'path': match.group(2),
            'full_match': match.group(0)
        })
    return links

def check_link_validity(file_path, link_path):
    """检查链接有效性"""
    # 跳过外部链接和锚点链接
    if link_path.startswith('http') or link_path.startswith('#') or link_path.startswith('file:'):
        return True, None
    
    # 计算目标路径
    if link_path.startswith('/'):
        target_path = FACTOR_LIBRARY.parent / link_path[1:]
    else:
        target_path = file_path.parent / link_path
    
    try:
        target_path = target_path.resolve()
        if target_path.exists():
            return True, target_path
        else:
            return False, None
    except:
        return False, None

def analyze_file(file_path):
    """分析单个文件"""
    rel_path = file_path.relative_to(FACTOR_LIBRARY)
    
    result = {
        'path': str(rel_path),
        'depth': len(rel_path.parts) - 1,
        'size': 0,
        'hash': None,
        'metadata': {},
        'title': None,
        'summary': None,
        'links': [],
        'invalid_links': [],
        'issues': []
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        result['size'] = len(content)
        result['hash'] = get_file_hash(file_path)
        result['metadata'] = extract_yaml_metadata(content)
        result['title'] = extract_title(content)
        result['summary'] = extract_summary(content)
        
        # 提取链接
        links = extract_all_links(content)
        result['links'] = links
        
        # 检查链接有效性
        for link in links:
            is_valid, target = check_link_validity(file_path, link['path'])
            if not is_valid:
                result['invalid_links'].append({
                    'text': link['text'],
                    'path': link['path']
                })
        
        # L1检查：文件命名
        file_name = file_path.stem
        if 'Layer' in file_name or 'LAYER' in file_name:
            result['issues'].append({
                'level': 'L1',
                'type': '旧架构命名残留',
                'description': f'文件名包含旧架构关键词: {file_name}'
            })
        
        # L2检查：元数据完整性
        if not result['metadata'].get('module_id'):
            result['issues'].append({
                'level': 'L2',
                'type': '元数据缺失',
                'description': '缺少module_id'
            })
        
        if not result['metadata'].get('responsibility'):
            result['issues'].append({
                'level': 'L2',
                'type': '职责描述缺失',
                'description': '缺少responsibility字段'
            })
        
        # L2检查：标题
        if not result['title']:
            result['issues'].append({
                'level': 'L2',
                'type': '标题缺失',
                'description': '文档缺少标题'
            })
        
        # L2检查：无效链接
        if result['invalid_links']:
            result['issues'].append({
                'level': 'L2',
                'type': '无效链接',
                'description': f'发现{len(result["invalid_links"])}个无效链接'
            })
        
        # L3检查：命名规范
        if not re.match(r'^[A-Z0-9_]+$', file_name.upper()) and file_name.upper() not in ['INDEX', 'README', 'SITEMAP']:
            # 检查是否是小写命名
            if file_name != file_name.upper():
                result['issues'].append({
                    'level': 'L3',
                    'type': '命名不规范',
                    'description': f'文件名应使用大写: {file_name}'
                })
    
    except Exception as e:
        result['issues'].append({
            'level': 'ERROR',
            'type': '读取错误',
            'description': str(e)
        })
    
    return result

def find_duplicates(analysis_results):
    """查找重复文档"""
    print("\n" + "=" * 80)
    print("查找重复文档")
    print("=" * 80)
    
    # 按内容哈希分组
    hash_groups = defaultdict(list)
    for result in analysis_results:
        if result['hash']:
            hash_groups[result['hash']].append(result['path'])
    
    # 找出重复
    duplicates = []
    for hash_val, paths in hash_groups.items():
        if len(paths) > 1:
            duplicates.append({
                'hash': hash_val,
                'paths': paths,
                'count': len(paths)
            })
    
    print(f"\n发现重复文档组: {len(duplicates)}")
    for dup in duplicates:
        print(f"\n重复组 (内容相同):")
        for path in dup['paths']:
            print(f"  - {path}")
    
    return duplicates

def find_responsibility_overlap(analysis_results):
    """查找职责重叠"""
    print("\n" + "=" * 80)
    print("查找职责重叠")
    print("=" * 80)
    
    # 按职责关键词分组
    responsibility_groups = defaultdict(list)
    
    for result in analysis_results:
        responsibilities = result['metadata'].get('responsibility', [])
        for resp in responsibilities:
            # 提取关键词
            keywords = re.findall(r'[\u4e00-\u9fa5]+', resp)
            for keyword in keywords:
                if len(keyword) >= 2:
                    responsibility_groups[keyword].append({
                        'path': result['path'],
                        'responsibility': resp
                    })
    
    # 找出重叠
    overlaps = []
    for keyword, items in responsibility_groups.items():
        if len(items) > 1:
            overlaps.append({
                'keyword': keyword,
                'items': items,
                'count': len(items)
            })
    
    # 按数量排序
    overlaps.sort(key=lambda x: x['count'], reverse=True)
    
    print(f"\n发现职责重叠关键词: {len(overlaps)}")
    for overlap in overlaps[:10]:  # 只显示前10个
        print(f"\n关键词 '{overlap['keyword']}' 出现在 {overlap['count']} 个文档:")
        for item in overlap['items'][:5]:  # 只显示前5个
            print(f"  - {item['path']}: {item['responsibility']}")
    
    return overlaps

def find_unclear_responsibility(analysis_results):
    """查找职责不清的文档"""
    print("\n" + "=" * 80)
    print("查找职责不清的文档")
    print("=" * 80)
    
    unclear_docs = []
    
    for result in analysis_results:
        issues = []
        
        # 检查是否有职责描述
        responsibilities = result['metadata'].get('responsibility', [])
        if not responsibilities:
            issues.append('缺少职责描述')
        
        # 检查标题是否清晰
        title = result.get('title')
        if not title:
            issues.append('缺少标题')
        elif len(title) < 5:
            issues.append(f'标题过短: {title}')
        
        # 检查摘要是否清晰
        summary = result.get('summary')
        if not summary:
            issues.append('缺少摘要')
        
        # 检查是否有多个职责
        if len(responsibilities) > 3:
            issues.append(f'职责过多({len(responsibilities)}个)，可能职责不清')
        
        if issues:
            unclear_docs.append({
                'path': result['path'],
                'issues': issues,
                'responsibilities': responsibilities,
                'title': title
            })
    
    print(f"\n发现职责不清的文档: {len(unclear_docs)}")
    for doc in unclear_docs[:20]:  # 只显示前20个
        print(f"\n{doc['path']}:")
        for issue in doc['issues']:
            print(f"  - {issue}")
    
    return unclear_docs

def audit_directory_structure(analysis_results):
    """审计目录结构"""
    print("\n" + "=" * 80)
    print("L1 文件系统层审计 - 目录结构")
    print("=" * 80)
    
    issues = []
    
    # 统计目录文件数
    dir_files = defaultdict(list)
    for result in analysis_results:
        parts = Path(result['path']).parts
        if len(parts) > 1:
            dir_path = str(Path(*parts[:-1]))
            dir_files[dir_path].append(result['path'])
    
    # 检查稀疏目录
    sparse_dirs = []
    for dir_path, files in dir_files.items():
        if len(files) < 3:
            sparse_dirs.append({
                'path': dir_path,
                'file_count': len(files),
                'files': files
            })
    
    if sparse_dirs:
        print(f"\n发现稀疏目录（文件数<3）: {len(sparse_dirs)}")
        for dir_info in sparse_dirs:
            print(f"  - {dir_info['path']}: {dir_info['file_count']}个文件")
    
    # 检查深层目录
    deep_dirs = []
    for result in analysis_results:
        if result['depth'] >= 4:
            deep_dirs.append(result['path'])
    
    if deep_dirs:
        print(f"\n发现深层目录（深度≥4）: {len(deep_dirs)}")
        for path in deep_dirs[:10]:
            print(f"  - {path}")
    
    return {
        'sparse_dirs': sparse_dirs,
        'deep_dirs': deep_dirs
    }

def audit_index_completeness(analysis_results):
    """审计索引完备性"""
    print("\n" + "=" * 80)
    print("L2 文档内容层审计 - 索引完备性")
    print("=" * 80)
    
    issues = []
    
    # 检查各目录是否有INDEX.md
    dir_has_index = defaultdict(bool)
    for result in analysis_results:
        parts = Path(result['path']).parts
        if len(parts) > 1:
            dir_path = str(Path(*parts[:-1]))
            if parts[-1].upper() == 'INDEX.MD':
                dir_has_index[dir_path] = True
    
    # 找出缺少INDEX的目录
    missing_index_dirs = []
    for result in analysis_results:
        parts = Path(result['path']).parts
        if len(parts) > 1:
            dir_path = str(Path(*parts[:-1]))
            if not dir_has_index[dir_path] and dir_path not in [d['path'] for d in missing_index_dirs]:
                missing_index_dirs.append({
                    'path': dir_path,
                    'reason': '缺少INDEX.md'
                })
    
    if missing_index_dirs:
        print(f"\n发现缺少INDEX的目录: {len(missing_index_dirs)}")
        for dir_info in missing_index_dirs[:10]:
            print(f"  - {dir_info['path']}")
    
    return {
        'missing_index_dirs': missing_index_dirs
    }

def audit_module_id_uniqueness(analysis_results):
    """审计module_id唯一性"""
    print("\n" + "=" * 80)
    print("L3 专业标准层审计 - module_id唯一性")
    print("=" * 80)
    
    # 按module_id分组
    module_id_groups = defaultdict(list)
    for result in analysis_results:
        module_id = result['metadata'].get('module_id')
        if module_id:
            module_id_groups[module_id].append(result['path'])
    
    # 找出重复
    duplicates = []
    for module_id, paths in module_id_groups.items():
        if len(paths) > 1:
            duplicates.append({
                'module_id': module_id,
                'paths': paths,
                'count': len(paths)
            })
    
    if duplicates:
        print(f"\n发现重复的module_id: {len(duplicates)}")
        for dup in duplicates:
            print(f"\nmodule_id '{dup['module_id']}' 重复 {dup['count']} 次:")
            for path in dup['paths']:
                print(f"  - {path}")
    else:
        print("\n无重复的module_id")
    
    return duplicates

def generate_report(analysis_results, duplicates, overlaps, unclear_docs, dir_issues, index_issues, module_id_duplicates):
    """生成审计报告"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = OUTPUT_DIR / f'ALPHA_FACTOR_LAYER_DEEP_AUDIT_REPORT_{timestamp}.md'
    
    # 统计问题
    total_issues = sum(len(r['issues']) for r in analysis_results)
    
    # 按级别统计
    l1_issues = sum(1 for r in analysis_results for i in r['issues'] if i['level'] == 'L1')
    l2_issues = sum(1 for r in analysis_results for i in r['issues'] if i['level'] == 'L2')
    l3_issues = sum(1 for r in analysis_results for i in r['issues'] if i['level'] == 'L3')
    
    report_content = f"""---
module_id: ALPHA_FACTOR_LAYER_DEEP_AUDIT_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: 审计报告
applicable_scope: Alpha因子层深度审计
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# Alpha因子层深度审计报告

> **核心职责**: 记录Alpha因子层深度审计的结果
> **职责边界**: 
> - [OK] 本文档负责：审计记录、问题统计、改进建议
> - [NO] 本文档不负责：问题修复、后续审计执行

---

## 审计概要

**审计时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**审计范围**: Alpha因子层所有文档  
**审计方法**: 三层审计（L1-L3）  
**审计结论**: 发现问题并识别重复和职责不清的文档

---

## 审计统计

| 统计项 | 数量 | 说明 |
|--------|------|------|
| **总文档数** | {len(analysis_results)} | Alpha因子层所有文档 |
| **总问题数** | {total_issues} | 所有级别问题总和 |
| **L1问题数** | {l1_issues} | 文件系统层问题 |
| **L2问题数** | {l2_issues} | 文档内容层问题 |
| **L3问题数** | {l3_issues} | 专业标准层问题 |
| **重复文档组** | {len(duplicates)} | 内容完全相同的文档 |
| **职责重叠关键词** | {len(overlaps)} | 多个文档共享的职责关键词 |
| **职责不清文档** | {len(unclear_docs)} | 职责描述不清晰的文档 |

---

## L1 文件系统层问题

### 1.1 目录结构问题

"""
    
    # 稀疏目录
    if dir_issues['sparse_dirs']:
        report_content += f"**稀疏目录（文件数<3）**: {len(dir_issues['sparse_dirs'])}个\n\n"
        for dir_info in dir_issues['sparse_dirs'][:20]:
            report_content += f"- {dir_info['path']}: {dir_info['file_count']}个文件\n"
    else:
        report_content += "无稀疏目录问题。\n"
    
    report_content += f"""

### 1.2 深层目录问题

"""
    
    # 深层目录
    if dir_issues['deep_dirs']:
        report_content += f"**深层目录（深度≥4）**: {len(dir_issues['deep_dirs'])}个\n\n"
        for path in dir_issues['deep_dirs'][:20]:
            report_content += f"- {path}\n"
    else:
        report_content += "无深层目录问题。\n"
    
    report_content += f"""

---

## L2 文档内容层问题

### 2.1 索引完备性问题

"""
    
    # 缺少INDEX的目录
    if index_issues['missing_index_dirs']:
        report_content += f"**缺少INDEX的目录**: {len(index_issues['missing_index_dirs'])}个\n\n"
        for dir_info in index_issues['missing_index_dirs'][:20]:
            report_content += f"- {dir_info['path']}\n"
    else:
        report_content += "所有目录都有INDEX文件。\n"
    
    report_content += f"""

### 2.2 职责不清文档

**发现职责不清的文档**: {len(unclear_docs)}个

"""
    
    for doc in unclear_docs[:30]:
        report_content += f"#### {doc['path']}\n\n"
        for issue in doc['issues']:
            report_content += f"- {issue}\n"
        if doc['responsibilities']:
            report_content += f"\n**当前职责**:\n"
            for resp in doc['responsibilities']:
                report_content += f"- {resp}\n"
        report_content += "\n"
    
    report_content += f"""

---

## L3 专业标准层问题

### 3.1 module_id重复问题

"""
    
    if module_id_duplicates:
        report_content += f"**发现重复的module_id**: {len(module_id_duplicates)}个\n\n"
        for dup in module_id_duplicates:
            report_content += f"#### module_id: {dup['module_id']}\n\n"
            report_content += f"重复次数: {dup['count']}\n\n"
            for path in dup['paths']:
                report_content += f"- {path}\n"
            report_content += "\n"
    else:
        report_content += "无重复的module_id。\n"
    
    report_content += f"""

---

## 重复文档分析

**发现重复文档组**: {len(duplicates)}组

"""
    
    for dup in duplicates:
        report_content += f"### 重复组\n\n"
        report_content += f"**内容哈希**: {dup['hash'][:16]}...\n\n"
        report_content += f"**重复文档**:\n"
        for path in dup['paths']:
            report_content += f"- {path}\n"
        report_content += "\n"
    
    report_content += f"""

---

## 职责重叠分析

**发现职责重叠关键词**: {len(overlaps)}个

"""
    
    for overlap in overlaps[:20]:
        report_content += f"### 关键词: {overlap['keyword']}\n\n"
        report_content += f"**出现次数**: {overlap['count']}\n\n"
        report_content += f"**相关文档**:\n"
        for item in overlap['items'][:10]:
            report_content += f"- {item['path']}: {item['responsibility']}\n"
        report_content += "\n"
    
    report_content += f"""

---

## 改进建议

### 立即行动

1. [ ] 处理重复文档（合并或删除）
2. [ ] 补充缺失的INDEX文件
3. [ ] 修复重复的module_id

### 短期改进

1. [ ] 整合稀疏目录
2. [ ] 明确职责不清文档的职责
3. [ ] 优化目录结构

### 持续改进

1. [ ] 建立职责审查机制
2. [ ] 定期执行深度审计
3. [ ] 持续优化文档质量

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本，Alpha因子层深度审计报告 | 首席文档架构师 |
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n报告已生成: {report_path}")
    return report_path

def main():
    """主函数"""
    print("=" * 80)
    print("Alpha因子层深度审计")
    print("=" * 80)
    print(f"审计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"审计范围: {FACTOR_LIBRARY}")
    print("=" * 80)
    
    # 扫描所有文档
    print("\n[阶段1] 扫描所有文档...")
    all_files = list(FACTOR_LIBRARY.rglob('*.md'))
    print(f"发现文档: {len(all_files)}个")
    
    # 分析每个文档
    print("\n[阶段2] 分析每个文档...")
    analysis_results = []
    for i, file_path in enumerate(all_files, 1):
        if i % 20 == 0:
            print(f"  进度: {i}/{len(all_files)}")
        result = analyze_file(file_path)
        analysis_results.append(result)
    
    # L1审计：目录结构
    print("\n[阶段3] L1文件系统层审计...")
    dir_issues = audit_directory_structure(analysis_results)
    
    # L2审计：索引完备性
    print("\n[阶段4] L2文档内容层审计...")
    index_issues = audit_index_completeness(analysis_results)
    
    # L3审计：module_id唯一性
    print("\n[阶段5] L3专业标准层审计...")
    module_id_duplicates = audit_module_id_uniqueness(analysis_results)
    
    # 查找重复文档
    print("\n[阶段6] 查找重复文档...")
    duplicates = find_duplicates(analysis_results)
    
    # 查找职责重叠
    print("\n[阶段7] 查找职责重叠...")
    overlaps = find_responsibility_overlap(analysis_results)
    
    # 查找职责不清的文档
    print("\n[阶段8] 查找职责不清的文档...")
    unclear_docs = find_unclear_responsibility(analysis_results)
    
    # 生成报告
    print("\n[阶段9] 生成审计报告...")
    report_path = generate_report(analysis_results, duplicates, overlaps, unclear_docs, dir_issues, index_issues, module_id_duplicates)
    
    # 保存详细数据
    data_path = OUTPUT_DIR / f'ALPHA_FACTOR_LAYER_DEEP_AUDIT_DATA_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump({
            'analysis_results': analysis_results,
            'duplicates': duplicates,
            'overlaps': overlaps,
            'unclear_docs': unclear_docs,
            'dir_issues': dir_issues,
            'index_issues': index_issues,
            'module_id_duplicates': module_id_duplicates
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n详细数据已保存: {data_path}")
    
    print("\n" + "=" * 80)
    print("审计完成！")
    print("=" * 80)
    print(f"总文档数: {len(analysis_results)}")
    print(f"总问题数: {sum(len(r['issues']) for r in analysis_results)}")
    print(f"重复文档组: {len(duplicates)}")
    print(f"职责不清文档: {len(unclear_docs)}")
    print(f"报告位置: {report_path}")

if __name__ == '__main__':
    main()
