# [BLUEPRINT] MOD-GOV_commit_gates | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.commit_gates
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
# [A_module] module_id=MOD-GOV_commit_gates | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""commit_gates — GitCommitGateway pre-commit 门禁实现包。

每个 gate 一个文件 + ``make_*_gate()`` 工厂函数，返回 ``GateSpec``。
注册到 ``GitCommitGateway._gate_registry``（见 commit_gate_registry.py）。

新增门禁流程（AGENTS.md §8 门禁注册制）：
1. 在本包下创建 ``make_xxx_gate()`` 返回 ``GateSpec``
2. 在 ``GitCommitGateway.__init__`` 中 ``self._gate_registry.register(...)``

禁止在 ``commit()`` 方法体硬编码 ``_check_*`` 调用（架构债务 #AD-001 治本）。
"""

__all__: list[str] = []  # 子模块各自导出 make_*_gate()，包级不 re-export
