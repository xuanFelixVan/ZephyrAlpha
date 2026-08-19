# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.fetch_perf_recorder
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.shared.io.paths（REPO_ROOT）
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 被动记录组件：任何失败仅 log 不抛；JSONL 按日滚动；线程安全追加
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 写入异常→log.warning+返回 None，绝不阻断调度主链路
# [TESTS] tests/zephyr/data/test_fetch_perf_recorder.py
# [A_module] module_id=MOD-L00-004-FP | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 任务执行结果
#   fields: task_id/source/capability/table/status/elapsed_sec/rows/error
# 层: 算法
# - id: A1
#   name_zh: JSONL 追加落盘
#   name_en: record_fetch_perf
#   intro: 按日滚动文件追加一行 JSON；模块级锁防多线程行交错
# 层: 输出
# - id: O1
#   name_zh: .runtime/fetch_perf/fetch_perf_YYYYMMDD.jsonl
#   name_en: 落盘路径或 None（失败）
#   intro: 为 64号 Q11 调度动态化/Q17 自动熔断供数据基础（替代 c0_meta.fetch_perf 仅测速抽样的盲区）
"""fetch_perf 被动记录通道（64号 Q16，P2，2026-08-20 AI-NIGHT-001 施工）。

裁定真源：64号 §16.2 Q16——scheduler 每次任务结束写一条运行时 fetch_perf，
让 api_status 反映真实运行而非仅测速抽样（speed_tester 只写 c0_meta.fetch_perf）。
本模块落 `.runtime/fetch_perf/fetch_perf_YYYYMMDD.jsonl`（JSONL，禁新 DDL 故不入 CH），
为 Q11 调度优先级动态化 / Q17 自动熔断参数校准供数据基础。
"""

from __future__ import annotations

import datetime
import json
import logging
import threading
from collections.abc import Mapping
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT

log = logging.getLogger(__name__)

_DEFAULT_BASE_DIR = REPO_ROOT / ".runtime" / "fetch_perf"
_write_lock = threading.Lock()


def record_fetch_perf(record: Mapping, *, base_dir: str | Path | None = None) -> Path | None:
    """追加一条 fetch_perf 记录到当日 JSONL 文件。

    Args:
        record: 记录字段（task_id/source/capability/table/status/elapsed_sec/rows/error 等）。
            ts 字段缺省时自动补当前本地时间（ISO8601）。
        base_dir: 输出目录（默认 REPO_ROOT/.runtime/fetch_perf，测试可注入临时目录）。

    Returns:
        写入的文件路径；失败返回 None（异常吞掉，被动记录不得阻断调度）。
    """
    try:
        out_dir = Path(base_dir) if base_dir is not None else _DEFAULT_BASE_DIR
        out_dir.mkdir(parents=True, exist_ok=True)
        payload = dict(record)
        payload.setdefault("ts", datetime.datetime.now().isoformat(timespec="milliseconds"))
        day = datetime.date.today().isoformat().replace("-", "")
        path = out_dir / f"fetch_perf_{day}.jsonl"
        line = json.dumps(payload, ensure_ascii=False, default=str)
        with _write_lock, open(path, "a", encoding="utf-8", newline="\n") as f:
            f.write(line + "\n")
        return path
    except Exception as e:  # noqa: BLE001 — 被动记录失败仅告警
        log.warning("fetch_perf 记录失败（不影响调度）: %s", e)
        return None
