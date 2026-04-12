# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import re

file_path = r'd:\ZephyrAlpha\docs\10_AI_WORKFLOW\SENTIMENT_ANALYSIS_SHORT_TERM_TECHNICAL_SPECIFICATION.md'

with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

lines = content.split('\n')
fixed_lines = []

for i, line in enumerate(lines, 1):
    if i <= 15:
        fixed_lines.append(line)
        continue
    
    if any(char in line for char in ['é', 'è', 'ç', 'å', 'æ', 'ð', 'ã', 'ä', 'ö', 'ü', 'ï', 'î', 'ê', 'ë']):
        try:
            fixed_line = line.encode('latin-1').decode('utf-8')
            fixed_lines.append(fixed_line)
        except:
            try:
                fixed_line = line.encode('cp1252').decode('utf-8')
                fixed_lines.append(fixed_line)
            except:
                fixed_lines.append(line)
    else:
        fixed_lines.append(line)

fixed_content = '\n'.join(fixed_lines)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print('文件编码修复完成！')
print('\n前100行:')
for i, line in enumerate(fixed_lines[:100], 1):
    print(f'{i}: {line}')
