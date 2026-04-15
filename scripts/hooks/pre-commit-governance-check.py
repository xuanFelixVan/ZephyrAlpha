#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pre-commit hook: 自动运行 sentinel_l1_governance_scan
在每次 commit 前验证文档治理健康度，防止断链回流
"""
import io
import json
import subprocess
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SENTINEL_SCRIPT = REPO_ROOT / "scripts" / "audit" / "sentinel_l1_governance_scan.py"
L1_STATE = REPO_ROOT / "docs/09_AUDIT/STATE/SENTINEL_L1_SCAN_20260408.json"

def check_governance_health():
    """运行扫描并检查健康度"""
    print("[pre-commit] 运行文档治理健康度扫描...")
    result = subprocess.run(
        [sys.executable, str(SENTINEL_SCRIPT)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("[pre-commit] ❌ 扫描失败")
        print(result.stderr)
        return False
    
    # 读取扫描结果
    try:
        with open(L1_STATE, encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"[pre-commit] ⚠️  无法读取扫描结果: {e}")
        return True  # 允许提交继续
    
    links_stats = data.get("links", {}).get("stats", {})
    mod_stats = data.get("module_ids", {})
    
    invalid = links_stats.get("invalid", 0)
    dup_count = mod_stats.get("duplicate_ids_count", 0)
    
    # 设定阈值
    BROKEN_LINK_THRESHOLD = 100    # 允许的最大断链增幅
    DUPLICATE_THRESHOLD = 20       # 允许的最大活跃重复组
    
    print("[pre-commit] 📊 治理健康度快照:")
    print(f"  断链数         : {invalid}")
    print(f"  重复 module_id : {dup_count}")
    
    if invalid > BROKEN_LINK_THRESHOLD:
        print(f"[pre-commit] ❌ 断链数 {invalid} 超过阈值 {BROKEN_LINK_THRESHOLD}")
        print("[pre-commit] 💡 建议: 运行 fix_dead_links.py --apply 修复")
        return False
    
    if dup_count > DUPLICATE_THRESHOLD:
        print(f"[pre-commit] ❌ 重复 module_id {dup_count} 超过阈值 {DUPLICATE_THRESHOLD}")
        return False
    
    print("[pre-commit] ✅ 治理健康度检查通过")
    return True

if __name__ == "__main__":
    success = check_governance_health()
    sys.exit(0 if success else 1)
