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
# [INVARIANTS] 幂等闸生命周期感知（Rx-1）：仅显式 candidate 重检；append-only 新建+原位 CAS 更新双写面
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent

"""C6 自动入库编排——事件消费端（挖矿真源 §2；A 方案落地本体）。

入口=run_intake(trigger_batch, passed_p, corr, dry_run)（纯编排，无线程/无调度）：
  ① bothwin 及格件 → ② BH-FDR 门（q=0.10，管 sim 流转） → ③ ρ>0.6 聚类簇首标记
  → ④ 注册表追加 candidate/（三条件过则）sim（deterministic STR-* 编号+三轴字段级差异化论证）
  → ⑤ auto_mount 挂图（复用，only-add 语义门） → ⑥ FSM 预授权流转记录
  → ⑦ 报告落盘 docs/_working/pipeline-research/reports/ + JSON 回执返回调用方。

自动模式=run_intake_auto(trigger, dry_run)：及格集/p 值/ρ 矩阵全部从台账自取（screen_source）。

职责边界：本模块不实现聚类数学以外的任何决策；差异化论证=字段级对比机器判定
（信号源/持仓周期/状态适配三轴，任一轴无库内同款=差异化成立——与 C5 报告 §差异化论证口径一致）。
# [ALGO_FLOW]
# # [ALGO_FLOW]
# # 层: 输入
# # - id: I1
# #   name: 及格集 p 值字典（bothwin 批，screen_source 产）
# # - id: I2
# #   name: ρ 相关系数对（可空；空=逐台独立簇）
# # - id: I3
# #   name: bothwin 结构化行 items（code_path/segments decay/三轴原料）
# # 层: 算法
# # - id: A1
# #   name_zh: ① BH-FDR 门
# #   desc: bh_filter 多重检验校正，产出 keep 集（假发现率预算 q）
# # - id: A2
# #   name_zh: ② 协同去重聚类
# #   desc: cluster_heads 薄委托 MOD-BT-086 核（ρ>阈值并查集，簇首=证据最强）
# # - id: A3
# #   name_zh: ③ 三轴差异化门
# #   desc: differentiation_ok 拒收三轴全同条目（信号指纹通道）
# # - id: A4
# #   name_zh: ④ FSM 预授权三条件（Rx-1 后：存量 candidate 同门重检）
# #   desc: dual_window ∧ bh_fdr ∧ no_decay → promote_to_sim；否则 candidate 留观
# # - id: A5
# #   name_zh: ⑤ 幂等闸（生命周期感知，Rx-1 语义）
# #   desc: 已毕业（sim/production/shelved/retired）重放跳过；显式 candidate=重检
# # 层: 输出
# # - id: O1
# #   name: 注册表条目（新建/原位更新）+ 批报告 + sim 开户钩子
# # [MATURITY] experimental
# # [INVARIANTS] 全自动 only-add（注册表追加经 registry_writer CAS；挂图经 auto_mount 语义门）；
# #   sim 流转=FSM 预授权三条件（A 方案：§8 双窗过 ∧ BH-FDR q≤0.10 ∧ 无未决衰减预警）——
# #   FDR 门的是 sim 流转不是候选登记（方案真源 §2.3 入库三件=及格∧簇首∧差异化，§2.5 三条件才含 FDR）；
# #   写入路径 fail-closed：EVIDENCE 文件（验收⑥回放证据）不存在即 RuntimeError；
# #   KillSwitch 非 normal 时管线拒绝执行（不丢事件：事件留 journal 恢复重放）；
# #   幂等=同批重放零 diff（已入库判定键=code_path，回退 strategy_id）；
# #   BH 假设族=当批 bothwin 及格全集（含已入库者防选择偏差）；
# #   行数豁免（GOV-010 分层裁量 301-500 档）：本文件=C6 编排单抽象族高内聚（及格/聚类/差异化/
# #   入库/挂图调用/FSM 共享同一组真源常量与 only-add 语义，拆分=跨文件耦合+语义漂移），
# #   变更隔离面=管线六步同批演化
# # [MODIFY-GUARD] tests/strategy_pipeline/test_intake.py
# # [STABILITY] experimental
# # [SAFETY] M
# # [AI_AUTONOMY] ai_modifiable
# # [ERROR_CONTRACT] RuntimeError(KillSwitch 激活/写入路径未授权/CAS 失败)；guard 拒绝=正常业务路径
# # [TESTS] tests/strategy_pipeline/test_intake.py
# # [A_module] module_id=MOD-BT-189 | layer=module | stability=experimental | safety=M | ai_autonomy=ai_modifiable
# # [TTL] permanent
# # [CREATION-TOKEN] intake-mod-bt-189-20260915
# # [/ALGO_FLOW]
"""

from __future__ import annotations

import hashlib
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
EVIDENCE = (
    ROOT / "docs/01_policies_and_standards/policies/strategy_intake_acceptance6_evidence.md"
)  # 验收⑥证据=写入路径钥匙（FILE-PLACEMENT-TTL 裁定：永久件住 policies 区）
BH_Q = 0.10  # A 方案预授权：FDR 上界
CLUSTER_RHO = 0.6  # C5 聚类阈值（上一班人工先例同参数）
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
    except Exception:  # noqa: BLE001 -- 探针不可达同样 fail-closed
        return False


# ---------- ② BH-FDR ----------
def fdr_gate(candidates: dict[str, float], q: float = BH_Q) -> tuple[set[str], dict[str, Any]]:
    from zephyr.strategy_pipeline.bh_fdr import bh_filter

    return bh_filter(candidates, q=q)


# ---------- ③ 聚类（相关系数由调用方注入；纯函数核便于测试） ----------
def cluster_heads(
    corr: dict[tuple[str, str], float],
    passed: set[str],
    rho: float = CLUSTER_RHO,
    strength: dict[str, float] | None = None,
) -> tuple[set[str], dict[str, str]]:
    """ρ>阈值 贪心聚类——薄委托 MOD-BT-086 核（E5 唯一算法实现，2026-10-04 收敛）。

    语义与原内联实现逐字等价（核即原实现迁入 086 后原样保留）；本壳仅为保住
    intake 既有调用面与测试面。strength 语义=越小越强（p 值）。
    """
    from zephyr.pf_alloc.core.synergy_dedup import cluster_heads_from_corr  # noqa: PLC0415

    return cluster_heads_from_corr(corr, passed, rho=rho, strength=strength)


# ---------- ④ 差异化论证（字段级机器判定） ----------
def differentiation_ok(
    entry_axes: dict[str, str],
    registry_entries: list[dict[str, Any]],
    cand_tokens: frozenset[str] | None = None,
    entry_tokens_fn=None,
) -> tuple[bool, str]:
    """三轴差异化（SOP-C §5 语义的字段级实现）。

    基础判据：三轴字段全同=拒收。
    信号指纹通道（cand_tokens+entry_tokens_fn 提供时）：字段三轴全同的条目，若「指标级信号
    指纹集合」不同（如 DMI vs 双均线、BIAS vs 跌幅门——同一 strategy_class 下的真实信号差异，
    C5 人工论证的机器等价物），则视为差异化成立；指纹集合相等（含非空）=同一信号=拒收。
    """
    for e in registry_entries:
        same_all = all(
            str(e.get(axis_map[a], "")).strip().lower() == str(entry_axes.get(a, "")).strip().lower()
            for a in DIFF_AXES
            if (
                axis_map := {
                    "signal_axis": "strategy_class",
                    "holding_period": "holding_period",
                    "state_adaptation": "sleeve",
                }
            ).get(a)
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
    nums = [int(m.group(1)) for e in reg.get("strategies", []) for m in [pat.match(str(e.get("strategy_id", "")))] if m]
    return (max(nums) + 1) if nums else 1


# ---------- ⑥ FSM ----------
def promote_to_sim(fsm, conditions: dict[str, bool]) -> tuple[bool, str]:
    """三条件预授权流转（conditions 键=dual/fdr/no_decay，缺省 True；DEBT-2 收敛形态）。"""
    from zephyr.strategy_pipeline.lifecycle_fsm import SIM, SimPromotionContext

    if fsm.current_state != "candidate":
        return False, f"当前态 {fsm.current_state} 非 candidate"
    dual = bool(conditions.get("dual", True))
    fdr = bool(conditions.get("fdr", True))
    no_decay = bool(conditions.get("no_decay", True))
    ctx = {
        "sim_promotion": SimPromotionContext(dual_window_pass=dual, bh_fdr_pass=fdr, no_pending_decay_alert=no_decay)
    }
    try:
        fsm.transition(SIM, ctx)
        return True, "预授权三条件全过，自动进 sim"
    except Exception as exc:  # noqa: BLE001 -- guard 拒绝是正常业务路径
        return False, str(exc)[:120]


def _entry_from_item(
    key: str,
    item: dict[str, Any] | None,
    axes: dict[str, str],
    new_sid: str,
    lifecycle: str,
    absorbed: list[dict[str, Any]],
    fdr_pass: bool,
    trigger_batch: str,
) -> dict[str, Any]:
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
    fdr_txt = (
        "BH-FDR 过（已流转 sim）"
        if fdr_pass and lifecycle == "sim"
        else ("BH-FDR 未过（candidate 留观，后续批次重检）" if not fdr_pass else "BH-FDR 过")
    )
    evidence = (
        f"auto_intake {trigger_batch}：§8 双窗及格 IS SR={is_sr}；OOS {seg_txt}；{fdr_txt}"
        f"{fam_txt}；三轴（启发式初值）{axes['signal_axis']}/{axes['holding_period']}"
        f"/{axes['state_adaptation']}。"
    )
    tags = [axes["signal_axis"], "auto_intake"]
    entry = {
        "strategy_id": new_sid,
        "name": name,
        "name_zh": name,
        "aliases": [key.split("@")[0]],
        "strategy_class": axes["signal_axis"],
        "holding_period": axes["holding_period"],
        "entry_logic": (
            f"C6 auto_intake 生成（启发式初值，语义字段待复核）：翻译件 {src or '见 code_symbol'}；"
            "入场/出场逻辑见翻译件源码 build 契约。"
        ),
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
            "role": "cluster_head",
            "absorbed": absorbed,
            "ruling_ref": "docs/_working/pipeline-research/reports/（auto_intake 聚类裁定）",
        }
    return entry


def write_intake_report(receipt: dict[str, Any], path: Path | None = None) -> Path:
    """批报告落盘（交接清单⑤/⑫可观测面）：Markdown 一页+JSON 同名落盘。"""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    md = path or (REPORT_DIR / f"intake-{time.strftime('%Y%m%d-%H%M')}.md")
    lines = [
        "---",
        "ttl: task_bound",
        "---",
        "",
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
        json.dumps(receipt, ensure_ascii=False, indent=1, default=str), encoding="utf-8", newline="\n"
    )
    return md


# ---------- 编排 ----------
def run_intake(
    trigger_batch: str,
    passed_p: dict[str, float],
    corr: dict[tuple[str, str], float] | None = None,
    dry_run: bool = True,
    items: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
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
    # Rx-1（2026-10-04 Owner 批）：幂等闸感知生命周期——已毕业件（sim/production/shelved/
    # retired）重放跳过；candidate 留观件本批再过考=重检三条件（兑现"后续批次重检"承诺）
    life_by_file = {e.get("code_path"): str(e.get("lifecycle_status", "")) for e in entries if e.get("code_path")}
    life_by_sid = {e["strategy_id"]: str(e.get("lifecycle_status", "")) for e in entries}
    sid_by_file = {e.get("code_path"): e["strategy_id"] for e in entries if e.get("code_path")}
    reeval_eligible = "candidate"  # 仅显式 candidate 重评；缺省/未知/毕业态一律幂等跳过（保守）
    item_map = {i["key"]: i for i in (items or [])}
    promoted: dict[str, str] = {}
    sim_promoted: dict[str, str] = {}
    reeval_promoted: dict[str, str] = {}
    reeval_failed: dict[str, str] = {}
    skipped: dict[str, str] = {}
    created: list[dict[str, Any]] = []
    created_sids: list[str] = []
    from zephyr.strategy_pipeline import screen_source as ss
    from zephyr.strategy_pipeline.lifecycle_fsm import build_strategy_fsm

    for key in sorted(heads):
        item = item_map.get(key)
        src = item.get("source_file") if item else None
        if src and src in have_files:
            if life_by_file.get(src, "") != reeval_eligible:
                skipped[key] = "已入库（重放幂等，键=code_path）"
                continue
            no_decay = (
                all((s.get("decay") is None or float(s["decay"]) < 0.5) for s in item.get("segments", []))
                if item
                else True
            )
            old_sid = sid_by_file.get(src, "")
            fsm = build_strategy_fsm(old_sid)
            sim_ok, sim_why = promote_to_sim(fsm, {"dual": True, "fdr": key in keep, "no_decay": no_decay})
            if sim_ok:
                reeval_promoted[old_sid] = f"{key}: {sim_why}"
            else:
                reeval_failed[key] = f"candidate 重检未过（{sim_why}）"
            continue
        if key in have_sids:
            if life_by_sid.get(key, "") != reeval_eligible:
                skipped[key] = "已入库（重放幂等）"
                continue
            fsm = build_strategy_fsm(key)
            sim_ok, sim_why = promote_to_sim(fsm, {"dual": True, "fdr": key in keep, "no_decay": True})
            if sim_ok:
                reeval_promoted[key] = f"{key}: {sim_why}"
            else:
                reeval_failed[key] = f"candidate 重检未过（{sim_why}）"
            continue
        if item:
            axes = ss.derive_axes(src, item.get("turnover"))
        else:
            axes = {"signal_axis": "mined", "holding_period": "波段", "state_adaptation": "alpha"}
        cand_tokens = ss.module_signal_tokens(src) if src else None
        ok, why = differentiation_ok(axes, entries, cand_tokens=cand_tokens, entry_tokens_fn=ss.entry_signal_tokens)
        if not ok:
            skipped[key] = why
            continue
        fam = ss.family_of(axes["signal_axis"])
        num = next_strategy_number({"strategies": entries}, fam)
        new_sid = f"STR-{fam}-{num:03d}"
        # FSM 预授权三条件（双窗=bothwin 已过；FDR=本批门；衰减=segments 全部 decay<0.5；
        # 无 items（单元/回放注入模式）时衰减证据由调用方负责，默认无预警）
        if item:
            no_decay = all((s.get("decay") is None or float(s["decay"]) < 0.5) for s in item.get("segments", []))
        else:
            no_decay = True
        fsm = build_strategy_fsm(new_sid)
        sim_ok, sim_why = promote_to_sim(fsm, {"dual": True, "fdr": key in keep, "no_decay": no_decay})
        lifecycle = "sim" if sim_ok else "candidate"
        absorbed = _absorbed_for(key, redundant, item_map, corr or {})
        entry = _entry_from_item(
            key, item, axes, new_sid, lifecycle, absorbed, fdr_pass=key in keep, trigger_batch=trigger_batch
        )
        created.append(entry)
        created_sids.append(new_sid)
        entries.append(
            {
                "strategy_id": new_sid,
                "code_path": src,
                "strategy_class": axes["signal_axis"],
                "holding_period": axes["holding_period"],
                "sleeve": "alpha",
            }
        )
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
            orphan = [
                e["strategy_id"]
                for e in reg_now.get("strategies", [])
                if "/translated/c4_" in (e.get("code_path") or "").replace("\\", "/")
                and e["strategy_id"] not in mounted
            ]
            orphan = [s for s in orphan if s not in created_sids][:5]
            if orphan:
                mount["self_heal"] = {"attempted": orphan, "result": _auto_mount_sids(orphan)}
        except Exception as exc:  # noqa: BLE001 -- 自愈是增强项，失败不阻断主入库流程
            mount["self_heal"] = {"error": str(exc)[:160]}
        # Rx-1：重检放行的存量 candidate 原位 CAS 更新（append_entries 只增不改，走独立面）
        reeval_receipt: dict[str, Any] = {}
        if reeval_promoted and not dry_run:
            reeval_receipt = _apply_candidate_promotion(reeval_promoted, trigger_batch=trigger_batch)
        write_intake_report(
            {
                "trigger_batch": trigger_batch,
                "passed": len(passed_p),
                "fdr_keep": sorted(keep),
                "cluster_heads": sorted(heads),
                "redundant": redundant,
                "created_sids": created_sids,
                "sim_promoted": sim_promoted,
                "reeval_promoted": reeval_promoted,
                "reeval_failed": reeval_failed,
                "skipped": skipped,
                "dry_run": False,
                "mount": mount,
                "reeval_receipt": reeval_receipt,
            },
            path=report_path,
        )
        reeval_hook_rows = [{"strategy_id": sid, "code_path": ""} for sid in reeval_promoted]
        if sim_promoted:
            # S08 C1 开户钩子：sim 流转落册成功后通知开户（FSM 流转+注册表写之后；
            # 任何故障不反噬入库主流程，事件留 journal 重放）
            _emit_sim_wallet_hook(
                [
                    {"strategy_id": e["strategy_id"], "code_path": e.get("code_path") or ""}
                    for e in created
                    if e["strategy_id"] in sim_promoted
                ]
                + reeval_hook_rows
            )
        elif reeval_hook_rows:
            _emit_sim_wallet_hook(reeval_hook_rows)
        return {
            "trigger_batch": trigger_batch,
            "passed": len(passed_p),
            "fdr_keep": sorted(keep),
            "cluster_heads": sorted(heads),
            "redundant": redundant,
            "promoted": promoted,
            "sim_promoted": sim_promoted,
            "reeval_promoted": reeval_promoted,
            "reeval_failed": reeval_failed,
            "skipped": skipped,
            "fdr_report": fdr_report,
            "dry_run": False,
            "created_sids": created_sids,
            "registry": reg_receipt,
            "mount": mount,
            "report": str(report_path),
        }
    return {
        "trigger_batch": trigger_batch,
        "passed": len(passed_p),
        "fdr_keep": sorted(keep),
        "cluster_heads": sorted(heads),
        "redundant": redundant,
        "promoted": promoted,
        "sim_promoted": sim_promoted,
        "reeval_promoted": reeval_promoted,
        "reeval_failed": reeval_failed,
        "skipped": skipped,
        "fdr_report": fdr_report,
        "dry_run": True,
        "created_sids": created_sids,
        "created": created,
    }


def _apply_candidate_promotion(promoted: dict[str, str], *, trigger_batch: str) -> dict[str, Any]:
    """Rx-1 原位 CAS 更新：重检放行的存量 candidate lifecycle→sim（append_entries 只增不改）。

    逐条更新 lifecycle_status/updated_at/last_evaluated_at/evidence（追加放行证据行）；
    safe_write_text CAS + 条目数守恒断言；任何失败整体抛出不落半态。
    """
    import yaml as _yaml

    reg_doc = _load_registry()
    entries = reg_doc.get("strategies", [])
    hit = 0
    today = time.strftime("%Y-%m-%d")
    for e in entries:
        sid = str(e.get("strategy_id", ""))
        if sid in promoted and str(e.get("lifecycle_status", "")) == "candidate":
            e["lifecycle_status"] = "sim"
            e["updated_at"] = today
            e["last_evaluated_at"] = today
            e["evidence"] = (
                str(e.get("evidence") or "")
                + f"；Rx-1 重检放行 {trigger_batch}：{promoted[sid]}（candidate→sim，三条件全绿）"
            )
            hit += 1
    if hit != len(promoted):
        raise RuntimeError(f"Rx-1 更新失配：放行 {len(promoted)} 台，实际命中 {hit}（registry 漂移，fail-closed）")
    from zephyr.shared.io.file_utils import safe_write_text  # noqa: PLC0415 -- 与 _sim 钩子同风格

    new_text = _yaml.safe_dump(reg_doc, allow_unicode=True, sort_keys=False)
    disk_now = REGISTRY.read_text(encoding="utf-8")
    r = safe_write_text(REGISTRY, new_text, expected_base_sha256=hashlib.sha256(disk_now.encode("utf-8")).hexdigest())
    if not getattr(r, "written", False):
        raise RuntimeError(f"Rx-1 CAS 写入未生效: {r}")
    return {"updated": hit, "sids": sorted(promoted)}


def _emit_sim_wallet_hook(strategies: list[dict[str, Any]]) -> None:
    """开户钩子（S08 C1，MOD-BT-190 写侧钩子同款）：emit sim_wallet_due，任何故障不反噬入库。"""
    try:
        from zephyr.strategy_pipeline.pipeline_events import emit_sim_wallet_due

        out = emit_sim_wallet_due(strategies)
        logging.getLogger(__name__).info("sim_wallet_due 钩子: %s", out.get("event"))
    except Exception as exc:  # noqa: BLE001 -- 事件留 journal 能力已内置；这里兜 import 级故障
        logging.getLogger(__name__).warning("sim_wallet_due 事件通知失败（不影响入库）: %s", exc)


def _corr_of(corr: dict[tuple[str, str], float], a: str, b: str) -> float | None:
    if (a, b) in corr:
        return corr[(a, b)]
    if (b, a) in corr:
        return corr[(b, a)]
    return None


def _absorbed_for(
    head_key: str, redundant: dict[str, str], item_map: dict[str, dict[str, Any]], corr: dict[tuple[str, str], float]
) -> list[dict[str, Any]]:
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
        out.append(
            {
                "candidate_id": rid.split("@")[0],
                "name": ss.derive_name(src) if src else rid.split("@")[0],
                "correlation": rho,
            }
        )
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
        out: dict[str, Any] = {
            "ops_n": len(ops),
            "applied": False,
            "weights": weights,
            "skipped": skipped,
            "fails": None,
        }
        if ops:
            import hashlib

            from zephyr.shared.io.file_utils import safe_write_text

            r = safe_write_text(
                auto_mount.MAP_YAML,
                after,
                expected_base_sha256=hashlib.sha256(before.encode()).hexdigest(),
                newline="\n",
            )
            if not getattr(r, "written", True):
                raise RuntimeError("safe_write_text 未确认写入")
            fails = auto_mount.validate_map()
            assert not fails, f"38 规则校验未过: {fails[:5]}"
            out["fails"] = fails
            out["applied"] = True
    except Exception as exc:  # noqa: BLE001 -- 挂图失败不回滚注册表（下批重放自愈补挂）
        from zephyr.strategy_pipeline.pipeline_events import alert

        alert(f"auto_mount 挂图失败（注册表已入库，下批重放自愈）: {sids} {exc}", level="ERROR")
        return {"error": str(exc)[:200]}
    try:
        out["report"] = str(auto_mount.write_report(out, ",".join(sids)))
    except Exception:  # noqa: BLE001 -- 报告失败不影响挂图事实
        pass
    return out


def run_intake_auto(trigger: str, dry_run: bool = True) -> dict[str, Any]:
    """全自动模式：及格集/p 值/ρ 矩阵自台账获取（screen_source），再走 run_intake。"""
    from zephyr.strategy_pipeline import screen_source as ss

    passed_p, items = ss.passing_with_p()
    corr = ss.corr_matrix(items)
    return run_intake(trigger, passed_p, corr, dry_run=dry_run, items=items)


# ---------- Rx-2 月度全池复检（2026-10-04 Owner 批：清库存主通道，candidate_reexam_monthly 执行体） ----------
def run_candidate_reexam(dry_run: bool = False) -> dict[str, Any]:
    """对全 registry candidate 池逐台重评三条件（Rx-2 月度巡检本体）。

    复用 promotion_advisory.evaluate_sim_preauthorization（fail-closed 逐项回执，任何一路
    不可用=该路不通过）：全绿者经 FSM 独立复裁+原位 CAS 更新+开户钩子（复用 Rx-1 面）；
    未过者按缺证据类型分类（dual_window 缺=Rx-3 补考名单；bh_fdr 缺=批报告缺口；
    decay 未决=衰减台账面）。dry_run=True 只出预演回执。
    """
    if not _kill_switch_clear():
        raise RuntimeError("KillSwitch 激活——管线暂停（事件不丢，恢复后重试）")
    from zephyr.strategy_pipeline.lifecycle_fsm import build_strategy_fsm
    from zephyr.strategy_pipeline.promotion_advisory import evaluate_sim_preauthorization

    reg_doc = _load_registry()
    entries = reg_doc.get("strategies", [])
    cands = [e for e in entries if str(e.get("lifecycle_status", "")) == "candidate"]
    promoted: dict[str, str] = {}
    promoted_order: list[str] = []
    gaps: dict[str, list[str]] = {}
    failed: dict[str, str] = {}
    for e in cands:
        sid = str(e.get("strategy_id", ""))
        ev = evaluate_sim_preauthorization(sid, entry=e)
        if ev.get("ok"):
            fsm = build_strategy_fsm(sid, initial_state="candidate")
            ok, why = promote_to_sim(fsm, {"dual": True, "fdr": True, "no_decay": True})
            if ok:
                promoted[sid] = (
                    "月度复检三条件全绿："
                    + "; ".join(f"{k}={v.get('reason', '')[:60]}" for k, v in ev.get("conditions", {}).items())
                )[:220]
                promoted_order.append(sid)
            else:
                failed[sid] = why
        else:
            for k in ev.get("failed", []):
                gaps.setdefault(k, []).append(sid)
            failed[sid] = "三条件未全绿：" + "; ".join(ev.get("failed", []))
    receipt: dict[str, Any] = {
        "candidates": len(cands),
        "promoted": promoted,
        "promoted_order": promoted_order,
        "gaps": {k: len(v) for k, v in gaps.items()},
        "gap_detail": gaps,
        "failed": failed,
        "dry_run": dry_run,
    }
    if promoted and not dry_run:
        receipt["update_receipt"] = _apply_candidate_promotion(promoted, trigger_batch="candidate_reexam_monthly")
        _emit_sim_wallet_hook([{"strategy_id": s, "code_path": ""} for s in promoted_order])
    return receipt
