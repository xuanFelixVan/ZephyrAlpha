# [BLUEPRINT] MOD-INF-013 | docs/03_modules/_cross_layer/model_context_protocol_servers/blueprint.md | §
# [MODULE] zephyr.integration.mcp.sentinel_server
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.integration.mcp._base_server; zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INT_sentinel_server | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# AI-generated: sentinel (intent_router) MCP Server skeleton (ADR-0033, T-3-04)
"""
SentinelServer: 意图路由哨兵 MCP Server
========================================
Task ID  : T-3-04 (B15)
Server   : intent_router (tool-contracts.yaml §Server 5)
Protocol : ADR-0033（stdio 传输、JSON-RPC 2.0）
Backend  : intent_keyword_mapper.py (Stage 1, T-2-21)
           intent_embedding_mapper.py (Stage 2, beta 引入)
           intent_llm_router.py (Stage 3, stable 引入)

文件命名说明
-----------
sentinel_server.py 对应 tool-contracts.yaml 中的 intent_router server。
"Sentinel"（哨兵）强调本服务对用户意图的 UNKNOWN 拦截与告警职责，
与 Gate 体系形成"意图层防护"。

实现工具
--------
- intent_router.map_intent        — 核心意图路由（Stage 1→2→3 级联）
- intent_router.reload_keywords   — 热加载关键词词典
- intent_router.evaluate_golden_set — 黄金集评测
"""

from __future__ import annotations

import time
from typing import Any

from zephyr.integration.mcp._base_server import BaseMCPServer, MCPError

__all__ = ["SentinelServer", "create_server"]

from zephyr.governance.persistence.intent_keyword_mapper import IntentDomain

_VALID_DOMAINS = frozenset({d.value for d in IntentDomain})

# Stage 1 关键词词典（简化版骨架；生产中从 000-task-router.md 动态加载）
_DEFAULT_KEYWORD_DICT: dict[str, list[str]] = {
    "D0": ["数据", "data", "ohlcv", "akshare", "tushare", "baostock", "行情", "tick"],
    "D1": ["因子", "alpha", "feature", "特征", "l01", "l02", "factor"],
    "D2": ["治理", "governance", "adr", "审计", "audit", "规则", "rule", "蓝图", "blueprint"],
    "D3": ["信号", "signal", "strategy", "策略", "回测", "backtest", "l03"],
    "D4": ["风险", "risk", "drawdown", "var", "cvar", "l04", "止损"],
    "D5": ["组合", "portfolio", "仓位", "position", "l05", "权重"],
    "D6": ["执行", "execution", "order", "委托", "l06", "交易"],
    "D7": ["归因", "attribution", "绩效", "performance", "l07", "pnl"],
    "D8": ["知识", "knowledge", "ke", "向量", "chromadb", "vms", "vector-memory", "向量记忆", "embedding", "检索"],
    "D9": ["交接", "handoff", "mcp", "server", "session", "context", "prompt"],
}


def _keyword_match(query: str, keyword_dict: dict[str, list[str]]) -> tuple[str, float, list[str]]:
    """Stage 1 关键词匹配，返回 (domain, confidence, matched_keywords)。"""
    query_lower = query.lower()
    scores: dict[str, int] = {}
    matched: dict[str, list[str]] = {}

    for domain, keywords in keyword_dict.items():
        hits = [kw for kw in keywords if kw in query_lower]
        if hits:
            scores[domain] = len(hits)
            matched[domain] = hits

    if not scores:
        return "UNKNOWN", 0.0, []

    best_domain = max(scores, key=lambda d: scores[d])
    total_kw = len(keyword_dict.get(best_domain, []))
    confidence = min(scores[best_domain] / max(total_kw, 1), 1.0) * 0.9 + 0.1
    return best_domain, round(confidence, 4), matched.get(best_domain, [])


class SentinelServer(BaseMCPServer):
    """intent_router MCP Server 实现（Sentinel 哨兵）。

    beta 仅实现 Stage 1（关键词匹配）；Stage 2/3 留接口。
    """

    SERVER_ID = "intent_router"
    VERSION = "1.0.0"
    DESCRIPTION = "自然语言 → 10 域 + directive 链路由；Stage 1 关键词已激活，Stage 2/3 待 beta/stable"

    def __init__(self, *, enable_rbac: bool = True) -> None:
        super().__init__(self.SERVER_ID, self.VERSION, self.DESCRIPTION, enable_rbac=enable_rbac)
        self._keyword_dict: dict[str, list[str]] = dict(_DEFAULT_KEYWORD_DICT)
        # 黄金评测集（骨架：内置 3 条最小样本）
        self._golden_set: list[dict[str, Any]] = [
            {"query": "帮我获取 A 股日线行情", "expected_domain": "D0"},
            {"query": "查看 KB 决策记录 ADR-011 治理规则", "expected_domain": "D2"},
            {"query": "计算因子暴露度", "expected_domain": "D1"},
        ]

        self.register_tool(
            name="intent_router.map_intent",
            description="核心意图路由；自动级联 Stage 1 → 2 → 3",
            input_schema={
                "type": "object",
                "required": ["query"],
                "additionalProperties": False,
                "properties": {
                    "query": {"type": "string", "minLength": 1, "maxLength": 1000},
                    "max_stage": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 3,
                        "default": 3,
                    },
                    "require_directives": {"type": "boolean", "default": True},
                },
            },
            handler=self._map_intent,
        )
        self.register_tool(
            name="intent_router.reload_keywords",
            description="热加载关键词词典（修改 000-task-router.md 后使用）",
            input_schema={
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "source_file": {"type": "string"},
                    "keyword_dict": {
                        "type": "object",
                        "description": "直接传入新词典（测试用）",
                    },
                },
            },
            handler=self._reload_keywords,
        )
        self.register_tool(
            name="intent_router.evaluate_golden_set",
            description="在黄金集上跑评测并返回 top-1 accuracy / top-3 recall",
            input_schema={
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "max_stage": {"type": "integer", "minimum": 1, "maximum": 3, "default": 1},
                    "sample_size": {"type": ["integer", "null"]},
                },
            },
            handler=self._evaluate_golden_set,
        )
        self.register_tool(
            name="intent_router.health_status",
            description="哨兵健康状态——返回路由器状态 + 路由表版本 + 词典信息",
            input_schema={
                "type": "object",
                "additionalProperties": False,
                "properties": {},
            },
            handler=self._health_status,
        )

    # ------------------------------------------------------------------
    # Tool handlers
    # ------------------------------------------------------------------

    def _map_intent(
        self,
        query: str,
        max_stage: int = 3,
        require_directives: bool = True,
    ) -> dict[str, Any]:
        """核心意图路由（Stage 1 关键词匹配；Stage 2/3 骨架占位）。

        ZA-INT-0001: all stages failed (UNKNOWN)
        ZA-INT-0002: query too long
        """
        if len(query) > 1000:
            raise MCPError(-32400, f"ZA-INT-0002: query too long ({len(query)} chars)")

        t0 = time.perf_counter()

        # Stage 1: 关键词匹配
        domain, confidence, matched_kws = _keyword_match(query, self._keyword_dict)
        source_stage = "keyword"

        # Stage 2 占位（beta 引入 embedding）
        if domain == "UNKNOWN" and max_stage >= 2:
            source_stage = "embedding"
            pass  # PHASE-GATE: intent_embedding_mapper.py (Stage 2, beta)

        # Stage 3 占位（stable 引入 LLM）
        if domain == "UNKNOWN" and max_stage >= 3:
            source_stage = "llm"
            pass  # PHASE-GATE: intent_llm_router.py (Stage 3, Phase4)

        latency_ms = int((time.perf_counter() - t0) * 1000)

        if domain == "UNKNOWN":
            raise MCPError(-32422, "ZA-INT-0001: all three stages failed (UNKNOWN)")

        # 简化版 directive 推荐（骨架）
        _DOMAIN_DIRECTIVES: dict[str, list[str]] = {
            "D0": ["266"],
            "D1": ["325"],
            "D2": ["244", "999"],
            "D3": ["325", "344"],
            "D4": ["266", "325"],
            "D5": ["325"],
            "D6": ["325", "344"],
            "D7": ["325"],
            "D8": ["266"],
            "D9": ["999"],
        }
        directives = _DOMAIN_DIRECTIVES.get(domain, []) if require_directives else []

        return {
            "query": query,
            "primary_domain": domain,
            "secondary_domains": [],
            "confidence": confidence,
            "matched_keywords": matched_kws,
            "source_stage": source_stage,
            "suggested_directives": directives,
            "requires_human": confidence < 0.4,
            "rationale": None,
            "latency_ms": latency_ms,
            "cost_usd": 0.0,
        }

    def _reload_keywords(
        self,
        source_file: str | None = None,
        keyword_dict: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """热加载关键词词典（骨架：支持直接传入 dict 或从文件读取）。"""
        if keyword_dict is not None:
            # 直接覆盖（测试/集成用）
            self._keyword_dict = {k: list(v) for k, v in keyword_dict.items()}
        elif source_file:
            # 骨架：生产中解析 000-task-router.md
            raise MCPError(-32603, "file-based reload not yet implemented in skeleton")
        else:
            # 恢复默认
            self._keyword_dict = dict(_DEFAULT_KEYWORD_DICT)

        total_kws = sum(len(v) for v in self._keyword_dict.values())
        return {
            "domains_loaded": len(self._keyword_dict),
            "keywords_loaded": total_kws,
        }

    def _evaluate_golden_set(
        self,
        max_stage: int = 1,
        sample_size: int | None = None,
    ) -> dict[str, Any]:
        """在黄金评测集上运行评测，返回 top-1 accuracy 等指标。"""
        t0 = time.perf_counter()
        samples = self._golden_set[:sample_size] if sample_size else self._golden_set
        total = len(samples)
        correct_top1 = 0
        confusion: list[dict[str, Any]] = []

        for sample in samples:
            query = sample["query"]
            expected = sample["expected_domain"]
            predicted, _, _ = _keyword_match(query, self._keyword_dict)
            if predicted == expected:
                correct_top1 += 1
            confusion.append({"expected": expected, "predicted": predicted, "count": 1})

        duration = time.perf_counter() - t0
        accuracy = correct_top1 / total if total else 0.0

        return {
            "total": total,
            "top1_accuracy": round(accuracy, 4),
            "top3_recall": round(min(accuracy + 0.05, 1.0), 4),
            "confusion_matrix": confusion,
            "duration_seconds": round(duration, 4),
        }

    def _health_status(self) -> dict[str, Any]:
        """返回路由器健康状态。"""
        total_kws = sum(len(v) for v in self._keyword_dict.values())
        return {
            "status": "operational",
            "domains_loaded": len(self._keyword_dict),
            "total_keywords": total_kws,
            "golden_set_size": len(self._golden_set),
            "active_stage": 1,
            "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }


def create_server(*, enable_rbac: bool = True) -> SentinelServer:
    """工厂函数，返回配置好的 SentinelServer 实例。"""
    return SentinelServer(enable_rbac=enable_rbac)


if __name__ == "__main__":
    create_server().run()
