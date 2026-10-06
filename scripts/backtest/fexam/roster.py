# [BLUEPRINT] MOD-BT-FEXAM | docs/_working/matrix_campaign/90_execution_log.md | 批0 BT-P0 应考名单机生器
# [MODULE] scripts.backtest.fexam.roster
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.fexam.ch_data; yaml
# [CONSUMERS] ic_exam.py; strategy_exam.py; allocator_shadow.py; campaign_report.py
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 名单全部来自册（零手工挑题=S3铁律）；计数用字段（entry_count/per_bucket）禁散文；
#              可考性预分类机判（outputs列→CH表解析）；prereg窗口与及格线在本模块冻结，考试器禁改；
#              registry_expected 记录施工单旧数并标注漂移（175→实/139→实），禁硬编码断言
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 任一册缺失/结构非法 → RegistryError 上抛（fail-closed）
# [TESTS] tests/backtest/fexam/test_roster.py
# [MODIFY-GUARD] docs/_working/matrix_campaign/90_execution_log.md（prereg冻结口径改动=重考全部批次）
# [TTL] permanent
# create-guard-not-dup: 四册应考名单机生器（独立能力：registry→roster），命中文档校验类能力无交集
"""roster — 批0：四册→BT-P0 应考名单（机生，禁手工挑）。

对象来源册（真源指针随行）：
- 策略 = docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml
- 因子 = docs/01_policies_and_standards/_registry/catalogs/factor_registry.yaml
- 指标 = docs/01_policies_and_standards/_registry/catalogs/technical_indicator_registry.yaml
- 分配器 = 5 套（三层栈 RK-08+PA-015+SIG-131 组合；challenger=等权平均/单算法简化版×2，
  模块锚 src/zephyr/pf_alloc/ + risk_budget_allocator + MOD-PA-015 + _domain_signal/signal_weight_adjuster）
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

RUN_ROOT = Path(__file__).resolve().parents[3]
_SRC = RUN_ROOT / "src"
for _p in (str(RUN_ROOT / "scripts" / "backtest" / "fexam"), str(_SRC)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import ch_data  # noqa: E402 — 同簇兄弟模块（path 注入后平铺导入）

CATALOGS = RUN_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"
FACTOR_REGISTRY = CATALOGS / "factor_registry.yaml"
INDICATOR_REGISTRY = CATALOGS / "technical_indicator_registry.yaml"
STRATEGY_REGISTRY = CATALOGS / "strategy_registry.yaml"

#: 施工单旧数（BT-P0 工单口径）——仅用于漂移披露，禁作断言
WORK_ORDER_EXPECTED = {"strategy": 161, "factor": 175, "indicator": 139, "allocator": 5}

#: prereg v1 冻结口径（与 ch_data.WINDOW_* 同源；考试器禁止改窗）
PREREG_V1: dict[str, Any] = {
    "windows": {
        "holdout_exam": {
            "start": ch_data.WINDOW_HOLDOUT[0],
            "end": ch_data.WINDOW_HOLDOUT[1],
            "note": "近12月干净窗，选样窗与考试窗分离",
        },
        "is_ref_decay": {
            "start": ch_data.WINDOW_IS_REF[0],
            "end": ch_data.WINDOW_IS_REF[1],
            "note": "衰减参照窗，与考试窗不交",
        },
    },
    "horizons": [1, 5, 20],
    "headline_horizon": 5,
    "factor_pass_line": {
        "abs_ic_min": 0.02,
        "icir_min": 0.3,
        "ic_retain_min": 0.5,
        "note": "初拟待Owner校（施工单§2口径）",
    },
    "indicator_pass_line": {
        "abs_ic_5d_min": 0.02,
        "regime_check": "report_only",
        "note": "IC及格线同因子；regime_valid声明核对只报告不判死",
    },
    "strategy_pass_line": {
        "oos_sharpe_min": 0.0,
        "is_sharpe_min": 0.0,
        "oos_maxdd_max": 0.30,
        "activation_weight_band": {"floor": 0, "current": 0.1, "ceiling": 0.3, "step_cap": 0.2},
        "note": "初拟待Owner校",
    },
    "strategy_device": {
        "engine": "DefaultBacktestEngine(MOD-BT-001)",
        "execution_lag_days": 1,
        "exclude_st": True,
        "pit_filter": True,
        "top_n": 20,
        "rebalance": "monthly",
        "weighting": "equal",
        "single_run_split": "一次连续跑，nav按窗分段（IS/OOS同源同参数）",
    },
    "device_policy": "IC考试=CPU pandas（spearman秩相关无GPU核，逐条可解释degrade）；"
    "批2整装=vectorized_engine CPU逐日（c4 GPU引擎为网格考专属，"
    "批2单跑非网格不适用0.53s/格口径）；degrade台账随册",
    "regime_key": "c1_backtest.regime_snapshot_history HMM四态argmax；<2019-04用SMA200 fallback",
    "lookahead_note": "因子/指标册 last_updated=2026-09 晚于考试窗——registry 本身含前视风险，"
    "本考为存量清点口径（verdict 只证明窗内表现，不证明可上线），上线另走晋升门",
}

ALLOCATORS: list[dict[str, Any]] = [
    {
        "allocator_id": "ALC-THREELAYER-001",
        "name": "three_layer_stack",
        "name_zh": "三层栈(RK-08地板+PA-015倾斜+SIG-131运动学组合)",
        "module_refs": [
            "src/zephyr/pf_alloc/core/risk_budget_allocator(经 risk/core)",
            "MOD-PA-015 regime_bma_weighting",
            "SIG-131 signal_weight_adjuster",
        ],
        "variant": "champion_combo",
    },
    {
        "allocator_id": "ALC-EQUAL-001",
        "name": "equal_weight",
        "name_zh": "等权平均(challenger)",
        "module_refs": [],
        "variant": "challenger",
    },
    {
        "allocator_id": "ALC-RK08-001",
        "name": "rk08_solo",
        "name_zh": "RK-08风险预算单走(简化版)",
        "module_refs": ["src/zephyr/pf_alloc(risk/core/risk_budget)"],
        "variant": "challenger_simplified",
    },
    {
        "allocator_id": "ALC-PA015-001",
        "name": "pa015_solo",
        "name_zh": "PA-015体制倾斜单走(简化版)",
        "module_refs": ["MOD-PA-015 regime_bma_weighting"],
        "variant": "challenger_simplified",
    },
    {
        "allocator_id": "ALC-SIG131-001",
        "name": "sig131_solo",
        "name_zh": "SIG-131权重钳制单走(简化版)",
        "module_refs": ["_domain_signal/signal_weight_adjuster"],
        "variant": "challenger_simplified",
    },
]


class RegistryError(RuntimeError):
    """册缺失/结构非法（路径走 details 不进消息——MSG-EXPOSURE 处方）。"""

    def __init__(self, msg: str, details: dict | None = None) -> None:
        super().__init__(msg)
        self.details = details or {}


def _load_entries(path: Path, *, id_field: str) -> list[dict[str, Any]]:
    if not path.exists():
        raise RegistryError("册不存在（path 见 details）", {"path": str(path)})
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    entries = None
    if isinstance(doc, dict):
        for key in ("entries", id_field.removesuffix("_id") + "s", id_field):
            if isinstance(doc.get(key), list):
                entries = doc[key]
                break
        if entries is None:  # 兜底：扫描全部列表值，取首个以 id_field 为键的字典列表
            for v in doc.values():
                if isinstance(v, list) and v and isinstance(v[0], dict) and id_field in v[0]:
                    entries = v
                    break
    elif isinstance(doc, list):
        entries = doc
    if not isinstance(entries, list):
        raise RegistryError(f"册结构非法（找不到条目列表键 entries/{id_field}s，path 见 details）", {"path": str(path)})
    out = []
    for e in entries:
        if isinstance(e, dict) and e.get(id_field):
            out.append(e)
    return out


def classify_factor_outputs(
    entries: list[dict[str, Any]], *, cache: dict[str, set[str]] | None = None
) -> list[dict[str, Any]]:
    """因子可考性预分类：ch_backed（outputs列可解析）/ code_backed（quantized有码无列）/ non_quantified。"""
    cache = cache if cache is not None else {}
    out = []
    for e in entries:
        outputs = e.get("outputs") or []
        resolved = ch_data.resolve_output_columns(outputs, cache=cache)
        if resolved:
            bucket, backings = "ch_backed", [f"{t}.{c}" for t, c in resolved]
        elif e.get("code_symbol") or (e.get("code_path") and e.get("algorithm_status") == "quantized"):
            bucket, backings = "code_backed", []
        else:
            bucket, backings = "non_quantified", []
        out.append(
            {
                "object_id": e["factor_id"],
                "source_registry": str(FACTOR_REGISTRY.relative_to(RUN_ROOT)).replace("\\", "/"),
                "bucket": bucket,
                "ch_backings": backings,
                "factor_class": e.get("factor_class"),
                "algorithm_status": e.get("algorithm_status"),
                "regime_valid": e.get("regime_valid") or [],
                "status": e.get("status"),
            }
        )
    return out


def classify_indicators(
    entries: list[dict[str, Any]], *, cache: dict[str, set[str]] | None = None
) -> list[dict[str, Any]]:
    """指标可考性预分类：全部应考；outputs列解析到 technical_indicator 表。"""
    cache = cache if cache is not None else {}
    out = []
    for e in entries:
        outputs = e.get("outputs") or []
        resolved = ch_data.resolve_output_columns(outputs, cache=cache)
        out.append(
            {
                "object_id": e["indicator_id"],
                "source_registry": str(INDICATOR_REGISTRY.relative_to(RUN_ROOT)).replace("\\", "/"),
                "bucket": "ch_backed" if resolved else "col_missing",
                "ch_backings": [f"{t}.{c}" for t, c in resolved],
                "indicator_class": e.get("indicator_class"),
                "regime_valid": e.get("regime_valid") or [],
                "regime_invalid": e.get("regime_invalid") or [],
                "status": e.get("status"),
            }
        )
    return out


def classify_strategies(entries: list[dict[str, Any]], factor_map: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """策略可考性预分类：harness_examinable（≥1个alpha_source可解析到ch_backed因子）/ non_quantified。

    harness 口径（prereg 冻结）：策略考=其 alpha_sources 等权合成在标准装置
    （top20/月频/等权/引擎PIT+剔ST+T+1）上的表现，非其全部定制逻辑。
    """
    out = []
    for e in entries:
        alpha = [a for a in (e.get("alpha_sources") or []) if isinstance(a, str)]
        backed = [a for a in alpha if factor_map.get(a, {}).get("bucket") == "ch_backed"]
        missing = {
            "alpha_sources_empty": not alpha,
            "universe_id_missing": not e.get("universe_id"),
            "cost_model_id_missing": not e.get("cost_model_id"),
        }
        if backed:
            bucket = "harness_examinable"
        elif e.get("code_path"):
            bucket = "code_backed"  # 有代码锚但通用harness无法实例化逐策略定制代码
        else:
            bucket = "non_quantified"
        out.append(
            {
                "object_id": e["strategy_id"],
                "source_registry": str(STRATEGY_REGISTRY.relative_to(RUN_ROOT)).replace("\\", "/"),
                "bucket": bucket,
                "alpha_sources": alpha,
                "backed_alpha_sources": backed,
                "missing_recipe_flags": [k for k, v in missing.items() if v],
                "lifecycle_status": e.get("lifecycle_status"),
                "status": e.get("status"),
                "distilled_to_code": bool(e.get("distilled_to_code")),
            }
        )
    return out


def build_roster() -> dict[str, Any]:
    """批0主入口：四册解析+分类+计数对平。返回 roster 文档结构（含 prereg 冻结块）。"""
    factors_raw = _load_entries(FACTOR_REGISTRY, id_field="factor_id")
    indicators_raw = _load_entries(INDICATOR_REGISTRY, id_field="indicator_id")
    strategies_raw = _load_entries(STRATEGY_REGISTRY, id_field="strategy_id")

    cache: dict[str, set[str]] = {}
    factors = classify_factor_outputs(factors_raw, cache=cache)
    indicators = classify_indicators(indicators_raw, cache=cache)
    factor_map = {f["object_id"]: f for f in factors}
    strategies = classify_strategies(strategies_raw, factor_map)
    allocators = [dict(a, bucket="prereg_fixed", source_registry="inline_prereg_ALLOCATORS") for a in ALLOCATORS]

    def _counts(items: list[dict[str, Any]]) -> dict[str, int]:
        c: dict[str, int] = {"total": len(items)}
        for it in items:
            c[it["bucket"]] = c.get(it["bucket"], 0) + 1
        return c

    roster: dict[str, Any] = {
        "doc_type": "fexam_bt_p0_roster",
        "version": "v1",
        "generated_note": "机生（scripts/backtest/fexam/roster.py build_roster）禁手工挑题；S3铁律",
        "prereg_v1": PREREG_V1,
        "counts": {
            "factor": _counts(factors),
            "indicator": _counts(indicators),
            "strategy": _counts(strategies),
            "allocator": _counts(allocators),
        },
        "work_order_expected_drift": {
            "note": "施工单写死计数 vs 本次机生实测（册为活文档，以机生实测为准）",
            "expected": WORK_ORDER_EXPECTED,
            "actual": {
                "strategy": len(strategies),
                "factor": len(factors),
                "indicator": len(indicators),
                "allocator": len(allocators),
            },
        },
        "factor": factors,
        "indicator": indicators,
        "strategy": strategies,
        "allocator": allocators,
    }
    return roster


def write_roster(path: Path) -> dict[str, Any]:
    from zephyr.shared.io.file_utils import safe_write_text

    roster = build_roster()
    path.parent.mkdir(parents=True, exist_ok=True)
    safe_write_text(path, yaml.safe_dump(roster, allow_unicode=True, sort_keys=False, width=120))
    return roster
