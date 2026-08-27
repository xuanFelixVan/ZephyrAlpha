#!/usr/bin/env python3
"""check_wiring_orphan.py — 装配超期门禁（Owner 裁定三 Layer3，#ARCH-278）。

职责：扫描 wiring_registry.yaml，检出「登记超期未接线」模块，防架上当品烂尾。

规则：
- wiring_status=unwired 且登记日期早于 today - ORPHAN_DAYS（默认 90 天）→ 判定 orphan。
- wired/exempt 不参与；pure_library 默认 exempt（需求驱动消费，无需装配）。
- defer_reason 已登记的 unwired 模块同样计龄（defer 不是免死牌——超期须重新评审 defer 是否仍成立）。

用法：
  python scripts/governance/check_wiring_orphan.py             # 报告模式（恒 exit 0）
  python scripts/governance/check_wiring_orphan.py --strict    # 门禁模式（有 orphan → exit 1）
  python scripts/governance/check_wiring_orphan.py --days 30   # 自定义超期阈值
  python scripts/governance/check_wiring_orphan.py --registry <path> --today YYYY-MM-DD
"""
from __future__ import annotations

import argparse
import datetime as _dt
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = REPO_ROOT / "docs/01_policies_and_standards/_registry/catalogs/wiring_registry.yaml"

REQUIRED_KEYS = ("candidate_id", "name", "path", "domain", "wiring_class", "wiring_status")
VALID_CLASSES = {"eventbus_consumer", "startup_instance", "di_service", "pure_library"}
VALID_STATUS = {"unwired", "wired", "exempt"}


def _parse_registry(text: str) -> tuple[list[dict], str | None]:
    """轻量 YAML 解析（仅本台账结构；避免引入 yaml 依赖的启动开销）。"""
    generated_at = None
    m = re.search(r"^generated_at: '([^']+)'", text, re.M)
    if m:
        generated_at = m.group(1)
    modules = []
    entries = re.split(r"^- candidate_id: ", text, flags=re.M)[1:]
    for e in entries:
        mod = {"candidate_id": e.split("\n", 1)[0].strip()}
        for key in ("name", "path", "domain", "wiring_class", "wiring_status", "defer_reason", "wired_evidence", "registered_at"):
            km = re.search(rf"^  {key}: (.+)$", e, re.M)
            if km:
                mod[key] = km.group(1).strip().strip('"')
        modules.append(mod)
    return modules, generated_at


def check(registry: Path, days: int, today: str | None) -> tuple[list[str], list[str]]:
    """返回 (problems, orphans)。problems=结构缺陷；orphans=超期未接线清单。"""
    problems: list[str] = []
    orphans: list[str] = []
    if not registry.exists():
        return [f"registry missing: {registry}"], []
    modules, generated_at = _parse_registry(registry.read_text(encoding="utf-8"))
    if not modules:
        problems.append("registry has zero modules")
    try:
        base_date = _dt.date.fromisoformat(today) if today else _dt.date.today()
    except ValueError:
        problems.append(f"bad date: today={today}")
        return problems, []
    if generated_at:
        try:
            _dt.date.fromisoformat(generated_at)
        except ValueError:
            problems.append(f"bad generated_at {generated_at}")
    for mod in modules:
        cid = mod.get("candidate_id", "<unknown>")
        for key in REQUIRED_KEYS:
            if key not in mod:
                problems.append(f"{cid}: missing key {key}")
        cls = mod.get("wiring_class")
        if cls and cls not in VALID_CLASSES:
            problems.append(f"{cid}: invalid wiring_class {cls}")
        status = mod.get("wiring_status")
        if status and status not in VALID_STATUS:
            problems.append(f"{cid}: invalid wiring_status {status}")
        if status == "unwired":
            mod_date_str = mod.get("registered_at") or generated_at
            try:
                mod_date = _dt.date.fromisoformat(mod_date_str) if mod_date_str else None
            except ValueError:
                problems.append(f"{cid}: bad registered_at {mod_date_str}")
                continue
            if mod_date is not None:
                age = (base_date - mod_date).days
                if age > days:
                    orphans.append(f"{cid} ({mod.get('path', '?')}) age={age}d > {days}d")
    return problems, orphans


def main() -> int:
    parser = argparse.ArgumentParser(description="装配超期门禁（wiring orphan gate）")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--days", type=int, default=90, help="超期阈值（默认 90 天）")
    parser.add_argument("--today", type=str, default=None, help="测试用日期注入 YYYY-MM-DD")
    parser.add_argument("--strict", action="store_true", help="门禁模式：有 orphan 即 exit 1")
    args = parser.parse_args()

    problems, orphans = check(args.registry, args.days, args.today)
    for p in problems:
        print(f"[STRUCT] {p}")
    for o in orphans:
        print(f"[ORPHAN] {o}")
    print(f"summary: problems={len(problems)} orphans={len(orphans)} (threshold={args.days}d)")
    if problems:
        return 2
    if args.strict and orphans:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
