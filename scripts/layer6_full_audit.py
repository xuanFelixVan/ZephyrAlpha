import os
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import hashlib

blueprints_dir = r'd:\ZephyrAlpha\docs\05_IMPLEMENTATION\06_CONSTRUCTION_DOCS\01_BLUEPRINTS'
output_dir = r'd:\ZephyrAlpha\docs\05_IMPLEMENTATION\04_OPERATIONS\audit_state'

required_yaml_fields = [
    'module_id', 'version', 'status', 'created_date', 'last_updated', 
    'owner', 'standard_type', 'compliance_level', 'layer', 'responsibility'
]

all_docs = []
issues = defaultdict(list)
responsibility_map = defaultdict(list)
content_hashes = defaultdict(list)
module_ids = defaultdict(list)
layer_classification = defaultdict(list)

print('='*80)
print('Layer 6 组合优化层全面深度审计')
print('='*80)
print(f'审计时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print(f'审计目录: {blueprints_dir}')
print()

files = [f for f in os.listdir(blueprints_dir) if f.endswith('.md') and f != 'INDEX.md']

print(f'扫描文档总数: {len(files)}')
print()

for file in files:
    file_path = os.path.join(blueprints_dir, file)
    
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
    except Exception as e:
        issues['文件读取错误'].append({'file': file, 'error': str(e)})
        continue
    
    doc_info = {
        'file': file,
        'path': file_path,
        'content': content,
        'issues': []
    }
    
    yaml_match = re.search(r'^---\s*[\r\n]+(.*?)[\r\n]+---', content, re.DOTALL)
    
    if not yaml_match:
        issues['缺少YAML头部'].append(file)
        doc_info['yaml'] = {}
        all_docs.append(doc_info)
        continue
    
    yaml_content = yaml_match.group(1)
    
    module_id_match = re.search(r'module_id:\s*(\S+)', yaml_content)
    module_id = module_id_match.group(1) if module_id_match else 'MISSING'
    
    layer_match = re.search(r'layer:\s*(.+?)(?:\n|$)', yaml_content)
    layer = layer_match.group(1).strip() if layer_match else 'MISSING'
    
    resp_match = re.search(r'responsibility:\s*([\s\S]*?)(?=\n\w+:|$)', yaml_content)
    if resp_match:
        resp_text = resp_match.group(1)
        resp_items = re.findall(r'-\s*(.+?)(?:\n|$)', resp_text)
        resp_items = [item.strip() for item in resp_items if item.strip()]
    else:
        resp_items = []
    
    doc_info['yaml'] = {
        'module_id': module_id,
        'layer': layer,
        'responsibility': resp_items
    }
    
    if module_id != 'MISSING':
        module_ids[module_id].append(file)
    
    if layer != 'MISSING':
        layer_classification[layer].append(file)
    
    for resp in resp_items:
        responsibility_map[resp].append(file)
    
    core_content = re.sub(r'^---[\s\S]*?---', '', content)
    core_content = re.sub(r'\s+', ' ', core_content).strip()
    content_hash = hashlib.md5(core_content.encode()).hexdigest()[:16]
    content_hashes[content_hash].append(file)
    
    for field in required_yaml_fields:
        if field not in yaml_content:
            issues[f'YAML缺少{field}'].append(file)
            doc_info['issues'].append(f'YAML缺少{field}')
    
    if len(resp_items) < 2:
        issues['responsibility项不足'].append({'file': file, 'count': len(resp_items)})
        doc_info['issues'].append(f'responsibility项不足({len(resp_items)}个)')
    
    boundary_patterns = [
        r'>\s*\*\*职责边界\*\*',
        r'职责边界.*负责',
        r'本文档负责',
        r'本文档不负责'
    ]
    has_boundary = any(re.search(p, content) for p in boundary_patterns)
    if not has_boundary:
        issues['缺少职责边界'].append(file)
        doc_info['issues'].append('缺少职责边界')
    
    core_match = re.search(r'##\s*核心定位\s*\n(.+?)(?=\n##|\Z)', content, re.DOTALL)
    if core_match:
        core_text = core_match.group(1).strip()
        if len(core_text) < 50:
            issues['核心定位过短'].append({'file': file, 'length': len(core_text)})
            doc_info['issues'].append(f'核心定位过短({len(core_text)}字符)')
    else:
        issues['缺少核心定位'].append(file)
        doc_info['issues'].append('缺少核心定位')
    
    change_history_patterns = [
        r'##\s*\d*\.?\s*变更历史',
        r'##\s*\d*\.?\s*版本管理',
        r'\|\s*v\d+\.\d+\.\d+'
    ]
    has_history = any(re.search(p, content) for p in change_history_patterns)
    if not has_history:
        issues['缺少变更历史'].append(file)
        doc_info['issues'].append('缺少变更历史')
    
    garbled_patterns = [
        r'å',
        r'æ',
        r'\\x8d',
        r'\ufffd',
        r'？\*',
        r'？\|',
    ]
    for pattern in garbled_patterns:
        if re.search(pattern, content):
            issues['内容包含乱码'].append({'file': file, 'pattern': pattern})
            doc_info['issues'].append(f'内容包含乱码({pattern})')
            break
    
    all_docs.append(doc_info)

print('='*80)
print('职责重叠分析')
print('='*80)

overlap_found = False
for resp, files_list in responsibility_map.items():
    if len(files_list) > 1:
        overlap_found = True
        issues['职责重叠'].append({
            'responsibility': resp,
            'files': files_list
        })
        print(f'\n⚠️ 职责重叠: "{resp}"')
        for f in files_list:
            print(f'   - {f}')

if not overlap_found:
    print('✓ 无职责重叠')

print()
print('='*80)
print('重复文档分析')
print('='*80)

duplicate_found = False
for hash_val, files_list in content_hashes.items():
    if len(files_list) > 1:
        duplicate_found = True
        issues['内容重复'].append({
            'hash': hash_val,
            'files': files_list
        })
        print(f'\n⚠️ 内容重复 (hash: {hash_val}):')
        for f in files_list:
            print(f'   - {f}')

if not duplicate_found:
    print('✓ 无重复文档')

print()
print('='*80)
print('module_id唯一性检查')
print('='*80)

dup_module_found = False
for mid, files_list in module_ids.items():
    if len(files_list) > 1:
        dup_module_found = True
        issues['module_id重复'].append({
            'module_id': mid,
            'files': files_list
        })
        print(f'\n⚠️ module_id重复: {mid}')
        for f in files_list:
            print(f'   - {f}')

if not dup_module_found:
    print('✓ module_id唯一')

print()
print('='*80)
print('Layer分类统计')
print('='*80)

for layer, files_list in sorted(layer_classification.items()):
    print(f'{layer}: {len(files_list)}个文档')

print()
print('='*80)
print('问题汇总')
print('='*80)

total_issues = 0
for issue_type, issue_list in issues.items():
    if issue_list:
        print(f'\n{issue_type} ({len(issue_list)}个):')
        for item in issue_list[:5]:
            if isinstance(item, dict):
                print(f'  - {item}')
            else:
                print(f'  - {item}')
        if len(issue_list) > 5:
            print(f'  ... 还有{len(issue_list)-5}个')
        total_issues += len(issue_list)

print()
print('='*80)
print('审计结论')
print('='*80)

total_docs = len(all_docs)
docs_with_issues = len([d for d in all_docs if d['issues']])
docs_clean = total_docs - docs_with_issues
compliance_rate = (docs_clean / total_docs * 100) if total_docs > 0 else 0

print(f'审计文档总数: {total_docs}')
print(f'合规文档数: {docs_clean}')
print(f'问题文档数: {docs_with_issues}')
print(f'问题总数: {total_issues}')
print(f'合规率: {compliance_rate:.1f}%')

if compliance_rate >= 95:
    print('\n[OK] 文档质量优秀')
elif compliance_rate >= 80:
    print('\n[WARNING] 文档质量良好，需要改进')
else:
    print('\n[ERROR] 文档质量需要大幅改进')

report_path = os.path.join(output_dir, f'LAYER6_FULL_AUDIT_REPORT_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(f'''# Layer 6 组合优化层全面深度审计报告

## 1. 审计概要

| 项目 | 内容 |
|------|------|
| **审计目标** | Layer 6 组合优化层所有文档 |
| **审计范围** | {blueprints_dir} |
| **审计时间** | {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} |
| **文档总数** | {total_docs} |
| **问题总数** | {total_issues} |
| **合规率** | {compliance_rate:.1f}% |

## 2. 审计结果统计

| 指标 | 数量 |
|------|------|
| 合规文档 | {docs_clean} |
| 问题文档 | {docs_with_issues} |

## 3. Layer分类统计

| Layer | 文档数 |
|-------|--------|
''')
    for layer, files_list in sorted(layer_classification.items()):
        f.write(f'| {layer} | {len(files_list)} |\n')
    
    f.write('''
## 4. 问题详情

''')
    for issue_type, issue_list in issues.items():
        if issue_list:
            f.write(f'### {issue_type} ({len(issue_list)}个)\n\n')
            for item in issue_list:
                if isinstance(item, dict):
                    f.write(f'- {item}\n')
                else:
                    f.write(f'- {item}\n')
            f.write('\n')
    
    f.write('''
## 5. 改进建议

### 5.1 立即修复项 (P0)
- 修复YAML头部缺失字段
- 修复内容乱码问题

### 5.2 短期改进项 (P1)
- 添加职责边界定义
- 添加变更历史

### 5.3 长期优化项 (P2)
- 扩展核心定位内容
- 解决职责重叠问题

---
''')

print(f'\n审计报告已生成: {report_path}')
