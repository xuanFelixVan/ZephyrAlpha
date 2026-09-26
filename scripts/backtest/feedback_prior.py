# [BLUEPRINT] MOD-BT-223 | docs/03_modules/_domain_backtest/blueprint.md | §回灌边消费端
# [MODULE] scripts.backtest.feedback_prior
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pathlib/json; zephyr.data.ch_reader（CH 只读，可选注入）
# [CONSUMERS] scripts.backtest.factory_intake_pipeline（FL2：E1 进货方向读数，编排层只读不评分）;
#   scripts.backtest.hypothesis_precheck（FL1：E2 预审先验注记，注入 prompt/notes）;
#   docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md §二 feedback_loops（FL1/FL2 定义真源）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 纯读零写（回灌边消费端不产数据——E6/E9 写入端各自在岗，本件只聚合读数）;
#   fail-open：台账缺/坏/CH 不可达=None/空串，禁静默绿也禁反噬消费方（先验是增益不是依赖）;
#   时戳一律取自数据源（updated_at/最新 trade_date），禁墙钟（RULE-SCHEMA-TZ 同源纪律）;
#   编排层不评分——intake_direction 只产出可读方向面，不做任何配额/闸门决策（FL2 语义=
#   "哪类策略值得多进/少进"的读数呈现，决策权在 E2 生杀门与 Owner）;
#   先验注记在 prompt 中明确"只作背景不作判据"——E2 判定权仍属六问逻辑门，防先验越权
# [MODIFY-GUARD] tests/backtest/test_feedback_prior.py；读数字段变更须同步 strategy_decay_certifier
#   （MOD-SIG-150 写入端）与 sim_attribution_daily DDL 两侧口径
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 全函数 fail-open（None/空串/{"error": ...}），禁 raise 出模块
# [TESTS] tests/backtest/test_feedback_prior.py
# [A_module] module_id=MOD-BT-223 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] mod-bt-223-feedback-prior-20260927
"""法定回灌边 FL1/FL2 的消费端读数件——把"声明性边"变成"消费端可读"（最小闭环）。

骨架总册 §二 feedback_loops 两行长期声明性空转（b2_f25/b2_f28 两作业簿堵点③同判
"全仓无消费实件"）：
  FL1  FAC-E9→FAC-E2  实盘/sim 归因回灌假说先验——消费端=本件 precheck_prior_note
      （hypothesis_precheck 注入预审 prompt 与台账 notes）；
  FL2  FAC-E6→FAC-E1  衰减/失效结论反馈进货方向——消费端=本件 intake_direction
      （factory_intake_pipeline 夜批报告 feedback_prior 段）。

写入端（已在岗，零重建）：
  E6 = data/runtime/strategy_decay_ledger.json（MOD-SIG-150 strategy_decay_certifier 日更）；
  E9 = c1_backtest.sim_attribution_daily（WO-1 归因日账，SIM_DAILY_KINDS FIFO 日更）。

任务级判定口径（EC2 车道）：回灌边最小实现=事件/台账写入端存在且消费端可读——
本件即"消费端可读"的实件锚。
"""

from __future__ import annotations

import json
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT  # SSOT 复用（SSOT-REDEFINITION：禁重定义，paths.py 真源）

DECAY_LEDGER = REPO_ROOT / "data" / "runtime" / "strategy_decay_ledger.json"

# CH 只读单值摘要（schema 真源=schemas/categories/sim_attribution_daily.py）
_SQL_ATTRIBUTION_LATEST = (  # noqa: bare-sql  回灌先验单值摘要常量（_SQL_ 前缀+FINAL 去重；PF_ALLOC_BIZ_DATE_SQL 同款豁免形态）
    "SELECT trade_date, count() AS n, sum(pnl_net) AS net_sum "
    "FROM c1_backtest.sim_attribution_daily FINAL "
    "WHERE trade_date = (SELECT max(trade_date) FROM c1_backtest.sim_attribution_daily FINAL) "
    "GROUP BY trade_date"
)


def decay_prior_digest(ledger_path: Path | str | None = None) -> dict | None:
    """E6 衰减台账→先验读数（纯读；文件缺/坏/空=None 出声不反噬）。

    返回 {"schema", "updated_at", "total", "states": {state: n}, "suspect": [sid...]}；
    suspect=state 非 probation 的存疑/判死条目（decay 面焦点集）。
    """
    p = Path(ledger_path) if ledger_path else DECAY_LEDGER
    try:
        doc = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    strategies = doc.get("strategies")
    if not isinstance(strategies, dict) or not strategies:
        return None
    states: dict[str, int] = {}
    suspect: list[str] = []
    for sid, entry in strategies.items():
        state = str((entry or {}).get("state") or "unknown")
        states[state] = states.get(state, 0) + 1
        if state != "probation":
            suspect.append(str(sid))
    return {
        "schema": doc.get("schema"),
        "updated_at": doc.get("updated_at"),
        "total": len(strategies),
        "states": states,
        "suspect": sorted(suspect),
    }


def attribution_prior_digest(query=None) -> dict | None:
    """E9 归因日账最近一日摘要（CH 不可达/空表→None fail-open；query 可注入供测试）。

    返回 {"trade_date", "strategies", "pnl_net_sum"}。
    """
    if query is None:
        try:
            from zephyr.data.ch_reader import query  # noqa: PLC0415
        except Exception:  # noqa: BLE001 — 模块缺位=降级
            return None
    try:
        rows = query(_SQL_ATTRIBUTION_LATEST) or []
    except Exception:  # noqa: BLE001 — CH 断连/权限=降级（归因面缺证≠先验为零）
        return None
    if not rows:
        return None
    row = rows[0]
    return {
        "trade_date": str(row.get("trade_date") or ""),
        "strategies": int(row.get("n") or 0),
        "pnl_net_sum": float(row.get("net_sum") or 0.0),
    }


def intake_direction(decay: dict | None, attribution: dict | None = None) -> dict:
    """FL2（E6→E1）消费端读数（纯函数）：E1 进货编排的方向面呈现。

    语义=骨架 FAC-E6 algo_note"衰减/失效结论反馈进货方向（哪类策略值得多进/少进）"
    的最小读数形态：在考量/状态分布/存疑清单——只呈现不决策（编排层不评分铁律）。
    """
    out: dict = {"loops": {"FL1": "FAC-E9→FAC-E2", "FL2": "FAC-E6→FAC-E1"}, "sources": {}}
    if decay:
        states_txt = "，".join(f"{k} {v}" for k, v in sorted(decay["states"].items()))
        out["sources"]["decay_ledger"] = {
            "updated_at": decay["updated_at"],
            "total": decay["total"],
            "states": decay["states"],
            "suspect": decay["suspect"],
        }
        note = f"衰减台账（E6，updated {decay['updated_at']}）：在考 {decay['total']} 只（{states_txt}）"
        if decay["suspect"]:
            note += f"；存疑/判死 {len(decay['suspect'])} 只（{'、'.join(decay['suspect'][:5])}"
            if len(decay["suspect"]) > 5:
                note += "等"
            note += "）——同族机制假说进货须附差异化论证"
        out["direction_note"] = note
    else:
        out["direction_note"] = "衰减台账缺证（E6 读数不可用）——方向面缺证如实呈现"
    if attribution:
        out["sources"]["attribution_daily"] = attribution
        out["direction_note"] += (
            f"；归因日账（E9）{attribution['trade_date']}："
            f"{attribution['strategies']} 只净收益合计 "
            f"{attribution['pnl_net_sum']:.2f} 元"
        )
    return out


def precheck_prior_note(decay: dict | None, attribution: dict | None = None) -> str:
    """FL1（E9→E2）消费端（纯函数）：预审先验短注记；双源全缺=空串（零注记零干扰）。

    注入点=hypothesis_precheck.build_prompt（prompt 背景）与判定行 notes（审计面）。
    注记定性="只作背景不作判据"——E2 生杀门判定权仍在六问逻辑，防先验越权。
    """
    parts: list[str] = []
    if decay:
        states_txt = "，".join(f"{k} {v}" for k, v in sorted(decay["states"].items()))
        parts.append(f"衰减台账（E6，updated {decay['updated_at']}）在考 {decay['total']} 只（{states_txt}）")
        if decay["suspect"]:
            parts.append(f"其中存疑/判死 {len(decay['suspect'])} 只——同族机制假说须给出差异化机制论证")
    if attribution:
        parts.append(
            f"归因日账（E9）{attribution['trade_date']} {attribution['strategies']} 只"
            f"净收益合计 {attribution['pnl_net_sum']:.2f} 元"
        )
    if not parts:
        return ""
    return "；".join(parts) + "。（回灌先验只作背景不作判据）"
