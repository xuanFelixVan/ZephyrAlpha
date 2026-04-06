#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
稀疏目录分析和治理工具
功能：分析稀疏目录，决定补充内容还是整合
"""

import os
import re
from pathlib import Path
from datetime import datetime

def analyze_sparse_directories(root_path, threshold=3):
    """
    分析稀疏目录
    
    Args:
        root_path: 根目录路径
        threshold: 文件数阈值
    
    Returns:
        dict: 分析结果
    """
    sparse_dirs = []
    
    for root, dirs, files in os.walk(root_path):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        
        if root == root_path:
            continue
        
        # 统计.md文件
        md_files = [f for f in files if f.endswith('.md')]
        
        if len(md_files) < threshold and len(md_files) > 0:
            rel_path = os.path.relpath(root, root_path)
            
            # 分析文件类型
            has_blueprint = 'BLUEPRINT.md' in md_files
            has_index = 'INDEX.md' in md_files
            has_readme = 'README.md' in md_files
            
            # 判断治理策略
            if has_blueprint and has_index:
                strategy = '补充内容'
                reason = '蓝图+索引文件，需要补充详细文档'
            elif has_index and not has_blueprint:
                strategy = '补充蓝图'
                reason = '仅有索引文件，需要补充蓝图'
            elif has_blueprint and not has_index:
                strategy = '补充索引'
                reason = '仅有蓝图文件，需要补充索引'
            else:
                strategy = '评估整合'
                reason = '文件结构不完整，评估是否整合到父目录'
            
            sparse_dirs.append({
                'path': rel_path,
                'file_count': len(md_files),
                'files': md_files,
                'has_blueprint': has_blueprint,
                'has_index': has_index,
                'has_readme': has_readme,
                'strategy': strategy,
                'reason': reason
            })
    
    return sparse_dirs

def generate_governance_report(sparse_dirs, output_path):
    """生成治理报告"""
    report = f"""# 稀疏目录治理报告

## 📊 治理概要

- **治理时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **治理范围**: Alpha因子层（02_FACTOR_LIBRARY）
- **稀疏目录数**: {len(sparse_dirs)}

---

## 📋 稀疏目录分析

"""
    
    # 按治理策略分组
    strategies = {}
    for d in sparse_dirs:
        strategy = d['strategy']
        if strategy not in strategies:
            strategies[strategy] = []
        strategies[strategy].append(d)
    
    for strategy, dirs in strategies.items():
        report += f"### {strategy} ({len(dirs)}个)\n\n"
        
        for d in dirs:
            report += f"#### {d['path']}\n\n"
            report += f"- **文件数**: {d['file_count']}\n"
            report += f"- **文件列表**: {', '.join(d['files'])}\n"
            report += f"- **治理策略**: {d['strategy']}\n"
            report += f"- **治理原因**: {d['reason']}\n"
            report += f"- **蓝图文件**: {'✅' if d['has_blueprint'] else '❌'}\n"
            report += f"- **索引文件**: {'✅' if d['has_index'] else '❌'}\n"
            report += f"- **README文件**: {'✅' if d['has_readme'] else '❌'}\n"
            report += "\n"
    
    report += f"""---

## 🎯 治理建议

### 立即执行

"""
    
    # 补充内容的目录
    supplement_dirs = [d for d in sparse_dirs if d['strategy'] == '补充内容']
    if supplement_dirs:
        report += f"#### 补充内容 ({len(supplement_dirs)}个)\n\n"
        for d in supplement_dirs:
            report += f"- **{d['path']}**: 补充详细文档\n"
        report += "\n"
    
    # 补充蓝图的目录
    add_blueprint_dirs = [d for d in sparse_dirs if d['strategy'] == '补充蓝图']
    if add_blueprint_dirs:
        report += f"#### 补充蓝图 ({len(add_blueprint_dirs)}个)\n\n"
        for d in add_blueprint_dirs:
            report += f"- **{d['path']}**: 创建BLUEPRINT.md\n"
        report += "\n"
    
    # 补充索引的目录
    add_index_dirs = [d for d in sparse_dirs if d['strategy'] == '补充索引']
    if add_index_dirs:
        report += f"#### 补充索引 ({len(add_index_dirs)}个)\n\n"
        for d in add_index_dirs:
            report += f"- **{d['path']}**: 创建INDEX.md\n"
        report += "\n"
    
    report += f"""### 评估整合

"""
    
    # 评估整合的目录
    evaluate_dirs = [d for d in sparse_dirs if d['strategy'] == '评估整合']
    if evaluate_dirs:
        report += f"#### 需要评估 ({len(evaluate_dirs)}个)\n\n"
        for d in evaluate_dirs:
            report += f"- **{d['path']}**: 评估是否整合到父目录\n"
        report += "\n"
    
    report += f"""---

## 📝 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本 |
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return report

def main():
    """主函数"""
    root_path = r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY'
    output_dir = r'D:\ZephyrAlpha\docs\05_IMPLEMENTATION\04_OPERATIONS\audit_state'
    
    print("=" * 80)
    print("稀疏目录分析和治理")
    print("=" * 80)
    print()
    
    # 分析稀疏目录
    print("1. 分析稀疏目录...")
    sparse_dirs = analyze_sparse_directories(root_path)
    print(f"  发现稀疏目录: {len(sparse_dirs)}个")
    print()
    
    # 统计治理策略
    strategies = {}
    for d in sparse_dirs:
        strategy = d['strategy']
        strategies[strategy] = strategies.get(strategy, 0) + 1
    
    print("2. 治理策略分布:")
    for strategy, count in strategies.items():
        print(f"  {strategy}: {count}个")
    print()
    
    # 生成报告
    report_path = os.path.join(output_dir, 'SPARSE_DIRECTORY_GOVERNANCE_REPORT.md')
    generate_governance_report(sparse_dirs, report_path)
    print(f"✅ 报告已生成: {report_path}")
    print()
    print("=" * 80)
    print("分析完成")
    print("=" * 80)

if __name__ == '__main__':
    main()
