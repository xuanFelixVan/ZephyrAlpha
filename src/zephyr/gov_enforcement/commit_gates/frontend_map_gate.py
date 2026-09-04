# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.frontend_map_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] scripts.governance.d5_architecture.generators.check_frontend_map (run_checks, sys.path 动态加载——校验逻辑单一真源)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断（确定性校验非启发式）——frontend_map.yaml 三规则 fail（R0 id 重复/R1 backend_ref 非类型化/R2-R3 由 check_frontend_map 分级）→ 阻断 commit；YAML 解析异常 → 阻断（真源损坏必须先修，fail-closed）；恒跑（读两 yaml 毫秒级，不按文件过滤）；校验逻辑单一真源=check_frontend_map.py（gate 只做阻塞语义封装，禁复制规则）
# [MODIFY-GUARD] gate_id="FRONTEND-MAP"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 不吞 yaml 异常（真源损坏=fail-closed 阻断）；run_checks 异常由 registry 统一降级 fail-closed
# [TESTS] tests/governance/commit_gates/test_frontend_map_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""frontend_map_gate.py — 前端全景图对齐阻断门禁（FRONTEND-MAP，六图对齐最后一环）

病根（第一性原理）
-----------------
Owner 2026-09-04 六图对齐升级后，图 1-5 已有自动对齐（align_panoramas/align_battle_map），
图 6 frontend_map 的校验器（check_frontend_map.py）已落地但只在手动/align_all 场景跑——
commit 阶段无自动拦截，frontend_map 漂移（id 重复/backend_ref 悬空）可在无感中入库。
本 gate 把图 6 校验接进 pre-commit 链，六图对齐全自动闭环。

设计权衡
--------
1. **恒跑**：校验=读两个 YAML+内存比对（毫秒级），不值得按文件过滤引入漏检面。
2. **fail=阻断**：三规则是确定性校验（非启发式），fail=0 已实证（302 功能点），直接硬。
   与 frontend_truth_source_gate（启发式 warn 起步）形成"确定性硬/启发式软"分层。
3. **校验逻辑单一真源**：R0-R3 规则只在 check_frontend_map.py 实现（scripts 层），
   gate 经 sys.path 动态 import 复用（先例：align_all.py 同模式）——禁在 gate 里复制规则，
   否则双真源漂移（本仓血泪教训）。
4. **YAML 异常=阻断**：frontend_map.yaml 损坏（如 2026-09-04 发现的 \\q 转义炸）时
   全体前端对账失效，必须先修图再提交。
5. **priority=137**：紧随 FRONTEND-TRUTH-SOURCE(136)，同为前端治理链尾部。

Usage::

    from zephyr.gov_enforcement.commit_gates.frontend_map_gate import make_frontend_map_gate

    registry.register(make_frontend_map_gate())

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: frontend_map + manifest 真源
#   fields: web/frontend_map.yaml（302 功能点）+ features/manifest.yaml（11 模块）
#   code: check_frontend_map.run_checks()
# 层: 算法
# - id: A1
#   name_zh: ① 动态加载校验器
#   name_en: sys.path insert generators 目录 + import run_checks
#   intro: 校验逻辑单一真源在 scripts 层，gate 复用不复制
#   desc: 先例=align_all.py 同目录动态 import；import 失败=fail-closed（registry 异常降级）
#   inputs: I1
#   outputs: 三规则结果 (fails, warns, total)
# - id: A2
#   name_zh: ② 阻塞语义封装
#   name_en: _check 闭包
#   intro: fails>0 → passed=False 阻断（明细逐条列出）；warns 只展示不阻断
#   desc: R0 id 重复 / R1 backend_ref 悬空 → 阻断；R2 manifest 双向 / R3 file 失联 → warn
#   inputs: A1
#   outputs: (passed, detail)
# 层: 输出
# - id: O1
#   name_zh: GateSpec
#   name_en: GateSpec(gate_id="FRONTEND-MAP", priority=137)
#   intro: 硬阻断型确定性门禁（六图对齐 commit 链闭环）
#   downstream: zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__: list[str] = ["make_frontend_map_gate"]

# 校验逻辑单一真源（scripts 层 check_frontend_map.py），动态加载（先例：align_all.py）
_GENERATORS_DIR = Path(__file__).resolve().parents[4] / "scripts" / "governance" / "d5_architecture" / "generators"


def make_frontend_map_gate() -> GateSpec:
    """构造 frontend_map 对齐硬阻断 GateSpec（六图对齐 commit 链闭环）。

    Returns:
        GateSpec(gate_id="FRONTEND-MAP", priority=137)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        if str(_GENERATORS_DIR) not in sys.path:
            sys.path.insert(0, str(_GENERATORS_DIR))
        try:
            from check_frontend_map import run_checks  # noqa: import-integrity  sys.path 动态加载（align_all 同模式）
        except Exception as e:  # noqa: BLE001 — 校验器不可达=fail-closed（安全优先）
            logger.error("FRONTEND-MAP gate: 校验器加载失败（fail-closed）: %s", e)
            return False, f"FRONTEND-MAP: 校验器 check_frontend_map 加载失败（fail-closed）: {e}"

        try:
            fails, warns, total = run_checks()
        except Exception as e:  # noqa: BLE001 — YAML 解析异常=真源损坏=fail-closed（须先修图）
            logger.error("FRONTEND-MAP gate: frontend_map.yaml 校验异常（fail-closed）: %s", e)
            return False, (
                f"FRONTEND-MAP: frontend_map.yaml 校验异常（真源损坏须先修）: {e}\n"
                "-> 检查 src/zephyr/frontend/dashboard/web/frontend_map.yaml 语法（参照 2026-09-04 E:\\q 转义炸先例）"
            )

        if not fails:
            if warns:
                logger.info("FRONTEND-MAP gate: fail=0 warn=%d（放行）", len(warns))
            return True, ""

        detail_lines = "\n".join(f"  - {x}" for x in fails)
        detail = (
            f"FRONTEND-MAP：frontend_map 对齐校验 {len(fails)} 项 fail（共 {total} 功能点）\n"
            f"{detail_lines}\n"
            "-> 修复 src/zephyr/frontend/dashboard/web/frontend_map.yaml 后重提"
            "（backend_ref 五前缀类型化：module:/registry:/table:/api:/none:；id 禁重复）"
        )
        logger.error("FRONTEND-MAP gate block:\n%s", detail)
        return False, detail

    return GateSpec(gate_id="FRONTEND-MAP", check=_check, priority=137)
