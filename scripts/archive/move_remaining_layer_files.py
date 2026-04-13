# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
移动剩余Layer 10和Layer 11文件到归档目录
"""

import shutil
from pathlib import Path

PROJECT_ROOT = Path("D:/ZephyrAlpha")
ARCHIVE_DIR = PROJECT_ROOT / "docs/06_ARCHIVE/20260407_old_layer_audit_reports"

def move_remaining_files():
    print("移动剩余Layer 10和Layer 11文件...")
    
    layer10_files = [
        "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER_10_GOVERNANCE_COMPLIANCE_DEEP_AUDIT_REPORT_V4_20260406.md",
        "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER_10_GOVERNANCE_COMPLIANCE_DEEP_AUDIT_REPORT_V5_20260406.md",
        "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER_10_GOVERNANCE_COMPLIANCE_DEEP_AUDIT_REPORT_V6_20260406.md",
        "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER_10_GOVERNANCE_COMPLIANCE_DEEP_AUDIT_REPORT_V7_20260406.md",
        "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER_10_GOVERNANCE_COMPLIANCE_DEEP_AUDIT_REPORT_V8_20260407.md",
        "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER_10_GOVERNANCE_COMPLIANCE_DEEP_AUDIT_REPORT_V9_20260407.md",
        "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER_10_GOVERNANCE_COMPLIANCE_DEEP_AUDIT_REPORT_V10_20260407.md",
        "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER_10_GOVERNANCE_COMPLIANCE_DEEP_AUDIT_REPORT_V11_20260407.md",
        "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER_10_GOVERNANCE_COMPLIANCE_DEEP_AUDIT_REPORT_V12_20260407.md",
    ]
    
    layer11_files = [
        "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER_11_BLUEPRINT_COMPLETION_PLAN_20260407.md",
        "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER_11_DEEP_AUDIT_REPORT_V2_20260407.md",
        "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER_11_MISSING_MODULES_BLUEPRINT_20260407.md",
        "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER_11_P0_RECTIFICATION_REPORT_20260406.md",
        "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER_11_P1_RECTIFICATION_REPORT_20260406.md",
        "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER_11_SHORT_TERM_IMPROVEMENT_PLAN_20260407.md",
        "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER_11_STRATEGIC_DECISION_DEEP_AUDIT_REPORT_20260406.md",
    ]
    
    moved_count = 0
    
    print("\n移动Layer 10文件:")
    for file_path in layer10_files:
        source = PROJECT_ROOT / file_path
        if source.exists():
            target = ARCHIVE_DIR / "layer10_reports" / source.name
            shutil.move(str(source), str(target))
            print(f"  ✅ {source.name}")
            moved_count += 1
    
    print("\n移动Layer 11文件:")
    for file_path in layer11_files:
        source = PROJECT_ROOT / file_path
        if source.exists():
            target = ARCHIVE_DIR / "layer11_reports" / source.name
            shutil.move(str(source), str(target))
            print(f"  ✅ {source.name}")
            moved_count += 1
    
    print(f"\n移动完成: {moved_count}个文件")
    return moved_count

if __name__ == "__main__":
    move_remaining_files()
