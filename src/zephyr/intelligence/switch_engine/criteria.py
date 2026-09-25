# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §l6_switch_engine
# [MODULE] zephyr.intelligence.switch_engine.criteria
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.io.paths (REPO_ROOT)
# [CONSUMERS] zephyr.intelligence.switch_engine.switch_engine (判据键消费);
#             zephyr.intelligence.switch_engine.shadow_runner (corpus 冻结核验);
#             zephyr.ai_layer.switch_engine.* (观察窗/TTL/演练参数读取)
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] config/switch_criteria.yaml 运行时只读禁写（改判据=新 switch_id，根约束
#              禁区）；冻结哈希=对 criteria: 键下全部内容做 canonical-JSON sha256
#              （sort_keys+紧凑分隔符，跨进程可复现可验）；缺文件/缺 criteria 键 fail-closed
#              抛错不降级；本模块不缓存文件内容（每次读盘，改盘即感知，配合新 switch_id 纪律）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L6_ab_switch/DESIGN.md §②-C/§④-S2；
#                YAML 数值修订走 OBJ_R 提案流水线
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] YAML 缺失→SwitchCriteriaError（fail-closed）；顶层非 mapping 或缺 criteria 键
#                  →SwitchCriteriaError；哈希入口只收 Mapping（类型错→TypeError 上抛）
# [TESTS] tests/intelligence/switch_engine/test_criteria.py（真 YAML 可载+DESIGN 原值核对/
#         canonical sha256 确定性/键序无关/载入缺失文件抛错/冻结三元组落 registry 形状）
# [TTL] permanent
"""criteria — L6 判据预注册 YAML 加载器 + sha256 冻结哈希（S2 施工件）。

config/switch_criteria.yaml 是主文档 §五 判据的工程化（同一真源非新增）。本模块把
"判据预注册冻结"从纪律变成机制：open_switch 时以 ``freeze`` 产出
(criteria_yaml_ref, criteria_hash) 写入 switch_registry；此后 L4 终裁/回切审议/演练
复核一律用冻结哈希核对——"判据档案=当时为什么算它赢"（L7 传承契约）直接消费本哈希。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Final

import yaml

from zephyr.shared.io.paths import REPO_ROOT

DEFAULT_CRITERIA_PATH: Final[Path] = REPO_ROOT / "config" / "switch_criteria.yaml"
CRITERIA_ROOT_KEY: Final[str] = "criteria"

_CRITERIA_ORIGINAL_VALUES: Final[dict[str, Any]] = {
    # DESIGN §②-C 原值（Owner 夜批追认生效；首轮数据后走 OBJ_R 提案修订）
    "t2_disagreement_rate_max": 0.05,
    "t3_perf_delta_pct_max": 20,
    "t3_consecutive_trading_days": 5,
    "t4_cost_increase_pct_max": 15,
}


class SwitchCriteriaError(RuntimeError):
    """判据错误（5.99.20：敏感上下文走 details 不进消息文本）。"""

    def __init__(self, msg: str, *, details: dict[str, str] | None = None) -> None:
        super().__init__(msg)
        self.details: dict[str, str] = details or {}
    """判据 YAML 缺失/形状非法（fail-closed，绝不降级到内置默认值）。"""


def load_criteria(path: Path | None = None) -> dict[str, Any]:
    """加载判据 YAML 并返回顶层 mapping；非法形状抛 SwitchCriteriaError。"""
    target = path or DEFAULT_CRITERIA_PATH
    if not target.is_file():
        raise SwitchCriteriaError("判据 YAML 缺失（fail-closed）", details={"target": str(target)})
    with target.open("r", encoding="utf-8") as fh:
        payload = yaml.safe_load(fh)
    if not isinstance(payload, dict) or CRITERIA_ROOT_KEY not in payload:
        raise SwitchCriteriaError(f"判据 YAML 形状非法：顶层需为 mapping 且含 {CRITERIA_ROOT_KEY!r} 键")
    return payload


def criteria_sha256(criteria_payload: dict[str, Any]) -> str:
    """canonical-JSON sha256：sort_keys+紧凑分隔符，跨进程字节级可复现。

    CloneGuard 合并：实现委托 dual_run.freeze_hash（extract 级克隆零逃生，
    落地序 OBJ_M 先于本包，导入恒可解析）。
    """
    from zephyr.intelligence.canonical_hash import canonical_json_sha256  # noqa: PLC0415
    return canonical_json_sha256(criteria_payload)


def freeze(path: Path | None = None) -> dict[str, str]:
    """产出 switch_registry 冻结三元组（criteria_yaml_ref + criteria_hash + frozen_at 键名约定）。

    返回 dict 直接并入 open_switch 入参；hash 恒对 ``criteria:`` 键下内容计算，
    meta 头（版本注释类）不参与——改 meta 不换 switch_id，改判据必换。
    """
    payload = load_criteria(path)
    target = path or DEFAULT_CRITERIA_PATH
    return {
        "criteria_yaml_ref": str(target),
        "criteria_hash": criteria_sha256(payload[CRITERIA_ROOT_KEY]),
    }


def verify_frozen(criteria_hash: str, path: Path | None = None) -> bool:
    """核验现值哈希与冻结哈希一致（L4 终裁/演练复核前必过）。不一致=False 不抛。"""
    payload = load_criteria(path)
    return criteria_sha256(payload[CRITERIA_ROOT_KEY]) == criteria_hash


def original_trigger_values() -> dict[str, Any]:
    """DESIGN §②-C 提案原值快照（测试核对 YAML 未漂移；文档用，非运行时判据）。"""
    return dict(_CRITERIA_ORIGINAL_VALUES)
