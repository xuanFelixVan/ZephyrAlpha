#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P0-1: 删除重复监控报告
保留最新的1个，删除其他所有重复文件
"""

import os
from pathlib import Path
from datetime import datetime

def delete_duplicate_monitoring_reports():
    project_root = Path("D:/ZephyrAlpha")
    monitoring_dir = project_root / "docs" / "09_AUDIT" / "STATE"
    
    monitoring_reports = list(monitoring_dir.glob("monitoring_report_*.md"))
    
    if not monitoring_reports:
        print("未找到监控报告文件")
        return
    
    monitoring_reports.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    latest_report = monitoring_reports[0]
    duplicate_reports = monitoring_reports[1:]
    
    print("=" * 80)
    print("P0-1: 删除重复监控报告")
    print("=" * 80)
    print(f"发现监控报告总数: {len(monitoring_reports)}")
    print(f"保留最新报告: {latest_report.name}")
    print(f"待删除报告数: {len(duplicate_reports)}")
    print("-" * 80)
    
    deleted_count = 0
    for report in duplicate_reports:
        try:
            os.remove(report)
            print(f"✅ 已删除: {report.name}")
            deleted_count += 1
        except Exception as e:
            print(f"❌ 删除失败: {report.name} - {e}")
    
    print("-" * 80)
    print(f"删除完成: {deleted_count} 个文件")
    print(f"保留文件: {latest_report.name}")
    print("=" * 80)

if __name__ == "__main__":
    delete_duplicate_monitoring_reports()
