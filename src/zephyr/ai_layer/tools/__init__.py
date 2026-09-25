# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_tools
# [MODULE] zephyr.ai_layer.tools
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] 零依赖（本包公共常量层；子模块互不在 __init__ 引入，防环）
# [CONSUMERS] zephyr.ai_layer.tools.inventory_generator（T1 盘点生成器）;
#             zephyr.ai_layer.tools.usage_stats（T1 运营态计量）;
#             zephyr.ai_layer.tools.suite / scoring（T2 基准任务集考尺+Tier B 判分）;
#             L4 comparator.venue_tool_bench（RULER 指针待改一处常量接通，见包说明）
# [STARTUP] event_driven
# [MATURITY] new
# [INVARIANTS] 本文件只放跨子模块公共枚举/异常，零业务逻辑、零 IO；
#              organ 词表（hand|eye|foot）与 OBJ_T DESIGN §2.1 同源（改一处必改两处，测试护栏）；
#              stat_source 词表（telemetry|audit_jsonl|failures_dir|manual_v0）与 usage_stats
#              DDL CHECK 约束同表驱动
# [MODIFY-GUARD] docs/_working/ai_layer_vision/OBJ_T_tools/DESIGN.md §2/§3（设计真源，判据改动走 OBJ_R）
# [STABILITY] new
# [SAFETY] L
# [ALGO_FLOW] external: docs/03_modules/_domain_ai_layer/algo_flow/tools_pkg.yaml
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 本包公共异常：ToolBenchError 基类；子模块各自派生（词表外值一律拒收）
# [TESTS] tests/ai_layer/tools/（词表一致性护栏在 test_package_vocab.py 所在目录合跑）
# [TTL] permanent
"""tools — OBJ_T 工具对象线（T1 盘点/T2 考尺/T4 配对消费面）。

设计真源：``docs/_working/ai_layer_vision/OBJ_T_tools/DESIGN.md``（design_v1）。
子模块图::

    inventory_generator  T1 五源聚合盘点生成器 → config/tool_inventory.yaml   [C1]
    usage_stats          T1 运营态计量（ai_tools.tool_usage_stats 三源接线）   [C2]
    scoring              T2 Tier B 判分（Wilson 区间/效应量门槛/红线一票否决）  [C3]
    suite                T2 考尺（考卷装载 fail-closed+venue_tool_bench 契约）  [C3/C4]

考场接线现状（诚实声明）：L4 ``venue_tool_bench.RULER_MODULES`` 指针锁定
``zephyr.intelligence.tool_bench.suite``——本包考尺落位 ``zephyr.ai_layer.tools.suite``
（宪法红线：本班禁改既有文件，改指针=后续授权批一处常量改动）；指针缺席期间
L4 考场维持 fail-closed 拒考既定态，本包 suite 契约面已按该指针预期的
``suite_criteria()``/``suite_run(payload)`` 形态对齐（C4 验收=考卷 schema 对齐）。
"""

from __future__ import annotations

from typing import Final

__all__: Final = [
    "ToolBenchError",
    "ORGANS",
    "STAT_SOURCES",
    "KINDS",
    "SAFETY_LEVELS",
    "DELETE_CLASSES",
    "STATUSES",
]


class ToolBenchError(Exception):
    """OBJ_T 工具线基类异常（fail-closed 语义；子模块派生专用）。

    :param details: 敏感上下文（路径等）走 details 不进消息文本（5.99.20）。
    """

    def __init__(self, msg: str, *, details: dict[str, str] | None = None) -> None:
        super().__init__(msg)
        self.details: dict[str, str] = details or {}


ORGANS: Final = ("hand", "eye", "foot")
STAT_SOURCES: Final = ("telemetry", "audit_jsonl", "failures_dir", "manual_v0")
KINDS: Final = ("script", "skill", "mcp_server", "cli", "builtin", "plugin", "card")
def _load_safety_levels() -> tuple[str, ...]:
    """safety_level 词表 SSoT 动态加载（fail-open 回退内置三元组）。"""
    try:
        import yaml as _yaml
        from zephyr.shared.io.paths import REPO_ROOT
        doc = _yaml.safe_load((REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "vocabularies" / "safety_level_vocabulary.yaml").read_text(encoding="utf-8"))
        vals = doc.get("safety_levels") or doc.get("values") or []
        if isinstance(vals, list) and vals:
            out = []
            for v in vals:
                if isinstance(v, dict) and "value" in v:
                    out.append(str(v["value"]))
                elif isinstance(v, str):
                    out.append(v)
            if out:
                return tuple(out)
    except Exception:  # noqa: BLE001 — fail-open 回退（词表缺席不炸包导入）
        pass
    return tuple("LMH")


SAFETY_LEVELS: Final = _load_safety_levels()
DELETE_CLASSES: Final = ("none", "owner_gated", "tombstone", "ttl_only")
STATUSES: Final = ("active", "trial", "tombstone")

# 包公共面显式重导出（2026-09-24 st-ailayer-final-20260924：suite 由 venue_tool_bench RULER_MODULES 字符串动态导入，静态不可见需包级边）
from . import inventory_generator  # noqa: F401
from . import scoring  # noqa: F401
from . import suite  # noqa: F401
from . import usage_stats  # noqa: F401
