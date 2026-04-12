#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
专业蓝图文件治理 - 稀疏目录处理
基于五大原则：职责驱动、索引完备、版本隔离、文档代码对应、命名规范
"""

import re
from pathlib import Path
from datetime import datetime

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY')

def analyze_sparse_directories():
    """分析稀疏目录"""
    print("=" * 80)
    print("分析稀疏目录")
    print("=" * 80)
    
    sparse_dirs = []
    
    for dir_path in FACTOR_LIBRARY.rglob('*'):
        if not dir_path.is_dir():
            continue
        
        files = list(dir_path.glob('*.md'))
        file_count = len(files)
        has_index = (dir_path / 'INDEX.md').exists()
        has_readme = (dir_path / 'README.md').exists()
        has_other_docs = any(f.stem not in ['INDEX', 'README'] for f in files)
        
        rel_path = dir_path.relative_to(FACTOR_LIBRARY)
        
        if file_count < 3:
            sparse_dirs.append({
                'path': dir_path,
                'rel_path': str(rel_path),
                'file_count': file_count,
                'has_index': has_index,
                'has_readme': has_readme,
                'has_other_docs': has_other_docs,
                'files': [f.name for f in files]
            })
    
    print(f"\n发现稀疏目录: {len(sparse_dirs)}个")
    
    empty_dirs = [d for d in sparse_dirs if d['file_count'] == 0]
    readme_only = [d for d in sparse_dirs if d['file_count'] == 1 and d['has_readme']]
    other_single = [d for d in sparse_dirs if d['file_count'] == 1 and not d['has_readme']]
    two_files = [d for d in sparse_dirs if d['file_count'] == 2]
    
    print(f"空目录: {len(empty_dirs)}个")
    print(f"只有README: {len(readme_only)}个")
    print(f"只有其他文档: {len(other_single)}个")
    print(f"两个文件: {len(two_files)}个")
    
    return sparse_dirs, empty_dirs, readme_only, other_single, two_files

def evaluate_directory_necessity(sparse_dirs):
    """评估目录存在的必要性"""
    print("\n" + "=" * 80)
    print("评估目录存在的必要性")
    print("=" * 80)
    
    keep_dirs = []
    merge_dirs = []
    delete_dirs = []
    
    core_modules = [
        '01_STANDARDS', '02_ALPHA_FACTORS_INDEX', '03_RISK_FACTORS',
        '04_DATA_SOURCE', '05_BACKTEST', '06_REGISTRY',
        '07_FACTOR_MONITORING', '09_AUDIT', '10_MANUAL',
        '00_GOVERNANCE'
    ]
    
    for d in sparse_dirs:
        rel_path = d['rel_path']
        
        if d['file_count'] == 0:
            delete_dirs.append(d)
            print(f"\n删除（空目录）: {rel_path}")
            continue
        
        dir_name = Path(rel_path).name
        
        is_core = dir_name in core_modules
        is_submodule = any(rel_path.startswith(m) for m in core_modules)
        
        if is_core or (is_submodule and d['has_other_docs']):
            keep_dirs.append(d)
            print(f"\n保留（核心模块）: {rel_path}")
        elif d['has_other_docs']:
            keep_dirs.append(d)
            print(f"\n保留（有内容）: {rel_path}")
        else:
            merge_dirs.append(d)
            print(f"\n待整合: {rel_path}")
    
    print(f"\n保留目录: {len(keep_dirs)}个")
    print(f"待整合目录: {len(merge_dirs)}个")
    print(f"删除目录: {len(delete_dirs)}个")
    
    return keep_dirs, merge_dirs, delete_dirs

def create_index_files(keep_dirs):
    """为保留的目录创建INDEX文件"""
    print("\n" + "=" * 80)
    print("创建INDEX文件")
    print("=" * 80)
    
    created_count = 0
    
    for d in keep_dirs:
        if d['has_index']:
            continue
        
        index_path = d['path'] / 'INDEX.md'
        dir_name = Path(d['rel_path']).name
        
        index_content = f"""---
module_id: FACTOR_LIBRARY_{re.sub(r'[^A-Z0-9]', '_', dir_name.upper())}_INDEX
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 文档管理团队
responsibility:
  - {dir_name}目录索引与导航
standard_type: 索引文档
applicable_scope: 因子库
compliance_level: 专业标准
---

# {dir_name} 目录索引

> **核心职责**: {dir_name}目录导航、文档索引和快速定位
> **职责边界**: 
> - ✅ 本文档负责：目录导航、文档索引、快速定位
> - ❌ 本文档不负责：具体实现细节、其他模块内容

---

## 目录结构

"""
        
        for file_name in d['files']:
            if file_name != 'INDEX.md':
                file_stem = Path(file_name).stem
                index_content += f"- [{file_stem}](./{file_name})\n"
        
        index_content += f"""
---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本 | 文档管理团队 |
"""
        
        try:
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(index_content)
            
            print(f"\n创建: {d['rel_path']}/INDEX.md")
            created_count += 1
        except Exception as e:
            print(f"\n创建失败: {d['rel_path']}/INDEX.md")
            print(f"  错误: {e}")
    
    print(f"\n创建INDEX文件: {created_count}")
    return created_count

def delete_empty_directories(delete_dirs):
    """删除空目录"""
    print("\n" + "=" * 80)
    print("删除空目录")
    print("=" * 80)
    
    deleted_count = 0
    
    for d in delete_dirs:
        try:
            if not list(d['path'].iterdir()):
                d['path'].rmdir()
                print(f"\n删除: {d['rel_path']}")
                deleted_count += 1
            else:
                print(f"\n跳过（非空）: {d['rel_path']}")
        except Exception as e:
            print(f"\n删除失败: {d['rel_path']}")
            print(f"  错误: {e}")
    
    print(f"\n删除目录: {deleted_count}")
    return deleted_count

def main():
    """主函数"""
    print("=" * 80)
    print("专业蓝图文件治理 - 稀疏目录处理")
    print("=" * 80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n基于五大原则：职责驱动、索引完备、版本隔离、文档代码对应、命名规范")
    
    sparse_dirs, empty_dirs, readme_only, other_single, two_files = analyze_sparse_directories()
    keep_dirs, merge_dirs, delete_dirs = evaluate_directory_necessity(sparse_dirs)
    created_count = create_index_files(keep_dirs)
    deleted_count = delete_empty_directories(delete_dirs)
    
    print("\n" + "=" * 80)
    print("治理完成")
    print("=" * 80)
    print(f"稀疏目录: {len(sparse_dirs)}")
    print(f"保留目录: {len(keep_dirs)}")
    print(f"待整合目录: {len(merge_dirs)}")
    print(f"删除目录: {len(delete_dirs)}")
    print(f"创建INDEX: {created_count}")
    print(f"删除目录: {deleted_count}")

if __name__ == '__main__':
    main()
