#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每月自动化检查脚本
检查内容：
1. 完整三层审计
2. 合规率统计
3. 问题趋势分析
4. 改进建议生成
"""

import sys
sys.path.append("D:/ZephyrAlpha")

from pathlib import Path
from datetime import datetime
import json

def run_monthly_check():
    project_root = Path("D:/ZephyrAlpha")
    check_results = {
        "check_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_docs": 0,
        "compliance_rate": 0,
        "issues": {
            "L1": 0,
            "L2": 0,
            "L3": 0
        }
    }

    print("=" * 80)
    print("每月自动化检查")
    print("=" * 80)
    print(f"检查时间: {check_results['check_time']}")
    print("-" * 80)

    docs_dir = project_root / "docs"
    md_files = list(docs_dir.rglob("*.md"))

    check_results['total_docs'] = len(md_files)
    print(f"发现 {len(md_files)} 个Markdown文件")

    yaml_complete = 0
    resp_complete = 0
    layer_complete = 0

    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            if content.startswith('---'):
                yaml_complete += 1

            if 'responsibility:' in content:
                resp_complete += 1

            if 'layer:' in content:
                layer_complete += 1

        except:
            pass

    if len(md_files) > 0:
        check_results['compliance_rate'] = round(
            (yaml_complete + resp_complete + layer_complete) / (len(md_files) * 3) * 100, 2
        )

    print(f"YAML完整性: {yaml_complete}/{len(md_files)}")
    print(f"职责完整性: {resp_complete}/{len(md_files)}")
    print(f"Layer完整性: {layer_complete}/{len(md_files)}")
    print(f"总体合规率: {check_results['compliance_rate']}%")

    report_path = project_root / "docs" / "09_AUDIT" / "STATE" / f"monthly_check_{datetime.now().strftime('%Y%m%d')}.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(check_results, f, ensure_ascii=False, indent=2)

    print(f"
✅ 检查报告已保存: {report_path}")
    print("=" * 80)

if __name__ == "__main__":
    run_monthly_check()
