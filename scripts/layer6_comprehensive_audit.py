import os
import re
import hashlib
import json
from datetime import datetime
from collections import defaultdict

blueprints_dir = r'd:\ZephyrAlpha\docs\05_IMPLEMENTATION\06_CONSTRUCTION_DOCS\01_BLUEPRINTS'
audit_state_dir = r'd:\ZephyrAlpha\docs\05_IMPLEMENTATION\04_OPERATIONS\audit_state'

def get_file_hash(file_path):
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    yaml_match = re.search(r'^---\s*[\r\n]+(.*?)[\r\n]+---', content, re.DOTALL)
    if yaml_match:
        core_content = content[yaml_match.end():]
    else:
        core_content = content
    return hashlib.md5(core_content.encode()).hexdigest()

def parse_yaml_header(content):
    yaml_match = re.search(r'^---\s*[\r\n]+(.*?)[\r\n]+---', content, re.DOTALL)
    if not yaml_match:
        return None
    
    yaml_content = yaml_match.group(1)
    yaml_data = {}
    
    lines = yaml_content.split('\n')
    current_key = None
    current_list = []
    
    for line in lines:
        if ':' in line and not line.startswith(' '):
            if current_key and current_list:
                yaml_data[current_key] = current_list
                current_list = []
            key, value = line.split(':', 1)
            current_key = key.strip()
            value = value.strip()
            if value:
                yaml_data[current_key] = value
        elif line.strip().startswith('- '):
            value = line.strip()[2:].strip()
            current_list.append(value)
    
    if current_key and current_list:
        yaml_data[current_key] = current_list
    
    return yaml_data

def audit_l1_file_system():
    issues = []
    
    if not os.path.exists(blueprints_dir):
        issues.append({'type': 'L1-目录不存在', 'severity': 'P0', 'path': blueprints_dir})
        return issues
    
    files = [f for f in os.listdir(blueprints_dir) if f.endswith('.md')]
    
    for file in files:
        file_path = os.path.join(blueprints_dir, file)
        
        if 'Layer 0' in file or 'Layer 1' in file or 'Layer 2' in file or 'Layer 3' in file or 'Layer 4' in file:
            issues.append({'type': 'L1-旧架构命名残留', 'severity': 'P2', 'file': file})
        
        if ' ' in file:
            issues.append({'type': 'L1-文件名包含空格', 'severity': 'P1', 'file': file})
        
        if not re.match(r'^[A-Z_0-9]+_BLUEPRINT\.md$', file) and file != 'INDEX.md':
            issues.append({'type': 'L1-命名不规范', 'severity': 'P2', 'file': file})
    
    return issues

def audit_l2_document_content():
    issues = []
    responsibility_map = defaultdict(list)
    
    files = [f for f in os.listdir(blueprints_dir) if f.endswith('.md') and f != 'INDEX.md']
    
    for file in files:
        file_path = os.path.join(blueprints_dir, file)
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        yaml_data = parse_yaml_header(content)
        
        if not yaml_data:
            issues.append({'type': 'L2-缺少YAML头部', 'severity': 'P0', 'file': file})
            continue
        
        required_fields = ['module_id', 'responsibility', 'layer', 'owner']
        for field in required_fields:
            if field not in yaml_data:
                issues.append({'type': f'L2-YAML缺少{field}', 'severity': 'P1', 'file': file})
        
        if 'responsibility' in yaml_data:
            resp_list = yaml_data['responsibility']
            if isinstance(resp_list, list):
                if len(resp_list) < 2:
                    issues.append({'type': 'L2-responsibility项不足', 'severity': 'P0', 'file': file, 'count': len(resp_list)})
                
                for resp in resp_list:
                    responsibility_map[resp].append(file)
        
        if not re.search(r'职责边界|本文档负责|本文档不负责', content):
            issues.append({'type': 'L2-缺少职责边界', 'severity': 'P1', 'file': file})
        
        if not re.search(r'##\s*\d*\.?\s*变更历史|##\s*\d*\.?\s*版本管理', content):
            issues.append({'type': 'L2-缺少变更历史', 'severity': 'P2', 'file': file})
        
        core_match = re.search(r'##\s*核心定位\s*\n(.+?)(?=\n##|\n#|$)', content, re.DOTALL)
        if core_match:
            core_text = core_match.group(1).strip()
            if len(core_text) < 50:
                issues.append({'type': 'L2-核心定位过短', 'severity': 'P2', 'file': file, 'length': len(core_text)})
    
    for resp, files_list in responsibility_map.items():
        if len(files_list) > 1:
            issues.append({'type': 'L2-职责重叠', 'severity': 'P1', 'responsibility': resp, 'files': files_list})
    
    return issues

def audit_l3_professional_standards():
    issues = []
    module_ids = {}
    
    files = [f for f in os.listdir(blueprints_dir) if f.endswith('.md') and f != 'INDEX.md']
    
    for file in files:
        file_path = os.path.join(blueprints_dir, file)
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        yaml_data = parse_yaml_header(content)
        if not yaml_data:
            continue
        
        if 'module_id' in yaml_data:
            module_id = yaml_data['module_id']
            if module_id in module_ids:
                issues.append({'type': 'L3-module_id重复', 'severity': 'P0', 'module_id': module_id, 'files': [module_ids[module_id], file]})
            else:
                module_ids[module_id] = file
        
        if 'standard_type' not in yaml_data:
            issues.append({'type': 'L3-缺少standard_type', 'severity': 'P2', 'file': file})
        
        if 'compliance_level' not in yaml_data:
            issues.append({'type': 'L3-缺少compliance_level', 'severity': 'P2', 'file': file})
    
    return issues

def check_duplicates():
    duplicates = []
    file_hashes = {}
    
    files = [f for f in os.listdir(blueprints_dir) if f.endswith('.md') and f != 'INDEX.md']
    
    for file in files:
        file_path = os.path.join(blueprints_dir, file)
        try:
            file_hash = get_file_hash(file_path)
            if file_hash in file_hashes:
                duplicates.append({'type': '重复文档', 'files': [file_hashes[file_hash], file], 'hash': file_hash})
            else:
                file_hashes[file_hash] = file
        except Exception as e:
            pass
    
    return duplicates

def check_responsibility_clarity():
    issues = []
    
    files = [f for f in os.listdir(blueprints_dir) if f.endswith('.md') and f != 'INDEX.md']
    
    for file in files:
        file_path = os.path.join(blueprints_dir, file)
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        yaml_data = parse_yaml_header(content)
        if not yaml_data or 'responsibility' not in yaml_data:
            continue
        
        resp_list = yaml_data['responsibility']
        if isinstance(resp_list, list):
            generic_terms = ['系统架构蓝图设计与实施指导', '模块功能实现', '性能优化', '质量保证']
            for resp in resp_list:
                if resp in generic_terms:
                    issues.append({'type': '职责描述过于通用', 'severity': 'P2', 'file': file, 'responsibility': resp})
    
    return issues

def generate_audit_report(l1_issues, l2_issues, l3_issues, duplicates, clarity_issues):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(audit_state_dir, f'LAYER6_COMPREHENSIVE_AUDIT_REPORT_{timestamp}.md')
    
    all_issues = l1_issues + l2_issues + l3_issues + duplicates + clarity_issues
    
    p0_count = len([i for i in all_issues if i.get('severity') == 'P0'])
    p1_count = len([i for i in all_issues if i.get('severity') == 'P1'])
    p2_count = len([i for i in all_issues if i.get('severity') == 'P2'])
    
    files = [f for f in os.listdir(blueprints_dir) if f.endswith('.md')]
    total_files = len(files)
    problem_files = len(set([i.get('file') for i in all_issues if 'file' in i]))
    compliant_files = total_files - problem_files
    compliance_rate = (compliant_files / total_files * 100) if total_files > 0 else 0
    
    report = f'''# Layer 6 组合优化层全面深度审计报告

## 1. 审计概要

| 项目 | 内容 |
|------|------|
| **审计目标** | Layer 6 组合优化层所有文档 |
| **审计范围** | {blueprints_dir} |
| **审计时间** | {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} |
| **文档总数** | {total_files} |
| **问题总数** | {len(all_issues)} |
| **合规率** | {compliance_rate:.1f}% |

## 2. 审计结果统计

| 指标 | 数量 |
|------|------|
| 合规文档 | {compliant_files} |
| 问题文档 | {problem_files} |
| P0问题 | {p0_count} |
| P1问题 | {p1_count} |
| P2问题 | {p2_count} |

## 3. L1文件系统层问题

| 问题类型 | 数量 | 严重程度 |
|----------|------|----------|
'''
    
    l1_types = defaultdict(int)
    for issue in l1_issues:
        l1_types[issue['type']] += 1
    
    for issue_type, count in l1_types.items():
        severity = 'P2'
        if 'P0' in issue_type or '不存在' in issue_type:
            severity = 'P0'
        elif 'P1' in issue_type or '空格' in issue_type:
            severity = 'P1'
        report += f"| {issue_type} | {count} | {severity} |\n"
    
    report += f'''
## 4. L2文档内容层问题

| 问题类型 | 数量 | 严重程度 |
|----------|------|----------|
'''
    
    l2_types = defaultdict(int)
    for issue in l2_issues:
        l2_types[issue['type']] += 1
    
    for issue_type, count in l2_types.items():
        severity = 'P2'
        if 'P0' in issue_type or 'YAML头部' in issue_type or 'responsibility项不足' in issue_type:
            severity = 'P0'
        elif 'P1' in issue_type or '职责边界' in issue_type or '职责重叠' in issue_type:
            severity = 'P1'
        report += f"| {issue_type} | {count} | {severity} |\n"
    
    report += f'''
## 5. L3专业标准层问题

| 问题类型 | 数量 | 严重程度 |
|----------|------|----------|
'''
    
    l3_types = defaultdict(int)
    for issue in l3_issues:
        l3_types[issue['type']] += 1
    
    for issue_type, count in l3_types.items():
        severity = 'P2'
        if 'P0' in issue_type or 'module_id重复' in issue_type:
            severity = 'P0'
        elif 'P1' in issue_type:
            severity = 'P1'
        report += f"| {issue_type} | {count} | {severity} |\n"
    
    if duplicates:
        report += f'''
## 6. 重复文档检测

| 文件对 | 相似度 |
|--------|--------|
'''
        for dup in duplicates:
            report += f"| {dup['files'][0]} <-> {dup['files'][1]} | 100% |\n"
    else:
        report += f'''
## 6. 重复文档检测

✓ 无重复文档
'''
    
    if clarity_issues:
        report += f'''
## 7. 职责清晰度问题

| 文件 | 问题描述 |
|------|----------|
'''
        for issue in clarity_issues:
            report += f"| {issue['file']} | {issue['responsibility']} (过于通用) |\n"
    else:
        report += f'''
## 7. 职责清晰度问题

✓ 职责描述清晰
'''
    
    report += f'''
## 8. 问题详情

### 8.1 P0问题 (立即修复)

'''
    p0_issues = [i for i in all_issues if i.get('severity') == 'P0']
    if p0_issues:
        for issue in p0_issues[:20]:
            if 'file' in issue:
                report += f"- {issue['type']}: {issue['file']}\n"
            else:
                report += f"- {issue['type']}\n"
    else:
        report += "✓ 无P0问题\n"
    
    report += f'''
### 8.2 P1问题 (短期改进)

'''
    p1_issues = [i for i in all_issues if i.get('severity') == 'P1']
    if p1_issues:
        for issue in p1_issues[:20]:
            if 'file' in issue:
                report += f"- {issue['type']}: {issue['file']}\n"
            elif 'responsibility' in issue:
                report += f"- {issue['type']}: {issue['responsibility']} ({len(issue['files'])}个文件)\n"
            else:
                report += f"- {issue['type']}\n"
    else:
        report += "✓ 无P1问题\n"
    
    report += f'''
### 8.3 P2问题 (长期优化)

'''
    p2_issues = [i for i in all_issues if i.get('severity') == 'P2']
    if p2_issues:
        for issue in p2_issues[:20]:
            if 'file' in issue:
                report += f"- {issue['type']}: {issue['file']}\n"
            else:
                report += f"- {issue['type']}\n"
    else:
        report += "✓ 无P2问题\n"
    
    report += f'''
## 9. 改进建议

### 9.1 立即修复项 (P0)
- 修复YAML头部缺失字段
- 修复responsibility项不足问题

### 9.2 短期改进项 (P1)
- 添加职责边界定义
- 解决职责重叠问题

### 9.3 长期优化项 (P2)
- 扩展核心定位内容
- 细化职责描述

---
**审计完成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
'''
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return report_path, all_issues

print('='*80)
print('Layer 6 组合优化层全面深度审计')
print('='*80)
print(f'审计时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print(f'审计目录: {blueprints_dir}')
print()

print('[阶段1] L1 文件系统层审计...')
l1_issues = audit_l1_file_system()
print(f'  发现问题: {len(l1_issues)}个')

print('[阶段2] L2 文档内容层审计...')
l2_issues = audit_l2_document_content()
print(f'  发现问题: {len(l2_issues)}个')

print('[阶段3] L3 专业标准层审计...')
l3_issues = audit_l3_professional_standards()
print(f'  发现问题: {len(l3_issues)}个')

print('[阶段4] 检查重复文档...')
duplicates = check_duplicates()
print(f'  发现重复: {len(duplicates)}对')

print('[阶段5] 检查职责清晰度...')
clarity_issues = check_responsibility_clarity()
print(f'  发现问题: {len(clarity_issues)}个')

print('[阶段6] 生成审计报告...')
report_path, all_issues = generate_audit_report(l1_issues, l2_issues, l3_issues, duplicates, clarity_issues)
print(f'  报告路径: {report_path}')

print()
print('='*80)
print('审计完成!')
print('='*80)

p0_count = len([i for i in all_issues if i.get('severity') == 'P0'])
p1_count = len([i for i in all_issues if i.get('severity') == 'P1'])
p2_count = len([i for i in all_issues if i.get('severity') == 'P2'])

print(f'问题总数: {len(all_issues)}')
print(f'  P0问题: {p0_count}个')
print(f'  P1问题: {p1_count}个')
print(f'  P2问题: {p2_count}个')
