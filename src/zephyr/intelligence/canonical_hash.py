# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §canonical_hash
# [MODULE] zephyr.intelligence.canonical_hash
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] hashlib, json（标准库）
# [CONSUMERS] zephyr.intelligence.model_profiling.dual_run（freeze_hash）；zephyr.intelligence.switch_engine.criteria（criteria_sha256）
# [STARTUP] manual
# [MATURITY] evolving
# [INVARIANTS] 规范化口径=sort_keys+紧凑分隔符+UTF-8 字节，跨进程字节级可复现；
#              同 payload 恒同哈希，改任意叶子字段（含嵌套）哈希必变（判据冻结语义的公共底座）；
#              CloneGuard 合并件：dual_run/criteria 两处同构实现收敛于此（extract 级克隆零逃生）
# [MODIFY-GUARD] 改规范化口径=破坏既有冻结哈希可比性，须 OBJ_R 提案+新版本号
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] payload 不可 JSON 序列化→TypeError 上抛（不静默降级）
# [TESTS] tests/intelligence/test_canonical_hash.py
# [TTL] permanent
"""canonical_hash — 规范化 JSON sha256 公共底座（判据冻结/防篡改指纹共用）。

消费方：OBJ_M 双跑判据冻结（freeze_hash）与 L6 切换判据冻结（criteria_sha256）。
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Final

__all__: Final[list[str]] = ["canonical_json_sha256"]

_CANONICAL_KWARGS: Final[dict[str, Any]] = {
    "sort_keys": True,
    "ensure_ascii": False,
    "separators": (",", ":"),
}


def canonical_json_sha256(payload: Any) -> str:
    """规范化 JSON sha256（sort_keys+紧凑分隔符，十六进制）。

    稳定性约定：``json.dumps(sort_keys=True, ensure_ascii=False,
    separators=(",", ":"))``——键序归一、无空白差异，同 payload 恒同哈希。
    """
    canonical = json.dumps(payload, **_CANONICAL_KWARGS)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
