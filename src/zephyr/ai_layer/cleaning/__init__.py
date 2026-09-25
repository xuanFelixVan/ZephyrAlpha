# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_cleaning
# [MODULE] zephyr.ai_layer.cleaning
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] （见正文/DESIGN）
# [CONSUMERS] CLI 与段内消费方（见各模块头）
# [STARTUP] manual
# [MATURITY] evolving
# [INVARIANTS] （见正文/DESIGN）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/（段 DESIGN.md）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] （见正文/DESIGN）
# [TESTS] tests/ai_layer/（对应段测试目录）
# [TTL] permanent
"""cleaning — AI 层 L3 清洗段（强模型消化：规格重写 + 抽验 + 零执行边界）。

设计真源：``docs/_working/ai_layer_vision/L3_cleaning/DESIGN.md``。
模块清单：policy（考尺装载）/spec_store（规格卡库）/local_prefill（本地预洗）/
washer（清洗执行器）/auditor（抽验审计器）。外部 fetched 代码零执行（DESIGN §2.3
E0-E6）；全部 LLM 调用经 LSG 网关（P2，零裸调）。生食库模块，产线代码禁 import。
"""

from __future__ import annotations

from typing import Final

__all__: Final[list[str]] = ["auditor", "local_prefill", "policy", "spec_store", "washer"]

# 包公共面显式重导出（2026-09-24 st-ailayer-final-20260924：ORPHAN-MODULE 静态可见性——
# washer/auditor 为运行时回调注入与 CLI 派发消费，静态扫描需包级 import 边）
from . import auditor  # noqa: F401
from . import local_prefill  # noqa: F401
from . import policy  # noqa: F401
from . import spec_store  # noqa: F401
from . import washer  # noqa: F401
