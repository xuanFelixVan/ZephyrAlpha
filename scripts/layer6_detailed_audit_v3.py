import os
import re
from pathlib import Path
from collections import defaultdict

blueprints_dir = r'd:\ZephyrAlpha\docs\05_IMPLEMENTATION\06_CONSTRUCTION_DOCS\01_BLUEPRINTS'

required_yaml_fields = [
    'module_id', 'version', 'status', 'created_date', 'last_updated', 
    'owner', 'standard_type', 'compliance_level', 'layer', 'responsibility'
]

layer6_docs = []
issues = defaultdict(list)

for file in os.listdir(blueprints_dir):
    if file.endswith('.md') and 'BLUEPRINT' in file:
        file_path = os.path.join(blueprints_dir, file)
        
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 检查Layer 6或5.2组合优化
        layer_match = re.search(r'layer:\s*Layer\s*(5\.2|6|组合优化)', content, re.IGNORECASE)
        if not layer_match:
            continue
        
        # 更灵活的YAML匹配（处理BOM和各种换行符）
        yaml_match = re.search(r'^---\s*[\r\n]+(.*?)[\r\n]+---', content, re.DOTALL)
        
        if not yaml_match:
            issues['missing_yaml'].append(file)
            continue
        
        yaml_content = yaml_match.group(1)
        
        missing_fields = []
        for field in required_yaml_fields:
            if field not in yaml_content:
                missing_fields.append(field)
        
        if missing_fields:
            issues['missing_fields'].append({
                'file': file,
                'fields': missing_fields
            })
        
        module_id_match = re.search(r'module_id:\s*(\S+)', yaml_content)
        module_id = module_id_match.group(1) if module_id_match else 'MISSING'
        
        if module_id == 'MISSING':
            issues['missing_module_id'].append(file)
        
        if module_id.endswith('_BLUEPRINT') or '_BLUEPRINT_' in module_id:
            issues['invalid_module_id'].append({
                'file': file,
                'module_id': module_id
            })
        
        resp_match = re.search(r'responsibility:\s*[\r\n]+((?:\s+-\s+.+[\r\n]?)+)', yaml_content)
        if resp_match:
            resp_text = resp_match.group(1)
            resp_items = re.findall(r'-\s+(.+)', resp_text)
            resp_items = [item.strip() for item in resp_items if item.strip()]
            
            if len(resp_items) < 2:
                issues['insufficient_responsibilities'].append({
                    'file': file,
                    'count': len(resp_items),
                    'items': resp_items
                })
        else:
            issues['missing_responsibility'].append(file)
        
        # 检查职责边界（使用多种模式）
        boundary_patterns = [
            r'>\s*\*\*职责边界\*\*:',
            r'>\s*\*\*职责边界\*\*：',
            r'职责边界.*负责'
        ]
        has_boundary = False
        for pattern in boundary_patterns:
            if re.search(pattern, content):
                has_boundary = True
                break
        
        if not has_boundary:
            issues['missing_boundary'].append(file)
        
        layer6_docs.append({
            'file': file,
            'module_id': module_id,
            'missing_fields': missing_fields
        })

print('='*80)
print('Layer 6 组合优化层深度审计报告')
print('='*80)
print(f'\n审计文档总数: {len(layer6_docs)}')

print('\n' + '='*80)
print('问题汇总')
print('='*80)

total_issues = 0

if issues['missing_yaml']:
    print(f"\n[P0] 缺少YAML头部 ({len(issues['missing_yaml'])}个):")
    for f in issues['missing_yaml']:
        print(f"  - {f}")
    total_issues += len(issues['missing_yaml'])

if issues['missing_fields']:
    print(f"\n[P1] YAML字段缺失 ({len(issues['missing_fields'])}个):")
    for item in issues['missing_fields']:
        print(f"  - {item['file']}: 缺少 {', '.join(item['fields'])}")
    total_issues += len(issues['missing_fields'])

if issues['missing_module_id']:
    print(f"\n[P0] 缺少module_id ({len(issues['missing_module_id'])}个):")
    for f in issues['missing_module_id']:
        print(f"  - {f}")
    total_issues += len(issues['missing_module_id'])

if issues['invalid_module_id']:
    print(f"\n[P2] module_id格式错误 ({len(issues['invalid_module_id'])}个):")
    for item in issues['invalid_module_id']:
        print(f"  - {item['file']}: {item['module_id']}")
    total_issues += len(issues['invalid_module_id'])

if issues['missing_responsibility']:
    print(f"\n[P0] 缺少responsibility ({len(issues['missing_responsibility'])}个):")
    for f in issues['missing_responsibility']:
        print(f"  - {f}")
    total_issues += len(issues['missing_responsibility'])

if issues['insufficient_responsibilities']:
    print(f"\n[P1] responsibility项不足 ({len(issues['insufficient_responsibilities'])}个):")
    for item in issues['insufficient_responsibilities']:
        print(f"  - {item['file']}: 仅{item['count']}项 ({item['items']})")
    total_issues += len(issues['insufficient_responsibilities'])

if issues['missing_boundary']:
    print(f"\n[P1] 缺少职责边界说明 ({len(issues['missing_boundary'])}个):")
    for f in issues['missing_boundary']:
        print(f"  - {f}")
    total_issues += len(issues['missing_boundary'])

print('\n' + '='*80)
print('审计结论')
print('='*80)
print(f"\n总问题数: {total_issues}")

if len(layer6_docs) > 0:
    compliance_rate = max(0, (1 - total_issues / (len(layer6_docs) * 3)) * 100)
    print(f"合规率: {compliance_rate:.1f}%")

if total_issues == 0:
    print("\n[OK] 所有文档均符合专业量化机构标准")
else:
    print(f"\n[WARNING] 发现{total_issues}个问题需要修复")
