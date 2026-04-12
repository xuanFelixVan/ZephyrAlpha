#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
全面死链接修复工具
扫描所有文档文件，批量修复死链接
"""

import re
import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import shutil

DOCS_DIR = Path("D:/ZephyrAlpha/docs")
OUTPUT_FILE = DOCS_DIR / "09_AUDIT/STATE/COMPREHENSIVE_DEAD_LINK_FIX_REPORT_20260407.md"

def scan_all_dead_links():
    """扫描所有文件中的死链接"""
    
    print("=" * 80)
    print("全面死链接扫描")
    print("=" * 80)
    
    dead_links = {
        'missing_file': [],
        'missing_anchor': [],
        'relative_path_error': [],
        'self_reference': []
    }
    
    # 扫描所有markdown文件
    md_files = list(DOCS_DIR.rglob("*.md"))
    print(f"\n发现 {len(md_files)} 个markdown文件")
    
    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取所有链接
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            all_links = re.findall(link_pattern, content)
            
            for link_text, link_path in all_links:
                # 跳过外部链接
                if link_path.startswith('http://') or link_path.startswith('https://'):
                    continue
                
                # 跳过特殊链接
                if link_path.startswith('#') or link_path.startswith('mailto:'):
                    continue
                
                # 分离文件路径和锚点
                if '#' in link_path:
                    file_path, anchor = link_path.split('#', 1)
                else:
                    file_path = link_path
                    anchor = None
                
                # 计算相对路径
                if file_path:
                    # 处理相对路径
                    if file_path.startswith('../'):
                        # 相对路径
                        target_path = (md_file.parent / file_path).resolve()
                    elif file_path.startswith('./'):
                        # 当前目录相对路径
                        target_path = (md_file.parent / file_path[2:]).resolve()
                    else:
                        # 绝对路径（相对于docs目录）
                        target_path = DOCS_DIR / file_path
                    
                    # 检查文件是否存在
                    if not target_path.exists():
                        # 检查是否是自引用
                        if target_path.resolve() == md_file.resolve():
                            dead_links['self_reference'].append({
                                'source_file': str(md_file.relative_to(DOCS_DIR)),
                                'link_text': link_text,
                                'link_path': link_path,
                                'reason': '自引用错误'
                            })
                        else:
                            dead_links['missing_file'].append({
                                'source_file': str(md_file.relative_to(DOCS_DIR)),
                                'link_text': link_text,
                                'link_path': link_path,
                                'target_file': str(target_path.relative_to(DOCS_DIR)) if target_path.is_relative_to(DOCS_DIR) else str(target_path),
                                'reason': '文件不存在'
                            })
                    elif anchor:
                        # 检查锚点是否存在
                        try:
                            with open(target_path, 'r', encoding='utf-8') as f:
                                target_content = f.read()
                            
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
                                if pattern in target_content:
                                    anchor_found = True
                                    break
                            
                            if not anchor_found:
                                dead_links['missing_anchor'].append({
                                    'source_file': str(md_file.relative_to(DOCS_DIR)),
                                    'link_text': link_text,
                                    'link_path': link_path,
                                    'target_file': str(target_path.relative_to(DOCS_DIR)),
                                    'anchor': anchor,
                                    'reason': '锚点不存在'
                                })
                        except Exception as e:
                            pass
        except Exception as e:
            print(f"处理文件失败: {md_file}, 错误: {str(e)}")
    
    return dead_links

def fix_dead_links(dead_links):
    """修复死链接"""
    
    print("\n" + "=" * 80)
    print("开始修复死链接")
    print("=" * 80)
    
    fixes = {
        'removed_links': 0,
        'removed_anchors': 0,
        'updated_links': 0,
        'skipped': 0
    }
    
    # 按源文件分组
    file_fixes = defaultdict(list)
    
    # 收集需要修复的链接
    for item in dead_links['missing_file']:
        file_fixes[item['source_file']].append({
            'type': 'missing_file',
            'link_text': item['link_text'],
            'link_path': item['link_path'],
            'action': 'remove'
        })
    
    for item in dead_links['missing_anchor']:
        file_fixes[item['source_file']].append({
            'type': 'missing_anchor',
            'link_text': item['link_text'],
            'link_path': item['link_path'],
            'anchor': item['anchor'],
            'action': 'remove_anchor'
        })
    
    for item in dead_links['self_reference']:
        file_fixes[item['source_file']].append({
            'type': 'self_reference',
            'link_text': item['link_text'],
            'link_path': item['link_path'],
            'action': 'remove'
        })
    
    # 批量修复文件
    for source_file, fix_list in file_fixes.items():
        file_path = DOCS_DIR / source_file
        
        if not file_path.exists():
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            for fix in fix_list:
                if fix['action'] == 'remove':
                    # 删除整个链接
                    pattern = re.escape(f"[{fix['link_text']}]({fix['link_path']})")
                    content = re.sub(pattern, fix['link_text'], content)
                    fixes['removed_links'] += 1
                
                elif fix['action'] == 'remove_anchor':
                    # 删除锚点，保留文件链接
                    if '#' in fix['link_path']:
                        file_link = fix['link_path'].split('#')[0]
                        pattern = re.escape(f"[{fix['link_text']}]({fix['link_path']})")
                        replacement = f"[{fix['link_text']}]({file_link})"
                        content = re.sub(pattern, replacement, content)
                        fixes['removed_anchors'] += 1
            
            # 保存修复后的文件
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"已修复: {source_file}")
        
        except Exception as e:
            print(f"修复失败: {source_file}, 错误: {str(e)}")
            fixes['skipped'] += 1
    
    return fixes

def generate_report(dead_links, fixes):
    """生成修复报告"""
    
    report = f"""# 全面死链接修复报告

**修复时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**扫描范围**: 所有markdown文件
**修复工具**: comprehensive_dead_link_fixer.py

---

## 📊 死链接统计

| 类型 | 数量 |
|------|------|
| **文件不存在** | {len(dead_links['missing_file'])} |
| **锚点不存在** | {len(dead_links['missing_anchor'])} |
| **自引用错误** | {len(dead_links['self_reference'])} |
| **总死链接数** | {sum(len(v) for v in dead_links.values())} |

---

## 🔧 修复统计

| 操作 | 数量 |
|------|------|
| **删除链接** | {fixes['removed_links']} |
| **删除锚点** | {fixes['removed_anchors']} |
| **更新链接** | {fixes['updated_links']} |
| **跳过** | {fixes['skipped']} |
| **总修复数** | {sum(fixes.values())} |

---

## 📁 文件不存在详情 (前20个)

| 源文件 | 链接文本 | 目标文件 | 原因 |
|--------|---------|---------|------|
"""
    
    for item in dead_links['missing_file'][:20]:
        report += f"| `{item['source_file']}` | {item['link_text']} | `{item['target_file']}` | {item['reason']} |\n"
    
    if len(dead_links['missing_file']) > 20:
        report += f"\n*还有 {len(dead_links['missing_file']) - 20} 个文件不存在的链接未显示*\n"
    
    report += f"""
---

## 🔗 锚点不存在详情 (前20个)

| 源文件 | 链接文本 | 目标文件 | 锚点 | 原因 |
|--------|---------|---------|------|------|
"""
    
    for item in dead_links['missing_anchor'][:20]:
        report += f"| `{item['source_file']}` | {item['link_text']} | `{item['target_file']}` | `#{item['anchor']}` | {item['reason']} |\n"
    
    if len(dead_links['missing_anchor']) > 20:
        report += f"\n*还有 {len(dead_links['missing_anchor']) - 20} 个锚点不存在的链接未显示*\n"
    
    report += f"""
---

## ✅ 修复结果

- **修复前死链接数**: {sum(len(v) for v in dead_links.values())}个
- **修复后死链接数**: 预计0个
- **修复成功率**: 预计100%

---

## 📝 后续建议

1. **验证修复**: 运行comprehensive_deep_audit.py验证修复效果
2. **定期检查**: 建议每周运行一次死链接检查
3. **预防措施**: 在文档创建时检查链接有效性

---

**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    return report

def main():
    """主函数"""
    
    # 扫描死链接
    dead_links = scan_all_dead_links()
    
    # 修复死链接
    fixes = fix_dead_links(dead_links)
    
    # 生成报告
    report = generate_report(dead_links, fixes)
    
    # 保存报告
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n修复报告已保存至: {OUTPUT_FILE}")
    
    # 打印摘要
    print("\n" + "=" * 80)
    print("修复完成摘要")
    print("=" * 80)
    print(f"总死链接数: {sum(len(v) for v in dead_links.values())}个")
    print(f"总修复数: {sum(fixes.values())}个")
    print(f"删除链接: {fixes['removed_links']}个")
    print(f"删除锚点: {fixes['removed_anchors']}个")
    print(f"更新链接: {fixes['updated_links']}个")

if __name__ == "__main__":
    main()
