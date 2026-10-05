# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §dev_delivery_map_gate
# [MODULE] zephyr.gov_enforcement.commit_gates.map_family.dev_delivery_map_gate
# create-guard-not-dup: 图11 交付流水线图提交门（阻塞语义封装体，校验逻辑单一真源=validate_dev_delivery_map 复用禁复制）；token=mapfamily-dev_delivery_map_gate-20261001 系 st-matrix-final-20260930 预登记在册，本件兑现其登记位（FOLDER-CAPACITY 120 顶格拆簇 map_family/ 收纳，90_execution_log 拆簇工单挂账兑现）
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.validate_dev_delivery_map（validate_structure
#   单一真源，sys.path 动态加载——校验逻辑禁复制）
# [CONSUMERS] zephyr.gov_enforcement.commit_gates.panorama_alignment_gate（MAP-ALIGNMENT 聚合台 subs 清单——
#   兑现 validate_dev_delivery_map [CONSUMERS] 自落地起声明的 gate 消费方）；
#   tests/governance/commit_gates/test_dev_delivery_map_gate.py
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 硬阻断（确定性结构校验）——config/dev_delivery_map.yaml 经 validate_structure 判
#   error>0 → 阻断 commit（顶层必填键/L0 统一名/28+2 环节契约全集/边闭合/三车道归属/枚举族/
#   built 必带 module_ref 代码锚/verified 必带 evidence/decision_question 长度/counts 一致/
#   路径锚实存/store_refs 三要素/INV-1 复制侵权/CV-BUS/CV-DUAL/CV-L0/CV-GAP/CV-DOMAIN）；
#   触发式——本 commit（files∪held）触及图输入面（图 YAML+生成器+校验器+骨架+门禁双册+
#   tasks/schedule+数据资产册+flags）才跑全量；own_scope=None 退化恒跑保守；YAML 解析异常=
#   fail-closed（真源损坏必须先修）；血肉未满=validator 内部降 warn 级不拦（挂图 SOP §4 分阶段口径）
# [MODIFY-GUARD] gate_id="DEV-DELIVERY-MAP"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]；
#   触发面变更须与 validate_dev_delivery_map 判据读取面及 alignment_checklist 图11 行同批
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] validator 加载失败/YAML 损坏=fail-closed 阻断；外部面不可达由 validator 内部降 warn
#   （骨架两列/depgraph PG/门禁册，禁环境异常打死无辜提交）
# [TESTS] tests/governance/commit_gates/test_dev_delivery_map_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-MAP-MOUNT-012-001
"""dev_delivery_map_gate.py — 图11（交付流水线全景图）结构校验门（DEV-DELIVERY-MAP，经 MAP-ALIGNMENT 聚合台）

病根（第一性原理）
-----------------
图11 真源 config/dev_delivery_map.yaml 是机生图（生成器 generate_dev_delivery_map.py
产出，禁手改不回生成），validate_dev_delivery_map.py 已随 st-sG-mapwrite-20261004
上户口批落地并声明本 gate 为消费方，但 gate 通道此前不存在——图 YAML 被裸改/改坏时
无任何提交门拦截。本批（st-fig1113reg-20261004 图11 转正四件套收尾）把校验器接进
MAP-ALIGNMENT 聚合台（panorama_alignment_gate subs 清单，同 DATA-SUPPLY-CHAIN-MAP/
TRADING-DAY-CYCLE-MAP 先例），坏图在 commit 时硬拦。

设计权衡
--------
1. **触发式**：本 commit（files∪held）触及图输入面才跑全量校验；无归属信息退化恒跑
   保守（先例：decision_map_gate/data_supply_chain_map_gate/trading_day_cycle_map_gate 同款）。
2. **error=阻断**：validator 全部确定性判据（CV 规则族+环节契约全集），gate 只封阻塞
   语义禁复制。
3. **外部面降 warn**：骨架两列/depgraph PG/门禁册不可达由 validator 内部降 warn
   （挂图 SOP §4 口径——禁环境异常打死无辜提交），gate 不升级。
4. **YAML 异常=阻断**：图真源损坏时全体缺口检测失效，必须先修图再提交。

Usage::

    # 经 panorama_alignment_gate 的 subs 清单自动接入（MAP-ALIGNMENT），无需手动注册：
    ("DEV-DELIVERY-MAP", "map_family.dev_delivery_map_gate", "_check")

# [ALGO_FLOW] external: docs/03_modules/_domain_gov_enforcement/algo_flow/dev_delivery_map_gate.yaml
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Final

from zephyr.gov_enforcement.commit_gates._diff_helpers import _build_own_scope, _norm_rel
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__: Final = ["make_dev_delivery_map_gate", "_check"]

# 校验逻辑单一真源（validators/ 目录），动态加载（先例：data_supply_chain_map_gate）。
# parents[5]=仓根（map_family/ 子包比 flat 深一层，迁移件同步加深防 src/scripts 幽灵目录）
_VALIDATORS_DIR = Path(__file__).resolve().parents[5] / "scripts" / "governance" / "d5_architecture" / "validators"

# 图输入面（触发式收窄真源）：与生成器/校验器读取面一一对应（generate_dev_delivery_map.py
# 的 [DEPENDENCIES] 声明面 + validate_dev_delivery_map.py 判据读取面）。
# 常量侧 os.path.normcase 与 _norm_rel 输出同域可比。
_MAP_INPUT_EXACT: Final = frozenset(
    os.path.normcase(p)
    for p in (
        "config/dev_delivery_map.yaml",
        "scripts/governance/d5_architecture/generators/generate_dev_delivery_map.py",
        "scripts/governance/d5_architecture/validators/validate_dev_delivery_map.py",
        "docs/_working/map_build/fig11_delivery/00_skeleton.md",
        "docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml",
        "docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml",
        "src/zephyr/data/config/tasks.yaml",
        "src/zephyr/data/config/schedule.yaml",
        "docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml",
        "config/flags.yaml",
    )
)

_MAP_YAML_REL: Final = "config/dev_delivery_map.yaml"


def _is_map_input(norm_rel: str) -> bool:
    """normcase 归一后的相对路径是否命中图11输入面。"""
    return norm_rel in _MAP_INPUT_EXACT


def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
    """图11 结构校验闭包（经 MAP-ALIGNMENT 聚合台 subs 调用）。"""
    own_scope = _build_own_scope(gateway, files, kwargs.get("session_id"))
    if own_scope is not None and not any(_is_map_input(p) for p in own_scope):
        return True, "skip: 本 commit 未触及图11输入面（触发式收窄，先例 trading_day_cycle_map_gate）"

    if str(_VALIDATORS_DIR) not in sys.path:
        sys.path.insert(0, str(_VALIDATORS_DIR))
    try:
        from validate_dev_delivery_map import validate_structure  # noqa: import-integrity  sys.path 动态加载
    except Exception as e:  # noqa: BLE001 — 校验器不可达=fail-closed
        logger.error("DEV-DELIVERY-MAP gate: 校验器加载失败（fail-closed）: %s", e)
        return False, f"DEV-DELIVERY-MAP: 校验器 validate_dev_delivery_map 加载失败（fail-closed）: {e}"

    import yaml

    map_path = Path(gateway.repo_root) / _MAP_YAML_REL if hasattr(gateway, "repo_root") else Path(_MAP_YAML_REL)
    try:
        data = yaml.safe_load(map_path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001 — 真源损坏=fail-closed（须先修图）
        logger.error("DEV-DELIVERY-MAP gate: 图 YAML 解析异常（fail-closed）: %s", e)
        return False, (
            f"DEV-DELIVERY-MAP: {_MAP_YAML_REL} 解析异常（真源损坏须先修）: {e}\n"
            "-> 重跑 scripts/governance/d5_architecture/generators/generate_dev_delivery_map.py"
        )

    warns: list[str] = []
    try:
        errors = validate_structure(data, map_path.parents[1] if map_path.parents else None, warns)
    except Exception as e:  # noqa: BLE001 — 判据异常=fail-closed
        logger.error("DEV-DELIVERY-MAP gate: validate_structure 异常（fail-closed）: %s", e)
        return False, f"DEV-DELIVERY-MAP: validate_structure 异常（fail-closed）: {e}"

    if errors:
        detail_lines = "\n".join(f"  - {x}" for x in errors[:20])
        detail = (
            f"DEV-DELIVERY-MAP：图11 校验 {len(errors)} 项 error\n{detail_lines}\n"
            "-> 修复后重提（机生面走生成器重跑，禁手改："
            "python scripts/governance/d5_architecture/generators/generate_dev_delivery_map.py）"
        )
        logger.error("DEV-DELIVERY-MAP gate block:\n%s", detail)
        return False, detail

    # 放行：warn 留痕（外部面不可达降级项——骨架两列/depgraph PG/门禁册）
    if warns:
        return True, f"pass: 外部面降级 warn={len(warns)}（骨架/depgraph/门禁册不可达，禁环境异常打死提交）"
    return True, ""


def make_dev_delivery_map_gate() -> GateSpec:
    """单门工厂（保留兼容形态；实际经 panorama_alignment_gate subs 清单接入 MAP-ALIGNMENT）。"""
    return GateSpec(gate_id="DEV-DELIVERY-MAP", check=_check, priority=149)
