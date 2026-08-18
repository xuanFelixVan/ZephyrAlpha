# [BLUEPRINT] SH-GOV-001 | scripts/governance/oneoff/
# [MODULE] scripts.governance.oneoff.factor_design_state_complete
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] apply_depgraph.py; zephyr.infrastructure
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] oneoff
# [INVARIANTS] 因子工厂全景设计态补全：补全 subdomain_id + 删反向边 + 新增域内依赖边 + GATE 分类；depgraph 修改通过 apply_depgraph.py 受控函数（铁律）
# [MODIFY-GUARD] none
# [STABILITY] ephemeral
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] dry-run->退出码0; 执行成功->退出码0; depgraph不可达->退出码2; 部分失败->退出码1
# [TESTS] python scripts/governance/oneoff/factor_design_state_complete.py --dry-run
# [TTL] permanent
"""因子工厂全景设计态补全——一次性执行脚本。

执行计划 Step 1-4：
  Step 1: 补全 50 个节点的 subdomain_id（扁平分组，FAC-CORE/ASHARE/ANALYSIS/GOV/BARRA/MINE）
  Step 2: 删除 2 条反向 barra 设计态边（risk_model→exposure / exposure→risk_budget 方向错误）
  Step 3: 新增 43 条域内设计态依赖边（from=依赖方, to=被依赖方, dep_maturity=design）
  Step 4: GATE 分类——依赖型已转边（GATE-11/24/105），安全约束/数据可用型→gate_reason 注解

机制（遵守"depgraph 修改必须用 apply_depgraph.py"铁律）：
  - subdomain_id / gate_reason：_load_depgraph() 改 dep dict → _atomic_write() 全量 UPDATE 写回
  - 边删除/新增：delete_edge() / add_edge()（apply_depgraph.py 受控函数）

用法：
  python scripts/governance/oneoff/factor_design_state_complete.py --dry-run   # 预览
  python scripts/governance/oneoff/factor_design_state_complete.py              # 执行
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 因子工厂全景设计态补全——一次性执行脚本。
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]  # oneoff -> governance -> scripts -> repo_root
_GOVERNANCE_DIR = _REPO_ROOT / "scripts" / "governance"
for _p in (str(_REPO_ROOT), str(_GOVERNANCE_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from apply_depgraph import (  # noqa: E402
    _load_depgraph,
    _atomic_write,
    add_edge,
    delete_edge,
)

# ============================================================
# Step 1 数据：path 前缀 → subdomain_id 映射（扁平分组，不建子域节点）
# ============================================================
SUBDOMAIN_BY_PREFIX: list[tuple[str, str]] = [
    ("src/zephyr/factor/core/", "FAC-CORE"),
    ("src/zephyr/factor/ashare/", "FAC-ASHARE"),
    ("src/zephyr/factor/analysis/", "FAC-ANALYSIS"),
    ("src/zephyr/factor/governance/", "FAC-GOV"),
    ("src/zephyr/factor/barra/", "FAC-BARRA"),
    ("src/zephyr/factor/mine/", "FAC-MINE"),
]

# file 粒度节点单独指定（不带子目录前缀）
SUBDOMAIN_BY_FILE: dict[str, str] = {
    "src/zephyr/factor/factor_base.py": "FAC-CORE",            # Engine+Registry 载体
    "src/zephyr/factor/alpha_signal_pipeline.py": "FAC-CORE",  # Pipeline 载体
    "src/zephyr/factor/bus_factor_defense.py": "FAC-CORE",     # 保命防御
    "src/zephyr/factor/momentum_factor.py": "FAC-ASHARE",      # A股动量因子
    "src/zephyr/factor/value_factor.py": "FAC-ASHARE",         # A股价值因子
}

# ============================================================
# Step 2 数据：待删除的反向边 edge_id
# ============================================================
EDGES_TO_DELETE: list[int] = [
    8831509,  # barra/risk_model → exposure_calculator（反向，应为 exposure→risk_model）
    8831510,  # barra/exposure_calculator → risk_budget_allocator（反向，应为 risk_budget→exposure）
]

# ============================================================
# Step 3 数据：新增域内设计态边（from=依赖方 → to=被依赖方）
# ============================================================
FACTOR_BASE = "src/zephyr/factor/factor_base.py"
PIPELINE = "src/zephyr/factor/alpha_signal_pipeline.py"

EDGES_TO_ADD: list[tuple[str, str, str]] = [
    # A. Engine(factor_base) 相关（5）—— 各组件依赖 Engine 基类
    ("src/zephyr/factor/core/ctr001_consumer/", FACTOR_BASE, "F76→F01"),
    ("src/zephyr/factor/core/ctr002_producer/", FACTOR_BASE, "F01→F77 Producer依赖Engine基类"),
    ("src/zephyr/factor/core/evaluation/", FACTOR_BASE, "F03 Evaluation依赖FactorBase"),
    (PIPELINE, FACTOR_BASE, "F04 Pipeline依赖F01"),
    ("src/zephyr/factor/core/dist_feature_eng/", FACTOR_BASE, "F105→F01 (GATE-105-01依赖部分)"),
    # B. FAC-ASHARE 子模块 → Engine（14）
    ("src/zephyr/factor/ashare/capital_flow/", FACTOR_BASE, "FAC_ASHARE→F01"),
    ("src/zephyr/factor/ashare/microstructure/", FACTOR_BASE, "FAC_ASHARE→F01"),
    ("src/zephyr/factor/ashare/fundamental/", FACTOR_BASE, "FAC_ASHARE→F01"),
    ("src/zephyr/factor/ashare/intraday/", FACTOR_BASE, "FAC_ASHARE→F01"),
    ("src/zephyr/factor/ashare/smc/", FACTOR_BASE, "FAC_ASHARE→F01"),
    ("src/zephyr/factor/ashare/irl/", FACTOR_BASE, "FAC_ASHARE→F01"),
    ("src/zephyr/factor/ashare/alpha87/", FACTOR_BASE, "FAC_ASHARE→F01"),
    ("src/zephyr/factor/ashare/technical_indicator/", FACTOR_BASE, "FAC_ASHARE→F01"),
    ("src/zephyr/factor/ashare/pattern_signal/", FACTOR_BASE, "FAC_ASHARE→F01"),
    ("src/zephyr/factor/ashare/market_structure/", FACTOR_BASE, "FAC_ASHARE→F01"),
    ("src/zephyr/factor/ashare/sector/", FACTOR_BASE, "FAC_ASHARE→F01"),
    ("src/zephyr/factor/ashare/institutional/", FACTOR_BASE, "FAC_ASHARE→F01"),
    ("src/zephyr/factor/ashare/cross_market/", FACTOR_BASE, "FAC_ASHARE→F01"),
    ("src/zephyr/factor/ashare/ps_liquidity/", FACTOR_BASE, "FAC_ASHARE→F01"),
    # C. FAC-BARRA 子模块 → Engine（4）
    ("src/zephyr/factor/barra/risk_model/", FACTOR_BASE, "FAC_BARRA→F01"),
    ("src/zephyr/factor/barra/esg/", FACTOR_BASE, "FAC_BARRA→F01"),
    ("src/zephyr/factor/barra/exposure_calculator/", FACTOR_BASE, "FAC_BARRA→F01"),
    ("src/zephyr/factor/barra/risk_budget_allocator/", FACTOR_BASE, "FAC_BARRA→F01"),
    # D. FAC-MINE → Engine + Evaluation（3）
    ("src/zephyr/factor/mine/mining_agent/", FACTOR_BASE, "FAC_MINE→F01"),
    ("src/zephyr/factor/mine/causal_validator/", FACTOR_BASE, "FAC_MINE→F01"),
    ("src/zephyr/factor/mine/mining_agent/", "src/zephyr/factor/core/evaluation/", "FAC_MINE→F03 挖掘因子需评估验证"),
    # E. FAC-ANALYSIS 子模块 → Engine（11）
    ("src/zephyr/factor/analysis/ic_ir_evaluator/", FACTOR_BASE, "F01→FAC_ANALYSIS"),
    ("src/zephyr/factor/analysis/ic_ir_calc/", FACTOR_BASE, "F01→FAC_ANALYSIS"),
    ("src/zephyr/factor/analysis/three_level_judgment/", FACTOR_BASE, "F01→FAC_ANALYSIS"),
    ("src/zephyr/factor/analysis/layered_backtest/", FACTOR_BASE, "F01→FAC_ANALYSIS"),
    ("src/zephyr/factor/analysis/ic_decay/", FACTOR_BASE, "F01→FAC_ANALYSIS"),
    ("src/zephyr/factor/analysis/multifactor_synthesis/", FACTOR_BASE, "F01→FAC_ANALYSIS"),
    ("src/zephyr/factor/analysis/correlation_dedup/", FACTOR_BASE, "F01→FAC_ANALYSIS"),
    ("src/zephyr/factor/analysis/factor_optimization/", FACTOR_BASE, "F01→FAC_ANALYSIS"),
    ("src/zephyr/factor/analysis/factor_attribution/", FACTOR_BASE, "F01→FAC_ANALYSIS"),
    ("src/zephyr/factor/analysis/decay_monitor/", FACTOR_BASE, "F02→F08 Registry→Decay"),
    ("src/zephyr/factor/analysis/correlation_analyzer/", FACTOR_BASE, "F02→F09 Registry→Correlation"),
    # F. Pipeline → 治理/背压（2）
    (PIPELINE, "src/zephyr/factor/governance/abs001_gate/", "F04→F64"),
    (PIPELINE, "src/zephyr/factor/core/backpressure/", "F04→F65"),
    # G. 治理引擎 → 生命周期状态机（1）
    ("src/zephyr/factor/governance/engine/", "src/zephyr/factor/governance/lifecycle_state_machine/", "FAC_GOV→F67"),
    # H. barra 反向修正（3）—— GATE-11/24 依赖型转边
    ("src/zephyr/factor/barra/exposure_calculator/", "src/zephyr/factor/barra/risk_model/", "GATE-11-01: Exposure需06就绪"),
    ("src/zephyr/factor/barra/risk_budget_allocator/", "src/zephyr/factor/barra/exposure_calculator/", "GATE-24-01: RiskBudget需11就绪"),
    ("src/zephyr/factor/barra/risk_budget_allocator/", "src/zephyr/factor/barra/risk_model/", "GATE-24-01: RiskBudget需06就绪"),
]

# ============================================================
# Step 4 数据：安全约束/数据可用型 GATE → gate_reason 注解
# ============================================================
GATE_REASON_BY_PATH: dict[str, str] = {
    "src/zephyr/factor/mine/mining_agent/": "GATE-05-01~03: AST沙箱白名单(禁import/exec/eval/open)+复杂度约束(嵌套≤5/参数≤10/节点≤50)+三重语义一致性; FactorMAD投票",
    "src/zephyr/factor/mine/causal_validator/": "GATE-16-01~02: DoWhy/DML因果验证(三阶段:工具变量/Do-calculus/反事实)",
    "src/zephyr/factor/barra/esg/": "GATE-17-01~02: ESG因子需ESG数据就绪",
    "src/zephyr/factor/ashare/microstructure/": "GATE-27-01: 需Level-2逐笔成交数据",
    "src/zephyr/factor/ashare/intraday/": "GATE-29-01: 需3秒Tick管线稳定运行",
    "src/zephyr/factor/ashare/smc/": "GATE-55-01~02: 需SMC数据",
    "src/zephyr/factor/ashare/irl/": "GATE-56-01: 需IRL数据",
    "src/zephyr/factor/ashare/alpha87/": "GATE-92-01: 需87-Alpha数据集",
    "src/zephyr/factor/ashare/pattern_signal/": "GATE-97-01: 需形态识别数据",
    "src/zephyr/factor/ashare/institutional/": "GATE-100-01: 需iFind龙虎榜+北向+大宗数据",
    "src/zephyr/factor/ashare/cross_market/": "GATE-102-01: 需iFind全球市场数据",
    "src/zephyr/factor/ashare/ps_liquidity/": "GATE-106-01: 需iFind全球市场数据+统计回归库",
    "src/zephyr/factor/core/dist_feature_eng/": "GATE-105-01: 需01 Engine+因子池≥10因子就绪; 产出不入因子池IC评估,专供密度预测模型",
    "src/zephyr/factor/analysis/three_level_judgment/": "GATE-87-01: 三级判断门禁",
    "src/zephyr/factor/analysis/layered_backtest/": "GATE-101-01: 分层回测门禁",
    "src/zephyr/factor/analysis/ic_decay/": "GATE-88-01: IC衰减分析门禁",
    "src/zephyr/factor/analysis/multifactor_synthesis/": "GATE-84-01: 多因子合成验证门禁",
    "src/zephyr/factor/analysis/correlation_dedup/": "GATE-110-01: 相关性去冗余门禁",
    "src/zephyr/factor/analysis/factor_optimization/": "GATE-111-01: 因子组合优化门禁",
    "src/zephyr/factor/analysis/factor_attribution/": "GATE-112-01: 需06 Barra+11 Exposure就绪; 因子归因分析",
    "src/zephyr/factor/governance/grayscale_rollout/": "GATE-54-01: 灰度上线门禁(5%→20%→全权重)",
    "src/zephyr/factor/governance/six_step_flow/": "GATE-66-01: 6步入职流程门禁",
    "src/zephyr/factor/governance/lifecycle_state_machine/": "GATE-67-01: 生命周期状态机门禁",
    "src/zephyr/factor/governance/abs001_gate/": "GATE-64-01: ABS-001准入门禁",
}


def resolve_subdomain(path: str) -> str | None:
    """按 path 前缀/文件名解析 subdomain_id。"""
    if path in SUBDOMAIN_BY_FILE:
        return SUBDOMAIN_BY_FILE[path]
    for prefix, sub in SUBDOMAIN_BY_PREFIX:
        if path.startswith(prefix):
            return sub
    return None


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="因子工厂全景设计态补全")
    parser.add_argument("--dry-run", action="store_true", help="仅预览，不写 DB")
    args = parser.parse_args()

    print(f"=== 因子工厂设计态补全 (dry_run={args.dry_run}) ===\n")

    # ---- Step 1+4: 加载 dep, 设 subdomain_id + gate_reason ----
    print("[Step 1+4] 加载 depgraph, 设置 subdomain_id + gate_reason ...")
    dep = _load_depgraph()
    path_to_id: dict[str, int] = {}
    sub_changes = 0
    gate_changes = 0
    for nid, node in dep["nodes"].items():
        path = node.get("path", "")
        if not path.startswith("src/zephyr/factor"):
            continue
        path_to_id[path] = int(nid)
        # subdomain_id
        sub = resolve_subdomain(path)
        if sub and node.get("subdomain_id") != sub:
            print(f"  subdomain: {path} -> {sub} (was {node.get('subdomain_id')})")
            node["subdomain_id"] = sub
            sub_changes += 1
        # gate_reason
        gate = GATE_REASON_BY_PATH.get(path)
        if gate and node.get("gate_reason") != gate:
            print(f"  gate_reason: {path} -> {gate[:60]}...")
            node["gate_reason"] = gate
            gate_changes += 1

    print(f"  subdomain_id 变更: {sub_changes} 个节点")
    print(f"  gate_reason 变更: {gate_changes} 个节点\n")

    if args.dry_run:
        print("[DRY RUN] Step 1+4 不写 DB（_atomic_write 跳过）\n")
    else:
        _atomic_write(dep)
        print("[OK] Step 1+4 已写回 DB\n")

    # ---- Step 2: 删除反向边 ----
    print(f"[Step 2] 删除 {len(EDGES_TO_DELETE)} 条反向边 ...")
    for eid in EDGES_TO_DELETE:
        if args.dry_run:
            print(f"  [DRY RUN] 将删除 edge_id={eid}")
        else:
            ok = delete_edge(eid)
            print(f"  delete edge_id={eid}: {'OK' if ok else 'FAIL'}")
    print()

    # ---- Step 3: 新增设计态边 ----
    print(f"[Step 3] 新增 {len(EDGES_TO_ADD)} 条设计态边 (dep_maturity=design) ...")
    ok_cnt = 0
    fail_cnt = 0
    for from_path, to_path, label in EDGES_TO_ADD:
        from_id = path_to_id.get(from_path)
        to_id = path_to_id.get(to_path)
        if from_id is None:
            print(f"  FAIL: from_path 未找到节点: {from_path} ({label})")
            fail_cnt += 1
            continue
        if to_id is None:
            print(f"  FAIL: to_path 未找到节点: {to_path} ({label})")
            fail_cnt += 1
            continue
        if args.dry_run:
            print(f"  [DRY RUN] {from_path} -> {to_path}  ({label})")
            ok_cnt += 1
        else:
            eid = add_edge(from_id, to_id, dep_type="import_depends", dep_maturity="design")
            if eid > 0:
                ok_cnt += 1
            else:
                fail_cnt += 1
            print(f"  add {from_path} -> {to_path}: edge_id={eid}  ({label})")
    print(f"\n  成功: {ok_cnt}, 失败: {fail_cnt}\n")

    print("=== 完成 ===")
    return 0 if fail_cnt == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
