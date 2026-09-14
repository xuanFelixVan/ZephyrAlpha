# -*- coding: utf-8 -*-
# [BLUEPRINT] MOD-GOV-INDUSAGE
# [MODULE] zephyr.governance.indicator_usage_audit
# [DOMAIN] D_GOV
# [DEPENDENCIES] zephyr.shared.io.file_utils(safe_write); pathlib(静态扫描)
# [CONSUMERS] trading_lifecycle_weekly 任务（capability 分支）; 指标域会话（零消费退役建议消费方）
# [STARTUP] imported(周末校准档事件触发;禁 cron 自轮询)
# [MATURITY] design
# [INVARIANTS] 静态扫描零写副作用(只读源码+配置); 台账 JSON safe_write; 判定=消费活性非统计闸(指标无预测力语义); active=消费者≥1 / stale=仅注册表自引用 / zero=零消费(退役建议); 扫描范围注入(测试 tmp_path); 同输入必同输出
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] registry 不可读->IOError 透传; 扫描根不存在->ValueError
# [TESTS] tests/governance/test_indicator_usage_audit.py(tmp_path 合成仓库)
# [A_module] module_id=MOD-GOV-INDUSAGE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""indicator_usage_audit — 指标消费活性台账（MOD-GOV-INDUSAGE，协议 v2.0 指标域落地）。

指标是变换不是信号：生命周期退化为"正确性+消费活性"，不上统计闸。
静态扫描仓库源码/配置，对 technical_indicator_registry 全部 IND-* 统计
消费引用（registry 自身文件除外），产出台账：

    active（消费者≥1）/ stale（仅注册表自引用）/ zero（零消费→退役建议）

退役建议供指标域会话消费（状态翻转归指标域管线——边界）。
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from zephyr.shared.io.file_utils import safe_write_text

__all__ = ["run_indicator_usage_audit"]

_DEFAULT_REGISTRY = "docs/01_policies_and_standards/_registry/catalogs/technical_indicator_registry.yaml"
_SCAN_EXCLUDE_DIRS = {".git", ".runtime", "__pycache__", "node_modules", ".venv", "tmp"}
_SCAN_EXTS = {".py", ".yaml", ".yml", ".json", ".js", ".md", ".ps1", ".sh"}


def load_indicator_ids(registry_path: str | Path) -> list[str]:
    """读注册表全部 indicator_id（92 条口径）。"""
    import yaml

    reg = yaml.safe_load(Path(registry_path).read_text(encoding="utf-8"))
    items = reg.get("indicators") or reg.get("technical_indicators") or []
    return [it["indicator_id"] for it in items if it.get("indicator_id")]


def _iter_source_files(scan_root: Path, *, exclude_registry: Path | None = None) -> Iterable[Path]:
    # 排除目录按「相对扫描根」的 parts 判断——绝对 parts 会把扫描根本身位于
    # .runtime/tmp 下的 pytest tmp_path 全军覆没（W-R 实测坑）
    for p in scan_root.rglob("*"):
        if not p.is_file() or p.suffix not in _SCAN_EXTS:
            continue
        rel_parts = p.relative_to(scan_root).parts
        if any(part in _SCAN_EXCLUDE_DIRS for part in rel_parts[:-1]):
            continue
        if exclude_registry is not None and p.resolve() == exclude_registry.resolve():
            continue
        yield p


def run_indicator_usage_audit(
    registry_path: str | Path = _DEFAULT_REGISTRY,
    *,
    scan_root: str | Path | None = None,
    output_path: str | Path = "data/runtime/indicator_usage_ledger.json",
    today: str = "2026-09-15",
) -> dict:
    """消费活性审计入口：读注册表→全仓扫描引用→台账落盘→返回摘要。

    scan_root 注入供测试（生产=仓库根）。
    """
    registry_path = Path(registry_path)
    ids = load_indicator_ids(registry_path)
    if not ids:
        raise ValueError(f"注册表无指标条目: {registry_path}")
    root = Path(scan_root) if scan_root is not None else registry_path.parents[3]
    if not root.exists():
        raise ValueError(f"扫描根不存在: {root}")
    consumers: dict[str, set[str]] = {i: set() for i in ids}
    # 代码引用惯例=下划线形式（IND-A → IND_A）；连字符/下划线双形式匹配
    id_variants = {i: (i, i.replace("-", "_")) for i in ids}
    registry_resolved = str(registry_path.resolve())
    for f in _iter_source_files(root, exclude_registry=registry_path):
        fstr = str(f)
        if fstr == registry_resolved:
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for ind, (hyphen, underscore) in id_variants.items():
            if hyphen in text or underscore in text:
                consumers[ind].add(fstr)
    entries: list[dict[str, Any]] = []
    counts: dict[str, int] = {"active": 0, "stale": 0, "zero": 0}
    for ind in ids:
        n = len(consumers[ind])
        state = "active" if n >= 1 else "zero"
        counts[state] = counts.get(state, 0) + 1
        entries.append({
            "indicator_id": ind, "state": state,
            "consumer_files": n, "recommendation": (
                "keep" if state == "active" else
                "retire_candidate(零消费，指标域会话核实后处置)"
            ),
        })
    entries.sort(key=lambda e: e["indicator_id"])
    doc = {"schema": "indicator_usage/1", "updated_at": today,
           "counts": counts, "entries": entries}
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    safe_write_text(
        str(output_path), json.dumps(doc, ensure_ascii=False, indent=1) + "\n", newline="\n"
    )
    return {"total": len(ids), "counts": counts, "ledger": str(output_path)}
