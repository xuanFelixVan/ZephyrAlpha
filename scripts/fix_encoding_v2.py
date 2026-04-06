import re

file_path = r'd:\ZephyrAlpha\docs\10_AI_WORKFLOW\SENTIMENT_ANALYSIS_SHORT_TERM_TECHNICAL_SPECIFICATION.md'

with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

fixed_lines = []
for line in lines:
    if 'é' in line or 'è' in line or 'ç' in line or 'å' in line or 'æ' in line or 'ð' in line:
        try:
            fixed_line = line.encode('latin-1').decode('utf-8')
            fixed_lines.append(fixed_line)
        except:
            fixed_lines.append(line)
    else:
        fixed_lines.append(line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print('文件修复完成！')
print('\n前30行:')
for i, line in enumerate(fixed_lines[:30], 1):
    print(f'{i}: {line}', end='')
