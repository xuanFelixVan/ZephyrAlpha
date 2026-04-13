# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
深度分析剩余稀疏目录
用途：识别所有可以安全整合的稀疏目录
创建时间：2026-04-07
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"

def analyze_sparse_directory_deep(sparse_path: Path) -> Dict:
    md_files = list(sparse_path.glob("*.md"))
    all_files = list(sparse_path.glob("*"))
    all_dirs = [f for f in all_files if f.is_dir()]
    
    has_index = any(f.name.lower() == 'index.md' for f in md_files)
    has_readme = any(f.name.lower() == 'readme.md' for f in md_files)
    has_blueprint = any('blueprint' in f.name.lower() for f in md_files)
    
    non_index_files = [f for f in md_files if f.name.lower() not in ['index.md', 'readme.md']]
    
    depth = len(sparse_path.relative_to(DOCS_DIR).parts)
    
    should_integrate = False
    reason = ""
    action = "skip"
    
    if len(all_dirs) > 0:
        should_integrate = False
        reason = f"包含{len(all_dirs)}个子目录"
        action = "skip"
    elif depth >= 4:
        should_integrate = True
        reason = f"深度{depth}层，过深"
        action = "merge_to_parent"
    elif len(md_files) == 1 and has_index and not has_blueprint:
        should_integrate = True
        reason = "仅有INDEX.md，无实际内容"
        action = "delete_empty"
    elif len(md_files) == 2 and has_index and has_readme and not has_blueprint and not non_index_files:
        should_integrate = True
        reason = "仅有INDEX.md和README.md，无实际内容"
        action = "delete_empty"
    elif depth >= 3 and len(md_files) <= 2 and not has_blueprint:
        should_integrate = True
        reason = f"深度{depth}层，文件少，无蓝图"
        action = "merge_to_parent"
    elif len(md_files) == 2 and has_index and has_blueprint:
        should_integrate = False
        reason = "包含蓝图文件，保留"
        action = "keep"
    elif len(md_files) >= 2 and has_blueprint:
        should_integrate = False
        reason = "包含蓝图文件，保留"
        action = "keep"
    
    return {
        "path": str(sparse_path.relative_to(DOCS_DIR)),
        "depth": depth,
        "md_count": len(md_files),
        "total_count": len(all_files),
        "dir_count": len(all_dirs),
        "has_index": has_index,
        "has_readme": has_readme,
        "has_blueprint": has_blueprint,
        "non_index_files": [f.name for f in non_index_files],
        "should_integrate": should_integrate,
        "reason": reason,
        "action": action
    }

def main():
    print("=" * 80)
    print("深度分析剩余稀疏目录")
    print("=" * 80)
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    sparse_dirs = []
    
    for root, dirs, files in os.walk(DOCS_DIR):
        md_files = [f for f in files if f.endswith('.md')]
        
        if len(md_files) < 3 and len(md_files) > 0:
            sparse_path = Path(root)
            analysis = analyze_sparse_directory_deep(sparse_path)
            sparse_dirs.append(analysis)
    
    sparse_dirs.sort(key=lambda x: (x['depth'], x['md_count']))
    
    integrate_dirs = [d for d in sparse_dirs if d['should_integrate']]
    keep_dirs = [d for d in sparse_dirs if not d['should_integrate']]
    
    delete_empty_dirs = [d for d in integrate_dirs if d['action'] == 'delete_empty']
    merge_dirs = [d for d in integrate_dirs if d['action'] == 'merge_to_parent']
    
    print(f"\n总稀疏目录数: {len(sparse_dirs)}")
    print(f"建议整合: {len(integrate_dirs)}")
    print(f"  - 删除空目录: {len(delete_empty_dirs)}")
    print(f"  - 合并到父目录: {len(merge_dirs)}")
    print(f"保持现状: {len(keep_dirs)}")
    
    print("\n" + "=" * 80)
    print("建议删除的空目录")
    print("=" * 80)
    
    for i, d in enumerate(delete_empty_dirs, 1):
        print(f"\n{i}. {d['path']}")
        print(f"   深度: {d['depth']}")
        print(f"   文件数: {d['md_count']}")
        print(f"   原因: {d['reason']}")
    
    print("\n" + "=" * 80)
    print("建议合并到父目录")
    print("=" * 80)
    
    for i, d in enumerate(merge_dirs, 1):
        print(f"\n{i}. {d['path']}")
        print(f"   深度: {d['depth']}")
        print(f"   文件数: {d['md_count']}")
        print(f"   原因: {d['reason']}")
        if d['non_index_files']:
            print(f"   非索引文件: {', '.join(d['non_index_files'])}")
    
    print("\n" + "=" * 80)
    print("保持现状的目录")
    print("=" * 80)
    
    for i, d in enumerate(keep_dirs[:10], 1):
        print(f"\n{i}. {d['path']}")
        print(f"   深度: {d['depth']}")
        print(f"   文件数: {d['md_count']}")
        print(f"   原因: {d['reason']}")
    
    if len(keep_dirs) > 10:
        print(f"\n... 还有 {len(keep_dirs) - 10} 个目录")
    
    report_path = PROJECT_ROOT / "docs/09_AUDIT/STATE" / f"deep_sparse_directory_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total": len(sparse_dirs),
            "integrate": len(integrate_dirs),
            "delete_empty": len(delete_empty_dirs),
            "merge_to_parent": len(merge_dirs),
            "keep": len(keep_dirs),
            "integrate_dirs": integrate_dirs,
            "keep_dirs": keep_dirs
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n分析报告已保存至: {report_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()
