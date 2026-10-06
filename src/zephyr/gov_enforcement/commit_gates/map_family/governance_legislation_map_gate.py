# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §governance_legislation_map_gate
# [MODULE] zephyr.gov_enforcement.commit_gates.map_family.governance_legislation_map_gate
# create-guard-not-dup: 本件=map_family 第四图族提交面执法件（图16 治理立法流图结构门，裁定#486 ①）；CapabilityLookup 命中 'gate governance' 泛词系 d8_doc_sync 族跨域邻居，判据真源=本图专用校验器 validate_governance_legislation_map，canonical 无重叠非第二实现
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] yaml；validate_governance_legislation_map（结构判据单一真源动态复用）+ _diff_helpers——详单见下方详情块
# [CONSUMERS] MAP-ALIGNMENT 聚合台 subs 消费（panorama_alignment_gate）+ 对抗测试——详单见下方详情块
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 触发式硬阻断（确定性校验）：本 commit 触及图16 真源四件（图 YAML/校验器/生成器/骨架）时跑结构校验（六态闭集+九机构+九迁移+七禁边、终态无出边、禁边不可同对绕过、保险丝下限 12、INV-1 长度面、实例禁入 nodes、prose_counts）error>0→阻断；live=False 提交面（真源磁盘实存与 counts 账本对拍归 CLI/align_all，一项不放宽结构面）；fail-closed——详单见下方详情块
# [MODIFY-GUARD] gate_id="GOVERNANCE-LEGISLATION-MAP"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]；_TRIGGER_FILES 变更须同步 in_process_gate_registry MAP-ALIGNMENT files_trigger 与 alignment_checklist 图16 行；本件禁复制校验器判据（改判据只改校验器）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 校验器不可达/图 YAML 损坏/结构校验异常=fail-closed 阻断；触发面外 skip 放行；不抛业务异常（内部异常收敛为 (False, detail)）
# [TESTS] tests/governance/commit_gates/map_family/test_governance_legislation_map_gate.py
# [TTL] permanent
# —— 详情块（14 字段头 30 行窗内，长文降为详情）——
#   图16 治理立法流图结构门（裁定#486 ①准入，立项卡呈批制首例）。域=治理立法条目状态面
#   （ruling_id 键），与图10 GOMAP（运行时进程面）跨域不同对象不并（w5_1）；与图15 卡生命周期
#   （card_id 键）同族不同域。判据真源=validate_governance_legislation_map.validate_structure，
#   本 gate 只做阻塞语义封装（形态逐条照抄 map_family 同族四 gate，勿造新概念）。
#   触发面四件：config/governance_legislation_map.yaml / 校验器 / 生成器 /
#   docs/_working/map_build/fig16_legislation/00_skeleton.md（骨架=语义契约）。
#   实例面不入 gate 的代价如实记：CV-04 真源磁盘实存与 CV-05 counts 账本对拍需读 PG 账本
#   （全仓扫描语义），提交面不做——结构面已把"幽灵状态/终态出边/禁边同对绕过/实例入 nodes"
#   钉死，账本侧漂移由 CLI 与 align_all 兜（生成器重灌回图）。
#   注册与聚合台挂载不属本件：图门自 st-gslim P4 起并入 MAP-ALIGNMENT 聚合台，本模块只暴露
#   _check；gate 册登记与 subs 挂载行由总包统一落（净零增长纪律）。

"""governance_legislation_map_gate.py — 治理立法流图（图16）结构门禁（GOVERNANCE-LEGISLATION-MAP）。

触发式：本 commit 触及图16 真源四件才跑；判据单一真源=校验器（懒加载防 zephyr↔scripts 成环，
先例=map_family 同族 gate）。

# [ALGO_FLOW] external: docs/03_modules/_domain_gov_enforcement/algo_flow/governance_legislation_map_gate.yaml
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Final

import yaml

from zephyr.gov_enforcement.commit_gates._diff_helpers import _norm_rel

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[5]
_VALIDATORS_DIR = _REPO_ROOT / "scripts" / "governance" / "d5_architecture" / "validators"
_VALIDATOR_MOD = "validate_governance_legislation_map"

_MAP_REL: Final[str] = "config/governance_legislation_map.yaml"
_VALIDATOR_REL: Final[str] = "scripts/governance/d5_architecture/validators/validate_governance_legislation_map.py"
_GENERATOR_REL: Final[str] = "scripts/governance/d5_architecture/generators/generate_governance_legislation_map.py"
_SKELETON_REL: Final[str] = "docs/_working/map_build/fig16_legislation/00_skeleton.md"

# 触发面=图 16 真源四件（图 YAML/校验器/生成器/骨架）
_TRIGGER_FILES: Final[frozenset[str]] = frozenset({_MAP_REL, _VALIDATOR_REL, _GENERATOR_REL, _SKELETON_REL})
_TRIGGER_FILES_NORMCASE: Final[frozenset[str]] = frozenset(os.path.normcase(p) for p in _TRIGGER_FILES)

_MAP_PATH: Final[Path] = _REPO_ROOT / _MAP_REL


def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
    """触发式结构校验（签名与聚合台 subs 约定一致；阻塞语义封装，判据真源在校验器）。"""
    if not files:
        return True, ""
    norm = {_norm_rel(gateway, f) for f in files}
    triggered = sorted(_TRIGGER_FILES_NORMCASE & norm)
    if not triggered:
        return True, "skip: 本 commit 未触及图16 触发面（图 YAML/校验器/生成器/骨架）"

    # 校验逻辑单一真源，懒加载防 zephyr↔scripts 成环（先例=map_family 同族）
    if str(_VALIDATORS_DIR) not in sys.path:
        sys.path.insert(0, str(_VALIDATORS_DIR))
    try:
        from validate_governance_legislation_map import (  # noqa: E402  sys.path 动态加载：判据单一真源，懒加载防成环
            check_prose_counts,
            validate_structure,
        )
    except Exception as e:  # noqa: BLE001 — 校验器不可达=fail-closed
        logger.error("GOVERNANCE-LEGISLATION-MAP gate: 校验器加载失败（fail-closed）: %s", e)
        return False, f"GOVERNANCE-LEGISLATION-MAP: 校验器 {_VALIDATOR_MOD} 加载失败（fail-closed）: {e}"

    try:
        raw = _MAP_PATH.read_text(encoding="utf-8")
        data = yaml.safe_load(raw)
    except Exception as e:  # noqa: BLE001 — 真源损坏=fail-closed
        logger.error("GOVERNANCE-LEGISLATION-MAP gate: 图真源解析失败（fail-closed）: %s", e)
        return False, f"GOVERNANCE-LEGISLATION-MAP: {_MAP_REL} 解析失败（fail-closed，真源损坏须先修）: {e}"
    if not isinstance(data, dict):
        return False, f"GOVERNANCE-LEGISLATION-MAP: {_MAP_REL} 顶层非对象（真源损坏须先修）"

    warnings: list[str] = []
    try:
        errors = list(validate_structure(data, root=_REPO_ROOT, warnings=warnings, live=False))
        errors += check_prose_counts(data)
    except Exception as e:  # noqa: BLE001 — 校验器抛异常=fail-closed
        logger.error("GOVERNANCE-LEGISLATION-MAP gate: 结构校验异常（fail-closed）: %s", e)
        return False, f"GOVERNANCE-LEGISLATION-MAP: 结构校验异常（fail-closed）: {e}"

    for w in warnings:  # 外部真源面不可达/口径提示=随结论留痕，绝不升级为阻断
        logger.warning("GOVERNANCE-LEGISLATION-MAP gate（降级项）: %s", w)

    if errors:
        detail_lines = "\n".join(f"  - {x}" for x in errors)
        detail = (
            f"GOVERNANCE-LEGISLATION-MAP：治理立法流图结构校验 {len(errors)} 项 error"
            f"（states={len(data.get('states') or [])} "
            f"machinery={len(data.get('machinery') or [])} "
            f"transitions={len(data.get('transitions') or [])} "
            f"forbidden={len(data.get('forbidden_edges') or [])}）\n{detail_lines}\n"
            f"-> 修复真源后重提：状态/机构/迁移语义改 {_SKELETON_REL}（骨架=契约），"
            f"实例计数重跑生成器回灌（禁手改图不回生成；账本=REG-RULING-001 唯一实例真源）"
            "（六态闭集/终态无出边/禁边不可同对绕过/保险丝下限/实例禁入 nodes/计数只进 counts）"
        )
        logger.error("GOVERNANCE-LEGISLATION-MAP gate block:\n%s", detail)
        return False, detail
    logger.info("GOVERNANCE-LEGISLATION-MAP gate: 结构校验通过（触发面=%s）", ",".join(triggered))
    return True, ""
