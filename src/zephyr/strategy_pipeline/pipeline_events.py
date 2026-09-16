# [BLUEPRINT] MOD-BT-190 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.strategy_pipeline.pipeline_events
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.strategy_pipeline.intake; zephyr.data.alerter; zephyr.security.access_control.kill_switch(探针);
#   scripts.backtest.sim_paper_ledger(import 复用 ensure_wallet，经 sys.path);
#   scripts.backtest.{sim_platform_journal,sim_deviation_report,sim_governance}(子进程);
#   zephyr.pf_alloc.allocation_orchestrator(子进程 -m，pf_alloc_daily 日分配执行体);
#   zephyr.strategy_pipeline.fw_backtest(import 复用 ensure_regime_snapshot——regime 日序供给，
#     函数级惰性导入避开 fw_backtest 侧对本模块的相互引用);
#   zephyr.infrastructure.database_service(reader 角色——日频产出者共用业务日解析，宪法 §9.1 禁裸连接)
# [CONSUMERS] DataScheduler task_completed（调度器侧 wire_data_scheduler 注册）; c4_batch_screen 落账钩子;
#   intake sim 流转钩子（emit_sim_wallet_due）; 管线 CLI（python -m zephyr.strategy_pipeline.pipeline_events emit/drain/status）
# [STARTUP] imported（本包不建线程/不建调度器；事件持久化=JSONL 日志，恢复重放由 drain 完成）
# [MATURITY] experimental
# [INVARIANTS] 事件不丢：先落 journal 再处理，处理成功才出队；KillSwitch 非 normal 时 drain 停止且全量保留；
#   重资源 kind（c4_batch_due）只经显式 drain（CLI/C4 进程）执行，调度器唤醒钩子只做轻消费（记录+告警）；
#   单条事件重试超 MAX_ATTEMPTS 判毒丸留档+告警，不再自动重试；drain 幂等（消费成功=出队，重放零副作用）；
#   模拟盘件（S08/S09/S10 C1C2）：sim_wallet_due/sim_ledger_daily/sim_journal_daily/sim_deviation_monthly
#   归轻 kind（幂等写/分钟级子进程，月频或日频；sim_deviation_monthly 归轻=无人值守自动消费的显式裁定）；
#   pf_alloc_daily（车道 D 分配链）归轻 kind：payload 必带 trade_date（禁墙钟猜业务日）、
#   trade_date 级 marker 防同日双写（alloc 三表只增不改）、子进程超时 PF_ALLOC_TIMEOUT_S 有界、
#   失败/超时抛错进 attempts 计数（MAX_ATTEMPTS=3 后毒丸留档）；
#   pf_alloc_daily 的**唯一自动产出者=本模块 maybe_emit_pf_alloc_daily**（清单 #15 治本：此前
#   该 kind 有派发/执行体/幂等闸却无发射方=分配链"消而不产"，alloc 三表恒 0 行）——挂
#   daily_kline SUCCESS 唤醒、先于 sim_ledger_daily 入队（分配先落，账本同日开户才拿到真实额度）、
#   业务日=行情最新入库日（resolve_pf_alloc_trade_date，禁墙钟猜日）、解析不出日=不发事件+告警、
#   已成功分配过的业务日永不再自动重发（幂等键=trade_date → 用 _marker_seen 永久闸而非
#   当日口径，否则行情停更/周末唤醒对同一 D 追加重复快照；人工重跑走 CLI/emit 不受此挡）；
#   regime_snapshot_history 的**唯一自动产出者=本模块 maybe_refresh_regime_snapshot**
#   （S11 §5 施工项 4 挂点 A：此前该表唯一写方=manual CLI print_regime_history，两次手工
#   印制之间表静默腐烂；2026-09-16 实测 1809 行/max=2026-09-11/滞后 5 天）——挂同一
#   daily_kline SUCCESS 唤醒且**先于** pf_alloc（分配链 regime 口径读本表）、同一业务日只印
#   一次（写方=全窗重印 append-only，同日二次自动印=纯台账膨胀零信息增益，故用 _marker_seen
#   业务日级永久闸；记号先落再动手=失败不得在每个唤醒点重起分钟级重印）、刷新失败只
#   [REGIME-SNAPSHOT] ERROR 出声、绝不上抛（快照腐烂不许反噬唤醒钩子链）；
#   日件幂等双闸=当日 UTC date-marker（消费成功才落）∨ 非 poison 同 kind 在队；月度档毒丸不堵队
#   （毒丸不算已入队——sim_memo_monthly 从未正常轮转的病根修复，C2/X2）；
#   OPTIONAL_DUE_KINDS 预埋派发缺失=逐出队跳过（不抛不占 attempts，实现由后续批次交付）；
#   行数豁免（GOV-010 分层裁量 301-500 档）：本文件=事件层单抽象族高内聚（journal 原语/KillSwitch
#   探针/告警/各 kind 执行体/调度器注册共享同一组路径常量与 fail-closed 语义），变更隔离面=事件层同批演化
# [MODIFY-GUARD] tests/strategy_pipeline/test_pipeline_events.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(KillSwitch 激活)；IO 异常上抛（journal 不可达=管线故障，fail-closed）
# [TESTS] tests/strategy_pipeline/test_pipeline_events.py; tests/pf_alloc/test_pf_alloc_event_wiring.py
# [A_module] module_id=MOD-BT-190 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] pipeline-events-mod-bt-190-20260915
"""C6 管线事件持久化与消费编排——"事件不丢+KillSwitch 恢复续跑"的本体（交接清单①⑬）。

设计裁定（第一性原理）：C4 批测是独立脚本（MOD-BT-076），不是 DataScheduler 数据任务——
"调度器 task_completed→run_intake"的真链路=三层：
  ①写侧钩子：c4_batch_screen 落账成功后 emit_c4_batch_completed()（同进程直消费）；
  ②持久化：事件先追加 .runtime/strategy_pipeline/pending_events.jsonl，处理成功才出队——
    KillSwitch/进程死亡/异常都不丢，恢复后 drain 重放（幂等由 intake 已入库跳过保证）；
  ③调度器唤醒：wire_data_scheduler() 在 DataScheduler 侧注册 task_completed 轻钩子——
    有数据任务完成=自然唤醒点（禁 cron/Timer 的 event-driven 替代），只消费轻 kind
    （intake 重放/月度审计/模拟盘开户与日件）+ 翻译件积压扫描告警；重 kind（c4_batch_due=
    自动批测）留给显式 drain（CLI 或 C4 进程启动时），重活不偷调度器线程。
模拟盘四件套（S08 开户/S09 日件/S10 月度，C1+C2）：
  sim_wallet_due（intake sim 流转后开户，import 复用账本 ensure_wallet，幂等）；
  sim_ledger_daily → sim_journal_daily（daily_kline 唤醒入队，FIFO 串行，date-marker 日幂等）；
  sim_deviation_monthly（30 天 marker 月度档，成功后串行触发治理建议器）；
  pf_alloc_daily（车道 D：分配链日分配，子进程隔离+有界超时+trade_date 级幂等 marker；
    它是账本 ensure_wallet 钱包额度的上游——分配先落，账本同日开户才拿得到真实额度；
    产出者=本模块 maybe_emit_pf_alloc_daily，与 sim 日件同一 daily_kline SUCCESS 唤醒点、
    且先于其入队。清单 #15 前该 kind 只有派发/执行体没有发射方=分配链恒 0 行的真断点）；
  fw_backtest_due / promotion_advisory_due（预埋派发，实现模块由 S12/S13 批次交付，缺失跳过）；
  regime_snapshot_history 日序台账（S11 §5 施工项 4 挂点 A，挖矿节点 F3 治本）：唯一自动产出者
    =本模块 maybe_refresh_regime_snapshot，与 pf_alloc 同一 daily_kline SUCCESS 唤醒点、且先于
    其调用（分配链的 regime 口径就读这张表，表旧=分配带旧教材）；内部走 fw_backtest.
    ensure_regime_snapshot(refresh=True)——滞后 ≤3 天零成本直通，超限才子进程全窗重印；
    一个业务日至多一印（append-only 台账，同日重印=纯行数膨胀零信息增益）。

用法:
    python -m zephyr.strategy_pipeline.pipeline_events status          # 看积压
    python -m zephyr.strategy_pipeline.pipeline_events drain --all     # 全量消费（含重 kind）
    python -m zephyr.strategy_pipeline.pipeline_events emit c4_batch_due --payload '{}'
"""

from __future__ import annotations

import json
import logging
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Callable

log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[3]
STATE_DIR = ROOT / ".runtime/strategy_pipeline"
JOURNAL = STATE_DIR / "pending_events.jsonl"
RECEIPT = STATE_DIR / "last_receipt.json"

MAX_ATTEMPTS = 3
# 轻 kind=调度器唤醒钩子可消费（有界耗时/只读或幂等写）；重 kind=批测级耗时，只经显式 drain
# sim_deviation_monthly 裁定（C2/X2 自裁留痕）：偏离报告为分钟级子进程（月频），归轻 kind 走
# 调度器唤醒自动消费（无人值守优先）；handler 子进程隔离+超时+失败告警，重活不进主进程。
# pf_alloc_daily（车道 D 分配链，2026-09-16）同归轻 kind：handler=子进程隔离 + 有界超时
# （PF_ALLOC_TIMEOUT_S，分配链是分钟级：逐策略读净值 + 三表追加写），且三表只增不改
# （重跑=新 run_id 追加=同日双写）→ 幂等由 trade_date 级 date-marker 跳过闸承担（见 handler）。
LIGHT_KINDS = frozenset({"c4_batch_completed", "mount_audit_monthly", "c2_screen_due",
                         "sim_memo_monthly", "sim_wallet_due", "sim_ledger_daily",
                         "sim_journal_daily", "sim_deviation_monthly", "pf_alloc_daily"})
HEAVY_KINDS = frozenset({"c4_batch_due"})
# 模拟盘日件（S09 C2）：顺序=journal 依赖账本日账先行（drain FIFO 天然串行）
SIM_DAILY_KINDS = ("sim_ledger_daily", "sim_journal_daily")
# 日件唤醒任务（task_completed task_id 子串匹配）：daily_kline 时段键/kline_daily_incremental
# 主任务/kline_index_incremental（账本直读指数行情）。DAG 并行竞态由 journal 失败重试兜底
# （行情未齐→账本 RuntimeError→留队，下个数据任务完成唤醒重试）。
SIM_DAILY_WAKE_TASKS = ("daily_kline", "kline_daily", "kline_index")
# pf_alloc 日分配件（车道 D）：kind 名 + 装配体模块（子进程 -m 调用，进程级超时边界）+ 有界运行时
# （分配链=分钟级：逐策略读净值/regime + 三表追加；超时视同失败进重试计数，不挂住调度器线程）
PF_ALLOC_KIND = "pf_alloc_daily"
PF_ALLOC_MODULE = "zephyr.pf_alloc.allocation_orchestrator"
PF_ALLOC_TIMEOUT_S = 900
# regime 日序供给件（S11 §5 施工项 4 挂点 A，挖矿节点 F3）：幂等键前缀（业务日级 marker，不建事件
# kind=零新机制，挂点 A 的本意）+ 播报稳定前缀（日志/告警面可 grep，"腐烂"与"刷新失败"必须出声）
REGIME_SNAPSHOT_KIND = "regime_snapshot_daily"
REGIME_SNAPSHOT_PREFIX = "[REGIME-SNAPSHOT]"
# ensure_regime_snapshot 返回 action 中视为成功/无异常的两态（其余=refresh_failed/error → ERROR 播报）
REGIME_SNAPSHOT_OK_ACTIONS = frozenset({"fresh", "refreshed"})
# 预埋派发（S12/S13 前置契约）：实现模块由后续批次交付，缺失=log-and-skip（不抛、出队留痕）
OPTIONAL_DUE_KINDS = {
    "fw_backtest_due": ("zephyr.strategy_pipeline.fw_backtest", "run_fw_backtest_due"),
    "promotion_advisory_due": ("zephyr.strategy_pipeline.promotion_advisory",
                               "run_promotion_advisory_due"),
}

AUDIT_MARKER = STATE_DIR / "last_audit.json"     # mount_audit/sim_memo 最近执行时间戳
MONTHLY_DAYS = 30                                 # 月度档评估线（对齐 decay_watch monthly 语义）


# ---------- KillSwitch 探针（管线专用：fail-closed） ----------
def kill_switch_clear() -> tuple[bool, str]:
    """（清除?, 原因）。探测失败=不清除（全自动管线的安全方向；与 intake 旧探针的 fail-open 相反，
    A 方案全托管后探针失败必须停——事件留 journal，恢复后重放）。"""
    try:
        from zephyr.security.access_control.kill_switch import get_kill_switch

        raw = get_kill_switch().state
        val = str(getattr(raw, "value", raw) or "").lower()
        if val in ("", "normal"):
            return True, "normal"
        return False, f"kill_switch={val}"
    except Exception as exc:  # noqa: BLE001——探针失败 fail-closed（见 docstring 裁定）
        return False, f"kill_switch_probe_error:{type(exc).__name__}"


# ---------- 告警（渠道未定=日志+Alerter 落盘先行，交接清单⑫） ----------
def alert(message: str, level: str = "WARN") -> None:
    log.warning("PIPELINE-ALERT [%s] %s", level, message)
    try:
        from zephyr.data.alerter import Alerter

        Alerter().notify("strategy_pipeline", message, level=level, source="strategy_pipeline")
    except Exception:  # noqa: BLE001——告警通道故障不反噬管线主流程
        log.debug("alerter 不可达", exc_info=True)


# ---------- journal 原语 ----------
def record(kind: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """事件先落盘（唯一真源），返回事件对象。"""
    evt = {
        "id": f"PIPE-{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}",
        "kind": kind,
        "payload": payload or {},
        "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "attempts": 0,
    }
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with JOURNAL.open("a", encoding="utf-8") as f:
        f.write(json.dumps(evt, ensure_ascii=False) + "\n")
    return evt


def pending() -> list[dict[str, Any]]:
    if not JOURNAL.exists():
        return []
    out = []
    for line in JOURNAL.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def _rewrite(events: list[dict[str, Any]]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = JOURNAL.with_suffix(".jsonl.tmp")
    tmp.write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in events), encoding="utf-8")
    tmp.replace(JOURNAL)


def _save_receipt(receipt: dict[str, Any]) -> None:
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=1), encoding="utf-8")
    except OSError:
        log.debug("receipt 落盘失败", exc_info=True)


# ---------- 消费 ----------
Handler = Callable[[dict[str, Any]], dict[str, Any]]


def _default_handler(evt: dict[str, Any]) -> dict[str, Any]:
    kind = evt["kind"]
    if kind == "c4_batch_completed":
        from zephyr.strategy_pipeline.intake import run_intake_auto

        return run_intake_auto(trigger=evt["payload"].get("batch") or evt["id"], dry_run=False)
    if kind == "mount_audit_monthly":
        out = run_mount_audit()
        _touch_marker("mount_audit")
        return out
    if kind == "sim_memo_monthly":
        out = run_sim_memo()
        _touch_marker("sim_memo")  # 病根修复（C2/X2）：marker 此前从不落盘→月度档反复重跑/或毒丸堵队
        return out
    if kind == "sim_wallet_due":
        return run_sim_wallet_due(evt["payload"])
    if kind == "sim_ledger_daily":
        out = run_sim_ledger_daily(evt["payload"])
        _touch_marker("sim_ledger_daily")  # 日件 date-marker（UTC，消费成功才落）
        return out
    if kind == "sim_journal_daily":
        out = run_sim_journal_daily(evt["payload"])
        _touch_marker("sim_journal_daily")
        return out
    if kind == "sim_deviation_monthly":
        out = run_sim_deviation_monthly(evt["payload"])
        _touch_marker("sim_deviation")
        return out
    if kind == "pf_alloc_daily":
        out = run_pf_alloc_daily(evt["payload"])
        _touch_marker("pf_alloc_daily")  # kind 级日号（唤醒侧去重）；trade_date 级双写闸在 handler 内
        return out
    if kind in OPTIONAL_DUE_KINDS:
        return run_optional_due(kind, evt)
    if kind == "c2_screen_due":
        return run_c2_screen(evt["payload"])
    if kind == "c4_batch_due":
        return run_c4_batch_due(evt["payload"])
    raise ValueError(f"未知事件 kind: {kind}")


def drain(allow_heavy: bool = False, handler: Handler | None = None,
          max_events: int = 20) -> dict[str, Any]:
    """消费 journal：成功才出队/失败保留并计 attempts（一次 drain 只试一次，重试跨唤醒）/KillSwitch 停止全保留。

    allow_heavy=False（调度器唤醒默认）跳过重 kind 不计失败；=True（CLI/C4 进程）全量消费。
    毒丸（attempts≥MAX_ATTEMPTS）事件留档不再自动消费（CLI status 可见，人工处置后删行）。
    """
    handler = handler or _default_handler
    processed: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    stop_reason = None
    for _ in range(max_events):
        ok, why = kill_switch_clear()
        if not ok:
            stop_reason = why
            break
        evts = pending()
        evt = next((e for e in evts
                    if not e.get("poison") and not (e["kind"] in HEAVY_KINDS and not allow_heavy)),
                   None)
        if evt is None:
            for e in evts:
                if e.get("poison"):
                    skipped.append({"id": e["id"], "kind": e["kind"], "why": "poison_held"})
            break
        try:
            result = handler(evt)
            processed.append({"id": evt["id"], "kind": evt["kind"], "result": result})
            _rewrite([e for e in pending() if e["id"] != evt["id"]])  # 成功才出队
        except Exception as exc:  # noqa: BLE001——失败保留+计 attempts，本轮到此为止（重试跨唤醒）
            err = f"{type(exc).__name__}: {exc}"[:200]
            evts_now = pending()
            for e in evts_now:
                if e["id"] == evt["id"]:
                    e["attempts"] = int(e.get("attempts", 0)) + 1
                    e["last_error"] = err
                    if e["attempts"] >= MAX_ATTEMPTS:
                        e["poison"] = True
                        alert(f"管线事件毒丸留档: {evt['id']} kind={evt['kind']} err={err}",
                              level="ERROR")
            _rewrite(evts_now)
            failed.append({"id": evt["id"], "kind": evt["kind"], "error": err})
            break
    receipt = {"processed": processed, "failed": failed, "skipped": skipped,
               "stop_reason": stop_reason, "pending_left": len(pending())}
    _save_receipt(receipt)
    return receipt


# ---------- 具体 kind 执行体 ----------
def run_mount_audit() -> dict[str, Any]:
    """月度挂图审计（交接清单⑪）：auto_mount.mount_audit 复用，drift 必告警。"""
    sys.path.insert(0, str(ROOT / "scripts/backtest"))
    import auto_mount  # noqa: PLC0415

    out = auto_mount.mount_audit("monthly")
    if out.get("drift"):
        alert(f"挂图审计漂移 {len(out['drift'])} 条: {out['drift'][:3]}", level="ERROR")
    if out.get("fails"):
        alert(f"挂图审计 38 规则 fails={len(out['fails'])}: {out['fails'][:3]}", level="ERROR")
    return {"audit": out.get("audit"), "mounted": out.get("mounted_count"),
            "drift_n": len(out.get("drift", [])), "fails_n": len(out.get("fails", []))}


def run_c4_batch_due(payload: dict[str, Any]) -> dict[str, Any]:
    """自动批测（交接清单⑦）：发现未批测翻译件 → c4_batch_screen --auto-only --defer-emit（子进程隔离+超时）。

    --defer-emit 对齐兄弟班 C0 双窗编排契约：IS 落账不触发 intake，c4_batch_completed
    由 OOS 步骤在双窗行齐后统一发（bothwin 依赖完整双窗行）。
    """
    import subprocess

    cmd = [sys.executable, str(ROOT / "scripts/backtest/c4_batch_screen.py"),
           "--auto-only", "--defer-emit"]
    timeout_s = int(payload.get("timeout_s", 3600))
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s, cwd=str(ROOT),
                          encoding="utf-8", errors="replace")
    ok = proc.returncode == 0
    if not ok:
        alert(f"自动批测失败 rc={proc.returncode}: {proc.stderr[-300:]}", level="ERROR")
    return {"rc": proc.returncode, "stdout_tail": proc.stdout[-500:] if ok else ""}


def run_c2_screen(payload: dict[str, Any]) -> dict[str, Any]:
    """C2 粗筛自动执行（交接清单⑧：确定性启发式、秒级、子进程隔离）。"""
    import subprocess

    timeout_s = int(payload.get("timeout_s", 900))
    proc = subprocess.run([sys.executable, str(ROOT / "scripts/backtest/strategy_screen_c2.py")],
                          capture_output=True, text=True, timeout=timeout_s, cwd=str(ROOT),
                          encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        alert(f"C2 粗筛自动执行失败 rc={proc.returncode}: {proc.stderr[-200:]}", level="ERROR")
    return {"rc": proc.returncode, "tail": (proc.stdout or "")[-300:]}


def run_sim_memo() -> dict[str, Any]:
    """sim 绩效月报+转正建议书（交接清单⑭）：生成器落盘 docs/_working/pipeline-research/sim-memos/。"""
    sys.path.insert(0, str(ROOT / "scripts/backtest"))
    import sim_promotion_memo  # noqa: PLC0415

    return sim_promotion_memo.generate()


# ---------- 模拟盘四件套执行体（S08 C1 / S09+S10 C2） ----------
def run_sim_wallet_due(payload: dict[str, Any]) -> dict[str, Any]:
    """sim 新贵逐个幂等开钱包（S08 C1）：import 复用账本 ensure_wallet（自裁：不走 subprocess——
    账本模块 import 零副作用、函数级幂等可控，与 run_mount_audit/run_sim_memo 同款 import 先例）。"""
    sys.path.insert(0, str(ROOT / "scripts/backtest"))
    import sim_paper_ledger  # noqa: PLC0415

    out: dict[str, Any] = {"opened": [], "skipped": []}
    for s in payload.get("strategies") or []:
        r = sim_paper_ledger.ensure_wallet(s["strategy_id"], code_path=s.get("code_path") or "")
        (out["opened"] if r.get("created") else out["skipped"]).append(s["strategy_id"])
    return out


def _run_sim_script(script: str, args: list[str], timeout_s: int) -> tuple[int, str]:
    """模拟盘 CLI 子进程隔离（账本 CH 维护窗重试/日刊/偏离报告均在各自 main 内，进程级隔离）。"""
    import subprocess

    proc = subprocess.run([sys.executable, str(ROOT / "scripts/backtest" / script), *args],
                          capture_output=True, text=True, timeout=timeout_s, cwd=str(ROOT),
                          encoding="utf-8", errors="replace")
    return proc.returncode, (proc.stderr or "")[-300:]


def run_sim_ledger_daily(payload: dict[str, Any]) -> dict[str, Any]:
    """账本日跑（S09 C2）：sim_daily --from-registry 全 sim 条目幂等日账（子进程=保留 CH 撞窗重试加固）。
    超时下限须覆盖账本内部有界重试（10×120s）+执行，默认 1800s。"""
    rc, err = _run_sim_script("sim_paper_ledger.py",
                              ["--mode", "sim_daily", "--from-registry"],
                              int(payload.get("timeout_s", 1800)))
    if rc != 0:
        alert(f"模拟盘账本日跑失败 rc={rc}: {err}", level="ERROR")
    return {"rc": rc}


def run_sim_journal_daily(payload: dict[str, Any]) -> dict[str, Any]:
    """平台日刊（S09 C2）：三健康检+日刊落库（账本 handler 成功后由 journal FIFO 串行触发）。"""
    rc, err = _run_sim_script("sim_platform_journal.py", [], int(payload.get("timeout_s", 600)))
    if rc != 0:
        alert(f"模拟盘平台日刊失败 rc={rc}: {err}", level="ERROR")
    return {"rc": rc}


def run_sim_deviation_monthly(payload: dict[str, Any]) -> dict[str, Any]:
    """月度偏离对照+治理建议（S10 C2）：偏离报告 --month <上一自然月>，成功后串行触发治理
    （判定史先落、建议后出，S10 §5.2③）；治理失败只告警不反噬偏离报告事件（建议下月补出）。"""
    import datetime as _dt

    today = _dt.date.today()
    prev = today.replace(day=1) - _dt.timedelta(days=1)
    month = payload.get("month") or f"{prev.year}-{prev.month:02d}"
    rc, err = _run_sim_script("sim_deviation_report.py", ["--month", month],
                              int(payload.get("timeout_s", 3600)))
    if rc != 0:
        alert(f"月度偏离报告失败 rc={rc}: {err}", level="ERROR")
        return {"rc": rc, "month": month}
    gov_rc, gov_err = _run_sim_script("sim_governance.py", [], 600)
    if gov_rc != 0:
        alert(f"模拟盘治理失败 rc={gov_rc}: {gov_err}", level="ERROR")
    return {"rc": rc, "month": month, "governance_rc": gov_rc}


def _pf_alloc_brief(stdout: str) -> str:
    """装配体 CLI 的 summary JSON → 一行可播报的人读摘要（解析失败退回首文本，绝不误判失败）。"""
    try:
        s = json.loads((stdout or "").strip() or "{}")
    except ValueError:
        return (stdout or "").strip()[-200:] or "无摘要"
    if not isinstance(s, dict):
        return str(s)[:200]
    wallets = s.get("wallet_capital") or {}
    wallet_txt = ",".join(f"{k}={v}" for k, v in wallets.items()) or "无（链停用/宇宙为空）"
    rg = s.get("regime") or {}
    regime_txt = f"{rg.get('dominant')}@{rg.get('source_date')}(滞后{rg.get('lag_days')}日)"
    return (f"run={s.get('run_id')} 总盘={s.get('portfolio_total_capital')} "
            f"Σbudget={s.get('sum_effective_budget')} shrinkage={s.get('global_shrinkage')} "
            f"未分配现金={s.get('unallocated_cash')} 钱包[{wallet_txt}] "
            f"落地={s.get('persisted')} 告警={len(s.get('warnings') or [])}条 regime={regime_txt}")


def run_pf_alloc_daily(payload: dict[str, Any]) -> dict[str, Any]:
    """pf_alloc 日分配（车道 D 实盘接线，MOD-PA-030 装配体的事件执行体）：一事件=一分配周期。

    触发面=事件（宪法 §9.3）：本件不建 cron/Timer/sleep 循环，节拍由调度器唤醒链上的
    pf_alloc_daily 事件给；执行体=subprocess 隔离 `python -m zephyr.pf_alloc.allocation_orchestrator
    --date <D>`（与 run_c2_screen/run_sim_ledger_daily 同款"重活不进主进程"，超时即硬边界）。
    该 CLI 与事件正门 handle_pf_alloc_daily_event 调的是同一个 run_daily_allocation。

    Args:
        payload: 必带 ``trade_date``（或 ``biz_date``）——缺失即抛错，**不按墙钟猜业务日**
          （分配链 handle_pf_alloc_daily_event 同口径，发射方负责给日）；
          可选 ``strategy_ids``（限定策略，透传 --strategy-id）/``timeout_s``（默认 PF_ALLOC_TIMEOUT_S）。

    幂等：alloc 三表 MergeTree 只增不改（重跑=新 run_id 追加），故以 trade_date 级 date-marker
      做当日跳过闸——同一业务日已成功落地则零副作用返回（不双写快照、不重复落库）。
    失败：超时 / rc≠0 → 告警 + 抛错，交 drain 的 attempts 计数（MAX_ATTEMPTS=3 后毒丸留档）。

    Returns:
        {"rc": 0, "trade_date": D, "alloc_brief": 一行摘要, "summary_tail": str}
        或 {"skipped": ..., "trade_date": D}
    """
    import subprocess

    day = str(payload.get("trade_date") or payload.get("biz_date") or "").strip()
    if not day:
        raise RuntimeError(
            "pf_alloc_daily 事件 payload 缺 trade_date——分配链禁按墙钟猜交易日"
            "（zephyr.pf_alloc.allocation_orchestrator.handle_pf_alloc_daily_event 同口径），"
            "发射方须带业务日")
    marker = f"{PF_ALLOC_KIND}:{day}"
    if _date_marker_done(marker):
        log.info("pf_alloc_daily %s 当日已落地，跳过（防同日双写分配快照）", day)
        return {"skipped": "already_persisted", "trade_date": day}
    cmd = [sys.executable, "-m", PF_ALLOC_MODULE, "--date", day]
    for sid in payload.get("strategy_ids") or []:
        cmd += ["--strategy-id", str(sid)]
    timeout_s = int(payload.get("timeout_s", PF_ALLOC_TIMEOUT_S))
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s,
                              cwd=str(ROOT), encoding="utf-8", errors="replace")
    except subprocess.TimeoutExpired as exc:
        alert(f"pf_alloc 日分配超时（>{timeout_s}s）trade_date={day}", level="ERROR")
        raise RuntimeError(f"pf_alloc_daily 超时 {timeout_s}s trade_date={day}") from exc
    if proc.returncode != 0:
        err = (f"pf_alloc 日分配失败 rc={proc.returncode} trade_date={day}: "
               f"{(proc.stderr or '')[-300:]}")
        alert(err, level="ERROR")
        raise RuntimeError(err)
    _touch_marker(marker)  # 成功才落号（失败不落→同唤醒点重试仍可执行）
    brief = _pf_alloc_brief(proc.stdout)
    # 出声：分配结果不能只停在子进程 stdout——一行摘要进告警面（Alerter→日志）+ drain 回执，
    # 落库投递事实（ch_committed/local_durable）在摘要里，"算了没落地"当场可见。
    alert(f"pf_alloc 日分配已落地 trade_date={day}: {brief}", level="INFO")
    return {"rc": 0, "trade_date": day, "alloc_brief": brief,
            "summary_tail": (proc.stdout or "")[-300:]}


def run_optional_due(kind: str, evt: dict[str, Any]) -> dict[str, Any]:
    """预埋派发（S12/S13 前置契约）：模块/函数由后续批次交付，缺失=log-and-skip（不抛、出队留痕）。

    契约=模块路径+函数签名 def run_xxx_due(event: dict) -> dict（见 OPTIONAL_DUE_KINDS）。
    """
    module_path, func_name = OPTIONAL_DUE_KINDS[kind]
    try:
        import importlib

        fn = getattr(importlib.import_module(module_path), func_name)
    except Exception as exc:  # noqa: BLE001——实现未交付是预期态，跳过不是失败（不占 attempts）
        log.info("可选事件执行体未交付，跳过: kind=%s module=%s (%s)", kind, module_path,
                 type(exc).__name__)
        return {"skipped": "module_not_ready", "module": module_path,
               "event_id": evt.get("id")}
    return fn(evt)


def _touch_marker(name: str) -> None:
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        data = json.loads(AUDIT_MARKER.read_text(encoding="utf-8")) if AUDIT_MARKER.exists() else {}
        data[name] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())  # UTC（与 _marker_due 同口径）
        AUDIT_MARKER.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    except OSError:
        log.debug("audit marker 写入失败", exc_info=True)


def _marker_due(name: str) -> bool:
    try:
        if not AUDIT_MARKER.exists():
            return True
        data = json.loads(AUDIT_MARKER.read_text(encoding="utf-8"))
        last = data.get(name)
        if not last:
            return True
        import datetime as _dt

        last_dt = _dt.datetime.strptime(last, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=_dt.UTC)
        return (_dt.datetime.now(_dt.UTC) - last_dt).days >= MONTHLY_DAYS
    except Exception:  # noqa: BLE001——标记损坏按到期处理（宁可多审一次）
        return True


def maybe_emit_monthly() -> dict[str, Any]:
    """月度档到期评估（交接清单⑪⑭+S10 C2）：挂在事件唤醒点上评估，非自走时钟（禁 cron 语义的合规实现）。

    到期即入队（幂等：同月已入队/已处理则跳过——marker 30 天线为主闸，pending 同月去重为辅闸），
    消费由 drain 完成。毒丸事件不算"已入队"（否则毒丸永久堵死该月度档——sim_memo_monthly
    从未正常轮转的病根之一，C2/X2 修复）。
    """
    emitted = []
    for name, kind in (("mount_audit", "mount_audit_monthly"), ("sim_memo", "sim_memo_monthly"),
                       ("sim_deviation", "sim_deviation_monthly")):
        if not _marker_due(name):
            continue
        if any(e["kind"] == kind and not e.get("poison")
               and e["recorded_at"][:7] == time.strftime("%Y-%m")  # recorded_at=本地时
               for e in pending()):
            continue
        record(kind, {"due_marker": name})
        emitted.append(kind)
    if emitted:
        alert(f"月度档到期已入队: {emitted}")
    return {"emitted": emitted}


def _date_marker_done(name: str) -> bool:
    """日件当日记号（UTC 日期口径，与 _touch_marker 的 UTC 时间戳一致）：当日已成功消费=真。"""
    try:
        if not AUDIT_MARKER.exists():
            return False
        data = json.loads(AUDIT_MARKER.read_text(encoding="utf-8"))
        return str(data.get(name) or "")[:10] == time.strftime("%Y-%m-%d", time.gmtime())
    except Exception:  # noqa: BLE001——标记损坏按未做处理（宁可重跑一次，日件本身幂等）
        return False


def _marker_seen(name: str) -> bool:
    """记号**曾**落过盘（不看 UTC 日期，永久闸）：幂等键本身是业务日时用它而非 _date_marker_done。

    分配链幂等键=trade_date（alloc 三表只增不改）。用 UTC 日口径会漏：行情停更/周末唤醒时
    业务日仍是旧的 D，而记号日期已翻篇 → 同一 D 再发一件 → 只增表里多一份重复快照。
    """
    try:
        if not AUDIT_MARKER.exists():
            return False
        return bool(json.loads(AUDIT_MARKER.read_text(encoding="utf-8")).get(name))
    except Exception:  # noqa: BLE001 — 标记损坏按未做过处理（宁可重发，分配链同日双写另有闸）
        return False


def maybe_emit_sim_daily(task_id: Any = None, success: bool = True, **_kwargs) -> dict[str, Any]:
    """模拟盘日件到期评估（S09 C2）：daily_kline 数据任务当日 SUCCESS=自然唤醒（非自走时钟）。

    幂等双闸：当日 date-marker 已成功（handler 消费成功后落）或同 kind 非 poison 事件在队
    则跳过；ledger 先于 journal 入队（FIFO 串行=日刊体检必见当日钱包行），账本失败时 drain
    中断、日刊事件留队跨唤醒重试，顺序不倒置。
    """
    tid = str(task_id or "")
    if not success or not any(k in tid for k in SIM_DAILY_WAKE_TASKS):
        return {"emitted": []}
    emitted = []
    for kind in SIM_DAILY_KINDS:
        if _date_marker_done(kind) or any(e["kind"] == kind and not e.get("poison")
                                          for e in pending()):
            continue
        record(kind, {"due": "daily_kline", "task_id": str(task_id)})
        emitted.append(kind)
    if emitted:
        alert(f"模拟盘日件已入队: {emitted}")
    return {"emitted": emitted}


# ---- 日频产出者（清单 #15 分配链 / 挖矿 F3 regime 日序：kind 有消费端无产出者=静默纸面链）────
# 业务日真源=行情最新入库日（daily_kline/kline_index 任务 SUCCESS 即该日已入库）。
# 查询口径与 scripts/backtest/sim_platform_journal.py 健检 1 同源（同表同 symbol），此处只解析
# 不猜：解析不出=不发事件（分配链正门 handle_pf_alloc_daily_event 对缺 trade_date 抛错，
# 墙钟猜日会在非交易日/数据晚到日写出错误的分配快照，且 alloc 三表只增不改无法回收）。
PF_ALLOC_BIZ_DATE_SQL = ("SELECT max(trade_date) FROM c1_market.kline_index "
                         "WHERE symbol = '000300'")
# CH 对空 Date 列的 min/max 返回 1970-01-01 哨兵（实证见 market_daban_engine_load.py 注记）
_EMPTY_TABLE_SENTINEL = "1971-01-01"


def resolve_pf_alloc_trade_date() -> str:
    """分配链业务日（数据驱动，非墙钟）：行情最新入库交易日 -> 'YYYY-MM-DD'。

    本模块日频产出者共用的业务日真源（名字里的 pf_alloc 是历史遗留）：regime 日序刷新
    （maybe_refresh_regime_snapshot）也走这一条只读模板 + DatabaseService reader 角色，
    不在别处再拼第二条 SQL。

    Raises:
        RuntimeError: CH 不可达 / 无行 / 空表哨兵 / 日期非法——宁可不发事件也不猜日。
    """
    from zephyr.infrastructure.database_service import get_db_service

    conn = get_db_service().get_clickhouse_conn(role="reader")
    rows = list(conn.execute(PF_ALLOC_BIZ_DATE_SQL) or [])
    raw = rows[0][0] if rows and rows[0] else None
    day = str(raw or "")[:10]
    if not day or day < _EMPTY_TABLE_SENTINEL:
        raise RuntimeError(f"行情无可用业务日（kline_index max(trade_date)={raw!r}）")
    return day


def maybe_emit_pf_alloc_daily(task_id: Any = None, success: bool = True,
                              **_kwargs) -> dict[str, Any]:
    """pf_alloc 日分配的唯一自动产出者：行情日件 SUCCESS=自然唤醒，一个唤醒=一个分配周期。

    宪法 §9.3 合规：本件不建 cron/Timer/sleep 循环，节拍由调度器 task_completed 唤醒给。
    入队顺序即落地顺序（journal FIFO）——本件在 maybe_emit_sim_daily **之前**被调用，
    故 pf_alloc_daily 先于 sim_ledger_daily 消费，账本同日 ensure_wallet 才读得到真实额度
    （否则 alloc_budget_daily 恒空、账本恒回退 flat 100 万=PFA-2 原状）。
    幂等双闸：该业务日**曾**已成功（trade_date 级记号，永久）∨ 同业务日非 poison 事件在队
    → 零副作用跳过。用永久记号而非"当日"记号：幂等键是业务日，行情停更/周末唤醒时业务日
    还是旧的 D，按 UTC 日口径会再发一件 → 只增不改的 alloc 表里多出一份重复快照。
    人工重跑不受本闸约束：`pipeline_events emit pf_alloc_daily --payload '{"trade_date":D}'`
    或直接 `python -m zephyr.pf_alloc.allocation_orchestrator --date D`（重跑=新 run_id 追加）。
    """
    tid = str(task_id or "")
    if not success or not any(k in tid for k in SIM_DAILY_WAKE_TASKS):
        return {"emitted": []}
    try:
        day = resolve_pf_alloc_trade_date()
    except Exception as exc:  # noqa: BLE001 — 业务日不可得=不发事件，但必须出声（静默=链又变纸面）
        msg = f"pf_alloc 日分配未入队（业务日不可解析，禁墙钟猜日）: {type(exc).__name__}: {exc}"
        alert(msg[:300], level="WARN")
        return {"emitted": [], "error": msg[:200]}
    if _marker_seen(f"{PF_ALLOC_KIND}:{day}") or any(
            e["kind"] == PF_ALLOC_KIND and not e.get("poison")
            and str((e.get("payload") or {}).get("trade_date") or "") == day
            for e in pending()):
        return {"emitted": [], "skipped": "already_queued_or_done", "trade_date": day}
    record(PF_ALLOC_KIND, {"trade_date": day, "due": "sim_daily_wake", "task_id": tid})
    alert(f"pf_alloc 日分配已入队 trade_date={day}（先于账本消费=同日钱包拿真实额度）",
          level="INFO")
    return {"emitted": [PF_ALLOC_KIND], "trade_date": day}


# ---------- regime 日序供给产出者（挖矿 F3 治本：表有唯一消费端与 manual 写方，无自动写方）──
def maybe_refresh_regime_snapshot(task_id: Any = None, success: bool = True,
                                 **_kwargs) -> dict[str, Any]:
    """regime_snapshot_history 的唯一自动产出者：行情日件 SUCCESS=自然唤醒，一业务日至多一印。

    宪法 §9.3 合规（S11 §5 施工项 4「挂点 A」，零新机制）：本件不建 cron/Timer/sleep 循环，
    节拍由调度器 task_completed 唤醒给。此前该表唯一写方=manual CLI
    scripts/backtest/print_regime_history.py（START=2019-01-01 全窗重印，每次手工跑一批新
    run_id），两次手工印制之间无人补日 → 表静默腐烂（2026-09-16 实测 1809 行、
    max=2026-09-11、滞后 5 天且逐日变大），而 fw_backtest/auto_mount/pf_alloc 三方都读它。

    幂等闸=业务日级永久记号（_marker_seen，与 pf_alloc_daily 同款，不用 UTC 日口径）：
      键 regime_snapshot_daily:<D>，D=行情最新入库日（resolve_pf_alloc_trade_date，禁墙钟猜日；
      解析不出=不印 + ERROR 出声，且因日未定→记号不落，下个唤醒点自会重解析）。写方是全窗
      重印 append-only 台账，同一 D 二次自动印制=整窗行数再翻一份而信息增益为零；行情停更/
      周末唤醒时 UTC 日翻篇而 D 不变，按日口径必漏。
      **记号先落再动手**（与 pf_alloc handler 的"成功才落号"相反，自裁留痕）：pf_alloc 有
      journal attempts/毒丸兜底且由事件驱动（一次入队一次执行），本件是唤醒钩子内直调——失败
      若不留号=每个行情唤醒点重起一次分钟级 walk-forward 全窗重印（风暴）。失败已 ERROR 出声，
      当日人工补跑走逃生口（见下）。
      真正的重印闸门在 ensure_regime_snapshot 内：滞后 ≤_REGIME_STALE_DAYS(3) 天零成本直通
      （只花一条只读新鲜度查询），只有超限才起子进程 → 常态下本钩子是廉价的看门狗。

    永不抛：快照刷新失败绝不得反噬唤醒钩子链（记 [REGIME-SNAPSHOT] ERROR + 返回值）。
    人工逃生口（不受本闸约束）：`python scripts/backtest/print_regime_history.py [--start/--end]`。

    Returns:
        {"action": "fresh|refreshed|refresh_failed|already_refreshed|skipped_wake_point|error",
         "trade_date": D（唤醒点不匹配时缺）, 成功态另带 "brief": 一行摘要}
    """
    tid = str(task_id or "")
    if not success or not any(k in tid for k in SIM_DAILY_WAKE_TASKS):
        return {"action": "skipped_wake_point"}
    day = ""
    try:
        day = resolve_pf_alloc_trade_date()  # 共用业务日真源（DatabaseService reader，§9.1）
        key = f"{REGIME_SNAPSHOT_KIND}:{day}"
        if _marker_seen(key):
            return {"action": "already_refreshed", "trade_date": day}
        _touch_marker(key)  # 先落号再动手（防失败重印风暴，见 docstring 裁定）
        from zephyr.strategy_pipeline.fw_backtest import ensure_regime_snapshot  # noqa: PLC0415

        out = ensure_regime_snapshot(refresh=True)
    except Exception as exc:  # noqa: BLE001——钩子永不反噬调度器，但失败必须出声（静默=链又变纸面）
        msg = (f"{REGIME_SNAPSHOT_PREFIX} 刷新未完成（trade_date={day or '未知'}）："
               f"{type(exc).__name__}: {exc}")
        log.error(f"{REGIME_SNAPSHOT_PREFIX} 刷新异常（不影响唤醒链，人工补跑 "
                  f"scripts/backtest/print_regime_history.py）trade_date={day or '未知'}",
                  exc_info=True)
        alert(msg[:300], level="ERROR")
        return {"action": "error", "trade_date": day, "error": f"{type(exc).__name__}"[:200]}
    action = str(out.get("action") or "")
    # 出声：滞后天数/行数/动作一行进告警面（Alerter→日志）——"印了没印、还滞后几天"当场可见
    brief = (f"action={action} max_trade_date={out.get('max_trade_date')} "
             f"滞后={out.get('stale_days')}日 行数={out.get('rows')}")
    level = "INFO" if action in REGIME_SNAPSHOT_OK_ACTIONS else "ERROR"
    alert(f"{REGIME_SNAPSHOT_PREFIX} 刷新体检 trade_date={day}: {brief}", level=level)
    return {"action": action, "trade_date": day, "brief": brief}


# ---------- 写侧钩子 ----------
def emit_c4_batch_completed(batch: str, run_id: str, inserted: int) -> dict[str, Any]:
    """C4 批测落账成功后的通知钩子（c4_batch_screen 调用）：记录事件并尝试立即消费。"""
    evt = record("c4_batch_completed", {"batch": batch, "run_id": run_id, "inserted": inserted})
    try:
        receipt = drain(allow_heavy=False)
    except Exception as exc:  # noqa: BLE001——消费失败不反噬批测进程，事件留 journal
        alert(f"c4_batch_completed 事件消费失败（已留 journal 待重放）: {evt['id']} {exc}", level="WARN")
        return {"event": evt["id"], "drained": False, "error": str(exc)[:200]}
    return {"event": evt["id"], "drained": True, "receipt": receipt}


def emit_sim_wallet_due(strategies: list[dict[str, Any]]) -> dict[str, Any]:
    """sim 流转入册后的开户通知钩子（intake 调用，c4 同款 record+立即轻消费）。

    payload=新 sim 条目 [{"strategy_id", "code_path"}]；失败留 journal 重放（开户幂等）。
    """
    evt = record("sim_wallet_due", {"strategies": strategies})
    try:
        receipt = drain(allow_heavy=False)
    except Exception as exc:  # noqa: BLE001——消费失败不反噬入库主流程，事件留 journal
        alert(f"sim_wallet_due 事件消费失败（已留 journal 待重放）: {evt['id']} {exc}", level="WARN")
        return {"event": evt["id"], "drained": False, "error": str(exc)[:200]}
    return {"event": evt["id"], "drained": True, "receipt": receipt}


# ---------- 调度器侧注册（交接清单①："新事件处理器注册在调度器侧"） ----------
def wire_data_scheduler(scheduler: Any) -> None:
    """DataScheduler.subscribe("task_completed", ...) 轻钩子：数据任务完成=自然唤醒点。

    职责边界：只做 ①轻 kind drain（intake 重放/审计）②翻译件积压扫描→记录 c4_batch_due+告警
    ③日频产出者唤醒（regime 日序供给 → pf_alloc 分配链 → 模拟盘日件 → 月度档；顺序即下游
    读到新鲜数据的顺序：先刷新 regime_snapshot_history 再入队分配件，分配链读本表口径；
    分配再先于账本入队是"钱包额度来自分配链"这一接通的唯一次序保证）。
    永不抛异常（数据任务完成回调故障不得反噬调度器）；重 kind 不在此消费（见模块裁定）。
    """
    def _on_task_completed(**_kwargs) -> None:
        try:
            scan_translated_backlog()
            scan_c1_c2_backlog()
            # 挖矿 F3：regime 日序台账日产出者——须先于分配链（pf_alloc 的 regime 口径读本表，
            # 表旧=分配快照带旧教材）；滞后 ≤3 天时只是一条只读查询，不起子进程
            maybe_refresh_regime_snapshot(**_kwargs)
            # 车道 D #15：分配链日产出者——必须先于日件入队（journal FIFO=分配先落，
            # 同日账本 ensure_wallet 才读得到 alloc_budget_daily 的真实钱包额度）
            maybe_emit_pf_alloc_daily(**_kwargs)
            maybe_emit_sim_daily(**_kwargs)  # S09 C2：daily_kline SUCCESS=模拟盘日件自然唤醒
            maybe_emit_monthly()
            drain(allow_heavy=False)
        except Exception:  # noqa: BLE001——钩子永不反噬调度器
            log.debug("pipeline 唤醒钩子异常", exc_info=True)

    scheduler.subscribe("task_completed", _on_task_completed)


def scan_translated_backlog() -> dict[str, Any]:
    """⑦ 上半场：发现未批测翻译件（translated/c4_*.py 中不在 IS 批台账的）→ 记录事件+告警。

    只发现不执行（重 kind 留显式 drain）；幂等：同集合已记录则不重复入队。
    """
    translated = ROOT / "scripts/backtest/translated"
    files = {p.name for p in translated.glob("c4_*.py")}
    from zephyr.data.ch_writer import get_client_strict

    rows = get_client_strict().execute(
        f"SELECT DISTINCT source_file FROM c1_backtest.strategy_screen "
        f"WHERE screen_batch = 'C4-translated-20260912' AND verdict = 'translated_c4'")
    known = {str(r[0]).rsplit("/", 1)[-1] for r in rows}
    backlog = sorted(files - known - {"__init__.py"})
    if not backlog:
        return {"backlog": []}
    recorded = {tuple(e["payload"].get("files") or ()) for e in pending()
                if e["kind"] == "c4_batch_due"}
    if tuple(backlog) in recorded:
        return {"backlog": backlog, "already_recorded": True}
    record("c4_batch_due", {"files": backlog, "n": len(backlog)})
    alert(f"发现 {len(backlog)} 个未批测翻译件（已登记 c4_batch_due，等显式 drain）: {backlog[:5]}")
    return {"backlog": backlog}


def scan_c1_c2_backlog() -> dict[str, Any]:
    """⑧⑨ 上游供料扫描（事件唤醒点评估，非自走时钟）：

    - C2 粗筛积压：raw_manifest.csv 比 screen_c2.csv 新（或后者缺失）→ c2_screen_due（轻，自动执行）；
    - C1 矿脉到期：lane_b_candidates.csv 存在且比最近一次登记新 → 仅告警提示有新海选材料
      （生成器为 LLM 会话入口，全自动生成=方案真源 §1 噪音过滤裁定，执行留当班会话）。
    幂等：同类事件未消费且 mtime 未变则不重复入队。
    """
    intake_dir = ROOT / "data/strategy_intake"
    manifest = intake_dir / "raw_manifest.csv"
    screen_c2 = intake_dir / "screen_c2.csv"
    lane_b = intake_dir / "lane_b_candidates.csv"
    out: dict[str, Any] = {}
    if manifest.exists() and (not screen_c2.exists()
                              or screen_c2.stat().st_mtime < manifest.stat().st_mtime):
        sig = int(manifest.stat().st_mtime)
        if not any(e["kind"] == "c2_screen_due" and e["payload"].get("sig") == sig
                   for e in pending()):
            record("c2_screen_due", {"sig": sig, "manifest_mtime": sig})
            out["c2_due"] = True
    if lane_b.exists():
        sig = int(lane_b.stat().st_mtime)
        done_marker = STATE_DIR / "c1_seen_laneb.txt"
        seen = done_marker.read_text(encoding="utf-8").strip() if done_marker.exists() else ""
        if str(sig) != seen:
            alert("lane_b 候选台账有更新（C1 矿脉材料就绪，LLM 生成入口留当班会话执行）")
            try:
                STATE_DIR.mkdir(parents=True, exist_ok=True)
                done_marker.write_text(str(sig), encoding="utf-8")
            except OSError:
                pass
            out["c1_material"] = True
    return out


# ---------- CLI ----------
def main(argv: list[str] | None = None) -> int:  # pragma: no cover — CLI 薄壳，逻辑全在函数
    import argparse

    ap = argparse.ArgumentParser(description="strategy_pipeline 事件 CLI（emit/drain/status）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status", help="查看积压事件与最近回执")
    d = sub.add_parser("drain", help="消费事件")
    d.add_argument("--all", action="store_true", help="含重 kind（c4_batch_due 自动批测）")
    e = sub.add_parser("emit", help="手工入队事件")
    e.add_argument("kind", choices=["c4_batch_completed", "c4_batch_due", "mount_audit_monthly",
                                    "c2_screen_due", "sim_memo_monthly", "sim_wallet_due",
                                    "sim_ledger_daily", "sim_journal_daily",
                                    "sim_deviation_monthly", "fw_backtest_due",
                                    "promotion_advisory_due", "pf_alloc_daily"])
    e.add_argument("--payload", default="{}", help="JSON payload")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    if args.cmd == "status":
        evts = pending()
        print(json.dumps({"pending": len(evts),
                          "events": [{"id": x["id"], "kind": x["kind"], "attempts": x["attempts"]}
                                     for x in evts],
                          "last_receipt": json.loads(RECEIPT.read_text(encoding="utf-8"))
                          if RECEIPT.exists() else None}, ensure_ascii=False, indent=1))
        return 0
    if args.cmd == "drain":
        print(json.dumps(drain(allow_heavy=args.all), ensure_ascii=False, indent=1, default=str))
        return 0
    evt = record(args.kind, json.loads(args.payload))
    print(json.dumps({"recorded": evt["id"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
