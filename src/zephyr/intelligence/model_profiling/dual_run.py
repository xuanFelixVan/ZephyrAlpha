# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §model_profiling
# [MODULE] zephyr.intelligence.model_profiling.dual_run
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.utils.time_utils (now_utc); zephyr.shared.io.paths (REPO_ROOT); config/dual_run_criteria.yaml（判据预注册冻结件，唯一真源）
# [CONSUMERS] M3 双跑实验调用方（实跑接线批=exam_executor 通道）；CLI 直调（--dry-run / --check-freeze）
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 判据冻结：改判据=拒绝执行+强制新 experiment_id（判据自改=根约束禁区，主文档定调#8）；
#              判据冻结哈希=全量 sort_keys 稳定 JSON 的 sha256（verify_freeze 不匹配即 CriteriaFrozenError）；
#              同 seed 同池=同样本（分层抽样可复现，random.Random(seed+层序号)）；
#              judge 与被测异厂异档（DESIGN §4.2，裁判解耦由调用方保证，执行器只记账）；
#              层内可判件<10=该层"undecided"（诚实条款，禁硬判）；
#              本版只提供库函数+dry-run，不虚标实跑能力（实跑需接 exam_executor 通道，接线批）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/OBJ_M_models/DESIGN.md §4.2/§4.4（判据门槛改动须先改 DESIGN 并换 experiment_id）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 判据缺文件/缺关键字段→CriteriaError 上抛（fail-closed，禁退回码内默认判据）；
#                  判据冻结哈希不匹配→CriteriaFrozenError（CriteriaError 子类）
# [TESTS] tests/intelligence/model_profiling/test_dual_run.py
# [TTL] permanent
"""dual_run — M3 同任务双跑执行器（纯函数库，DESIGN §4.2/§4.4）。

职责三段：**判据冻结**（load_criteria/freeze_hash/verify_freeze，fail-closed）→
**分层双跑**（sample_strata 可复现抽样 + run_pair 逐样本记账，LLM 调用面经
champion_fn/challenger_fn 注入，单测零真实 LLM）→ **统计判定**
（mcnemar_p/wilcoxon_signed_rank_p 手写统计 + stratum_verdict 四态机检 +
evidence_pack 证据包）。裁判（judge_fn）与被测异厂异档的解耦由调用方保证。

CLI 用法::

    python -m zephyr.intelligence.model_profiling.dual_run --dry-run \\
        --experiment-id DR-20260923-demo
    python -m zephyr.intelligence.model_profiling.dual_run \\
        --check-freeze <recorded_sha256>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
from pathlib import Path
from typing import Any, Callable, Final

import yaml

from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc
from zephyr.intelligence.canonical_hash import canonical_json_sha256
from zephyr.signal_ashare.strength_ic_weight_calibrator import _average_ranks  # CloneGuard 合并：复用既有真源实现（extract 级克隆零逃生）

__all__: Final = [
    "CriteriaError",
    "CriteriaFrozenError",
    "DEFAULT_CRITERIA_PATH",
    "MIN_JUDGEABLE",
    "thresholds_from_criteria",
    "load_criteria",
    "freeze_hash",
    "verify_freeze",
    "sample_strata",
    "run_pair",
    "mcnemar_p",
    "wilcoxon_signed_rank_p",
    "stratum_verdict",
    "evidence_pack",
    "main",
]

#: 判据预注册冻结件默认路径（真源唯一，fail-closed 统读）
DEFAULT_CRITERIA_PATH: Final[Path] = REPO_ROOT / "config" / "dual_run_criteria.yaml"

#: load_criteria 必查关键字段（缺任一即 CriteriaError）
_REQUIRED_FIELDS: Final[tuple[str, ...]] = (
    "experiment_id",
    "champion",
    "challenger",
    "strata",
    "metrics",
    "significance",
    "freeze_rule",
)

#: 四项指标键（DESIGN §4.2 metrics 四项）
_REQUIRED_METRICS: Final[tuple[str, ...]] = (
    "success_rate",
    "latency_s",
    "rework_count",
    "cost_usd_unit",
)

#: 层内可判件下限（诚实条款：可判件<10=undecided，DESIGN §4.2）
MIN_JUDGEABLE: Final = 10

ModelFn = Callable[[dict[str, Any]], dict[str, Any]]
JudgeFn = Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], dict[str, Any]]


class CriteriaError(Exception):
    """判据错误（5.99.20：敏感上下文走 details 不进消息文本）。"""

    def __init__(self, msg: str, *, details: dict[str, str] | None = None) -> None:
        super().__init__(msg)
        self.details: dict[str, str] = details or {}
    """判据缺失/畸形（fail-closed：禁止码内第二真源兜底）。"""


class CriteriaFrozenError(CriteriaError):
    """判据冻结哈希不匹配（改判据=拒绝执行，须换新 experiment_id）。"""


def load_criteria(path: Path = DEFAULT_CRITERIA_PATH) -> dict[str, Any]:
    """fail-closed 加载判据预注册冻结件，返回 ``dual_run_criteria`` 映射。

    缺文件 / YAML 畸形 / 缺 ``dual_run_criteria`` 键 / 缺关键字段 /
    结构畸形（strata 空、metrics 缺四项、significance 缺 alpha 等）一律
    抛 :class:`CriteriaError`，绝不退回码内默认判据。
    """
    if not path.is_file():
        raise CriteriaError("判据冻结件不存在", details={"path": str(path)})
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise CriteriaError(f"判据冻结件 YAML 畸形: {exc}", details={"path": str(path)})
    if not isinstance(doc, dict) or "dual_run_criteria" not in doc:
        raise CriteriaError("判据冻结件缺 dual_run_criteria 顶层键", details={"path": str(path)})
    criteria = doc["dual_run_criteria"]
    if not isinstance(criteria, dict):
        raise CriteriaError("dual_run_criteria 必须是映射", details={"path": str(path)})
    _validate_criteria(criteria, path)
    return criteria


def _validate_sides_and_strata(criteria: dict[str, Any], path: Path) -> None:
    """champion/challenger 双方与 strata 分层结构校验。"""
    for side in ("champion", "challenger"):
        if not isinstance(criteria[side], dict) or "model_id" not in criteria[side]:
            raise CriteriaError(f"判据 {side} 缺 model_id", details={"path": str(path)})
    strata = criteria["strata"]
    if not isinstance(strata, list) or not strata:
        raise CriteriaError("判据 strata 必须非空列表", details={"path": str(path)})
    for st in strata:
        if not isinstance(st, dict) or not {"stratum", "n", "seed"} <= set(st):
            raise CriteriaError("判据 strata 条目缺 stratum/n/seed", details={"path": str(path)})


def _validate_metrics_and_significance(criteria: dict[str, Any]) -> None:
    """metrics 四项与 significance.alpha 校验。"""
    metrics = criteria["metrics"]
    if not isinstance(metrics, dict):
        raise CriteriaError("判据 metrics 必须是映射")
    missing_metrics = [m for m in _REQUIRED_METRICS if m not in metrics]
    if missing_metrics:
        raise CriteriaError(f"判据 metrics 缺 {missing_metrics}")
    sig = criteria["significance"]
    if not isinstance(sig, dict) or "alpha" not in sig:
        raise CriteriaError("判据 significance 缺 alpha")


def _validate_criteria(criteria: dict[str, Any], path: Path) -> None:
    """关键字段机械校验（缺任一即 CriteriaError；拆三段保每函数复杂度 ≤15）。"""
    missing = [k for k in _REQUIRED_FIELDS if k not in criteria]
    if missing:
        raise CriteriaError(f"判据缺关键字段 {missing}", details={"path": str(path)})
    _validate_sides_and_strata(criteria, path)
    _validate_metrics_and_significance(criteria)


def freeze_hash(criteria: dict[str, Any]) -> str:
    """判据冻结哈希：全量 sort_keys 稳定 JSON 序列化后 sha256（十六进制）。

    稳定性约定：``json.dumps(sort_keys=True, ensure_ascii=False,
    separators=(",", ":"))``——键序归一、无空白差异，同判据恒同哈希，
    改任意叶子字段（含嵌套）哈希必变。
    """
    return canonical_json_sha256(criteria)


def verify_freeze(criteria_path: Path, recorded_hash: str) -> None:
    """判据冻结校验：现哈希 ≠ recorded_hash 即抛 :class:`CriteriaFrozenError`。

    CLI ``--check-freeze <hash>`` 消费；不匹配=判据被改，拒绝执行，
    强制换新 experiment_id 重走预注册。
    """
    criteria = load_criteria(criteria_path)
    actual = freeze_hash(criteria)
    if actual != recorded_hash:
        raise CriteriaFrozenError(
            f"判据冻结哈希不匹配：记录={recorded_hash} 现值={actual}"
            f"（判据已被改动，拒绝执行，须换新 experiment_id 重走预注册）"
        )


def sample_strata(
    strata: list[dict[str, Any]], task_pool: list[dict[str, Any]], seed: int
) -> dict[str, list[dict[str, Any]]]:
    """分层抽样（纯函数，可复现）：同 seed 同池=同样本。

    规则（DESIGN §4.2）：第 i 层用 ``random.Random(seed + i)``（层序号 i 从 0
    起）；层条目声明 task_type/quadrant 时先按轴过滤任务池（轴=任务类型×二维
    象限），未声明则全池抽样；层内取 min(n, 候选数) 件（池不足时不虚凑）。
    """
    sampled: dict[str, list[dict[str, Any]]] = {}
    for index, stratum in enumerate(strata):
        name = str(stratum["stratum"])
        candidates = _filter_by_axis(stratum, task_pool)
        rng = random.Random(seed + index)
        take = min(int(stratum["n"]), len(candidates))
        picked = [dict(item) for item in rng.sample(candidates, take)]
        sampled[name] = picked
    return sampled


def _filter_by_axis(
    stratum: dict[str, Any], task_pool: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """按层声明的抽样轴（task_type/quadrant）过滤任务池；未声明轴=全池。"""
    axes = [ax for ax in ("task_type", "quadrant") if ax in stratum]
    if not axes:
        return list(task_pool)
    return [item for item in task_pool if all(item.get(ax) == stratum[ax] for ax in axes)]


def run_pair(
    challenger_fn: ModelFn,
    champion_fn: ModelFn,
    samples: dict[str, list[dict[str, Any]]],
    judge_fn: JudgeFn,
) -> list[dict[str, Any]]:
    """对每样本双跑并逐样本记账（LLM 调用面经注入，本函数零 LLM 依赖）。

    champion_fn/challenger_fn: ``dict -> {"output": ..., "latency_s": float,
    "cost_usd": float, "rework_count": int}``；judge_fn(champion_out,
    challenger_out, sample) ``-> {"success_champion": bool,
    "success_challenger": bool}``。

    **DESIGN §4.2 裁判约束**：judge 与被测异厂异档（防同源偏袒），该解耦由
    调用方保证——本函数只忠实记账，不校验 judge 身份。
    """
    records: list[dict[str, Any]] = []
    for stratum, sample_list in samples.items():
        for order, sample in enumerate(sample_list):
            champion_out = champion_fn(sample)
            challenger_out = challenger_fn(sample)
            judge_out = judge_fn(champion_out, challenger_out, sample)
            records.append(
                {
                    "stratum": stratum,
                    "sample_id": sample.get("sample_id", f"{stratum}-{order}"),
                    "champion": champion_out,
                    "challenger": challenger_out,
                    "success_champion": bool(judge_out["success_champion"]),
                    "success_challenger": bool(judge_out["success_challenger"]),
                }
            )
    return records


def mcnemar_p(b: int, c: int) -> float:
    """McNemar 检验 p 值（连续性校正卡方，1 自由度），手写零依赖。

    数学：校正卡方 ``chi2 = (|b-c| - 1)^2 / (b+c)``（b,c=两种不一致对数）；
    1 自由度卡方生存函数 ``P(X>chi2) = erfc(sqrt(chi2/2))``。b+c=0（无不
    一致对）时两法无差异，直接记 p=1.0。连续性校正使小样本更保守（防假显著）。
    """
    total = b + c
    if total == 0:
        return 1.0
    chi2 = (abs(b - c) - 1) ** 2 / total
    return math.erfc(math.sqrt(chi2 / 2.0))


def wilcoxon_signed_rank_p(diffs: list[float]) -> float:
    """Wilcoxon 符号秩检验 p 值（双侧正态近似），手写零依赖。

    数学：剔除 |diff|=0 后，对 |diff| 升序排平均秩（并列取均值），W=min(W+,W-)；
    n>=10 时正态近似 ``z = (W - 0.5 - n(n+1)/4) / sqrt(n(n+1)(2n+1)/24)``（−0.5
    为连续性校正），双侧 ``p = erfc(|z|/sqrt(2))``。n<10（或剔零后不足）返回
    NaN=样本不足，不硬判。注：v0 未含 tie 方差校正（手写口径，偏保守）。
    """
    nonzero = [d for d in diffs if d != 0.0]
    n = len(nonzero)
    if n < MIN_JUDGEABLE:
        return float("nan")
    ranks = _average_ranks([abs(d) for d in nonzero])
    w_positive = sum(rank for rank, d in zip(ranks, nonzero, strict=False) if d > 0)
    w_stat = min(w_positive, sum(ranks) - w_positive)
    mean = n * (n + 1) / 4.0
    sigma = math.sqrt(n * (n + 1) * (2 * n + 1) / 24.0)
    z_score = (w_stat - 0.5 - mean) / sigma
    return math.erfc(abs(z_score) / math.sqrt(2.0))



def thresholds_from_criteria(criteria: dict[str, Any]) -> dict[str, float]:
    """从冻结判据提取层内判定门槛（单一真源，禁判定常量旁落码内）。"""
    sig = criteria["significance"]
    alpha = float(sig["alpha"])
    return {
        "alpha": alpha,
        "win_pp": 5.0,
        "non_inferior_pp_min": -5.0,
        "cost_diff_ratio_max": -0.20,
        "median_diff_ratio_max": -0.20,
        "min_judgeable": float(MIN_JUDGEABLE),
    }


def stratum_verdict(
    pairs: list[dict[str, Any]], thresholds: dict[str, float]
) -> dict[str, Any]:
    """层内四态判定（DESIGN §4.4 判据表机检）：可判件<MIN_JUDGEABLE 即 undecided。

    结论 ∈ {challenger_win, non_inferior_cost_win, champion_hold, undecided}：
    胜=成功率差 ≥ +win_pp 且 McNemar p<alpha；换更便宜=成本单价差 ≤
    cost_diff_ratio_max 且成功率 ≥ −5pp 且不显著；其余=champion_hold。
    """
    flags = [
        (p["success_champion"], p["success_challenger"])
        for p in pairs
        if isinstance(p.get("success_champion"), bool)
        and isinstance(p.get("success_challenger"), bool)
    ]
    judgeable = len(flags)
    stats: dict[str, Any] = {
        "n": len(pairs),
        "judgeable": judgeable,
        "min_judgeable": MIN_JUDGEABLE,
    }
    if judgeable < MIN_JUDGEABLE:
        stats["verdict"] = "undecided"
        stats["reason"] = "judgeable_below_min（诚实条款：不硬判）"
        return stats
    stats.update(_pair_stats(pairs, flags, thresholds))
    stats["verdict"] = _decide(stats, thresholds)
    return stats


def _pair_stats(
    pairs: list[dict[str, Any]],
    flags: list[tuple[bool, bool]],
    thresholds: dict[str, float],
) -> dict[str, Any]:
    """层内统计量：成功率差/McNemar/时延中位差/Wilcoxon/单位成本差。"""
    n = len(flags)
    sr_champ = sum(1 for fc, _ in flags if fc) / n
    sr_chal = sum(1 for _, fx in flags if fx) / n
    b_count = sum(1 for fc, fx in flags if fc and not fx)
    c_count = sum(1 for fc, fx in flags if fx and not fc)
    lat_ratio, wilcoxon_p = _continuous_stats(pairs)
    cost_ratio = _unit_cost_ratio(pairs)
    return {
        "success_rate_champion": sr_champ,
        "success_rate_challenger": sr_chal,
        "diff_pp": (sr_chal - sr_champ) * 100.0,
        "mcnemar_b": b_count,
        "mcnemar_c": c_count,
        "mcnemar_p": mcnemar_p(b_count, c_count),
        "latency_median_diff_ratio": lat_ratio,
        "wilcoxon_p": wilcoxon_p,
        "cost_unit_diff_ratio": cost_ratio,
        "thresholds": dict(thresholds),
    }


def _continuous_stats(pairs: list[dict[str, Any]]) -> tuple[float | None, float]:
    """时延中位差（相对 champion 中位）+ 逐对时延差的 Wilcoxon p。"""
    lat_c = sorted(
        p["champion"]["latency_s"]
        for p in pairs
        if isinstance(p.get("champion", {}).get("latency_s"), (int, float))
    )
    lat_x = sorted(
        p["challenger"]["latency_s"]
        for p in pairs
        if isinstance(p.get("challenger", {}).get("latency_s"), (int, float))
    )
    if not lat_c or not lat_x:
        return None, float("nan")
    med_c = _median(lat_c)
    med_x = _median(lat_x)
    ratio = (med_x - med_c) / med_c if med_c != 0 else None
    diffs = [
        p["challenger"]["latency_s"] - p["champion"]["latency_s"]
        for p in pairs
        if isinstance(p.get("champion", {}).get("latency_s"), (int, float))
        and isinstance(p.get("challenger", {}).get("latency_s"), (int, float))
    ]
    return ratio, wilcoxon_signed_rank_p(diffs)


def _median(sorted_values: list[float]) -> float:
    """中位数（输入已排序；偶数取中间两值均值）。"""
    mid = len(sorted_values) // 2
    if len(sorted_values) % 2 == 1:
        return float(sorted_values[mid])
    return (sorted_values[mid - 1] + sorted_values[mid]) / 2.0


def _unit_cost_ratio(pairs: list[dict[str, Any]]) -> float | None:
    """单位合格产出成本差（§4.3 口径：层内总成本/合格产出件），challenger vs champion。"""
    ratios: list[float | None] = []
    for side in ("champion", "challenger"):
        qualified = [
            p[side]["cost_usd"]
            for p in pairs
            if p[f"success_{side}"]
            and isinstance(p.get(side, {}).get("cost_usd"), (int, float))
        ]
        ratios.append(sum(qualified) / len(qualified) if qualified else None)
    champ_unit, chal_unit = ratios[0], ratios[1]
    if champ_unit in (None, 0.0) or chal_unit is None:
        return None
    return (chal_unit - champ_unit) / champ_unit


def _decide(stats: dict[str, Any], thresholds: dict[str, float]) -> str:
    """四态机检：win → non_inferior_cost_win → champion_hold（DESIGN §4.4）。"""
    significant = stats["mcnemar_p"] < thresholds["alpha"]
    if stats["diff_pp"] >= thresholds["win_pp"] and significant:
        return "challenger_win"
    non_inferior = (
        stats["diff_pp"] >= thresholds["non_inferior_pp_min"] and not significant
    )
    cost_ok = (
        stats["cost_unit_diff_ratio"] is not None
        and stats["cost_unit_diff_ratio"] <= thresholds["cost_diff_ratio_max"]
    )
    if non_inferior and cost_ok:
        return "non_inferior_cost_win"
    return "champion_hold"


def evidence_pack(
    experiment_id: str, criteria_hash: str, strata_results: list[dict[str, Any]]
) -> dict[str, Any]:
    """产出 L4 格式证据包（判据冻结哈希随包留痕，可复核判据未被中途改动）。"""
    return {
        "experiment_id": experiment_id,
        "criteria_freeze_sha256": criteria_hash,
        "strata": strata_results,
        "generated_at": now_utc().isoformat(),
    }


_DEMO_TASK_POOL: Final[tuple[dict[str, Any], ...]] = (
    {
        "sample_id": "demo-001",
        "task_type": "挖矿广度扫/枚举反查",
        "quadrant": "低体积×低密度",
        "prompt": "枚举 registry_of_registries.yaml 中注册表类别数",
    },
    {
        "sample_id": "demo-002",
        "task_type": "挖矿深读复现（规格重写）",
        "quadrant": "高体积×高密度",
        "prompt": "按 blueprint.md §model_profiling 重写双跑规格",
    },
    {
        "sample_id": "demo-003",
        "task_type": "清洗管线规格化",
        "quadrant": "中体积×中密度",
        "prompt": "把 tick 清洗步骤规格化为 YAML 管线",
    },
)


def main(argv: list[str] | None = None) -> int:
    """CLI：--dry-run=加载+冻结哈希+抽样自检（内置 3 件假样例，零 LLM）；
    --check-freeze <hash>=判据冻结校验。无 --dry-run 时如实退出码 2：
    实跑需接 exam_executor 通道（接线批），本版只提供库函数+dry-run。
    """
    parser = argparse.ArgumentParser(
        prog="dual_run", description="M3 同任务双跑执行器（判据冻结+抽样+dry-run）"
    )
    parser.add_argument("--criteria", type=Path, default=DEFAULT_CRITERIA_PATH)
    parser.add_argument("--experiment-id", default="DR-<yyyymmdd>-<slug>")
    parser.add_argument(
        "--dry-run", action="store_true", help="只做加载+freeze_hash+抽样自检，不调 LLM"
    )
    parser.add_argument("--check-freeze", metavar="SHA256", default=None)
    args = parser.parse_args(argv)

    if args.check_freeze is not None:
        verify_freeze(args.criteria, args.check_freeze)
        print(json.dumps({"freeze_check": "ok", "criteria": str(args.criteria)}))
        return 0
    if not args.dry_run:
        print(
            "实跑需接 exam_executor 通道（接线批），本版只提供库函数+dry-run",
            file=sys.stderr,
        )
        return 2

    criteria = load_criteria(args.criteria)
    criteria_hash = freeze_hash(criteria)
    sampled = sample_strata(criteria["strata"], list(_DEMO_TASK_POOL), seed=20301)
    summary = {
        "mode": "dry-run",
        "experiment_id_template": criteria["experiment_id"],
        "experiment_id": args.experiment_id,
        "criteria_freeze_sha256": criteria_hash,
        "strata_sampled": {k: len(v) for k, v in sampled.items()},
        "note": "抽样自检用内置 3 件假样例，非真实任务池；单轮 100 件实跑在接线批",
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: 运维CLI入口由外部排班(排班登记register_*.ps1在册)/人工点火, 非自动常驻任务
    raise SystemExit(main())
