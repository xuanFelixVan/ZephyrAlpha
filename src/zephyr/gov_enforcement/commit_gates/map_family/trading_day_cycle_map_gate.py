# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §trading_day_cycle_map_gate
# [MODULE] zephyr.gov_enforcement.commit_gates.map_family.trading_day_cycle_map_gate
# create-guard-not-dup: 图13 交易日循环图提交门（阻塞语义封装体，校验逻辑单一真源=validate_trading_day_cycle_map 复用禁复制）；探针泛词命中系 docstring 描述装图动作片段，本件不实现既有 canonical 能力，与图族 DATA-SUPPLY-CHAIN-MAP gate 同形异真源（图13 48节点契约独立判据面）
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.validate_trading_day_cycle_map（validate_structure
#   单一真源，sys.path 动态加载——校验逻辑禁复制）
# [CONSUMERS] zephyr.gov_enforcement.commit_gates.panorama_alignment_gate（MAP-ALIGNMENT 聚合台 subs 清单
#   第 8 子检查——转正批 st-tclose-fig13reg-20261004 兑现生成器 [CONSUMERS] 声明；
#   token trading-day-cycle-map-trading-day-cycle-map-gate-20260924 系 st-mapbuild-20260924 预登记在册）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 硬阻断（确定性结构校验）——config/trading_day_cycle_map.yaml 经 validate_structure 判
#   error>0 → 阻断 commit（四段归属/slot_source 在册实存/越域判据字段/CV-L0/CV-BUS/CV-DUAL/CV-GAP/
#   CV-ADMIT/CV-DANGLE/CV-BLOOD/INV-1+cron 字面量）；触发式——本 commit（files∪held）触及图输入面
#   （图 YAML+生成器+校验器+排班两册+调度器+骨架+path_ownership+TDM 真源）才跑全量；own_scope=None
#   退化恒跑保守；YAML 解析异常=fail-closed（真源损坏必须先修）；血肉未满=blood_stage=f1_pending 期
#   validator warn 级不拦（F2 批灌肉翻 f2_done 后随裁定转硬）
# [MODIFY-GUARD] gate_id="TRADING-DAY-CYCLE-MAP"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] validator 加载失败/YAML 损坏=fail-closed 阻断；外部面不可达由 validator 内部降 warn
#   （禁环境异常打死无辜提交）；schema 0.2/0.3 均在支持域（加性迁移白名单）
# [TESTS] tests/governance/commit_gates/test_trading_day_cycle_map_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-MAP-MOUNT-012-001
"""trading_day_cycle_map_gate.py — 图13（交易日循环全景图）结构校验门（TRADING-DAY-CYCLE-MAP，经 MAP-ALIGNMENT 聚合台）

病根（第一性原理）
-----------------
图13 真源 config/trading_day_cycle_map.yaml 是机生图（生成器
generate_trading_day_cycle_map.py 的 [CONSUMERS] 自 09-24 起声明校验器/对抗测试为消费面），
但校验器此前从未落地、gate 通道不存在——图 YAML 被裸改/改坏时无任何提交门拦截。
st-tclose-fig13reg-20261004 转正批治本：validate_trading_day_cycle_map.py 落地（48 节点契约
判据单一真源）后，本门把校验器接进 MAP-ALIGNMENT 聚合台（panorama_alignment_gate subs 清单，
同 DATA-SUPPLY-CHAIN-MAP 先例），坏图在 commit 时硬拦。

设计权衡
--------
1. **触发式**：本 commit（files∪held）触及图输入面才跑全量校验；无归属信息退化恒跑
   保守（先例：decision_map_gate/data_supply_chain_map_gate 同款）。
2. **error=阻断**：validator 全部确定性判据，gate 只封阻塞语义禁复制。
3. **血肉分阶段**：blood_stage=f1_pending 期四字段空默认值由 validator 降 warn——
   schema 0.3 升级与血肉填充（F2 批）不同窗时，不把全图提交打死；翻 f2_done 后转 error。
4. **YAML 异常=阻断**：图真源损坏时全部缺口检测失效，必须先修图再提交。

Usage::

    # 经 panorama_alignment_gate 的 subs 清单自动接入（MAP-ALIGNMENT），无需手动注册：
    ("TRADING-DAY-CYCLE-MAP", "map_family.trading_day_cycle_map_gate", "_check")

# [ALGO_FLOW] external: docs/03_modules/_domain_gov_enforcement/algo_flow/trading_day_cycle_map_gate.yaml
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

__all__: Final = ["make_trading_day_cycle_map_gate", "_check"]

# 校验逻辑单一真源（validators/ 目录），动态加载（先例：data_supply_chain_map_gate）。
# parents[5]=仓根（map_family/ 子包比 flat 深一层——flat 布局的 parents[4] 迁移件必须同步加深，
# 否则 sys.path 指向 src/scripts 幽灵目录，生产侧校验器加载必 fail-closed）
_VALIDATORS_DIR = Path(__file__).resolve().parents[5] / "scripts" / "governance" / "d5_architecture" / "validators"

# 图输入面（触发式收窄真源）：与生成器 scan_* 读取面一一对应（generate_trading_day_cycle_map.py
# 的 [DEPENDENCIES]/[CONSUMERS] 声明面）。常量侧 os.path.normcase 与 _norm_rel 输出同域可比。
_MAP_INPUT_EXACT: Final = frozenset(
    os.path.normcase(p)
    for p in (
        "config/trading_day_cycle_map.yaml",
        "scripts/governance/d5_architecture/generators/generate_trading_day_cycle_map.py",
        "scripts/governance/d5_architecture/validators/validate_trading_day_cycle_map.py",
        "src/zephyr/data/config/schedule.yaml",
        "src/zephyr/data/config/tasks.yaml",
        "src/zephyr/data/scheduler.py",
        "src/zephyr/plan_engine/daily_loop_master_switch.py",
        "src/zephyr/data/trading_calendar.py",
        "docs/_working/map_build/fig13_daycycle/00_skeleton.md",
        "docs/03_modules/path_ownership_map.yaml",
        "config/trading_decision_map.yaml",
        "src/zephyr/data/config/resource_profile_registry.yaml",
    )
)

_MAP_YAML_REL: Final = "config/trading_day_cycle_map.yaml"


def _is_map_input(norm_rel: str) -> bool:
    """normcase 归一后的相对路径是否命中图13输入面。"""
    return norm_rel in _MAP_INPUT_EXACT


def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
    """图13 结构校验闭包（经 MAP-ALIGNMENT 聚合台 subs 调用）。"""
    own_scope = _build_own_scope(gateway, files, kwargs.get("session_id"))
    if own_scope is not None and not any(_is_map_input(p) for p in own_scope):
        return True, "skip: 本 commit 未触及图13输入面（触发式收窄，先例 data_supply_chain_map_gate）"

    if str(_VALIDATORS_DIR) not in sys.path:
        sys.path.insert(0, str(_VALIDATORS_DIR))
    try:
        # 新鲜加载（2026-10-05 修）：驻留 serializer 进程的 sys.modules 缓存会让本 gate
        # 复用旧版校验器——袋内同步升级的 validator/map 永不被读到（0009/0011 袋死实例），
        # 逐次 importlib 强制重载，契约常量随盘面即时生效
        import importlib

        _mod = importlib.import_module("validate_trading_day_cycle_map")
        _mod = importlib.reload(_mod)
        validate_structure = _mod.validate_structure
    except Exception as e:  # noqa: BLE001 — 校验器不可达=fail-closed
        logger.error("TRADING-DAY-CYCLE-MAP gate: 校验器加载失败（fail-closed）: %s", e)
        return False, f"TRADING-DAY-CYCLE-MAP: 校验器 validate_trading_day_cycle_map 加载失败（fail-closed）: {e}"

    import yaml

    map_path = Path(gateway.repo_root) / _MAP_YAML_REL if hasattr(gateway, "repo_root") else Path(_MAP_YAML_REL)
    try:
        data = yaml.safe_load(map_path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001 — 真源损坏=fail-closed（须先修图）
        logger.error("TRADING-DAY-CYCLE-MAP gate: 图 YAML 解析异常（fail-closed）: %s", e)
        return False, (
            f"TRADING-DAY-CYCLE-MAP: {_MAP_YAML_REL} 解析异常（真源损坏须先修）: {e}\n"
            "-> 重跑 scripts/governance/d5_architecture/generators/generate_trading_day_cycle_map.py"
        )

    warns: list[str] = []
    try:
        errors = validate_structure(data, map_path.parents[1] if map_path.parents else None, warns)
    except Exception as e:  # noqa: BLE001 — 判据异常=fail-closed
        logger.error("TRADING-DAY-CYCLE-MAP gate: validate_structure 异常（fail-closed）: %s", e)
        return False, f"TRADING-DAY-CYCLE-MAP: validate_structure 异常（fail-closed）: {e}"

    if errors:
        detail_lines = "\n".join(f"  - {x}" for x in errors[:20])
        detail = (
            f"TRADING-DAY-CYCLE-MAP：图13 校验 {len(errors)} 项 error\n{detail_lines}\n"
            "-> 修复后重提（机生面走生成器重跑，禁手改："
            "python scripts/governance/d5_architecture/generators/generate_trading_day_cycle_map.py）"
        )
        logger.error("TRADING-DAY-CYCLE-MAP gate block:\n%s", detail)
        return False, detail

    # 放行：warn 留痕（血肉未满计数——f1_pending 期降级，F2 批翻 f2_done 转硬）
    if warns:
        return True, f"pass: 血肉未满 warn={len(warns)}（blood_stage=f1_pending 期降级，F2 批灌肉翻闸后转硬）"
    return True, ""


def make_trading_day_cycle_map_gate() -> GateSpec:
    """单门工厂（保留兼容形态；实际经 panorama_alignment_gate subs 清单接入 MAP-ALIGNMENT）。"""
    return GateSpec(gate_id="TRADING-DAY-CYCLE-MAP", check=_check, priority=147)
