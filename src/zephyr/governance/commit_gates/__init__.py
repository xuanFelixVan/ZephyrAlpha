"""commit_gates — GitCommitGateway pre-commit 门禁实现包。

每个 gate 一个文件 + ``make_*_gate()`` 工厂函数，返回 ``GateSpec``。
注册到 ``GitCommitGateway._gate_registry``（见 commit_gate_registry.py）。

新增门禁流程（AGENTS.md §8 门禁注册制）：
1. 在本包下创建 ``make_xxx_gate()`` 返回 ``GateSpec``
2. 在 ``GitCommitGateway.__init__`` 中 ``self._gate_registry.register(...)``

禁止在 ``commit()`` 方法体硬编码 ``_check_*`` 调用（架构债务 #AD-001 治本）。
"""

__all__: list[str] = []  # 子模块各自导出 make_*_gate()，包级不 re-export
