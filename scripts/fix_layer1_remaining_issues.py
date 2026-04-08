"""
修复剩余的职责重叠问题
"""
import os
from pathlib import Path
import yaml
from datetime import datetime

from collections import defaultdict

import re

import json

def fix_remaining_issues():
    """修复剩余的职责重叠问题"""
    base_path = Path("d:/ZephyrAlpha/docs/02_FACTOR_LIBRARY/04_DATA_SOURCE")
    
    # 需要修复的文件列表
    files_to_fix = {
        # 系统架构 - 重复
        'DATA_SECURITY_PRIVACY/INDEX.md': '数据安全隐私模块导航',
        'DATA_STANDARDIZATION/INDEX.md': '数据标准化模块导航',
        'DATA_VERSION_CONTROL/INDEX.md': '数据版本控制模块导航',
        'TIME_SERIES_STORAGE/INDEX.md': '时序存储模块导航',
        
        # 文档治理 - 重复
        'DATA_SECURITY_PRIVACY/INDEX.md': '数据安全隐私模块导航',
        'DATA_STANDARDIZATION/INDEX.md': '数据标准化模块导航',
        'DATA_VERSION_CONTROL/INDEX.md': '数据版本控制模块导航',
        'TIME_SERIES_STORAGE/INDEX.md': '时序存储模块导航',
    }
    
    # 索引不完整问题 - 需要重建INDEX.md
    index_file = base_path / "INDEX.md"
    
    print("="*80)
    print("Layer 1 剩余问题修复")
    print("="*80)
    print(f"修复时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 修复职责重叠
    fixed_count = 0
    for file_path, new_resp in files_to_fix.items():
        full_path = base_path / file_path
        
        if not full_path.exists():
            print(f"  ⚠️ 文件不存在: {file_path}")
            continue
            
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 提取YAML
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    yaml_data = yaml.safe_load(parts[1]) or {}
                    
                    # 更新职责
                    yaml_data['responsibility'] = new_resp
                    
                    # 重新生成YAML
                    yaml_str = yaml.dump(yaml_data, allow_unicode=True, sort_keys=False, default_flow_style=False)
                    
                    # 替换内容
                    new_content = f"---\n{yaml_str}---{parts[2]}"
                    
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                        
                    print(f"  ✓ {file_path}: {new_resp}")
                    fixed_count += 1
                    
        except Exception as e:
            print(f"  ⚠️ 修复失败: {file_path} - {str(e)}")
            
    print()
    
    # 重建INDEX.md
    print("重建INDEX.md...")
    print("-"*80)
    
    # 收集所有文档
    all_docs = []
    for md_file in base_path.rglob("*.md"):
        if md_file.name == "INDEX.md":
            continue
        rel_path = md_file.relative_to(base_path)
        all_docs.append(str(rel_path).replace('\\', '/'))
        
    # 按目录分组
    grouped = defaultdict(list)
    for doc in all_docs:
        parts = Path(doc).parts
        if len(parts) > 1:
            group = parts[0]
            grouped[group].append(doc)
        else:
            grouped['root'].append(doc)
            
    # 生成新的INDEX.md内容
    index_content = f"""---
module_id: LAYER1_INDEX_001
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席架构师
standard_type: 专业量化机构文档
responsibility: Layer 1数据预处理层总索引与模块导航
layer: "Layer 1 (数据预处理层)"
---

# Layer 1 数据预处理层索引

> **核心职责**: Layer 1数据预处理层总索引与模块导航
> **职责边界**: 
> - ✅ 本文档负责：Layer 1所有模块的导航和索引
> - ❌ 本文档不负责：具体模块的详细设计

**文档总数**: {len(all_docs)}

---

## 📁 模块导航

"""
    
    # 添加各模块的索引
    for group, docs in sorted(grouped.items()):
        if group != 'root':
            index_content += f"\n### {group}\n\n"
            for doc in sorted(docs):
                doc_name = Path(doc).stem
                index_content += f"- [{doc_name}]({doc})\n"
        else:
            index_content += f"\n### 根目录文档\n\n"
            for doc in sorted(docs):
                doc_name = Path(doc).stem
                index_content += f"- [{doc_name}]({doc})\n"
                
    index_content += """
---

## 📊 快速统计

| 模块类别 | 文档数量 |
|--------|--------|
"""
    
    # 添加统计
    for group, docs in sorted(grouped.items()):
        index_content += f"| {group} | {len(docs)} |\n"
        
    index_content += f"| **总计** | **{len(all_docs)}** |\n\n"
    
    index_content += """
---

## 📋 变更历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|---------|------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本创建 | 首席架构师 |

---

**文档结束**
"""
    
    # 写入INDEX.md
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(index_content)
        
    print(f"✅ INDEX.md已重建")
    
    print()
    print(f"修复完成: {fixed_count} 个职责问题")
    print("="*80)

if __name__ == "__main__":
    fix_remaining_issues()
