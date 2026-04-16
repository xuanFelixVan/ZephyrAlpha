#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
检查合规率脚本
用于CI/CD流程中检查文档合规率是否达标
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def check_compliance_rate():
    project_root = Path(__file__).resolve().parents[2]
    audit_state_dir = project_root / "docs" / "09_AUDIT" / "STATE"
    
    today = datetime.now()
    
    weekly_report = audit_state_dir / f"weekly_audit_{today.strftime('%Y%m%d')}.json"
    
    if not weekly_report.exists():
        print(f"❌ 审计报告不存在: {weekly_report}")
        return False
    
    with open(weekly_report, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    compliance_rate = report.get('summary', {}).get('compliance_rate', 0)
    total_issues = report.get('summary', {}).get('total_issues', 0)
    
    print(f"📊 合规率: {compliance_rate}%")
    print(f"📋 总问题数: {total_issues}")
    
    if compliance_rate >= 95.0:
        print(f"✅ 合规率达标 (≥95%)")
        return True
    else:
        print(f"❌ 合规率不达标 (<95%)")
        return False

if __name__ == "__main__":
    success = check_compliance_rate()
    sys.exit(0 if success else 1)
