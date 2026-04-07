import os
import re
from pathlib import Path
from collections import defaultdict

blueprints_dir = r'd:\ZephyrAlpha\docs\05_IMPLEMENTATION\06_CONSTRUCTION_DOCS\01_BLUEPRINTS'

layer6_docs = []
responsibilities = defaultdict(list)
module_ids = {}

for file in os.listdir(blueprints_dir):
    if file.endswith('.md') and 'BLUEPRINT' in file:
        file_path = os.path.join(blueprints_dir, file)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        layer_match = re.search(r'layer:\s*Layer\s*(5\.2|6|组合优化)', content, re.IGNORECASE)
        if not layer_match:
            continue
        
        module_id_match = re.search(r'module_id:\s*(\S+)', content)
        module_id = module_id_match.group(1) if module_id_match else 'MISSING'
        
        resp_match = re.search(r'responsibility:\s*\n((?:\s+-\s+.+\n?)+)', content)
        if resp_match:
            resp_text = resp_match.group(1)
            resp_items = re.findall(r'-\s+(.+)', resp_text)
            for item in resp_items:
                responsibilities[item.strip()].append(file)
        
        boundary_match = re.search(r'>\s*\*\*职责边界\*\*:\s*\n((?:>.*\n?)+)', content)
        boundary = boundary_match.group(1) if boundary_match else 'MISSING'
        
        layer6_docs.append({
            'file': file,
            'module_id': module_id,
            'layer': layer_match.group(0),
            'has_boundary': 'YES' if boundary != 'MISSING' else 'NO',
            'boundary': boundary[:200] if boundary != 'MISSING' else 'MISSING'
        })
        
        module_ids[module_id] = module_ids.get(module_id, 0) + 1

print('='*80)
print('Layer 6 组合优化层文档清单 (共{}个)'.format(len(layer6_docs)))
print('='*80)

for doc in sorted(layer6_docs, key=lambda x: x['file']):
    print(f"\n文件: {doc['file']}")
    print(f"  module_id: {doc['module_id']}")
    print(f"  Layer: {doc['layer']}")
    print(f"  职责边界: {doc['has_boundary']}")

print('\n' + '='*80)
print('职责重叠分析')
print('='*80)

overlap_found = False
for resp, files in sorted(responsibilities.items()):
    if len(files) > 1:
        overlap_found = True
        print(f"\n职责 '{resp}' 出现在多个文档:")
        for f in files:
            print(f"  - {f}")

if not overlap_found:
    print('未发现职责重叠问题')

print('\n' + '='*80)
print('module_id重复检查')
print('='*80)

dup_found = False
for mid, count in module_ids.items():
    if count > 1:
        dup_found = True
        print(f"module_id '{mid}' 重复 {count} 次")

if not dup_found:
    print('未发现module_id重复问题')
