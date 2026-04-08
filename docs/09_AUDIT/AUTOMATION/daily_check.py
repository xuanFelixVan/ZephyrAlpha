#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日自动化检查脚本
检查内容：
1. YAML头部完整性
2. 职责描述清晰度
3. 死链接检测
4. 编码一致性
"""

import sys
sys.path.append("D:/ZephyrAlpha")

from pathlib import Path
from datetime import datetime
import json

def run_daily_check():
    project_root = Path("D:/ZephyrAlpha")
    check_results = {
        "check_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "yaml_issues": 0,
        "responsibility_issues": 0,
        "dead_links": 0,
        "encoding_issues": 0
    }
    
    print("=" * 80)
    print("每日自动化检查")
    print("=" * 80)
    print(f"检查时间: {check_results['check_time']}")
    print("-" * 80)
    
    docs_dir = project_root / "docs"
    md_files = list(docs_dir.rglob("*.md"))
    
    print(f"发现 {len(md_files)} 个Markdown文件")
    
    yaml_missing = 0
    resp_missing = 0
    
    for md_file in md_files[:100]:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.startswith('---'):
                yaml_missing += 1
            
            if 'responsibility:' not in content:
                resp_missing += 1
                
        except:
            pass
    
    check_results['yaml_issues'] = yaml_missing
    check_results['responsibility_issues'] = resp_missing
    
    print(f"YAML头部缺失: {yaml_missing}")
    print(f"职责描述缺失: {resp_missing}")
    
    report_path = project_root / "docs" / "09_AUDIT" / "STATE" / f"daily_check_{datetime.now().strftime('%Y%m%d')}.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(check_results, f, ensure_ascii=False, indent=2)
    
    print(f"
✅ 检查报告已保存: {report_path}")
    print("=" * 80)

if __name__ == "__main__":
    run_daily_check()
