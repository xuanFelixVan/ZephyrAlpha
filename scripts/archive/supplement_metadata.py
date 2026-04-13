#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
为重要文档补充完整元数据
"""

import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs')
OUTPUT_DIR = Path(r'D:\ZephyrAlpha\docs\09_AUDIT\STATE')

# 定义重要文档的优先级
IMPORTANT_PATTERNS = {
    'INDEX': {
        'pattern': 'INDEX.md',
        'priority': 1,
        'description': '索引文件'
    },
    'README': {
        'pattern': 'README.md',
        'priority': 1,
        'description': '说明文件'
    },
    'SITEMAP': {
        'pattern': 'SITEMAP.md',
        'priority': 1,
        'description': '站点地图'
    },
    'BLUEPRINT': {
        'pattern': '*BLUEPRINT.md',
        'priority': 2,
        'description': '蓝图文档'
    },
    'STANDARD': {
        'pattern': '*STANDARD*.md',
        'priority': 2,
        'description': '标准文档'
    },
    'GUIDE': {
        'pattern': '*GUIDE*.md',
        'priority': 2,
        'description': '指南文档'
    }
}

# 核心目录（优先处理）
CORE_DIRECTORIES = [
    '01_FRAMEWORK',
    '02_FACTOR_LIBRARY',
    '03_TRADING_TACTICS',
    '04_DATA_SOURCES',
    '05_IMPLEMENTATION',
    '09_AUDIT',
    '10_AI_WORKFLOW',
    '11_STRATEGIC_DECISION'
]

def identify_important_documents():
    """识别重要文档"""
    print("=" * 80)
    print("识别重要文档")
    print("=" * 80)
    
    important_docs = []
    
    # 扫描核心目录
    for core_dir in CORE_DIRECTORIES:
        dir_path = FACTOR_LIBRARY / core_dir
        if not dir_path.exists():
            continue
        
        # 扫描该目录下的所有文档
        for file_path in dir_path.rglob('*.md'):
            # 跳过audit_state和archive目录
            if 'audit_state' in str(file_path) or 'archive' in str(file_path).lower():
                continue
            
            rel_path = file_path.relative_to(FACTOR_LIBRARY)
            
            # 确定优先级
            priority = 99  # 默认优先级
            doc_type = '普通文档'
            
            for pattern_name, pattern_info in IMPORTANT_PATTERNS.items():
                if pattern_info['pattern'].startswith('*'):
                    # 通配符模式
                    if file_path.name.endswith(pattern_info['pattern'][1:]):
                        priority = pattern_info['priority']
                        doc_type = pattern_info['description']
                        break
                else:
                    # 精确匹配
                    if file_path.name == pattern_info['pattern']:
                        priority = pattern_info['priority']
                        doc_type = pattern_info['description']
                        break
            
            important_docs.append({
                'path': str(rel_path),
                'file': file_path.name,
                'parent': str(rel_path.parent),
                'priority': priority,
                'type': doc_type
            })
    
    # 按优先级排序
    important_docs.sort(key=lambda x: x['priority'])
    
    print(f"\n识别完成")
    print(f"重要文档总数: {len(important_docs)}")
    
    # 统计各类型文档数量
    type_stats = defaultdict(int)
    for doc in important_docs:
        type_stats[doc['type']] += 1
    
    print(f"\n文档类型统计:")
    for doc_type, count in sorted(type_stats.items()):
        print(f"  {doc_type}: {count}个")
    
    return important_docs

def check_metadata_completeness(file_path):
    """检查元数据完整性"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 检查是否有YAML元数据
        if not content.startswith('---'):
            return False, []
        
        yaml_end = content.find('---', 3)
        if yaml_end < 0:
            return False, []
        
        yaml_content = content[3:yaml_end]
        
        # 检查必需字段
        required_fields = ['module_id', 'version', 'status', 'created_date', 'owner']
        missing_fields = []
        
        for field in required_fields:
            if f'{field}:' not in yaml_content:
                missing_fields.append(field)
        
        return len(missing_fields) == 0, missing_fields
    
    except Exception as e:
        return False, ['读取失败']

def supplement_metadata(important_docs):
    """补充元数据"""
    print("\n" + "=" * 80)
    print("补充元数据")
    print("=" * 80)
    
    supplemented_count = 0
    skipped_count = 0
    failed_count = 0
    
    # 只处理优先级1和2的文档
    high_priority_docs = [doc for doc in important_docs if doc['priority'] <= 2]
    
    print(f"\n高优先级文档: {len(high_priority_docs)}个")
    
    for doc in high_priority_docs[:50]:  # 限制处理数量
        file_path = FACTOR_LIBRARY / doc['path']
        
        if not file_path.exists():
            continue
        
        # 检查元数据完整性
        is_complete, missing_fields = check_metadata_completeness(file_path)
        
        if is_complete:
            skipped_count += 1
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            # 生成module_id
            module_id = file_path.stem.upper()
            
            # 生成标准化的元数据
            metadata = f"""---
module_id: {module_id}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: {doc['type']}
applicable_scope: {doc['parent']}
compliance_level: 专业标准
parent_document: ../INDEX.md
---

"""
            
            # 如果已有YAML元数据，替换它
            if content.startswith('---'):
                yaml_end = content.find('---', 3)
                if yaml_end > 0:
                    content = metadata + content[yaml_end + 3:]
                else:
                    content = metadata + content
            else:
                content = metadata + content
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  补充: {doc['path']}")
            supplemented_count += 1
        
        except Exception as e:
            print(f"  失败: {doc['path']} - {e}")
            failed_count += 1
    
    print(f"\n补充完成")
    print(f"补充文档: {supplemented_count}")
    print(f"跳过文档: {skipped_count}")
    print(f"失败文档: {failed_count}")
    
    return supplemented_count, skipped_count, failed_count

def generate_report(important_docs, supplemented_count, skipped_count, failed_count):
    """生成报告"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = OUTPUT_DIR / f'METADATA_SUPPLEMENT_REPORT_{timestamp}.md'
    
    # 按类型分组
    grouped_docs = defaultdict(list)
    for doc in important_docs:
        grouped_docs[doc['type']].append(doc)
    
    report_content = f"""---
module_id: METADATA_SUPPLEMENT_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: 补充报告
applicable_scope: 元数据补充
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# 元数据补充报告

> **核心职责**: 记录元数据补充的过程和结果
> **职责边界**: 
> - [OK] 本文档负责：补充记录、效果评估、后续建议
> - [NO] 本文档不负责：后续审计执行、新问题发现

---

## 补充概要

**补充时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**补充范围**: 重要文档（优先级1和2）  
**补充方法**: 自动补充  
**补充结论**: 成功补充元数据

---

## 补充统计

| 统计项 | 数量 | 说明 |
|--------|------|------|
| **重要文档总数** | {len(important_docs)} | 识别的重要文档 |
| **补充文档** | {supplemented_count} | 成功补充元数据 |
| **跳过文档** | {skipped_count} | 已有完整元数据 |
| **失败文档** | {failed_count} | 补充失败 |

---

## 文档类型统计

| 类型 | 数量 | 说明 |
|------|------|------|
"""
    
    for doc_type, docs in sorted(grouped_docs.items()):
        report_content += f"| **{doc_type}** | {len(docs)} | - |\n"
    
    report_content += f"""

---

## 后续建议

### 立即行动

1. [x] 识别重要文档
2. [x] 补充元数据
3. [ ] 验证补充效果

### 持续改进

1. [ ] 为其他文档补充元数据
2. [ ] 建立元数据检查机制
3. [ ] 持续优化文档质量

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本，元数据补充报告 | 首席文档架构师 |
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n报告已生成: {report_path}")
    return report_path

if __name__ == '__main__':
    # 识别重要文档
    important_docs = identify_important_documents()
    
    # 补充元数据
    supplemented_count, skipped_count, failed_count = supplement_metadata(important_docs)
    
    # 生成报告
    report_path = generate_report(important_docs, supplemented_count, skipped_count, failed_count)
    
    print("\n" + "=" * 80)
    print("元数据补充完成")
    print("=" * 80)
    print(f"重要文档总数: {len(important_docs)}")
    print(f"补充文档: {supplemented_count}")
    print(f"跳过文档: {skipped_count}")
    print(f"失败文档: {failed_count}")
    print(f"报告位置: {report_path}")
