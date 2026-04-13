#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
Alpha因子层深度审计脚本 - 第二轮
全面审计每一个文档的每一个内容
"""

import re
import json
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY')
OUTPUT_DIR = Path(r'D:\ZephyrAlpha\docs\09_AUDIT\STATE')

def get_file_hash(file_path):
    """计算文件内容的哈希值"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    except:
        return None

def extract_yaml_metadata(content):
    """提取YAML元数据"""
    metadata = {}
    yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if yaml_match:
        yaml_content = yaml_match.group(1)
        for line in yaml_content.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                if value.startswith('['):
                    # 列表格式
                    items = re.findall(r'-\s*([^\]]+)', value)
                    metadata[key] = [item.strip() for item in items]
                elif value.startswith('"') or value.startswith("'"):
                    metadata[key] = value.strip('"\'')
                else:
                    metadata[key] = value
    return metadata

def extract_title(content):
    """提取文档标题"""
    # 查找第一个 # 标题
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None

def extract_summary(content):
    """提取文档摘要"""
    # 查找第一个引用块
    match = re.search(r'^>\s*(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None

def extract_all_links(content):
    """提取所有链接"""
    links = []
    # Markdown链接格式: [text](path)
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
    if link_path.startswith('http://') or link_path.startswith('https://'):
        return True, 'external'
    
    # 处理相对路径
    try:
        if link_path.startswith('/'):
            # 绝对路径
            target = FACTOR_LIBRARY / link_path.lstrip('/')
        else:
            # 相对路径
            target = file_path.parent / link_path
        
        # 标准化路径
        target = target.resolve()
        
        # 检查文件是否存在
        if target.exists():
            return True, str(target.relative_to(FACTOR_LIBRARY))
        else:
            return False, link_path
    except:
        return False, link_path

def get_file_depth(file_path):
    """获取文件深度"""
    rel_path = file_path.relative_to(FACTOR_LIBRARY)
    return len(rel_path.parts) - 1

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
        'issues': [],
        'content_preview': ''
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        result['size'] = len(content)
        result['hash'] = get_file_hash(file_path)
        result['metadata'] = extract_yaml_metadata(content)
        result['title'] = extract_title(content)
        result['summary'] = extract_summary(content)
        result['content_preview'] = content[:500]
        
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
        
        # L1检查：路径深度
        if result['depth'] > 4:
            result['issues'].append({
                'level': 'L1',
                'type': '目录层级过深',
                'description': f'文件深度为{result["depth"]}层，超过4层'
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
        elif len(result['title']) < 5:
            result['issues'].append({
                'level': 'L2',
                'type': '标题过短',
                'description': f'标题过短: {result["title"]}'
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
        
        # L3检查：职责描述格式
        responsibility = result['metadata'].get('responsibility', [])
        if responsibility:
            if isinstance(responsibility, list):
                for resp in responsibility:
                    if len(resp) < 10:
                        result['issues'].append({
                            'level': 'L3',
                            'type': '职责描述过短',
                            'description': f'职责描述过短: {resp}'
                        })
    
    except Exception as e:
        result['issues'].append({
            'level': 'ERROR',
            'type': '读取错误',
            'description': str(e)
        })
    
    return result

def analyze_directory_structure():
    """分析目录结构"""
    print("\n" + "=" * 80)
    print("分析目录结构")
    print("=" * 80)
    
    directories = {}
    
    for dir_path in FACTOR_LIBRARY.rglob('*'):
        if dir_path.is_dir():
            rel_path = dir_path.relative_to(FACTOR_LIBRARY)
            
            # 统计目录下的文件数
            files = list(dir_path.glob('*.md'))
            
            # 检查是否有INDEX.md
            has_index = (dir_path / 'INDEX.md').exists()
            
            # 检查是否有README.md
            has_readme = (dir_path / 'README.md').exists()
            
            directories[str(rel_path)] = {
                'file_count': len(files),
                'has_index': has_index,
                'has_readme': has_readme,
                'depth': len(rel_path.parts) - 1
            }
    
    # 识别稀疏目录
    sparse_dirs = {k: v for k, v in directories.items() if v['file_count'] < 3}
    
    # 识别深层目录
    deep_dirs = {k: v for k, v in directories.items() if v['depth'] > 3}
    
    # 识别缺少索引的目录
    missing_index = {k: v for k, v in directories.items() if not v['has_index']}
    
    print(f"\n总目录数: {len(directories)}")
    print(f"稀疏目录（文件<3）: {len(sparse_dirs)}")
    print(f"深层目录（深度>3）: {len(deep_dirs)}")
    print(f"缺少INDEX的目录: {len(missing_index)}")
    
    return directories, sparse_dirs, deep_dirs, missing_index

def find_duplicate_content(analysis_results):
    """查找重复内容"""
    print("\n" + "=" * 80)
    print("查找重复内容")
    print("=" * 80)
    
    # 按哈希分组
    hash_groups = defaultdict(list)
    for result in analysis_results:
        if result['hash']:
            hash_groups[result['hash']].append(result['path'])
    
    # 找出重复的
    duplicates = {k: v for k, v in hash_groups.items() if len(v) > 1}
    
    print(f"\n发现重复文档组: {len(duplicates)}组")
    
    for hash_val, paths in duplicates.items():
        print(f"\n哈希: {hash_val}")
        for path in paths:
            print(f"  - {path}")
    
    return duplicates

def find_module_id_duplicates(analysis_results):
    """查找重复的module_id"""
    print("\n" + "=" * 80)
    print("查找重复的module_id")
    print("=" * 80)
    
    # 按module_id分组
    module_id_groups = defaultdict(list)
    for result in analysis_results:
        module_id = result['metadata'].get('module_id')
        if module_id:
            module_id_groups[module_id].append(result['path'])
    
    # 找出重复的
    duplicates = {k: v for k, v in module_id_groups.items() if len(v) > 1}
    
    print(f"\n发现重复module_id: {len(duplicates)}个")
    
    for module_id, paths in sorted(duplicates.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        print(f"\nmodule_id: {module_id}")
        print(f"重复次数: {len(paths)}")
        for path in paths[:5]:
            print(f"  - {path}")
        if len(paths) > 5:
            print(f"  ... 还有{len(paths) - 5}个")
    
    return duplicates

def find_responsibility_overlap(analysis_results):
    """查找职责重叠"""
    print("\n" + "=" * 80)
    print("查找职责重叠")
    print("=" * 80)
    
    # 提取所有职责关键词
    responsibility_keywords = defaultdict(list)
    
    for result in analysis_results:
        responsibility = result['metadata'].get('responsibility', [])
        if responsibility:
            if isinstance(responsibility, list):
                for resp in responsibility:
                    # 提取关键词
                    keywords = re.findall(r'[\u4e00-\u9fa5]+', resp)
                    for keyword in keywords:
                        if len(keyword) >= 2:
                            responsibility_keywords[keyword].append({
                                'path': result['path'],
                                'responsibility': resp
                            })
    
    # 找出重叠的关键词
    overlap = {k: v for k, v in responsibility_keywords.items() if len(v) > 1}
    
    print(f"\n发现职责重叠关键词: {len(overlap)}个")
    
    # 显示前10个
    for keyword, docs in sorted(overlap.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        print(f"\n关键词: {keyword}")
        print(f"出现次数: {len(docs)}")
        for doc in docs[:5]:
            print(f"  - {doc['path']}: {doc['responsibility']}")
    
    return overlap

def main():
    """主函数"""
    print("=" * 80)
    print("Alpha因子层深度审计 - 第二轮")
    print("=" * 80)
    print(f"审计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"审计范围: {FACTOR_LIBRARY}")
    
    # 扫描所有文档
    print("\n" + "=" * 80)
    print("扫描所有文档")
    print("=" * 80)
    
    all_files = list(FACTOR_LIBRARY.rglob('*.md'))
    print(f"\n发现文档: {len(all_files)}个")
    
    # 分析每个文件
    analysis_results = []
    for i, file_path in enumerate(all_files, 1):
        if i % 20 == 0:
            print(f"处理进度: {i}/{len(all_files)}")
        result = analyze_file(file_path)
        analysis_results.append(result)
    
    print(f"\n分析完成: {len(analysis_results)}个文件")
    
    # 分析目录结构
    directories, sparse_dirs, deep_dirs, missing_index = analyze_directory_structure()
    
    # 查找重复内容
    duplicates = find_duplicate_content(analysis_results)
    
    # 查找重复的module_id
    module_id_duplicates = find_module_id_duplicates(analysis_results)
    
    # 查找职责重叠
    responsibility_overlap = find_responsibility_overlap(analysis_results)
    
    # 统计问题
    print("\n" + "=" * 80)
    print("统计问题")
    print("=" * 80)
    
    issues_by_level = defaultdict(list)
    for result in analysis_results:
        for issue in result['issues']:
            issues_by_level[issue['level']].append({
                'path': result['path'],
                'issue': issue
            })
    
    print(f"\nL1问题: {len(issues_by_level['L1'])}个")
    print(f"L2问题: {len(issues_by_level['L2'])}个")
    print(f"L3问题: {len(issues_by_level['L3'])}个")
    print(f"错误: {len(issues_by_level['ERROR'])}个")
    
    # 生成报告
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = OUTPUT_DIR / f'ALPHA_FACTOR_LAYER_DEEP_AUDIT_REPORT_ROUND2_{timestamp}.md'
    data_path = OUTPUT_DIR / f'ALPHA_FACTOR_LAYER_DEEP_AUDIT_DATA_ROUND2_{timestamp}.json'
    
    # 保存数据
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'total_files': len(analysis_results),
            'analysis_results': analysis_results,
            'directories': directories,
            'sparse_dirs': sparse_dirs,
            'deep_dirs': deep_dirs,
            'missing_index': missing_index,
            'duplicates': {k: v for k, v in duplicates.items()},
            'module_id_duplicates': {k: v for k, v in module_id_duplicates.items()},
            'issues_by_level': {k: v for k, v in issues_by_level.items()}
        }, f, ensure_ascii=False, indent=2)
    
    # 生成报告
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"""# Alpha因子层深度审计报告 - 第二轮

## 审计概要

- **审计时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **审计范围**: {FACTOR_LIBRARY}
- **审计方法**: 三层审计（L1文件系统层、L2文档内容层、L3专业标准层）
- **审计结论**: 发现{len(issues_by_level['L1']) + len(issues_by_level['L2']) + len(issues_by_level['L3'])}个问题

## 审计统计

| 统计项 | 数量 |
|--------|------|
| 总文档数 | {len(analysis_results)} |
| 总问题数 | {len(issues_by_level['L1']) + len(issues_by_level['L2']) + len(issues_by_level['L3'])} |
| L1问题 | {len(issues_by_level['L1'])} |
| L2问题 | {len(issues_by_level['L2'])} |
| L3问题 | {len(issues_by_level['L3'])} |
| 重复文档组 | {len(duplicates)} |
| 重复module_id | {len(module_id_duplicates)} |

## L1 文件系统层问题

### 稀疏目录（文件数<3）

""")
        for dir_path, info in sparse_dirs.items():
            f.write(f"- {dir_path}: {info['file_count']}个文件\n")
        
        f.write(f"""
### 深层目录（深度>3）

""")
        for dir_path, info in deep_dirs.items():
            f.write(f"- {dir_path}: 深度{info['depth']}\n")
        
        f.write(f"""
### 缺少INDEX的目录

""")
        for dir_path, info in missing_index.items():
            f.write(f"- {dir_path}\n")
        
        f.write(f"""
## L2 文档内容层问题

### 重复文档

""")
        if duplicates:
            for hash_val, paths in duplicates.items():
                f.write(f"\n哈希: {hash_val}\n")
                for path in paths:
                    f.write(f"- {path}\n")
        else:
            f.write("无重复文档\n")
        
        f.write(f"""
### 重复module_id

""")
        for module_id, paths in sorted(module_id_duplicates.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            f.write(f"\n#### module_id: {module_id}\n\n")
            f.write(f"重复次数: {len(paths)}\n\n")
            for path in paths[:10]:
                f.write(f"- {path}\n")
        
        f.write(f"""
## L3 专业标准层问题

### 职责重叠关键词

""")
        for keyword, docs in sorted(responsibility_overlap.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            f.write(f"\n### 关键词: {keyword}\n\n")
            f.write(f"出现次数: {len(docs)}\n\n")
            f.write("**相关文档**:\n")
            for doc in docs[:10]:
                f.write(f"- {doc['path']}: {doc['responsibility']}\n")
        
        f.write(f"""
## 问题详情

""")
        for level in ['L1', 'L2', 'L3']:
            if issues_by_level[level]:
                f.write(f"\n### {level}问题详情\n\n")
                for issue_info in issues_by_level[level][:20]:
                    f.write(f"- **{issue_info['path']}**: {issue_info['issue']['type']} - {issue_info['issue']['description']}\n")
        
        f.write(f"""
## 改进建议

### 立即行动

1. 处理重复文档（合并或删除）
2. 修复重复的module_id
3. 补充缺失的INDEX文件

### 短期改进

1. 整合稀疏目录
2. 明确职责不清文档的职责
3. 优化目录结构

### 长期优化

1. 建立职责审查机制
2. 定期执行深度审计
3. 持续优化文档质量

---

**审计完成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")
    
    print(f"\n" + "=" * 80)
    print("审计完成")
    print("=" * 80)
    print(f"报告路径: {report_path}")
    print(f"数据路径: {data_path}")

if __name__ == '__main__':
    main()
