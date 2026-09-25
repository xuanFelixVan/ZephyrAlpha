# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_comparator
# [MODULE] zephyr.ai_layer.comparator
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] 零依赖（本包公共原语层；子模块互不在 __init__ 引入，防环）
# [CONSUMERS] zephyr.ai_layer.comparator.executor / fairness / too_good / venue_* / compare_events;
#             L5 排产（verdict 裁定卡消费方，设计预留）；L7 判据档案（comparison_archived_due 消费方，设计预留）
# [STARTUP] event_driven
# [MATURITY] new
# [INVARIANTS] 本文件只放跨子模块公共原语（异常/枚举/判定结果），零业务逻辑、零 IO；
#              考场枚举 VENUE_IDS 与 experiment_store DDL CHECK 约束同表驱动（改一处必改两处，测试护栏）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L4_compare/DESIGN.md §2/§4（设计真源）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RefuseExam 聚合拒考原因清单（fail-closed 语义，永不部分通过）；VenueUnavailable
#                  表示考尺不可达（适配器 fail-closed 拒考，DESIGN C4 验收标准）
# [TESTS] tests/ai_layer/comparator/（VENUE_IDS 与 store DDL 枚举一致性护栏在 test_experiment_store.py）
# [TTL] permanent
"""comparator — L4 对比段：通用对比器（考卷统一、裁定统一、独立性机检）。

设计真源：``docs/_working/ai_layer_vision/L4_compare/DESIGN.md``（D-L4-01：L4 不自建考尺，
做协议层+登记层）。子模块图::

    experiment_store  实验卡库（ai_compare schema DDL+预注册/流转服务）   [C2]
    executor          对比执行器（领考/三锁机检/裁定卡签发）              [C3]
    venue_c4/replay/dual_run/tool_bench  考场适配器×4（薄封装，fail-closed）[C4]
    fairness          公平性对齐器（三轴+防假胜三条）                    [C5]
    too_good          too-good 三查执行器（G1-G5+三查+三出口）           [C6]
    compare_events    L7 接线（comparison_archived_due+先验只读查询）     [C8]

考场边界（DESIGN §2.1 声明）：策略候选的考场止于 L4 证据包产出；verdict 只是证据，
不构成任何策略上线/转正动作（AI 层不设第二转正门）。
"""

from __future__ import annotations

import importlib
import importlib.util
from dataclasses import dataclass
from typing import Any, Final, Sequence

__all__: Final = [
    "CompareCheckResult",
    "RefuseExam",
    "VENUE_IDS",
    "VenueUnavailable",
    "import_ruler",
    "ruler_available",
]

VENUE_IDS: Final = ("venue_c4", "venue_replay", "venue_dual_run", "venue_tool_bench")


class VenueUnavailable(Exception):
    """考尺不可达（import 失败/件未建成）——适配器 fail-closed 拒考（DESIGN C4）。"""


def import_ruler(module_name: str) -> Any:
    """考尺模块惰性导入（fail-closed：调不到考尺=VenueUnavailable 拒考，DESIGN C4 验收标准）。"""
    try:
        return importlib.import_module(module_name)
    except ImportError as exc:
        raise VenueUnavailable(f"ruler_unreachable:{module_name}:{exc}") from exc


def ruler_available(module_names: Sequence[str]) -> bool:
    """考尺在场探测（find_spec，零副作用；探测异常一律判不可达——缺省从重 fail-closed）。"""
    try:
        return all(importlib.util.find_spec(name) is not None for name in module_names)
    except (ImportError, ValueError, AttributeError):
        return False


class RefuseExam(Exception):
    """拒考（fail-closed）：携带全部未通过机检的 reason 清单，绝不部分通过。"""

    def __init__(self, reasons: list[str]) -> None:
        self.reasons: Final = list(reasons)
        super().__init__("refuse_exam:" + ";".join(self.reasons))


@dataclass(frozen=True)
class CompareCheckResult:
    """单道机检结果（name/passed/reason 三元，聚合进 ComparePreflightReport 或 FairnessReport）。"""

    name: str
    passed: bool
    reason: str = "ok"

# 包公共面显式重导出（2026-09-24 st-ailayer-final-20260924：ORPHAN-MODULE 静态可见性——
# executor 为 claim_exam 注册表派发、compare_events/fairness 为账本与裁定供源，静态扫描需包级 import 边）
def make_available_probe(ruler_modules, namespace):
    """生成考场级 available() 探针（FUNCTION-DUP 治本 2026-09-24：四考场同体探测唯一实现）。

    namespace=各考场模块 globals——available() 调用时动态解析 namespace["ruler_available"]，
    测试 monkeypatch（setattr 模块属性）保持可拦截语义。
    """
    def available() -> bool:
        return namespace["ruler_available"](ruler_modules)
    return available

from . import compare_events  # noqa: F401
from . import executor  # noqa: F401
from . import fairness  # noqa: F401
from . import policy  # noqa: F401
from . import too_good  # noqa: F401
from . import venue_c4  # noqa: F401
from . import venue_dual_run  # noqa: F401
from . import venue_replay  # noqa: F401
from . import venue_tool_bench  # noqa: F401

# 包公共面显式重导出（2026-09-24 st-ailayer-final-20260924：ORPHAN-MODULE 静态可见边——动态派发消费型模块）
from . import venue_c4  # noqa: F401
from . import venue_dual_run  # noqa: F401
from . import venue_replay  # noqa: F401
from . import venue_tool_bench  # noqa: F401


