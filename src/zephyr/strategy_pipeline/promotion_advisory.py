# [BLUEPRINT] MOD-BT-199 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.strategy_pipeline.promotion_advisory
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.strategy_pipeline.lifecycle_fsm（sim→production Owner 门流转）;
#   zephyr.shared.io.file_utils(safe_write_text CAS); zephyr.shared.security.secrets(owner token);
#   zephyr.shared.utils.time_utils(now_utc); zephyr.data.alerter(真通道，降级不抛);
#   run 档案目录只读扫描（data/backtest_artifacts/runs，不经 run_archive API 写路径）
# [CONSUMERS] zephyr.strategy_pipeline.pipeline_events（OPTIONAL_DUE_KINDS promotion_advisory_due
#   lazy 派发）; scripts/backtest/sim_governance（治理建议产出后 emit）;
#   api_server POST /api/promotion-decide（S13/Y2 拍板端点调 decide）
# [STARTUP] imported+event（promotion_advisory_due 经 pipeline_events drain 消费）
# [MATURITY] experimental
# [INVARIANTS] 建议包只产不改册（decide 是唯一写路径：FSM sim→production/shelved + 注册表 CAS）；
#   owner token 明文绝不落盘/进日志（台账只存 sha256 前 12 位指纹，MOD-EX-035 同款）；
#   未配置 ZEPHYR_OWNER_APPROVAL_TOKEN=Owner 门 fail-closed（拒绝，不降级放行）；
#   已决 advisory 重复 decide=拒绝（幂等，台账即墓碑）；
#   建议包幂等（同日同策略覆盖同文件，不堆叠）；无建议策略不产包（S12 §5.1 验收）；
#   三路证据源任一缺失=该路降级（0/null），不抛不阻断其余策略；
#   alerter 推送/回执任何故障不反噬建议产出与拍板执行
# [MODIFY-GUARD] tests/strategy_pipeline/test_promotion_advisory.py
# [STABILITY] experimental
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FileNotFoundError(advisory_id 不存在)；ValueError(decision 非法)；
#   其余失败返回 {"ok": false, "reason": ...}（token 校验失败/未配置/已决/lifecycle 不可流转均不抛）
# [TESTS] tests/strategy_pipeline/test_promotion_advisory.py
# [A_module] module_id=MOD-BT-199 | layer=module | stability=experimental | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
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
时间比对校验。approve→FSM sim→production（demote→sim→shelved）→注册表 lifecycle CAS 更新
→decision 台账（token 指纹留痕）→alerter 回执。

CLI 自检：python -m zephyr.strategy_pipeline.promotion_advisory [build|list]
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


def _read_registry_lifecycle(registry_path: Path | None = None) -> dict[str, str]:
    """注册表当前 lifecycle 快照 {sid: lifecycle_status}（只读）。"""
    import yaml

    path = registry_path or REGISTRY
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, ValueError):
        logger.warning("strategy_registry 读取失败（lifecycle 快照为空）", exc_info=True)
        return {}
    return {s["strategy_id"]: str(s.get("lifecycle_status") or "")
            for s in data.get("strategies", []) if s.get("strategy_id")}


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


def _update_registry_lifecycle(sid: str, new_state: str,
                               registry_path: Path | None = None) -> dict[str, Any]:
    """单条目 lifecycle_status 手术更新（safe_write_text CAS+写后复核：仅目标条目两字段变化）。"""
    import yaml

    path = registry_path or REGISTRY
    before = path.read_text(encoding="utf-8")
    lines = before.splitlines(keepends=True)
    block_start = None
    for i, line in enumerate(lines):
        m = _SID_LINE_RE.match(line.rstrip("\n"))
        if m and m.group("sid") == sid:
            block_start = i
            break
    if block_start is None:
        raise RuntimeError(f"注册表未找到条目: {sid}")
    # 块边界=下一个同缩进的列表项行（真册条目为两空格缩进 `  - `；缩进感知防跨条目误伤）
    block_indent = _SID_LINE_RE.match(lines[block_start].rstrip("\n")).group(1)
    block_end = next((j for j in range(block_start + 1, len(lines))
                      if lines[j].startswith(f"{block_indent}- ")), len(lines))
    n_lc = n_upd = 0
    for j in range(block_start, block_end):
        if _LC_LINE_RE.match(lines[j]):
            lines[j] = f"{_LC_LINE_RE.match(lines[j]).group('indent')}lifecycle_status: \"{new_state}\"\n"
            n_lc += 1
        elif _UPD_LINE_RE.match(lines[j]):
            lines[j] = f"{_UPD_LINE_RE.match(lines[j]).group('indent')}updated_at: {now_utc().strftime('%Y-%m-%d')}\n"
            n_upd += 1
    if n_lc != 1 or n_upd != 1:
        raise RuntimeError(f"注册表条目字段定位异常: {sid} lifecycle={n_lc} updated_at={n_upd}")
    after = "".join(lines)
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


def decide(advisory_id: str, decision: str, token: str | None = None,
           via: str = "api", advisory_dir: Path | None = None,
           registry_path: Path | None = None) -> dict[str, Any]:
    """Owner 拍板：token 校验→FSM 流转→注册表 CAS 更新→decision 台账→alerter 回执。

    幂等：已决 advisory（台账存在）重复 decide=拒绝（{"ok": false, "reason": "already_decided"}）。
    token 明文只进内存，台账/日志/回执一律 token 指纹。
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
    if target_state is not None:
        lifecycle_now = _read_registry_lifecycle(registry_path).get(sid, "")
        if lifecycle_now not in _OBSERVING_LIFECYCLES:
            return {"ok": False, "advisory_id": advisory_id,
                    "reason": "invalid_lifecycle", "lifecycle_now": lifecycle_now}
        from zephyr.strategy_pipeline.lifecycle_fsm import (
            PRODUCTION,
            SHELVED,
            SIM,
            SimPromotionContext,
            build_strategy_fsm,
        )

        fsm = build_strategy_fsm(sid)
        if fsm.current_state == "candidate":
            # 观察态（sim/paper）对位 FSM sim：三条件已在其入册时预授权（intake 先例）
            fsm.transition(SIM, {"sim_promotion": SimPromotionContext(
                dual_window_pass=True, bh_fdr_pass=True, no_pending_decay_alert=True)})
        fsm_target = PRODUCTION if target_state == "production" else SHELVED
        ctx: dict[str, Any] = ({"owner_token": effective} if target_state == "production"
                               else {})
        from_state = fsm.current_state
        fsm.transition(fsm_target, ctx)  # 非法转换/Owner 门拒绝=原样上抛（fail-closed）
        fsm_state = {"from": from_state, "to": target_state}
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

    ap = argparse.ArgumentParser(description="转正建议包 CLI（build/list）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build", help="生成建议包+推送")
    sub.add_parser("list", help="列出建议包")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    if args.cmd == "build":
        print(json.dumps(run_promotion_advisory_due({}), ensure_ascii=False, indent=1))
    else:
        print(json.dumps(list_advisories(), ensure_ascii=False, indent=1, default=str))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
