#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日自动化检查脚本
检查内容：
1. YAML 头部完整性（抽样）
2. 职责描述清晰度（抽样）
3. 死链接检测（占位，完整版见 CI link_checker）
4. 编码一致性（D-05）：调用 doc_guard_pre_commit.py --scan-encoding
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 仓库根：本文件位于 docs/09_AUDIT/AUTOMATION/daily_check.py → 上溯 4 级
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DOCS_DIR = PROJECT_ROOT / "docs"
STATE_DIR = PROJECT_ROOT / "docs" / "09_AUDIT" / "STATE"
DOC_GUARD = PROJECT_ROOT / "scripts" / "hooks" / "doc_guard_pre_commit.py"


def run_daily_check() -> int:
    check_results = {
        "check_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "yaml_issues": 0,
        "responsibility_issues": 0,
        "dead_links": 0,
        "encoding_issues": 0,
        "encoding_scan_exit_code": None,
        "encoding_ok": None,
    }

    print("=" * 80)
    print("每日自动化检查")
    print("=" * 80)
    print(f"检查时间: {check_results['check_time']}")
    print(f"项目根: {PROJECT_ROOT}")
    print("-" * 80)

    md_files = list(DOCS_DIR.rglob("*.md"))
    print(f"发现 {len(md_files)} 个 Markdown 文件")

    yaml_missing = 0
    resp_missing = 0

    for md_file in md_files[:100]:
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()
            if not content.startswith("---"):
                yaml_missing += 1
            if "responsibility:" not in content:
                resp_missing += 1
        except OSError:
            pass

    check_results["yaml_issues"] = yaml_missing
    check_results["responsibility_issues"] = resp_missing

    print(f"YAML 头部缺失（抽样前100）: {yaml_missing}")
    print(f"职责描述缺失（抽样前100）: {resp_missing}")
    print("-" * 80)

    # 第四层：编码全量扫描（与 pre-commit D-05、CI 对齐）
    print("运行编码扫描: python scripts/hooks/doc_guard_pre_commit.py --scan-encoding")
    proc = subprocess.run(
        [sys.executable, str(DOC_GUARD), "--scan-encoding"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    check_results["encoding_scan_exit_code"] = proc.returncode
    # doc_guard: 0=无阻断问题, 1=有 D-05 等阻断项
    check_results["encoding_ok"] = proc.returncode == 0
    if proc.stdout:
        print(proc.stdout[-8000:] if len(proc.stdout) > 8000 else proc.stdout)
    if proc.stderr:
        print(proc.stderr, file=sys.stderr)

    # 从退出码推导 encoding_issues 计数（脚本未输出 JSON 计数时仅记录布尔）
    check_results["encoding_issues"] = 0 if proc.returncode == 0 else -1

    STATE_DIR.mkdir(parents=True, exist_ok=True)
    report_path = STATE_DIR / f"daily_check_{datetime.now().strftime('%Y%m%d')}.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(check_results, f, ensure_ascii=False, indent=2)

    print("-" * 80)
    print(f"检查报告已保存: {report_path}")
    print("=" * 80)

    # 编码失败时非零退出，便于计划任务告警
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(run_daily_check())
