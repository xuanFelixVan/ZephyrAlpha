import os
from pathlib import Path

docs_dir = Path('D:/ZephyrAlpha/docs')

# Find all integrated_from_* directories
integrated_dirs = []
for root, dirs, files in os.walk(docs_dir):
    for d in dirs:
        if 'integrated_from_' in d:
            full_path = Path(root) / d
            # Count files in directory
            file_count = len([f for f in full_path.iterdir() if f.is_file()])
            subdir_count = len([sd for sd in full_path.iterdir() if sd.is_dir()])

            # List files
            files_list = [f.name for f in full_path.iterdir() if f.is_file()]

            integrated_dirs.append({
                'path': str(full_path.relative_to(docs_dir)),
                'file_count': file_count,
                'subdir_count': subdir_count,
                'files': files_list
            })

print(f"Found {len(integrated_dirs)} integrated_from_* directories:\n")

# Sort by path
for d in sorted(integrated_dirs, key=lambda x: x['path']):
    print(f"Path: {d['path']}")
    print(f"  Files: {d['file_count']}, Subdirs: {d['subdir_count']}")
    print(f"  Contents: {', '.join(d['files'][:5])}")
    if len(d['files']) > 5:
        print(f"  ... and {len(d['files']) - 5} more")

    # Check if it's an empty shell (only INDEX.md or README.md)
    is_shell = d['file_count'] <= 2 and d['subdir_count'] == 0
    if is_shell and d['files']:
        main_files = [f.lower() for f in d['files']]
        is_shell = all(f in ['index.md', 'readme.md'] for f in main_files)

    print(f"  Is empty shell: {is_shell}")
    print()

# Count shells
shells = [d for d in integrated_dirs if d['file_count'] <= 2 and d['subdir_count'] == 0]
print(f"\nSummary: {len(shells)} / {len(integrated_dirs)} directories are empty shells")
