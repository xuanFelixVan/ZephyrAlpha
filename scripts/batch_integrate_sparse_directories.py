"""
批量整合稀疏目录脚本
用途：批量整合建议合并的稀疏目录
创建时间：2026-04-07
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"

def get_directories_to_merge() -> List[Dict]:
    return [
        {
            "sparse_dir": "03_TRADING_TACTICS/05_STRATEGY_POOL",
            "target_dir": "03_TRADING_TACTICS",
            "reason": "仅1个文件，建议合并到父目录",
            "action": "delete_empty"
        },
        {
            "sparse_dir": "05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/05_DESIGN_DOCS/a_stock_rules",
            "target_dir": "05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/05_DESIGN_DOCS",
            "reason": "深度3层，建议合并到父目录",
            "action": "merge"
        },
        {
            "sparse_dir": "05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/05_DESIGN_DOCS/ui_design",
            "target_dir": "05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/05_DESIGN_DOCS",
            "reason": "深度3层，建议合并到父目录",
            "action": "merge"
        },
        {
            "sparse_dir": "05_IMPLEMENTATION/07_OPERATIONS/knowledge_base/lessons_learned",
            "target_dir": "05_IMPLEMENTATION/07_OPERATIONS/knowledge_base",
            "reason": "深度3层，建议合并到父目录",
            "action": "merge"
        },
        {
            "sparse_dir": "06_ARCHIVE/20260404_audit_reports_archive",
            "target_dir": "06_ARCHIVE",
            "reason": "仅1个文件，建议合并到父目录",
            "action": "delete_empty"
        },
        {
            "sparse_dir": "06_ARCHIVE/20260404_audit_reports_archive/audit_state/sample_validation_2026-04-02",
            "target_dir": "06_ARCHIVE/20260404_audit_reports_archive/audit_state",
            "reason": "深度3层，建议合并到父目录",
            "action": "merge"
        },
        {
            "sparse_dir": "06_ARCHIVE/20260404_audit_reports_archive/technical_reviews/IFIND_CONNECTOR",
            "target_dir": "06_ARCHIVE/20260404_audit_reports_archive/technical_reviews",
            "reason": "深度3层，建议合并到父目录",
            "action": "merge"
        },
        {
            "sparse_dir": "06_ARCHIVE/20260404_audit_reports_archive/technical_reviews/QMT_DATA_INTERFACE",
            "target_dir": "06_ARCHIVE/20260404_audit_reports_archive/technical_reviews",
            "reason": "深度3层，建议合并到父目录",
            "action": "merge"
        },
        {
            "sparse_dir": "06_ARCHIVE/architecture_v4/module_designs/layer_4",
            "target_dir": "06_ARCHIVE/architecture_v4/module_designs",
            "reason": "深度3层，建议合并到父目录",
            "action": "merge"
        },
        {
            "sparse_dir": "08_HUMAN_AI_INTERFACE/01_MOBILE_PUSH",
            "target_dir": "08_HUMAN_AI_INTERFACE",
            "reason": "仅1个文件，建议合并到父目录",
            "action": "delete_empty"
        },
        {
            "sparse_dir": "08_HUMAN_AI_INTERFACE/02_MONITORING",
            "target_dir": "08_HUMAN_AI_INTERFACE",
            "reason": "仅1个文件，建议合并到父目录",
            "action": "delete_empty"
        },
        {
            "sparse_dir": "08_HUMAN_AI_INTERFACE/03_AUTHENTICATION",
            "target_dir": "08_HUMAN_AI_INTERFACE",
            "reason": "仅1个文件，建议合并到父目录",
            "action": "delete_empty"
        },
        {
            "sparse_dir": "08_HUMAN_AI_INTERFACE/04_BACKTEST_INTERFACE",
            "target_dir": "08_HUMAN_AI_INTERFACE",
            "reason": "仅1个文件，建议合并到父目录",
            "action": "delete_empty"
        },
        {
            "sparse_dir": "09_AUDIT/PROCESSES",
            "target_dir": "09_AUDIT",
            "reason": "仅1个文件，建议合并到父目录",
            "action": "merge"
        },
        {
            "sparse_dir": "09_RESEARCH_INNOVATION/01_ai_research_lab",
            "target_dir": "09_RESEARCH_INNOVATION",
            "reason": "仅1个文件，建议合并到父目录",
            "action": "delete_empty"
        },
        {
            "sparse_dir": "10_GOVERNANCE_COMPLIANCE/01_internal_controls",
            "target_dir": "10_GOVERNANCE_COMPLIANCE",
            "reason": "仅1个文件，建议合并到父目录",
            "action": "delete_empty"
        }
    ]

def integrate_directory(sparse_dir: str, target_dir: str, action: str) -> Dict:
    result = {
        "sparse_dir": sparse_dir,
        "target_dir": target_dir,
        "action": action,
        "success": False,
        "files_moved": [],
        "files_skipped": [],
        "directories_deleted": [],
        "error": None
    }
    
    try:
        sparse_path = DOCS_DIR / sparse_dir
        target_path = DOCS_DIR / target_dir
        
        if not sparse_path.exists():
            result["error"] = f"稀疏目录不存在: {sparse_dir}"
            return result
        
        if not target_path.exists():
            result["error"] = f"目标目录不存在: {target_dir}"
            return result
        
        md_files = list(sparse_path.glob("*.md"))
        
        if not md_files:
            result["error"] = f"稀疏目录中没有Markdown文件: {sparse_dir}"
            return result
        
        if action == "delete_empty":
            index_files = [f for f in md_files if f.name.lower() in ['index.md', 'readme.md']]
            other_files = [f for f in md_files if f.name.lower() not in ['index.md', 'readme.md']]
            
            for md_file in other_files:
                target_file = target_path / md_file.name
                
                if target_file.exists():
                    result["files_skipped"].append(md_file.name)
                    continue
                
                shutil.move(str(md_file), str(target_file))
                result["files_moved"].append(md_file.name)
            
            remaining_files = list(sparse_path.glob("*"))
            if not remaining_files:
                shutil.rmtree(sparse_path)
                result["directories_deleted"].append(sparse_dir)
                result["success"] = True
            else:
                result["error"] = f"目录非空，无法删除: {[f.name for f in remaining_files]}"
                if result["files_moved"] or result["files_skipped"]:
                    result["success"] = True
        
        elif action == "merge":
            for md_file in md_files:
                target_file = target_path / md_file.name
                
                if target_file.exists():
                    result["files_skipped"].append(md_file.name)
                    continue
                
                shutil.move(str(md_file), str(target_file))
                result["files_moved"].append(md_file.name)
            
            remaining_files = list(sparse_path.glob("*"))
            if not remaining_files:
                shutil.rmtree(sparse_path)
                result["directories_deleted"].append(sparse_dir)
                result["success"] = True
            else:
                result["error"] = f"目录非空，无法删除: {[f.name for f in remaining_files]}"
                if result["files_moved"] or result["files_skipped"]:
                    result["success"] = True
        
    except Exception as e:
        result["error"] = str(e)
    
    return result

def main():
    print("=" * 80)
    print("批量整合稀疏目录")
    print("=" * 80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    directories_to_merge = get_directories_to_merge()
    
    print(f"\n准备整合 {len(directories_to_merge)} 个稀疏目录...\n")
    
    results = []
    success_count = 0
    failed_count = 0
    total_files_moved = 0
    total_dirs_deleted = 0
    
    for i, dir_info in enumerate(directories_to_merge, 1):
        print(f"[{i}/{len(directories_to_merge)}] 整合: {dir_info['sparse_dir']}")
        print(f"  目标: {dir_info['target_dir']}")
        print(f"  原因: {dir_info['reason']}")
        print(f"  动作: {dir_info['action']}")
        
        result = integrate_directory(
            dir_info['sparse_dir'],
            dir_info['target_dir'],
            dir_info['action']
        )
        results.append(result)
        
        if result['success']:
            success_count += 1
            print(f"  ✅ 成功")
            if result['files_moved']:
                print(f"  移动文件: {', '.join(result['files_moved'])}")
                total_files_moved += len(result['files_moved'])
            if result['files_skipped']:
                print(f"  跳过文件: {', '.join(result['files_skipped'])}")
            if result['directories_deleted']:
                print(f"  删除目录: {', '.join(result['directories_deleted'])}")
                total_dirs_deleted += len(result['directories_deleted'])
        else:
            failed_count += 1
            print(f"  ❌ 失败: {result['error']}")
        
        print()
    
    print("=" * 80)
    print("整合完成")
    print("=" * 80)
    print(f"成功: {success_count}")
    print(f"失败: {failed_count}")
    print(f"移动文件总数: {total_files_moved}")
    print(f"删除目录总数: {total_dirs_deleted}")
    print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    report_path = PROJECT_ROOT / "docs/09_AUDIT/STATE" / f"batch_sparse_directory_integration_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    import json
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total": len(directories_to_merge),
            "success": success_count,
            "failed": failed_count,
            "total_files_moved": total_files_moved,
            "total_dirs_deleted": total_dirs_deleted,
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n整合报告已保存至: {report_path}")

if __name__ == "__main__":
    main()
