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

新增门禁流程（AGENTS.md §8 门禁注册制 + #ARCH-GATE-REGISTRY-AUTO-001 YAML 驱动自动注册）：
1. 在本包下创建 ``make_xxx_gate()`` 返回 ``GateSpec``
2. 在 ``in_process_gate_registry.yaml`` 追加条目（gate_id + module_path + factory_function）
3. ``gate_auto_registrar.py`` 启动时从 YAML 动态 import + register

禁止在 ``commit()`` 方法体硬编码 ``_check_*`` 调用（架构债务 #AD-001 治本）。

ORPHAN-MODULE 注意：gate 模块通过 YAML 动态加载（importlib），但 ORPHAN-MODULE gate
只检测静态 import 引用。新增 gate MUST 在下方 ``_ORPHAN_MODULE_STATIC_IMPORTS`` 区块
追加一行静态 import（``as _`` 别名，不 re-export），否则 commit 被 ORPHAN-MODULE 阻断。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: ORPHAN-MODULE 静态检测请求
#   fields: git grep 静态 import 引用扫描（该 gate 只检测静态引用）
#   code: __init__.py L30-33 docstring 说明
# - id: I2
#   name: 门禁注册条目 in_process_gate_registry.yaml
#   fields: gate_id + module_path + factory_function
#   code: AGENTS.md §8 门禁注册制 + ARCH-GATE-REGISTRY-AUTO-001
# 层: 算法
# - id: A1
#   name_zh: ① ORPHAN-MODULE 静态引用锚定
#   name_en: _ORPHAN_MODULE_STATIC_IMPORTS
#   intro: 集中静态 import 7 个 make_*_gate 工厂（别名 _ 不 re-export），防 YAML 动态加载的 gate 被误判孤儿
#   desc: L80-100：blueprint_node_id_hardcode/test_residue_ssot/secret_registry_consistency/secret_hardcode/commit_scope/reconciler_file_ops/registry_code_anchor 七工厂静态锚定
#   inputs: I1
#   outputs: 7 个门禁工厂静态引用
# - id: A2
#   name_zh: ② 包级导出封口
#   name_en: __all__ = []
#   intro: 子模块各自导出 make_*_gate()，包级不 re-export，配合 YAML 自动注册
#   desc: L55：__all__ 置空；gate_auto_registrar 启动时按 YAML 条目动态 import + register
#   inputs: I2
#   outputs: 空包级导出表
# 层: 输出
# - id: O1
#   name_zh: commit 门禁工厂锚定集
#   name_en: 7 × make_*_gate factories
#   intro: 7 个 pre-commit 门禁工厂经静态锚定 + YAML 动态注册进 GitCommitGateway
#   downstream: zephyr.gov_enforcement.rule_bridge.git_commit_gateway（[CONSUMERS] 头）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A2
# A1 --> O1
# A2 --> O1
"""

# === ORPHAN-MODULE 静态引用区 ===
# gate 模块通过 gate_auto_registrar YAML 动态加载，但 ORPHAN-MODULE gate 只做静态
# `git grep` 检测。此处集中声明静态 import 引用（别名 _，不 re-export，包级 __all__ 不变）。
# 新增 gate 时在此追加一行。#ARCH-GATE-REGISTRY-AUTO-001 已知限制。
from zephyr.gov_enforcement.commit_gates.blueprint_node_id_hardcode_gate import (  # noqa: F401
    make_blueprint_node_id_hardcode_gate as _make_blueprint_node_id_hardcode_gate,
)
from zephyr.gov_enforcement.commit_gates.test_residue_ssot_gate import (  # noqa: F401
    make_test_residue_ssot_gate as _make_test_residue_ssot_gate,
)
from zephyr.gov_enforcement.commit_gates.secret_registry_consistency_gate import (  # noqa: F401  #ARCH-SECRETS-GOV-001 Phase 2-S3
    make_secret_registry_consistency_gate as _make_secret_registry_consistency_gate,
)
from zephyr.gov_enforcement.commit_gates.secret_hardcode_gate import (  # noqa: F401  #ARCH-SECRETS-GOV-001 Phase 3
    make_secret_hardcode_gate as _make_secret_hardcode_gate,
)
from zephyr.gov_enforcement.commit_gates.commit_scope_gate import (  # noqa: F401  # COMMIT-SCOPE 跨域混合提交治本（13a5e1d512 事故）
    make_commit_scope_gate as _make_commit_scope_gate,
)
from zephyr.gov_enforcement.commit_gates.reconciler_file_ops_gate import (  # noqa: F401  # RECONCILER-FILE-OPS 裸删除原语静态扫描（#ARCH-RECONCILER-AUTO-DELETE-GOV-001 T1③）
    make_reconciler_file_ops_gate as _make_reconciler_file_ops_gate,
)
from zephyr.gov_enforcement.commit_gates.registry_code_anchor_gate import (  # noqa: F401  # REGISTRY-CODE-ANCHOR 业务注册表代码锚点门禁（#ARCH-BREG-002 门禁A）
    make_registry_code_anchor_gate as _make_registry_code_anchor_gate,
)

__all__: list[str] = []  # 子模块各自导出 make_*_gate()，包级不 re-export
