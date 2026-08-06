# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §4.4
# [MODULE] zephyr.clone_guard.mcp_server
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.integration.mcp._base_server (BaseMCPServer, MCPError); zephyr.clone_guard.orchestrator (CloneGuardOrchestrator, CheckResult); zephyr.clone_guard.engines.echo_guard_adapter (EchoGuardAdapter); zephyr.clone_guard.engines.mcrit_adapter (McritAdapter); zephyr.clone_guard.engines.relate_adapter (RelateAdapter); zephyr.shared.utils.time_utils (now_iso)
# [CONSUMERS] config/mcp.json (servers.clone_guard); AI agent (L0 源头预防)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] L0 源头预防——AI 写代码前主动调用，返回 advisory findings + import_suggestion（不硬阻断）；check_before_write 永不抛异常（orchestrator.check() 守 ERROR_CONTRACT）；co-located with clone_guard 模块（守 red_blue_validator 先例）；search_functions/audit_status 永不抛异常（6层闭环·可达性）
# [MODIFY-GUARD] blueprint=docs/03_modules/_cross_layer/clone_guard/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check_before_write/search_functions/audit_status 永不抛异常——降级时返回 degraded=True（warn-only 兜底）；health_check 永不抛异常
# [TESTS] tests/clone_guard/test_mcp_server.py
# [A_module] module_id=MOD-CLONE_GUARD | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""CloneGuardMCPServer — L0 源头预防 + L2 技术债可达性 MCP Server（Phase C）

治本 100% AI 开发场景下的"重复造轮子"病根。L0 层让 AI 在写代码前主动查重，
返回 advisory findings + import_suggestion，引导 AI 复用已有代码而非重复实现。
L2 层让 AI 冷启动时主动查询累积技术债（6层闭环·可达性），看见债才能还债。

四层防御纵深定位
----------------
  L0 源头预防（本 Server）— AI 写代码前主动调用 check_before_write，advisory 不阻断
  L1 提交拦截              — pre-commit 硬阻断 extract 级克隆（CAPABILITY-OVERLAP 门禁）
  L2 周期审计              — 全量语义扫描（audit_status 让 AI 主动查询技术债）
  L3 跨边界审计            — 跨仓库/跨项目（Phase C）

L0 vs L1 的本质区别
-------------------
  L0 是 advisory（建议性）——返回 findings + import_suggestion，AI 自主决定是否复用。
  L1 是 enforcement（强制性）——extract 级克隆硬阻断提交，无逃逸。
  L0 不抛 MCPError 阻断——即使发现 extract 级克隆也仅返回 hint，守"源头预防非强制"语义。

实现工具
--------
- clone_guard.check_before_write — L0 源头预防：AI 写代码前查重，返回 advisory findings
- clone_guard.search_functions   — L0 按语义搜已有函数（mcrit/relate search()），引导复用
- clone_guard.audit_status       — L2 查询技术债（读最近 audit JSON，6层闭环·可达性）
- clone_guard.health_check       — 检查 echo-guard 引擎 + 索引可用性

Usage::

    # AI agent 写代码前主动调用
    result = await mcp_call("clone_guard.check_before_write", {
        "files": ["src/new_module.py", "src/helpers.py"],
    })
    if result["findings"]:
        # AI 看到 import_suggestion，选择复用而非重复实现
        for f in result["findings"]:
            print(f"  已有 {f['existing_function']} 在 {f['existing_file']}——{f['import_suggestion']}")

    # AI 冷启动查询累积技术债
    status = await mcp_call("clone_guard.audit_status", {})
    if status["health_score"] in ("D", "F"):
        for plan in status["refactoring_plan"]:
            print(f"  待还债: {plan}")
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Final

from zephyr.clone_guard.config import load_config
from zephyr.clone_guard.engines.echo_guard_adapter import EchoGuardAdapter
from zephyr.clone_guard.orchestrator import CloneGuardOrchestrator
from zephyr.integration.mcp._base_server import BaseMCPServer
from zephyr.shared.utils.time_utils import now_iso

logger = logging.getLogger(__name__)

__all__ = ["CloneGuardMCPServer", "create_server", "main"]

SERVER_ID: Final[str] = "clone_guard"
SERVER_VERSION: Final[str] = "1.0.0"
SERVER_DESCRIPTION: Final[str] = (
    "CloneGuard L0 源头预防 MCP Server——AI 写代码前查重，返回 advisory findings + import_suggestion"
)

# 默认仓库根目录（MCP Server 通常在仓库根目录启动）
_DEFAULT_REPO_ROOT: Final[str] = "."


class CloneGuardMCPServer(BaseMCPServer):
    """CloneGuard L0 源头预防 MCP Server。

    复用 BaseMCPServer（JSON-RPC 2.0 over stdio），注册 L0 查重工具。
    生命周期内复用单个 CloneGuardOrchestrator 实例（避免每次调用重建索引连接）。
    """

    SERVER_ID = SERVER_ID
    VERSION = SERVER_VERSION
    DESCRIPTION = SERVER_DESCRIPTION

    def __init__(
        self,
        *,
        repo_root: str | Path | None = None,
        enable_rbac: bool = True,
    ) -> None:
        super().__init__(self.SERVER_ID, self.VERSION, self.DESCRIPTION, enable_rbac=enable_rbac)

        self._repo_root = Path(repo_root or _DEFAULT_REPO_ROOT).resolve()
        self._config = load_config(self._repo_root)
        self._orchestrator: CloneGuardOrchestrator | None = None  # 懒加载——首次 check 时初始化

        # ── L0 源头预防：AI 写代码前查重 ──
        self.register_tool(
            name="clone_guard.check_before_write",
            description=(
                "L0 源头预防：AI 写代码前查重。传入待写/已写草稿文件路径，"
                "返回克隆检测结果 + import_suggestion（advisory 不阻断）。"
                "AI 应根据 import_suggestion 复用已有代码而非重复实现。"
            ),
            input_schema={
                "type": "object",
                "required": ["files"],
                "additionalProperties": False,
                "properties": {
                    "files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "待检测文件路径列表（相对仓库根目录）",
                    },
                    "session_id": {
                        "type": "string",
                        "description": "AI session 标识（审计用，可选）",
                    },
                },
            },
            handler=self._check_before_write,
            safety_level="L",  # 只读检测，不修改任何文件
        )

        # ── 引擎健康检查 ──
        self.register_tool(
            name="clone_guard.health_check",
            description="检查 echo-guard 引擎可用性（CLI 存在 + 索引已建）。",
            input_schema={
                "type": "object",
                "additionalProperties": False,
                "properties": {},
            },
            handler=self._health_check,
            safety_level="L",
        )

    # ------------------------------------------------------------------
    # 懒加载 orchestrator（避免 __init__ 时触发 echo-guard 索引探测）
    # ------------------------------------------------------------------

    def _get_orchestrator(self) -> CloneGuardOrchestrator:
        """懒加载 CloneGuardOrchestrator（首次调用时初始化）。"""
        if self._orchestrator is None:
            self._orchestrator = CloneGuardOrchestrator(self._repo_root, self._config)
        return self._orchestrator

    # ------------------------------------------------------------------
    # Tool handlers
    # ------------------------------------------------------------------

    def _check_before_write(
        self,
        files: list[str],
        session_id: str | None = None,
    ) -> dict[str, Any]:
        """L0 源头预防：AI 写代码前查重。

        调用 CloneGuardOrchestrator.check() 检测给定文件，
        返回 advisory findings（不抛 MCPError 阻断——L0 是建议性而非强制性）。

        Args:
            files: 待检测文件路径列表（相对路径）。
            session_id: AI session 标识（审计用，可选）。

        Returns:
            包含 passed/findings/degraded/hint 的 dict。
        """
        if not files:
            return {
                "passed": True,
                "findings_count": 0,
                "findings": [],
                "degraded": False,
                "checked_files": 0,
                "hint": "未提供待检测文件——无需查重。",
                "checked_at": now_iso(),
            }

        try:
            orch = self._get_orchestrator()
            result = orch.check(files)
        except Exception as e:  # noqa: BLE001  层0 永不阻断——orchestrator 守 ERROR_CONTRACT 但额外兜底
            logger.warning("clone_guard.check_before_write 异常(%s: %s)", type(e).__name__, e)
            return {
                "passed": True,  # 降级放行——L0 不阻断
                "findings_count": 0,
                "findings": [],
                "degraded": True,
                "error": f"{type(e).__name__}: {e}",
                "checked_files": len(files),
                "hint": "CloneGuard 检测异常——L0 降级放行，L1 pre-commit 仍会兜底。",
                "checked_at": now_iso(),
            }

        # 序列化 findings 为可 JSON 化的 dict 列表
        findings_serialized = [
            {
                "severity": f.severity,
                "clone_type": f.clone_type,
                "similarity": round(f.similarity, 4),
                "source_file": f.source_file,
                "source_function": f.source_function,
                "source_lineno": f.source_lineno,
                "existing_file": f.existing_file,
                "existing_function": f.existing_function,
                "existing_lineno": f.existing_lineno,
                "import_suggestion": f.import_suggestion,
            }
            for f in result.findings
        ]

        # 生成 actionable hint——引导 AI 复用而非重复
        hint = self._build_hint(result, findings_serialized)

        return {
            "passed": result.passed,
            "findings_count": len(findings_serialized),
            "findings": findings_serialized,
            "degraded": result.degraded,
            "error": result.error,
            "checked_files": result.checked_files,
            "hint": hint,
            "checked_at": now_iso(),
        }

    def _health_check(self) -> dict[str, Any]:
        """检查 echo-guard 引擎可用性。

        Returns:
            包含 engine_available/index_exists/cli_present 的 dict。
        """
        adapter = EchoGuardAdapter(self._repo_root, self._config)
        index_path = self._repo_root / ".echo-guard" / "index.duckdb"
        index_exists = index_path.exists()

        try:
            cli_present = adapter.health_check()
        except Exception as e:  # noqa: BLE001  health_check 永不抛异常
            logger.warning("clone_guard.health_check 异常(%s: %s)", type(e).__name__, e)
            cli_present = False

        return {
            "engine_available": cli_present,
            "index_exists": index_exists,
            "index_path": str(index_path),
            "echo_guard_enabled": self._config.echo_guard_enabled,
            "fail_closed": self._config.fail_closed,
            "env": dict(self._config.env),
            "hint": (
                "echo-guard 可用——L0/L1 查重正常。"
                if cli_present
                else "echo-guard 不可用——运行 `echo-guard index` 构建索引。L1 降级为 warn-only。"
            ),
            "checked_at": now_iso(),
        }

    # ------------------------------------------------------------------
    # 辅助方法
    # ------------------------------------------------------------------

    @staticmethod
    def _build_hint(result: Any, findings: list[dict[str, Any]]) -> str:
        """根据检测结果生成 actionable hint，引导 AI 复用而非重复。"""
        if result.degraded:
            return (
                "CloneGuard 降级模式（echo-guard 不可用）——L0 无法查重，"
                "L1 pre-commit 会兜底。建议先运行 `echo-guard index` 构建索引。"
            )

        if not findings:
            return "未检测到代码克隆——可以安全写入。"

        extract_count = sum(1 for f in findings if f["severity"] == "extract")
        review_count = sum(1 for f in findings if f["severity"] == "review")

        parts: list[str] = []
        if extract_count:
            parts.append(
                f"发现 {extract_count} 处 extract 级克隆（3+副本，必须合并）——"
                "强烈建议使用以下 import_suggestion 复用已有代码："
            )
            for f in findings:
                if f["severity"] == "extract" and f["import_suggestion"]:
                    parts.append(f"  {f['import_suggestion']}  # 替代 {f['source_function']}")
        if review_count:
            parts.append(
                f"发现 {review_count} 处 review 级克隆（2副本，建议精简）——"
                "考虑复用已有代码以减少重复。"
            )

        return "\n".join(parts) if parts else "检测到克隆但无 actionable 建议。"


# ---------------------------------------------------------------------------
# 工厂函数 + 启动入口
# ---------------------------------------------------------------------------


def create_server(
    *,
    repo_root: str | Path | None = None,
    enable_rbac: bool = True,
) -> CloneGuardMCPServer:
    """工厂函数，返回配置好的 CloneGuardMCPServer 实例。

    Args:
        repo_root: 仓库根目录（默认当前目录）。
        enable_rbac: 是否启用 RBAC（默认 True）。
    """
    return CloneGuardMCPServer(repo_root=repo_root, enable_rbac=enable_rbac)


def main() -> None:
    """启动 CloneGuard MCP Server（stdio 传输）。

    日志输出到 stderr——stdout 保留给 JSON-RPC 协议帧。
    """
    import sys as _sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
        stream=_sys.stderr,
    )

    server = create_server()
    server.run()


if __name__ == "__main__":
    main()
