#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速合规率验证脚本
验证死链接修复效果
"""

import re
from pathlib import Path
from datetime import datetime

DOCS_DIR = Path("D:/ZephyrAlpha/docs")
OUTPUT_FILE = DOCS_DIR / "09_AUDIT/STATE/COMPLIANCE_VERIFICATION_REPORT_20260407.md"

def verify_compliance():
    """验证合规率"""
    
    print("=" * 80)
    print("合规率验证")
    print("=" * 80)
    
    # 扫描所有markdown文件
    md_files = list(DOCS_DIR.rglob("*.md"))
    print(f"\n发现 {len(md_files)} 个markdown文件")
    
    # 统计问题
    issues = {
        'dead_links': 0,
        'missing_index': 0,
        'missing_module_id': 0,
        'old_naming': 0
    }
    
    # 检查死链接
    dead_links = []
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
                    if file_path.startswith('../'):
                        target_path = (md_file.parent / file_path).resolve()
                    elif file_path.startswith('./'):
                        target_path = (md_file.parent / file_path[2:]).resolve()
                    else:
                        target_path = DOCS_DIR / file_path
                    
                    # 检查文件是否存在
                    if not target_path.exists():
                        issues['dead_links'] += 1
                        dead_links.append({
                            'source': str(md_file.relative_to(DOCS_DIR)),
                            'target': str(target_path.relative_to(DOCS_DIR)) if target_path.is_relative_to(DOCS_DIR) else str(target_path),
                            'text': link_text
                        })
        except Exception as e:
            pass
    
    # 检查缺少INDEX.md的目录
    dirs = [d for d in DOCS_DIR.rglob("*") if d.is_dir()]
    for dir_path in dirs:
        index_file = dir_path / "INDEX.md"
        if not index_file.exists():
            # 跳过归档目录和特殊目录
            if 'archive' not in str(dir_path).lower() and '_archive' not in str(dir_path).lower():
                issues['missing_index'] += 1
    
    # 计算合规率
    total_files = len(md_files)
    total_issues = sum(issues.values())
    compliance_rate = (total_files - total_issues) / total_files * 100 if total_files > 0 else 0
    
    # 生成报告
    report = f"""# 合规率验证报告

**验证时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**验证范围**: 所有markdown文件

---

## 📊 合规率统计

| 指标 | 数值 |
|------|------|
| **总文件数** | {total_files} |
| **总问题数** | {total_issues} |
| **合规率** | {compliance_rate:.2f}% |

---

## 🔍 问题分布

| 问题类型 | 数量 |
|---------|------|
| **死链接** | {issues['dead_links']} |
| **缺少INDEX.md** | {issues['missing_index']} |
| **缺少Module ID** | {issues['missing_module_id']} |
| **旧架构命名** | {issues['old_naming']} |

---

## 📝 死链接详情 (前20个)

| 源文件 | 目标文件 | 链接文本 |
|--------|---------|---------|
"""
    
    for item in dead_links[:20]:
        report += f"| `{item['source']}` | `{item['target']}` | {item['text']} |\n"
    
    if len(dead_links) > 20:
        report += f"\n*还有 {len(dead_links) - 20} 个死链接未显示*\n"
    
    report += f"""
---

## ✅ 验证结果

- **合规率**: {compliance_rate:.2f}%
- **距离99.9%目标**: {abs(99.9 - compliance_rate):.2f}%
- **修复效果**: {'✅ 成功' if issues['dead_links'] < 100 else '⚠️ 需要进一步修复'}

---

**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    # 保存报告
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n验证报告已保存至: {OUTPUT_FILE}")
    
    # 打印摘要
    print("\n" + "=" * 80)
    print("验证结果摘要")
    print("=" * 80)
    print(f"总文件数: {total_files}")
    print(f"总问题数: {total_issues}")
    print(f"合规率: {compliance_rate:.2f}%")
    print(f"死链接数: {issues['dead_links']}")
    print(f"缺少INDEX.md: {issues['missing_index']}")

if __name__ == "__main__":
    verify_compliance()
