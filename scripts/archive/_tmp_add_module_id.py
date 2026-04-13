# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import re, os, sys

p = 'docs/09_AUDIT/STATE/TRAE_MASTER_EXECUTION_CHECKLIST_20260409.md'
c = open(p, 'r', encoding='utf-8').read()

matches = re.findall(r'\[ \] \*\*T(\d+)\*\* （NO-MID）`([^`]+)`', c)
print(f'Total NO-MID tasks: {len(matches)}')

batch_size = 50
batch_num = int(sys.argv[1]) if len(sys.argv) > 1 else 0
start = batch_num * batch_size
end = start + batch_size
batch = matches[start:end]
print(f'Processing batch {batch_num}: tasks {start}-{start+len(batch)-1}')

for tid, rel_path in batch:
    full_path = rel_path
    if not os.path.exists(full_path):
        print(f'  SKIP T{tid}: {full_path} not found')
        continue

    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()

    basename = os.path.splitext(os.path.basename(full_path))[0]
    new_mid = basename.upper()

    if content.startswith('---'):
        end_yaml = content.find('---', 3)
        if end_yaml > 0:
            yaml_block = content[3:end_yaml]
            if 'module_id:' in yaml_block:
                print(f'  SKIP T{tid}: {full_path} already has module_id')
                continue
            new_yaml = 'module_id: ' + new_mid + '\n' + yaml_block
            new_content = '---' + new_yaml + '---' + content[end_yaml+3:]
        else:
            print(f'  SKIP T{tid}: {full_path} malformed YAML')
            continue
    else:
        new_content = '---\nmodule_id: ' + new_mid + '\n---\n\n' + content

    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'  DONE T{tid}: {full_path} -> module_id: {new_mid}')

print(f'Batch {batch_num} complete')
