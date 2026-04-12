# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
旧架构命名文件归档脚本
用途：将旧架构命名文件移动到归档目录
创建时间：2026-04-07
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"
ARCHIVE_DIR = DOCS_DIR / "06_ARCHIVE/20260407_old_layer_audit_reports"

def archive_old_layer_files():
    print("=" * 80)
    print("旧架构命名文件归档")
    print("=" * 80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    archive_map = {
        "layer5_reports": [
            "docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state/LAYER5_DEEP_AUDIT_REPORT_v4_20260407.md",
            "docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state/LAYER5_DEEP_AUDIT_REPORT_v5_20260407.md",
            "docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state/LAYER5_DEEP_AUDIT_SUMMARY_v5_20260407.md",
            "docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state/LAYER5_P1_IMPROVEMENT_REPORT_20260407.md",
            "docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state/LAYER5_P2_OPTIMIZATION_REPORT_20260407.md",
            "docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state/LAYER5_RESPONSIBILITY_FIX_REPORT_20260407.md",
        ],
        "layer6_reports": [
            "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER6_DEEP_AUDIT_REPORT_20260407.md",
        ],
        "layer9_reports": [
            "docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state/LAYER9_DEEP_AUDIT_REPORT_20260407.md",
            "docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state/LAYER9_DEEP_AUDIT_REPORT_v2_20260407.md",
            "docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state/LAYER9_DEEP_AUDIT_REPORT_v3_20260407.md",
            "docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state/LAYER9_COMPREHENSIVE_AUDIT_REPORT_20260407.md",
            "docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state/LAYER9_FINAL_AUDIT_SUMMARY_20260407.md",
            "docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state/LAYER9_FINAL_FIX_SUMMARY_20260407.md",
            "docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state/LAYER9_ISSUE_FIX_REPORT_20260407.md",
        ],
        "layer10_reports": [
            "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER_10_GOVERNANCE_COMPLIANCE_DEEP_AUDIT_REPORT_V4_20260406.md",
            "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER_10_GOVERNANCE_COMPLIANCE_DEEP_AUDIT_REPORT_V5_20260406.md",
            "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER_10_GOVERNANCE_COMPLIANCE_DEEP_AUDIT_REPORT_V6_20260406.md",
            "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER_10_GOVERNANCE_COMPLIANCE_DEEP_AUDIT_REPORT_V7_20260406.md",
            "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER_10_GOVERNANCE_COMPLIANCE_DEEP_AUDIT_REPORT_V8_20260407.md",
            "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER_10_GOVERNANCE_COMPLIANCE_DEEP_AUDIT_REPORT_V9_20260407.md",
            "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER_10_GOVERNANCE_COMPLIANCE_DEEP_AUDIT_REPORT_V10_20260407.md",
            "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER_10_GOVERNANCE_COMPLIANCE_DEEP_AUDIT_REPORT_V11_20260407.md",
            "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER_10_GOVERNANCE_COMPLIANCE_DEEP_AUDIT_REPORT_V12_20260407.md",
        ],
        "layer11_reports": [
            "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER_11_BLUEPRINT_COMPLETION_PLAN_20260407.md",
            "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER_11_DEEP_AUDIT_REPORT_V2_20260407.md",
            "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER_11_MISSING_MODULES_BLUEPRINT_20260407.md",
            "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER_11_P0_RECTIFICATION_REPORT_20260406.md",
            "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER_11_P1_RECTIFICATION_REPORT_20260406.md",
            "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER_11_SHORT_TERM_IMPROVEMENT_PLAN_20260407.md",
            "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER_11_STRATEGIC_DECISION_DEEP_AUDIT_REPORT_20260406.md",
            "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER_7_11_DIRECTORY_REORGANIZATION_REPORT_20260404.md",
            "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER_7_11_DIRECTORY_RESTRUCTURE_REPORT_20260404.md",
            "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER_7_11_EXTENSION_OPTIMIZATION_REPORT_20260404.md",
        ],
    }
    
    moved_count = 0
    failed_count = 0
    
    for layer_name, files in archive_map.items():
        target_dir = ARCHIVE_DIR / layer_name
        target_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n处理 {layer_name}:")
        
        for file_path in files:
            source = PROJECT_ROOT / file_path
            
            if source.exists():
                target = target_dir / source.name
                
                try:
                    shutil.move(str(source), str(target))
                    print(f"  ✅ {source.name}")
                    moved_count += 1
                except Exception as e:
                    print(f"  ❌ {source.name}: {e}")
                    failed_count += 1
            else:
                print(f"  ⚠️  {source.name}: 文件不存在")
    
    print("\n" + "=" * 80)
    print("归档统计")
    print("=" * 80)
    print(f"成功移动: {moved_count}个文件")
    print(f"移动失败: {failed_count}个文件")
    print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

if __name__ == "__main__":
    archive_old_layer_files()
