# [BLUEPRINT] MOD-BT-FEXAM | docs/_working/matrix_campaign/90_execution_log.md | 网格考配置发射器（策略族→subspace配置）
# [MODULE] scripts.backtest.fexam.grid_adapter.emit_configs.py
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] 见文件内 import
# [CONSUMERS] run_fexam.py 或手工 CLI
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] staging 转正件；判定面不入核
# [MODIFY-GUARD] docs/_working/matrix_campaign/90_execution_log.md
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 见 docstring
# [TESTS] tests/backtest/fexam/
# [TTL] task_bound
# create-guard-not-dup: tmp 24h TTL 抢救转正件（Owner 批 P0-1），对拍结论已锁定随文件
# -*- coding: utf-8 -*-
"""F道·配置发射器：策略考 CPU→GPU 网格适配（st-matrix-20261006 / F lane）。

把 roster（docs/_working/fexam/bt_p0_roster_v1.yaml）harness_examinable/backed 策略
翻译成 factory_grid_executor 可消费的 subspace-json 序列（--subspace-json 内联 JSON，
dict[合法轴名]→[合法取值列表]，笛卡尔过滤语义=factory_grid_executor.run_batch L1270-1272）。

口径（诚实声明）：
- 装置翻译真源=roster prereg_v1.strategy_device（top20/月频/等权/剔ST/PIT/T+1），
  逐键映射到 schema（config/position_recipe_grid_schema.yaml）合法轴——禁造轴名。
- 网格引擎信号面板=注册列（v1: f_mom20/f_lowvol20/f_ma_gap；v1_value 增 f_ep/f_bp/f_np_yoy），
  无"信号列选择轴"——策略族在网格上的可考面=装置级（与 CPU 考 harness 口径一致：
  "策略考=alpha_sources 等权合成在标准装置上的表现，非其全部定制逻辑"）。
  strategy_class→factor_surface 翻译表为适配器声明（待 Owner 校），非冻结件。
- 网格不可表达类（timing/event/rule 类入场逻辑，非截面排名合成）如实列为
  not_grid_expressible，禁造凑数（S3 铁律）。
- subspace-json 文件只含纯轴→取值 dict（多余键会毒化过滤：未知键→全格点被滤掉）；
  家族元数据（覆盖策略/指标列/合法性依据）一律进 sidecar .meta.yaml。

产出（全部落本目录 grid_configs/）：
  <family>.subspace.json  纯 subspace（执行器 --subspace-json 消费面）
  <family>.meta.yaml      元数据 sidecar（禁被执行器消费）
  fire_plan.yaml          点火计划（fire_grid.py 消费面）
  emit_summary.json       发射计数汇总

用法：
  python emit_configs.py                # 发射+自校验（只读消费既有文件，零 DB）
  python emit_configs.py --out-dir X    # 自定义输出目录（默认脚本同目录 grid_configs/）
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parents[3]  # .runtime/tmp/st-matrix-20261006/grid_adapter -> repo root
sys.path.insert(0, str(_REPO / "src"))
_BT = _REPO / "scripts" / "backtest"
sys.path.insert(0, str(_BT / "translated"))
sys.path.insert(0, str(_BT))

ROSTER_PATH = _REPO / "docs" / "_working" / "fexam" / "bt_p0_roster_v1.yaml"
STRATEGY_REGISTRY_PATH = (
    _REPO / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "strategy_registry.yaml"
)
SCHEMA_PATH = _REPO / "config" / "position_recipe_grid_schema.yaml"
PREREG_PATHS = (_REPO / "config" / "search_space_prereg.yaml", _REPO / "config" / "search_space_prereg_t3a.yaml")

#: 装置→网格轴翻译表（roster prereg_v1.strategy_device 键 → schema 轴=取值）。
#: 值含函数的项从 roster 动态解析；其余=口径常量（依据见注释）。
DEVICE_STATIC_PINS = {
    # harness 口径（roster.py classify_strategies docstring，prereg 冻结）：alpha_sources 等权合成
    "A2_combine_weight": ["equal"],
    # 月频日历调仓 → periodic（drift_band 是另一族触发语义，非本装置）
    "D2_rebalance_trigger": ["periodic"],
    # CPU harness 无换手惩罚 → lambda_0
    "H_turnover_lambda": ["lambda_0"],
}

#: strategy_class → 网格因子面（适配器声明翻译表，待 Owner 校；非冻结件）。
#: 网格信号面板注册列：v1={f_mom20,f_lowvol20,f_ma_gap}；v1_value=+{f_ep,f_bp,f_np_yoy}。
GRID_EXPRESSIBLE_CLASS_SURFACE = {
    "value_reversal": "v1_value",  # 价值/反转 → 估值列族（f_ep/f_bp/f_np_yoy）
    "momentum_trend": "v1",  # 动量/趋势 → f_mom20/f_ma_gap
    "multifactor": "v1",  # 多因子合成 → 注册列等权合成本体
}
NOT_GRID_EXPRESSIBLE_REASON = (
    "入场逻辑=择时/事件/规则类（非截面排名列合成），网格信号面板（注册列排名-合成语义）不可表达——"
    "如实排除禁凑数；定制回测=L级另行登记（harness 口径同源）"
)

# fire 计划里 std_device 的价值面补跑行（value_reversal 族唯一网格投影）


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"[emit] 真源缺失（fail-closed）: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_schema_axes() -> tuple[dict[str, list[str]], dict]:
    """schema 合法轴→取值域（禁造轴名的唯一判据）。"""
    schema = _load_yaml(SCHEMA_PATH)
    axes: dict[str, list[str]] = {}
    for dim in schema.get("dimensions") or []:
        axes[dim["id"]] = [str(v) for v in dim.get("values") or []]
    return axes, schema


def select_backed_strategies(roster: dict) -> tuple[list[dict], list[dict]]:
    """roster → (backed 策略明细[并注册表 strategy_class/指标列], 网格不可表达清单)。"""
    sreg = _load_yaml(STRATEGY_REGISTRY_PATH)
    rmap = {e.get("strategy_id"): e for e in (sreg.get("strategies") or [])}
    backed, not_expressible = [], []
    for s in roster.get("strategy") or []:
        if s.get("bucket") not in ("harness_examinable", "code_backed"):
            continue
        e = rmap.get(s.get("object_id"), {}) or {}
        cls = e.get("strategy_class") or "UNKNOWN"
        item = {
            "object_id": s.get("object_id"),
            "bucket": s.get("bucket"),
            "strategy_class": cls,
            "backed_alpha_sources": list(s.get("backed_alpha_sources") or []),
            "alpha_sources": list(s.get("alpha_sources") or []),
            "distilled_to_code": bool(s.get("distilled_to_code")),
            "code_path": e.get("code_path") or "",
        }
        if cls in GRID_EXPRESSIBLE_CLASS_SURFACE:
            item["grid_factor_surface"] = GRID_EXPRESSIBLE_CLASS_SURFACE[cls]
            backed.append(item)
        else:
            item["reason"] = NOT_GRID_EXPRESSIBLE_REASON
            not_expressible.append(item)
    return backed, not_expressible


def device_base_pins(roster: dict, axes: dict[str, list[str]]) -> dict[str, list[str]]:
    """roster prereg strategy_device → 标准装置轴钉（全部轴名/取值过 schema 合法性校验）。"""
    dev = (roster.get("prereg_v1") or {}).get("strategy_device") or {}
    pins: dict[str, list[str]] = {}
    # top_n: 20 → B_top_n=top20（schema 值命名法）
    b = f"top{int(dev.get('top_n', 20))}"
    pins["B_top_n"] = [b]
    # rebalance: monthly → D1_rebalance_freq
    pins["D1_rebalance_freq"] = [str(dev.get("rebalance", "monthly"))]
    # weighting: equal → C_sizing=equal_weight（harness 等权）
    pins["C_sizing"] = ["equal_weight"]
    # exclude_st: true → G_universe=all_a_ex_st（引擎冻结土规 filter_st 同口径）
    pins["G_universe"] = ["all_a_ex_st"]
    pins.update(DEVICE_STATIC_PINS)
    _check_pins(pins, axes)
    return pins


def _check_pins(pins: dict[str, list[str]], axes: dict[str, list[str]]) -> None:
    for axis, values in pins.items():
        if axis not in axes:
            raise SystemExit(f"[emit] 造轴名拦截: {axis!r} 非 schema 合法轴（合法={sorted(axes)}）")
        bad = [v for v in values if v not in axes[axis]]
        if bad:
            raise SystemExit(f"[emit] 造取值拦截: {axis}={bad} 非 schema 合法值（合法={axes[axis]}）")
        if not values:
            raise SystemExit(f"[emit] 空取值集: {axis}")


def build_family_configs(roster: dict, axes: dict[str, list[str]]) -> list[dict]:
    """发射序列：标准装置区 + 4 个装置族带（轴名/取值全部 schema/prereg 合法）。"""
    base = device_base_pins(roster, axes)
    prereg = _load_yaml(PREREG_PATHS[0])
    ffa = ((prereg.get("tracks") or {}).get("f06_grid") or {}).get("fact_family_axes") or {}
    win = ((roster.get("prereg_v1") or {}).get("windows") or {}).get("holdout_exam") or {}

    def cfg(name: str, extra: dict[str, list[str]], basis: str) -> dict:
        pins = dict(base)
        pins.update(extra)
        _check_pins(pins, axes)  # extra 也禁造轴名/取值
        return {"name": name, "subspace": {k: sorted(v) for k, v in sorted(pins.items())}, "basis": basis}

    configs = [
        cfg(
            "std_device",
            {},
            "roster prereg_v1.strategy_device 全钉（harness 装置 1:1 网格投影）；自由轴=A1_factor_normalize/E_single_cap",
        ),
        cfg(
            "b_topn_band",
            {"B_top_n": [str(v) for v in ffa.get("B_top_n") or ["top10", "top20", "top30"]]},
            "prereg tracks.f06_grid.fact_family_axes.B_top_n（批E-① 拉长持有期预注册轴）×标准装置",
        ),
        cfg(
            "d1_freq_band",
            {"D1_rebalance_freq": [str(v) for v in ffa.get("D1_rebalance_freq") or ["weekly", "biweekly", "monthly"]]},
            "prereg tracks.f06_grid.fact_family_axes.D1_rebalance_freq（批E-①）×标准装置",
        ),
        cfg(
            "g_universe_band",
            {"G_universe": list(axes["G_universe"])},
            "schema G_universe 全值域（跨池稳健带）×标准装置",
        ),
        cfg(
            "a2_composite_band",
            {"A2_combine_weight": list(axes["A2_combine_weight"])},
            "schema A2_combine_weight 全值域（等权指标列族→合成权重族带，T2a 精确实现面）×标准装置",
        ),
    ]
    for c in configs:
        c["window"] = {"start": win.get("start"), "end": win.get("end")}
    return configs


def count_cells(subspace: dict) -> int:
    """GridCompiler 只读编译+执行器同语义过滤计数（禁 DB/禁 GPU——compile 是纯笛卡尔展开）。"""
    from zephyr.position.core.position_recipe_compiler import GridCompiler

    compiler = GridCompiler.from_yaml(str(SCHEMA_PATH))
    expansion = compiler.compile({"strategy_pool": ["primary"], "phase": 1, "capital_ramp_enabled": False})
    recipes = list(expansion.recipes)
    return sum(1 for r in recipes if all(r.values.get(k) in vs for k, vs in subspace.items()))


def main() -> int:
    ap = argparse.ArgumentParser(description="F道 配置发射器：roster→网格 subspace-json 序列")
    ap.add_argument("--out-dir", default=str(_HERE / "grid_configs"))
    args = ap.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    roster = _load_yaml(ROSTER_PATH)
    axes, _schema = load_schema_axes()
    backed, not_expressible = select_backed_strategies(roster)
    configs = build_family_configs(roster, axes)

    surfaces = sorted({s["grid_factor_surface"] for s in backed})
    plan_rows = []
    written = []
    for c in configs:
        cells = count_cells(c["subspace"])
        if cells <= 0:
            raise SystemExit(f"[emit] {c['name']} 过滤后 0 格点（轴/值非法或空域）——禁发射")
        jpath = out_dir / f"{c['name']}.subspace.json"
        jpath.write_text(
            json.dumps(c["subspace"], ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        meta = {
            "family": c["name"],
            "basis": c["basis"],
            "window": c["window"],
            "expected_cells": cells,
            "subspace_file": jpath.name,
            "legal_axis_source": [str(p.name) for p in PREREG_PATHS] + [SCHEMA_PATH.name],
            "device_translation": {
                "roster_prereg_strategy_device": (roster.get("prereg_v1") or {}).get("strategy_device"),
                "pins": c["subspace"],
                "note": "top20/月频/等权/剔ST→B_top20/D1_monthly/C_equal_weight/G_all_a_ex_st；A2=equal=等权指标列合成",
            },
            "covered_strategies": backed,
            "not_grid_expressible": not_expressible,
        }
        mpath = out_dir / f"{c['name']}.meta.yaml"
        mpath.write_text(yaml.safe_dump(meta, allow_unicode=True, sort_keys=False), encoding="utf-8")
        written += [jpath.name, mpath.name]
        # fire 计划行：std_device 按族面拆两行（v1=动量/多因子投影，v1_value=价值族唯一投影）
        plan_surfaces = surfaces if c["name"] == "std_device" else ["v1"]
        for sf in plan_surfaces:
            plan_rows.append(
                {
                    "row_id": f"{c['name']}@{sf}",
                    "config": c["name"],
                    "subspace_file": jpath.name,
                    "factor_surface": sf,
                    "n_samples": cells,
                    "stage": "",
                    "start": c["window"]["start"],
                    "end": c["window"]["end"],
                    "covered_classes": sorted({s["strategy_class"] for s in backed if s["grid_factor_surface"] == sf})
                    if c["name"] == "std_device"
                    else sorted({s["strategy_class"] for s in backed}),
                }
            )
    plan = {
        "doc_type": "grid_adapter_fire_plan",
        "lane": "F-st-matrix-20261006",
        "ignition_policy": "今晚禁点火（st-t3series 占卡 ETA 23:30）；fire_grid.py 默认 dry-run，点火需 GPU 空闲门通过+显式旗标",
        "rows": plan_rows,
    }
    ppath = out_dir / "fire_plan.yaml"
    ppath.write_text(yaml.safe_dump(plan, allow_unicode=True, sort_keys=False), encoding="utf-8")
    summary = {
        "emitted_configs": len(configs),
        "plan_rows": len(plan_rows),
        "total_cells": sum(r["n_samples"] for r in plan_rows),
        "backed_strategies": len(backed),
        "not_grid_expressible": len(not_expressible),
        "files": written + [ppath.name],
    }
    spath = out_dir / "emit_summary.json"
    spath.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
