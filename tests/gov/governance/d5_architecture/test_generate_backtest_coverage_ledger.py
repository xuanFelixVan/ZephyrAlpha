# [MODULE] tests.governance.d5_architecture.test_generate_backtest_coverage_ledger
# [DOMAIN] D_GOV_SCRIPTS
# [MODIFY-GUARD] none（只读校验/生成器红绿测试，全部夹具构造于 tmp_path，不碰生产路径与 data/）
# [DEPENDENCIES] pytest; yaml;
#   scripts.governance.d5_architecture.generators.generate_backtest_coverage_ledger
# [CONSUMERS] 回测覆盖总册生成器质量守卫（缺真源必须报错不静默；同输入两次产出逐字节等）；
#   真源计数断言守卫（A16/B26/C118/D22=182 口径漂移必红）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 红组=缺任一真源 CoverageLedgerError 且消息含路径 / 计数断言失败报错 / F6R 锚缺失报错 /
#   active_if 未知形态报错（fail-closed 禁猜测）；绿组=夹具渲染形态逐键断言 + 幂等逐字节等 +
#   --check 漂移检出 + 真仓产物与派生一致（generated_at/as_of 易变面除外）；
#   测试隔离：输出一律 tmp_path fixture，禁写 data/（宪法 §9.6）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=TEST-MOD-GOVERNANCE-TEST_GENERATE_BACKTEST_COVERAGE_LEDGER | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""回测覆盖总册生成器红绿测试：fixtures 断言渲染形态 + 缺真源报错不静默。

红组（每种真源破坏必须被点名报出）：
  缺 H9 挖矿文档 / 缺 F6R 执行日志 / 缺 F6R 锚行 / 缺 grid schema / 缺 prereg /
  缺考场证据根 / 缺 trial ledger / 四类计数和不等于 182 / S 级缺口表行数与声明不符 /
  DEFAULT_CONTEXT 赋值行缺失 / active_if 未知表达式（fail-closed 禁猜测）。
绿组（渲染形态逐键钉死）：
  顶层键 / 七层金字塔逐层（automation 枚举、automation_evidence、gate、covered/uncovered）/
  13 维逐维（phase1 激活态、t1/t2 覆盖、缺口三态：折叠/部分/全含）/
  trial_summary 双口径（registry 累计+grid 普查分列）/ consumers 四消费方 /
  幂等（同 as-of 两次逐字节等）/ --check 漂移检出与 CLEAN。
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest
import yaml

_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / "scripts" / "governance" / "d5_architecture" / "generators"))

import generate_backtest_coverage_ledger as gen  # noqa: E402

_AS_OF = "2026-10-06T00:00:00+08:00"


# ─────────────────────────── 夹具构造 ───────────────────────────

_MINING_DOC = """# T3 挖矿（夹具）

## 0. 一页结论

| 判定 | 计数 | 占比 |
|---|---|---|
| A. 引擎已实现且可考 | **2** | 1.1% |
| B. 引擎有接口但考卷未开 | **1** | 0.5% |
| C. 引擎无实现=缺口 | **175** | 96.2% |
| D. 非回测域（盘前运维/治理/台账，天然不进回测） | **4** | 2.2% |

- 分层：**T3a（S 级接线，纯向量化）→ T3b（M 级模块补写，耗时口径须重标定）→ T3c（L 级子系统，回测只考日级可表达子集）**。

## 2. 缺口清单

### S 级（接线即可考，估计 2 项）

| # | 缺口（TDM 节点） | 接线内容 | 复用资产 |
|---|---|---|---|
| S1 | L1 总闸 | J 开闸 | switcher |
| S2 | L4-02 时序 | open 口径 | load_px |

### M 级（模块补写，估计 1 项）

| # | 缺口（TDM 节点） | 补写内容 | 备注 |
|---|---|---|---|
| M1 | X-S1-02 止损族 | ATR 带 | 样板在册 |

### L 级（新子系统，估计 1 项）

| # | 缺口（TDM 节点带） | 子系统 | 备注 |
|---|---|---|---|
| L1 | P2 做T全链 | tick 考卷 | 框架在册 |
"""

_EXEC_LOG = """## 10-05 深夜 Owner 方法论问询→H11 发车（回测覆盖总册）
- 裁定：建机生账本不建新图……（七层金字塔逐层：自动化态/已考/未考/缺口）+CASEBOOK 册号登记+图书馆入口。
"""

_GRID_SCHEMA = """schema_id: position_recipe_grid_v2
dimensions:
  - id: A1_factor_normalize
    desc: 因子标准化
    values: [raw, rank, zscore]
    baseline: zscore
  - id: F_merge_policy
    desc: 多策略合并
    values: [single, equal_capital]
    baseline: single
    active_if: "len(strategy_pool) > 1"
  - id: J_regime_switch
    desc: regime 开关
    values: [off, on]
    baseline: off
    active_if: "phase >= 2"
  - id: K_capital_ramp
    desc: 建仓节奏
    values: [lump, pyramid]
    baseline: lump
    active_if: "capital_ramp_enabled"
  - id: I_cost_tier
    desc: 成本假设档（恒折叠）
    values: [frozen_l0, frozen_l1]
    baseline: frozen_l0
    active_if: "False"
"""

_EXECUTOR = """DEFAULT_CONTEXT = {"strategy_pool": ["primary"], "phase": 1, "capital_ramp_enabled": False}
"""

_PREREG = """frozen_at: '2026-09-24T22:00:00+08:00'
budget_caps:
  trial0_calibration_points: 200
  tier1_points: 3700
  tier2_points: 900
"""

_TRIAL_REGISTRY = """schema_version: 1.0.0
counting_rule: count = screen_runs.total_trials + sum(batch_records.n_trials)
manual_population: 0
screen_runs:
  total_trials: 269
  total_runs: 25
  last_synced_at: '2026-09-15T05:43:43+00:00'
batch_records:
- batch_id: grid_x
  n_trials: 31
"""


def _make_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    for rel in (gen._MINING_DOC, gen._EXEC_LOG, gen._GRID_SCHEMA, gen._PREREG, gen._TRIAL_REGISTRY, gen._EXECUTOR):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
    (root / gen._MINING_DOC).write_text(_MINING_DOC, encoding="utf-8")
    (root / gen._EXEC_LOG).write_text(_EXEC_LOG, encoding="utf-8")
    (root / gen._GRID_SCHEMA).write_text(_GRID_SCHEMA, encoding="utf-8")
    (root / gen._PREREG).write_text(_PREREG, encoding="utf-8")
    (root / gen._TRIAL_REGISTRY).write_text(_TRIAL_REGISTRY, encoding="utf-8")
    (root / gen._EXECUTOR).write_text(_EXECUTOR, encoding="utf-8")
    return root


def _make_run(root: Path, run_id: str, *, mode: str, n_sampled: int, evaluated: int) -> Path:
    d = root / "data/strategy_intake" / run_id
    d.mkdir(parents=True, exist_ok=True)
    (d / "summary.json").write_text(
        f'{{"run_ts": "{run_id}", "mode": "{mode}", "n_sampled": {n_sampled}, "evaluated": {evaluated}}}',
        encoding="utf-8",
    )
    return d


def _make_t1_handover(root: Path) -> None:
    d = _make_run(root, "grid_20260926-024947", mode="batch_a_census", n_sampled=3700, evaluated=3700)
    (d / "t2_subspace.json").write_text('{"A1_factor_normalize": ["rank"], "J_regime_switch": []}', encoding="utf-8")
    (d / "t2_subspace_meta.yaml").write_text(
        "generated_by: scripts/backtest/t1_t2_handover.py\nexpected_points: 24\n", encoding="utf-8"
    )
    (d / "handover_verdict.yaml").write_text(
        "criteria:\n  points:\n    pass: true\n  dead_zero:\n    pass: true\n", encoding="utf-8"
    )


# ─────────────────────────── 绿组 ───────────────────────────


def test_green_render_shape_on_fixtures(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    _make_run(root, "grid_20260924-080309", mode="batch_a_census", n_sampled=200, evaluated=200)
    _make_run(root, "grid_20260915-051517", mode="smoke", n_sampled=8, evaluated=6)
    _make_run(root, "grid_20260929-040003", mode="batch_b_subspace", n_sampled=4, evaluated=0)
    _make_run(root, "grid_20261005-215457", mode="batch_b_subspace", n_sampled=24, evaluated=24)
    _make_t1_handover(root)

    doc = gen.build_document(as_of=_AS_OF, root=root)

    # 顶层键
    for key in ("schema_version", "generated_at", "as_of", "pyramid", "factory_dims", "trial_summary", "consumers"):
        assert key in doc, f"缺顶层键 {key}"
    assert doc["generated_at"] == _AS_OF
    assert doc["as_of"] == _AS_OF[:10]

    # 金字塔：七层逐层
    assert [p["layer"] for p in doc["pyramid"]] == [
        "data_validation",
        "factor_unit_test",
        "strategy_grid",
        "tdm_module_replay",
        "stage_integration",
        "prereg_acceptance",
        "integrated",
    ]
    automations = {p["layer"]: p["automation"] for p in doc["pyramid"]}
    assert automations == {
        "data_validation": "full",
        "factor_unit_test": "full",
        "strategy_grid": "semi",
        "tdm_module_replay": "manual",
        "stage_integration": "manual",
        "prereg_acceptance": "semi",
        "integrated": "semi",
    }
    for p in doc["pyramid"]:
        assert p["automation_evidence"], f"{p['layer']} 缺 automation_evidence（F6R 溯源）"
        assert "gate" in p and "covered_tests" in p and "uncovered_gaps" in p
    grid = next(p for p in doc["pyramid"] if p["layer"] == "strategy_grid")
    grid_refs = {c["ref"] for c in grid["covered_tests"]}
    assert "grid_20260924-080309" in grid_refs and "grid_20260926-024947" in grid_refs
    assert all(not r.startswith("grid_20260915-051517") for r in grid_refs), "smoke run 不得计入已考"
    prereg_layer = next(p for p in doc["pyramid"] if p["layer"] == "prereg_acceptance")
    hv = next(c for c in prereg_layer["covered_tests"] if c["kind"] == "handover_verdict")
    assert hv["status"] == "pass" and hv["run"] == "grid_20260926-024947"

    # 计数（夹具口径 2/1/175/4=182）
    assert doc["counts"]["tdm_nodes"] == {
        "total": 182,
        "a_tested": 2,
        "b_interface_not_opened": 1,
        "c_gap": 175,
        "d_non_backtest": 4,
    }
    assert doc["counts"]["gap_work"] == {"S": 2, "M": 1, "L": 1}
    assert doc["counts"]["pyramid_layers"] == 7
    assert doc["counts"]["factory_dims_total"] == 5

    # 13 维逐维（夹具 5 维）：激活/折叠/恒折叠/子空间缺口三态
    dims = {d["dim"]: d for d in doc["factory_dims"]}
    assert dims["A1_factor_normalize"]["phase1_active"] is True
    assert dims["A1_factor_normalize"]["t1_examined"] is True
    assert dims["A1_factor_normalize"]["t2_subspace"] == ["rank"]
    assert "1/3" in dims["A1_factor_normalize"]["gap"]
    assert dims["F_merge_policy"]["phase1_active"] is False
    assert "B 类有接口未开考" in dims["F_merge_policy"]["gap"]
    assert dims["I_cost_tier"]["gap"].startswith("恒折叠（设计边界非缺口）")
    assert dims["J_regime_switch"]["t1_examined"] is False
    assert dims["K_capital_ramp"]["t2_subspace"] == []

    # trial_summary 双口径分列
    t = doc["trial_summary"]["n_trial_ledger"]
    assert t["cumulative_count"] == 269 + 31
    assert t["screen_runs_total_trials"] == 269
    gc = doc["trial_summary"]["grid_census"]
    assert gc["runs_scanned"] == 5
    assert gc["total_evaluated"] == 200 + 6 + 0 + 24 + 3700
    assert gc["by_stage"]["t0_calibration"] == ["grid_20260924-080309"]
    assert gc["by_stage"]["t1_coarse"] == ["grid_20260926-024947"]
    assert gc["by_stage"]["smoke"] == ["grid_20260915-051517"]
    assert gc["t2_main_candidates"] == ["grid_20261005-215457"]
    assert "在跑/待判定" in gc["t2_main_note"]

    assert doc["consumers"] == ["晨报", "发车闸", "晋级池", "图书馆查询"]


def test_green_idempotent_and_check(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    _make_t1_handover(root)
    text1 = gen.render(gen.build_document(as_of=_AS_OF, root=root))
    text2 = gen.render(gen.build_document(as_of=_AS_OF, root=root))
    assert hashlib.sha256(text1.encode()).hexdigest() == hashlib.sha256(text2.encode()).hexdigest(), (
        "同输入两次产出不逐字节等=非幂等事故"
    )
    out = root / gen._OUT_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text1, encoding="utf-8")
    assert gen.main(["--check", "--root", str(root), "--as-of", _AS_OF]) == 0
    drifted = text1.replace("回测覆盖总册", "回测覆盖总册（被手改）")
    out.write_text(drifted, encoding="utf-8")
    assert gen.main(["--check", "--root", str(root), "--as-of", _AS_OF]) == 1


# ─────────────────────────── 红组：缺真源/结构漂移必报错 ───────────────────────────


def test_red_missing_mining_doc(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    (root / gen._MINING_DOC).unlink()
    with pytest.raises(gen.CoverageLedgerError, match="t3_fullflow_exam_mining"):
        gen.build_document(as_of=_AS_OF, root=root)


def test_red_missing_exec_log_and_anchors(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    (root / gen._EXEC_LOG).unlink()
    with pytest.raises(gen.CoverageLedgerError, match="90_execution_log"):
        gen.build_document(as_of=_AS_OF, root=root)
    (root / gen._EXEC_LOG).write_text("无锚行内容\n", encoding="utf-8")
    with pytest.raises(gen.CoverageLedgerError, match="F6R 锚行"):
        gen.build_document(as_of=_AS_OF, root=root)


def test_red_counts_sum_not_182(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    bad = _MINING_DOC.replace("| **175** |", "| **174** |")
    (root / gen._MINING_DOC).write_text(bad, encoding="utf-8")
    with pytest.raises(gen.CoverageLedgerError, match="182"):
        gen.build_document(as_of=_AS_OF, root=root)


def test_red_gap_section_row_count_mismatch(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    bad = _MINING_DOC.replace("估计 2 项", "估计 3 项", 1)
    (root / gen._MINING_DOC).write_text(bad, encoding="utf-8")
    with pytest.raises(gen.CoverageLedgerError, match="S 级缺口表行数"):
        gen.build_document(as_of=_AS_OF, root=root)


def test_red_missing_grid_schema_or_prereg_or_intake_or_registry(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    _make_run(root, "grid_20260924-080309", mode="batch_a_census", n_sampled=200, evaluated=200)
    content_by_path = {gen._GRID_SCHEMA: _GRID_SCHEMA, gen._PREREG: _PREREG, gen._TRIAL_REGISTRY: _TRIAL_REGISTRY}
    for target, match in (
        (gen._GRID_SCHEMA, "position_recipe_grid_schema"),
        (gen._PREREG, "search_space_prereg"),
        (gen._TRIAL_REGISTRY, "trial_ledger_registry"),
    ):
        (root / target).unlink()
        with pytest.raises(gen.CoverageLedgerError, match=match):
            gen.build_document(as_of=_AS_OF, root=root)
        (root / target).write_text(content_by_path[target], encoding="utf-8")
    import shutil

    shutil.rmtree(root / "data/strategy_intake")
    with pytest.raises(gen.CoverageLedgerError, match="strategy_intake"):
        gen.build_document(as_of=_AS_OF, root=root)


def test_red_default_context_missing(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    (root / gen._EXECUTOR).write_text("OTHER = 1\n", encoding="utf-8")
    with pytest.raises(gen.CoverageLedgerError, match="DEFAULT_CONTEXT"):
        gen.build_document(as_of=_AS_OF, root=root)


def test_red_unknown_active_if_fails_closed(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    bad = _GRID_SCHEMA.replace('active_if: "phase >= 2"', 'active_if: "mood == good"')
    (root / gen._GRID_SCHEMA).write_text(bad, encoding="utf-8")
    with pytest.raises(gen.CoverageLedgerError, match="未知形态"):
        gen.build_document(as_of=_AS_OF, root=root)


def test_red_timeban_source_guard() -> None:
    """RULE-SCHEMA-TZ：生成器禁 datetime.now()/time.time()（时间戳必经入参/HEAD 派生）。"""
    src = Path(gen.__file__).read_text(encoding="utf-8")
    assert "datetime.now()" not in src, "生成器出现 datetime.now()（违反取时禁令）"
    assert "time.time()" not in src, "生成器出现 time.time()（违反取时禁令）"


def test_green_real_repo_ledger_consistent() -> None:
    """真仓绿组：真实产物与三真源派生一致（--check 退出码 0；易变面 generated_at/as_of 已豁免）。"""
    import subprocess

    r = subprocess.run(
        [
            sys.executable,
            str(_REPO / "scripts/governance/d5_architecture/generators/generate_backtest_coverage_ledger.py"),
            "--check",
        ],
        capture_output=True,
        text=True,
        cwd=str(_REPO),
    )
    assert r.returncode == 0, f"真仓账本与三真源漂移：{r.stdout}{r.stderr}"
