# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §4.4
# [MODULE] zephyr.clone_guard.mcp_server
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.integration.mcp._base_server (BaseMCPServer, MCPError); zephyr.clone_guard.orchestrator (CloneGuardOrchestrator, CheckResult); zephyr.clone_guard.engines.echo_guard_adapter (EchoGuardAdapter); zephyr.clone_guard.engines.relate_adapter (RelateAdapter); zephyr.shared.utils.time_utils (now_iso)
# [CONSUMERS] config/mcp.json (servers.clone_guard); AI agent (L0 源头预防 + L2 技术债可达性)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] L0 源头预防——AI 写代码前主动调用，返回 advisory findings + import_suggestion（不硬阻断）；check_before_write/search_functions/audit_status/health_check 永不抛异常（orchestrator 守 ERROR_CONTRACT）；resolve_finding 永不抛异常（acknowledge 写操作降级返回 degraded）；co-located with clone_guard 模块（守 red_blue_validator 先例）
# [MODIFY-GUARD] blueprint=docs/03_modules/_cross_layer/clone_guard/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check_before_write/search_functions/audit_status 永不抛异常——降级时返回 degraded=True（warn-only 兜底）；health_check 永不抛异常；resolve_finding 永不抛异常——acknowledge 失败返回 acknowledged=False + degraded=True
# [TESTS] tests/clone_guard/test_mcp_server.py
# [A_module] module_id=MOD-CLONE_GUARD | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""



CloneGuardMCPServer — L0 源头预防 + L2 技术债可达性 MCP Server（Phase C）

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
- clone_guard.search_functions   — L0 按语义搜已有函数（relate search()），引导复用
- clone_guard.audit_status       — L2 查询技术债（读最近 audit JSON，6层闭环·可达性）
- clone_guard.health_check       — 检查 echo-guard 引擎 + 索引可用性
- clone_guard.resolve_finding    — L2 acknowledged 白名单管理（写操作，safety_level=M）

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

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: repo_root 参数
#   fields: 参数 repo_root（无注解）
#   code: mcp_server.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: enable_rbac 参数
#   fields: 参数 enable_rbac（无注解）
#   code: mcp_server.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① create_server
#   name_en: create_server
#   intro: 工厂函数，返回配置好的 CloneGuardMCPServer 实例。
#   desc: 工厂函数，返回配置好的 CloneGuardMCPServer 实例。 Args: repo_root: 仓库根目录（默认当前目录）。 enable_rbac: 是否启用 RBA…；源码 L648-L659
#   inputs: repo_root enable_rbac
#   outputs: CloneGuardMCPServer
# - id: A2
#   name_zh: ② main
#   name_en: main
#   intro: 启动 CloneGuard MCP Server（stdio 传输）。
#   desc: 启动 CloneGuard MCP Server（stdio 传输）。 日志输出到 stderr——stdout 保留给 JSON-RPC 协议帧。；源码 L662-L676
#   inputs: 无参数
#   outputs: 返回值
#   （注：A2 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: CloneGuardMCPServer
#   name_en: CloneGuardMCPServer
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: config/mcp.json (servers.clone_guard); AI agent (L0 源头预防 + L2 技术债可达性)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Final

from zephyr.clone_guard.config import load_config
from zephyr.clone_guard.engines.echo_guard_adapter import EchoGuardAdapter
from zephyr.clone_guard.engines.relate_adapter import RelateAdapter
from zephyr.clone_guard.orchestrator import CloneGuardOrchestrator
from zephyr.integration.mcp._base_server import BaseMCPServer
from zephyr.shared.utils.time_utils import now_iso

logger = logging.getLogger(__name__)

__all__ = ["CloneGuardMCPServer", "create_server", "main"]

SERVER_ID: Final[str] = "clone_guard"
SERVER_VERSION: Final[str] = "1.0.0"
SERVER_DESCRIPTION: Final[str] = (
    "CloneGuard L0 源头预防 + L2 技术债可达性 MCP Server——AI 写代码前查重 + 冷启动查询累积技术债"
)

# 默认仓库根目录（MCP Server 通常在仓库根目录启动）
_DEFAULT_REPO_ROOT: Final[str] = "."


class CloneGuardMCPServer(BaseMCPServer):
    """CloneGuard L0 源头预防 + L2 技术债可达性 MCP Server。

    复用 BaseMCPServer（JSON-RPC 2.0 over stdio），注册 5 个工具（4 只读 + 1 写）。
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
        self._orchestrator: CloneGuardOrchestrator | None = None  # 懒加载——首次调用时初始化

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

        # ── L0 按语义搜已有函数（Phase C：relate search() 复用）──
        self.register_tool(
            name="clone_guard.search_functions",
            description=(
                "L0 按语义搜已有函数：传入函数签名/片段，返回 top-k 相似已有函数。"
                "AI 写新函数前应先调用此工具查找可复用代码（6层闭环·可达性）。"
                "复用 relate 适配器的 search() 方法，引擎不可用时返回空。"
            ),
            input_schema={
                "type": "object",
                "required": ["query"],
                "additionalProperties": False,
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索查询（函数签名/代码片段/功能描述）",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "返回 top-k 结果（可选，默认 10）",
                        "minimum": 1,
                        "maximum": 100,
                    },
                },
            },
            handler=self._search_functions,
            safety_level="L",  # 只读搜索，不修改任何文件
        )

        # ── L2 查询累积技术债（读最近 audit JSON，6层闭环·可达性）──
        self.register_tool(
            name="clone_guard.audit_status",
            description=(
                "L2 查询累积技术债：返回最近一次周期审计结果（health_score A-F + "
                "refactoring_plan + findings_count）。AI 冷启动应先调用此工具看见债。"
                "无历史审计时返回 no_audit 状态。"
            ),
            input_schema={
                "type": "object",
                "additionalProperties": False,
                "properties": {},
            },
            handler=self._audit_status,
            safety_level="L",  # 只读查询，不修改任何文件
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

        # ── L2 acknowledged 白名单管理（写操作，safety_level=M 需确认）──
        self.register_tool(
            name="clone_guard.resolve_finding",
            description=(
                "L2 acknowledged 白名单管理：将合理重复 finding 加入 echo-guard.yml "
                "suppressed 列表，标记为 acknowledged 严重性（最低，不阻断 CI）。"
                "intentional=保留两份（函数变化时重新浮现，非永久豁免）；"
                "dismissed=标记为非重复（永久豁免）。"
                "AI 应仅对经人工确认合理的克隆调用此工具，并在 note 中说明理由"
                "（强制留痕防滥用）。写操作——会修改 echo-guard.yml，需后续提交持久化。"
            ),
            input_schema={
                "type": "object",
                "required": ["finding_id", "verdict", "note"],
                "additionalProperties": False,
                "properties": {
                    "finding_id": {
                        "type": "string",
                        "description": (
                            "来自 clone_guard.audit_status 或 `echo-guard scan --output json` 的 finding ID"
                        ),
                    },
                    "verdict": {
                        "type": "string",
                        "enum": ["intentional", "dismissed"],
                        "description": ("intentional=保留两份（函数变化重新浮现）；dismissed=非重复（永久豁免）"),
                    },
                    "note": {
                        "type": "string",
                        "minLength": 1,
                        "description": "说明为何 acknowledge（强制留痕，防滥用）",
                    },
                },
            },
            handler=self._resolve_finding,
            safety_level="M",  # 写操作——修改 echo-guard.yml，需确认
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

    def _search_functions(
        self,
        query: str,
        top_k: int | None = None,
    ) -> dict[str, Any]:
        """L0 按语义搜已有函数（relate search() 复用）。

        引擎不可用时返回空结果 + degraded=True（守 6层闭环·可达性——空结果也是有效反馈）。
        """
        if not query or not query.strip():
            return {
                "results": [],
                "results_count": 0,
                "degraded": False,
                "engines_checked": [],
                "hint": "未提供查询——无需搜索。",
                "checked_at": now_iso(),
            }

        results: list[dict[str, Any]] = []
        engines_checked: list[str] = []
        engines_available: list[str] = []

        # relate search（无模型快速预筛）
        try:
            relate = RelateAdapter(self._repo_root, self._config)
            engines_checked.append("relate")
            if relate.health_check():
                engines_available.append("relate")
                for f in relate.search(query, top_k):
                    results.append(self._serialize_search_result(f, "relate"))
        except Exception as e:  # noqa: BLE001  search 永不抛异常
            logger.debug("search_functions: relate 异常(%s)", e)

        # 去重（按 existing_file + existing_function，保留相似度最高）
        seen: dict[tuple[str, str], dict[str, Any]] = {}
        for r in results:
            key = (r["existing_file"], r["existing_function"])
            if key not in seen or r["similarity"] > seen[key]["similarity"]:
                seen[key] = r
        deduped = sorted(seen.values(), key=lambda r: r["similarity"], reverse=True)[
            : (top_k or self._config.relate_top_k)
        ]

        degraded = len(engines_available) == 0
        hint = (
            f"找到 {len(deduped)} 个相似函数——建议复用而非重复实现。"
            if deduped
            else (
                "无可用搜索引擎（relate 未安装或索引未建）——安装 datasketch (pip install datasketch) 并在 clone_guard.yml 启用 relate_prescreen。"
                if degraded
                else "未找到相似函数——可以安全新建。"
            )
        )

        return {
            "results": deduped,
            "results_count": len(deduped),
            "degraded": degraded,
            "engines_checked": engines_checked,
            "engines_available": engines_available,
            "hint": hint,
            "checked_at": now_iso(),
        }

    def _audit_status(self) -> dict[str, Any]:
        """L2 查询累积技术债（读最近 audit JSON，6层闭环·可达性）。

        返回最近一次 audit() 持久化结果；无历史记录时返回 no_audit 状态。
        本工具只读不触发审计——触发审计由 CLI/事件负责（守"禁止时间触发"）。
        """
        try:
            orch = self._get_orchestrator()
            data = orch.load_latest_audit()
        except Exception as e:  # noqa: BLE001  audit_status 永不抛异常
            logger.warning("clone_guard.audit_status 异常(%s: %s)", type(e).__name__, e)
            return {
                "status": "error",
                "degraded": True,
                "error": f"{type(e).__name__}: {e}",
                "hint": "读取审计状态异常。",
                "checked_at": now_iso(),
            }

        if data is None:
            return {
                "status": "no_audit",
                "degraded": False,
                "hint": "尚未执行周期审计——无历史技术债记录。可经 CLI 触发 clone_guard audit 后再查询。",
                "checked_at": now_iso(),
            }

        health_score = str(data.get("health_score", "?"))
        findings_count = int(data.get("findings_count", 0))
        hint = self._audit_hint(health_score, findings_count)

        return {
            "status": "ok",
            "degraded": False,
            "timestamp": data.get("timestamp", ""),
            "health_score": health_score,
            "findings_count": findings_count,
            "refactoring_plan": data.get("refactoring_plan", []),
            "degraded_engines": data.get("degraded_engines", []),
            "active_engine_count": data.get("active_engine_count", 0),
            "checked_files": data.get("checked_files", 0),
            "hint": hint,
            "checked_at": now_iso(),
        }

    def _health_check(self) -> dict[str, Any]:
        """检查 echo-guard 引擎可用性。"""
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

    def _resolve_finding(
        self,
        finding_id: str,
        verdict: str,
        note: str,
    ) -> dict[str, Any]:
        """L2 acknowledged 白名单管理——封装 echo-guard acknowledge CLI。

        将合理重复 finding 加入 echo-guard.yml suppressed 列表，标记为 acknowledged
        严重性（最低，不阻断 CI）。守 ERROR_CONTRACT：永不抛异常，CLI 失败/异常返回
        ``acknowledged=False + degraded=True``。

        输入校验（防御兜底——JSON Schema 已约束，但 handler 直调时仍需校验）：
        - finding_id 非空
        - verdict ∈ {intentional, dismissed}
        - note 非空（强制留痕防滥用）
        """
        # ── 输入校验（防御兜底）──
        if not finding_id or not finding_id.strip():
            return {
                "acknowledged": False,
                "degraded": True,
                "error": "finding_id 不能为空",
                "hint": "请提供来自 echo-guard scan --output json 的 finding ID。",
                "checked_at": now_iso(),
            }
        if verdict not in ("intentional", "dismissed"):
            return {
                "acknowledged": False,
                "degraded": True,
                "error": f"verdict 非法: {verdict!r}（须为 intentional 或 dismissed）",
                "hint": "verdict 须为 intentional（保留两份）或 dismissed（非重复永久豁免）。",
                "checked_at": now_iso(),
            }
        if not note or not note.strip():
            return {
                "acknowledged": False,
                "degraded": True,
                "error": "note 不能为空（强制留痕防滥用）",
                "hint": "必须在 note 中说明 acknowledge 理由——防 AI 滥用白名单消除告警。",
                "checked_at": now_iso(),
            }

        try:
            adapter = EchoGuardAdapter(self._repo_root, self._config)
            success, error = adapter.acknowledge(finding_id.strip(), verdict, note)
        except Exception as e:  # noqa: BLE001  resolve_finding 永不抛异常
            logger.warning("clone_guard.resolve_finding 异常(%s: %s)", type(e).__name__, e)
            return {
                "acknowledged": False,
                "degraded": True,
                "error": f"{type(e).__name__}: {e}",
                "finding_id": finding_id,
                "verdict": verdict,
                "hint": "acknowledge 异常——白名单未更新，echo-guard.yml 未修改。",
                "checked_at": now_iso(),
            }

        if not success:
            return {
                "acknowledged": False,
                "degraded": True,
                "error": error,
                "finding_id": finding_id,
                "verdict": verdict,
                "hint": (
                    "acknowledge 失败——白名单未更新。"
                    "检查 echo-guard CLI 可用性 + finding_id 有效性（须来自 scan --output json）。"
                ),
                "checked_at": now_iso(),
            }

        return {
            "acknowledged": True,
            "degraded": False,
            "finding_id": finding_id,
            "verdict": verdict,
            "note": note,
            "hint": (
                f"finding {finding_id} 已加入 echo-guard.yml suppressed 白名单"
                f"（verdict={verdict}）。下次 scan/check 该 finding 标记为 acknowledged"
                " 严重性（不阻断）。注意：echo-guard.yml 已修改，需提交以持久化。"
            ),
            "checked_at": now_iso(),
        }

    # ------------------------------------------------------------------
    # 辅助方法
    # ------------------------------------------------------------------

    @staticmethod
    def _serialize_search_result(f: Any, engine: str) -> dict[str, Any]:
        """将 search() 返回的 Finding 序列化为可 JSON 化的 dict。"""
        return {
            "existing_file": f.existing_file,
            "existing_function": f.existing_function,
            "existing_lineno": f.existing_lineno,
            "similarity": round(f.similarity, 4),
            "import_suggestion": f.import_suggestion,
            "engine": engine,
        }

    @staticmethod
    def _audit_hint(health_score: str, findings_count: int) -> str:
        """根据 health_score 生成技术债 hint。"""
        if health_score in ("D", "F"):
            return (
                f"技术债严重（health_score={health_score}，{findings_count} 处克隆）——"
                "建议优先处理 refactoring_plan 中的 extract 级项。"
            )
        if health_score == "C":
            return f"有累积技术债（health_score=C，{findings_count} 处克隆）——建议择期还债。"
        return f"技术债健康（health_score={health_score}，{findings_count} 处克隆）——状态良好。"

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
            parts.append(f"发现 {review_count} 处 review 级克隆（2副本，建议精简）——考虑复用已有代码以减少重复。")

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
