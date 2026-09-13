# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §strategy_factory_map_gate
# [MODULE] zephyr.gov_enforcement.commit_gates.strategy_factory_map_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] yaml（外部）；scripts.governance.d5_architecture.validators.validate_strategy_production_map（validate_structure，sys.path 动态加载——校验逻辑单一真源，禁复制）
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__（经 in_process_gate_registry.yaml 自动注册）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 硬阻断（确定性校验）——触发式：本 commit 触及 config/strategy_production_map.yaml 或校验器真源时跑 v0.2 schema 结构十项校验（字段完整性/边闭合/E0-E9 层位/laws/产品清单/built 必有锚/lane 归属/未声明反馈环/自环/store_refs 三要素），error>0→阻断；YAML 解析/校验器加载异常=fail-closed（真源损坏必须先修）；仓储存在性（含 CH 连通性=环境异常域）不入本 gate——归 align_all 第八节（CH fail-open）与 CLI 校验器；无归属信息退化恒跑（保守面不改宽）
# [MODIFY-GUARD] gate_id="FACTORY-MAP"；触发文件清单 _TRIGGER_FILES 变更须同步 alignment_checklist §3 图 9 行；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 校验器加载失败/图 YAML 解析失败/结构校验异常=fail-closed 阻断（真源损坏须先修）；触发面外=skip 放行；与 DECISION-MAP(138)/INDUSTRY-CHAIN-MAP(141) 同族确定性硬门禁
# [TESTS] tests/governance/commit_gates/test_strategy_factory_map_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-FACTORY-MAP-GATE-001
# [CREATION-TOKEN] factory-map-gate-20260913
"""strategy_factory_map_gate.py — 策略生产全景图（图 9）结构门禁（FACTORY-MAP，priority=142）

病根（第一性原理）
-----------------
策略工厂图（图 9，E0-E9 十层供给端全景）是**增长轨**设计：E1 五车道"无限生长"、
E3 构造层 growth=极大——节点/边将持续增殖。无 commit 门禁时，断边/缺字段/非法层位/
built 无代码锚等结构腐坏是静默的（批1 校验器上线即抓到 FAC-E1A built 无锚真问题=
风险实证），等消费者（registry/组合装配）接入就是整页幻觉。本 gate 把批1 结构校验器
接进 pre-commit 链，与 DECISION-MAP(138) 同构：校验逻辑单一真源在
validate_strategy_production_map.validate_structure，gate 只做阻塞语义封装。

设计权衡
--------
1. **触发式**：仅本 commit 触及图真源 YAML 或校验器真源 .py 时跑结构校验（纯 YAML
   解析+内存校验 <1s，无外部 I/O）；其余提交零开销（skip 路径）。
2. **结构归 gate、仓储归 align_all**：store_refs 存在性含 CH 连通性（环境异常域），
   入 gate 会把 infra 故障误伤为全部地图提交阻断；故仓储存在性归 align_all 第八节
   （CH 连接异常降 warn，学图 8 PG fail-open 先例）+ CLI 校验器（--skip-stores 可控）。
3. **校验器变更也触发**：规则收紧时强制重校当前图（学 INDUSTRY-CHAIN-MAP(141)
   字典↔DDL↔引擎三方同 commit 同步先例——图/规则同 commit 收敛）。
4. **YAML 损坏 fail-closed**：图真源损坏时结构校验全线失效，必须先修图再提交
   （对标 DECISION-MAP 对 trading_decision_map.yaml 的处理）。

Usage::

    from zephyr.gov_enforcement.commit_gates.strategy_factory_map_gate import make_strategy_factory_map_gate

    registry.register(make_strategy_factory_map_gate())  # 经 in_process_gate_registry.yaml 自动注册
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Final

import yaml

from zephyr.gov_enforcement.commit_gates._diff_helpers import _norm_rel
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__: Final = ["make_strategy_factory_map_gate"]

_REPO_ROOT = Path(__file__).resolve().parents[4]
_VALIDATORS_DIR = _REPO_ROOT / "scripts" / "governance" / "d5_architecture" / "validators"

# 触发面：图真源 + 校验器真源（规则变更强制重校，学 INDUSTRY-CHAIN-MAP 三方同步先例）
_TRIGGER_FILES: Final[frozenset[str]] = frozenset(
    {
        "config/strategy_production_map.yaml",
        "scripts/governance/d5_architecture/validators/validate_strategy_production_map.py",
    }
)

# 触发面 normcase 归一（commit() 传入绝对路径——git_commit_gateway abspath，朴素
# 反斜杠替换对绝对路径恒 miss=实弹实证 7af850ac/a839ad38 断边图放行；本集合与
# _norm_rel 输出同域可比，学 DECISION-MAP _MAP_INPUT_YAML 先例）
_TRIGGER_FILES_NORMCASE: Final[frozenset[str]] = frozenset(
    os.path.normcase(p) for p in _TRIGGER_FILES
)

# 图真源路径（模块级常量=测试可替换挂点，红蓝 tmp 图直调 gate.check 先例=TestRedDecisionMap）
_MAP_PATH: Final[Path] = _REPO_ROOT / "config" / "strategy_production_map.yaml"


def make_strategy_factory_map_gate() -> GateSpec:
    """构造策略生产全景图结构门禁 GateSpec（图 9 挂总线，alignment_checklist §3）。

    Returns:
        GateSpec(gate_id="FACTORY-MAP", priority=142)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        if not files:
            return True, ""
        # 生产形态=绝对路径（gateway abspath），_norm_rel 归一到 normcase 相对路径
        # （实弹教训 2026-09-13：朴素反斜杠替换对绝对路径恒 miss）
        norm = {_norm_rel(gateway, f) for f in files}
        triggered = sorted(_TRIGGER_FILES_NORMCASE & norm)
        if not triggered:
            return True, "skip: 本 commit 未触及工厂图触发面（图 YAML/校验器真源）"

        # 校验逻辑单一真源（批1 validator），懒加载防 zephyr↔scripts 成环（先例=decision_map_gate）
        if str(_VALIDATORS_DIR) not in sys.path:
            sys.path.insert(0, str(_VALIDATORS_DIR))
        try:
            from validate_strategy_production_map import validate_structure  # noqa: import-integrity  sys.path 动态加载
        except Exception as e:  # noqa: BLE001 — 校验器不可达=fail-closed
            logger.error("FACTORY-MAP gate: 校验器加载失败（fail-closed）: %s", e)
            return False, f"FACTORY-MAP: 校验器 validate_strategy_production_map 加载失败（fail-closed）: {e}"

        try:
            data = yaml.safe_load(_MAP_PATH.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001 — 真源损坏=fail-closed
            logger.error("FACTORY-MAP gate: 图真源解析失败（fail-closed）: %s", e)
            return False, f"FACTORY-MAP: config/strategy_production_map.yaml 解析失败（真源损坏须先修）: {e}"
        if not isinstance(data, dict):
            return False, "FACTORY-MAP: config/strategy_production_map.yaml 顶层非对象（真源损坏须先修）"

        try:
            errors = validate_structure(data)
        except Exception as e:  # noqa: BLE001 — 校验器异常=fail-closed
            logger.error("FACTORY-MAP gate: 结构校验异常（fail-closed）: %s", e)
            return False, f"FACTORY-MAP: 结构校验异常（fail-closed）: {e}"

        if errors:
            detail_lines = "\n".join(f"  - {x}" for x in errors)
            detail = (
                f"FACTORY-MAP：策略生产全景图结构校验 {len(errors)} 项 error"
                f"（nodes={len(data.get('nodes') or [])}）\n{detail_lines}\n"
                "-> 修复 config/strategy_production_map.yaml 后重提"
                "（字段完整性/边引用闭合/E0-E9 层位/built 代码锚/lane 归属/store_refs 三要素/反馈环声明）"
            )
            logger.error("FACTORY-MAP gate block:\n%s", detail)
            return False, detail
        if triggered:
            logger.info("FACTORY-MAP gate: 结构校验通过（触发面=%s）", ",".join(triggered))
        return True, ""

    return GateSpec(gate_id="FACTORY-MAP", check=_check, priority=142)
