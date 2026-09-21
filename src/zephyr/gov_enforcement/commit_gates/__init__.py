# [BLUEPRINT] MOD-GOV_COMMIT_GATES | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.gov_enforcement.commit_gates
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES]
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_COMMIT_GATES | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

commit_gates — GitCommitGateway pre-commit 门禁实现包。

每个 gate 一个文件 + ``make_*_gate()`` 工厂函数，返回 ``GateSpec``。
注册到 ``GitCommitGateway._gate_registry``（见 commit_gate_registry.py）。

新增门禁流程（gate_registry.yaml 门禁注册制 + #ARCH-GATE-REGISTRY-AUTO-001 YAML 驱动自动注册）：
1. 在本包下创建 ``make_xxx_gate()`` 返回 ``GateSpec``
2. 在 ``in_process_gate_registry.yaml`` 追加条目（gate_id + module_path + factory_function）
3. ``gate_auto_registrar.py`` 启动时从 YAML 动态 import + register

禁止在 ``commit()`` 方法体硬编码 ``_check_*`` 调用（架构债务 #AD-001 治本）。

ORPHAN-MODULE 注意：gate 模块通过 YAML 动态加载（importlib），但 ORPHAN-MODULE gate
只检测静态 import 引用。新增 gate MUST 在下方 ``_ORPHAN_MODULE_STATIC_IMPORTS`` 区块
追加一行静态 import（``as _`` 别名，不 re-export），否则 commit 被 ORPHAN-MODULE 阻断。

# [ALGO_FLOW] external: docs/03_modules/_domain_gov_enforcement/algo_flow/commit_gates/c/commit_gates__init__.yaml
"""

# === ORPHAN-MODULE 静态引用区 ===
# gate 模块通过 gate_auto_registrar YAML 动态加载，但 ORPHAN-MODULE gate 只做静态
# `git grep` 检测。此处集中声明静态 import 引用（别名 _，不 re-export，包级 __all__ 不变）。
# 新增 gate 时在此追加一行。#ARCH-GATE-REGISTRY-AUTO-001 已知限制。
from zephyr.gov_enforcement.commit_gates.battle_map_alignment_gate import (  # noqa: F401  # GATE-BATTLE-MAP-ALIGNMENT 作战地图对齐硬化门禁（#ARCH-BATTLE-MAP-HARD-001 2026-09-05，三类升硬）
    make_battle_map_alignment_gate as _make_battle_map_alignment_gate,
)
from zephyr.gov_enforcement.commit_gates.blueprint_node_id_hardcode_gate import (  # noqa: F401
    make_blueprint_node_id_hardcode_gate as _make_blueprint_node_id_hardcode_gate,
)
from zephyr.gov_enforcement.commit_gates.business_registry_gate import (  # noqa: F401  # BUSINESS-REGISTRY 业务资产库入库门禁（#ARCH-BUSINESS-REG-GATE-001 2026-09-05，alignment_checklist §4.1 待建转正式）
    make_business_registry_gate as _make_business_registry_gate,
)
from zephyr.gov_enforcement.commit_gates.commit_scope_gate import (  # noqa: F401  # COMMIT-SCOPE 跨域混合提交治本（13a5e1d512 事故）
    make_commit_scope_gate as _make_commit_scope_gate,
)
from zephyr.gov_enforcement.commit_gates.decision_map_gate import (  # noqa: F401  # DECISION-MAP 交易决策地图对齐阻断门禁（七图对齐第7项，#ARCH-DECISION-MAP-GATE-001 2026-09-05）
    make_decision_map_gate as _make_decision_map_gate,
)
from zephyr.gov_enforcement.commit_gates.frontend_map_gate import (  # noqa: F401  # FRONTEND-MAP 前端全景图对齐阻断门禁（六图对齐 commit 链闭环，Owner 2026-09-04 裁定）
    make_frontend_map_gate as _make_frontend_map_gate,
)
from zephyr.gov_enforcement.commit_gates.frontend_truth_source_gate import (  # noqa: F401  # FRONTEND-TRUTH-SOURCE 前端真源接通铁律配套（TRAE-086 v1.2.0 §truth_source_wiring，Owner 2026-09-04 裁定）
    make_frontend_truth_source_gate as _make_frontend_truth_source_gate,
)
from zephyr.gov_enforcement.commit_gates.industry_chain_map_gate import (  # noqa: F401  # INDUSTRY-CHAIN-MAP 产业链全景图 git 侧工件门禁（图 8 挂总线，alignment_checklist §3 图 8 行 2026-09-11）
    make_industry_chain_map_gate as _make_industry_chain_map_gate,
)
from zephyr.gov_enforcement.commit_gates.library_coverage_gate import (  # noqa: F401  # LIBRARY-COVERAGE 图书馆覆盖度门禁（in_process_gate_registry 条目驱动；st-dloop 死会话遗物补记批完成注册，st-workclean-20260921）
    make_library_coverage_gate as _make_library_coverage_gate,
)
from zephyr.gov_enforcement.commit_gates.reconciler_file_ops_gate import (  # noqa: F401  # RECONCILER-FILE-OPS 裸删除原语静态扫描（#ARCH-RECONCILER-AUTO-DELETE-GOV-001 T1③）
    make_reconciler_file_ops_gate as _make_reconciler_file_ops_gate,
)
from zephyr.gov_enforcement.commit_gates.registry_code_anchor_gate import (  # noqa: F401  # REGISTRY-CODE-ANCHOR 业务注册表代码锚点门禁（#ARCH-BREG-002 门禁A）
    make_registry_code_anchor_gate as _make_registry_code_anchor_gate,
)
from zephyr.gov_enforcement.commit_gates.resource_schedule_gate import (  # noqa: F401  # RESOURCE-SCHEDULE 排班冲突检测门禁（资源排班全景 B2，own-scope，priority=144，MOD-RESCHED-GATE）
    make_resource_schedule_gate as _make_resource_schedule_gate,
)
from zephyr.gov_enforcement.commit_gates.secret_hardcode_gate import (  # noqa: F401  #ARCH-SECRETS-GOV-001 Phase 3
    make_secret_hardcode_gate as _make_secret_hardcode_gate,
)
from zephyr.gov_enforcement.commit_gates.secret_registry_consistency_gate import (  # noqa: F401  #ARCH-SECRETS-GOV-001 Phase 2-S3
    make_secret_registry_consistency_gate as _make_secret_registry_consistency_gate,
)
from zephyr.gov_enforcement.commit_gates.split_coordination_gate import (  # noqa: F401  # SPLIT-COORDINATION 拆分×编辑双重存在协议门禁（#ARCH-SPLIT-COORDINATION-001 2026-09-13，极限红蓝 F5 治本）
    make_split_coordination_gate as _make_split_coordination_gate,
)
from zephyr.gov_enforcement.commit_gates.strategy_factory_map_gate import (  # noqa: F401  # FACTORY-MAP 策略生产全景图结构门禁（图 9 挂总线，alignment_checklist §3 图 9 行，#ARCH-FACTORY-MAP-GATE-001 2026-09-13）
    make_strategy_factory_map_gate as _make_strategy_factory_map_gate,
)
from zephyr.gov_enforcement.commit_gates.syntax_validation_gate import (  # noqa: F401  # SYNTAX-VALIDATION staged .py 语法错误硬阻断门禁（红蓝 v3 P0-1 批 2 治本，priority=49）
    make_syntax_validation_gate as _make_syntax_validation_gate,
)
from zephyr.gov_enforcement.commit_gates.test_residue_ssot_gate import (  # noqa: F401
    make_test_residue_ssot_gate as _make_test_residue_ssot_gate,
)

__all__: list[str] = []  # 子模块各自导出 make_*_gate()，包级不 re-export

# 【GOV-DOC-018 命名约定（T_soft=120 资格声明，2026-09-13 DEDUP/平铺债批）】
# 本目录 111 个 .py 按文件名前缀簇管理命名规则（模块地图如下）。
# 前缀簇（top12）：
#   - blueprint_* (4 件)
#   - capability_* (4 件)
#   - bare_* (3 件)
#   - ch_* (3 件)
#   - depgraph_* (3 件)
#   - domain_* (2 件)
#   - file_* (2 件)
#   - frontend_* (2 件)
#   - import_* (2 件)
#   - msg_* (2 件)
#   - pure_* (2 件)
#   - reconciler_* (2 件)
#   - split_* (1 件，2026-09-13 新簇登记：SPLIT-COORDINATION 拆分协调协议门禁)
# 约定：新增文件必须延续所属簇前缀；新簇须先在本约定登记再落文件；
# 单簇超过 20 件时应拆子目录（参照 tests/signal_ashare 拆分先例）。
