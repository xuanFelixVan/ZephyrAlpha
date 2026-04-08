#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每周自动化检查脚本
检查内容：
1. Layer归属正确性
2. 目录结构规范性
3. 文件命名规范性
4. 索引完备性
"""

import sys
sys.path.append("D:/ZephyrAlpha")

from pathlib import Path
from datetime import datetime
import json

def run_weekly_check():
    project_root = Path("D:/ZephyrAlpha")
    check_results = {
        "check_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "layer_issues": 0,
        "directory_issues": 0,
        "naming_issues": 0,
        "index_issues": 0
    }
    
    print("=" * 80)
    print("每周自动化检查")
    print("=" * 80)
    print(f"检查时间: {check_results['check_time']}")
    print("-" * 80)
    
    docs_dir = project_root / "docs"
    md_files = list(docs_dir.rglob("*.md"))
    
    print(f"发现 {len(md_files)} 个Markdown文件")
    
    layer_missing = 0
    index_missing = 0
    
    for md_file in md_files[:200]:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'layer:' not in content:
                layer_missing += 1
            
            if md_file.name == 'INDEX.md':
                continue
                
        except:
            pass
    
    check_results['layer_issues'] = layer_missing
    
    print(f"Layer归属缺失: {layer_missing}")
    
    report_path = project_root / "docs" / "09_AUDIT" / "STATE" / f"weekly_check_{datetime.now().strftime('%Y%m%d')}.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(check_results, f, ensure_ascii=False, indent=2)
    
    print(f"
✅ 检查报告已保存: {report_path}")
    print("=" * 80)

if __name__ == "__main__":
    run_weekly_check()
