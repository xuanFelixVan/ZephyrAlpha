# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | CT-ORC-CE-001
# [MODULE] zephyr.trading.orchestrator.execution.task_context_builder
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.integration.shared.schema.schemas
# [CONSUMERS] zephyr.trading.orchestrator.context_bridge
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 四阶段流水线(build/compress/validate/inject); missing文件不阻塞返回partial; ContextAssembler不可用降级
# [MODIFY-GUARD] CT-ORC-CE-001 必须同步更新orchestrator/context_bridge
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 蓝图文件缺失返回status=partial; ContextAssembler不可用返回status=degraded
# [TESTS] scripts/connect/orc_ce.py --trigger
# [A_module] module_id=MOD-ORC_task_context_builder | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""CE 任务上下文构建器 — build_from_task() 消费者

CT-ORC-CE-001: 接收 Orc 的上下文请求, 四阶段构建可注入的执行上下文。
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

__all__ = [
    "TaskContextBuilder",
    "TaskContextResponse",
]


class TaskContextResponse:
    def __init__(
        self,
        task_id: str = "",
        blocks: list[dict[str, Any]] | None = None,
        total_tokens: int = 0,
        status: str = "pending",
        build_stages: dict[str, float] | None = None,
        error: str | None = None,
    ):
        self.task_id = task_id
        self.blocks = blocks or []
        self.total_tokens = total_tokens
        self.status = status
        self.build_stages = build_stages or {}
        self.error = error

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "blocks": self.blocks,
            "total_tokens": self.total_tokens,
            "status": self.status,
            "build_stages": self.build_stages,
            "error": self.error,
        }


class TaskContextBuilder:
    def build_from_task(
        self,
        task_id: str,
        task_type: str = "code_construction",
        blueprint_refs: list[str] | None = None,
        file_context: list[str] | None = None,
        max_tokens: int = 8000,
        session_id: str = "",
    ) -> TaskContextResponse:
        stages: dict[str, float] = {}

        blocks: list[dict[str, Any]] = []
        total_tokens = 0
        status = "pending"

        t0 = time.perf_counter()

        try:
            blueprint_refs = blueprint_refs or []
            file_context = [str(f) for f in (file_context or [])]

            result = _build_context_blocks(task_id, task_type, blueprint_refs, file_context, max_tokens)
            blocks = result["blocks"]
            total_tokens = result["total_tokens"]
            status = result["status"]
        except Exception as exc:
            logger.error("[CE-TCB] build failed: %s", exc)
            status = "degraded"
        finally:
            stages["build_ms"] = round((time.perf_counter() - t0) * 1000, 1)

        t0 = time.perf_counter()
        if blocks and total_tokens > max_tokens:
            try:
                compressed = _compress_blocks(blocks, max_tokens)
                blocks = compressed["blocks"]
                total_tokens = compressed["total_tokens"]
            except Exception as exc:
                logger.warning("[CE-TCB] compress failed: %s", exc)
        stages["compress_ms"] = round((time.perf_counter() - t0) * 1000, 1)

        t0 = time.perf_counter()
        try:
            validated = _validate_blocks(blocks)
            blocks = validated
        except Exception as exc:
            logger.warning("[CE-TCB] validate failed: %s", exc)
        stages["validate_ms"] = round((time.perf_counter() - t0) * 1000, 1)

        t0 = time.perf_counter()
        _inject_log(task_id, blocks, total_tokens, session_id)
        stages["inject_ms"] = round((time.perf_counter() - t0) * 1000, 1)

        logger.info(
            "[ORC-CE] context built: task=%s status=%s tokens=%d blocks=%d stages=%s",
            task_id,
            status,
            total_tokens,
            len(blocks),
            stages,
        )

        return TaskContextResponse(
            task_id=task_id,
            blocks=blocks,
            total_tokens=total_tokens,
            status=status,
            build_stages=stages,
        )


def _build_context_blocks(
    task_id: str,
    task_type: str,
    blueprint_refs: list[str],
    file_context: list[str],
    max_tokens: int,
) -> dict[str, Any]:
    blocks: list[dict[str, Any]] = []
    total_tokens = 0
    status = "complete"

    for ref in blueprint_refs:
        blocks.append(
            {
                "type": "blueprint",
                "content": f"[BLUEPRINT] {ref} — 蓝图引用 (task={task_type})",
                "tokens": 50,
                "source": ref,
                "priority": "required",
            }
        )
        total_tokens += 50

    for fpath in file_context:
        resolved = Path(fpath)
        if resolved.exists():
            try:
                content = resolved.read_text(encoding="utf-8")
                tokens = len(content) // 3
                blocks.append(
                    {
                        "type": "code",
                        "content": content[:5000],
                        "tokens": min(tokens, 2000),
                        "source": str(resolved),
                        "priority": "recommended",
                    }
                )
                total_tokens += min(tokens, 2000)
            except Exception:
                status = "partial"
                blocks.append(
                    {
                        "type": "code",
                        "content": "",
                        "tokens": 0,
                        "source": str(resolved),
                        "priority": "optional",
                    }
                )
        else:
            status = "partial" if status == "complete" else status
            blocks.append(
                {
                    "type": "code",
                    "content": "",
                    "tokens": 0,
                    "source": str(resolved),
                    "priority": "optional",
                }
            )

    try:
        conventions = _load_conventions(task_type)
        if conventions:
            blocks.append(
                {
                    "type": "convention",
                    "content": json.dumps(conventions, ensure_ascii=False),
                    "tokens": 100,
                    "source": "zephyr/shared/schema/conventions",
                    "priority": "required",
                }
            )
            total_tokens += 100
    except Exception as e:
        logger.warning("suppressed error in task_context_builder", exc_info=True)

    return {"blocks": blocks, "total_tokens": total_tokens, "status": status}


def _compress_blocks(blocks: list[dict[str, Any]], max_tokens: int) -> dict[str, Any]:
    new_blocks = []
    new_tokens = 0
    for b in blocks:
        if b.get("priority") == "required":
            new_blocks.append(b)
            new_tokens += b.get("tokens", 0)
        elif b.get("priority") == "recommended":
            if new_tokens + b.get("tokens", 0) <= max_tokens:
                new_blocks.append(b)
                new_tokens += b.get("tokens", 0)
            else:
                truncated = dict(b)
                truncated["content"] = truncated.get("content", "")[:2000]
                truncated["tokens"] = min(truncated.get("tokens", 500), 800)
                if new_tokens + truncated["tokens"] <= max_tokens:
                    new_blocks.append(truncated)
                    new_tokens += truncated["tokens"]
        else:
            if new_tokens + b.get("tokens", 0) <= max_tokens:
                new_blocks.append(b)
                new_tokens += b.get("tokens", 0)
    return {"blocks": new_blocks, "total_tokens": new_tokens}


def _validate_blocks(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    validated = []
    for b in blocks:
        if not b.get("source"):
            continue
        validated.append(b)
    return validated


def _inject_log(task_id: str, blocks: list[dict[str, Any]], total_tokens: int, session_id: str) -> None:
    sources = [b.get("source", "?") for b in blocks[:5]]
    logger.info(
        "[ORC-CE] inject: task=%s session=%s blocks=%d tokens=%d sources=%s",
        task_id,
        session_id,
        len(blocks),
        total_tokens,
        sources,
    )


def _load_conventions(task_type: str) -> dict[str, Any] | None:
    try:
        from zephyr.integration.shared.schema.schemas import BASE_CONFIG

        return {"task_type": task_type, "config": str(BASE_CONFIG)[:200]}
    except Exception:
        return None
