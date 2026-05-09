import os

base_src = r'D:\ZephyrAlpha\src\zephyr'
base_docs = r'D:\ZephyrAlpha\docs\03_modules'

# 1. Get ALL .py files on disk
disk_files = set()
for root, dirs, fnames in os.walk(base_src):
    dirs[:] = [d for d in dirs if d != '__pycache__']
    for f in fnames:
        if f.endswith('.py'):
            full = os.path.join(root, f)
            rel = os.path.relpath(full, base_src).replace(os.sep, '/')
            disk_files.add(rel)

# 2. Get ALL files mentioned in manifests
manifest_files = set()
manifest_dir = os.path.join(base_docs, '_manifests')
if os.path.isdir(manifest_dir):
    for mf in os.listdir(manifest_dir):
        if mf.endswith('.manifest.md'):
            with open(os.path.join(manifest_dir, mf), 'r', encoding='utf-8') as fh:
                for line in fh:
                    line = line.strip()
                    if line.startswith('- `'):
                        # Extract path from `- `path``
                        parts = line[3:].split('`')
                        if len(parts) >= 1:
                            path = parts[0]
                            if path.endswith('.py'):
                                manifest_files.add(path)

# 3. Find TRUE orphans
orphans = sorted(disk_files - manifest_files)

print(f'=== 全量逐文件比对 ===')
print(f'磁盘 .py 文件总数: {len(disk_files)}')
print(f'Manifest 登记 .py 文件数: {len(manifest_files)}')
print(f'孤儿文件数: {len(orphans)}')
print()

if orphans:
    print('孤儿文件列表:')
    for f in orphans:
        print(f'  {f}')
else:
    print('零孤儿文件！所有 .py 文件都已登记在 manifest 中。')

# 4. Check phantoms
phantoms = sorted(manifest_files - disk_files)
print()
print(f'幽灵文件数 (manifest中有但磁盘不存在): {len(phantoms)}')
if phantoms:
    print('幽灵文件列表 (前20):')
    for f in phantoms[:20]:
        print(f'  {f}')
