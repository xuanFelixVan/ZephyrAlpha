# scripts/governance/d5_architecture/panorama_common.py
# [BLUEPRINT] MOD-GOV-SYNC-PANORAMA | docs/_working/2026-07-10-panorama_remediation_plan.md | §Task1
# [MODULE] scripts.governance.d5_architecture.panorama_common
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] 无（纯函数，无外部依赖）
# [CONSUMERS] align_panoramas; blueprint_frontmatter_reconciler; sync_panorama_module
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 纯函数无副作用;确定性输出(相同输入→相同输出);测试文件降权weight=0.1;平局按domain_id字母序
# [MODIFY-GUARD] weighted_domain_vote/min_maturity 为对外入口;MATURITY_RANK 为常量;_get_field 为内部辅助
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空输入→返回空字符串;无domain_id→返回空字符串;不抛异常
# [TESTS] tests/governance/test_panorama_common.py
# [TTL] permanent
# [ARCH-REF] #ARCH-056
"""panorama_common.py — 四图投票共享工具（ARCH-056 引擎加固）

提供确定性域投票函数，消除 3 个引擎文件中 Counter.most_common 平局不稳定的问题。

核心规则：
  1. 测试文件（path LIKE 'tests/%'）降权 weight=0.1
  2. 平局时按 domain_id 字母序 tie-break（不依赖 SQL ORDER BY）
  3. 纯函数，无 DB 依赖，无副作用
"""
from __future__ import annotations

MATURITY_RANK: dict[str, int] = {"design": 0, "prototype": 1, "production": 2}

_TEST_PATH_PREFIX = "tests/"


def _get_field(row, key: str):
    """从 dict 或 tuple 行中取字段值。"""
    if isinstance(row, dict):
        return row.get(key)
    # tuple 兼容：无列名映射，无法安全取值
    return None


def weighted_domain_vote(rows: list) -> str:
    """加权域投票：测试文件降权（weight=0.1），平局按 domain_id 字母序。

    Args:
        rows: DB 查询返回的行列表（dict 或 tuple）
    Returns:
        代表性 domain_id，空列表/无域返回 ""
    """
    weighted: dict[str, float] = {}
    for row in rows:
        dom = _get_field(row, "domain_id")
        if not dom:
            continue
        path = _get_field(row, "path") or _get_field(row, "blueprint_path") or ""
        weight = 0.1 if path.startswith(_TEST_PATH_PREFIX) else 1.0
        weighted[dom] = weighted.get(dom, 0.0) + weight
    if not weighted:
        return ""
    # 票数降序 + domain_id 字母升序（确定性 tie-break）
    return sorted(weighted, key=lambda k: (-weighted[k], k))[0]


def min_maturity(maturities: list[str]) -> str:
    """取最 design 的状态（design < prototype < production）。

    聚合策略：min rank（design=0 < prototype=1 < production=2）。
    """
    if not maturities:
        return ""
    return min(maturities, key=lambda v: MATURITY_RANK.get(v, 99))
