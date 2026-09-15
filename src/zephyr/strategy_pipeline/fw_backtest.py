# [BLUEPRINT] MOD-BT-198 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.strategy_pipeline.fw_backtest
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.strategy_pipeline.pipeline_events（journal/告警原语，import 复用非修改）;
#   zephyr.pf_core.strategy_engine.framework_composer; zephyr.pf_core.strategy_engine.translated_strategy_adapter;
#   scripts/backtest/generate_framework_plan_from_tdm（子进程）; scripts/backtest/print_regime_history（子进程，regime 供给）
# [CONSUMERS] scripts/backtest/auto_mount.py（挂图落地后 emit_fw_backtest_due）;
#   管线 CLI（python -m zephyr.strategy_pipeline.fw_backtest run）
# [STARTUP] imported（本模块不建线程/不建调度器；重活=子进程隔离+超时）
# [MATURITY] experimental
# [INVARIANTS] 契约钉死 run_fw_backtest_due(event: dict) -> dict；事件不丢（journal 先落，
#   成功才出队，失败留档计 attempts 毒丸告警）；重活子进程隔离（生成器/回测/regime 印制均
#   subprocess+超时，禁长活阻塞挂图进程主流程）；证据包必含 plan 身份/面板对账/核心指标/
#   bt-fw 产物路径/时间戳（验收五要素）；幂等=plan 指纹（权重+TDM sha）不变且最近一次 ok
#   →跳过重跑（force=True 可越过）；语义失败（对账超容差/空净值）不重试——落证据包+ERROR
#   告警+消费出队（同输入重跑结果必然相同，重试无意义）；瞬时故障（生成器 rc≠0/CH 不可达/
#   异常）上抛留 journal 等重放
# [MODIFY-GUARD] tests/strategy_pipeline/test_fw_backtest.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(生成器失败/方案缺失/CAS 冲突/子进程超时)——由 drain 语义保留重试
# [TESTS] tests/strategy_pipeline/test_fw_backtest.py
# [A_module] module_id=MOD-BT-198 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""fw_backtest_due 自动触发件——挂图成功→整装组合回测自动跑→证据包落档（断桥③桥件）。

流程（S11 README §5 施工项 3，四步）:
  ① 重跑方案表生成器（generate_framework_plan_from_tdm，子进程）——TDM sleeves→fw-tdm-current；
  ② 幂等闸: plan 指纹（成员权重+TDM sha12）与最近一次 ok 证据包相同→跳过（返回 skipped 摘要）；
  ③ 组装参数: symbols=沪深300 成份快照 ∪ STR 成员面板列并集（预取缓存零二次 build）；
     窗口=滚动 12 个月（payload 可覆盖）；regime 日序=regime_snapshot_history.dominant
     窗口内日序（可用则附——fw-tdm-current 无 regime_overrides 时纯披露口径，权重不变）；
  ④ run_framework_backtest → 验收（panel_reconciliation.within_tolerance ∧ equity_points>0）
     → 证据包 JSON 落 data/backtest_artifacts/fw-auto/（fw-auto-<ts>-<fp8>.json + latest.json）。

事件语义（本班裁定留痕——pipeline_events.py 并行编辑禁令未动其文件）:
  fw_backtest_due 为重 kind（分钟级），但 pipeline_events 的 LIGHT/HEAVY 词表与
  _default_handler 分派表不含本 kind（本班不能改该文件）；故 emit_fw_backtest_due 自带
  消费路径：journal record → 子进程执行本模块 CLI → rc==0 出队 / 失败留档（attempts 语义
  与 drain 同款，≥3 毒丸告警）。若未来把 fw_backtest_due 注册进 pipeline_events 分派表，
  emit 帮手自动兼容（消费体仍是本模块 run_fw_backtest_due）。

regime 日序供给（S11 README §5 施工项 4）——精确挂法登记（主会话执行，DataScheduler 重启
属受控步骤，本班不改 tasks.yaml）:
  现状: c1_backtest.regime_snapshot_history 唯一写方=print_regime_history.py（manual CLI，
  无排班；全窗 walk-forward 逐日重印，append-only 台账）。
  建议挂点 A（首选，零新机制）: pipeline_events.wire_data_scheduler 的 _on_task_completed
  钩子里加一行 `fw_backtest.ensure_regime_snapshot()`（有数据任务完成=自然唤醒点，事件触发
  合规；staleness≤3 天零成本返回，超限只告警不阻塞——refresh=True 才印制）。
  建议挂点 B（备选）: DataScheduler tasks.yaml 增 kind=regime_snapshot_daily 事件
  （daily_kline 完成唤醒，重 kind 显式 drain 消费）。
  本班已交付: ensure_regime_snapshot()/regime_snapshot_freshness() 可直接调用；
  fw_backtest_due 证据包自动引用表新鲜度。

用法:
    python -m zephyr.strategy_pipeline.fw_backtest run --payload '{"trigger":"manual"}'
真源: docs/_working/full-auto-chain/S11_assembled_backtest/README.md §5 施工项 3/4。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE_DIR = ROOT / "data" / "backtest_artifacts" / "fw-auto"
GENERATOR_SCRIPT = ROOT / "scripts" / "backtest" / "generate_framework_plan_from_tdm.py"
REGIME_WRITER_SCRIPT = ROOT / "scripts" / "backtest" / "print_regime_history.py"
PLAN_ID = "fw-tdm-current"
DEFAULT_TIMEOUT_S = 3600  # S11 §5 施工项 5 首值
_REGIME_STALE_DAYS = 3

_EVENT_KIND = "fw_backtest_due"


# ---------- 幂等指纹 ----------

def plan_fingerprint(plans_path: str | Path | None = None) -> dict[str, Any]:
    """fw-tdm-current 身份指纹：成员权重表 + TDM 源 sha12（变更即新指纹）。"""
    from zephyr.pf_core.strategy_engine.framework_composer import get_framework_plan

    plan = get_framework_plan(PLAN_ID, plans_path)
    weights = {w.strategy_id: round(w.weight, 9) for w in plan.weights}
    raw = (Path(plans_path) if plans_path else ROOT / "config" / "framework_plans.yaml").read_text(
        encoding="utf-8"
    )
    import re

    m = re.search(r"source_sha256_12: ([0-9a-f]{12})", raw)
    payload = json.dumps({"weights": weights, "tdm": m.group(1) if m else ""}, sort_keys=True)
    return {
        "plan_id": PLAN_ID,
        "weights": weights,
        "tdm_sha256_12": m.group(1) if m else None,
        "fingerprint": hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12],
    }


def _latest_evidence() -> dict[str, Any] | None:
    latest = EVIDENCE_DIR / "latest.json"
    if not latest.exists():
        return None
    try:
        return json.loads(latest.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


# ---------- 输入组装 ----------

def default_window(today: date | None = None) -> tuple[str, str]:
    """滚动 12 个月窗口（S11 §5：start/end=近 12 个月滚动窗）。"""
    end = today or date.today()
    start = end - timedelta(days=365)
    return start.isoformat(), end.isoformat()


def _hs300_symbols() -> list[str]:
    """沪深300 成份快照（纯 6 位代码；与 _c4_engine.load_hs300 同真源同口径）。"""
    from zephyr.data.ch_writer import get_client_strict

    rows = get_client_strict().execute(
        "SELECT symbol_canonical FROM c1_market.index_constituent "
        "WHERE index_code = '000300.SH' AND valid_to IS NULL"
    )
    syms = sorted({(r[0] or "")[:6] for r in rows if r[0]})
    if not syms:
        raise RuntimeError("index_constituent 沪深300 成份缺失——自动标的池不可组装")
    return syms


def resolve_symbols(
    start: str, end: str, base: list[str] | None = None
) -> tuple[list[str], dict[str, Any]]:
    """自动标的池=基池（默认沪深300 快照）∪ STR 成员面板列并集（预取触发缓存）。

    返回 (symbols, info)；info.str_columns_by_sid 供证据包披露各 STR 成员标的宇宙。
    """
    from zephyr.pf_core.strategy_engine.translated_strategy_adapter import (
        is_translated_member,
        prefetch_translated_panels,
    )

    from zephyr.pf_core.strategy_engine.framework_composer import get_framework_plan

    plan = get_framework_plan(PLAN_ID)
    str_ids = [w.strategy_id for w in plan.weights if is_translated_member(w.strategy_id)]
    panels = prefetch_translated_panels(str_ids, start, end)
    str_cols: set[str] = set()
    by_sid: dict[str, int] = {}
    for sid, panel in panels.items():
        cols = {str(c) for c in panel.columns}
        str_cols |= cols
        by_sid[sid] = len(cols)
    symbols = sorted(set(base or _hs300_symbols()) | str_cols)
    return symbols, {"str_members": str_ids, "str_columns_n": by_sid, "total": len(symbols)}


def load_regime_series(start: str, end: str) -> dict[str, Any]:
    """regime_snapshot_history.dominant 窗口日序（可用=附作披露口径；空/异常=静态降级）。"""
    out: dict[str, Any] = {"mode": "static", "series": None, "freshness": None, "note": ""}
    try:
        from zephyr.data.ch_writer import get_client_strict

        rows = get_client_strict().execute(
            f"SELECT trade_date, dominant FROM c1_backtest.regime_snapshot_history "
            f"WHERE trade_date >= '{start}' AND trade_date <= '{end}' ORDER BY trade_date"
        )
        out["freshness"] = regime_snapshot_freshness()
        if rows:
            series = {str(r[0])[:10]: str(r[1]) for r in rows}
            out.update({"mode": "dynamic_disclosure", "series": series,
                        "note": "fw-tdm-current 无 regime_overrides——日序仅供分段披露，权重=基准（查表语义）"})
        else:
            out["note"] = "窗口内无 regime 快照行——静态模式降级"
    except Exception as exc:  # noqa: BLE001——regime 供给失败降静态，不阻断整装跑
        out["note"] = f"regime 日序加载失败（静态降级）: {type(exc).__name__}: {exc}"[:160]
    return out


# ---------- 核心契约 ----------

def run_fw_backtest_due(event: dict) -> dict[str, Any]:
    """fw_backtest_due 事件处理体（契约钉死）。

    Args:
        event: 完整事件 {"kind", "payload", ...} 或裸 payload dict；payload 建议
            {"trigger": "auto_mount", "sids": [...]}，可选 start/end/symbols/force/timeout_s。

    Returns:
        摘要 dict（ok/skipped/evidence_path/run_id/plan/window/acceptance/...）。

    Raises:
        RuntimeError: 瞬时故障（生成器 rc≠0、方案缺失、参数组装失败）——journal 留档重试。
    """
    from zephyr.pf_core.strategy_engine.framework_composer import (
        FrameworkBacktestConfig,
        run_framework_backtest,
    )

    t0 = time.time()
    payload = dict(event.get("payload") or event) if isinstance(event, dict) else {}
    trigger = str(payload.get("trigger", "manual"))
    force = bool(payload.get("force", False))

    # ① 方案表生成器（子进程隔离；rc≠0=瞬时故障留 journal 重试）
    gen = _run_generator(payload.get("timeout_s"))

    # ①.5 regime 日序新鲜度闸（fresh=零成本直通；stale=告警披露进证据包，不阻断跑批）
    regime_guard = ensure_regime_snapshot()

    # ② 幂等闸：指纹未变且最近一次 ok → 跳过（自裁留痕：同指纹重跑结果必然逐位同——
    #    面板由同窗口同数据决定，引擎确定性；省分钟级重跑与产物膨胀）
    fp = plan_fingerprint()
    latest = _latest_evidence()
    if not force and latest and latest.get("plan", {}).get("fingerprint") == fp["fingerprint"] \
            and latest.get("acceptance", {}).get("ok"):
        return {
            "ok": True,
            "skipped": "plan_fingerprint_unchanged（同指纹最近已 ok，force=true 可强制重跑）",
            "plan_fingerprint": fp["fingerprint"],
            "latest_evidence": str(latest.get("evidence_path", "")),
            "generator": gen,
        }

    # ③ 参数组装（窗口/标的池/regime 日序）
    start = str(payload.get("start") or default_window()[0])
    end = str(payload.get("end") or default_window()[1])
    base = payload.get("symbols") or None
    symbols, sym_info = resolve_symbols(start, end, base)
    regime = load_regime_series(start, end)

    config = FrameworkBacktestConfig(
        regime_by_date=regime.get("series"),
        enable_stk_limit_provider=bool(payload.get("enable_stk_limit_provider", True)),
    )
    result = run_framework_backtest(PLAN_ID, symbols, start, end, config=config)

    # ④ 验收+证据包
    recon = result.get("panel_reconciliation") or {}
    acceptance = {
        "ok": bool(result.get("ok")) and bool(recon.get("within_tolerance"))
        and int(result.get("equity_points") or 0) > 0,
        "run_ok": bool(result.get("ok")),
        "within_tolerance": bool(recon.get("within_tolerance")),
        "equity_points": int(result.get("equity_points") or 0),
    }
    metrics = result.get("metrics") or {}
    core_metrics = {
        k: metrics.get(k)
        for k in ("total_return", "annual_return", "sharpe_ratio", "max_drawdown",
                  "win_rate", "trades_count")
        if k in metrics
    }
    summary: dict[str, Any] = {
        "ok": acceptance["ok"],
        "trigger": trigger,
        "sids": payload.get("sids") or [],
        "plan": {**fp, "name": result.get("plan_id"), "static_mode": regime["mode"] != "dynamic_disclosure"},
        "window": {"start": start, "end": end},
        "symbols_total": sym_info["total"],
        "symbols_info": sym_info,
        "regime": {k: regime[k] for k in ("mode", "freshness", "note") if k in regime}
        | {"freshness_guard": regime_guard.get("action")},
        "regime_day_counts": result.get("regime_day_counts") or {},
        "run": {
            "ok": result.get("ok"),
            "run_id": result.get("run_id"),
            "artifact_path": f"data/backtest_artifacts/{result.get('run_id')}.json"
            if result.get("run_id") else None,
            "participants": result.get("participants"),
            "skipped": result.get("skipped"),
            "rescale_factor": result.get("rescale_factor"),
            "warn": result.get("warn"),
            "panel_reconciliation": recon,
            "equity_points": result.get("equity_points"),
            "trades": result.get("trades"),
            "core_metrics": core_metrics,
        },
        "generator": gen,
        "duration_s": round(time.time() - t0, 1),
        "acceptance": acceptance,
    }
    evidence_path = _write_evidence(summary)
    summary["evidence_path"] = str(evidence_path)
    if not acceptance["ok"]:
        _alert(
            f"fw-tdm-current 整装回测验收未过: ok={acceptance['run_ok']} "
            f"within_tolerance={acceptance['within_tolerance']} "
            f"equity_points={acceptance['equity_points']} warn={result.get('warn')!r} "
            f"evidence={evidence_path}",
            level="ERROR",
        )
    return summary


def _run_generator(timeout_payload: Any) -> dict[str, Any]:
    """重跑方案表生成器（子进程；--check 语义内置在生成器幂等里）。"""
    timeout_s = int(timeout_payload or DEFAULT_TIMEOUT_S)
    t0 = time.time()
    proc = subprocess.run(
        [sys.executable, str(GENERATOR_SCRIPT)],
        capture_output=True, text=True, timeout=timeout_s, cwd=str(ROOT),
        encoding="utf-8", errors="replace",
    )
    if proc.returncode != 0:
        raise RuntimeError(f"方案表生成器失败 rc={proc.returncode}: {(proc.stderr or '')[-300:]}")
    try:
        out = json.loads(proc.stdout.strip().splitlines()[-1]) if proc.stdout.strip() else {}
    except ValueError:
        out = {"raw_stdout_tail": (proc.stdout or "")[-200:]}
    return {"rc": 0, "duration_s": round(time.time() - t0, 1), "summary": out}


def _write_evidence(summary: dict[str, Any]) -> Path:
    """证据包落档：fw-auto-<ts>-<fp8>.json + latest.json（safe_write_text；时间戳命名不覆盖历史）。"""
    from zephyr.shared.io.file_utils import safe_write_text

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    fp8 = (summary.get("plan", {}).get("fingerprint") or "00000000")[:8]
    path = EVIDENCE_DIR / f"fw-auto-{stamp}-{fp8}.json"
    body = json.dumps(summary, ensure_ascii=False, indent=1, default=str)
    r = safe_write_text(path, body, newline="\n")
    if not getattr(r, "written", True):
        raise RuntimeError(f"证据包写入未确认: {path}")
    latest = dict(summary)
    latest["evidence_path"] = str(path)  # latest 与分档件同构（跳过闸读 plan/acceptance 两键）
    safe_write_text(EVIDENCE_DIR / "latest.json",
                    json.dumps(latest, ensure_ascii=False, indent=1, default=str), newline="\n")
    return path


# ---------- regime 日序供给（挂点登记见模块 docstring） ----------

def regime_snapshot_freshness() -> dict[str, Any]:
    """regime_snapshot_history 新鲜度（max(trade_date)/行数/滞后天数）。"""
    from zephyr.data.ch_writer import get_client_strict

    row = get_client_strict().execute(
        "SELECT max(trade_date), count() FROM c1_backtest.regime_snapshot_history"
    )[0]
    max_date = row[0]
    stale_days = (date.today() - max_date).days if max_date else -1
    return {
        "max_trade_date": str(max_date) if max_date else None,
        "rows": int(row[1]),
        "stale_days": int(stale_days),
        "checked_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }


def ensure_regime_snapshot(
    max_staleness_days: int = _REGIME_STALE_DAYS,
    refresh: bool = False,
    timeout_s: int = DEFAULT_TIMEOUT_S,
) -> dict[str, Any]:
    """regime 日序供给件（最小实现）：staleness 检查→（默认）告警 /（refresh=True）子进程印制。

    调度挂点=管线唤醒钩子（挂法登记见模块 docstring；本函数零副作用可安全挂）。
    """
    fresh = regime_snapshot_freshness()
    if fresh["stale_days"] <= max_staleness_days:
        return {"action": "fresh", **fresh}
    msg = (f"regime_snapshot_history 滞后 {fresh['stale_days']} 天"
           f"（max={fresh['max_trade_date']}）——整装动态模式日序供给告急")
    if not refresh:
        _alert(msg, level="WARN")
        return {"action": "stale_alert_only", **fresh}
    proc = subprocess.run(
        [sys.executable, str(REGIME_WRITER_SCRIPT)],
        capture_output=True, text=True, timeout=timeout_s, cwd=str(ROOT),
        encoding="utf-8", errors="replace",
    )
    if proc.returncode != 0:
        _alert(f"regime 印制失败 rc={proc.returncode}: {(proc.stderr or '')[-200:]}", level="ERROR")
        return {"action": "refresh_failed", "rc": proc.returncode, **fresh}
    return {"action": "refreshed", "rc": 0, **regime_snapshot_freshness()}


# ---------- emit 帮手（写侧钩子，auto_mount 调用） ----------

def emit_fw_backtest_due(trigger: str, sids: list[str] | None = None, **extra: Any) -> dict[str, Any]:
    """journal record + 子进程立即消费（成功出队/失败留档）。任何异常不反噬调用方主流程由调用方兜。

    与 c4_batch_screen._emit_pipeline_hook 同款防御姿态：本函数自身不抛（故障转告警+返回值）。
    """
    from zephyr.strategy_pipeline import pipeline_events as pe

    payload: dict[str, Any] = {"trigger": trigger, "sids": list(sids or []), **extra}
    evt = pe.record(_EVENT_KIND, payload)
    timeout_s = int(payload.get("timeout_s") or DEFAULT_TIMEOUT_S)
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "zephyr.strategy_pipeline.fw_backtest",
             "run", "--payload", json.dumps(payload, ensure_ascii=False)],
            capture_output=True, text=True, timeout=timeout_s, cwd=str(ROOT),
            encoding="utf-8", errors="replace",
        )
    except Exception as exc:  # noqa: BLE001——超时/启动失败=留档等重放
        _retain_event(pe, evt, f"{type(exc).__name__}: {exc}"[:200])
        return {"event": evt["id"], "drained": False, "error": str(exc)[:200]}
    if proc.returncode != 0:
        _retain_event(pe, evt, f"rc={proc.returncode} {(proc.stderr or '')[-200:]}")
        return {"event": evt["id"], "drained": False, "rc": proc.returncode}
    _dequeue_event(pe, evt)
    result_tail = (proc.stdout or "").strip().splitlines()[-1] if (proc.stdout or "").strip() else "{}"
    return {"event": evt["id"], "drained": True, "result_tail": result_tail[:500]}


def _retain_event(pe: Any, evt: dict[str, Any], err: str) -> None:
    """失败留档：attempts+1，≥MAX_ATTEMPTS 毒丸告警（与 drain 同款语义，不动 pipeline_events 文件）。"""
    try:
        evts = pe.pending()
        for e in evts:
            if e["id"] == evt["id"]:
                e["attempts"] = int(e.get("attempts", 0)) + 1
                e["last_error"] = err
                if e["attempts"] >= pe.MAX_ATTEMPTS:
                    e["poison"] = True
                    _alert(f"管线事件毒丸留档: {evt['id']} kind={evt['kind']} err={err}", level="ERROR")
        pe._rewrite(evts)
    except Exception:  # noqa: BLE001——簿记失败不反噬
        pass
    _alert(f"fw_backtest_due 消费失败（事件留 journal 待重放）: {evt['id']} {err}", level="WARN")


def _dequeue_event(pe: Any, evt: dict[str, Any]) -> None:
    """成功出队+回执（只动本事件，不碰 journal 其余事件）。"""
    try:
        pe._rewrite([e for e in pe.pending() if e["id"] != evt["id"]])
        pe._save_receipt({
            "processed": [{"id": evt["id"], "kind": evt["kind"], "result": "fw_backtest_done"}],
            "failed": [], "skipped": [], "stop_reason": None,
            "pending_left": len(pe.pending()),
        })
    except Exception:  # noqa: BLE001
        pass


def _alert(message: str, level: str = "WARN") -> None:
    try:
        from zephyr.strategy_pipeline.pipeline_events import alert as pe_alert

        pe_alert(message, level=level)
    except Exception:  # noqa: BLE001——告警通道故障不反噬主流程
        pass


# ---------- CLI（子进程消费入口） ----------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="fw_backtest_due 触发件 CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="执行一次整装回测（emit 帮手子进程入口）")
    r.add_argument("--payload", default="{}", help="事件 payload JSON")
    f = sub.add_parser("freshness", help="regime_snapshot_history 新鲜度")
    args = ap.parse_args(argv)
    if args.cmd == "freshness":
        print(json.dumps(regime_snapshot_freshness(), ensure_ascii=False))
        return 0
    out = run_fw_backtest_due({"kind": _EVENT_KIND, "payload": json.loads(args.payload)})
    print(json.dumps(out, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
