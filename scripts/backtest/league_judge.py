# [BLUEPRINT] MOD-AUTO-L11-JUDGE | docs/_working/fullflow_mining/03_promotion_ab/02_ab_league.md | 堵点2/3（晋升判据执行器+相关性闸）
# [MODULE] scripts.backtest.league_judge
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] yaml; numpy; zephyr.data.ch_reader; zephyr.pf_core.core.msprt_champion_challenger; zephyr.factor.analysis.bhy_fdr; zephyr.shared.io.file_utils
# [CONSUMERS] Owner 终审门（6 个月挂单终裁）; F74 转正汇总器（challenger 上位建议消费位）;
#   league_archive.py（终审证据链输入）
# [STARTUP] event  # league_judge_due（pipeline_events OPTIONAL_DUE_KINDS 月度档，禁 cron）
# [MATURITY] testing
# [INVARIANTS] 尺动态读 config/standards.yaml（禁硬编码阈值=防第二真源漂移，处方堵点 5 铁律）;
#   STD-SIM-ACCESS-002 非 frozen→硬失败 fail-closed（器必须吃 v2 冻结尺 STD-SIM-ACCESS-002）;
#   建议≠决定——promote/eliminate 均只是判定书建议，注册表 lifecycle 零写触碰（终裁归 Owner 门）;
#   判定书落档 safe_write_text（CAS）；空场诚实——零成员/零对局/断供=如实落档，禁编造成绩;
#   相关性闸是判定前置步（ρ>阈值=合并算一档，晋升封顶观察），非独立系统（处方堵点 3）
# [MODIFY-GUARD] config/league_registry.yaml 只读（入组写经 league_registry.register_member CAS）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] v2 尺缺失/非 frozen→SystemExit(2); 注册表缺失→FileNotFoundError 上抛;
#   CH 不可达→成员序列 None 降级（evidence_gap，不抛不编造）
# [TESTS] tests/backtest/test_league_judge.py
# [A_module] module_id=MOD-AUTO-L11-JUDGE | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""league_judge — A/B 联赛成对晋升判据执行器（处方 02_ab_league.md 堵点 2/3，F73）。

champion（A 组）vs challenger（B 组）成对判定三态：promote（挑战者上位建议）/ eliminate（淘汰）/
observe（观察延续）。判定口径（STD-SWITCH-001，draft→判定书带 draft_ruler 注记）：
  ①成对显著性=msprt e-process（MOD-PF-008 序贯判定，anytime-valid，最少 30 配对样本才终局）；
  ②族多重比较=league_family_scope="league_batch"（同批全体挑战者），e-value→p=min(1,1/M)
    Markov 校准后 BHY q=0.10（90 号 §2 裁定③，canonical=bhy_fdr.DEFAULT_Q）——未过族校正的
    晋升降级观察（族守门）；
  ③相关性闸=correlation_gate_rho（STD-SWITCH-001）对(champion,challenger)日收益序列算 ρ，
    ρ>阈值=合并算一档（骨架 §7 先例），晋升封顶观察；
  ④成本口径=switch_cost_accounting mandatory——delta 取自纸面净值日收益差（往返成本已内嵌）。
个体准入尺=v2 STD-SIM-ACCESS-002（frozen 裁定#337）——本执行器判成对赛绩，个体准入归
promotion_combo_gate（v2 已切，终审时 combo 报告一并入证据链）。

用法（仓库根，Python 3.12）：
    python scripts/backtest/league_judge.py --check-rulers
    python scripts/backtest/league_judge.py --judge [--month 2026-09] [--dry-run]
    python scripts/backtest/league_judge.py --register-first A   # 首位参赛者（sim 现役首个，禁编造）
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from pathlib import Path

import numpy as np
import yaml

_SCRIPT_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_SCRIPT_ROOT), str(_SCRIPT_ROOT / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from zephyr.factor.analysis.bhy_fdr import DEFAULT_Q, bhy_fdr  # noqa: E402
from zephyr.pf_core.core.msprt_champion_challenger import (  # noqa: E402
    ChampionChallengerDecision,
    MSPRTChampionChallenger,
)
from zephyr.shared.io.file_utils import content_sha256, safe_write_text  # noqa: E402
from zephyr.shared.utils.time_utils import now_utc, now_utc_str  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import league_registry as lr  # noqa: E402  同目录收编件（TC-11 件1 基建）

_REPO_ANCHOR = _SCRIPT_ROOT
STANDARDS_PATH = _REPO_ANCHOR / "config" / "standards.yaml"
# 注册表默认路径锚定本文件位置（Path(__file__) 口径，确定性=worktree 本地）——
# 禁用 zephyr.shared.io.paths.REPO_ROOT 作默认（editable 安装+无 ZEPHYR_WORKTREE_ROOT
# 注入时会静默解析到主仓=st-c9-f73 事故实录；注册表写口经 lr.register_member 仍 CAS）。
# [SSOT-REDEFINITION 修复 st-c9-close4] 原 PROJECT_ROOT/REPO_ROOT 模块级重定义遮蔽
# 治理真源（src/zephyr/shared/io/paths.py canonical 符号），改本地命名 _SCRIPT_ROOT/
# _REPO_ANCHOR：语义零变化（仍锚定 __file__ parents[2]=worktree 本地确定性口径），
# 真源名不再被遮蔽。
LEAGUE_REGISTRY_PATH = _REPO_ANCHOR / "config" / "league_registry.yaml"
STRATEGY_REGISTRY_PATH = (
    _REPO_ANCHOR / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "strategy_registry.yaml"
)
JUDGMENT_DIR = _REPO_ANCHOR / "data" / "backtest_artifacts" / "league" / "judgments"
POCKET_TABLE = "c1_backtest.sim_pocket_daily"
# 命名循 SQL_* 常量定义行豁免口径（同 league_monthly_snapshot._SQL_MEMBER_EQUITY_TS 款）
_SQL_POCKET_TSV = (
    "SELECT trade_date, total_equity FROM {table} WHERE strategy_id = '{sid}' ORDER BY trade_date ASC FORMAT TSV"
)
# msprt 终局最小配对样本（STD-SWITCH-001 pair_decision_engine=msprt 注记：最少 30 配对样本才终局）
MIN_PAIRED_SAMPLES = 30
# ρ 计算最小重叠样本（少于=ρ 缺证不作闸判，evidence_gap）
MIN_RHO_SAMPLES = 10
VERDICTS = ("promote", "eliminate", "observe")


# --------------------------------------------------------------------------- 尺加载


def load_standards(path: Path | str = STANDARDS_PATH) -> dict:
    """standards.yaml → {std_id: entry}（缺失→FileNotFoundError）。"""
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    out: dict = {}
    for entry in data.get("standards") or []:
        sid = str(entry.get("std_id") or "").strip()
        if sid:
            out[sid] = entry
    return out


def resolve_rulers(standards: dict) -> dict:
    """解析判据尺（动态读，禁硬编码）：v2 准入尺必须 frozen（fail-closed）；切换尺 draft 容忍带注记。

    返回 {v2, switch, ruler_note, draft_ruler}；v2 缺失/非 frozen→ValueError（器不吃未冻结核尺）。
    """
    v2 = standards.get("STD-SIM-ACCESS-002")
    if not v2:
        raise ValueError("尺缺失：STD-SIM-ACCESS-002（v2）不在 standards.yaml——器必须吃 v2 冻结尺")
    if v2.get("status") != "frozen":
        raise ValueError(f"STD-SIM-ACCESS-002 status={v2.get('status')!r} 非 frozen——fail-closed 拒判")
    switch = standards.get("STD-SWITCH-001") or {}
    th = switch.get("thresholds") or {}
    draft_ruler = switch.get("status") != "frozen"
    note = (
        "STD-SWITCH-001 draft（未冻结）——判定书按 draft 尺口径产出，只作观察/建议证据，终审效力待尺 frozen 后复核"
        if draft_ruler
        else "STD-SWITCH-001 frozen"
    )
    return {
        "v2": v2,
        "switch": switch,
        "v2_thresholds": v2.get("thresholds") or {},
        "rho_max": float(th.get("correlation_gate_rho", 0.7)),
        "family_scope": str(th.get("league_family_scope") or "league_batch"),
        "pair_engine": str(th.get("pair_decision_engine") or "msprt"),
        "draft_ruler": draft_ruler,
        "ruler_note": note,
    }


# --------------------------------------------------------------------------- 数据面


def _esc(raw: str) -> str:
    """strategy_id 入 SQL 模板前的消毒（同 league_monthly_snapshot 口径）。"""
    return str(raw).replace("\\", "\\\\").replace("'", "\\'").strip()


def fetch_equity_series(strategy_id: str, query_fn=None) -> list[tuple[str, float]] | None:
    """成员全窗 equity 序列 [(trade_date, total_equity)]；CH 不可达→None（降级，区别于空序列）。"""
    try:
        if query_fn is None:
            from zephyr.data.ch_reader import query as query_fn  # noqa: PLC0415
        tsv = query_fn(_SQL_POCKET_TSV.format(table=POCKET_TABLE, sid=_esc(strategy_id)))
    except Exception:  # noqa: BLE001 — CH 断连/模块缺失统一降级（不抛不编造）
        return None
    if tsv is None:
        return None
    rows: list[tuple[str, float]] = []
    for line in (tsv or "").splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        try:
            rows.append((parts[0].strip()[:10], float(parts[1])))
        except ValueError:
            continue
    return rows


def daily_returns(series: list[tuple[str, float]]) -> dict[str, float]:
    """equity 序列 → {trade_date: 日收益}（首日无收益；净值序列往返成本已内嵌）。"""
    out: dict[str, float] = {}
    for (d0, e0), (d1, e1) in itertools.pairwise(series):
        if e0 > 0:
            out[d1] = e1 / e0 - 1.0
    return out


def pair_deltas(champ: dict[str, float], chall: dict[str, float]) -> list[float]:
    """共同交易日对齐的日收益差序列 delta = challenger − champion（msprt 输入口径）。"""
    return [chall[d] - champ[d] for d in sorted(set(champ) & set(chall))]


def pairwise_rho(champ: dict[str, float], chall: dict[str, float]) -> float | None:
    """(champion, challenger) 日收益 Pearson ρ；重叠不足→None（缺证不作闸判）。"""
    common = sorted(set(champ) & set(chall))
    if len(common) < MIN_RHO_SAMPLES:
        return None
    a = np.array([champ[d] for d in common], dtype=float)
    b = np.array([chall[d] for d in common], dtype=float)
    if a.std() < 1e-12 or b.std() < 1e-12:
        return None
    r = float(np.corrcoef(a, b)[0, 1])
    return r if math.isfinite(r) else None


# --------------------------------------------------------------------------- 判定核心


def _msprt_verdict(decision: ChampionChallengerDecision) -> str:
    return {
        ChampionChallengerDecision.PROMOTE_CHALLENGER: "promote",
        ChampionChallengerDecision.ELIMINATE_CHALLENGER: "eliminate",
        ChampionChallengerDecision.RETAIN_CHAMPION: "observe",
    }[decision]


def judge_pair(champion_id: str, challenger_id: str, rulers: dict, query_fn=None) -> dict:
    """单对判定（纯计算+只读数据）：msprt e-process + ρ 闸，输出 e-value/p/三态初判。"""
    out: dict = {"champion": champion_id, "challenger": challenger_id}
    eq_c = fetch_equity_series(champion_id, query_fn)
    eq_h = fetch_equity_series(challenger_id, query_fn)
    if eq_c is None or eq_h is None:
        out["verdict"] = "observe"
        out["skipped"] = True
        out["evidence_gaps"] = ["ch_unreachable"]
        return out
    ret_c = daily_returns(eq_c)
    ret_h = daily_returns(eq_h)
    deltas = pair_deltas(ret_c, ret_h)
    out["n_samples"] = len(deltas)
    out["rho"] = pairwise_rho(ret_c, ret_h)
    out["correlation_merged"] = out["rho"] is not None and out["rho"] > rulers["rho_max"]
    if len(deltas) < MIN_PAIRED_SAMPLES:
        # 终局最小样本门（STD-SWITCH-001：最少 30 配对样本才终局）——不足=观察延续
        out["verdict"] = "observe"
        out["e_value"] = None
        out["p_value"] = None
        out["msprt_decision"] = "insufficient_samples"
        out["evidence_gaps"] = ["insufficient_samples"]
        return out
    engine = MSPRTChampionChallenger(alpha=0.05, window_size=MIN_PAIRED_SAMPLES)
    step = engine.evaluate(deltas)
    out["mean_delta"] = step.mean_delta
    out["e_value"] = float(step.m) if math.isfinite(step.m) else None
    out["p_value"] = min(1.0, 1.0 / step.m) if math.isfinite(step.m) and step.m > 0 else 0.0
    out["msprt_decision"] = _msprt_verdict(step.decision)
    out["verdict"] = out["msprt_decision"]
    out["evidence_gaps"] = []
    if out["correlation_merged"]:
        # ρ>阈值=合并算一档（骨架 §7）：同注不加座——晋升封顶观察（淘汰不受闸保护）
        if out["verdict"] == "promote":
            out["verdict"] = "observe"
        out.setdefault("notes", []).append(
            f"correlation_merge: rho={out['rho']:.3f}>{rulers['rho_max']} 合并算一档，晋升封顶观察"
        )
    return out


def apply_family_guard(pair_results: list[dict], rulers: dict) -> list[dict]:
    """BHY q=0.10 族守门（league_family_scope=league_batch）：未过族校正的晋升降级观察。

    e-value→p=min(1,1/M)（Markov 校准，anytime-valid e-process 的合法 p 投影）；
    族=本批全部有 e-value 的挑战者对；淘汰/观察不受 FDR 保护侧影响。
    """
    family = [r for r in pair_results if r.get("p_value") is not None]
    if not family:
        return pair_results
    pvals = [float(r["p_value"]) for r in family]
    res = bhy_fdr(pvals, q=DEFAULT_Q)
    note = {
        "family_scope": rulers["family_scope"],
        "family_size": res.m,
        "bhy_q": res.q,
        "bhy_threshold": res.threshold,
        "n_rejected": res.n_rejected,
    }
    for r, rej in zip(family, res.rejected, strict=True):
        r["bhy_rejected"] = bool(rej)
        if r["msprt_decision"] == "promote" and not rej:
            r["verdict"] = "observe"
            r.setdefault("notes", []).append(
                f"family_guard: BHY q={res.q} 未拒绝（p={r['p_value']:.4f}）——晋升降级观察"
            )
    # 家族注记挂到批级（判定书 family 段）
    return pair_results


def run_judgment(
    registry_path: Path | str | None = None,
    standards_path: Path | str = STANDARDS_PATH,
    query_fn=None,
) -> dict:
    """整场判定：注册表成对配齐→逐对判定→族守门→判定书 dict（不落盘）。

    空场诚实：零成员/零对局/断供全部如实记录，禁编造成绩；v2 尺非 frozen→ValueError 上抛。
    """
    rulers = resolve_rulers(load_standards(standards_path))
    reg = lr.load_registry(registry_path or LEAGUE_REGISTRY_PATH)
    errors = lr.validate_registry(reg)
    if errors:
        raise ValueError(f"league_registry schema 违规: {errors}")
    champ_groups = [g for g in reg["groups"] if g.get("status") == "champion"]
    chall_groups = [g for g in reg["groups"] if g.get("status") == "challenger"]
    pairs = [
        (c, h)
        for g in champ_groups
        for c in g.get("members") or []
        for h in [m for gg in chall_groups for m in gg.get("members") or []]
    ]
    out: dict = {
        "generated_at": now_utc_str(),
        "judge": "scripts/backtest/league_judge.py",
        "rulers": {
            "access_std_id": "STD-SIM-ACCESS-002",
            "access_status": rulers["v2"].get("status"),
            "access_frozen_at": rulers["v2"].get("frozen_at"),
            "switch_std_id": "STD-SWITCH-001",
            "switch_status": rulers["switch"].get("status"),
            "pair_decision_engine": rulers["pair_engine"],
            "family_scope": rulers["family_scope"],
            "bhy_q": DEFAULT_Q,
            "correlation_gate_rho": rulers["rho_max"],
            "min_paired_samples": MIN_PAIRED_SAMPLES,
            "ruler_note": rulers["ruler_note"],
            "draft_ruler": rulers["draft_ruler"],
        },
        "champions": [m for g in champ_groups for m in g.get("members") or []],
        "challengers": [m for g in chall_groups for m in g.get("members") or []],
        "pairs": [],
        "empty_field": not pairs,
        "verdicts": {},
        "suggestions": [],
        "evidence_gaps": [],
    }
    if not pairs:
        out["note"] = "空场：零成员或零对局——如实留档不判胜负（月度只留档铁律；链路保温空跑）"
        return out
    results = [judge_pair(c, h, rulers, query_fn) for c, h in pairs]
    results = apply_family_guard(results, rulers)
    out["pairs"] = results
    for r in results:
        out["verdicts"][f"{r['champion']}|{r['challenger']}"] = r["verdict"]
        if r.get("skipped"):
            out["evidence_gaps"].append(f"{r['champion']}|{r['challenger']}:ch_unreachable")
        elif "insufficient_samples" in (r.get("evidence_gaps") or []):
            out["evidence_gaps"].append(f"{r['champion']}|{r['challenger']}:insufficient_samples")
        if r["verdict"] in ("promote", "eliminate"):
            out["suggestions"].append(
                {
                    "pair": f"{r['champion']}|{r['challenger']}",
                    "verdict": r["verdict"],
                    "note": "建议≠决定——终裁归 Owner 6 个月终审门（league_registry review_policy）",
                }
            )
    return out


# --------------------------------------------------------------------------- 判定书落档


def render_markdown(j: dict) -> str:
    """判定书 dict → markdown 判定书（机生禁手改）。"""
    r = j["rulers"]
    lines = [
        "# A/B 联赛判定书（league judgment）",
        "",
        f"- 生成: {j['generated_at']}（机生禁手改）",
        f"- 准入尺: {r['access_std_id']}（{r['access_status']} {r['access_frozen_at']}，裁定#337）",
        f"- 切换尺: {r['switch_std_id']}（{r['switch_status']}）——{r['ruler_note']}",
        f"- 判定引擎: {r['pair_decision_engine']} e-process（MOD-PF-008，anytime-valid，"
        f"≥{r['min_paired_samples']} 配对样本才终局）",
        f"- 族守门: {r['family_scope']} BHY q={r['bhy_q']}（e→p Markov 校准）",
        f"- 相关性闸: ρ>{r['correlation_gate_rho']} 合并算一档（晋升封顶观察）",
        "",
    ]
    if j.get("empty_field"):
        lines += [f"**{j.get('note', '空场')}**", ""]
        lines += [f"- champions: {j['champions'] or '无'}", f"- challengers: {j['challengers'] or '无'}", ""]
        return "\n".join(lines)
    lines += [
        "| champion | challenger | n | mean δ | e-value M | p | ρ | msprt | BHY | 裁定 |",
        "|----------|-----------|---|--------|-----------|---|---|-------|-----|------|",
    ]
    for p in j["pairs"]:
        ev = "inf" if p.get("e_value") is None and p.get("msprt_decision") == "promote" else p.get("e_value")
        rho = "缺证" if p.get("rho") is None else f"{p['rho']:.3f}"
        lines.append(
            f"| {p['champion']} | {p['challenger']} | {p.get('n_samples', '缺证')} | "
            f"{p.get('mean_delta', '—')} | {ev} | {p.get('p_value', '—')} | {rho} | "
            f"{p.get('msprt_decision', '—')} | {p.get('bhy_rejected', '—')} | **{p['verdict']}** |"
        )
    lines.append("")
    if j["evidence_gaps"]:
        lines += [f"- 证据缺口: {', '.join(j['evidence_gaps'])}（如实降级不编造）"]
    for p in j["pairs"]:
        for note in p.get("notes") or []:
            lines.append(f"- 注记（{p['challenger']}）: {note}")
    for s in j["suggestions"]:
        lines.append(f"- **建议 {s['verdict']}**: {s['pair']}——{s['note']}")
    lines.append("")
    return "\n".join(lines)


def land_judgment(j: dict, out_dir: Path | str | None = None, stamp: str | None = None) -> dict:
    """判定书落档（月度幂等覆盖：judgment-YYYYMM.md/.json，CAS safe_write_text）。"""
    d = Path(out_dir) if out_dir else JUDGMENT_DIR
    d.mkdir(parents=True, exist_ok=True)
    month = stamp or now_utc().strftime("%Y-%m")
    paths = {}
    for suffix, text in ((".md", render_markdown(j)), (".json", json.dumps(j, ensure_ascii=False, indent=2))):
        p = d / f"judgment-{month}{suffix}"
        expected = content_sha256(p.read_text(encoding="utf-8")) if p.exists() else None
        safe_write_text(p, text, expected_base_sha256=expected)
        paths[suffix] = str(p)
    return paths


# --------------------------------------------------------------------------- 首位参赛者


def pick_first_sim_contestant(strategy_registry_path: Path | str = STRATEGY_REGISTRY_PATH) -> str | None:
    """处方规则首位参赛者：strategy_registry 现役 sim 态首个真策略（注册表序）。

    禁编造——sim 现役为空返回 None（诚实空场，留待首个自然 advisory）。
    """
    data = yaml.safe_load(Path(strategy_registry_path).read_text(encoding="utf-8")) or {}
    for entry in data.get("strategies") or []:
        if (
            str(entry.get("lifecycle_status") or "").strip() == "sim"
            and str(entry.get("status") or "").strip() == "active"
        ):
            sid = str(entry.get("strategy_id") or "").strip()
            if sid:
                return sid
    return None


# --------------------------------------------------------------------------- 事件契约+CLI


def run_league_judge_due(event: dict) -> dict:
    """pipeline_events OPTIONAL_DUE_KINDS 契约执行体（def run_xxx_due(event)->dict）。

    月度档（maybe_emit_monthly marker 线）到期触发：整场判定+判定书落档；
    空场照常落空表（链路保温），建议只落判定书不碰注册表 lifecycle。
    """
    j = run_judgment()
    paths = land_judgment(j)
    return {
        "ok": True,
        "event_id": event.get("id"),
        "empty_field": j["empty_field"],
        "verdicts": j["verdicts"],
        "landed": paths,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="A/B 联赛成对晋升判据执行器（league judge）")
    ap.add_argument("--check-rulers", action="store_true", help="只解析判据尺状态打印（不判不写）")
    ap.add_argument("--judge", action="store_true", help="整场判定+判定书落档")
    ap.add_argument("--month", type=str, default=None, help="判定书月份戳 YYYY-MM（默认当前月）")
    ap.add_argument("--registry", type=str, default=None, help="联赛注册表路径")
    ap.add_argument("--standards", type=str, default=str(STANDARDS_PATH), help="标准库路径")
    ap.add_argument("--out-dir", type=str, default=None, help="判定书落档目录")
    ap.add_argument("--dry-run", action="store_true", help="只打印不落盘")
    ap.add_argument(
        "--register-first",
        type=str,
        default=None,
        metavar="GROUP",
        help="首位参赛者：sim 现役首个真策略入指定组（禁编造，空场=不写诚实退出）",
    )
    ap.add_argument(
        "--strategy-registry",
        type=str,
        default=str(STRATEGY_REGISTRY_PATH),
        help="策略注册表路径（配 --register-first）",
    )
    args = ap.parse_args()

    if args.check_rulers:
        rulers = resolve_rulers(load_standards(args.standards))
        print(
            json.dumps(
                {
                    "access_std_id": "STD-SIM-ACCESS-002",
                    "access_status": rulers["v2"].get("status"),
                    "switch_std_id": "STD-SWITCH-001",
                    "switch_status": rulers["switch"].get("status"),
                    "pair_decision_engine": rulers["pair_engine"],
                    "family_scope": rulers["family_scope"],
                    "correlation_gate_rho": rulers["rho_max"],
                    "draft_ruler": rulers["draft_ruler"],
                },
                ensure_ascii=False,
            )
        )
        return 0

    if args.register_first:
        sid = pick_first_sim_contestant(args.strategy_registry)
        if not sid:
            print(
                json.dumps(
                    {
                        "ok": True,
                        "empty_field": True,
                        "registered": None,
                        "note": "sim 现役为空=诚实空场，未写注册表；留待首个自然 advisory",
                    },
                    ensure_ascii=False,
                )
            )
            return 0
        reg_path = Path(args.registry) if args.registry else LEAGUE_REGISTRY_PATH
        group = lr.register_member(args.register_first, sid, path=reg_path)
        print(
            json.dumps(
                {
                    "ok": True,
                    "empty_field": False,
                    "registered": sid,
                    "group": group.get("group_id"),
                    "members": group.get("members"),
                },
                ensure_ascii=False,
            )
        )
        return 0

    # 默认=--judge（整场判定）
    j = run_judgment(args.registry, args.standards)
    if args.dry_run:
        print(render_markdown(j))
        return 0
    paths = land_judgment(j, args.out_dir, stamp=args.month)
    print(
        json.dumps(
            {
                "ok": True,
                "empty_field": j["empty_field"],
                "verdicts": j["verdicts"],
                "suggestions": len(j["suggestions"]),
                "landed": paths,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
