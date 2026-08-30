# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.night_shift_queue
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.shared.schema.schemas
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
# [A_module] module_id=MOD-INF-035 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
NightShiftQueue — 夜班登记表持久化
====================================
蓝图: docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md §3.1
JSONL 持久化 + 线程安全。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: storage_path 参数
#   fields: 参数 storage_path（无注解）
#   code: night_shift_queue.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① NightShiftQueue
#   name_en: NightShiftQueue
#   intro: 夜班登记表——API 夜间执行遇到不确定时登记，留待人类裁定。
#   desc: 夜班登记表——API 夜间执行遇到不确定时登记，留待人类裁定。；公共方法（定义序）: append, pending, resolve, stats, has_unresolved, flush_all…
#   inputs: storage_path
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: NightShiftQueue
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

import json
import threading
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field

from zephyr.shared.io.serialization import filter_dataclass_fields
from zephyr.shared.schema.schemas import BASE_CONFIG
from zephyr.shared.utils.time_utils import now_utc


class NightShiftEntry(BaseModel):
    model_config = BASE_CONFIG
    id: str = Field(default="", description="NSL-{sequence}")
    timestamp: str = Field(default_factory=lambda: now_utc().isoformat())
    task_id: str = ""
    module: str = ""
    context: str = ""
    options: list[dict[str, str]] = Field(default_factory=list)
    auto_decision: str = "C"
    requires_human: bool = True
    human_decision: str | None = None
    human_timestamp: str | None = None
    human_notes: str | None = None


class NightShiftQueue:
    """夜班登记表——API 夜间执行遇到不确定时登记，留待人类裁定。"""

    def __init__(self, storage_path: Path) -> None:
        self._path = Path(storage_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._counter = self._count_existing()

    def _count_existing(self) -> int:
        if not self._path.exists():
            return 0
        count = 0
        with self._path.open(encoding="utf-8") as f:
            for _ in f:
                count += 1
        return count

    def _next_id(self) -> str:
        self._counter += 1
        return f"NSL-{self._counter:04d}"

    def append(self, entry: NightShiftEntry) -> str:
        with self._lock:
            # 5.142.4 修复: _next_id() 必须在锁内调用, 避免 += 1 与读取的读-写竞争产生重复 NSL-XXXX ID
            if not entry.id:
                entry.id = self._next_id()
            line = entry.model_dump_json() + "\n"
            # 5.169 修复：用 context manager 防止文件句柄泄漏
            with self._path.open("a", encoding="utf-8") as f:
                f.write(line)
        return entry.id

    def pending(self) -> list[NightShiftEntry]:
        results: list[NightShiftEntry] = []
        if not self._path.exists():
            return results
        # 5.169 修复：用 context manager 防止文件句柄泄漏
        with self._lock, self._path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    entry = NightShiftEntry(**filter_dataclass_fields(NightShiftEntry, data))
                    if entry.human_decision is None:
                        results.append(entry)
                except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                    continue
        return results

    def resolve(self, entry_id: str, decision: str, notes: str = "") -> bool:
        if not self._path.exists():
            return False
        lines: list[str] = []
        is_found = False
        with self._lock:
            # 5.169 修复：用 context manager 防止文件句柄泄漏
            with self._path.open(encoding="utf-8") as f:
                for line in f:
                    line_stripped = line.strip()
                    if not line_stripped:
                        continue
                    try:
                        data = json.loads(line_stripped)
                        if data.get("id") == entry_id:
                            data["human_decision"] = decision
                            data["human_timestamp"] = now_utc().isoformat()
                            data["human_notes"] = notes
                            is_found = True
                        lines.append(json.dumps(data, ensure_ascii=False) + "\n")
                    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                        lines.append(line)
            self._path.write_text("".join(lines), encoding="utf-8")
        return is_found

    def stats(self) -> dict[str, int]:
        total = 0
        resolved = 0
        if not self._path.exists():
            return {"total": 0, "pending": 0, "resolved": 0}
        # 5.169 修复：用 context manager 防止文件句柄泄漏
        with self._lock, self._path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    total += 1
                    if data.get("human_decision") is not None:
                        resolved += 1
                except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                    continue
        return {"total": total, "pending": total - resolved, "resolved": resolved}

    def has_unresolved(self) -> bool:
        return len(self.pending()) > 0

    def flush_all(self) -> None:
        pass
