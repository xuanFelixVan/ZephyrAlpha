# [BLUEPRINT] MOD-BT-189 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.strategy_pipeline.intake
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.strategy_pipeline.bh_fdr; zephyr.strategy_pipeline.lifecycle_fsm;
#   zephyr.strategy_pipeline.screen_source; zephyr.strategy_pipeline.registry_writer;
#   scripts.backtest.auto_mount(经 sys.path); zephyr.shared.io.file_utils
# [CONSUMERS] DataScheduler task_completed 事件（经 pipeline_events 轻钩子）; c4_batch_screen 落账钩子;
#   面板/告警（报告落盘+JSON 回执）; sim_paper_ledger 开户（sim 流转后 emit sim_wallet_due，
#   经 pipeline_events 消费，本模块不直接依赖账本）
# [STARTUP] imported（事件处理器由 pipeline_events 注册；本包不建线程/不建调度器）
# [MATURITY] experimental
# [INVARIANTS] 全自动 only-add（注册表追加经 registry_writer CAS；挂图经 auto_mount 语义门）；
#   sim 流转=FSM 预授权三条件（A 方案：§8 双窗过 ∧ BH-FDR q≤0.10 ∧ 无未决衰减预警）——
#   FDR 门的是 sim 流转不是候选登记（方案真源 §2.3 入库三件=及格∧簇首∧差异化，§2.5 三条件才含 FDR）；
#   写入路径 fail-closed：EVIDENCE 文件（验收⑥回放证据）不存在即 RuntimeError；
#   KillSwitch 非 normal 时管线拒绝执行（不丢事件：事件留 journal 恢复重放）；
#   幂等=同批重放零 diff（已入库判定键=code_path，回退 strategy_id）；
#   BH 假设族=当批 bothwin 及格全集（含已入库者防选择偏差）；
#   行数豁免（GOV-010 分层裁量 301-500 档）：本文件=C6 编排单抽象族高内聚（及格/聚类/差异化/
#   入库/挂图调用/FSM 共享同一组真源常量与 only-add 语义，拆分=跨文件耦合+语义漂移），
#   变更隔离面=管线六步同批演化
# [MODIFY-GUARD] tests/strategy_pipeline/test_intake.py
# [STABILITY] experimental
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(KillSwitch 激活/写入路径未授权/CAS 失败)；guard 拒绝=正常业务路径
# [TESTS] tests/strategy_pipeline/test_intake.py
# [A_module] module_id=MOD-BT-189 | layer=module | stability=experimental | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] intake-mod-bt-189-20260915
"""C6 自动入库编排——事件消费端（挖矿真源 §2；A 方案落地本体）。

入口=run_intake(trigger_batch, passed_p, corr, dry_run)（纯编排，无线程/无调度）：
  ① bothwin 及格件 → ② BH-FDR 门（q=0.10，管 sim 流转） → ③ ρ>0.6 聚类簇首标记
  → ④ 注册表追加 candidate/（三条件过则）sim（deterministic STR-* 编号+三轴字段级差异化论证）
  → ⑤ auto_mount 挂图（复用，only-add 语义门） → ⑥ FSM 预授权流转记录
  → ⑦ 报告落盘 docs/_working/pipeline-research/reports/ + JSON 回执返回调用方。

自动模式=run_intake_auto(trigger, dry_run)：及格集/p 值/ρ 矩阵全部从台账自取（screen_source）。

职责边界：本模块不实现聚类数学以外的任何决策；差异化论证=字段级对比机器判定
（信号源/持仓周期/状态适配三轴，任一轴无库内同款=差异化成立——与 C5 报告 §差异化论证口径一致）。
"""

from __future__ import annotations

import json
import logging
import re
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
REGISTRY = ROOT / "docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml"
REPORT_DIR = ROOT / "docs/_working/pipeline-research/reports"
EVIDENCE = ROOT / "docs/01_policies_and_standards/policies/strategy_intake_acceptance6_evidence.md"  # 验收⑥证据=写入路径钥匙（FILE-PLACEMENT-TTL 裁定：永久件住 policies 区）
BH_Q = 0.10            # A 方案预授权：FDR 上界
CLUSTER_RHO = 0.6      # C5 聚类阈值（上一班人工先例同参数）
DIFF_AXES = ("signal_axis", "holding_period", "state_adaptation")


def _load_registry() -> dict[str, Any]:
    import yaml
    return yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))


def _kill_switch_clear() -> bool:
    """管线专用探针：fail-closed（探测失败=不清除；与旧版 fail-open 相反——全托管后安全优先）。"""
    try:
        from zephyr.strategy_pipeline.pipeline_events import kill_switch_clear
        ok, _why = kill_switch_clear()
        return ok
    except Exception:  # noqa: BLE001——探针不可达同样 fail-closed
        return False


# ---------- ② BH-FDR ----------
def fdr_gate(candidates: dict[str, float], q: float = BH_Q) -> tuple[set[str], dict[str, Any]]:
    from zephyr.strategy_pipeline.bh_fdr import bh_filter
    return bh_filter(candidates, q=q)


# ---------- ③ 聚类（相关系数由调用方注入；纯函数核便于测试） ----------
def cluster_heads(corr: dict[tuple[str, str], float], passed: set[str],
                  rho: float = CLUSTER_RHO,
                  strength: dict[str, float] | None = None) -> tuple[set[str], dict[str, str]]:
    """ρ>阈值 贪心聚类（确定性序= sid 字典序）：簇首=簇内 strength 最强者（缺省=sid 最小者）。

    strength 语义=越小越强（传 p 值即「簇首=证据最强」——C5 人工先例「簇首=Sharpe 最高」的
    p 值等价）；平局/缺省回落 sid 最小，保证确定性。
    返回（簇首集，redundant→簇首）。
    """
    order = sorted(passed)
    parent: dict[str, str] = {s: s for s in order}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for (a, b), r in sorted(corr.items()):
        if a in passed and b in passed and r > rho:
            ra, rb = find(a), find(b)
            if ra != rb:
                lo, hi = sorted((ra, rb))
                parent[hi] = lo
    heads: set[str] = set()
    redundant: dict[str, str] = {}
    members: dict[str, list[str]] = {}
    for s in order:
        members.setdefault(find(s), []).append(s)
    for root, mem in members.items():
        if strength:
            head = min(mem, key=lambda s: (strength.get(s, float("inf")), s))
        else:
            head = min(mem)
        heads.add(head)
        for s in mem:
            if s != head:
                redundant[s] = head
    return heads, redundant


# ---------- ④ 差异化论证（字段级机器判定） ----------
def differentiation_ok(entry_axes: dict[str, str], registry_entries: list[dict[str, Any]],
                       cand_tokens: frozenset[str] | None = None,
                       entry_tokens_fn=None) -> tuple[bool, str]:
    """三轴差异化（SOP-C §5 语义的字段级实现）。

    基础判据：三轴字段全同=拒收。
    信号指纹通道（cand_tokens+entry_tokens_fn 提供时）：字段三轴全同的条目，若「指标级信号
    指纹集合」不同（如 DMI vs 双均线、BIAS vs 跌幅门——同一 strategy_class 下的真实信号差异，
    C5 人工论证的机器等价物），则视为差异化成立；指纹集合相等（含非空）=同一信号=拒收。
    """
    for e in registry_entries:
        same_all = all(
            str(e.get(axis_map[a], "")).strip().lower() == str(entry_axes.get(a, "")).strip().lower()
            for a in DIFF_AXES if (axis_map := {"signal_axis": "strategy_class",
                                                "holding_period": "holding_period",
                                                "state_adaptation": "sleeve"}).get(a)
        )
        if not same_all:
            continue
        if cand_tokens is not None and entry_tokens_fn is not None:
            e_tokens = entry_tokens_fn(e)
            if e_tokens and e_tokens == cand_tokens:
                return False, f"与既有 {e.get('strategy_id')} 三轴全同且信号指纹全同（SOP-C §5 拒收）"
            continue
        return False, f"与既有 {e.get('strategy_id')} 三轴全同（SOP-C §5 拒收）"
    return True, "三轴存在差异"


def next_strategy_number(reg: dict[str, Any], family: str) -> int:
    pat = re.compile(rf"STR-{family}-(\d+)")
    nums = [int(m.group(1)) for e in reg.get("strategies", [])
            for m in [pat.match(str(e.get("strategy_id", "")))] if m]
    return (max(nums) + 1) if nums else 1


# ---------- ⑥ FSM ----------
def promote_to_sim(fsm, dual: bool, fdr: bool, no_decay: bool) -> tuple[bool, str]:
    from zephyr.strategy_pipeline.lifecycle_fsm import SIM, SimPromotionContext
    if fsm.current_state != "candidate":
        return False, f"当前态 {fsm.current_state} 非 candidate"
    ctx = {"sim_promotion": SimPromotionContext(
        dual_window_pass=dual, bh_fdr_pass=fdr, no_pending_decay_alert=no_decay)}
    try:
        fsm.transition(SIM, ctx)
        return True, "预授权三条件全过，自动进 sim"
    except Exception as exc:  # noqa: BLE001——guard 拒绝是正常业务路径
        return False, str(exc)[:120]


def _entry_from_item(key: str, item: dict[str, Any] | None, axes: dict[str, str],
                     new_sid: str, lifecycle: str, absorbed: list[dict[str, Any]],
                     fdr_pass: bool, trigger_batch: str) -> dict[str, Any]:
    """注册表条目构造（模板缺省值由 registry_writer 补齐）。"""
    from zephyr.strategy_pipeline import screen_source as ss

    if item:
        src = item["source_file"]
        is_sr = item.get("is_sharpe")
        seg_txt = "; ".join(f"{s['batch']}:SR={s['sharpe']}" for s in item.get("segments", []))
        dd = item.get("max_drawdown")
    else:
        src = ""
        is_sr = None
        seg_txt = ""
        dd = None
    name = ss.derive_name(src) if src else key.split("@")[0]
    fam_txt = ""
    if absorbed:
        fam_txt = "；家族吸收 " + ", ".join(f"{a['name']}(ρ={a['correlation']})" for a in absorbed)
    fdr_txt = "BH-FDR 过（已流转 sim）" if fdr_pass and lifecycle == "sim" else (
        "BH-FDR 未过（candidate 留观，后续批次重检）" if not fdr_pass else "BH-FDR 过")
    evidence = (f"auto_intake {trigger_batch}：§8 双窗及格 IS SR={is_sr}；OOS {seg_txt}；{fdr_txt}"
                f"{fam_txt}；三轴（启发式初值）{axes['signal_axis']}/{axes['holding_period']}"
                f"/{axes['state_adaptation']}。")
    tags = [axes["signal_axis"], "auto_intake"]
    entry = {
        "strategy_id": new_sid,
        "name": name, "name_zh": name,
        "aliases": [key.split("@")[0]],
        "strategy_class": axes["signal_axis"],
        "holding_period": axes["holding_period"],
        "entry_logic": (f"C6 auto_intake 生成（启发式初值，语义字段待复核）：翻译件 {src or '见 code_symbol'}；"
                        "入场/出场逻辑见翻译件源码 build 契约。"),
        "exit_logic": "见翻译件源码 build 契约（auto_intake 条目）。",
        "doc_ref": "docs/_working/pipeline-research/reports/（auto_intake 批报告）",
        "code_path": src,
        "lifecycle_status": lifecycle,
        "created_at": time.strftime("%Y-%m-%d"),
        "updated_at": time.strftime("%Y-%m-%d"),
        "last_evaluated_at": time.strftime("%Y-%m-%d"),
        "baseline_sharpe": is_sr,
        "baseline_max_drawdown": dd,
        "evidence": evidence,
        "tags": tags,
    }
    if src:
        entry["code_symbol"] = f"{src}::build"
    if absorbed:
        entry["family_redundancy"] = {
            "role": "cluster_head", "absorbed": absorbed,
            "ruling_ref": "docs/_working/pipeline-research/reports/（auto_intake 聚类裁定）",
        }
    return entry


def write_intake_report(receipt: dict[str, Any], path: Path | None = None) -> Path:
    """批报告落盘（交接清单⑤/⑫可观测面）：Markdown 一页+JSON 同名落盘。"""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    md = path or (REPORT_DIR / f"intake-{time.strftime('%Y%m%d-%H%M')}.md")
    lines = [
        f"# C6 auto_intake 批报告——{receipt.get('trigger_batch', '')}",
        "",
        f"> {time.strftime('%Y-%m-%d %H:%M')}｜MOD-BT-189｜dry_run={receipt.get('dry_run')}",
        "",
        f"- 及格集：{receipt.get('passed')} 条；BH-FDR 通过：{receipt.get('fdr_keep')}",
        f"- 簇首：{receipt.get('cluster_heads')}",
        f"- 新入库：{json.dumps(receipt.get('created_sids') or [], ensure_ascii=False)}",
        f"- sim 流转：{json.dumps(receipt.get('sim_promoted') or {}, ensure_ascii=False)}",
        f"- 跳过：{json.dumps(receipt.get('skipped') or {}, ensure_ascii=False)}",
        f"- redundant：{json.dumps(receipt.get('redundant') or {}, ensure_ascii=False)}",
        f"- 挂图：{json.dumps(receipt.get('mount') or {}, ensure_ascii=False, default=str)[:400]}",
        "",
    ]
    md.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    # .yaml 而非 .json：DIRECTORY-CONTRACT 禁 docs/_working 落 .json（JSON 是合法 YAML，内容零转换）
    md.with_suffix(".yaml").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=1, default=str), encoding="utf-8", newline="\n")
    return md


# ---------- 编排 ----------
def run_intake(trigger_batch: str, passed_p: dict[str, float],
               corr: dict[tuple[str, str], float] | None = None,
               dry_run: bool = True,
               items: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """①→⑥ 编排：dry_run=True 只出预演回执（默认）；写入路径=注册表 CAS+auto_mount apply。

    items（可选，自动模式注入）：bothwin 结构化行（键=key），用于 code_path 幂等/三轴初值/证据字段。
    """
    if not _kill_switch_clear():
        raise RuntimeError("KillSwitch 激活——管线暂停（事件不丢，恢复后重试）")
    keep, fdr_report = fdr_gate(passed_p)
    heads, redundant = cluster_heads(corr or {}, set(passed_p), strength=passed_p)
    reg = _load_registry()
    entries = list(reg.get("strategies", []))
    have_sids = {e["strategy_id"] for e in entries}
    have_files = {e.get("code_path") for e in entries}
    item_map = {i["key"]: i for i in (items or [])}
    promoted: dict[str, str] = {}
    sim_promoted: dict[str, str] = {}
    skipped: dict[str, str] = {}
    created: list[dict[str, Any]] = []
    created_sids: list[str] = []
    from zephyr.strategy_pipeline import screen_source as ss
    from zephyr.strategy_pipeline.lifecycle_fsm import build_strategy_fsm

    for key in sorted(heads):
        item = item_map.get(key)
        src = item.get("source_file") if item else None
        if src and src in have_files:
            skipped[key] = "已入库（重放幂等，键=code_path）"
            continue
        if key in have_sids:
            skipped[key] = "已入库（重放幂等）"
            continue
        if item:
            axes = ss.derive_axes(src, item.get("turnover"))
        else:
            axes = {"signal_axis": "mined", "holding_period": "波段", "state_adaptation": "alpha"}
        cand_tokens = ss.module_signal_tokens(src) if src else None
        ok, why = differentiation_ok(axes, entries, cand_tokens=cand_tokens,
                                     entry_tokens_fn=ss.entry_signal_tokens)
        if not ok:
            skipped[key] = why
            continue
        fam = ss.family_of(axes["signal_axis"])
        num = next_strategy_number({"strategies": entries}, fam)
        new_sid = f"STR-{fam}-{num:03d}"
        # FSM 预授权三条件（双窗=bothwin 已过；FDR=本批门；衰减=segments 全部 decay<0.5；
        # 无 items（单元/回放注入模式）时衰减证据由调用方负责，默认无预警）
        if item:
            no_decay = all(
                (s.get("decay") is None or float(s["decay"]) < 0.5) for s in item.get("segments", []))
        else:
            no_decay = True
        fsm = build_strategy_fsm(new_sid)
        sim_ok, sim_why = promote_to_sim(fsm, dual=True, fdr=key in keep, no_decay=no_decay)
        lifecycle = "sim" if sim_ok else "candidate"
        absorbed = _absorbed_for(key, redundant, item_map, corr or {})
        entry = _entry_from_item(key, item, axes, new_sid, lifecycle, absorbed,
                                 fdr_pass=key in keep, trigger_batch=trigger_batch)
        created.append(entry)
        created_sids.append(new_sid)
        entries.append({"strategy_id": new_sid, "code_path": src,
                        "strategy_class": axes["signal_axis"],
                        "holding_period": axes["holding_period"], "sleeve": "alpha"})
        promoted[new_sid] = f"{key}: 及格 ∧ 簇首 ∧ 三轴差异化"
        if sim_ok:
            sim_promoted[new_sid] = f"{key}: {sim_why}"
        else:
            promoted[new_sid] += f"；sim 留观（{sim_why}）"
    mount: dict[str, Any] = {}
    if not dry_run:
        if not EVIDENCE.exists():
            raise RuntimeError(f"写入路径未授权：验收⑥证据缺失 {EVIDENCE}——fail-closed")
        from zephyr.strategy_pipeline.registry_writer import append_entries
        # 报告路径先定（条目 doc_ref 指向它），再写注册表→挂图→落报告
        report_path = REPORT_DIR / f"intake-{time.strftime('%Y%m%d-%H%M')}.md"
        for e in created:
            e["doc_ref"] = str(report_path.relative_to(ROOT)).replace("\\", "/")
        reg_receipt = append_entries(created, REGISTRY, dry_run=False)
        mount = _auto_mount_sids(created_sids)
        # 自愈补挂（历史批挂图失败/漏挂的已入库 C4 翻译件条目；单批上界 5 条防长尾放大）
        try:
            sys.path.insert(0, str(ROOT / "scripts/backtest"))
            import auto_mount as _am
            mounted = _am.mounted_sids(_am.MAP_YAML.read_text(encoding="utf-8"))
            reg_now = _load_registry()
            orphan = [e["strategy_id"] for e in reg_now.get("strategies", [])
                      if "/translated/c4_" in (e.get("code_path") or "").replace("\\", "/")
                      and e["strategy_id"] not in mounted]
            orphan = [s for s in orphan if s not in created_sids][:5]
            if orphan:
                mount["self_heal"] = {"attempted": orphan, "result": _auto_mount_sids(orphan)}
        except Exception as exc:  # noqa: BLE001——自愈是增强项，失败不阻断主入库流程
            mount["self_heal"] = {"error": str(exc)[:160]}
        write_intake_report({
            "trigger_batch": trigger_batch, "passed": len(passed_p),
            "fdr_keep": sorted(keep), "cluster_heads": sorted(heads), "redundant": redundant,
            "created_sids": created_sids, "sim_promoted": sim_promoted, "skipped": skipped,
            "dry_run": False, "mount": mount,
        }, path=report_path)
        if sim_promoted:
            # S08 C1 开户钩子：sim 流转落册成功后通知开户（FSM 流转+注册表写之后；
            # 任何故障不反噬入库主流程，事件留 journal 重放）
            _emit_sim_wallet_hook([
                {"strategy_id": e["strategy_id"], "code_path": e.get("code_path") or ""}
                for e in created if e["strategy_id"] in sim_promoted])
        return {
            "trigger_batch": trigger_batch, "passed": len(passed_p),
            "fdr_keep": sorted(keep), "cluster_heads": sorted(heads),
            "redundant": redundant, "promoted": promoted, "sim_promoted": sim_promoted,
            "skipped": skipped, "fdr_report": fdr_report, "dry_run": False,
            "created_sids": created_sids, "registry": reg_receipt, "mount": mount,
            "report": str(report_path),
        }
    return {
        "trigger_batch": trigger_batch,
        "passed": len(passed_p), "fdr_keep": sorted(keep), "cluster_heads": sorted(heads),
        "redundant": redundant, "promoted": promoted, "sim_promoted": sim_promoted,
        "skipped": skipped, "fdr_report": fdr_report, "dry_run": True,
        "created_sids": created_sids, "created": created,
    }


def _emit_sim_wallet_hook(strategies: list[dict[str, Any]]) -> None:
    """开户钩子（S08 C1，MOD-BT-190 写侧钩子同款）：emit sim_wallet_due，任何故障不反噬入库。"""
    try:
        from zephyr.strategy_pipeline.pipeline_events import emit_sim_wallet_due
        out = emit_sim_wallet_due(strategies)
        logging.getLogger(__name__).info("sim_wallet_due 钩子: %s", out.get("event"))
    except Exception as exc:  # noqa: BLE001——事件留 journal 能力已内置；这里兜 import 级故障
        logging.getLogger(__name__).warning("sim_wallet_due 事件通知失败（不影响入库）: %s", exc)


def _corr_of(corr: dict[tuple[str, str], float], a: str, b: str) -> float | None:
    if (a, b) in corr:
        return corr[(a, b)]
    if (b, a) in corr:
        return corr[(b, a)]
    return None


def _absorbed_for(head_key: str, redundant: dict[str, str], item_map: dict[str, dict[str, Any]],
                  corr: dict[tuple[str, str], float]) -> list[dict[str, Any]]:
    """簇首的家族吸收块（candidate_id/name/correlation），ρ 缺失者不收（宁漏勿误）。"""
    from zephyr.strategy_pipeline import screen_source as ss

    out: list[dict[str, Any]] = []
    for rid, head in sorted(redundant.items()):
        if head != head_key:
            continue
        rho = _corr_of(corr, rid, head_key)
        if rho is None:
            continue
        src = (item_map.get(rid) or {}).get("source_file")
        out.append({"candidate_id": rid.split("@")[0],
                    "name": ss.derive_name(src) if src else rid.split("@")[0],
                    "correlation": rho})
    return out


def _auto_mount_sids(sids: list[str]) -> dict[str, Any]:
    """挂图集成（交接清单④）：复用 auto_mount 五步管线原语（语义与 CLI --apply 分支一字不差）。

    步骤：登记→分状态判定（缓存）→ops→手术→only_add 语义断言→CAS 写入→38 规则校验→报告。
    挂图失败不回滚注册表（only-add 自愈：下批重放补挂），降级为告警回执。
    """
    if not sids:
        return {"skipped": "无新条目"}
    sys.path.insert(0, str(ROOT / "scripts/backtest"))
    import auto_mount  # noqa: PLC0415

    try:
        entries = auto_mount.load_registry_entries()
        dom = auto_mount.load_dominant()
        ops, before, weights, skipped = auto_mount._plan_inserts(entries, dom, set(sids))
        after = auto_mount.apply_ops(ops, before)
        auto_mount.only_add_assert(before, after)
        out: dict[str, Any] = {"ops_n": len(ops), "applied": False, "weights": weights,
                               "skipped": skipped, "fails": None}
        if ops:
            from zephyr.shared.io.file_utils import safe_write_text
            import hashlib
            r = safe_write_text(auto_mount.MAP_YAML, after,
                                expected_base_sha256=hashlib.sha256(before.encode()).hexdigest(),
                                newline="\n")
            if not getattr(r, "written", True):
                raise RuntimeError("safe_write_text 未确认写入")
            fails = auto_mount.validate_map()
            assert not fails, f"38 规则校验未过: {fails[:5]}"
            out["fails"] = fails
            out["applied"] = True
    except Exception as exc:  # noqa: BLE001——挂图失败不回滚注册表（下批重放自愈补挂）
        from zephyr.strategy_pipeline.pipeline_events import alert
        alert(f"auto_mount 挂图失败（注册表已入库，下批重放自愈）: {sids} {exc}", level="ERROR")
        return {"error": str(exc)[:200]}
    try:
        out["report"] = str(auto_mount.write_report(out, ",".join(sids)))
    except Exception:  # noqa: BLE001——报告失败不影响挂图事实
        pass
    return out


def run_intake_auto(trigger: str, dry_run: bool = True) -> dict[str, Any]:
    """全自动模式：及格集/p 值/ρ 矩阵自台账获取（screen_source），再走 run_intake。"""
    from zephyr.strategy_pipeline import screen_source as ss

    passed_p, items = ss.passing_with_p()
    corr = ss.corr_matrix(items)
    return run_intake(trigger, passed_p, corr, dry_run=dry_run, items=items)
