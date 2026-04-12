#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
System_Manifest.md死链接详细分析工具
分析所有死链接的类型和分布，生成修复建议
"""

import re
import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime

DOCS_DIR = Path("D:/ZephyrAlpha/docs")
MANIFEST_FILE = DOCS_DIR / "System_Manifest.md"
OUTPUT_FILE = DOCS_DIR / "09_AUDIT/STATE/SYSTEM_MANIFEST_DEAD_LINK_ANALYSIS_20260407.md"

def analyze_dead_links():
    """分析System_Manifest.md中的所有死链接"""
    
    print("=" * 80)
    print("System_Manifest.md死链接详细分析")
    print("=" * 80)
    
    if not MANIFEST_FILE.exists():
        print(f"错误: System_Manifest.md文件不存在: {MANIFEST_FILE}")
        return
    
    with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取所有链接
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    all_links = re.findall(link_pattern, content)
    
    print(f"\n发现 {len(all_links)} 个链接")
    
    # 分类统计
    dead_links = {
        'missing_file': [],
        'missing_anchor': [],
        'missing_directory': [],
        'other': []
    }
    
    for link_text, link_path in all_links:
        # 跳过外部链接
        if link_path.startswith('http://') or link_path.startswith('https://'):
            continue
        
        # 分离文件路径和锚点
        if '#' in link_path:
            file_path, anchor = link_path.split('#', 1)
        else:
            file_path = link_path
            anchor = None
        
        # 检查文件是否存在
        full_path = DOCS_DIR / file_path
        
        if not full_path.exists():
            # 检查是否是目录不存在
            parent_dir = full_path.parent
            if not parent_dir.exists():
                dead_links['missing_directory'].append({
                    'text': link_text,
                    'path': link_path,
                    'file': file_path,
                    'reason': '目录不存在'
                })
            else:
                dead_links['missing_file'].append({
                    'text': link_text,
                    'path': link_path,
                    'file': file_path,
                    'reason': '文件不存在'
                })
        elif anchor:
            # 检查锚点是否存在
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                
                # 检查锚点格式
                anchor_patterns = [
                    f'<a name="{anchor}"></a>',
                    f'<a id="{anchor}"></a>',
                    f'{{#{anchor}}}',
                    f'## {anchor}',
                    f'### {anchor}',
                ]
                
                anchor_found = False
                for pattern in anchor_patterns:
                    if pattern in file_content:
                        anchor_found = True
                        break
                
                if not anchor_found:
                    dead_links['missing_anchor'].append({
                        'text': link_text,
                        'path': link_path,
                        'file': file_path,
                        'anchor': anchor,
                        'reason': '锚点不存在'
                    })
            except Exception as e:
                dead_links['other'].append({
                    'text': link_text,
                    'path': link_path,
                    'file': file_path,
                    'reason': f'检查失败: {str(e)}'
                })
    
    # 生成报告
    report = generate_report(dead_links, len(all_links))
    
    # 保存报告
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n分析报告已保存至: {OUTPUT_FILE}")
    
    # 打印摘要
    print("\n" + "=" * 80)
    print("死链接分类统计")
    print("=" * 80)
    print(f"总链接数: {len(all_links)}")
    print(f"文件不存在: {len(dead_links['missing_file'])}个")
    print(f"锚点不存在: {len(dead_links['missing_anchor'])}个")
    print(f"目录不存在: {len(dead_links['missing_directory'])}个")
    print(f"其他问题: {len(dead_links['other'])}个")
    print(f"总死链接数: {sum(len(v) for v in dead_links.values())}个")

def generate_report(dead_links, total_links):
    """生成详细分析报告"""
    
    report = f"""# System_Manifest.md死链接详细分析报告

**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**分析文件**: System_Manifest.md
**总链接数**: {total_links}
**总死链接数**: {sum(len(v) for v in dead_links.values())}

---

## 📊 死链接分类统计

| 类型 | 数量 | 占比 |
|------|------|------|
| **文件不存在** | {len(dead_links['missing_file'])} | {len(dead_links['missing_file'])/total_links*100:.2f}% |
| **锚点不存在** | {len(dead_links['missing_anchor'])} | {len(dead_links['missing_anchor'])/total_links*100:.2f}% |
| **目录不存在** | {len(dead_links['missing_directory'])} | {len(dead_links['missing_directory'])/total_links*100:.2f}% |
| **其他问题** | {len(dead_links['other'])} | {len(dead_links['other'])/total_links*100:.2f}% |
| **总计** | {sum(len(v) for v in dead_links.values())} | {sum(len(v) for v in dead_links.values())/total_links*100:.2f}% |

---

"""
    
    # 文件不存在
    if dead_links['missing_file']:
        report += f"""## 📁 文件不存在 ({len(dead_links['missing_file'])}个)

| 链接文本 | 文件路径 | 原因 |
|---------|---------|------|
"""
        for item in dead_links['missing_file'][:20]:  # 只显示前20个
            report += f"| {item['text']} | `{item['file']}` | {item['reason']} |\n"
        
        if len(dead_links['missing_file']) > 20:
            report += f"\n*还有 {len(dead_links['missing_file']) - 20} 个文件不存在的链接未显示*\n"
        
        report += "\n---\n\n"
    
    # 锚点不存在
    if dead_links['missing_anchor']:
        report += f"""## 🔗 锚点不存在 ({len(dead_links['missing_anchor'])}个)

| 链接文本 | 文件路径 | 锚点 | 原因 |
|---------|---------|------|------|
"""
        for item in dead_links['missing_anchor'][:20]:  # 只显示前20个
            report += f"| {item['text']} | `{item['file']}` | `#{item['anchor']}` | {item['reason']} |\n"
        
        if len(dead_links['missing_anchor']) > 20:
            report += f"\n*还有 {len(dead_links['missing_anchor']) - 20} 个锚点不存在的链接未显示*\n"
        
        report += "\n---\n\n"
    
    # 目录不存在
    if dead_links['missing_directory']:
        report += f"""## 📂 目录不存在 ({len(dead_links['missing_directory'])}个)

| 链接文本 | 文件路径 | 原因 |
|---------|---------|------|
"""
        for item in dead_links['missing_directory']:
            report += f"| {item['text']} | `{item['file']}` | {item['reason']} |\n"
        
        report += "\n---\n\n"
    
    # 其他问题
    if dead_links['other']:
        report += f"""## ⚠️ 其他问题 ({len(dead_links['other'])}个)

| 链接文本 | 文件路径 | 原因 |
|---------|---------|------|
"""
        for item in dead_links['other']:
            report += f"| {item['text']} | `{item['file']}` | {item['reason']} |\n"
        
        report += "\n---\n\n"
    
    # 修复建议
    report += f"""## 💡 修复建议

### 优先级P0: 文件不存在 ({len(dead_links['missing_file'])}个)

**修复方式**:
1. 创建缺失的文件
2. 或更新链接指向正确的文件
3. 或删除无效链接

### 优先级P1: 锚点不存在 ({len(dead_links['missing_anchor'])}个)

**修复方式**:
1. 更新锚点指向正确的章节
2. 或删除锚点，只保留文件链接
3. 或在目标文件中创建对应章节

### 优先级P2: 目录不存在 ({len(dead_links['missing_directory'])}个)

**修复方式**:
1. 创建缺失的目录
2. 或更新链接指向正确的目录

---

## 📝 修复脚本建议

建议创建自动化修复脚本，批量处理以下问题：

1. **批量删除无效锚点**: 删除所有指向不存在章节的锚点
2. **批量更新文件路径**: 更新指向错误路径的链接
3. **批量创建缺失文件**: 创建必要的占位文件

---

**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    return report

if __name__ == "__main__":
    analyze_dead_links()
