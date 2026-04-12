# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
保守整合稀疏目录
用途：只整合可以安全整合的目录（备份、归档等），不整合蓝图目录
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

def load_keep_analysis() -> Dict:
    report_path = PROJECT_ROOT / "docs/09_AUDIT/STATE" / "deep_keep_directory_analysis_20260407_033213.json"
    
    with open(report_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def identify_conservative_integrations(analysis: Dict) -> List[Dict]:
    integrate_list = []
    
    for dir_info in analysis['optimize_dirs']:
        path = dir_info['path']
        action = dir_info['optimize_action']
        non_index_files = dir_info['non_index_files']
        
        if action == 'merge_blueprint':
            continue
        
        if action == 'merge_backup':
            integrate_list.append({
                "path": path,
                "action": "merge_to_parent",
                "reason": "备份/归档文件，可安全合并",
                "files": non_index_files
            })
        
        elif action == 'merge_single_file':
            file_name = non_index_files[0] if non_index_files else ""
            
            if 'backup' in file_name.lower() or 'archived' in file_name.lower():
                integrate_list.append({
                    "path": path,
                    "action": "merge_to_parent",
                    "reason": "备份/归档文件，可安全合并",
                    "files": non_index_files
                })
            elif 'tca' in file_name.lower():
                integrate_list.append({
                    "path": path,
                    "action": "merge_to_parent",
                    "reason": "交易成本分析文件，可安全合并",
                    "files": non_index_files
                })
            elif 'factor_catalog' in file_name.lower() or 'factor_library_manual' in file_name.lower():
                integrate_list.append({
                    "path": path,
                    "action": "merge_to_parent",
                    "reason": "因子库文档，可安全合并",
                    "files": non_index_files
                })
    
    return integrate_list

def integrate_conservative(dir_info: Dict) -> Dict:
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
    
    except Exception as e:
        result["error"] = str(e)
    
    return result

def main():
    print("=" * 80)
    print("保守整合稀疏目录")
    print("=" * 80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    analysis = load_keep_analysis()
    
    print(f"\n总保留目录: {analysis['total']}")
    print(f"可优化目录: {analysis['can_optimize']}")
    
    integrate_list = identify_conservative_integrations(analysis)
    
    print(f"\n保守整合目录: {len(integrate_list)}")
    
    print("\n" + "=" * 80)
    print("建议整合的目录")
    print("=" * 80)
    
    for i, d in enumerate(integrate_list, 1):
        print(f"\n{i}. {d['path']}")
        print(f"   原因: {d['reason']}")
        print(f"   文件: {', '.join(d['files'])}")
    
    if not integrate_list:
        print("\n没有需要整合的目录")
        return
    
    print("\n" + "=" * 80)
    print("开始整合")
    print("=" * 80)
    
    results = []
    success_count = 0
    failed_count = 0
    total_files_moved = 0
    total_dirs_deleted = 0
    
    for i, dir_info in enumerate(integrate_list, 1):
        print(f"\n[{i}/{len(integrate_list)}] 整合: {dir_info['path']}")
        print(f"  原因: {dir_info['reason']}")
        
        result = integrate_conservative(dir_info)
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
    
    final_report_path = PROJECT_ROOT / "docs/09_AUDIT/STATE" / f"conservative_sparse_directory_integration_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(final_report_path, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total": len(integrate_list),
            "success": success_count,
            "failed": failed_count,
            "total_files_moved": total_files_moved,
            "total_dirs_deleted": total_dirs_deleted,
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n整合报告已保存至: {final_report_path}")

if __name__ == "__main__":
    main()
