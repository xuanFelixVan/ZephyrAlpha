#!/usr/bin/env python
# [TTL] task_bound
# [STARTUP] manual: wave1a VERIFIED 升态窗口手工跑 + tests/governance/test_delivery_card_canary.py 四态 canary
# [CONSUMERS] tests/governance/test_delivery_card_canary.py（check_card 契约消费方）; wave1a 升态窗口操作者
# [MODULE] module_id=MOD-GOV-wave1a-verified_promotion_check | layer=script | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TASK_SYSTEM | docs/03_modules/_domain_infrastructure_runtime/task_system/blueprint.md | §task-system
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] stdlib(pathlib/json/sys/argparse)
# [MATURITY] draft
# [INVARIANTS] 只读判定不改卡状态（流转走 TaskRepository 官方 API，本尺不写库）；判据只升不降（新增判据须与 canary 同批）；缺锚/空锚必 REJECT 禁静默放行；artifact 存在性以现读文件系统为准禁缓存
# [MODIFY-GUARD] 改三判据口径须与 tests/governance/test_delivery_card_canary.py 四例同批（红蓝对齐），禁单独放宽
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 行格式异常按不可判处理并在 reasons 点名，禁吞成 ELIGIBLE（假绿源）
# [TESTS] python -m pytest tests/governance/test_delivery_card_canary.py -q
# create-guard-not-dup: VERIFIED 升态三判据校验器（判 artifact_paths 空锚/缺锚/rb 标记，输出四态判定 CLI）；与 task_repo（卡仓储 CRUD）无同源关系——本尺只读判定不写卡，关键词命中系"卡/校验"字面泛化
"""VERIFIED 升态校验器（wave1a）——升 VERIFIED 前置三判据。

大白话：一张卡自称"完成"想升 VERIFIED，空口无凭。本尺对着卡面做三判据硬校验：

  判据①（empty）：artifact_paths 非空——没有交付物锚点的"完成"不可信；
  判据②（missing）：每个 artifact 路径现读存在——指向不存在路径的锚=伪锚；
  判据③（anchor/rb）：requires_rb_check 为真（或 tags 带 rb-required: 前缀）时
                     必须先过红蓝复核，不得带旗直升。

四态输出（考卷口径）：empty / missing / eligible / rb_anchor_required。
verdict 只有两值：REJECT / ELIGIBLE。

check_card(row, repo_root) 为纯函数契约（row=卡面行 dict，兼容 sqlite Row 反转的
JSON 字符串字段），CLI 走 --cards-json 读卡面行清单逐卡判定，不触生产库。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

VERDICT_REJECT = "REJECT"
VERDICT_ELIGIBLE = "ELIGIBLE"

RB_TAG_PREFIX = "rb-required:"

__all__ = ["check_card", "main"]


def _coerce_json_list(value: Any) -> list:
    """sqlite Row 反转出的 artifact_paths/tags 可能是 JSON 字符串；统一成 list。"""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return []
        try:
            parsed = json.loads(s)
        except (json.JSONDecodeError, ValueError):
            return []
        return parsed if isinstance(parsed, list) else []
    return []


def _coerce_flag(value: Any) -> bool:
    """requires_rb_check 兼容 0/1、bool、"1"/"true" 等存储形态。"""
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


def check_card(row: dict, repo_root: str | Path) -> dict:
    """对一张卡面行做三判据校验，返回 {task_id, verdict, reasons, states}。

    row 至少含 artifact_paths；可选 requires_rb_check / tags / task_id / status。
    判定只读：不写库、不改卡、不追任何 transition。
    """
    repo = Path(repo_root)
    task_id = row.get("task_id") or "<unknown>"
    reasons: list[str] = []
    states: list[str] = []

    artifacts = [a for a in _coerce_json_list(row.get("artifact_paths")) if str(a).strip()]

    # 判据①：锚点非空
    if not artifacts:
        states.append("empty")
        reasons.append(f"判据①：artifact_paths 为空——自称完成却无交付物锚点，不可信（task_id={task_id}）。")
        return {"task_id": task_id, "verdict": VERDICT_REJECT, "reasons": reasons, "states": states}

    # 判据②：锚点现读存在（相对路径按 repo_root 解析，绝对路径原样）
    missing: list[str] = []
    for a in artifacts:
        p = Path(str(a))
        if not p.is_absolute():
            p = repo / p
        if not p.exists():
            missing.append(str(a))
    if missing:
        states.append("missing")
        reasons.append(
            f"判据②：{len(missing)} 个 artifact 锚点现读不存在（无 HEAD 证据锚的自称完成不可信）：" + "；".join(missing)
        )

    # 判据③：rb 旗标（requires_rb_check 为真，或 tags 带 rb-required: 前缀）
    tags = [str(t) for t in _coerce_json_list(row.get("tags"))]
    rb_flag = _coerce_flag(row.get("requires_rb_check")) or any(t.startswith(RB_TAG_PREFIX) for t in tags)
    if rb_flag:
        states.append("rb_anchor_required")
        reasons.append(
            f"判据③：requires_rb_check 为真（tags={tags or '[]'}）——带红蓝复核旗的卡必须先过复核，不得直升 VERIFIED。"
        )

    if states:
        return {"task_id": task_id, "verdict": VERDICT_REJECT, "reasons": reasons, "states": states}

    states.append("eligible")
    reasons.append(f"三判据全过：{len(artifacts)} 个锚点现读在案且无 rb 旗，准升 VERIFIED。")
    return {"task_id": task_id, "verdict": VERDICT_ELIGIBLE, "reasons": reasons, "states": states}


def main(argv: list[str] | None = None) -> int:
    """CLI：--cards-json <file|-> 逐卡判定并打印四态；全 ELIGIBLE 退 0，否则退 1。"""
    ap = argparse.ArgumentParser(description="VERIFIED promotion precheck (criteria 1/2/3)")
    ap.add_argument("--cards-json", required=True, help="卡面行 JSON 清单文件（'-' = stdin）")
    ap.add_argument("--repo-root", default=".", help="相对 artifact 锚点的解析根（默认 cwd）")
    ns = ap.parse_args(argv)

    raw = sys.stdin.read() if ns.cards_json == "-" else Path(ns.cards_json).read_text(encoding="utf-8")
    cards = json.loads(raw)
    if not isinstance(cards, list):
        cards = [cards]

    rc = 0
    for row in cards:
        res = check_card(row, ns.repo_root)
        print(f"{res['task_id']}\t{res['verdict']}\t{'/'.join(res['states'])}")
        for r in res["reasons"]:
            print(f"  - {r}")
        if res["verdict"] != VERDICT_ELIGIBLE:
            rc = 1
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
