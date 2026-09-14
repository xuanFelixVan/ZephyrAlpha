# [BLUEPRINT] MOD-SIG-150
# [MODULE] zephyr.signal_ashare.strategy_signal.strategy_decay_certifier
# [DOMAIN] D_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.strategy_signal.pattern_lifecycle(LifecycleStore 台账复用); zephyr.data.ch_writer(延迟 client)
# [CONSUMERS] trading_lifecycle_weekly 任务（capability 分支）; 策略域会话（退役建议台账消费方，状态翻转归策略域管线——边界）
# [STARTUP] imported(周末校准档事件触发;禁 cron 自轮询)
# [MATURITY] design
# [INVARIANTS] 只读 c1_backtest.backtest_strategy_screen（FINAL 每策略最新行）；判定阈值预注册（DS≥0.5 且有 OOS→certified / 0≤DS<0.5→probation / DS<0→failed / 连续 FAILED_WINDOWS=8 周扫 failed→retired 建议）；产出=衰减建议台账 JSON（不翻转策略域注册表状态——晋升侧 E0-E9 归属域管线，边界）；retired 后新 screen 行 DS≥0.5→resurrected；同输入必同输出
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH 不可达->RuntimeError(经 FetchResult.error 透传); 空 universe->空摘要非错误
# [TESTS] tests/signal_ashare/strategy_signal/test_strategy_decay_certifier.py(注入 fake client,不触库)
# [A_module] module_id=MOD-SIG-150 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""strategy_decay_certifier — 策略域衰减侧认证器（MOD-SIG-150，协议 v2.0 三域落地）。

晋升侧（E0-E9 工厂流水线+假说预审+holdout 锁窗）归属策略域管线，本模块只做
**衰减侧**：对已入册策略的滚动样本外成绩（strategy_screen 的 deflated_sharpe）
做周期判定，产出退役/复活建议台账——状态翻转由策略域消费台账后执行（边界）。

判定阈值（预注册，改动=裁定）：
    deflated_sharpe ≥ 0.5 且 oos_tested → certified
    0 ≤ deflated_sharpe < 0.5           → probation
    deflated_sharpe < 0                 → failed
    failed 连续 FAILED_WINDOWS=8 个周扫  → retired（建议）
    retired 后新 screen 行 DS ≥ 0.5     → resurrected

# [ALGO_FLOW]
# 层: 策略衰减
# - id: D1
#   name: 最新行判定
#   code: 每策略取 FINAL 最新 screen 行的 deflated_sharpe → 三态
# - id: D2
#   name: 生命周期
#   code: failed 连周计数→retired 建议；retired 后 DS 回升→resurrected（149 台账语义）
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from zephyr.shared.io.file_utils import safe_write_text

__all__ = ["run_strategy_decay_certify"]

FAILED_WINDOWS = 8
_CERTIFIED_DS = 0.5
_DEFAULT_TABLE = "c1_backtest.strategy_screen"
_DEFAULT_LEDGER = "data/runtime/strategy_decay_ledger.json"


def _ensure_client(client=None):
    if client is not None:
        return client
    from zephyr.data import ch_writer

    c = ch_writer.get_client()
    if c is None:
        raise RuntimeError("clickhouse-driver 不可用（client 未注入且 get_client 返回 None）")
    return c


def load_latest_metrics(client, *, table: str = _DEFAULT_TABLE) -> list[dict]:
    """每策略最新 screen 行（按 screen_batch 批次序 last-wins，Python 去重）。

    注意：该表引擎非 Replacing，FINAL 不可用（Code 181 实测）——去重在内存做。
    """
    rows = client.execute(
        f"SELECT strategy_id, deflated_sharpe, is_sharpe, max_drawdown FROM {table} "
        "ORDER BY screen_batch, strategy_id"
    )
    latest: dict[str, dict] = {}
    for r in rows:
        latest[r[0]] = {
            "strategy_id": r[0], "deflated_sharpe": r[1], "is_sharpe": r[2],
            "max_drawdown": r[3],
        }
    return list(latest.values())


def run_strategy_decay_certify(
    client=None,
    *,
    ledger_path: str | Path = _DEFAULT_LEDGER,
    today: str = "2026-09-15",
    rows: list[dict] | None = None,
) -> dict:
    """衰减判定入口：最新行→三态→连周计数→退役/复活建议→台账持久化。"""
    client = _ensure_client(client)
    metrics = rows if rows is not None else load_latest_metrics(client)
    ledger_file = Path(ledger_path)
    history: dict[str, dict] = {}
    if ledger_file.exists():
        doc = json.loads(ledger_file.read_text(encoding="utf-8"))
        history = doc.get("strategies", {})
    counts: dict[str, int] = {}
    strategies: dict[str, dict] = {}
    for m in metrics:
        sid = m["strategy_id"]
        ds = m.get("deflated_sharpe")
        prev = history.get(sid) or {"state": "certified", "failed_streak": 0}
        if prev.get("state") in ("retired", "resurrected"):
            # 复活闸：retired 后 DS 回升→resurrected；否则维持 retired 建议
            if ds is not None and float(ds) >= _CERTIFIED_DS:
                prev["state"] = "resurrected"
                prev["resurrected_at"] = today
                strategies[sid] = {**prev, "state": "resurrected", "ds": ds}
                counts["resurrected"] = counts.get("resurrected", 0) + 1
                continue
            else:
                prev["failed_streak"] = prev.get("failed_streak", 0)
                strategies[sid] = {**prev, "ds": ds}
                counts[prev["state"]] = counts.get(prev["state"], 0) + 1
                continue
        if ds is None:
            state = "probation"  # 无 DS=判不了，Fail-Closed 封顶
        elif float(ds) < 0:
            state = "failed"
        elif float(ds) < _CERTIFIED_DS:
            state = "probation"
        else:
            state = "certified"
        if state == "failed":
            prev["failed_streak"] = prev.get("failed_streak", 0) + 1
        else:
            prev["failed_streak"] = 0
        if prev["failed_streak"] >= FAILED_WINDOWS and state == "failed":
            state = "retired"  # 退役建议（状态翻转归策略域管线）
        strategies[sid] = {**prev, "state": state, "ds": ds}
        counts[state] = counts.get(state, 0) + 1
    doc_out = {"schema": "strategy_decay/1", "updated_at": today, "strategies": strategies}
    ledger_file.parent.mkdir(parents=True, exist_ok=True)
    safe_write_text(
        str(ledger_file), json.dumps(doc_out, ensure_ascii=False, indent=1) + "\n", newline="\n"
    )
    return {"total": len(strategies), "counts": counts, "ledger": str(ledger_file)}
