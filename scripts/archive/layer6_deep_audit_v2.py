# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

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

layer6_docs = []
l1_issues = defaultdict(list)
l2_issues = defaultdict(list)
l3_issues = defaultdict(list)
responsibility_map = defaultdict(list)
content_hashes = defaultdict(list)
module_ids = defaultdict(list)

print('='*80)
print('Layer 6 组合优化层三层深度审计')
print('='*80)
print(f'审计时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print(f'审计目录: {blueprints_dir}')
print()

# ============================================================================
# L1 文件系统层审计
# ============================================================================
print('【L1 文件系统层审计】')
print('-'*80)

# 1.1 目录结构检查
print('\n1.1 目录结构检查:')
if os.path.exists(blueprints_dir):
    files = [f for f in os.listdir(blueprints_dir) if f.endswith('.md')]
    print(f'  ✓ 目录存在: {blueprints_dir}')
    print(f'  ✓ 文档数量: {len(files)}')
    
    # 检查目录层级深度
    path_depth = blueprints_dir.count(os.sep) - blueprints_dir.count(os.sep, 0, blueprints_dir.find('ZephyrAlpha'))
    if path_depth > 4:
        l1_issues['目录层级过深'].append(f'{blueprints_dir} (深度: {path_depth})')
        print(f'  ✗ 目录层级过深: {path_depth}层')
    else:
        print(f'  ✓ 目录层级: {path_depth}层')
else:
    l1_issues['目录不存在'].append(blueprints_dir)
    print(f'  ✗ 目录不存在: {blueprints_dir}')

# 1.2 文件命名检查
print('\n1.2 文件命名检查:')
for file in files:
    # INDEX.md 是合法的索引文件，跳过检查
    if file == 'INDEX.md':
        continue
    
    # 检查命名规范
    if not re.match(r'^[A-Z_0-9]+_BLUEPRINT\.md$', file):
        l1_issues['命名不规范'].append(file)
    
    # 检查旧架构命名残留
    if re.search(r'Layer_[0-9]|L[0-9]_', file):
        l1_issues['旧架构命名残留'].append(file)
    
    # 检查特殊字符
    if ' ' in file or re.search(r'[\u4e00-\u9fff]', file):
        l1_issues['特殊字符问题'].append(file)

if l1_issues.get('命名不规范'):
    print(f'  ✗ 命名不规范: {len(l1_issues["命名不规范"])}个')
    for f in l1_issues["命名不规范"][:5]:
        print(f'    - {f}')
else:
    print('  ✓ 所有BLUEPRINT文件命名规范')

# ============================================================================
# L2 文档内容层审计
# ============================================================================
print('\n【L2 文档内容层审计】')
print('-'*80)

for file in files:
    file_path = os.path.join(blueprints_dir, file)
    
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    # 检查Layer归属
    layer_match = re.search(r'layer:\s*Layer\s*(5\.2|6|组合优化)', content, re.IGNORECASE)
    if not layer_match:
        continue
    
    # YAML头部检查
    yaml_match = re.search(r'^---\s*[\r\n]+(.*?)[\r\n]+---', content, re.DOTALL)
    
    if not yaml_match:
        l2_issues['缺少YAML头部'].append(file)
        continue
    
    yaml_content = yaml_match.group(1)
    
    # 检查必要字段
    missing_fields = []
    for field in required_yaml_fields:
        if field not in yaml_content:
            missing_fields.append(field)
    
    if missing_fields:
        l2_issues['YAML字段缺失'].append({
            'file': file,
            'fields': missing_fields
        })
    
    # 提取module_id
    module_id_match = re.search(r'module_id:\s*(\S+)', yaml_content)
    module_id = module_id_match.group(1) if module_id_match else 'MISSING'
    
    # 检查module_id唯一性
    if module_id != 'MISSING':
        module_ids[module_id].append(file)
    
    # 检查module_id格式
    if module_id == 'MISSING':
        l2_issues['缺少module_id'].append(file)
    elif module_id.endswith('_BLUEPRINT') or '_BLUEPRINT_' in module_id:
        l3_issues['module_id格式错误'].append({
            'file': file,
            'module_id': module_id
        })
    
    # 提取responsibility
    resp_match = re.search(r'responsibility:\s*[\r\n]+((?:\s+-\s+.+[\r\n]?)+)', yaml_content)
    if resp_match:
        resp_text = resp_match.group(1)
        resp_items = re.findall(r'-\s+(.+)', resp_text)
        resp_items = [item.strip() for item in resp_items if item.strip()]
        
        # 检查职责项是否包含乱码或无效字符
        has_garbled = any(
            'æ' in item or 
            '\ufffd' in item or 
            not item.strip() or 
            item.strip() == '' 
            for item in resp_items
        )
        if has_garbled:
            l2_issues['responsibility包含乱码'].append({
                'file': file,
                'items': resp_items
            })
        
        if len(resp_items) < 2:
            l2_issues['responsibility项不足'].append({
                'file': file,
                'count': len(resp_items),
                'items': resp_items
            })
        
        # 记录职责映射
        for item in resp_items:
            if not has_garbled:
                responsibility_map[item].append(file)
    else:
        l2_issues['缺少responsibility'].append(file)
    
    # 检查职责边界
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
        l2_issues['缺少职责边界'].append(file)
    
    # 检查核心定位章节
    if '## 核心定位' not in content:
        l2_issues['缺少核心定位章节'].append(file)
    
    # 检查变更历史
    if '## 变更历史' not in content and '## 11. 变更历史' not in content:
        l2_issues['缺少变更历史'].append(file)
    
    # 内容相似度检查（用于检测重复文档）
    content_lower = content.lower()
    # 提取核心内容（去除YAML和空行）
    core_content = re.sub(r'^---[\s\S]*?---', '', content)
    core_content = re.sub(r'\s+', ' ', core_content).strip()
    content_hash = hashlib.md5(core_content.encode()).hexdigest()[:16]
    content_hashes[content_hash].append(file)
    
    layer6_docs.append({
        'file': file,
        'module_id': module_id,
        'missing_fields': missing_fields
    })

print(f'\n审计文档总数: {len(layer6_docs)}')

# ============================================================================
# L3 专业标准层审计
# ============================================================================
print('\n【L3 专业标准层审计】')
print('-'*80)

# 3.1 五大原则符合性检查
print('\n3.1 五大原则符合性检查:')

# 职责驱动原则
print('\n  【职责驱动原则】')
if l2_issues.get('缺少responsibility'):
    print(f'    ✗ 缺少responsibility: {len(l2_issues["缺少responsibility"])}个')
if l2_issues.get('缺少职责边界'):
    print(f'    ✗ 缺少职责边界: {len(l2_issues["缺少职责边界"])}个')
if l2_issues.get('responsibility包含乱码'):
    print(f'    ✗ responsibility包含乱码: {len(l2_issues["responsibility包含乱码"])}个')

# 检查职责重叠
print('\n  【职责重叠检查】')
overlap_found = False
for resp, files_list in responsibility_map.items():
    if len(files_list) > 1:
        overlap_found = True
        l3_issues['职责重叠'].append({
            'responsibility': resp,
            'files': files_list
        })

if overlap_found:
    print(f'    ✗ 发现职责重叠: {len(l3_issues["职责重叠"])}项')
    for item in l3_issues['职责重叠'][:10]:
        print(f'      - "{item["responsibility"]}" 出现在: {", ".join(item["files"])}')
else:
    print('    ✓ 无职责重叠')

# 版本隔离原则
print('\n  【版本隔离原则】')
# 检查重复文档
duplicate_docs = []
for content_hash, files_list in content_hashes.items():
    if len(files_list) > 1:
        duplicate_docs.extend(files_list)
        l3_issues['疑似重复文档'].append(files_list)

if duplicate_docs:
    print(f'    ✗ 疑似重复文档: {len(duplicate_docs)}个')
    for group in l3_issues['疑似重复文档'][:5]:
        print(f'      - {", ".join(group)}')
else:
    print('    ✓ 无重复文档')

# 检查module_id重复
print('\n  【module_id唯一性检查】')
duplicate_module_ids = []
for mid, files_list in module_ids.items():
    if len(files_list) > 1:
        duplicate_module_ids.append({
            'module_id': mid,
            'files': files_list
        })
        l3_issues['module_id重复'].append({
            'module_id': mid,
            'files': files_list
        })

if duplicate_module_ids:
    print(f'    ✗ module_id重复: {len(duplicate_module_ids)}个')
    for item in duplicate_module_ids:
        print(f'      - {item["module_id"]}: {", ".join(item["files"])}')
else:
    print('    ✓ module_id唯一')

# 命名规范原则
print('\n  【命名规范原则】')
if l1_issues.get('命名不规范'):
    print(f'    ✗ 命名不规范: {len(l1_issues["命名不规范"])}个')
else:
    print('    ✓ 命名规范符合')

# ============================================================================
# 重点检查：职责不清、重复内容
# ============================================================================
print('\n【重点检查：职责不清、重复内容】')
print('-'*80)

# 检查职责描述模糊
print('\n职责描述清晰度检查:')
vague_keywords = ['管理', '处理', '优化', '支持', '实现', '提供']

for doc in layer6_docs:
    file_path = os.path.join(blueprints_dir, doc['file'])
    
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    resp_match = re.search(r'responsibility:\s*[\r\n]+((?:\s+-\s+.+[\r\n]?)+)', content)
    if resp_match:
        resp_text = resp_match.group(1)
        resp_items = re.findall(r'-\s+(.+)', resp_text)
        
        for item in resp_items:
            item = item.strip()
            # 检查是否过于简短
            if len(item) < 4:
                l3_issues['职责描述过短'].append({
                    'file': doc['file'],
                    'item': item
                })
            # 检查是否只有模糊关键词
            words = re.findall(r'[\u4e00-\u9fff]+', item)
            if len(words) == 1 and words[0] in vague_keywords:
                l3_issues['职责描述模糊'].append({
                    'file': doc['file'],
                    'item': item
                })

if l3_issues.get('职责描述过短'):
    print(f'  ✗ 职责描述过短: {len(l3_issues["职责描述过短"])}项')
if l3_issues.get('职责描述模糊'):
    print(f'  ✗ 职责描述模糊: {len(l3_issues["职责描述模糊"])}项')

# 检查核心定位章节内容
print('\n核心定位章节内容检查:')
for doc in layer6_docs:
    file_path = os.path.join(blueprints_dir, doc['file'])
    
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    # 提取核心定位章节
    core_match = re.search(r'## 核心定位\s*[\r\n]+(.+?)(?=\n##|\Z)', content, re.DOTALL)
    if core_match:
        core_content = core_match.group(1).strip()
        
        # 检查核心定位是否过于简短
        if len(core_content) < 50:
            l3_issues['核心定位过短'].append({
                'file': doc['file'],
                'length': len(core_content)
            })
        
        # 检查是否包含"负责"关键词
        if '负责' not in core_content and '职责' not in core_content:
            l3_issues['核心定位缺少职责描述'].append(doc['file'])

if l3_issues.get('核心定位过短'):
    print(f'  ✗ 核心定位过短: {len(l3_issues["核心定位过短"])}个')
if l3_issues.get('核心定位缺少职责描述'):
    print(f'  ✗ 核心定位缺少职责描述: {len(l3_issues["核心定位缺少职责描述"])}个')

# ============================================================================
# 问题汇总
# ============================================================================
print('\n' + '='*80)
print('问题汇总')
print('='*80)

total_issues = 0

# L1问题
if any(l1_issues.values()):
    print('\n【L1 文件系统层问题】')
    for issue_type, items in l1_issues.items():
        if items:
            print(f'\n  {issue_type} ({len(items)}个):')
            for item in items[:10]:
                print(f'    - {item}')
            total_issues += len(items)

# L2问题
if any(l2_issues.values()):
    print('\n【L2 文档内容层问题】')
    for issue_type, items in l2_issues.items():
        if items:
            if isinstance(items[0], dict):
                print(f'\n  {issue_type} ({len(items)}个):')
                for item in items[:10]:
                    if 'fields' in item:
                        print(f'    - {item["file"]}: 缺少 {", ".join(item["fields"])}')
                    elif 'items' in item:
                        print(f'    - {item["file"]}: {item["items"]}')
                    else:
                        print(f'    - {item}')
            else:
                print(f'\n  {issue_type} ({len(items)}个):')
                for item in items[:10]:
                    print(f'    - {item}')
            total_issues += len(items)

# L3问题
if any(l3_issues.values()):
    print('\n【L3 专业标准层问题】')
    for issue_type, items in l3_issues.items():
        if items:
            if isinstance(items[0], dict):
                print(f'\n  {issue_type} ({len(items)}个):')
                for item in items[:10]:
                    if 'responsibility' in item:
                        print(f'    - "{item["responsibility"]}" 在 {len(item["files"])}个文档中')
                    elif 'module_id' in item:
                        print(f'    - {item["module_id"]}: {", ".join(item["files"])}')
                    elif 'item' in item:
                        print(f'    - {item["file"]}: "{item["item"]}"')
                    else:
                        print(f'    - {item}')
            elif isinstance(items[0], list):
                print(f'\n  {issue_type} ({len(items)}组):')
                for group in items[:5]:
                    print(f'    - {", ".join(group)}')
            else:
                print(f'\n  {issue_type} ({len(items)}个):')
                for item in items[:10]:
                    print(f'    - {item}')
            total_issues += len(items)

# ============================================================================
# 审计结论
# ============================================================================
print('\n' + '='*80)
print('审计结论')
print('='*80)

print(f'\n审计文档总数: {len(layer6_docs)}')
print(f'发现问题总数: {total_issues}')

if len(layer6_docs) > 0:
    compliance_rate = max(0, (1 - total_issues / (len(layer6_docs) * 5)) * 100)
    print(f'合规率: {compliance_rate:.1f}%')

if total_issues == 0:
    print('\n[OK] 所有文档均符合专业量化机构标准')
else:
    print(f'\n[WARNING] 发现{total_issues}个问题需要修复')

# ============================================================================
# 生成审计报告
# ============================================================================
report_path = os.path.join(output_dir, f'LAYER6_DEEP_AUDIT_REPORT_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md')

with open(report_path, 'w', encoding='utf-8') as f:
    f.write(f'''# Layer 6 组合优化层深度审计报告

## 1. 审计概要

| 项目 | 内容 |
|------|------|
| **审计目标** | Layer 6 组合优化层所有文档 |
| **审计范围** | {blueprints_dir} |
| **审计时间** | {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} |
| **审计方法** | 三层审计(L1-L3) + 重点检查 |
| **文档总数** | {len(layer6_docs)} |
| **问题总数** | {total_issues} |
| **合规率** | {compliance_rate:.1f}% |

## 2. L1 文件系统层审计结果

### 2.1 目录结构检查
- 目录状态: {'✓ 正常' if os.path.exists(blueprints_dir) else '✗ 异常'}
- 文档数量: {len(files)}

### 2.2 文件命名检查
''')
    
    if l1_issues:
        for issue_type, items in l1_issues.items():
            if items:
                f.write(f'\n**{issue_type}** ({len(items)}个):\n')
                for item in items:
                    f.write(f'- {item}\n')
    else:
        f.write('\n✓ 所有文件命名规范\n')
    
    f.write('''
## 3. L2 文档内容层审计结果

### 3.1 YAML头部检查
''')
    
    yaml_issues = {k: v for k, v in l2_issues.items() if k in ['缺少YAML头部', 'YAML字段缺失', '缺少module_id', '缺少responsibility', 'responsibility项不足', 'responsibility包含乱码']}
    if yaml_issues:
        for issue_type, items in yaml_issues.items():
            if items:
                f.write(f'\n**{issue_type}** ({len(items)}个):\n')
                for item in items[:20]:
                    if isinstance(item, dict):
                        if 'fields' in item:
                            f.write(f'- {item["file"]}: 缺少 {", ".join(item["fields"])}\n')
                        elif 'items' in item:
                            f.write(f'- {item["file"]}: {item["items"]}\n')
                    else:
                        f.write(f'- {item}\n')
    else:
        f.write('\n✓ YAML头部完整\n')
    
    f.write('''
### 3.2 职责边界检查
''')
    
    if l2_issues.get('缺少职责边界'):
        f.write(f'\n**缺少职责边界** ({len(l2_issues["缺少职责边界"])}个):\n')
        for item in l2_issues['缺少职责边界']:
            f.write(f'- {item}\n')
    else:
        f.write('\n✓ 所有文档均有职责边界\n')
    
    f.write('''
## 4. L3 专业标准层审计结果

### 4.1 五大原则符合性
''')
    
    f.write(f'''
**职责驱动原则**:
- 缺少responsibility: {len(l2_issues.get('缺少responsibility', []))}个
- 缺少职责边界: {len(l2_issues.get('缺少职责边界', []))}个
- responsibility包含乱码: {len(l2_issues.get('responsibility包含乱码', []))}个
- 职责重叠: {len(l3_issues.get('职责重叠', []))}项

**版本隔离原则**:
- 疑似重复文档: {len(l3_issues.get('疑似重复文档', []))}组

**命名规范原则**:
- 命名不规范: {len(l1_issues.get('命名不规范', []))}个

**module_id唯一性**:
- module_id重复: {len(l3_issues.get('module_id重复', []))}个
''')
    
    if l3_issues.get('职责重叠'):
        f.write(f'\n### 4.2 职责重叠详情\n\n')
        for item in l3_issues['职责重叠']:
            f.write(f'- **"{item["responsibility"]}"** 出现在: {", ".join(item["files"])}\n')
    
    if l3_issues.get('疑似重复文档'):
        f.write(f'\n### 4.3 疑似重复文档\n\n')
        for group in l3_issues['疑似重复文档']:
            f.write(f'- {", ".join(group)}\n')
    
    f.write(f'''
## 5. 改进建议

### 5.1 立即修复 (P0)
''')
    
    p0_issues = []
    if l2_issues.get('缺少YAML头部'):
        p0_issues.append(f'- 修复{len(l2_issues["缺少YAML头部"])}个缺少YAML头部的文档')
    if l2_issues.get('缺少responsibility'):
        p0_issues.append(f'- 为{len(l2_issues["缺少responsibility"])}个文档添加responsibility字段')
    if l2_issues.get('responsibility包含乱码'):
        p0_issues.append(f'- 修复{len(l2_issues["responsibility包含乱码"])}个包含乱码的responsibility')
    if l3_issues.get('module_id重复'):
        p0_issues.append(f'- 解决{len(l3_issues["module_id重复"])}个module_id重复问题')
    
    if p0_issues:
        f.write('\n'.join(p0_issues) + '\n')
    else:
        f.write('\n✓ 无P0级问题\n')
    
    f.write('''
### 5.2 短期改进 (P1)
''')
    
    p1_issues = []
    if l2_issues.get('缺少职责边界'):
        p1_issues.append(f'- 为{len(l2_issues["缺少职责边界"])}个文档添加职责边界说明')
    if l3_issues.get('职责重叠'):
        p1_issues.append(f'- 解决{len(l3_issues["职责重叠"])}项职责重叠问题')
    if l3_issues.get('疑似重复文档'):
        p1_issues.append(f'- 处理{len(l3_issues["疑似重复文档"])}组疑似重复文档')
    
    if p1_issues:
        f.write('\n'.join(p1_issues) + '\n')
    else:
        f.write('\n✓ 无P1级问题\n')
    
    f.write('''
### 5.3 长期优化 (P2)
''')
    
    p2_issues = []
    if l3_issues.get('职责描述过短'):
        p2_issues.append(f'- 完善{len(l3_issues["职责描述过短"])}项过短的职责描述')
    if l3_issues.get('职责描述模糊'):
        p2_issues.append(f'- 明确{len(l3_issues["职责描述模糊"])}项模糊的职责描述')
    if l3_issues.get('核心定位过短'):
        p2_issues.append(f'- 扩展{len(l3_issues["核心定位过短"])}个过短的核心定位章节')
    
    if p2_issues:
        f.write('\n'.join(p2_issues) + '\n')
    else:
        f.write('\n✓ 无P2级问题\n')
    
    f.write(f'''
## 6. 审计质量声明

- **审计覆盖率**: 100% (所有Layer 6文档均已审计)
- **审计深度**: 三层审计(L1-L3) + 重点检查
- **审计标准**: 专业量化机构五大原则
- **审计时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

*本报告由自动化审计工具生成*
''')

print(f'\n审计报告已生成: {report_path}')
