# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §decision_map_gate
# [MODULE] zephyr.gov_enforcement.commit_gates.decision_map_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] scripts.governance.d5_architecture.generators.check_decision_map (run_checks, sys.path 动态加载——校验逻辑单一真源)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__（经 in_process_gate_registry.yaml 自动注册）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 硬阻断（确定性校验）——config/trading_decision_map.yaml R1-R8 error 级缺口>0 → 阻断 commit；恒跑（读 4 个 YAML 毫秒级，不按文件过滤——地图被任何提交改动都可能产生引用断链）；校验逻辑单一真源=check_decision_map.py（gate 只做阻塞语义封装，禁复制 R1-R8）；YAML 解析异常=fail-closed（真源损坏必须先修）
# [MODIFY-GUARD] gate_id="DECISION-MAP"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] run_checks 异常=fail-closed 阻断（真源损坏须先修）；与 FRONTEND-MAP(137) 同族确定性硬门禁
# [TESTS] tests/governance/test_alignment_gates_red_blue.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-DECISION-MAP-GATE-001
# [CREATION-TOKEN] auto-decision-map-gate-20260905
"""decision_map_gate.py — 第七图（交易决策地图）对齐阻断门禁（DECISION-MAP，priority=138）

病根（第一性原理）
-----------------
交易决策地图（MOD-TRADING-015，Owner D1-D6 裁定）的真源是引用型图谱：
策略挂载/因子引用/数据引用全按稳定标识符指向既有注册表。血肉填充阶段（状态矩阵
格子/策略挂载/因子引用逐格添加）会产生大量新引用——没有 commit 门禁，引用断链
（strategy_ref 写错/FCT-* 不存在/verified 缺 evidence/sequence 成环）是静默的，
等 V1 前端接上就是整页幻觉。本 gate 把校验接进 pre-commit 链（七图对齐 commit 闭环）。

设计权衡
--------
1. **恒跑**：读 4 个 YAML + AST 扫描 pf_core（毫秒级~十毫秒级），不按文件过滤。
2. **error=阻断**：R1-R8 全部确定性校验（非启发式），镜像 FRONTEND-MAP 分层。
3. **校验逻辑单一真源**：R1-R8 只在 zephyr.trading.decision_map.validate_decision_map
   实现，scripts 层 check_decision_map.py 封装，gate 动态复用——禁复制。
4. **YAML 异常=阻断**：地图真源损坏时全体缺口检测失效，必须先修图再提交。

Usage::

    from zephyr.gov_enforcement.commit_gates.decision_map_gate import make_decision_map_gate
    registry.register(make_decision_map_gate())

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 地图真源 + 三注册表 + 代码策略 id
#   fields: config/trading_decision_map.yaml + catalogs 三库 + pf_core AST 字面量
#   code: check_decision_map.run_checks()
# 层: 算法
# - id: A1
#   name_zh: ① 动态加载校验器并执行
#   name_en: _check 闭包
#   intro: sys.path 动态 import check_decision_map（先例=FRONTEND-MAP/align_all）
#   desc: fails>0 → 阻断（明细逐条）；warns 只展示；异常=fail-closed
#   inputs: I1
#   outputs: (passed, detail)
# 层: 输出
# - id: O1
#   name_zh: GateSpec
#   name_en: GateSpec(gate_id="DECISION-MAP", priority=138)
#   intro: 硬阻断型确定性门禁（七图对齐 commit 链闭环之一）
#   downstream: git_commit_gateway.GitCommitGateway.__init__
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Final

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__: Final = ["make_decision_map_gate"]

# 校验逻辑单一真源（scripts 层 check_decision_map.py），动态加载（先例：frontend_map_gate）
_GENERATORS_DIR = Path(__file__).resolve().parents[4] / "scripts" / "governance" / "d5_architecture" / "generators"


def make_decision_map_gate() -> GateSpec:
    """构造交易决策地图对齐硬阻断 GateSpec（七图对齐 commit 链闭环）。

    Returns:
        GateSpec(gate_id="DECISION-MAP", priority=138)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        if str(_GENERATORS_DIR) not in sys.path:
            sys.path.insert(0, str(_GENERATORS_DIR))
        try:
            from check_decision_map import run_checks  # noqa: import-integrity  sys.path 动态加载
        except Exception as e:  # noqa: BLE001 — 校验器不可达=fail-closed
            logger.error("DECISION-MAP gate: 校验器加载失败（fail-closed）: %s", e)
            return False, f"DECISION-MAP: 校验器 check_decision_map 加载失败（fail-closed）: {e}"

        try:
            fails, warns, total = run_checks()
        except Exception as e:  # noqa: BLE001 — 真源损坏=fail-closed（须先修图）
            logger.error("DECISION-MAP gate: trading_decision_map.yaml 校验异常（fail-closed）: %s", e)
            return False, (
                f"DECISION-MAP: trading_decision_map.yaml 校验异常（真源损坏须先修）: {e}\n"
                "-> 检查 config/trading_decision_map.yaml 语法与 schema v1.0 结构"
            )

        if not fails:
            if warns:
                logger.info("DECISION-MAP gate: fail=0 warn=%d（放行，缺口红节点占位）", len(warns))
            return True, ""

        detail_lines = "\n".join(f"  - {x}" for x in fails)
        detail = (
            f"DECISION-MAP：交易决策地图校验 {len(fails)} 项 error（共 {total} 节点）\n"
            f"{detail_lines}\n"
            "-> 修复 config/trading_decision_map.yaml 后重提"
            "（R1 枚举/R2 边/R3 策略引用/R4 因子/R5 数据/R6 置信度/R7 矩阵格/R8 成环）"
        )
        logger.error("DECISION-MAP gate block:\n%s", detail)
        return False, detail

    return GateSpec(gate_id="DECISION-MAP", check=_check, priority=138)
