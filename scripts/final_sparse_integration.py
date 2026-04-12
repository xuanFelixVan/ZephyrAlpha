# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
最终整合稀疏目录
用途：整合13个可整合的稀疏目录
创建时间：2026-04-07
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"

def load_scan_result() -> Dict:
    report_path = PROJECT_ROOT / "docs/09_AUDIT/STATE" / "final_sparse_scan_20260407_114159.json"
    
    with open(report_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def integrate_directory(dir_info: Dict) -> Dict:
    result = {
        "path": dir_info['path'],
        "action": dir_info['action'],
        "success": False,
        "files_moved": [],
        "directories_deleted": [],
        "error": None
    }
    
    try:
        sparse_path = DOCS_DIR / dir_info['path']
        
        if not sparse_path.exists():
            result["error"] = "目录不存在"
            return result
        
        if dir_info['action'] == 'delete_empty':
            md_files = list(sparse_path.glob("*.md"))
            
            for md_file in md_files:
                if md_file.name.lower() in ['index.md', 'readme.md']:
                    continue
                parent_path = sparse_path.parent
                target_file = parent_path / md_file.name
                if not target_file.exists():
                    shutil.move(str(md_file), str(target_file))
                    result["files_moved"].append(md_file.name)
            
            remaining_files = [f for f in sparse_path.glob("*") if f.name.lower() not in ['index.md', 'readme.md']]
            if not remaining_files:
                shutil.rmtree(sparse_path)
                result["directories_deleted"].append(dir_info['path'])
            
            result["success"] = True
        
        elif dir_info['action'] == 'merge_single':
            parent_path = sparse_path.parent
            md_files = list(sparse_path.glob("*.md"))
            
            non_index_files = [f for f in md_files if f.name.lower() not in ['index.md', 'readme.md']]
            
            for md_file in non_index_files:
                target_file = parent_path / md_file.name
                
                if target_file.exists():
                    continue
                
                shutil.move(str(md_file), str(target_file))
                result["files_moved"].append(md_file.name)
            
            remaining_files = list(sparse_path.glob("*"))
            if not remaining_files:
                shutil.rmtree(sparse_path)
                result["directories_deleted"].append(dir_info['path'])
            
            result["success"] = True
        
        else:
            result["error"] = f"未知操作: {dir_info['action']}"
    
    except Exception as e:
        result["error"] = str(e)
    
    return result

def main():
    print("=" * 80)
    print("最终整合稀疏目录")
    print("=" * 80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    scan_result = load_scan_result()
    
    integrate_dirs = scan_result['integrate_dirs']
    
    print(f"\n总可整合目录: {len(integrate_dirs)}")
    
    print("\n" + "=" * 80)
    print("开始整合")
    print("=" * 80)
    
    results = []
    success_count = 0
    failed_count = 0
    total_files_moved = 0
    total_dirs_deleted = 0
    
    for i, dir_info in enumerate(integrate_dirs, 1):
        print(f"\n[{i}/{len(integrate_dirs)}] 整合: {dir_info['path']}")
        print(f"  操作: {dir_info['action']}")
        print(f"  原因: {dir_info['reason']}")
        
        result = integrate_directory(dir_info)
        results.append(result)
        
        if result['success']:
            success_count += 1
            print(f"  ✅ 成功")
            if result['files_moved']:
                print(f"  移动文件: {', '.join(result['files_moved'])}")
                total_files_moved += len(result['files_moved'])
            if result['directories_deleted']:
                print(f"  删除目录: {', '.join(result['directories_deleted'])}")
                total_dirs_deleted += len(result['directories_deleted'])
        else:
            failed_count += 1
            print(f"  ❌ 失败: {result['error']}")
    
    print("\n" + "=" * 80)
    print("整合完成")
    print("=" * 80)
    print(f"成功: {success_count}")
    print(f"失败: {failed_count}")
    print(f"移动文件总数: {total_files_moved}")
    print(f"删除目录总数: {total_dirs_deleted}")
    print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    final_report_path = PROJECT_ROOT / "docs/09_AUDIT/STATE" / f"final_sparse_integration_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(final_report_path, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total": len(integrate_dirs),
            "success": success_count,
            "failed": failed_count,
            "total_files_moved": total_files_moved,
            "total_dirs_deleted": total_dirs_deleted,
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n整合报告已保存至: {final_report_path}")

if __name__ == "__main__":
    main()
