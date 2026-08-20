# [BLUEPRINT] MOD-GOV_ERROR_PATTERN_CONSUMER | docs/03_modules/_domain_governance/blueprint.md | §ARCH-PREVENTABILITY-LAYER-001 Phase 4 P4-1b
# [MODULE] zephyr.governance.audit.error_pattern_consumer_reconciler
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit.reconciliation_registry (ReconcileResult, ReconcilerSpec); stdlib (json, hashlib, logging, time, pathlib)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] post-commit 事件触发；reconciler 永不抛异常（异常降级为 warn）；只读 telemetry JSONL，不修改源文件；输出到 .runtime/ai_error_patterns/aggregated_patterns.json；幂等（全量重扫覆盖输出）
# [MODIFY-GUARD] _GATE_ID / _PRIORITY / _PATTERNS_VERSION / _PATTERN_ID_PREFIX / _TELEMETRY_GLOB
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] reconcile 永不抛异常——读取/解析失败降级为 ReconcileResult(action="warn")
# [TESTS] tests/governance/audit/test_error_pattern_consumer.py
# [A_module] module_id=MOD-GOV_ERROR_PATTERN_CONSUMER | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: reconciler 是 commit 事件触发(非 cron/manual)
"""

error_pattern_consumer_reconciler.py — AI 行为遥测 JSONL 错误事件聚合 consumer。

post-commit 事件触发，扫描 ``data/telemetry/prod/logs/telemetry_*.jsonl`` 下
AI behavior events（``labels.__type == "ai_behavior_event"``），过滤含 ``error``
字段的事件，按 ``(error_type, persistence, source)`` 三元组计算指纹聚合，持久化到
``.runtime/ai_error_patterns/aggregated_patterns.json``。

P4-1b（#ARCH-PREVENTABILITY-LAYER-001 Phase 4，2026-07-20）
-----------------------------------------------------------
- **治本动机**：``event_sink.py`` 的 JSONL 事件无消费方，错误模式散落在日志中
  无法被 P4-1 ``ai_error_pattern_library.py`` 消费。本 consumer 是 JSONL →
  聚合模式库的桥梁，为 P4-1 提供结构化输入。
- **输出格式**::

    {
      "version": "1.0",
      "last_updated": int,
      "total_events": int,
      "patterns": [
        {
          "pattern_id": "EP-xxxxxxxxxxxxxxxx",
          "error_type": str,
          "persistence": str,
          "source": str,
          "count": int,
          "first_seen": str,
          "last_seen": str,
          "expectation_dist": {"expected": int, "unexpected": int, "unknown": int},
          "severity_dist": {"degraded": int, "blocking": int, "fatal": int}
        }
      ]
    }

- **pattern_id 格式**：``EP-`` + sha1(error_type|persistence|source)[:16]，供 P4-1
  回填 ``reconcile_execution_log.error_pattern_id`` 使用（P4-1a 已扩展 schema）。
- **幂等**：每次 reconcile 重新扫描全量 JSONL 并覆盖输出（非增量），确保结果一致。

Usage
-----
::

    from zephyr.governance.audit.error_pattern_consumer_reconciler import (
        make_error_pattern_consumer_reconciler,
    )

    registry.register(make_error_pattern_consumer_reconciler(gateway))

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: AI 行为遥测 JSONL
#   fields: labels.__type=ai_behavior_event + error{error_type,persistence,source,expectation,severity} + ts
#   code: _iter_error_events L119（data/telemetry/prod/logs/telemetry_*.jsonl）
# - id: I2
#   name: 聚合输出路径
#   fields: .runtime/ai_error_patterns/aggregated_patterns.json
#   code: _OUTPUT_SUBDIR/_OUTPUT_FILENAME L95-96
# 层: 算法
# - id: A1
#   name_zh: ① 错误事件过滤迭代
#   name_en: _iter_error_events + _is_ai_behavior_error_event
#   intro: 逐行解析 JSONL，只留含 error_type 的 AI 行为事件
#   desc: __type==ai_behavior_event 且 error.error_type 非空才 yield；坏行/坏文件跳过 fail-open
#   inputs: I1
#   outputs: 错误事件流
# - id: A2
#   name_zh: ② 错误模式指纹计算
#   name_en: compute_error_pattern_id
#   intro: 用错误三元组算稳定指纹作为模式 ID
#   desc: pattern_id = EP- + sha1(error_type|persistence|source) 前 16 字符；expectation/severity 不计入指纹
#   inputs: A1
#   outputs: EP-xxxxxxxxxxxxxxxx 模式 ID
# - id: A3
#   name_zh: ③ 单事件聚合合并
#   name_en: _merge_event_into_patterns
#   intro: 把每条事件累进对应模式的计数与分布
#   desc: count+1；first_seen 取最小 ts、last_seen 取最大 ts；expectation/severity 分布逐项 +1
#   inputs: A1 A2
#   outputs: patterns 聚合字典
# - id: A4
#   name_zh: ④ 全量聚合与持久化
#   name_en: aggregate_error_patterns
#   intro: 全量重扫所有遥测文件并覆盖写出聚合结果，保证幂等
#   desc: 重新扫描全量 JSONL → result{version,last_updated,total_events,patterns} → 写 JSON；写失败仅 warning
#   inputs: A3 I2
#   outputs: 聚合结果 dict（落盘 + 返回）
#   invariant: 幂等（全量重扫覆盖输出）
# 层: 输出
# - id: O1
#   name_zh: 对账结果 ReconcileResult
#   name_en: ReconcileResult
#   intro: clean=聚合完成（含 N 模式 M 事件摘要），warn=聚合异常
#   downstream: GitCommitGateway MOD-INF-035
# - id: O2
#   name_zh: 聚合错误模式库
#   name_en: aggregated_patterns.json
#   intro: 结构化错误模式库，供 P4-1 模式库消费回填 error_pattern_id
#   downstream: ai_error_pattern_library（P4-1 消费，回填 reconcile_execution_log.error_pattern_id）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A1 --> A3
# A2 --> A3
# A3 --> A4
# I2 --> A4
# A4 --> O1
# A4 --> O2
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterator

from zephyr.governance.audit.reconciliation_registry import (
    ReconcileResult,
    ReconcilerSpec,
)

logger = logging.getLogger(__name__)

_GATE_ID = "GATE-ERROR-PATTERN-CONSUMER"
# priority=880: 晚于 commit_gateway_abuse_monitor(875)，早于 remediation_progress(900)
_PRIORITY = 880

_PATTERNS_VERSION = "1.0"
_PATTERN_ID_PREFIX = "EP-"
# SHA1 截取长度（16 字符 = 64 位熵，足够区分错误模式）
_PATTERN_ID_HASH_LEN = 16

# telemetry JSONL 文件 glob（由 structured_sink._resolve_target_path 产出）
_TELEMETRY_GLOB = "telemetry_*.jsonl"

# 聚合输出路径（相对于 repo_root）
_OUTPUT_SUBDIR = Path(".runtime", "ai_error_patterns")
_OUTPUT_FILENAME = "aggregated_patterns.json"


def compute_error_pattern_id(error_type: str, persistence: str, source: str) -> str:
    """计算错误模式 ID（P4-1b）。

    基于 ``(error_type, persistence, source)`` 三元组计算 SHA1 指纹，截取前 16
    字符作为 pattern_id。这三元组是错误模式最稳定的身份标识（expectation /
    severity 是同一模式的不同表现，不计入指纹）。

    Args:
        error_type: 错误类型字符串（如 ``"ConnectionError"``）。
        persistence: 错误持续性（``transient|permanent|intermittent``）。
        source: 错误来源（``client|server|dependency|internal``）。

    Returns:
        str — ``EP-`` + 16 字符 hex 摘要（如 ``"EP-a1b2c3d4e5f67890"``）。
    """
    raw = f"{error_type}|{persistence}|{source}"
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()
    return f"{_PATTERN_ID_PREFIX}{digest[:_PATTERN_ID_HASH_LEN]}"


def _iter_error_events(telemetry_dir: Path) -> Iterator[dict[str, Any]]:
    """扫描 telemetry JSONL 文件，yield 含 error 字段的 AI behavior events。

    fail-open：单文件读取/解析失败跳过（不中断扫描）。

    Args:
        telemetry_dir: ``data/telemetry/prod/logs`` 目录路径。

    Yields:
        dict[str, Any] — 单条事件的 JSON 解析结果（含 ``error`` 字段）。
    """
    if not telemetry_dir.exists():
        return
    for jsonl_path in sorted(telemetry_dir.glob(_TELEMETRY_GLOB)):
        try:
            text = jsonl_path.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            logger.warning("P4-1b: read %s failed (%s), skipping", jsonl_path, e)
            continue
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue  # 跳过损坏行
            if not _is_ai_behavior_error_event(entry):
                continue
            yield entry


def _is_ai_behavior_error_event(entry: dict[str, Any]) -> bool:
    """判断是否为含 error 的 AI behavior event（P4-1b 内部 helper）。"""
    labels = entry.get("labels")
    if not isinstance(labels, dict):
        return False
    if labels.get("__type") != "ai_behavior_event":
        return False
    error = entry.get("error")
    return isinstance(error, dict) and bool(error.get("error_type"))


def _merge_event_into_patterns(
    patterns: dict[str, dict[str, Any]],
    event: dict[str, Any],
) -> None:
    """将单条事件合并到 patterns dict（P4-1b 内部 helper，in-place 修改）。"""
    error = event["error"]
    error_type = error.get("error_type", "unknown")
    persistence = error.get("persistence", "unknown")
    source = error.get("source", "unknown")
    expectation = error.get("expectation", "unknown")
    severity = error.get("severity", "unknown")
    ts = event.get("ts", "")

    pattern_id = compute_error_pattern_id(error_type, persistence, source)
    if pattern_id not in patterns:
        patterns[pattern_id] = {
            "pattern_id": pattern_id,
            "error_type": error_type,
            "persistence": persistence,
            "source": source,
            "count": 0,
            "first_seen": ts,
            "last_seen": ts,
            "expectation_dist": {},
            "severity_dist": {},
        }
    pat = patterns[pattern_id]
    pat["count"] += 1
    if ts:
        if not pat["first_seen"] or ts < pat["first_seen"]:
            pat["first_seen"] = ts
        if ts > pat["last_seen"]:
            pat["last_seen"] = ts
    pat["expectation_dist"][expectation] = pat["expectation_dist"].get(expectation, 0) + 1
    pat["severity_dist"][severity] = pat["severity_dist"].get(severity, 0) + 1


def _persist_patterns(output_path: Path, result: dict[str, Any]) -> None:
    """持久化聚合结果到 JSON 文件（P4-1b 内部 helper）。

    fail-open：写入失败仅记 warning（reconciler 永不抛异常）。
    """
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError as e:
        logger.warning("P4-1b: persist patterns to %s failed: %s", output_path, e)


def aggregate_error_patterns(telemetry_dir: Path, output_path: Path) -> dict[str, Any]:
    """扫描 telemetry JSONL，聚合错误模式，持久化到 output_path（P4-1b 核心）。

    幂等：每次调用重新扫描全量 JSONL 并覆盖输出（非增量），确保结果一致。

    Args:
        telemetry_dir: ``data/telemetry/prod/logs`` 目录路径。
        output_path: 聚合结果输出文件路径（如
            ``.runtime/ai_error_patterns/aggregated_patterns.json``）。

    Returns:
        dict[str, Any] — 聚合结果（同时持久化到 output_path）。
    """
    patterns: dict[str, dict[str, Any]] = {}
    total_events = 0
    for event in _iter_error_events(telemetry_dir):
        total_events += 1
        _merge_event_into_patterns(patterns, event)

    result = {
        "version": _PATTERNS_VERSION,
        "last_updated": int(datetime.now(UTC).timestamp()),
        "total_events": total_events,
        "patterns": list(patterns.values()),
    }
    _persist_patterns(output_path, result)
    return result


def make_error_pattern_consumer_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 GATE-ERROR-PATTERN-CONSUMER post-commit 对账 reconciler（P4-1b）。

    闭包捕获 gateway 实例以复用 ``project_root``。每次 commit 触发全量扫描
    telemetry JSONL（与 manifest_reconciler / drift_scan_reconciler 全量扫描
    模式一致）。

    Args:
        gateway: GitCommitGateway 实例（仅用其 project_root，类型注解为
            object 避免本纯 stdlib 模块 import zephyr.*）。

    Returns:
        ReconcilerSpec(gate_id="GATE-ERROR-PATTERN-CONSUMER", priority=880)。
    """
    project_root: Path = gateway.project_root
    telemetry_dir = project_root / "data" / "telemetry" / "prod" / "logs"
    output_path = project_root / _OUTPUT_SUBDIR / _OUTPUT_FILENAME

    def _trigger(committed_files: list[str]) -> bool:
        # 任何 commit 都可能伴随新的 AI 行为遥测事件（异步写入 JSONL），
        # 全量扫描确保聚合结果最新。与 abuse_monitor(875) 同策略。
        return True

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        try:
            result = aggregate_error_patterns(telemetry_dir, output_path)
        except Exception as e:  # noqa: BLE001 — reconciler 永不抛异常
            return ReconcileResult(
                action="warn",
                detail=f"error pattern aggregation failed: {e}",
                gate_id=_GATE_ID,
            )
        n_events = result.get("total_events", 0)
        n_patterns = len(result.get("patterns", []))
        if n_events == 0:
            return ReconcileResult(
                action="clean",
                detail="no AI behavior error events to aggregate",
                gate_id=_GATE_ID,
            )
        return ReconcileResult(
            action="clean",
            detail=f"aggregated {n_patterns} error patterns from {n_events} events",
            gate_id=_GATE_ID,
        )

    return ReconcilerSpec(
        gate_id=_GATE_ID,
        trigger=_trigger,
        reconcile=_reconcile,
        priority=_PRIORITY,
        file_ops=frozenset({"read", "write"}),
    )
