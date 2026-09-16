# [BLUEPRINT] MOD-BT-199 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.strategy_pipeline.promotion_advisory
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.strategy_pipeline.lifecycle_fsm（sim→production Owner 门流转）;
#   zephyr.shared.io.file_utils(safe_write_text CAS); zephyr.shared.security.secrets(owner token);
#   zephyr.shared.utils.time_utils(now_utc); zephyr.data.alerter(真通道，降级不抛);
#   run 档案目录只读扫描（data/backtest_artifacts/runs，不经 run_archive API 写路径）;
#   zephyr.strategy_pipeline.screen_source(fetch_bothwin §8 双窗真源，PA-1 起惰性 import);
#   docs/_working/pipeline-research/reports/intake-*.yaml(BH-FDR 批报告，只读);
#   data/runtime/strategy_decay_ledger.json(MOD-SIG-150 衰减台账，只读回)
# [CONSUMERS] zephyr.strategy_pipeline.pipeline_events（OPTIONAL_DUE_KINDS promotion_advisory_due
#   lazy 派发）; scripts/backtest/sim_governance（治理建议产出后 emit）;
#   api_server POST /api/promotion-decide（S13/Y2 拍板端点调 decide）
# [STARTUP] imported+event（promotion_advisory_due 经 pipeline_events drain 消费）
# [MATURITY] experimental
# [INVARIANTS] 建议包只产不改册（decide 是唯一写路径：FSM sim→production/shelved + 注册表 CAS）；
#   owner token 明文绝不落盘/进日志（台账只存 sha256 前 12 位指纹，MOD-EX-035 同款）；
#   未配置 ZEPHYR_OWNER_APPROVAL_TOKEN=Owner 门 fail-closed（拒绝，不降级放行）；
#   candidate→sim 预授权三条件逐项回落实据（PA-1 治本 2026-09-17，禁硬编码 True）：
#   dual_window_pass=strategy_screen §8 双窗及格行在位 / bh_fdr_pass=intake 批报告 fdr_keep
#   在册 / no_pending_decay_alert=MOD-SIG-150 衰减台账无 failed/retired 未决建议；
#   **缺证据=不通过**（判不了不许放行），不通过即拒绝 approve 且不写 decision 墓碑（可重试）；
#   每条件带 {ok, reason, source} 三件套，落 decision 台账可追溯；
#   demote（→shelved）走低于 sim 的无守卫合法边 candidate→shelved，**不受晋升预授权阻断**
#   （降档是风险收敛动作，被证据缺位卡住=反向 fail-open）；
#   已决 advisory 重复 decide=拒绝（幂等，台账即墓碑）；
#   建议包幂等（同日同策略覆盖同文件，不堆叠）；无建议策略不产包（S12 §5.1 验收）；
#   三路证据源任一缺失=该路降级（0/null），不抛不阻断其余策略；
#   alerter 推送/回执任何故障不反噬建议产出与拍板执行
# [MODIFY-GUARD] tests/strategy_pipeline/test_promotion_advisory.py
# [STABILITY] experimental
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FileNotFoundError(advisory_id 不存在)；ValueError(decision 非法)；
#   其余失败返回 {"ok": false, "reason": ...}（token 校验失败/未配置/已决/lifecycle 不可流转/
#   sim_preauthorization_not_established（PA-1 预授权实据不齐，附 conditions 明细）均不抛）
# [TESTS] tests/strategy_pipeline/test_promotion_advisory.py
# [A_module] module_id=MOD-BT-199 | layer=module | stability=experimental | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 永久事件触发件——真触发链=pipeline_events
#   OPTIONAL_DUE_KINDS promotion_advisory_due lazy 派发（scripts/backtest/sim_governance 治理建议
#   产出后 emit），本文件 argparse main() 仅为 CLI 自检入口，非常驻触发方式
"""转正建议包生成+真通道推送+Owner 拍板执行器（S12 C4 本体）。

三路证据合流（S12 §5.1，全部只读扫描，任一缺失降级不抛）：
  ① sim_governance 的 SCR-SIMGOV run 档案（04_wide/sim_governance_advice.json，取最新 run）；
  ② SIM-DEV 月度偏离档案（SCR-DEV-*/04_wide/deviation_report.json，按 (sid,month) 去重累计）；
  ③ 整装回测证据包 data/backtest_artifacts/fw-auto/latest.json（X3 产物，组合级证据）；
  ④ sim_memo 月度档（sim-memo-<YYYYMM>.json，证据指针 memo_ref）。

建议词表映射：governance promote_paper→promote；demote_decayed→demote；缺治理建议时按
月度判定史兜底（pass≥2∧breach=0→promote；breach≥2→demote；其余 hold，hold 不产包）。

拍板语义（与 Y2 前端契约）：decide(advisory_id, "approve"|"reject", token=None, via="api")——
token=None 时服务端自取配置密钥（前端拍板=Owner 点击即授权）；token 显式给出时 sha256 常量
时间比对校验。approve→FSM sim→production（demote→shelved 留档）→注册表 lifecycle CAS 更新
→decision 台账（token 指纹留痕）→alerter 回执。

预授权实据（PA-1 治本，2026-09-17）：FSM 每台以 candidate 起步，promote 要落到 production 必须先
合法走过 candidate→sim 那一跳，而该跳的三条件（SimPromotionGuard）此前被本件硬编码为真——机器
给自己签发晋升令。现逐条回落到只读实据（evaluate_sim_preauthorization）：
    dual_window_pass        ← strategy_screen §8 双窗及格行（screen_source.fetch_bothwin）
    bh_fdr_pass             ← intake 批报告 fdr_keep（BH-FDR q≤0.10 批内通过名单）
    no_pending_decay_alert  ← MOD-SIG-150 衰减台账（failed/retired=未决建议，挡晋升）
缺证据=不通过（Fail-Closed），整条 approve 拒绝且**不写 decision 墓碑**（补齐证据后可重试）。
demote 目标态低于 sim，走 candidate→shelved 无守卫合法边，不被晋升预授权反向阻断。

CLI 自检：python -m zephyr.strategy_pipeline.promotion_advisory [build|list|preauth <STR-ID>]
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import re
from pathlib import Path
from typing import Any

from zephyr.shared.io.file_utils import safe_write_text
from zephyr.shared.security.secrets import get_secret_or_default
from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[3]
RUNS_DIR = ROOT / "data/backtest_artifacts/runs"
FW_DIR = ROOT / "data/backtest_artifacts/fw-auto"
MEMO_DIR = ROOT / "docs/_working/pipeline-research/sim-memos"
ADVISORY_DIR = ROOT / "data/strategy_intake/promotion_advisories"
REGISTRY = ROOT / "docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml"

OWNER_TOKEN_KEY = "ZEPHYR_OWNER_APPROVAL_TOKEN"
#: PA-1 证据源②：C6 auto_intake 批报告目录（fdr_keep=BH-FDR q≤0.10 批内通过名单）
INTAKE_REPORT_DIR = ROOT / "docs/_working/pipeline-research/reports"
#: PA-1 证据源③：MOD-SIG-150 衰减台账（strategy_decay_certifier 落盘）
DECAY_LEDGER = ROOT / "data/runtime/strategy_decay_ledger.json"
#: 衰减台账里"未决建议"态——挂在这上面的策略不许晋升
_DECAY_PENDING_STATES = ("failed", "retired")
#: SimPromotionContext 三条件名（顺序=证据链顺序，decision 台账按此留痕）
_PREAUTH_KEYS = ("dual_window_pass", "bh_fdr_pass", "no_pending_decay_alert")
_GOV_REC_MAP = {"promote_paper": "promote", "demote_decayed": "demote"}
# FSM 流转目标（approve 语义；hold 只记账不流转）
_DECISION_TARGET = {"promote": "production", "demote": "shelved", "hold": None}
# 建议包只认的注册表生命周期（sim 观察态；paper=注册表八态同位观察态，词表统一前的兼容口径）
_OBSERVING_LIFECYCLES = ("sim", "paper")


def _fingerprint(token: str) -> str:
    """token sha256 指纹（前 12 位，MOD-EX-035 SwitchRecord 同款；明文绝不落盘）。"""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()[:12]


# ---------- 证据源读取（只读，缺失降级） ----------
def _read_latest_governance() -> dict[str, dict[str, Any]]:
    """① 最新一次 SCR-SIMGOV run 的建议表 {strategy_id: rec}。"""
    runs = sorted(RUNS_DIR.glob("SCR-SIMGOV-*/04_wide/sim_governance_advice.json"))
    if not runs:
        return {}
    try:
        data = json.loads(runs[-1].read_text(encoding="utf-8"))
        return {r["strategy_id"]: r for r in data.get("recommendations", []) if r.get("strategy_id")}
    except (OSError, ValueError, KeyError, TypeError):
        logger.warning("SCR-SIMGOV run 档案解析失败（证据①降级）: %s", runs[-1].name, exc_info=True)
        return {}


def _read_deviation_months() -> dict[str, dict[str, Any]]:
    """② SIM-DEV 月度偏离档案累计：{sid: {months, pass, breach}}，(sid,month) 去重取最新 run。"""
    by_key: dict[tuple[str, str], dict[str, Any]] = {}
    for path in sorted(RUNS_DIR.glob("SCR-DEV-*/04_wide/deviation_report.json")):
        try:
            rows = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            logger.warning("SCR-DEV 偏离档案解析失败（跳过）: %s", path.parent.parent.name, exc_info=True)
            continue
        for r in rows if isinstance(rows, list) else []:
            sid, month = r.get("strategy_id"), r.get("month")
            if sid and month:
                by_key[(sid, str(month))] = r
    out: dict[str, dict[str, Any]] = {}
    for (sid, month), r in by_key.items():
        agg = out.setdefault(sid, {"months": [], "pass": 0, "breach": 0})
        agg["months"].append(month)
        agg["pass" if r.get("ok") else "breach"] += 1
    for agg in out.values():
        agg["months"].sort()
    return out


def _read_fw_evidence() -> dict[str, Any] | None:
    """③ 整装回测证据（组合级，latest.json 优先，退最新 fw-auto-*.json）。"""
    path = FW_DIR / "latest.json"
    if not path.is_file():
        candidates = sorted(FW_DIR.glob("fw-auto-*.json"))
        if not candidates:
            return None
        path = candidates[-1]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        run = data.get("run") or {}
        metrics = run.get("core_metrics") or {}
        panel = run.get("panel_reconciliation") or {}
        return {
            "run_id": run.get("run_id"),
            "sharpe": metrics.get("sharpe_ratio"),
            "max_dd": metrics.get("max_drawdown"),
            "total_return": metrics.get("total_return"),
            "panel_ok": bool(panel.get("within_tolerance")),
        }
    except (OSError, ValueError, AttributeError):
        logger.warning("fw-auto 证据包解析失败（证据③降级）", exc_info=True)
        return None


def _read_memo_ref() -> str | None:
    """④ sim_memo 月度档证据指针（最新一份，相对仓根路径）。"""
    memos = sorted(MEMO_DIR.glob("sim-memo-*.json"))
    if not memos:
        return None
    return memos[-1].relative_to(ROOT).as_posix()


def _read_registry_entries(registry_path: Path | None = None) -> dict[str, dict[str, Any]]:
    """注册表条目全量快照 {sid: entry}（只读；PA-1 取 code_path/aliases 作证据锚点）。"""
    import yaml

    path = registry_path or REGISTRY
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, ValueError):
        logger.warning("strategy_registry 读取失败（条目快照为空）", exc_info=True)
        return {}
    return {s["strategy_id"]: s for s in data.get("strategies", []) if s.get("strategy_id")}


def _read_registry_lifecycle(registry_path: Path | None = None) -> dict[str, str]:
    """注册表当前 lifecycle 快照 {sid: lifecycle_status}（只读）。"""
    return {sid: str(e.get("lifecycle_status") or "")
            for sid, e in _read_registry_entries(registry_path).items()}


# ---------- PA-1：candidate→sim 预授权三条件实据评估（缺证据=不通过，禁硬编码 True） ----------
def _load_bothwin_items() -> list[dict[str, Any]]:
    """证据源①：strategy_screen §8 双窗及格集行（真源=screen_source.fetch_bothwin）。

    台账不可达/翻译件缺 build 契约等一律降级为空表——空表在下游判"证据缺位=不通过"，
    与"该路未跑"同罪，故本函数不抛（INVARIANTS：证据源缺失降级不阻断）。
    """
    try:
        from zephyr.strategy_pipeline.screen_source import fetch_bothwin

        return list(fetch_bothwin())
    except Exception:  # noqa: BLE001 —— 证据降级路径，绝不让读失败变成放行理由
        logger.warning("双窗及格集读取失败（dual_window_pass 按证据缺位判）", exc_info=True)
        return []


def _load_fdr_keys() -> set[str]:
    """证据源②：全部 intake 批报告 fdr_keep 并集（键=cand@文件名，口径=intake 本体）。"""
    import yaml

    keys: set[str] = set()
    for path in sorted(INTAKE_REPORT_DIR.glob("intake-*.yaml")):
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except (OSError, ValueError):
            logger.warning("intake 批报告解析失败（该批 fdr_keep 不计入）: %s", path.name, exc_info=True)
            continue
        keys.update(str(k) for k in (doc.get("fdr_keep") or []))
    return keys


def _load_decay_states() -> dict[str, str]:
    """证据源③：MOD-SIG-150 衰减台账 {屏侧候选 id: state}（缺席=空表，下游按未巡检判）。"""
    try:
        doc = json.loads(DECAY_LEDGER.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        logger.warning("衰减台账读取失败（no_pending_decay_alert 按证据缺位判）: %s", DECAY_LEDGER,
                       exc_info=True)
        return {}
    return {str(sid): str(e.get("state") or "")
            for sid, e in (doc.get("strategies") or {}).items() if isinstance(e, dict)}


def _file_base(path: Any) -> str:
    """文件名（Windows 反斜杠/POSIX 正斜杠统一；空值安全）。"""
    return str(path or "").replace("\\", "/").rstrip("/").rsplit("/", 1)[-1]


def _rel(path: Any) -> str:
    """仓根相对显示（不在仓内=原样绝对路径——测试 tmp 树注入同样可用）。"""
    p = Path(path)
    try:
        return p.relative_to(ROOT).as_posix()
    except ValueError:
        return p.as_posix()


def _anchor_names(entry: dict[str, Any] | None) -> set[str]:
    """注册表 code_path 锚点文件名集（"+" 双锚条目拆开逐认）。"""
    raw = str((entry or {}).get("code_path") or "")
    return {_file_base(p) for p in raw.split("+") if _file_base(p)}


def _match_bothwin(entry: dict[str, Any] | None, items: list[dict[str, Any]]) -> dict | None:
    """注册表条目→双窗及格行（源文件名 ∧ aliases 屏侧候选 id 两路互认，先到先得）。"""
    names, cands = _anchor_names(entry), {str(a) for a in ((entry or {}).get("aliases") or [])}
    for it in items:
        if names and _file_base(it.get("source_file")) in names:
            return it
        if str(it.get("strategy_id")) in cands:
            return it
    return None


def _screen_sid(entry: dict[str, Any] | None, item: dict | None) -> str | None:
    """屏侧候选 id（CAND-*）：双窗行优先，回退注册表 aliases（衰减台账与 fdr 名单都按它建行）。"""
    if item and item.get("strategy_id"):
        return str(item["strategy_id"])
    for a in ((entry or {}).get("aliases") or []):
        if str(a).startswith("CAND-"):
            return str(a)
    return None


def _fail(reason: str, source: str) -> dict[str, Any]:
    return {"ok": False, "reason": reason, "source": source}


def _cond_dual_window(entry: dict | None, item: dict | None) -> dict[str, Any]:
    """§8 双窗：IS SR>0 ∧ 各 OOS 段 SR>0 ∧ 衰减未越存疑线（判定真源=strategy_screen_query）。"""
    source = "c1_backtest.strategy_screen(§8 双窗及格集)"
    if entry is None:
        return _fail("注册表无该策略条目=证据锚点缺失", "strategy_registry")
    if not _anchor_names(entry):
        return _fail("注册表条目无 code_path，无法与 §8 双窗台账联查", "strategy_registry")
    if item is None:
        return _fail(f"双窗及格集无 code_path∈{sorted(_anchor_names(entry))} 行（未跑或双窗未过）", source)
    return {"ok": True,
            "reason": f"双窗及格行在位 {item.get('key')}：IS SR={item.get('is_sharpe')} ∧ "
                      f"{len(item.get('segments') or [])} 段 OOS 逐段正且衰减未越线",
            "source": source}


def _cond_bh_fdr(entry: dict | None, item: dict | None, fdr_keys: set[str]) -> dict[str, Any]:
    """BH-FDR q≤0.10 批内通过：以 intake 批报告 fdr_keep 名单为真源（无列可查，报告即台账）。"""
    source = f"{_rel(INTAKE_REPORT_DIR)}/intake-*.yaml"
    key = (item or {}).get("key") or None
    if not key:
        sid, names = _screen_sid(entry, item), sorted(_anchor_names(entry))
        key = f"{sid}@{names[0]}" if sid and names else None
    if key is None:
        return _fail("屏侧候选 id 与源文件名无法联合定位=fdr_keep 键不可构造", source)
    if not fdr_keys:
        return _fail(f"无批报告 fdr_keep 名单（键={key}）=无 BH-FDR 判定记录，判不了不放行", source)
    if key not in fdr_keys:
        return _fail(f"键 {key} 不在任一批 fdr_keep 名单（BH-FDR 未过或该批未跑）", source)
    return {"ok": True, "reason": f"键 {key} 在 intake 批报告 fdr_keep 名单（q≤0.10 批内通过）",
            "source": source}


def _cond_no_pending_decay(screen_sid: str | None, states: dict[str, str]) -> dict[str, Any]:
    """衰减闸：MOD-SIG-150 台账无 failed/retired 未决建议才免检放行（本件是台账的下游消费端）。"""
    source = _rel(DECAY_LEDGER)
    if not states:
        return _fail(f"衰减台账空或缺席（{source}）=无衰减巡检记录，须先跑 run_strategy_decay_certify",
                     source)
    if screen_sid is None:
        return _fail("无法定位屏侧候选 id（衰减台账按 CAND-* 建行）=查无巡检记录", source)
    state = states.get(screen_sid)
    if state is None:
        return _fail(f"衰减台账无 {screen_sid} 行（该策略未被周扫覆盖）", source)
    if state in _DECAY_PENDING_STATES:
        return _fail(f"衰减闸门未决建议 state={state}（判死/退役在案）不许晋升", source)
    return {"ok": True, "reason": f"衰减台账 state={state}，无 {'/'.join(_DECAY_PENDING_STATES)} 未决建议",
            "source": source}


def evaluate_sim_preauthorization(
    sid: str,
    *,
    entry: dict[str, Any] | None = None,
    bothwin_items: list[dict[str, Any]] | None = None,
    fdr_keys: set[str] | None = None,
    decay_states: dict[str, str] | None = None,
    registry_path: Path | None = None,
) -> dict[str, Any]:
    """candidate→sim 预授权三条件逐项回落实据（纯只读，任何一路不可用=该路不通过）。

    返回 {ok, conditions{条件名:{ok,reason,source}}, context, screen_sid, failed}；
    context 即 SimPromotionContext，交 FSM guard 独立复裁（本件不自证）。
    """
    from zephyr.strategy_pipeline.lifecycle_fsm import SimPromotionContext

    if entry is None:
        entry = _read_registry_entries(registry_path).get(sid)
    items = _load_bothwin_items() if bothwin_items is None else list(bothwin_items)
    keys = _load_fdr_keys() if fdr_keys is None else set(fdr_keys)
    states = _load_decay_states() if decay_states is None else dict(decay_states)
    item = _match_bothwin(entry, items)
    screen_sid = _screen_sid(entry, item)
    conditions = {
        "dual_window_pass": _cond_dual_window(entry, item),
        "bh_fdr_pass": _cond_bh_fdr(entry, item, keys),
        "no_pending_decay_alert": _cond_no_pending_decay(screen_sid, states),
    }
    failed = [k for k in _PREAUTH_KEYS if not conditions[k]["ok"]]
    ctx = SimPromotionContext(**{k: bool(conditions[k]["ok"]) for k in _PREAUTH_KEYS})
    if failed:
        logger.warning("SIM 预授权未成立 %s: %s", sid,
                       "; ".join(f"{k}={conditions[k]['reason']}" for k in failed))
    return {"ok": not failed, "conditions": conditions, "failed": failed,
            "context": ctx, "screen_sid": screen_sid}


def _decide_recommendation(governance_action: str | None, pass_months: int,
                           breach_months: int) -> str:
    """建议词表归一：governance 优先，判定史兜底（规则真源=SOP-C §8 连续 2 月门槛）。"""
    if governance_action in _GOV_REC_MAP:
        return _GOV_REC_MAP[governance_action]
    if pass_months >= 2 and breach_months == 0:
        return "promote"
    if breach_months >= 2:
        return "demote"
    return "hold"


# ---------- 建议包生成 ----------
def _compose_advisory(sid: str, gov: dict[str, Any] | None, dev: dict[str, Any] | None,
                      fw: dict[str, Any] | None, memo_ref: str | None,
                      lifecycle_now: str) -> dict[str, Any]:
    dev = dev or {}
    pass_months, breach_months = int(dev.get("pass", 0)), int(dev.get("breach", 0))
    governance_action = (gov or {}).get("recommendation")
    rec = _decide_recommendation(governance_action, pass_months, breach_months)
    day = now_utc().strftime("%Y%m%d")
    return {
        "advisory_id": f"ADV-{day}-{sid}",
        "strategy_id": sid,
        "lifecycle_now": lifecycle_now,
        "evidence": {
            "sim_pass_months": pass_months,
            "sim_breach_months": breach_months,
            "fw_backtest": fw,
            "governance_action": governance_action,
            "memo_ref": memo_ref,
        },
        "recommendation": rec,
        "generated_at": now_utc().isoformat(timespec="seconds"),
    }


def build_advisories(advisory_dir: Path | None = None) -> list[dict]:
    """三路证据合流生成建议包并落 JSON（幂等覆盖）。hold 不产包（S12 §5.1：无建议策略不产包）。"""
    gov = _read_latest_governance()
    dev = _read_deviation_months()
    fw = _read_fw_evidence()
    memo_ref = _read_memo_ref()
    lifecycle = _read_registry_lifecycle()
    sids = sorted({s for s in (set(gov) | set(dev))
                   if lifecycle.get(s) in _OBSERVING_LIFECYCLES})
    out: list[dict] = []
    for sid in sids:
        adv = _compose_advisory(sid, gov.get(sid), dev.get(sid), fw, memo_ref,
                                lifecycle.get(sid, ""))
        if adv["recommendation"] == "hold":
            continue
        out.append(adv)
    if out:
        target = advisory_dir or ADVISORY_DIR
        target.mkdir(parents=True, exist_ok=True)
    for adv in out:
        path = (advisory_dir or ADVISORY_DIR) / f"{adv['advisory_id']}.json"
        payload = json.dumps(adv, ensure_ascii=False, indent=1) + "\n"
        r = safe_write_text(path, payload, newline="\n")
        if not getattr(r, "written", True):
            raise RuntimeError(f"建议包写入未确认（CAS 拒绝）: {adv['advisory_id']}")
        logger.info("建议包已落档: %s → %s", adv["advisory_id"], adv["recommendation"])
    return out


# ---------- 事件入口（pipeline_events OPTIONAL_DUE_KINDS 契约） ----------
def run_promotion_advisory_due(event: dict) -> dict:
    """promotion_advisory_due 执行体：生成建议包；promote 包经 data/alerter 真通道推送 Owner。

    webhook 未配置=alerter 自降级本地告警文件（data/failures/），通道故障不抛不反噬。
    """
    advisories = build_advisories()
    pushed: list[str] = []
    for adv in advisories:
        if adv["recommendation"] != "promote":
            continue
        fw = adv["evidence"].get("fw_backtest") or {}
        msg = (f"转正建议 {adv['advisory_id']}: {adv['strategy_id']}"
               f"（{adv['lifecycle_now']}）建议批准进整装；"
               f"fw={fw.get('run_id')} sharpe={fw.get('sharpe')} panel_ok={fw.get('panel_ok')}；"
               f"前端拍板: 页面 #promotion")
        try:
            from zephyr.data.alerter import Alerter

            Alerter().notify(f"promotion_advisory-{adv['advisory_id']}", msg,
                             level="ERROR", source="promotion_advisory")
            pushed.append(adv["advisory_id"])
        except Exception:  # noqa: BLE001——推送通道故障不反噬建议产出（包已在盘上）
            logger.warning("转正建议推送失败（本地告警文件未落，包已在盘）: %s",
                           adv["advisory_id"], exc_info=True)
    logger.info("转正建议包 %d 份（推送 %d）", len(advisories), len(pushed))
    return {"event_id": event.get("id"), "built": len(advisories),
            "advisories": [a["advisory_id"] for a in advisories], "pushed": pushed}


# ---------- 查询（S13 GET 契约真源） ----------
def list_advisories(advisory_dir: Path | None = None) -> list[dict]:
    """扫目录返回全部建议包（已决的附 decision 台账）。"""
    target = advisory_dir or ADVISORY_DIR
    out: list[dict] = []
    for path in sorted(target.glob("ADV-*.json")):
        try:
            adv = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            logger.warning("建议包解析失败（跳过）: %s", path.name, exc_info=True)
            continue
        decision_path = path.with_name(f"{path.stem}.decision.json")
        if decision_path.exists():
            try:
                adv["decision"] = json.loads(decision_path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                adv["decision"] = {"corrupt": True}
        out.append(adv)
    return out


# ---------- 注册表 lifecycle CAS 更新（registry_writer 同门：文本级手术+写后复核） ----------
_LC_LINE_RE = re.compile(r'^(?P<indent>\s*)lifecycle_status:\s*"?[a-z_]+"?\s*$')
_UPD_LINE_RE = re.compile(r"^(?P<indent>\s*)updated_at:\s*.*$")
_SID_LINE_RE = re.compile(r'^(\s*)- strategy_id:\s*"?(?P<sid>[A-Za-z0-9._-]+)"?\s*$')


def _locate_registry_block(lines: list[str], sid: str) -> tuple[int, int]:
    """目标条目块区间 [start, end)：块边界=下一个同缩进的列表项行。

    真册条目为两空格缩进 `  - `；缩进感知防跨条目误伤。
    """
    for i, line in enumerate(lines):
        m = _SID_LINE_RE.match(line.rstrip("\n"))
        if m and m.group("sid") == sid:
            indent = m.group(1)
            end = next((j for j in range(i + 1, len(lines))
                        if lines[j].startswith(f"{indent}- ")), len(lines))
            return i, end
    raise RuntimeError(f"注册表未找到条目: {sid}")


def _rewrite_lifecycle_fields(lines: list[str], start: int, end: int, sid: str,
                              new_state: str) -> None:
    """块内只改 lifecycle_status + updated_at 两行（原地改 lines；两行任一不唯一=异常上抛）。"""
    n_lc = n_upd = 0
    for j in range(start, end):
        if (lc := _LC_LINE_RE.match(lines[j])):
            lines[j] = f"{lc.group('indent')}lifecycle_status: \"{new_state}\"\n"
            n_lc += 1
        elif (upd := _UPD_LINE_RE.match(lines[j])):
            lines[j] = f"{upd.group('indent')}updated_at: {now_utc().strftime('%Y-%m-%d')}\n"
            n_upd += 1
    if n_lc != 1 or n_upd != 1:
        raise RuntimeError(f"注册表条目字段定位异常: {sid} lifecycle={n_lc} updated_at={n_upd}")


def _verify_registry_surgery(before: str, after: str, sid: str) -> None:
    """语义层写前复核：条目集合零触碰 + 仅目标条目两字段变化（yaml 解析比对，非文本 diff）。"""
    import yaml

    b, a = yaml.safe_load(before), yaml.safe_load(after)
    b_map = {e["strategy_id"]: e for e in b.get("strategies", [])}
    a_list = a.get("strategies", [])
    assert [e["strategy_id"] for e in a_list] == list(b_map), "写后复核失败：条目集合被触碰"
    changed = []
    for old, new in zip(b.get("strategies", []), a_list):
        diff = {k for k in set(old) | set(new) if old.get(k) != new.get(k)}
        if diff:
            changed.append((new["strategy_id"], diff))
    assert [c[0] for c in changed] == [sid], f"写后复核失败：非目标条目被触碰 {changed}"
    assert {"lifecycle_status", "updated_at"} >= changed[0][1], \
        f"写后复核失败：目标条目越界改动 {changed[0][1]}"


def _update_registry_lifecycle(sid: str, new_state: str,
                               registry_path: Path | None = None) -> dict[str, Any]:
    """单条目 lifecycle_status 手术更新（safe_write_text CAS+写后复核：仅目标条目两字段变化）。"""
    import yaml

    path = registry_path or REGISTRY
    before = path.read_text(encoding="utf-8")
    lines = before.splitlines(keepends=True)
    start, end = _locate_registry_block(lines, sid)
    _rewrite_lifecycle_fields(lines, start, end, sid, new_state)
    after = "".join(lines)
    _verify_registry_surgery(before, after, sid)
    r = safe_write_text(path, after,
                        expected_base_sha256=hashlib.sha256(before.encode("utf-8")).hexdigest(),
                        newline="\n")
    if not getattr(r, "written", True):
        raise RuntimeError("safe_write_text 未确认写入（CAS 竞争?）——fail-closed")
    back = yaml.safe_load(path.read_text(encoding="utf-8"))
    back_lc = {e["strategy_id"]: str(e.get("lifecycle_status") or "")
               for e in back.get("strategies", [])}
    if back_lc.get(sid) != new_state:
        raise RuntimeError("写后磁盘复核失败：lifecycle 未生效——fail-closed")
    return {"strategy_id": sid, "lifecycle_status": new_state,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()[:12]}


# ---------- Owner 拍板执行器（S13 POST 契约真源） ----------
def _token_check(provided: str | None) -> tuple[str | None, str | None]:
    """token 三态校验。返回 (有效 token, 拒绝 reason)；两者互斥。

    token=None → 服务端自取配置密钥（前端拍板=Owner 点击即授权）；
    token 显式给出 → sha256 常量时间比对；未配置密钥 → fail-closed。
    """
    secret = get_secret_or_default(OWNER_TOKEN_KEY, "")
    if not secret:
        return None, "owner_token_not_configured"
    if provided is None:
        return secret, None
    if not hmac.compare_digest(
            hashlib.sha256(provided.encode("utf-8")).hexdigest(),
            hashlib.sha256(secret.encode("utf-8")).hexdigest()):
        return None, "invalid_token"
    return provided, None


def _kill_switch_clear() -> tuple[bool, str]:
    """总闸探针（与 intake 同款 fail-closed）：非 normal/探测失败=不清除，转正流转一律拒。"""
    try:
        from zephyr.strategy_pipeline.pipeline_events import kill_switch_clear
        return kill_switch_clear()
    except Exception:  # noqa: BLE001——探针不可达同样 fail-closed
        return False, "probe_unavailable"


class _PreauthDenied(Exception):
    """PA-1：candidate→sim 预授权实据不齐（仅 decide 内部消费，不外抛——契约=返回拒绝 dict）。"""

    def __init__(self, pre: dict[str, Any]) -> None:
        super().__init__("; ".join(f"{k}={v['reason']}" for k, v in pre["conditions"].items()
                                   if not v["ok"]))
        self.conditions = pre["conditions"]
        self.failed = pre["failed"]
        self.screen_sid = pre.get("screen_sid")


def _transition_lifecycle(sid: str, target_state: str, effective_token: str, *,
                          lifecycle_now: str = "",
                          registry_path: Path | None = None,
                          sim_evidence: dict[str, Any] | None = None) -> tuple[dict, dict]:
    """FSM 定位+流转到决策目标态，返回 (fsm 回执, 预授权留痕)。

    FSM 每台以 candidate 起步（注册表才是状态真源），lifecycle_now 留痕进审计字段说明落差。
    promote（→production）：必须先以**实据**走过 candidate→sim（PA-1，取代旧硬编码 True
    三元组），任一条件证据缺位即 _PreauthDenied；
    demote（→shelved）：走 candidate→shelved 无守卫合法边——降档是风险收敛动作，
    被晋升预授权卡住等于反向 fail-open，故此处**不**造任何布尔凭据。
    """
    from zephyr.strategy_pipeline.lifecycle_fsm import (
        CANDIDATE,
        PRODUCTION,
        SHELVED,
        SIM,
        build_strategy_fsm,
    )

    fsm = build_strategy_fsm(sid)
    preauth: dict[str, Any]
    if target_state == PRODUCTION:
        pre = evaluate_sim_preauthorization(sid, registry_path=registry_path, **(sim_evidence or {}))
        if not pre["ok"]:
            raise _PreauthDenied(pre)
        if fsm.current_state == CANDIDATE:
            fsm.transition(SIM, {"sim_promotion": pre["context"]})
        preauth = {"mode": "evidence", "lifecycle_now": lifecycle_now,
                   "screen_sid": pre["screen_sid"], "conditions": pre["conditions"]}
    else:
        preauth = {"mode": "not_required", "lifecycle_now": lifecycle_now,
                   "reason": f"目标态 {target_state} 低于 sim（在册 {lifecycle_now}）："
                             f"降档走 candidate→{SHELVED} 无守卫合法边，不复核晋升预授权"}
    fsm_target = PRODUCTION if target_state == "production" else SHELVED
    ctx: dict[str, Any] = {"owner_token": effective_token} if target_state == "production" else {}
    from_state = fsm.current_state
    fsm.transition(fsm_target, ctx)  # 非法转换/Owner 门拒绝=原样上抛（fail-closed）
    return {"from": from_state, "to": target_state}, preauth


def decide(advisory_id: str, decision: str, token: str | None = None,
           via: str = "api", advisory_dir: Path | None = None,
           registry_path: Path | None = None,
           sim_evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    """Owner 拍板：token 校验→FSM 流转→注册表 CAS 更新→decision 台账→alerter 回执。

    幂等：已决 advisory（台账存在）重复 decide=拒绝（{"ok": false, "reason": "already_decided"}）。
    token 明文只进内存，台账/日志/回执一律 token 指纹。
    sim_evidence：PA-1 三条件实据的显式注入位（{"bothwin_items","fdr_keys","decay_states"}，
    离线/测试用；缺省则本件自读三路真源，读不到=证据缺位=promote 拒绝）。
    """
    if decision not in ("approve", "reject"):
        raise ValueError(f"decision 非法: {decision!r}（只认 approve|reject）")
    ks_ok, _ks_why = _kill_switch_clear()
    if not ks_ok:
        logger.warning("拍板拒绝（kill_switch_active）: %s", advisory_id)
        return {"ok": False, "advisory_id": advisory_id,
                "reason": "kill_switch_active（总闸激活，转正流转暂停；恢复后重试）"}
    target_dir = advisory_dir or ADVISORY_DIR
    adv_path = target_dir / f"{advisory_id}.json"
    if not adv_path.is_file():
        raise FileNotFoundError(f"advisory 不存在: {advisory_id}")
    decision_path = target_dir / f"{advisory_id}.decision.json"
    if decision_path.exists():
        return {"ok": False, "advisory_id": advisory_id, "reason": "already_decided"}
    effective, deny = _token_check(token)
    if deny:
        logger.warning("拍板拒绝（%s）: %s", deny, advisory_id)
        return {"ok": False, "advisory_id": advisory_id, "reason": deny}
    assert effective is not None  # deny 为空则必有有效凭据
    adv = json.loads(adv_path.read_text(encoding="utf-8"))
    sid = adv["strategy_id"]
    recommendation = adv.get("recommendation")
    target_state = _DECISION_TARGET.get(recommendation) if decision == "approve" else None

    fsm_state: dict[str, Any] | None = None
    registry_receipt: dict[str, Any] | None = None
    preauth_audit: dict[str, Any] | None = None
    if target_state is not None:
        lifecycle_now = _read_registry_lifecycle(registry_path).get(sid, "")
        if lifecycle_now not in _OBSERVING_LIFECYCLES:
            return {"ok": False, "advisory_id": advisory_id,
                    "reason": "invalid_lifecycle", "lifecycle_now": lifecycle_now}
        try:
            fsm_state, preauth_audit = _transition_lifecycle(
                sid, target_state, effective, lifecycle_now=lifecycle_now,
                registry_path=registry_path, sim_evidence=sim_evidence)
        except _PreauthDenied as exc:  # PA-1：预授权实据不齐=拒批，不落墓碑（补证后可重试）
            logger.warning("拍板拒绝（sim_preauthorization_not_established）: %s %s",
                           advisory_id, exc)
            return {"ok": False, "advisory_id": advisory_id, "strategy_id": sid,
                    "reason": "sim_preauthorization_not_established",
                    "failed": exc.failed, "conditions": exc.conditions,
                    "screen_sid": exc.screen_sid}
        registry_receipt = _update_registry_lifecycle(sid, target_state, registry_path)

    receipt = {
        "advisory_id": advisory_id,
        "strategy_id": sid,
        "decision": decision,
        "via": via,
        "recommendation": recommendation,
        "decided_at": now_utc().isoformat(timespec="seconds"),
        "token_fingerprint": _fingerprint(effective),
        "fsm": fsm_state,
        "sim_preauthorization": preauth_audit,
        "registry": registry_receipt,
    }
    r = safe_write_text(decision_path,
                        json.dumps(receipt, ensure_ascii=False, indent=1) + "\n", newline="\n")
    if not getattr(r, "written", True):
        raise RuntimeError(f"decision 台账写入未确认: {advisory_id}")
    _notify_decision(receipt)
    logger.info("拍板落账: %s %s via=%s token=%s", advisory_id, decision, via,
                receipt["token_fingerprint"])
    return {"ok": True, **receipt}


def _notify_decision(receipt: dict[str, Any]) -> None:
    """拍板回执推 Owner（ERROR 级触达飞书+failure 文件；通道故障不抛不反噬拍板）。"""
    msg = (f"转正拍板回执 {receipt['advisory_id']}: {receipt['strategy_id']} "
           f"{receipt['decision']}（via={receipt['via']}）"
           f" fsm={receipt['fsm']} token={receipt['token_fingerprint']}")
    try:
        from zephyr.data.alerter import Alerter

        Alerter().notify(f"promotion_decision-{receipt['advisory_id']}", msg,
                         level="ERROR", source="promotion_advisory")
    except Exception:  # noqa: BLE001——回执通道故障不影响拍板结果（台账已在盘）
        logger.warning("拍板回执推送失败（台账已在盘）: %s", receipt["advisory_id"], exc_info=True)


# ---------- CLI 自检 ----------
def main(argv: list[str] | None = None) -> int:  # pragma: no cover — CLI 薄壳
    import argparse

    ap = argparse.ArgumentParser(description="转正建议包 CLI（build/list/preauth）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build", help="生成建议包+推送")
    sub.add_parser("list", help="列出建议包")
    sp = sub.add_parser("preauth", help="SIM 预授权三条件实据核验（只读，零写盘）")
    sp.add_argument("strategy_id")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    if args.cmd == "build":
        print(json.dumps(run_promotion_advisory_due({}), ensure_ascii=False, indent=1))
    elif args.cmd == "preauth":
        from dataclasses import asdict

        pre = evaluate_sim_preauthorization(args.strategy_id)
        pre["context"] = asdict(pre["context"])
        print(json.dumps(pre, ensure_ascii=False, indent=1, default=str))
    else:
        print(json.dumps(list_advisories(), ensure_ascii=False, indent=1, default=str))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
