---
module_id: KE-module_blu-src_zephyr_context_engine_in_p-006
title: src/zephyr/context_engine/in_process.py (experimental 产出)
category: module_blueprint
---

# src/zephyr/context_engine/in_process.py (experimental 产出)

src/zephyr/context_engine/in_process.py (experimental 产出)

class InProcessContextEngine:  # implements ContextEngineProtocol
    """所有方法均为 async。依赖 VectorMemoryProtocol + NetworkX + tiktoken + llama.cpp。"""

    def __init__(
        self,
        config: CEConfig,
        vm: VectorMemoryProtocol,          # 从 get_vm() 注入
        entity_graph_path: str,
    ) -> None: ...

    # ───── 主流水（build → compress → validate → inject）─────
    async def build(self, request: ContextRequest) -> ContextBundle:
        """
        从三源汇聚：
          1. VMS multi_search（merge_strategy='rrf'）拉 decisions/code_context/task_history/lessons
          2. NetworkX entity-graph 查 target_files 的直接依赖节点（深度 ≤ 2）
          3. 文件系统兜底：VMS 降级时用 rg/grep 按 tags/target_files 检索（DEGRADE-001）
        按 slot_overrides 或默认比例分配 token 预算。
        """

    async def compress(
        self,
        bundle: ContextBundle,
        token_budget: int,
        strategy: Literal["llm_summary", "rule_based", "truncate"] = "llm_summary",
    ) -> ContextBundle:
        """
        压缩到 token_budget 以内：
          - 'llm_summary'：本地 Qwen2.5-3B 分 slot 摘要（首选）
          - 'rule_based'：按优先级 + 首尾 N 行 + 去 boilerplate（LLM 挂时降级）
          - 'truncate'：简单截断（最后降级）
        保留 source_traces 完整性，不丢引用链。
        """

    async def validate(self, bundle: ContextBundle) -> ValidationReport:
        """
        验证：
          - token_count ≤ budget
          - 所有 source_traces 可解析（vms:// 可 get_by_id，file:// 存在）
          - 无 stale references（超过 updated_at 阈值的 ADR 标 stale）
        失败时 violations 列出具体原因，不修正。
        """

    async def inject(
        self,
        bundle: ContextBundle,
        ide_id: IDEID,
    ) -> InjectResult:
        """
        按 IDE_CAPABILITY_MATRIX 多通道注入：
          - slot 'task_spec' / 'runtime_state' → prompts（所有 IDE full）
          - slot 'code_refs' / 'architecture' → resources（Trae/Claude-Desktop full，Cursor read_only）
          - slot 'guardrails' → tools schema descriptions（Cursor/Claude-Desktop full，Trae partial）
        不支持的通道自动降级到 prompts 单通道，InjectResult.channels_skipped 记录原因。
        """

    # ───── 反馈通道（遗漏 #5 补充）─────
    async def adjust_strategy(
        self,
        task_id: str,
        signal: FeedbackSignal,
    ) -> AdjustResult:
        """
        Feedback Loop Engine 的 FeedbackAction Protocol 调用此接口。
        不硬编码依赖 FLE，只接收符合 FeedbackSignal schema 的信号。
        调整在 ttl_minutes 内生效，到期自动回默认权重。
        """

    # ───── 辅助 ─────
    async def probe_ide_capabilities(self, ide_id: str) -> IDECapabilities:
        """
        运行时探测 IDE 能力（查 MCP initialize handshake 的 capabilities 字段）。
        探测失败回退到 IDE_CAPABILITY_MATRIX 静态值。
        """

    async def stats(self) -> CEStats: ...
    async def clear_cache(self, task_id: str | None = None) -> None: ...
```
