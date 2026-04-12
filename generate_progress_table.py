#!/usr/bin/env python3
"""
从 complete-blueprint-overview.md 提取蓝图状态并生成进度表格。
"""
import re
from pathlib import Path

def extract_status(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找表格行，格式为：| 文档名称 | 优先级 | 状态 | 实施状态 | 说明 |
    # 使用正则表达式匹配
    pattern = r'\|\s*(?P<name>[^|]+)\s*\|\s*(?P<priority>[^|]+)\s*\|\s*(?P<status>[^|]+)\s*\|\s*(?P<impl_status>[^|]*)\s*\|\s*(?P<desc>[^|]*)\s*\|'
    # 但表格可能有多行，我们简化处理：逐行解析
    lines = content.split('\n')
    records = []
    in_table = False
    for line in lines:
        if line.strip().startswith('|') and '文档名称' in line:
            in_table = True
            continue
        if in_table and line.strip().startswith('|') and '---' not in line:
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) >= 3:
                name = parts[0]
                priority = parts[1] if len(parts) > 1 else ''
                status = parts[2] if len(parts) > 2 else ''
                impl_status = parts[3] if len(parts) > 3 else ''
                desc = parts[4] if len(parts) > 4 else ''
                records.append({
                    'name': name,
                    'priority': priority,
                    'status': status,
                    'impl_status': impl_status,
                    'desc': desc
                })
        if line.strip() == '' and in_table:
            in_table = False
    return records

def main():
    filepath = Path('docs/11_STRATEGIC_DECISION/complete-blueprint-overview.md')
    records = extract_status(filepath)
    
    # 输出为 Markdown 表格
    output = []
    output.append('## 📊 蓝图进度跟踪表')
    output.append('')
    output.append('| 蓝图文档 | 优先级 | 状态 | 实施状态 | 说明 |')
    output.append('|----------|--------|------|----------|------|')
    for r in records:
        output.append(f'| {r["name"]} | {r["priority"]} | {r["status"]} | {r["impl_status"]} | {r["desc"]} |')
    
    with open('progress_table.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))
    
    print(f"生成了 {len(records)} 条记录，保存到 progress_table.md")

if __name__ == '__main__':
    main()