# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
执行稀疏目录整合脚本
用途：自动整合稀疏目录到父目录
创建时间：2026-04-07
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"

def get_sparse_directories_to_merge() -> List[Dict]:
    return [
        {
            "sparse_dir": "03_TRADING_TACTICS/05_STRATEGY_POOL",
            "target_dir": "03_TRADING_TACTICS",
            "reason": "仅1个文件，建议合并到父目录"
        },
        {
            "sparse_dir": "06_ARCHIVE/20260404_audit_reports_archive",
            "target_dir": "06_ARCHIVE",
            "reason": "仅1个文件，建议合并到父目录"
        },
        {
            "sparse_dir": "06_ARCHIVE/20260406_encoding_issues_archive",
            "target_dir": "06_ARCHIVE",
            "reason": "仅1个文件，建议合并到父目录"
        },
        {
            "sparse_dir": "09_RESEARCH_INNOVATION/01_ai_research_lab",
            "target_dir": "09_RESEARCH_INNOVATION",
            "reason": "仅1个文件，建议合并到父目录"
        },
        {
            "sparse_dir": "10_GOVERNANCE_COMPLIANCE/01_internal_controls",
            "target_dir": "10_GOVERNANCE_COMPLIANCE",
            "reason": "仅1个文件，建议合并到父目录"
        },
        {
            "sparse_dir": "11_STRATEGIC_DECISION/archive/2026-Q1",
            "target_dir": "11_STRATEGIC_DECISION/archive",
            "reason": "仅1个文件，建议合并到父目录"
        }
    ]

def integrate_directory(sparse_dir: str, target_dir: str) -> Dict:
    result = {
        "sparse_dir": sparse_dir,
        "target_dir": target_dir,
        "success": False,
        "files_moved": [],
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
        
        for md_file in md_files:
            target_file = target_path / md_file.name
            
            if target_file.exists():
                result["error"] = f"目标文件已存在: {target_file.name}"
                return result
            
            shutil.move(str(md_file), str(target_file))
            result["files_moved"].append(md_file.name)
        
        remaining_files = list(sparse_path.glob("*"))
        if not remaining_files:
            shutil.rmtree(sparse_path)
        else:
            result["error"] = f"目录非空，无法删除: {sparse_dir}"
            return result
        
        result["success"] = True
        
    except Exception as e:
        result["error"] = str(e)
    
    return result

def main():
    print("=" * 80)
    print("执行稀疏目录整合")
    print("=" * 80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    directories_to_merge = get_sparse_directories_to_merge()
    
    print(f"\n准备整合 {len(directories_to_merge)} 个稀疏目录...\n")
    
    results = []
    success_count = 0
    failed_count = 0
    
    for i, dir_info in enumerate(directories_to_merge, 1):
        print(f"[{i}/{len(directories_to_merge)}] 整合: {dir_info['sparse_dir']}")
        print(f"  目标: {dir_info['target_dir']}")
        print(f"  原因: {dir_info['reason']}")
        
        result = integrate_directory(dir_info['sparse_dir'], dir_info['target_dir'])
        results.append(result)
        
        if result['success']:
            success_count += 1
            print(f"  ✅ 成功")
            print(f"  移动文件: {', '.join(result['files_moved'])}")
        else:
            failed_count += 1
            print(f"  ❌ 失败: {result['error']}")
        
        print()
    
    print("=" * 80)
    print("整合完成")
    print("=" * 80)
    print(f"成功: {success_count}")
    print(f"失败: {failed_count}")
    print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    report_path = PROJECT_ROOT / "docs/09_AUDIT/STATE" / f"sparse_directory_integration_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    import json
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total": len(directories_to_merge),
            "success": success_count,
            "failed": failed_count,
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n整合报告已保存至: {report_path}")

if __name__ == "__main__":
    main()
