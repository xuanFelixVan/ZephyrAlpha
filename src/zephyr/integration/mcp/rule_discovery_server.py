# [BLUEPRINT] MOD-INF-014 | docs/03_modules/_cross_layer/model_context_protocol_servers/blueprint.md | §rule-discovery
# [MODULE] zephyr.integration.mcp.rule_discovery_server
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.integration.mcp._base_server; zephyr.shared.io.paths
# [CONSUMERS] AI session 冷启动；CAPABILITY-LOOKUP-REQUIRED gate（Phase 3.4a）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 真源是 rule_ai_perception_index.yaml（Phase 3.2a 生成器产出）；只读不写；fail-open（YAML缺失→空结果+error）；AI MUST 在施工前调用此工具查询适用规则（Phase 3.4a gate 强制）
# [MODIFY-GUARD] tool name rule_discovery.discover_applicable_rules；input_schema 字段
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空结果+error字段（YAML缺失/解析失败）
# [TESTS] tests/test_rule_discovery_server.py
# [A_module] module_id=MOD-INF-014 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: 无时间触发
"""

RuleDiscoveryServer — MCP Server for rule discovery（#ARCH-GOV-CONVERGENCE-META Phase 3.2b）

病根2（规则可发现性）治本：64条 trae 规则分散在各 YAML 文件中，AI 无法在施工前
快速查询"我即将做的操作命中哪些规则"。Phase 3.2a 建立了 rule_ai_perception_index.yaml
感知索引，本 server 通过 MCP 协议暴露查询能力，使 AI 可按 operation/gate_id/scope/
domain/tags 查询适用规则。

对标
----
Codified Context (arXiv 2602.20478) §3.3.1 Knowledge Retrieval Service:
  find_relevant_context(task) -> queries Cold Memory via keyword search

本 server 将 pattern 扩展到**规则级**路由：给定操作上下文，返回所有匹配的 trae 规则。

Registered Tools
----------------
- ``rule_discovery.discover_applicable_rules``:
    Input: operation/scope/domain/gate_id/tags/rule_id（均可选，至少一个）
    Output: matching rules list with rule_id/title/scope/operations/gate_ids/rule_file
    Source: ``docs/01_policies_and_standards/_registry/catalogs/rule_ai_perception_index.yaml``

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: MCP 查询过滤条件
#   fields: operation/gate_id/scope/domain/tags/rule_id + session_id（均可选）
#   code: rule_discovery.discover_applicable_rules input_schema
# - id: I2
#   name: 规则感知索引 YAML 数据
#   fields: rules 列表（rule_id/title/scope/domain/operations/gate_ids/tags/rule_file）
#   code: docs/01_policies_and_standards/_registry/catalogs/rule_ai_perception_index.yaml
# 层: 算法
# - id: A1
#   name_zh: ① 索引加载与 TTL 缓存
#   name_en: _load_index
#   intro: 读感知索引 YAML 并用 30 秒 TTL 缓存减少重复 IO
#   desc: yaml.safe_load 读 rules 列表；缓存命中直接返回；文件缺失/解析失败返回 None（fail-open）
#   inputs: I2
#   outputs: rules 列表 或 None
#   invariant: 只读不写；缓存 TTL=30s
# - id: A2
#   name_zh: ② AND 多条件规则匹配
#   name_en: _matches_rule
#   intro: 按操作/门禁/作用域/域/标签多条件过滤出适用规则
#   desc: 标量匹配(rule_id/scope/domain) + 列表包含(operation∈operations, gate_id∈gate_ids) + tags AND 匹配，全部大小写不敏感；无任何过滤条件时返回前 20 条
#   inputs: I1 A1
#   outputs: 命中的 rule 列表
# - id: A3
#   name_zh: ③ 规则摘要构建
#   name_en: _build_rule_summary
#   intro: 把命中规则裁成轻量摘要防止输出过大
#   desc: 抽取 rule_id/title/scope/domain/severity/operations/gate_ids/paired_gate_id/rule_file，剔除完整 aliases
#   inputs: A2
#   outputs: 规则摘要列表
# - id: A4
#   name_zh: ④ 查询审计日志写入
#   name_en: write_lookup_audit_log
#   intro: 把本次查询追加写进 session 级 jsonl 审计日志供门禁消费
#   desc: 写 .runtime/lookup_audit/<session_id>.jsonl（ts/tool/query/result_count/rule_ids）；best-effort 失败仅 warning 不抛异常；session_id 无效则跳过
#   inputs: I1 A3
#   outputs: 审计日志条目
#   invariant: fail-open 不影响查询结果
# 层: 输出
# - id: O1
#   name_zh: 适用规则查询结果
#   name_en: discover_applicable_rules 返回 dict
#   intro: results+count+total_rules_in_index+filters+hint，YAML 缺失时返回空结果+error 字段
#   downstream: AI session 冷启动；CAPABILITY-LOOKUP-REQUIRED gate（Phase 3.4a）
# - id: O2
#   name_zh: lookup 审计日志 jsonl
#   name_en: lookup_audit_log
#   intro: session 级审计流水，证明 AI 施工前查过规则
#   downstream: CAPABILITY-LOOKUP-REQUIRED gate（Phase 3.4a）
# [/ALGO_FLOW]
#
# 边:
# I2 --> A1
# I1 --> A2
# A1 --> A2
# A2 --> A3
# I1 --> A4
# A3 --> A4
# A3 --> O1
# A4 --> O2
"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Final

import yaml

from zephyr.integration.mcp._base_server import BaseMCPServer
from zephyr.shared.io.paths import MAIN_REPO_ROOT, REPO_ROOT

__all__ = ["RuleDiscoveryServer", "main", "write_lookup_audit_log"]

_logger = logging.getLogger(__name__)

SERVER_ID: Final[str] = "rule_discovery"
SERVER_VERSION: Final[str] = "1.0.0"
SERVER_DESCRIPTION: Final[tuple] = (
    "Rule discovery MCP server — finds applicable trae rules for a given "
    "operation/scope/domain context via rule_ai_perception_index.yaml. "
    "#ARCH-GOV-CONVERGENCE-META Phase 3.2b."
)

PERCEPTION_INDEX_PATH: Final[Path] = (
    REPO_ROOT
    / "docs"
    / "01_policies_and_standards"
    / "_registry"
    / "catalogs"
    / "rule_ai_perception_index.yaml"
)

# Phase 3.4a: audit log 目录——CAPABILITY-LOOKUP-REQUIRED gate 消费
# 观测数据锚 MAIN_REPO_ROOT（#ARCH-WORKTREE-ENV-001）：worktree 进程内 REPO_ROOT=worktree 根，
# 审计证据写 worktree 会随 abort 丢失且与门禁读端分裂
LOOKUP_AUDIT_DIR: Final[Path] = MAIN_REPO_ROOT / ".runtime" / "lookup_audit"

# session_id 环境变量（与 session_worktree 启动时设置的 env 对齐）
SESSION_ID_ENV_VAR: Final[str] = "ZEPHYR_SESSION_ID"


def _scalar_match(actual: object, expected: str) -> bool:
    """标量字符串匹配（大小写不敏感，None/空视为空串）。"""
    return str(actual or "").lower() == expected.lower()


def _list_contains(items: list[Any] | None, value: str) -> bool:
    """列表包含匹配（大小写不敏感）。"""
    if not items:
        return False
    lower_items = [str(i).lower() for i in items]
    return value.lower() in lower_items


def _tags_match(rule_tags: list[Any] | None, expected_tags: list[str]) -> bool:
    """tags AND 匹配（所有 expected_tags 都需在 rule_tags 中，大小写不敏感）。"""
    if not rule_tags:
        return False
    rule_tags_lower = [str(t).lower() for t in rule_tags]
    return all(str(t).lower() in rule_tags_lower for t in expected_tags)


def _matches_rule(
    rule: dict[str, Any],
    operation: str | None,
    gate_id: str | None,
    scope: str | None,
    domain: str | None,
    tags: list[str] | None,
    rule_id: str | None,
) -> bool:
    """检查规则是否匹配所有提供的过滤条件（AND 逻辑）。"""
    # 标量过滤：rule_id / scope / domain（直接字段比对）
    scalar_filters: tuple[tuple[str | None, str], ...] = (
        (rule_id, "rule_id"),
        (scope, "scope"),
        (domain, "domain"),
    )
    for expected, field in scalar_filters:
        if expected is not None and not _scalar_match(rule.get(field), expected):
            return False
    # 列表过滤：operation → operations, gate_id → gate_ids
    list_filters: tuple[tuple[str | None, str], ...] = (
        (operation, "operations"),
        (gate_id, "gate_ids"),
    )
    for expected, field in list_filters:
        if expected is not None and not _list_contains(rule.get(field), expected):
            return False
    # tags AND 过滤
    if tags and not _tags_match(rule.get("tags"), tags):
        return False
    return True


def _build_rule_summary(rule: dict[str, Any]) -> dict[str, Any]:
    """构建规则摘要（不含完整 aliases，避免输出过大）。"""
    return {
        "rule_id": rule.get("rule_id", ""),
        "title": rule.get("title", ""),
        "scope": rule.get("scope", ""),
        "domain": rule.get("domain", ""),
        "severity": rule.get("severity", ""),
        "operations": rule.get("operations", []) or [],
        "gate_ids": rule.get("gate_ids", []) or [],
        "paired_gate_id": rule.get("paired_gate_id"),
        "rule_file": rule.get("rule_file", ""),
    }


def write_lookup_audit_log(
    session_id: str,
    query: dict[str, Any],
    result_count: int,
    rule_ids: list[str],
    tool: str = "rule_discovery.discover_applicable_rules",
) -> None:
    """写入 session 级 lookup audit log（best-effort，失败不抛异常）。

    Phase 3.4a：CAPABILITY-LOOKUP-REQUIRED gate 消费此 log 判断 AI 是否在施工前
    调用了 rule_discovery / capability_lookup。log 文件路径：
    ``.runtime/lookup_audit/<session_id>.jsonl``。

    Args:
        session_id: session 标识（必填，空串则跳过）。
        query: 调用参数 dict（如 {"operation": "file_write"}）。
        result_count: 返回结果数。
        rule_ids: 命中的 rule_id 列表（如 ["TRAE-001"]）。
        tool: 调用方 tool name（默认 rule_discovery.discover_applicable_rules）。

    失败处理：log 写入失败仅 logger.warning，不抛异常——MCP 工具调用不应因
    audit log 故障失败（fail-open）。gate 端会处理 log 缺失的情况（fail-closed）。
    """
    if not session_id or session_id in ("unknown", "none", "null"):
        return  # 无有效 session_id，跳过 audit log
    try:
        LOOKUP_AUDIT_DIR.mkdir(parents=True, exist_ok=True)
        log_path = LOOKUP_AUDIT_DIR / f"{session_id}.jsonl"
        entry = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "tool": tool,
            "query": query,
            "result_count": result_count,
            "rule_ids": rule_ids,
        }
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError as exc:
        _logger.warning(
            "rule_discovery: audit log 写入失败 (session=%s): %s",
            session_id, exc, exc_info=True,
        )
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
        _logger.warning(
            "rule_discovery: audit log 写入异常 (session=%s): %s: %s",
            session_id, type(exc).__name__, exc, exc_info=True,
        )


class RuleDiscoveryServer(BaseMCPServer):
    """MCP server for discovering applicable trae rules.

    真源：rule_ai_perception_index.yaml（由 generate_rule_ai_perception_index.py 生成）
    查询：按 operation/gate_id/scope/domain/tags/rule_id 过滤（AND 逻辑）
    """

    def __init__(self) -> None:
        super().__init__(SERVER_ID, SERVER_VERSION, SERVER_DESCRIPTION)
        self._cache: dict[str, tuple[float, list[dict[str, Any]]]] = {}
        self._cache_ttl: float = 30.0

        self.register_tool(
            name="rule_discovery.discover_applicable_rules",
            description=(
                "查询当前操作上下文适用的 trae 规则。AI MUST 在施工前（写第一行业务代码前）"
                "调用此工具，按即将执行的操作类型（operation）或作用域（scope/domain）"
                "查询适用的治理规则。返回规则列表含 rule_id/title/operations/gate_ids/"
                "rule_file 路径。真源：rule_ai_perception_index.yaml（64条规则）。"
                "调用会被记录到 session audit log（CAPABILITY-LOOKUP-REQUIRED gate 消费）。"
                "#ARCH-GOV-CONVERGENCE-META Phase 3.2b/3.4a。"
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": "操作类型（如 file_write/code_naming/db_write）",
                    },
                    "gate_id": {
                        "type": "string",
                        "description": "门禁 ID（如 G0/GATE-ARCH）",
                    },
                    "scope": {
                        "type": "string",
                        "description": "作用域（如 file_operation/feature_creation）",
                    },
                    "domain": {
                        "type": "string",
                        "description": "域（如 TRAE/GOVERNANCE）",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "标签过滤（AND 逻辑，所有 tag 都需匹配）",
                    },
                    "rule_id": {
                        "type": "string",
                        "description": "按规则 ID 精确查询（如 TRAE-001）",
                    },
                    "session_id": {
                        "type": "string",
                        "description": (
                            "AI session 标识（用于 audit log）。可选——未提供时"
                            "从 ZEPHYR_SESSION_ID 环境变量读取。Phase 3.4a "
                            "CAPABILITY-LOOKUP-REQUIRED gate 消费此 log 强制"
                            "AI 在施工前查询适用规则。"
                        ),
                    },
                },
                "additionalProperties": False,
            },
            handler=self._discover_applicable_rules,
        )

    def discover_applicable_rules(
        self,
        operation: str | None = None,
        gate_id: str | None = None,
        scope: str | None = None,
        domain: str | None = None,
        tags: list[str] | None = None,
        rule_id: str | None = None,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        """公共接口：discover_applicable_rules（Stage 4 公共化）。

        默认值与私有 ``_discover_applicable_rules`` 对齐——Stage 4 公共化时
        漏带默认值，调用方按私有契约用 keyword args 调用会触发
        "missing 5 required positional arguments"（commit c8b1b8e493 回归）。
        """
        return self._discover_applicable_rules(operation, gate_id, scope, domain, tags, rule_id, session_id)


    # ------------------------------------------------------------------
    # Tool handlers
    # ------------------------------------------------------------------

    def _discover_applicable_rules(
        self,
        operation: str | None = None,
        gate_id: str | None = None,
        scope: str | None = None,
        domain: str | None = None,
        tags: list[str] | None = None,
        rule_id: str | None = None,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        """查询适用规则。

        至少提供一个过滤条件；若全为 None 则返回全部规则（limit 20）。
        Phase 3.4a: 调用结果写入 session audit log（best-effort）。
        """
        rules = self._load_index()
        if rules is None:
            return {
                "results": [],
                "count": 0,
                "source": "rule_ai_perception_index.yaml",
                "error": "perception_index_not_loaded",
            }

        # 若无任何过滤条件，返回全部（limit 20）
        has_filter = any(
            v is not None and v
            for v in (operation, gate_id, scope, domain, rule_id)
        ) or (tags is not None and tags)
        if has_filter:
            matched = [
                r for r in rules
                if _matches_rule(r, operation, gate_id, scope, domain, tags, rule_id)
            ]
        else:
            matched = rules[:20]

        summaries = [_build_rule_summary(r) for r in matched]

        # Phase 3.4a: 写入 session audit log（best-effort，失败不影响查询结果）
        effective_sid = session_id or os.environ.get(SESSION_ID_ENV_VAR, "")
        if effective_sid:
            query_record = {
                "operation": operation,
                "gate_id": gate_id,
                "scope": scope,
                "domain": domain,
                "tags": tags,
                "rule_id": rule_id,
            }
            rule_ids_hit = [s.get("rule_id", "") for s in summaries if s.get("rule_id")]
            write_lookup_audit_log(
                session_id=effective_sid,
                query=query_record,
                result_count=len(summaries),
                rule_ids=rule_ids_hit,
            )

        return {
            "results": summaries,
            "count": len(summaries),
            "total_rules_in_index": len(rules),
            "source": "rule_ai_perception_index.yaml",
            "filters": {
                "operation": operation,
                "gate_id": gate_id,
                "scope": scope,
                "domain": domain,
                "tags": tags,
                "rule_id": rule_id,
            },
            "hint": (
                "AI MUST 阅读返回的 rule_file 路径指向的 YAML 全文后再施工。"
                "Phase 3.4a CAPABILITY-LOOKUP-REQUIRED gate 将强制此调用。"
            ) if summaries else "No matching rules found. Check filter values.",
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _load_index(self) -> list[dict[str, Any]] | None:
        """加载感知索引（带 TTL 缓存）。"""
        cache_key = "__index__"
        now = time.monotonic()
        cached = self._cache.get(cache_key)
        if cached and (now - cached[0]) < self._cache_ttl:
            return cached[1]

        if not PERCEPTION_INDEX_PATH.exists():
            _logger.warning("perception index not found at %s", PERCEPTION_INDEX_PATH)
            return None

        try:
            data = yaml.safe_load(PERCEPTION_INDEX_PATH.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            _logger.error("Failed to load perception index: %s", exc, exc_info=True)
            return None

        if not isinstance(data, dict):
            return None

        rules = data.get("rules", []) or []
        self._cache[cache_key] = (now, rules)
        return rules


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Start the rule discovery MCP server on stdio."""
    import sys as _sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
        stream=_sys.stderr,
    )

    server = RuleDiscoveryServer()
    server.run()


if __name__ == "__main__":
    main()
