# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §battle_map_alignment_gate
# [MODULE] zephyr.gov_enforcement.commit_gates.battle_map_alignment_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] scripts.governance.align_battle_map (run_alignment, sys.path 动态加载——检测逻辑单一真源)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__（经 in_process_gate_registry.yaml 自动注册）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 硬阻断（文件触发）——staged 触及作战地图相关路径（module_translation_registry/battle_map_domain_policy/align_battle_map/apply_battle_map/src battle_map 代码）时跑七类对齐：ghost_anchors(BM-INV-002)>0 / orphan_steps 违规(BM-INV-001，acknowledged 已排除)>0 / missing_narratives(BM-INV-003)>0 → 阻断；domain_drifts/dangling_edges/parent_child/orphan_modules 保持 warn（孤儿模块 457=血肉阶段清淤campaign，G4）；基线 0 已实证（2026-09-05 G3 驱零后）；PG 异常=fail-open（对标 panorama gate 惯例）
# [MODIFY-GUARD] gate_id="GATE-BATTLE-MAP-ALIGNMENT"；触发路径清单变更须同步 trae_080
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] run_alignment 异常=fail-open + logger.error（检测器/DB 故障不阻塞 commit，与 GATE-PANORAMA-ALIGNMENT 同惯例）；纯判定逻辑在 evaluate_battle_map_report（纯函数，可单测）
# [TESTS] tests/governance/test_alignment_gates_red_blue.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-BATTLE-MAP-HARD-001
# [CREATION-TOKEN] auto-battle-map-gate-20260905
"""battle_map_alignment_gate.py — 作战地图对齐硬化门禁（GATE-BATTLE-MAP-ALIGNMENT，priority=833）

病根（第一性原理）
-----------------
作战地图七类对齐检查（BM-INV-001~007）此前全部 warn-only 君子协定——"改 battle_map
三表前自动 PG 备份"有，但"改完引用断了会拦截"没有。血肉填充阶段大量新环节/新锚点
入库，孤儿环节/缺失叙事可无感累积。2026-09-05 G3 驱零实证：违规孤儿环节=0、缺失
叙事=0、幽灵锚点=0（acknowledged 18 项已排除）——三类确定性检查具备升硬基线。

设计权衡
--------
1. **文件触发**（非恒跑）：run_alignment 需查 PG 三表（秒级），仅 staged 触及 BM 相关
   路径时跑——module_translation_registry.yaml（叙事真源）/battle_map_domain_policy.yaml
   （豁免+域策略真源）/align_battle_map.py/apply_battle_map.py/src 内 battle_map 代码。
2. **三类硬 / 四类软**：ghost（引用断链）/orphan_steps 违规/missing_narratives=确定性
   且基线 0 → 硬；domain_drifts（新域挂载需先更新 policy——warn 提示而非阻塞）/悬空边/
   父子嵌套/orphan_modules（457=血肉 campaign）→ warn。
3. **检测逻辑单一真源**：align_battle_map.run_alignment（scripts 层），gate 只做
   触发+分级+阻塞语义封装；纯判定抽取 evaluate_battle_map_report 供单测。
4. **fail-open**：检测器/PG 异常不阻塞 commit（与 GATE-PANORAMA-ALIGNMENT 同惯例），
   logger.error 留痕。

Usage::

    from zephyr.gov_enforcement.commit_gates.battle_map_alignment_gate import make_battle_map_alignment_gate
    registry.register(make_battle_map_alignment_gate())

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: staged 文件列表
#   fields: files（gateway 传入）
#   code: _check 按 _TRIGGER_SUFFIXES 匹配触发
# - id: I2
#   name: battle_map 三表 + 翻译真源 + policy
#   fields: PostgreSQL battle_map_steps/anchors/edges + module_translation_registry.yaml + battle_map_domain_policy.yaml
#   code: align_battle_map.run_alignment(write_report=False)
# 层: 算法
# - id: A1
#   name_zh: ① 纯判定
#   name_en: evaluate_battle_map_report
#   intro: ghost/orphan_steps/missing_narratives >0 → 硬；其余 → 软
#   desc: 纯函数（report 进、判定出），可脱离 PG 单测
#   inputs: I2
#   outputs: (hard_list, soft_list)
# - id: A2
#   name_zh: ② 阻塞语义封装
#   name_en: _check 闭包
#   intro: hard_list 非空 → 阻断；run_alignment 异常 → fail-open
#   desc: 触发判定在前（未触发=秒回 True）
#   inputs: A1 I1
#   outputs: (passed, detail)
# 层: 输出
# - id: O1
#   name_zh: GateSpec
#   name_en: GateSpec(gate_id="GATE-BATTLE-MAP-ALIGNMENT", priority=833)
#   intro: 文件触发型混合门禁（三类硬+四类软）
#   downstream: git_commit_gateway.GitCommitGateway.__init__
# [/ALGO_FLOW]
#
# 边:
# I1 --> A2
# I2 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any, Final

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__: Final = ["make_battle_map_alignment_gate", "evaluate_battle_map_report"]

_GOV_DIR = Path(__file__).resolve().parents[4] / "scripts" / "governance"

# 文件触发清单（staged 命中任一后缀才跑检测——秒级 PG 查询不恒跑）
_TRIGGER_SUFFIXES: tuple[str, ...] = (
    "module_translation_registry.yaml",
    "battle_map_domain_policy.yaml",
    "align_battle_map.py",
    "apply_battle_map.py",
    "generate_battle_map_diagram.py",
)
_TRIGGER_DIR_PARTS = ("battle_map",)


def evaluate_battle_map_report(report: Any) -> tuple[list[str], list[str]]:
    """纯判定：report → (hard_list, soft_list)。

    硬=ghost_anchors / 违规孤儿环节 / 缺失叙事（确定性、基线 0，G3 升硬）。
    软=域漂移/悬空边/父子嵌套/孤儿模块（warn，G4 清淤 campaign 承载）。
    """
    hard: list[str] = []
    soft: list[str] = []
    if report.ghost_anchors:
        hard.append(f"幽灵锚点（BM-INV-002）={len(report.ghost_anchors)}: {report.ghost_anchors[:5]}")
    if report.orphan_steps:
        hard.append(
            f"违规孤儿环节（BM-INV-001，acknowledged 已排除）={len(report.orphan_steps)}: "
            f"{[s.get('step_id') if isinstance(s, dict) else s for s in report.orphan_steps[:5]]}"
        )
    if report.missing_narratives:
        hard.append(
            f"缺失叙事（BM-INV-003）={len(report.missing_narratives)}: "
            f"{[s.get('step_id') if isinstance(s, dict) else s for s in report.missing_narratives[:5]]}"
        )
    if report.domain_drifts:
        soft.append(f"域漂移（BM-INV-004）={len(report.domain_drifts)}（新域挂载须先更新 battle_map_domain_policy）")
    if report.dangling_edges:
        soft.append(f"悬空边={len(report.dangling_edges)}")
    if report.parent_child_issues:
        soft.append(f"父子嵌套问题（BM-INV-006）={len(report.parent_child_issues)}")
    if report.orphan_modules:
        soft.append(f"孤儿模块（BM-INV-007）={len(report.orphan_modules)}（G4 清淤 campaign 承载，warn）")
    return hard, soft


def make_battle_map_alignment_gate() -> GateSpec:
    """构造作战地图对齐硬化 GateSpec（G3：BM-INV-001/003 驱零后升硬）。

    Returns:
        GateSpec(gate_id="GATE-BATTLE-MAP-ALIGNMENT", priority=833)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        if not files:
            return True, ""
        norm = [f.replace("\\", "/") for f in files]
        triggered = any(
            any(f.endswith(sfx) for sfx in _TRIGGER_SUFFIXES) or _TRIGGER_DIR_PARTS[0] in f.split("/") for f in norm
        )
        if not triggered:
            return True, ""

        if str(_GOV_DIR) not in sys.path:
            sys.path.insert(0, str(_GOV_DIR))
        try:
            from align_battle_map import run_alignment  # noqa: import-integrity  sys.path 动态加载
        except Exception as e:  # noqa: BLE001 — 检测器不可达=fail-open（与 panorama gate 同惯例）
            logger.error("GATE-BATTLE-MAP-ALIGNMENT: 检测器加载失败（fail-open）: %s", e)
            return True, ""

        try:
            report = run_alignment(write_report=False)
        except Exception as e:  # noqa: BLE001 — PG/检测异常=fail-open
            logger.error("GATE-BATTLE-MAP-ALIGNMENT: run_alignment 异常（fail-open）: %s", e)
            return True, ""

        hard, soft = evaluate_battle_map_report(report)
        if soft:
            logger.info("GATE-BATTLE-MAP-ALIGNMENT: soft warn=%d（不阻断）", len(soft))
        if not hard:
            return True, ""

        detail_lines = "\n".join(f"  - {x}" for x in hard)
        detail = (
            f"GATE-BATTLE-MAP-ALIGNMENT：作战地图对齐硬检查 {len(hard)} 类违规\n"
            f"{detail_lines}\n"
            "-> 幽灵锚点：apply_battle_map 清理 / 孤儿环节：挂锚点或登记 acknowledged "
            "（battle_map_domain_policy.yaml）/ 缺失叙事：module_translation_registry.yaml "
            "battle_map_steps 段补条目"
        )
        logger.error("GATE-BATTLE-MAP-ALIGNMENT block:\n%s", detail)
        return False, detail

    return GateSpec(gate_id="GATE-BATTLE-MAP-ALIGNMENT", check=_check, priority=833)
