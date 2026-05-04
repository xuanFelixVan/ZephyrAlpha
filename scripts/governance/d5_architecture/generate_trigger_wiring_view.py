"""
generate_trigger_wiring_view.py — CT-005 → trigger_router.yaml 接线状态自动派生

__manifest__ = """
args: []
description: CT-005 → trigger_router.yaml 接线状态自动派生（OpenAPI/Terraform模式——YAML canonical
  → MD视图自动生成）
dimensions:
- D5
priority: P2
timeout_seconds: 30
warn_only: false
"""


对标 AGENTS.md §6.12（AI受众优先——Canonical YAML → 自动生成 Markdown 视图）
     AGENTS.md §6.9（架构数据 Canonical SSoT 铁律——YAML 为真源，MD 为派生）
     OpenAPI（spec.yaml → Swagger UI 自动渲染）
     Terraform（state → plan 自动派生）

读取 declarative-contract-tracker.yaml CT-005 的 wiring 字段，
自动生成/更新 trigger_router.yaml 中的接线状态表区块。

使用方式: python scripts/governance/d5_architecture/generate_trigger_wiring_view.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared.constants import REPO_ROOT
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
CT_TRACKER_PATH = REPO_ROOT / "docs/01_policies_and_standards/_registry/catalogs/declarative-contract-tracker.yaml"
TRIGGER_ROUTER_PATH = REPO_ROOT / "config/trigger_router.yaml"
MARKER_START = "# --- AUTO-GENERATED WIRING STATUS START ---"
MARKER_END = "# --- AUTO-GENERATED WIRING STATUS END ---"

def load_ct005_wiring() -> list[dict]:
    """加载 CT005 接线配置"""
    ct = yaml.safe_load(CT_TRACKER_PATH.read_text(encoding="utf-8"))
    for c in ct.get("contracts", []):
        if c.get("contract_id") == "CT-005":
            return c.get("wiring", [])
    return []

def build_wiring_lines(wiring: list[dict]) -> list[str]:
    """load ct005 wiring."""
    lines: list[str] = []
    for w in wiring:
        arrow = "✅→" if "✅" in w["current"] else "🔲→"
        lines.append(f'# trigger: {w['trigger']} → {w['current']} {arrow} {w['goal']} [{w['phase']}]')
    lines.append("#")
    lines.append("# 真实 handler 实施后:")
    lines.append("#   (1) 更新 trigger_router.yaml triggers.<type>.handler 为真实路径")
    lines.append("#   (2) 删除 trigger_router.py 中对应 handle_*_stub 函数")
    lines.append("#   (3) 更新 CT-005 wiring.<trigger>.current 从 🔲 stub → ✅ 真实")
    lines.append("#   (4) 运行本脚本重新生成本区块")
    lines.append("#   每次替换须经 Owner 审批（Human-Gated）。")
    return lines
    "build wiring lines."

def update_trigger_router(wiring: list[dict]) -> tuple[int, int]:
    """更新触发器路由"""
    content = TRIGGER_ROUTER_PATH.read_text(encoding="utf-8")
    lines = content.split("\n")
    start_idx, end_idx = (-1, -1)
    for i, line in enumerate(lines):
        if line.strip() == MARKER_START:
            start_idx = i
        elif line.strip() == MARKER_END and start_idx >= 0:
            end_idx = i
            break
    if start_idx < 0 or end_idx < 0:
        return (0, len(wiring))
    wiring_lines = build_wiring_lines(wiring)
    new_block = [MARKER_START] + wiring_lines + [MARKER_END]
    new_lines = lines[:start_idx] + new_block + lines[end_idx + 1 :]
    TRIGGER_ROUTER_PATH.write_text("\n".join(new_lines), encoding="utf-8")
    return (len(wiring_lines), len(wiring))
    "update trigger router."

def main() -> None:
    """入口函数"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--warn-only", action="store_true", help="warn mode: exit 0 even if findings")
    args = parser.parse_args()
    wiring = load_ct005_wiring()
    if not wiring:
        print("[WIRING-GEN] CT-005 中无 wiring 数据 — 跳过")
        return
    generated, triggers = update_trigger_router(wiring)
    print(f"[WIRING-GEN] CT-005 → trigger_router.yaml: {generated} 行 / {triggers} 触发器 — 完成")
    "入口函数."

if __name__ == "__main__":
    sys.exit(main() or 0)
