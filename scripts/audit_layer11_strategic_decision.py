#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 11 战略决策层深度审计脚本
审计范围：L1文件系统层、L2文档内容层、L3专业标准层
"""

import os
import re
import sys
from collections import defaultdict
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

strategic_dir = 'docs/11_STRATEGIC_DECISION'
files = []

# 收集所有.md文件
for root, dirs, filenames in os.walk(strategic_dir):
    for f in filenames:
        if f.endswith('.md'):
            filepath = os.path.join(root, f)
            files.append(filepath)

print('=' * 80)
print('Layer 11 战略决策层深度审计报告')
print('=' * 80)
print(f'审计时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print(f'审计范围: {strategic_dir}')
print(f'总文件数: {len(files)}')
print()

# ============================================================================
# L1 文件系统层审计
# ============================================================================
print('=' * 80)
print('L1 文件系统层审计')
print('=' * 80)
print()

# 1.1 目录结构检查
print('### 1.1 目录结构检查')
print()
subdirs = {}
for f in files:
    parts = f.split(os.sep)
    if len(parts) > 3:
        subdir = parts[3]
        if subdir not in subdirs:
            subdirs[subdir] = []
        subdirs[subdir].append(f)

print(f'子目录数: {len(subdirs)}')
if subdirs:
    for d, flist in sorted(subdirs.items()):
        print(f'  - {d}/: {len(flist)}个文件')
        if len(flist) < 3:
            print(f'    ⚠️ 稀疏目录（文件数<3）')
else:
    print('  ✅ 无子目录（扁平结构）')

# 检查目录层级深度
max_depth = 0
for f in files:
    depth = f.count(os.sep) - strategic_dir.count(os.sep)
    max_depth = max(max_depth, depth)

print(f'目录层级深度: {max_depth}')
if max_depth > 4:
    print('  ⚠️ 目录层级过深（>4层）')
else:
    print('  ✅ 目录层级合理')
print()

# 1.2 文件命名检查
print('### 1.2 文件命名检查')
print()
naming_issues = []
for f in files:
    basename = os.path.basename(f)
    # 检查中文文件名
    if re.search(r'[\u4e00-\u9fff]', basename):
        naming_issues.append(('中文命名', basename))
    # 检查空格
    if ' ' in basename:
        naming_issues.append(('包含空格', basename))
    # 检查特殊字符（除了-_.）
    if re.search(r'[^\w\-_\.]', basename):
        naming_issues.append(('特殊字符', basename))

if naming_issues:
    for issue_type, filename in naming_issues:
        print(f'  ⚠️ {issue_type}: {filename}')
else:
    print('  ✅ 所有文件命名规范')
print()

# 1.3 路径引用检查
print('### 1.3 路径引用检查')
print()
dead_links = []
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 检查相对路径链接
    links = re.findall(r'\[.*?\]\(([^)]+)\)', content)
    for link in links:
        if link.startswith('http') or link.startswith('#'):
            continue
        
        # 计算链接的绝对路径
        link_path = os.path.normpath(os.path.join(os.path.dirname(f), link))
        if not os.path.exists(link_path):
            dead_links.append((os.path.basename(f), link))

if dead_links:
    print(f'  ⚠️ 发现 {len(dead_links)} 个死链接:')
    for filename, link in dead_links[:10]:
        print(f'    - {filename} -> {link}')
    if len(dead_links) > 10:
        print(f'    ... 还有 {len(dead_links) - 10} 个死链接')
else:
    print('  ✅ 无死链接')
print()

# ============================================================================
# L2 文档内容层审计
# ============================================================================
print('=' * 80)
print('L2 文档内容层审计')
print('=' * 80)
print()

# 2.1 职责驱动原则检查
print('### 2.1 职责驱动原则检查')
print()
responsibility_check = []
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    basename = os.path.basename(f)
    
    # 提取职责描述
    responsibility = None
    patterns = [
        r'##\s*文档职责\s*\n([^\n]+)',
        r'##\s*核心职责\s*\n([^\n]+)',
        r'###\s*核心职责\s*\n([^\n]+)',
        r'核心职责[：:]\s*([^\n]+)',
        r'职责[：:]\s*([^\n]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            responsibility = match.group(1).strip()
            break
    
    responsibility_check.append({
        'file': basename,
        'responsibility': responsibility
    })

# 打印职责检查结果
has_responsibility = sum(1 for item in responsibility_check if item['responsibility'])
print(f'有明确职责描述: {has_responsibility}/{len(files)}')

missing_responsibility = [item['file'] for item in responsibility_check if not item['responsibility']]
if missing_responsibility:
    print(f'  ⚠️ 缺少明确职责描述的文件 ({len(missing_responsibility)}个):')
    for f in missing_responsibility[:10]:
        print(f'    - {f}')
    if len(missing_responsibility) > 10:
        print(f'    ... 还有 {len(missing_responsibility) - 10} 个文件')
else:
    print('  ✅ 所有文件都有明确职责描述')
print()

# 2.2 职责重叠检查
print('### 2.2 职责重叠检查')
print()
keywords_map = {}
keyword_patterns = [
    '资产配置', '风险预算', '策略选择', '战略调整', '投资组合',
    '风险管理', '绩效归因', '再平衡', '流动性', '融资融券',
    '基准管理', '情景分析', '市场状态', '宏观因子', 'ESG',
    '税务管理', '多策略', 'IPS', '投资限制', '决策审计',
    '资本配置', '投资组合保险', '交易成本', '开源', '技术选型',
]

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    basename = os.path.basename(f)
    keywords = []
    
    for pattern in keyword_patterns:
        if pattern in content:
            keywords.append(pattern)
    
    keywords_map[basename] = keywords

# 找出关键词重叠的文件
overlap_pairs = []
for i, (file1, kw1) in enumerate(keywords_map.items()):
    for file2, kw2 in list(keywords_map.items())[i+1:]:
        common = set(kw1) & set(kw2)
        if len(common) >= 4:  # 4个以上关键词重叠
            overlap_pairs.append((file1, file2, common))

if overlap_pairs:
    print(f'  ⚠️ 发现 {len(overlap_pairs)} 对文件可能存在职责重叠:')
    for file1, file2, common in overlap_pairs[:5]:
        print(f'    - {file1[:35]:<35} <-> {file2[:35]}')
        print(f'      共同关键词: {", ".join(sorted(common))}')
    if len(overlap_pairs) > 5:
        print(f'    ... 还有 {len(overlap_pairs) - 5} 对文件')
else:
    print('  ✅ 未发现明显的职责重叠')
print()

# 2.3 索引完备性检查
print('### 2.3 索引完备性检查')
print()
index_file = os.path.join(strategic_dir, 'INDEX.md')
if os.path.exists(index_file):
    with open(index_file, 'r', encoding='utf-8') as f:
        index_content = f.read()
    
    # 检查INDEX.md中引用的文件
    linked_files = re.findall(r'\[.*?\]\(\.?\/?([^)]+\.md)\)', index_content)
    
    # 获取所有实际文件
    actual_files = [os.path.basename(f) for f in files if os.path.basename(f) != 'INDEX.md']
    
    # 检查缺失的链接
    missing_links = []
    for af in actual_files:
        if af not in linked_files:
            missing_links.append(af)
    
    if missing_links:
        print(f'  ⚠️ INDEX.md中缺失的文件链接 ({len(missing_links)}个):')
        for f in missing_links:
            print(f'    - {f}')
    else:
        print('  ✅ INDEX.md索引完整')
else:
    print('  ❌ 缺少INDEX.md文件')
print()

# 2.4 版本隔离检查
print('### 2.4 版本隔离检查')
print()
version_info = []
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    basename = os.path.basename(f)
    
    # 提取版本信息
    version_match = re.search(r'version:\s*(\S+)', content)
    version = version_match.group(1) if version_match else '未标识'
    
    # 提取更新日期
    date_match = re.search(r'last_updated:\s*(\S+)', content)
    last_updated = date_match.group(1) if date_match else '未标识'
    
    version_info.append({
        'file': basename,
        'version': version,
        'last_updated': last_updated
    })

print('版本标识统计:')
has_version = sum(1 for item in version_info if item['version'] != '未标识')
print(f'  有版本标识: {has_version}/{len(files)}')

has_date = sum(1 for item in version_info if item['last_updated'] != '未标识')
print(f'  有更新日期: {has_date}/{len(files)}')

# 检查重复版本号
version_count = defaultdict(list)
for item in version_info:
    if item['version'] != '未标识':
        version_count[item['version']].append(item['file'])

duplicates = {k: v for k, v in version_count.items() if len(v) > 1}
if duplicates:
    print('  ⚠️ 发现重复的版本号:')
    for ver, flist in duplicates.items():
        print(f'    {ver}: {flist}')
else:
    print('  ✅ 无重复版本号')
print()

# ============================================================================
# L3 专业标准层审计
# ============================================================================
print('=' * 80)
print('L3 专业标准层审计')
print('=' * 80)
print()

# 3.1 五大原则符合性检查
print('### 3.1 五大原则符合性检查')
print()

# 职责驱动原则
print('1. 职责驱动原则:')
if has_responsibility == len(files):
    print('  ✅ 所有文档都有明确职责')
else:
    print(f'  ⚠️ {len(files) - has_responsibility} 个文档缺少明确职责')

# 索引完备原则
print('2. 索引完备原则:')
if os.path.exists(index_file) and not missing_links:
    print('  ✅ 索引完备')
elif os.path.exists(index_file):
    print(f'  ⚠️ 索引不完整，缺失 {len(missing_links)} 个文件链接')
else:
    print('  ❌ 缺少索引文件')

# 版本隔离原则
print('3. 版本隔离原则:')
if has_version == len(files):
    print('  ✅ 所有文档都有版本标识')
else:
    print(f'  ⚠️ {len(files) - has_version} 个文档缺少版本标识')

# 文档代码对应原则
print('4. 文档代码对应原则:')
print('  ℹ️ 需要人工检查代码实现状态')

# 命名规范原则
print('5. 命名规范原则:')
if not naming_issues:
    print('  ✅ 所有文件命名规范')
else:
    print(f'  ⚠️ {len(naming_issues)} 个文件命名不规范')
print()

# 3.2 编号体系检查
print('### 3.2 编号体系检查')
print()
module_ids = {}
missing_module_id = []
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    basename = os.path.basename(f)
    
    # 提取module_id
    match = re.search(r'module_id:\s*(\S+)', content)
    if match:
        mid = match.group(1)
        if mid in module_ids:
            module_ids[mid].append(basename)
        else:
            module_ids[mid] = [basename]
    else:
        missing_module_id.append(basename)

has_module_id = len(files) - len(missing_module_id)
print(f'有module_id: {has_module_id}/{len(files)}')

if missing_module_id:
    print(f'  ⚠️ 缺少module_id的文件 ({len(missing_module_id)}个):')
    for f in missing_module_id:
        print(f'    - {f}')

# 检查重复的module_id
duplicates = {k: v for k, v in module_ids.items() if len(v) > 1}
if duplicates:
    print('  ❌ 发现重复的module_id:')
    for mid, flist in duplicates.items():
        print(f'    {mid}:')
        for f in flist:
            print(f'      - {f}')
else:
    print('  ✅ 无重复module_id')
print()

# 3.3 文档质量检查
print('### 3.3 文档质量检查')
print()
quality_issues = []
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    basename = os.path.basename(f)
    issues = []
    
    # 检查YAML头部
    if not content.startswith('---'):
        issues.append('缺少YAML头部')
    
    # 检查必要字段
    required_fields = ['module_id', 'version', 'status', 'created_date', 'last_updated']
    for field in required_fields:
        if f'{field}:' not in content:
            issues.append(f'缺少{field}字段')
    
    # 检查文档结构
    if '##' not in content:
        issues.append('缺少章节结构')
    
    if issues:
        quality_issues.append((basename, issues))

if quality_issues:
    print(f'  ⚠️ 发现 {len(quality_issues)} 个文档存在质量问题:')
    for filename, issues in quality_issues[:10]:
        print(f'    - {filename}: {", ".join(issues)}')
    if len(quality_issues) > 10:
        print(f'    ... 还有 {len(quality_issues) - 10} 个文档')
else:
    print('  ✅ 所有文档质量合格')
print()

# ============================================================================
# 审计总结
# ============================================================================
print('=' * 80)
print('审计总结')
print('=' * 80)
print()

# 统计问题数量
p0_issues = 0  # 高风险问题
p1_issues = 0  # 中风险问题
p2_issues = 0  # 低风险问题

# P0问题：架构破坏、职责混乱、安全漏洞
if len(overlap_pairs) > 0:
    p0_issues += len(overlap_pairs)
if duplicates:
    p0_issues += len(duplicates)

# P1问题：文档治理违规、索引缺失、版本混乱
if missing_links:
    p1_issues += len(missing_links)
if missing_module_id:
    p1_issues += len(missing_module_id)
if dead_links:
    p1_issues += len(dead_links)

# P2问题：命名不规范、格式问题、次要优化
if naming_issues:
    p2_issues += len(naming_issues)
if quality_issues:
    p2_issues += len(quality_issues)

print(f'P0级问题（高风险）: {p0_issues}个')
print(f'P1级问题（中风险）: {p1_issues}个')
print(f'P2级问题（低风险）: {p2_issues}个')
print()

# 计算合规率
total_checks = 5  # 五大原则
passed_checks = 0
if has_responsibility == len(files):
    passed_checks += 1
if os.path.exists(index_file) and not missing_links:
    passed_checks += 1
if has_version == len(files):
    passed_checks += 1
# 文档代码对应需要人工检查，暂不计入
if not naming_issues:
    passed_checks += 1

compliance_rate = (passed_checks / total_checks) * 100
print(f'文档治理合规率: {compliance_rate:.1f}%')
print()

if compliance_rate >= 90:
    print('✅ 符合专业量化机构标准（≥90%）')
elif compliance_rate >= 70:
    print('⚠️ 接近专业标准，需要优化')
else:
    print('❌ 不符合专业标准，需要整改')
print()

print('=' * 80)
print('审计完成')
print('=' * 80)
