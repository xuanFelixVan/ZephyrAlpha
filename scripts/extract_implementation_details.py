#!/usr/bin/env python3
"""
从 remaining-blueprints-implementation-plan.md 提取实施计划详情，输出为 Markdown 格式。
"""

import re
from pathlib import Path

def extract_sections(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 找到 "## 一、剩余P0级蓝图清单" 和 "## 二、剩余P1级蓝图清单"
    # 我们简单起见，直接截取
    lines = content.split('\n')
    p0_start = None
    p1_start = None
    for i, line in enumerate(lines):
        if line.strip() == '## 一、剩余P0级蓝图清单':
            p0_start = i
        elif line.strip() == '## 二、剩余P1级蓝图清单':
            p1_start = i

    if p0_start is None or p1_start is None:
        print("未找到章节")
        return []

    # 提取 P0 部分（从 p0_start 到 p1_start）
    p0_lines = lines[p0_start:p1_start]
    # 提取 P1 部分（从 p1_start 到文件结束）
    p1_lines = lines[p1_start:]

    # 解析每个蓝图块
    sections = []
    current = None
    for line in p0_lines + p1_lines:
        if line.startswith('### '):
            if current:
                sections.append(current)
            title = line[4:].strip()
            current = {'title': title, 'content': []}
        elif current is not None:
            current['content'].append(line)
    if current:
        sections.append(current)

    return sections

def main():
    filepath = Path('docs/11_STRATEGIC_DECISION/remaining-blueprints-implementation-plan.md')
    sections = extract_sections(filepath)

    # 输出为 Markdown
    output = []
    for sec in sections:
        output.append(f'### {sec["title"]}')
        output.extend(sec['content'])
        output.append('')  # 空行

    with open('implementation_details.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    print(f"提取了 {len(sections)} 个蓝图详情，已保存到 implementation_details.md")

if __name__ == '__main__':
    main()
