#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
稀疏目录分析与修复策略制定
分析文件数<3的目录，决定整合或补充策略
"""

import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY')

def analyze_sparse_directories():
    """分析稀疏目录"""
    sparse_dirs = []
    
    for root, dirs, files in os.walk(FACTOR_LIBRARY):
        # 只处理.md文件
        md_files = [f for f in files if f.endswith('.md')]
        file_count = len(md_files)
        
        # 稀疏目录定义：文件数<3
        if file_count < 3 and file_count > 0:
            rel_path = Path(root).relative_to(FACTOR_LIBRARY)
            sparse_dirs.append({
                'path': str(rel_path),
                'file_count': file_count,
                'files': md_files,
                'depth': len(rel_path.parts)
            })
    
    return sparse_dirs

def categorize_sparse_dirs(sparse_dirs):
    """对稀疏目录进行分类"""
    categories = {
        '一级目录': [],
        '二级目录': [],
        '三级目录': [],
        '四级及以上': []
    }
    
    for d in sparse_dirs:
        if d['depth'] == 1:
            categories['一级目录'].append(d)
        elif d['depth'] == 2:
            categories['二级目录'].append(d)
        elif d['depth'] == 3:
            categories['三级目录'].append(d)
        else:
            categories['四级及以上'].append(d)
    
    return categories

def determine_strategy(d):
    """决定修复策略"""
    files = d['files']
    file_count = d['file_count']
    path = d['path']
    
    # 策略1: 如果只有INDEX.md和README.md，建议补充内容
    if set(files) == {'INDEX.md', 'README.md'}:
        return '补充内容', '目录结构完整但内容稀疏，建议补充实际内容文档'
    
    # 策略2: 如果只有INDEX.md，建议补充README.md
    if files == ['INDEX.md']:
        return '补充README', '缺少README.md，建议补充说明文档'
    
    # 策略3: 如果只有README.md，建议补充INDEX.md
    if files == ['README.md']:
        return '补充INDEX', '缺少INDEX.md，建议补充索引文档'
    
    # 策略4: 如果是04_DATA_SOURCE下的子目录，建议保留
    if '04_DATA_SOURCE' in path:
        return '保留', '数据源模块目录，属于规划中的模块，建议保留'
    
    # 策略5: 其他情况，建议整合
    return '整合', '文件数过少，建议整合到上级目录或补充内容'

def generate_strategy_report(sparse_dirs, categories):
    """生成策略报告"""
    report = f"""# 稀疏目录分析与修复策略报告

## 执行概要

- **分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **分析范围**: D:\\ZephyrAlpha\\docs\\02_FACTOR_LIBRARY
- **稀疏目录定义**: 文件数<3的目录

## 统计概览

| 统计项 | 数量 |
|--------|------|
| 稀疏目录总数 | {len(sparse_dirs)} |
| 一级目录 | {len(categories['一级目录'])} |
| 二级目录 | {len(categories['二级目录'])} |
| 三级目录 | {len(categories['三级目录'])} |
| 四级及以上 | {len(categories['四级及以上'])} |

## 修复策略分类

"""
    
    # 按策略分组
    strategies = defaultdict(list)
    for d in sparse_dirs:
        strategy, reason = determine_strategy(d)
        strategies[strategy].append((d, reason))
    
    for strategy, items in strategies.items():
        report += f"### {strategy} ({len(items)}个目录)\n\n"
        
        for d, reason in items:
            report += f"#### {d['path']}\n"
            report += f"- **文件数**: {d['file_count']}\n"
            report += f"- **文件列表**: {', '.join(d['files'])}\n"
            report += f"- **修复建议**: {reason}\n\n"
    
    report += """## 推荐修复方案

### 方案1: 补充内容（推荐）

**适用目录**: 只有INDEX.md和README.md的目录

**操作步骤**:
1. 分析目录职责
2. 补充实际内容文档
3. 确保每个目录至少有3个文件

---

### 方案2: 补充README或INDEX

**适用目录**: 缺少INDEX.md或README.md的目录

**操作步骤**:
1. 补充缺失的标准文档
2. 确保目录结构完整

---

### 方案3: 保留规划目录

**适用目录**: 04_DATA_SOURCE下的子目录

**操作步骤**:
1. 保持现状
2. 标记为"规划中"状态
3. 后续开发时补充内容

---

## 执行建议

### 立即行动
- 补充缺失的README.md或INDEX.md

### 短期改进
- 为内容稀疏的目录补充实际内容

### 长期优化
- 定期审查目录结构
- 确保每个目录有足够的内容支撑

---

**分析完成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    return report

def main():
    """主函数"""
    print("=" * 80)
    print("稀疏目录分析与修复策略制定")
    print("=" * 80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 分析稀疏目录
    sparse_dirs = analyze_sparse_directories()
    print(f"\n发现稀疏目录: {len(sparse_dirs)}个")
    
    # 分类
    categories = categorize_sparse_dirs(sparse_dirs)
    
    # 生成报告
    report = generate_strategy_report(sparse_dirs, categories)
    
    # 保存报告
    report_path = Path(r'D:\ZephyrAlpha\docs\09_AUDIT\STATE\SPARSE_DIRECTORY_STRATEGY_REPORT.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n报告已生成: {report_path}")
    
    # 打印策略统计
    strategies = defaultdict(int)
    for d in sparse_dirs:
        strategy, _ = determine_strategy(d)
        strategies[strategy] += 1
    
    print("\n策略统计:")
    for strategy, count in strategies.items():
        print(f"  {strategy}: {count}个")

if __name__ == '__main__':
    main()
