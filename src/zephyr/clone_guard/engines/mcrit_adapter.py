# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §4.3
# [MODULE] zephyr.clone_guard.engines.mcrit_adapter
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.clone_guard.config (CloneGuardConfig); zephyr.clone_guard.engines.echo_guard_adapter (Finding); logging; pathlib
# [CONSUMERS] zephyr.clone_guard.orchestrator
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 已废弃降级占位——detect()/search() 恒返回空 + degraded，health_check() 恒 False；永不抛异常
# [MODIFY-GUARD] blueprint=docs/03_modules/_cross_layer/clone_guard/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] detect()/search() 永不抛异常——恒返回空 + 降级标记
# [TESTS] tests/clone_guard/test_mcrit_adapter.py
# [A_module] module_id=MOD-CLONE_GUARD | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
McritAdapter —— 已废弃降级占位（Phase C 引擎核实裁定）。

**已废弃**：经第一性原理核实（见 .trae/documents/clone-guard-engine-verification-ruling.md
§1.3 / §2.1），mcrit（github.com/danielplohmann/mcrit）实为 Fraunhofer FKIE 的
**二进制/恶意软件逆向相似度工具**（针对 SMDA 反汇编报告），非源码克隆检测器。
需 C++ 编译器 + MongoDB + 预建索引，GPL-3.0，与本项目环境/需求均不匹配。
原蓝图将其误设为"L2 MinHash 索引底座 + L0 查重加速"——领域完全错位，永远无法
fulfill 该角色，故裁定废弃。

本占位保留 McritAdapter 类名以维持 orchestrator 导入兼容（mcrit_enabled 默认 False，
不会参与调度），所有方法恒返回降级：

  - ``health_check()`` → ``False``（工具不可用）
  - ``detect(files, timeout)`` → ``([], True)``（空结果 + degraded=True）
  - ``search(query, top_k)`` → ``[]``（L0 搜索不可用）

mcrit 原承担的两个角色已重新分配（裁定 §2.2）：
  - L2 预筛底座 → relate（压缩相似度）/ reDUP
  - L0 语义搜函数 → relate ``similar`` / echo-guard 索引；均不可用时降级返回空

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: repo_root 参数
#   fields: 参数 repo_root（无注解）
#   code: mcrit_adapter.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: mcrit_adapter.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① McritAdapter
#   name_en: McritAdapter
#   intro: mcrit 适配器（已废弃·占位降级）。
#   desc: mcrit 适配器（已废弃·占位降级）。 保留类名以维持 orchestrator 导入兼容；所有方法恒返回降级，不执行任何真实检测。 mcrit_enabled 默认 Fals…；公共方法（定义序）: health_…
#   inputs: repo_root config
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: McritAdapter
#   downstream: zephyr.clone_guard.orchestrator
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from pathlib import Path

from zephyr.clone_guard.config import CloneGuardConfig
from zephyr.clone_guard.engines.echo_guard_adapter import Finding

logger = logging.getLogger(__name__)

__all__ = ["McritAdapter"]

# 废弃原因（供日志/诊断引用，避免在多处硬编码）
_DEPRECATION_REASON = (
    "mcrit 是二进制/恶意软件逆向相似度工具（非源码克隆检测），领域错位已废弃——"
    "见 clone-guard-engine-verification-ruling.md §2.1"
)


class McritAdapter:
    """mcrit 适配器（已废弃·占位降级）。

    保留类名以维持 orchestrator 导入兼容；所有方法恒返回降级，不执行任何真实检测。
    mcrit_enabled 默认 False，orchestrator 不会将其纳入调度引擎集。
    """

    def __init__(self, repo_root: Path, config: CloneGuardConfig | None = None):
        self._repo_root = Path(repo_root)
        self._config = config or CloneGuardConfig()

    def health_check(self) -> bool:
        """mcrit 已废弃——恒返回 False（工具不可用）。"""
        return False

    def detect(self, files: list[str], timeout: int | None = None) -> tuple[list[Finding], bool]:
        """mcrit 已废弃——恒返回 ``([], True)``（工具不可用·降级）。

        Args:
            files: 待检测文件路径列表（忽略）。
            timeout: 超时秒数（忽略）。

        Returns:
            ([], True) —— 空结果 + degraded=True。
        """
        logger.debug("McritAdapter.detect: mcrit 已废弃(%s)，返回降级", _DEPRECATION_REASON)
        return [], True

    def search(self, query: str, top_k: int | None = None) -> list[Finding]:
        """mcrit 已废弃——恒返回 ``[]``（L0 搜索不可用）。

        Args:
            query: 搜索查询（忽略）。
            top_k: 返回 top-k（忽略）。

        Returns:
            [] —— 空结果。
        """
        logger.debug("McritAdapter.search: mcrit 已废弃(%s)，返回空", _DEPRECATION_REASON)
        return []
