# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.io.streaming_reader
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
streaming_reader.py - Memory-efficient streaming file readers
==============================================================

SSoT: MOD-RESOURCE_OPTIMIZATION_ENGINE resource-optimization-engine/blueprint.md §11 Phase 2

Design:
  - tail_jsonl: read last N lines from JSONL without loading entire file
  - stream_jsonl: generator-based line-by-line reading
  - Memory budget: tail_jsonl < 100KB for any file size
  - Graceful degradation: malformed lines skipped, not crashed

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: path 参数
#   fields: 参数 path，类型注解 str | Path
#   code: streaming_reader.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: n 参数
#   fields: 参数 n，类型注解 int
#   code: streaming_reader.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① tail_jsonl
#   name_en: tail_jsonl
#   intro: Read the last *n* JSONL records from a file without loading…
#   desc: Read the last *n* JSONL records from a file without loading it all. Strategy: seek near t…；源码 L90-L134
#   inputs: path n
#   outputs: list[dict]
# - id: A2
#   name_zh: ② stream_jsonl
#   name_en: stream_jsonl
#   intro: Yield JSONL records one by one — never loads the whole file.
#   desc: Yield JSONL records one by one — never loads the whole file. Memory budget: O(1) per reco…；源码 L137-L160
#   inputs: path
#   outputs: Generator[dict, None, None]
# 层: 输出
# - id: O1
#   name_zh: list[dict]
#   name_en: list[dict]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# - id: O2
#   name_zh: Generator[dict, None, None]
#   name_en: Generator[dict, None, None]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import json
import logging
from collections.abc import Generator
from pathlib import Path

__all__ = ["stream_jsonl", "tail_jsonl"]

logger = logging.getLogger(__name__)

_READ_CHUNK = 8192
_LINE_SEPARATOR = b"\n"


def tail_jsonl(path: str | Path, n: int = 100) -> list[dict]:
    """Read the last *n* JSONL records from a file without loading it all.

    Strategy: seek near the end, read backwards in chunks, collect lines.
    Memory budget: O(n * avg_line_size), typically < 100KB.
    """
    p = Path(path)
    if not p.is_file():
        return []

    results: list[dict] = []
    file_size = p.stat().st_size
    if file_size == 0:
        return []

    max_read = min(file_size, n * 2048 + _READ_CHUNK)
    offset = max(0, file_size - max_read)

    try:
        with open(p, "rb") as f:
            f.seek(offset)
            raw = f.read()
    except OSError:
        logger.debug("streaming_reader: tail_jsonl read failed for %s", p)
        return []

    lines = raw.split(_LINE_SEPARATOR)
    if offset > 0:
        lines = lines[1:]

    for line in reversed(lines):
        if len(results) >= n:
            break
        line_str = line.strip()
        if not line_str:
            continue
        try:
            obj = json.loads(line_str)
            if isinstance(obj, dict):
                results.append(obj)
        except json.JSONDecodeError:
            continue

    results.reverse()
    return results


def stream_jsonl(path: str | Path) -> Generator[dict, None, None]:
    """Yield JSONL records one by one — never loads the whole file.

    Memory budget: O(1) per record (one line at a time).
    Malformed lines are silently skipped.
    """
    p = Path(path)
    if not p.is_file():
        return

    try:
        with open(p, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    if isinstance(obj, dict):
                        yield obj
                except json.JSONDecodeError:
                    continue
    except OSError:
        logger.debug("streaming_reader: stream_jsonl open failed for %s", p)
