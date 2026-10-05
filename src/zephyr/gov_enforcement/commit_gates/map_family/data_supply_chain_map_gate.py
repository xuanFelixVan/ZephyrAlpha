# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §data_supply_chain_map_gate
# [MODULE] zephyr.gov_enforcement.commit_gates.map_family.data_supply_chain_map_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.validate_data_supply_chain_map（validate_structure 单一真源，sys.path 动态加载——校验逻辑禁复制）
# [CONSUMERS] zephyr.gov_enforcement.commit_gates.panorama_alignment_gate（MAP-ALIGNMENT 聚合台 subs 清单）——补齐 generate_data_supply_chain_map.py [CONSUMERS] 自 2026-09-25 起声明的幽灵消费方（st-vm12surg-20261003 治本：文档说有实则没有型缺陷）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 硬阻断（确定性结构校验）——config/data_supply_chain_map.yaml 经 validate_structure 判 error>0 → 阻断 commit（CV-L0/BUS/BLOOD/DUAL/FACET/GAP/WAIT）；触发式——本 commit（files∪held）触及图输入面（图 YAML+生成器+校验器+tasks/schedule/scheduler+资产册+path_ownership+数据域蓝图族）才跑全量；own_scope=None 退化恒跑保守；YAML 解析异常=fail-closed（真源损坏必须先修）；血肉完备腿=warn 级不拦（blood_stage=f1_pending 血肉未满期防误伤；F2 批填满+覆盖账本绿后随裁定翻硬——「落地即挂图」强制位预留）
# [MODIFY-GUARD] gate_id="DATA-SUPPLY-CHAIN-MAP"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] validator 加载失败/YAML 损坏=fail-closed 阻断；CV-BLOOD 在 blood_stage=f1_pending 时缺键由 validator 降 warn（不拦，F2 批翻 f2_done 转硬）
# [TESTS] tests/governance/commit_gates/test_data_supply_chain_map_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-MAP-MOUNT-012-001
# [CREATION-TOKEN] data-supply-chain-map-data-supply-chain-map-gate-20260924
"""data_supply_chain_map_gate.py — 图12（数据供给链图）结构校验门（DATA-SUPPLY-CHAIN-MAP，经 MAP-ALIGNMENT 聚合台）

病根（第一性原理）
-----------------
图12 真源 config/data_supply_chain_map.yaml 是双层图（机生层+语义层）：生成器
generate_data_supply_chain_map.py 的 [CONSUMERS] 自 2026-09-25 起就声明本 gate 为
消费方，但模块从未存在——图 YAML 被裸改/改坏时无任何提交门拦截（校验器
validate_data_supply_chain_map.py 存在却从未接进提交通道=「文档说有实则没有」型
幽灵引用）。st-vm12surg-20261003 手术批治本：把校验器接进 MAP-ALIGNMENT 聚合台
（panorama_alignment_gate subs 清单），断链/越域/INV-1 抄写/血肉键缺失（f2_done 后）
在 commit 时硬拦。

设计权衡
--------
1. **触发式**：本 commit（files∪held）触及图输入面才跑全量校验；无归属信息退化恒跑
   保守（先例：decision_map_gate 2026-09-11 Owner 批准收窄同款）。
2. **error=阻断**：validator 全部确定性判据（CV 规则族），gate 只封阻塞语义禁复制。
3. **血肉分阶段**：blood_stage=f1_pending 期 CV-BLOOD 缺键由 validator 降 warn——
   schema 升级（0.3）与血肉填充（F2 批）不同窗时，不把全图提交打死；翻 f2_done
   后转 error。
4. **落地即挂图（第一版 warn 腿）**：触及数据域蓝图（_domain_data*/blueprint）的
   commit，检查其 MOD-* 号是否出现在图 YAML 挂载面——不在仅 warn 不拦（当前全图
   血肉未满+覆盖账本未跑，硬拦=误伤；F2 填满+覆盖账本绿后随裁定翻硬）。
5. **YAML 异常=阻断**：图真源损坏时全体缺口检测失效，必须先修图再提交。

Usage::

    # 经 panorama_alignment_gate 的 subs 清单自动接入（MAP-ALIGNMENT），无需手动注册：
    ("DATA-SUPPLY-CHAIN-MAP", "map_family.data_supply_chain_map_gate", "_check")

# [ALGO_FLOW] external: docs/03_modules/_domain_gov_enforcement/algo_flow/commit_gates/d/data_supply_chain_map_gate.yaml
"""

from __future__ import annotations

import logging
import os
import re
import sys
from pathlib import Path
from typing import Final

from zephyr.gov_enforcement.commit_gates._diff_helpers import _build_own_scope, _norm_rel
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__: Final = ["make_data_supply_chain_map_gate", "_check"]

# 校验逻辑单一真源（validators/ 目录），动态加载（先例：decision_map_gate/check_decision_map）。
# parents[5]=仓根（map_family/ 子包比 flat 深一层，迁移件同步加深防 src/scripts 幽灵目录）
_VALIDATORS_DIR = Path(__file__).resolve().parents[5] / "scripts" / "governance" / "d5_architecture" / "validators"

# 图输入面（触发式收窄真源）：与生成器 scan_* 读取面一一对应（generate_data_supply_chain_map.py
# 的 *_REL 常量）+ 数据域蓝图族（落地即挂图 warn 腿的触发锚）。
# 常量侧同过 os.path.normcase（Windows=小写+反斜杠），与 _norm_rel 输出同域可比。
_MAP_INPUT_EXACT: Final = frozenset(
    os.path.normcase(p)
    for p in (
        "config/data_supply_chain_map.yaml",
        "scripts/governance/d5_architecture/generators/generate_data_supply_chain_map.py",
        "scripts/governance/d5_architecture/validators/validate_data_supply_chain_map.py",
        "src/zephyr/data/config/tasks.yaml",
        "src/zephyr/data/config/schedule.yaml",
        "src/zephyr/data/scheduler.py",
        "docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml",
        "docs/03_modules/path_ownership_map.yaml",
    )
)
_DATA_BLUEPRINT_PREFIXES: Final = tuple(
    os.path.normcase(p) for p in ("docs/03_modules/_domain_data/", "docs/03_modules/_domain_data_security/")
)

_MAP_YAML_REL: Final = "config/data_supply_chain_map.yaml"
_MOD_ID_RE: Final = re.compile(r"MOD-[A-Z0-9]+-[0-9]+")


def _is_map_input(norm_rel: str) -> bool:
    """normcase 归一后的相对路径是否命中图12输入面（含数据域蓝图族=挂图 warn 腿触发锚）。"""
    if norm_rel in _MAP_INPUT_EXACT:
        return True
    return norm_rel.startswith(_DATA_BLUEPRINT_PREFIXES) and norm_rel.endswith((".md", ".yaml"))


def _mount_coverage_warns(gateway, files: list[str], map_text: str) -> list[str]:
    """落地即挂图 warn 腿（第一版，不拦）：触及数据域蓝图的 commit，其 MOD-* 号不在图 YAML
    挂载面 → warn。血肉未满期硬拦=误伤（F2 批填满+覆盖账本绿后随裁定翻硬）。"""
    warns: list[str] = []
    for f in files:
        rel = _norm_rel(gateway, str(f))
        if not rel.startswith(_DATA_BLUEPRINT_PREFIXES) or not rel.endswith((".md", ".yaml")):
            continue
        try:
            head = Path(f).read_text(encoding="utf-8", errors="replace")[:4000]
        except OSError:
            continue
        for mod in sorted(set(_MOD_ID_RE.findall(head))):
            if mod not in map_text:
                warns.append(f"{rel}: MOD 号 {mod} 未挂任何纵向图节点（落地即挂图义务，SOP §1 四判据）")
    return warns


def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
    """图12 结构校验闭包（经 MAP-ALIGNMENT 聚合台 subs 调用）。"""
    own_scope = _build_own_scope(gateway, files, kwargs.get("session_id"))
    if own_scope is not None and not any(_is_map_input(p) for p in own_scope):
        return True, "skip: 本 commit 未触及图12输入面（触发式收窄，先例 decision_map_gate）"

    if str(_VALIDATORS_DIR) not in sys.path:
        sys.path.insert(0, str(_VALIDATORS_DIR))
    try:
        from validate_data_supply_chain_map import validate_structure  # noqa: import-integrity  sys.path 动态加载
    except Exception as e:  # noqa: BLE001 — 校验器不可达=fail-closed
        logger.error("DATA-SUPPLY-CHAIN-MAP gate: 校验器加载失败（fail-closed）: %s", e)
        return False, f"DATA-SUPPLY-CHAIN-MAP: 校验器 validate_data_supply_chain_map 加载失败（fail-closed）: {e}"

    import yaml

    map_path = Path(gateway.repo_root) / _MAP_YAML_REL if hasattr(gateway, "repo_root") else Path(_MAP_YAML_REL)
    try:
        data = yaml.safe_load(map_path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001 — 真源损坏=fail-closed（须先修图）
        logger.error("DATA-SUPPLY-CHAIN-MAP gate: 图 YAML 解析异常（fail-closed）: %s", e)
        return False, (
            f"DATA-SUPPLY-CHAIN-MAP: {_MAP_YAML_REL} 解析异常（真源损坏须先修）: {e}\n"
            "-> 重跑 scripts/governance/d5_architecture/generators/generate_data_supply_chain_map.py"
        )

    warns: list[str] = []
    try:
        errors = validate_structure(data, map_path.parents[1] if map_path.parents else None, warns)
    except Exception as e:  # noqa: BLE001 — 判据异常=fail-closed
        logger.error("DATA-SUPPLY-CHAIN-MAP gate: validate_structure 异常（fail-closed）: %s", e)
        return False, f"DATA-SUPPLY-CHAIN-MAP: validate_structure 异常（fail-closed）: {e}"

    if errors:
        detail_lines = "\n".join(f"  - {x}" for x in errors[:20])
        detail = (
            f"DATA-SUPPLY-CHAIN-MAP：图12 校验 {len(errors)} 项 error\n{detail_lines}\n"
            "-> 修复 config/data_supply_chain_map.yaml 后重提（语义层手改须 existing-wins 保留；"
            "机生面走生成器重跑，禁手改）"
        )
        logger.error("DATA-SUPPLY-CHAIN-MAP gate block:\n%s", detail)
        return False, detail

    # 放行：warn 腿留痕（血肉未满计数 + 落地即挂图缺口），不拦
    notes: list[str] = []
    if warns:
        notes.append(f"血肉未满 warn={len(warns)}（blood_stage=f1_pending 期降级，F2 批填满翻 f2_done）")
    try:
        map_text = map_path.read_text(encoding="utf-8", errors="replace")
        mount_warns = _mount_coverage_warns(gateway, list(files), map_text)
        if mount_warns:
            notes.append("落地即挂图 warn 腿：" + "; ".join(mount_warns[:5]))
    except OSError:
        pass
    return True, ("pass: " + " | ".join(notes)) if notes else ""


def make_data_supply_chain_map_gate() -> GateSpec:
    """单门工厂（保留兼容形态；实际经 panorama_alignment_gate subs 清单接入 MAP-ALIGNMENT）。"""
    return GateSpec(gate_id="DATA-SUPPLY-CHAIN-MAP", check=_check, priority=146)
