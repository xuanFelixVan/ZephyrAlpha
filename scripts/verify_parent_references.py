import os
import re

framework_dir = 'docs/01_FRAMEWORK'
errors = []
checked = 0

for root, dirs, files in os.walk(framework_dir):
    for file in files:
        if file.endswith('.md'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(500)
                    match = re.search(r'^parent_document:\s*(.+)$', content, re.MULTILINE)
                    if match:
                        parent = match.group(1).strip()
                        parent_path = os.path.normpath(os.path.join(root, parent))
                        if not os.path.exists(parent_path):
                            errors.append(f'{filepath}: parent_document引用不存在: {parent}')
                        checked += 1
            except Exception as e:
                pass

print(f'检查了 {checked} 个parent_document引用')
if errors:
    print(f'\n发现 {len(errors)} 个错误:')
    for error in errors:
        print(f'  - {error}')
else:
    print('\n✅ 所有parent_document引用都正确！')
