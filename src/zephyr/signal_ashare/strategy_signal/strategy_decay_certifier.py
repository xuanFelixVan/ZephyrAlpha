# [BLUEPRINT] MOD-SIG-150
# [MODULE] zephyr.signal_ashare.strategy_signal.strategy_decay_certifier
# [DOMAIN] D_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.strategy_signal.pattern_lifecycle(LifecycleStore 台账复用); zephyr.data.ch_writer(延迟 client);
#   zephyr.shared.io.file_utils(safe_write_text CAS);
#   zephyr.infrastructure.system_telemetry.alerts.ops_alert_feed(退役建议唯一出口，函数级惰性 import)
# [CONSUMERS] trading_lifecycle_weekly 任务（capability 分支，internal_compute_provider 调 run_strategy_decay_certify）;
#   zephyr.strategy_pipeline.promotion_advisory（SIM 预授权第三条件 no_pending_decay_alert 回读本台账）;
#   前端 promotion 页（经 OpsAlertFeed 通知板 → GET /api/ops-notifications，退役建议唯一出口）
# [STARTUP] imported(周末校准档事件触发;禁 cron 自轮询)
# [MATURITY] design
# [INVARIANTS] 只读 c1_backtest.strategy_screen（每策略最新行；表非 Replacing，去重在内存做，
#   平序键显式化为 screen_batch,strategy_id,run_id,ingest_ts——同输入必同输出）；
#   判定阈值预注册（改动=裁定）：DS≥0.5 ∧ 衰减<0.5→certified / 证据缺席或 0≤DS<0.5→probation /
#   oos_years_decay≥0.5→failed（衰减判据挂 DDL 在册 0~1 列；旧判据 DS<0 是 Φ 值域外死分支，
#   SDC-1 治本 2026-09-17）/ 连续 FAILED_WINDOWS=8 周 failed→retired 建议 /
#   retired 后 DS≥0.5 ∧ 衰减<0.5→resurrected（双证齐才复活，缺证维持 retired）；
#   产出=衰减建议台账 JSON + 退役建议落通知板（本件不翻转策略域注册表状态——状态翻转归
#   策略域管线+Owner，边界）；零行输入=闸门失明：不落判决、不覆写台账、必落 critical 告警
#   （绝不静默当健康）；告警通道任何故障不反噬台账产出；同输入必同输出
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH 不可达->RuntimeError(经 FetchResult.error 透传); 空 universe->空摘要非错误，
#   但计 blind_scan 并落 strategy_decay_gate_blind critical（台账保持原样不覆写）
# [TESTS] tests/signal_ashare/strategy_signal/test_strategy_decay_certifier.py(注入 fake client+临时板,不触库)
# [A_module] module_id=MOD-SIG-150 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""strategy_decay_certifier — 策略域衰减侧认证器（MOD-SIG-150，协议 v2.0 三域落地）。

晋升侧（E0-E9 工厂流水线+假说预审+holdout 锁窗）归属策略域管线，本模块只做
**衰减侧**：对已入册策略的滚动样本外成绩（strategy_screen 的 deflated_sharpe 与
oos_years_decay）做周期判定，产出退役/复活建议——台账 + 通知板（promotion 页横幅），
状态翻转由 Owner/策略域消费建议后执行（边界）。

判定阈值（预注册，改动=裁定）：
    deflated_sharpe ≥ 0.5 ∧ oos_years_decay < 0.5  → certified
    证据双缺 / 0 ≤ deflated_sharpe < 0.5           → probation（判不了即封顶，不放行）
    oos_years_decay ≥ 0.5                          → failed
    failed 连续 FAILED_WINDOWS=8 个周扫            → retired（建议）
    retired 后 DS ≥ 0.5 ∧ 衰减 < 0.5               → resurrected

判据真源更正（SDC-1，2026-09-17 施工）：`failed` 原挂 `deflated_sharpe < 0`——DSR 是
Φ(·) 的值，域 [0,1]，生产 1205 行实测负值 0 行 ⇒ 该分支恒假 ⇒ failed/retired/8 周链
全部死码（挖矿报告 coverage_map_cert_gates_mining.md §3 SDC-1）。改挂**同表在册**的
`oos_years_decay`（DDL 注释「0~1,>=0.5 判存疑土规」，与 strategy_lifecycle_advisor
.DECAY_SUSPECT_LINE / strategy_screen_query.DECAY_SUSPECT / api_server._FACTORY_DECAY_SUSPECT
四条既有预注册线同数，非本件自立阈值）。

# [ALGO_FLOW]
# 层: 策略衰减
# - id: D1
#   name: 最新行判定
#   code: 每策略取最新 screen 行的 deflated_sharpe + oos_years_decay → 三态
# - id: D2
#   name: 生命周期
#   code: failed 连周计数→retired 建议；retired 后双证回升→resurrected（149 台账语义）
# - id: D3
#   name: 建议出口
#   code: retired 建议逐策略落 OpsAlertFeed 通知板（promotion 页），消失即 resolve
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Final

from zephyr.shared.io.file_utils import safe_write_text

logger = logging.getLogger(__name__)

__all__: Final = ["LEDGER_PATH", "load_latest_metrics", "run_strategy_decay_certify"]

FAILED_WINDOWS = 8
_CERTIFIED_DS = 0.5
_DECAY_SUSPECT = 0.5
_DEFAULT_TABLE = "c1_backtest.strategy_screen"
#: 衰减建议台账路径（相对仓根；promotion_advisory 的 SIM 预授权第三条件回读同一文件）
LEDGER_PATH = "data/runtime/strategy_decay_ledger.json"

#: 判定终态全集（counts 恒含全部键=缺席也可见，SDC-1「失败模式不可见」治本）
_STATES: Final = ("certified", "probation", "failed", "retired", "resurrected")
#: 需要"双证回升"才解除的终态（resurrected 不在此列——复活后回到常规判定，
#: 否则一次复活即永久豁免衰减闸）
_ENDED_STATES: Final = ("retired",)

# ── 退役建议出口（通知唯一出口=前端 promotion 页，Owner 2026-09-15 裁撤飞书/SMTP）──
_ALERT_MODULE_ID: Final = "strategy-decay-gate"
_RETIRE_KEY_PREFIX: Final = "strategy_retirement_advice:"
_BLIND_KEY: Final = "strategy_decay_gate_blind"
#: 同一建议的复刷节奏=周扫本身（8 周链最长 8 周），板内静默窗口取一扫描周期
_ALERT_SILENCE_WINDOW_S: Final = 7 * 86400.0

# SQL 模板常量（NO-BARE-SQL gate：_SQL_* 前缀定义行）
_SQL_LATEST_METRICS: Final = (
    "SELECT strategy_id, deflated_sharpe, is_sharpe, max_drawdown, oos_years_decay "
    "FROM {table} ORDER BY screen_batch, strategy_id, run_id, ingest_ts"
)


def _ensure_client(client=None):
    if client is not None:
        return client
    from zephyr.data import ch_writer

    c = ch_writer.get_client()
    if c is None:
        raise RuntimeError("clickhouse-driver 不可用（client 未注入且 get_client 返回 None）")
    return c


def load_latest_metrics(client, *, table: str = _DEFAULT_TABLE) -> list[dict]:
    """每策略最新 screen 行（按 screen_batch→strategy_id→run_id→ingest_ts 序 last-wins，Python 去重）。

    注意：该表引擎非 Replacing，FINAL 不可用（Code 181 实测）——去重在内存做。
    平序键必须显式给全（SDC-5）：只按 (screen_batch, strategy_id) 排时 ClickHouse 对
    同键多 run_id 行的返回序不保证，last-wins 会随批次抖动翻转判定结果。
    """
    rows = client.execute(_SQL_LATEST_METRICS.format(table=table))
    latest: dict[str, dict] = {}
    for r in rows:
        latest[r[0]] = {
            "strategy_id": r[0], "deflated_sharpe": r[1], "is_sharpe": r[2],
            "max_drawdown": r[3], "oos_years_decay": r[4],
        }
    return list(latest.values())


def _verdict(m: dict[str, Any]) -> tuple[str, str, bool]:
    """单策略本轮三态判定（纯函数）。返回 (state, reason, 是否证据缺席)。

    可达性（实测口径）：failed 挂 `oos_years_decay ≥ 0.5`——该列真源在表内
    非空 148 行 / max=1.0（2026-09-17 只读 CH），分支非死。
    """
    ds, decay = m.get("deflated_sharpe"), m.get("oos_years_decay")
    if ds is None and decay is None:
        return "probation", "证据双缺（DS 与 oos_years_decay 均 NULL）=判不了，Fail-Closed 封顶", True
    if ds is not None and not 0.0 <= float(ds) <= 1.0:
        return "probation", f"DS 越出定义域 [0,1]（={ds}）=上游口径事故，不作策略判决", False
    if decay is not None and float(decay) >= _DECAY_SUSPECT:
        return "failed", f"按年外样本衰减 {decay} ≥ 存疑线 {_DECAY_SUSPECT}（DDL 土规口径）", False
    if ds is None or float(ds) < _CERTIFIED_DS:
        return "probation", f"未达认证线（DS={ds} < {_CERTIFIED_DS} 或缺衰减外证据）", False
    return "certified", f"DS={ds} ≥ {_CERTIFIED_DS} 且衰减 {decay} 未越线", False


def _revive_entry(prev: dict, m: dict, today: str) -> tuple[dict, str]:
    """退役闸：retired 后须双证齐（DS 达线 ∧ 衰减在册且未越线）才判 resurrected。

    缺任一证据即维持 retired（复活是再准入，判不了不许悄悄放行）。
    """
    ds, decay = m.get("deflated_sharpe"), m.get("oos_years_decay")
    ds_ok = ds is not None and float(ds) >= _CERTIFIED_DS
    decay_ok = decay is not None and float(decay) < _DECAY_SUSPECT
    entry = dict(prev)
    entry.update({"ds": ds, "oos_years_decay": decay})
    if ds_ok and decay_ok:
        entry.update({"state": "resurrected", "resurrected_at": today,
                      "reason": f"复活闸双证齐（DS={ds} ≥ {_CERTIFIED_DS} ∧ 衰减 {decay} < {_DECAY_SUSPECT}）"})
        return entry, "resurrected"
    entry["reason"] = (
        f"维持退役建议：复活需双证（DS≥{_CERTIFIED_DS} ∧ 衰减<{_DECAY_SUSPECT}），"
        f"本轮 DS={ds} 衰减={decay}"
    )
    return entry, str(prev.get("state") or "retired")


def _judge_one(m: dict[str, Any], prev: dict[str, Any], today: str) -> tuple[dict, str, bool]:
    """常规判定 + 连周计数 → (台账条目, 终态, 证据缺席标记)。"""
    if str(prev.get("state")) in _ENDED_STATES:
        entry, state = _revive_entry(prev, m, today)
        return entry, state, False
    state, reason, no_evidence = _verdict(m)
    entry = dict(prev)
    if state == "failed":
        entry["failed_streak"] = int(prev.get("failed_streak") or 0) + 1
        if entry["failed_streak"] >= FAILED_WINDOWS:
            state = "retired"
            reason += f"；连续 {entry['failed_streak']} 周 failed→退役建议"
    else:
        entry["failed_streak"] = 0
    entry.update({
        "state": state, "reason": reason, "ds": m.get("deflated_sharpe"),
        "oos_years_decay": m.get("oos_years_decay"),
    })
    return entry, state, no_evidence


def _judge_round(metrics: list[dict], history: dict[str, dict], today: str) -> tuple[dict, dict, int]:
    """全量策略一轮判定 → (台账 strategies, counts(含零键), 证据缺席数)。"""
    strategies: dict[str, dict] = {}
    counts: dict[str, int] = {s: 0 for s in _STATES}
    no_evidence = 0
    for m in metrics:
        sid = m["strategy_id"]
        prev = history.get(sid) or {"state": "unknown", "failed_streak": 0}
        entry, state, blind = _judge_one(m, prev, today)
        strategies[sid] = entry
        counts[state] = counts.get(state, 0) + 1
        no_evidence += int(blind)
    return strategies, counts, no_evidence


def _load_history(ledger_file: Path) -> dict[str, dict]:
    """读回台账历史（损坏/缺席=空历史，不猜状态）。"""
    if not ledger_file.exists():
        return {}
    try:
        return json.loads(ledger_file.read_text(encoding="utf-8")).get("strategies", {}) or {}
    except (OSError, ValueError):
        logger.warning("衰减台账解析失败（本轮按无历史处理，退役连周计数将重起）: %s",
                       ledger_file, exc_info=True)
        return {}


def _write_ledger(ledger_file: Path, doc_out: dict) -> None:
    ledger_file.parent.mkdir(parents=True, exist_ok=True)
    safe_write_text(
        str(ledger_file), json.dumps(doc_out, ensure_ascii=False, indent=1) + "\n", newline="\n"
    )


# ── 退役建议 → 通知板（唯一出口，桥接方式照抄 breadth_freshness_alerts）────────────
def _feed(board_dir: str | Path | None = None):
    """通知板句柄（fail-safe：构造失败=ERROR 出声 + 返回 None，绝不让出口拖垮台账产出）。"""
    try:
        from zephyr.infrastructure.system_telemetry.alerts.ops_alert_feed import OpsAlertFeed

        return OpsAlertFeed(board_dir=board_dir, module_id=_ALERT_MODULE_ID)
    except Exception as exc:  # noqa: BLE001 — INVARIANTS：出口故障不反噬判定
        logger.error("退役建议出口不可用（OpsAlertFeed 构造失败，本轮建议仅落台账）: %s", exc)
        return None


def _outlet(rows: list[dict] | None, alert_feed, alert_board_dir):
    """通知出口选择：返回 (句柄|None, 出口标记)。

    - 显式注入 alert_feed → 用它（测试临时板）；
    - 注入 rows 但未给 feed → **整条出口关闭**：合成宇宙不是全量真源，据它做
      resolve 联动会误解除生产板上的真实退役告警；
    - rows=None（真读全量扫描）→ 构造生产板句柄。
    """
    if alert_feed is not None:
        return alert_feed, "injected"
    if rows is not None:
        return None, "off"
    feed = _feed(alert_board_dir)
    return (feed, "ops_board") if feed is not None else (None, "unavailable")


def _safe_publish(feed, **kwargs) -> dict:
    """单条落板 fail-safe：异常记日志返回 failed 摘要（告警线自身不得成为故障源）。"""
    try:
        return feed.publish(**kwargs)
    except Exception as exc:  # noqa: BLE001 — INVARIANTS：发布失败不反噬台账
        logger.warning("decay gate publish failed key=%s: %s", kwargs.get("key"), exc)
        return {"op": "failed", "key": kwargs.get("key"), "reason": str(exc)[:120]}


def _safe_resolve(feed, key: str) -> int:
    try:
        return int(feed.resolve(key))
    except Exception as exc:  # noqa: BLE001 — 解除失败同样不反噬
        logger.warning("decay gate resolve failed key=%s: %s", key, exc)
        return 0


def _retire_message(sid: str, entry: dict, today: str) -> str:
    streak = int(entry.get("failed_streak") or 0)
    return (
        f"策略 {sid} 衰减侧判死：连续 {streak} 周 oos_years_decay ≥ {_DECAY_SUSPECT}"
        f"（本轮 DS={entry.get('ds')} 衰减={entry.get('oos_years_decay')}，判定日 {today}）。\n"
        f"判据：{entry.get('reason')}\n"
        f"台账：{LEDGER_PATH}\n"
        "本告警=退役**建议**，不改注册表：终裁归 Owner（FSM production→retired 需 owner_token）"
        "与策略域管线；sim 侧已由 promotion_advisory 的 no_pending_decay_alert 条件自动挡下晋升。"
    )


def _blind_message(reason: str, today: str) -> str:
    return (
        f"衰减闸门本轮失明（{today}）：{reason}\n"
        "strategy_screen 零行 = 无法对任何策略做衰减判定。台账按原样保留（未覆写），"
        "但本轮**没有产出任何健康判定**——不得把 counts 全零读成"
        "「无策略需退役」。须人工确认 c1_backtest.strategy_screen 可达且非空。"
    )


def _board_keys(feed, module_id: str) -> set[str]:
    return {
        str(e.get("key"))
        for e in feed.list_active()
        if e.get("module_id") == module_id and not e.get("resolved_at")
    }


def _publish_advice(strategies: dict[str, dict], *, feed, today: str, outlet: str) -> dict:
    """retired→落板 / 不再 retired（含 resurrected）→resolve；失明告警一并解除。"""
    ops: list[dict] = []
    keys: set[str] = set()
    retired = sum(1 for e in strategies.values() if str(e.get("state")) == "retired")
    if feed is None:
        return {"retired": retired, "ops": [], "outlet": outlet}
    for sid in sorted(strategies):
        entry = strategies[sid]
        if str(entry.get("state")) != "retired":
            continue
        key = _RETIRE_KEY_PREFIX + sid
        keys.add(key)
        ops.append(_safe_publish(
            feed, key=key, severity="critical", title=f"策略退役建议 {sid}",
            message=_retire_message(sid, entry, today), source=_ALERT_MODULE_ID,
            labels={"strategy_id": sid, "ds": entry.get("ds"),
                    "oos_years_decay": entry.get("oos_years_decay"),
                    "failed_streak": int(entry.get("failed_streak") or 0),
                    "ledger": LEDGER_PATH},
            silence_window_s=_ALERT_SILENCE_WINDOW_S,
        ))
    stale = (_board_keys(feed, _ALERT_MODULE_ID) - keys) | {_BLIND_KEY}
    for key in sorted(stale):
        n = _safe_resolve(feed, key)
        if n:
            ops.append({"op": "resolved", "key": key, "count": n})
    return {"retired": len(keys), "ops": ops, "outlet": outlet}


def _publish_blind(feed, reason: str, today: str, outlet: str) -> dict:
    """闸门失明=必须外显的失败模式（counts 全零不等于健康）。"""
    if feed is None:
        return {"op": "skipped", "key": _BLIND_KEY, "outlet": outlet}
    return _safe_publish(
        feed, key=_BLIND_KEY, severity="critical", title="策略衰减闸门零输入（失明）",
        message=_blind_message(reason, today), source=_ALERT_MODULE_ID,
        labels={"table": _DEFAULT_TABLE, "reason": reason},
        silence_window_s=_ALERT_SILENCE_WINDOW_S,
    )


def run_strategy_decay_certify(
    client=None,
    *,
    ledger_path: str | Path = LEDGER_PATH,
    today: str = "2026-09-15",
    rows: list[dict] | None = None,
    alert_feed=None,
    alert_board_dir: str | Path | None = None,
) -> dict:
    """衰减判定入口：最新行→三态→连周计数→退役/复活建议→台账持久化+通知板落板。

    出口规则（_outlet）：alert_feed 注入即用该板（测试临时板，禁写生产 .runtime）；
    rows 注入而未给 alert_feed = 离线判定，**不外呼**（合成宇宙不做 resolve 联动）；
    rows=None 的真读全量扫描才走生产板（OpsAlertFeed 缺省路径，环境变量
    ZEPHYR_OPS_NOTIFICATION_DIR 可重定向）。
    """
    client = _ensure_client(client)
    metrics = rows if rows is not None else load_latest_metrics(client)
    ledger_file = Path(ledger_path)
    feed, outlet = _outlet(rows, alert_feed, alert_board_dir)
    if not metrics:
        return _blind_round(ledger_file, feed, outlet, today)
    history = _load_history(ledger_file)
    strategies, counts, no_evidence = _judge_round(metrics, history, today)
    _write_ledger(ledger_file, {
        "schema": "strategy_decay/2", "updated_at": today, "strategies": strategies,
    })
    alerts = _publish_advice(strategies, feed=feed, today=today, outlet=outlet)
    _log_round(counts, no_evidence, len(strategies), today)
    return {
        "total": len(strategies), "counts": counts, "ledger": str(ledger_file),
        "no_evidence": no_evidence, "blind_scan": False, "alerts": alerts,
    }


def _blind_round(ledger_file: Path, feed, outlet: str, today: str) -> dict:
    """零行输入：不判、不覆写台账、落 critical（治「静默错账+失败模式不可见」）。"""
    reason = f"{_DEFAULT_TABLE} 零行（判定输入为空）"
    logger.error("衰减闸门失明：%s —— 本轮不产出任何判定，台账 %s 保持原样", reason, ledger_file)
    ops = [_publish_blind(feed, reason, today, outlet)]
    return {
        "total": 0, "counts": {s: 0 for s in _STATES}, "ledger": str(ledger_file),
        "no_evidence": 0, "blind_scan": True,
        "alerts": {"retired": 0, "ops": ops, "outlet": outlet},
    }


def _log_round(counts: dict[str, int], no_evidence: int, total: int, today: str) -> None:
    """每轮出声：证据缺席计数与退役建议数一律落日志（缺席不是健康）。"""
    if no_evidence:
        logger.warning(
            "衰减判定 %d 策略中 %d 个证据双缺（按 probation 封顶，非放行）：%s",
            total, no_evidence, today,
        )
    if counts.get("failed") or counts.get("retired"):
        logger.warning(
            "衰减闸门产出建议：failed=%d retired=%d（退役建议已落通知板）",
            counts.get("failed", 0), counts.get("retired", 0),
        )
    logger.info("衰减判定完成：%s counts=%s", today, counts)
