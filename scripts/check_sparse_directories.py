#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
稀疏目录自动检测工具
功能：扫描文档目录，检测文件数少于阈值的稀疏目录，生成报告
"""

import os
import json
from datetime import datetime
from pathlib import Path

def detect_sparse_directories(root_path, threshold=3, exclude_dirs=None):
    """
    检测稀疏目录
    
    Args:
        root_path: 根目录路径
        threshold: 文件数阈值（默认3个）
        exclude_dirs: 排除的目录列表
    
    Returns:
        dict: 检测结果
    """
    if exclude_dirs is None:
        exclude_dirs = ['.git', '__pycache__', 'node_modules', '.venv']
    
    sparse_dirs = []
    total_dirs = 0
    total_files = 0
    
    for root, dirs, files in os.walk(root_path):
        # 排除特定目录
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        # 统计.md文件
        md_files = [f for f in files if f.endswith('.md')]
        total_files += len(md_files)
        
        if root == root_path:
            continue
        
        total_dirs += 1
        
        # 检测稀疏目录
        if len(md_files) < threshold and len(md_files) > 0:
            rel_path = os.path.relpath(root, root_path)
            sparse_dirs.append({
                'path': rel_path,
                'file_count': len(md_files),
                'files': md_files,
                'severity': 'high' if len(md_files) == 1 else 'medium'
            })
    
    return {
        'total_dirs': total_dirs,
        'total_files': total_files,
        'sparse_dir_count': len(sparse_dirs),
        'sparse_dirs': sparse_dirs,
        'threshold': threshold,
        'scan_time': datetime.now().isoformat()
    }

def generate_report(result, output_path):
    """生成检测报告"""
    report = f"""# 稀疏目录检测报告

## 📊 检测概要

- **扫描时间**: {result['scan_time']}
- **检测阈值**: 文件数 < {result['threshold']}
- **总目录数**: {result['total_dirs']}
- **总文件数**: {result['total_files']}
- **稀疏目录数**: {result['sparse_dir_count']}

---

## 🔍 稀疏目录列表

"""
    
    if result['sparse_dirs']:
        # 按严重程度分组
        high_severity = [d for d in result['sparse_dirs'] if d['severity'] == 'high']
        medium_severity = [d for d in result['sparse_dirs'] if d['severity'] == 'medium']
        
        if high_severity:
            report += "### 🔴 高优先级（仅1个文件）\n\n"
            for d in high_severity:
                report += f"- **{d['path']}** ({d['file_count']}个文件)\n"
                for f in d['files']:
                    report += f"  - {f}\n"
                report += "\n"
        
        if medium_severity:
            report += "### 🟡 中优先级（2个文件）\n\n"
            for d in medium_severity:
                report += f"- **{d['path']}** ({d['file_count']}个文件)\n"
                for f in d['files']:
                    report += f"  - {f}\n"
                report += "\n"
    else:
        report += "✅ 未发现稀疏目录\n"
    
    report += f"""
---

## 💡 改进建议

### 立即行动
1. 整合高优先级稀疏目录（仅1个文件的目录）
2. 补充中优先级稀疏目录的内容

### 长期优化
1. 建立文档数量预警机制
2. 定期执行稀疏目录检测
3. 制定目录整合标准

---

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
    # 配置
    root_path = r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY'
    output_dir = r'D:\ZephyrAlpha\docs\05_IMPLEMENTATION\04_OPERATIONS\audit_state'
    threshold = 3
    
    # 检测稀疏目录
    print(f'正在扫描: {root_path}')
    print(f'检测阈值: 文件数 < {threshold}')
    print()
    
    result = detect_sparse_directories(root_path, threshold)
    
    # 输出结果
    print(f'总目录数: {result["total_dirs"]}')
    print(f'总文件数: {result["total_files"]}')
    print(f'稀疏目录数: {result["sparse_dir_count"]}')
    print()
    
    if result['sparse_dirs']:
        print('稀疏目录列表:')
        for d in result['sparse_dirs']:
            severity = '🔴' if d['severity'] == 'high' else '🟡'
            print(f'{severity} {d["path"]} ({d["file_count"]}个文件)')
    else:
        print('✅ 未发现稀疏目录')
    
    # 保存JSON结果
    json_path = os.path.join(output_dir, 'sparse_directory_check_result.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f'\nJSON结果已保存: {json_path}')
    
    # 生成报告
    report_path = os.path.join(output_dir, 'SPARSE_DIRECTORY_CHECK_REPORT.md')
    generate_report(result, report_path)
    print(f'检测报告已生成: {report_path}')

if __name__ == '__main__':
    main()
