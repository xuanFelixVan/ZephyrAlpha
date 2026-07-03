#!/usr/bin/env python3
"""检查5.1-5.55范围内所有file:///路径的文件是否存在"""
import re
import os

content = open(r'D:\ZephyrAlpha\docs\02_enterprise_architecture\architecture_debt_registry.md', encoding='utf-8').read()
lines = content.splitlines()

in_range = False
paths = {}  # path -> [line_numbers]
for idx, l in enumerate(lines):
    m = re.match(r'^###\s+5\.(\d+)\s', l)
    if m:
        num = int(m.group(1))
        in_range = 1 <= num <= 55
        continue
    if not in_range:
        continue
    for m2 in re.finditer(r'file:///d:/ZephyrAlpha/([^\s)"]+)', l):
        rel = m2.group(1).replace('/', os.sep)
        paths.setdefault(rel, []).append(idx + 1)

missing = {}
exists_count = 0
for p, lns in paths.items():
    full = os.path.join(r'D:\ZephyrAlpha', p)
    if os.path.exists(full):
        exists_count += 1
    else:
        missing[p] = lns

print(f'5.1-5.55 range: total={len(paths)}, exists={exists_count}, missing={len(missing)}')
print('---MISSING---')
for p, lns in sorted(missing.items()):
    print(f'  L{lns[0]}: {p}')
