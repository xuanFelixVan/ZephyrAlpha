# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
深度分析保留目录
用途：重新分析66个保留目录，看是否有可以优化的地方
创建时间：2026-04-07
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"

def analyze_keep_directory_deep(dir_info: Dict) -> Dict:
    sparse_path = DOCS_DIR / dir_info['path']
    
    if not sparse_path.exists():
        return None
    
    md_files = list(sparse_path.glob("*.md"))
    all_files = list(sparse_path.glob("*"))
    all_dirs = [f for f in all_files if f.is_dir()]
    
    non_index_files = [f for f in md_files if f.name.lower() not in ['index.md', 'readme.md']]
    
    can_optimize = False
    optimize_reason = ""
    optimize_action = "keep"
    
    if dir_info['action'] == 'keep' and len(non_index_files) == 1:
        if 'BLUEPRINT' in non_index_files[0].name.upper():
            can_optimize = True
            optimize_reason = "仅有1个蓝图文件，可考虑合并到父目录"
            optimize_action = "merge_blueprint"
        elif 'backup' in non_index_files[0].name.lower() or 'archived' in non_index_files[0].name.lower():
            can_optimize = True
            optimize_reason = "仅有1个备份/归档文件，可考虑合并到父目录"
            optimize_action = "merge_backup"
        elif len(md_files) == 2 and dir_info['has_index']:
            can_optimize = True
            optimize_reason = "仅有INDEX.md和1个文件，可考虑合并"
            optimize_action = "merge_single_file"
    
    return {
        "path": dir_info['path'],
        "depth": dir_info['depth'],
        "md_count": len(md_files),
        "total_count": len(all_files),
        "dir_count": len(all_dirs),
        "non_index_files": [f.name for f in non_index_files],
        "original_reason": dir_info['reason'],
        "original_action": dir_info['action'],
        "can_optimize": can_optimize,
        "optimize_reason": optimize_reason,
        "optimize_action": optimize_action
    }

def main():
    print("=" * 80)
    print("深度分析保留目录")
    print("=" * 80)
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    report_path = PROJECT_ROOT / "docs/09_AUDIT/STATE" / "final_sparse_directory_analysis_20260407_031937.json"
    
    with open(report_path, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    keep_dirs = report['keep_dirs']
    
    print(f"\n分析 {len(keep_dirs)} 个保留目录...\n")
    
    results = []
    optimize_dirs = []
    
    for dir_info in keep_dirs:
        result = analyze_keep_directory_deep(dir_info)
        if result:
            results.append(result)
            if result['can_optimize']:
                optimize_dirs.append(result)
    
    print("=" * 80)
    print("可以优化的目录")
    print("=" * 80)
    
    for i, d in enumerate(optimize_dirs, 1):
        print(f"\n{i}. {d['path']}")
        print(f"   深度: {d['depth']}")
        print(f"   文件数: {d['md_count']}")
        print(f"   非索引文件: {', '.join(d['non_index_files'])}")
        print(f"   原始原因: {d['original_reason']}")
        print(f"   优化建议: {d['optimize_reason']}")
        print(f"   优化操作: {d['optimize_action']}")
    
    print("\n" + "=" * 80)
    print("统计结果")
    print("=" * 80)
    print(f"总保留目录: {len(keep_dirs)}")
    print(f"可以优化: {len(optimize_dirs)}")
    print(f"建议保持: {len(results) - len(optimize_dirs)}")
    
    final_report_path = PROJECT_ROOT / "docs/09_AUDIT/STATE" / f"deep_keep_directory_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(final_report_path, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total": len(keep_dirs),
            "can_optimize": len(optimize_dirs),
            "should_keep": len(results) - len(optimize_dirs),
            "optimize_dirs": optimize_dirs,
            "all_results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n分析报告已保存至: {final_report_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()
