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

"""commit_gates — GitCommitGateway pre-commit 门禁实现包。

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

__all__: list[str] = []  # 子模块各自导出 make_*_gate()，包级不 re-export
