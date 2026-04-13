import os, re, sys
from collections import defaultdict

def find_module_ids():
    module_ids = defaultdict(list)
    for root, dirs, files in os.walk('.'):
        # 忽略隐藏目录和 .git, .audit_cache 等
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('__pycache__', 'node_modules')]
        for file in files:
            if file.endswith('.md'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8-sig') as f:
                        content = f.read(10000)  # 只读前部
                except Exception as e:
                    continue
                # 匹配 frontmatter
                match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
                if match:
                    fm = match.group(1)
                    for line in fm.split('\n'):
                        line = line.strip()
                        if line.startswith('module_id:'):
                            module_id = line.split(':', 1)[1].strip()
                            module_ids[module_id].append(path)
                            break
    return module_ids

if __name__ == '__main__':
    module_ids = find_module_ids()
    duplicates = {k: v for k, v in module_ids.items() if len(v) > 1}
    print(f"Total unique module_ids: {len(module_ids)}")
    print(f"Duplicate groups: {len(duplicates)}")
    if duplicates:
        print("\nDuplicate module_ids:")
        for mid, paths in sorted(duplicates.items()):
            print(f"\n{mid}:")
            for p in paths:
                print(f"  {p}")
    else:
        print("No duplicate module_ids found.")