# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §W-M1
# [MODULE] zephyr.governance.registry_ledger.ledger_identity
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates.registry_mass_deletion_gate（try import，失败降级本地同规则）
# [CONSUMERS] api.py; baseline.py; registry_projection model/renderer
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 身份键唯一真源桥永不复制逻辑；复合键=首标量|token=值 与合并器同规则；等值由红蓝机械断言
# [MODIFY-GUARD] 新建 2026-09-23 st-wm1-buildA-20260923；2026-09-25 wave0 改名 ledger_identity（N-16 basename 唯一）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 非 dict/首字段非标量=返回 None（passthrough 边界，不 raise）
# [TESTS] tests/governance/test_registry_ledger.py（复合键 B22 同构断言）
# [TTL] permanent
"""条目身份键（账本/门禁/合并器三方同一真源，永不复制逻辑）。
# [ALGO_FLOW]

首标量键真源=门禁 entry_identity_key（registry_family/registry_mass_deletion_gate，
夜班手术一重组位）。该重组位落地前 HEAD 侧 gate 尚未导出单条函数——此处先本地
实现同规则（与 gate `_entry_identity_keys` 单条分支逐字同规则），重组位一落地
import 自动切换，等值由 tests/governance/test_registry_ledger.py 对
_merge_entry_identity 机械断言，防身份分叉。复合键升级规则与
commit_queue_landing._merge_entry_identity 同一条规则（`首标量|token=值`），
结构等价对 batch_creation_tokens B22 (file,token) 二元组断言。
"""

from __future__ import annotations

try:  # 重组位落地后走门禁真源
    from zephyr.gov_enforcement.commit_gates.registry_mass_deletion_gate import (  # noqa: F401
        entry_identity_key as _gate_entry_identity_key,
    )
except ImportError:  # 门禁模块不可用时降级本地同规则
    _gate_entry_identity_key = None


def entry_identity_key(item: object) -> str | None:
    """单条目身份键：每条首个标量字段 → ``"key=value"``（gate 同规则）。"""
    if _gate_entry_identity_key is not None:
        return _gate_entry_identity_key(item)
    if not isinstance(item, dict) or not item:
        return None
    first = next(iter(item))
    value = item[first]
    if isinstance(value, (str, int, float, bool)):
        return f"{first}={value}"
    return None


def entry_composite_key(payload: dict) -> str | None:
    """账本条目身份键：gate 单键 + token 复合升级（首标量|token=值）。

    纯标量族（首字段非标量）返回 None——账本侧 passthrough 不入条目表，
    与 W2 合并器判据同源同边界。
    """
    base = entry_identity_key(payload)
    if base is None or not isinstance(payload, dict):
        return base
    token = payload.get("token")
    if isinstance(token, (str, int, float)) and token is not None:
        return f"{base}|token={token}"
    return base
