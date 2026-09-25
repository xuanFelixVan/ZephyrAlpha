# [MODULE] zephyr.governance.registry_projection
# [DOMAIN] D_GOV_CODE_QUALITY
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §W-M1
# [TTL] permanent
# [DEPENDENCIES] （子模块聚合出口）
# [CONSUMERS] scripts/governance/registry_projection/；REGISTRY-YAML-PARSE 执法扩展；belt daemon 探针
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] YAML := render(PG 账本快照) 单向投影：生成器是投影册唯一合法写者，
#   读端零改动（11 读端继续读本地 YAML，永不触 PG——丙号文支柱③）
# [MODIFY-GUARD] 新建 2026-09-23 st-wm1-buildB-20260923（W-M1 波0 车道B）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
"""registry_projection — 注册表 PG 账本 → YAML 只读投影（W-M1 车道B）。

公开面：render/render_field（纯函数渲染）、snapshot_from_yaml/canonicalize（快照模型）、
load_state/save_state/classify（投影状态+四象限）、run（生成器编排 check/render）。
执法链挂点：registry_yaml_parse_gate 扩展（own-scope）+ belt daemon registry_drift 记账。


# [ALGO_FLOW]
层: 出口
- 聚合再导出投影子系统公共面（快照模型/渲染器/状态/只读源/编排器），无独立算法流程"""

from typing import Final

from zephyr.governance.registry_projection.model import (
    ProjectionSnapshot,
    Section,
    canonicalize,
    entry_identity_key,
    snapshot_from_yaml,
)
from zephyr.governance.registry_projection.projection_generator import default_registry, run
from zephyr.governance.registry_projection.renderer import SemanticMismatch, render, self_check
from zephyr.governance.registry_projection.state import (
    ProjectionState,
    classify,
    load_state,
    save_state,
    state_path,
)

__all__: Final = [
    "ProjectionSnapshot",
    "ProjectionState",
    "Section",
    "SemanticMismatch",
    "canonicalize",
    "classify",
    "entry_identity_key",
    "load_state",
    "render",
    "save_state",
    "self_check",
    "snapshot_from_yaml",
    "state_path",
]
