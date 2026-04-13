#!/usr/bin/env python3
"""查找重复的module_id"""

from pathlib import Path
import re
from collections import defaultdict

DOCS_ROOT = Path(__file__).resolve().parent.parent / "docs"

def find_duplicates():
    module_ids = defaultdict(list)
    
    for md_file in DOCS_ROOT.rglob("*.md"):
        try:
            with open(md_file, "r", encoding="utf-8-sig") as f:
                content = f.read()
            
            fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
            if fm_match:
                fm_content = fm_match.group(1)
                for line in fm_content.split("\n"):
                    if line.strip().startswith("module_id:"):
                        module_id = line.split(":", 1)[1].strip()
                        rel_path = str(md_file.relative_to(DOCS_ROOT.parent))
                        module_ids[module_id].append(rel_path)
                        break
        except:
            continue
    
    # 找出重复的
    duplicates = {k: v for k, v in module_ids.items() if len(v) > 1}
    
    print(f"共发现 {len(duplicates)} 组重复module_id:\n")
    for module_id, files in sorted(duplicates.items()):
        print(f"module_id: {module_id}")
        for f in files:
            print(f"  - {f}")
        print()
    
    return duplicates

if __name__ == "__main__":
    find_duplicates()
