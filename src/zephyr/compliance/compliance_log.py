# [BLUEPRINT] MOD-CMP-010 | docs/03_modules/_domain_compliance/compliance_log/blueprint.md
# [MODULE] zephyr.compliance.compliance_log
# [DOMAIN] D_COMPLIANCE
# [DEPENDENCIES] stdlib + zephyr.shared.io.paths
# [CONSUMERS] zephyr.compliance.discipline_must_do_checker ; zephyr.compliance.discipline_prohibition_checker ; zephyr.compliance.license_usage_auditor ; zephyr.compliance.hard_boundary_adjudicator ; zephyr.compliance.trading_compliance_detector ; zephyr.compliance.compliance_report_registry
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] append-only（只增不改不删）; 每行一条合法 JSON（JSONL）; 落盘失败不抛业务异常（返回 None 并 stderr 留痕）; 默认锚定 MAIN_REPO_ROOT（仓级业务证据归主仓）
# [MODIFY-GUARD] 43_compliance_discipline.md §3.2（compliance_log 载体裁定）
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ComplianceLogError(ZA-CMP-0010)
# [TESTS] tests/compliance/test_compliance_log.py
# [TTL] permanent

"""
合规日志 JSONL 落库（43_compliance_discipline §3.2/§7.6）。

MVP 载体裁定：合规检测结果落 ``data/compliance_log/compliance_log.jsonl``
（结构化 JSONL），达 3-5 个同类 artifact 再议生成器/数据库（01 号规范 §6）。

设计要点：
- **append-only**：只追加，不改不删，满足"自证清白"证据链语义（43 号 §7.3）。
- **单写者线程安全**：进程内锁；多进程并发写由调用方串行化（单人单系统场景）。
- **Fail-Silent 不 Fail-Open**：落盘 I/O 失败返回 None 并 stderr 留痕，
  绝不因日志失败阻断交易链路（交易阻断语义由各检测器自身承担）。
- **测试隔离**：路径可注入，测试写 tmp_path，不污染生产证据链。

Version: 1.0.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: path 参数
#   fields: 参数 path（无注解）
#   code: compliance_log.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ComplianceLogger
#   name_en: ComplianceLogger
#   intro: compliance_log JSONL 追写器。
#   desc: compliance_log JSONL 追写器。 Args: path: 日志文件路径；None 时用默认生产路径（MAIN_REPO_ROOT 锚定）。；公共方法（定义序）: path, log, read_all…
#   inputs: path
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: ComplianceLogger
#   downstream: zephyr.compliance.discipline_must_do_checker ; zephyr.compliance.discipline_pro…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import json
import sys
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from zephyr.shared.foundation.errors import ZephyrBaseError
from zephyr.shared.io.paths import MAIN_REPO_ROOT

DEFAULT_LOG_PATH: Path = MAIN_REPO_ROOT / "data" / "compliance_log" / "compliance_log.jsonl"


class ComplianceLogError(ZephyrBaseError):
    """合规日志错误。"""

    error_code = "ZA-CMP-0010"


@dataclass(frozen=True)
class ComplianceLogRecord:
    """一条合规日志记录（不可变）。"""

    ts: str  # ISO 8601 UTC 时间戳
    event_type: str  # 事件类型（如 CHECKLIST_VERDICT / DISCIPLINE_VERDICT）
    source: str  # 产生模块（如 discipline_prohibition_checker）
    payload: dict[str, Any] = field(default_factory=dict)


class ComplianceLogger:
    """compliance_log JSONL 追写器。

    Args:
        path: 日志文件路径；None 时用默认生产路径（MAIN_REPO_ROOT 锚定）。
    """

    def __init__(self, path: Path | None = None) -> None:
        self._path: Path = path if path is not None else DEFAULT_LOG_PATH
        self._lock = threading.Lock()

    @property
    def path(self) -> Path:
        """当前日志文件路径。"""
        return self._path

    def log(
        self,
        event_type: str,
        source: str,
        payload: dict[str, Any] | None = None,
        *,
        now: datetime | None = None,
    ) -> ComplianceLogRecord | None:
        """追加一条记录；I/O 失败返回 None（不抛异常，不阻断调用方）。

        Args:
            event_type: 事件类型标识。
            source: 产生模块名。
            payload: 结构化载荷（必须可 JSON 序列化）。
            now: 时间注入（测试用）；None 取当前 UTC。
        """
        ts = (now or datetime.now(timezone.utc)).isoformat()
        record = ComplianceLogRecord(ts=ts, event_type=event_type, source=source, payload=payload or {})
        line = json.dumps(
            {"ts": record.ts, "event_type": record.event_type, "source": record.source, "payload": record.payload},
            ensure_ascii=False,
            default=str,
        )
        try:
            with self._lock:
                self._path.parent.mkdir(parents=True, exist_ok=True)
                with self._path.open("a", encoding="utf-8", newline="\n") as fh:
                    fh.write(line + "\n")
        except OSError as exc:  # 落盘失败：留痕不阻断
            print(f"[ComplianceLogger] write failed: {exc}", file=sys.stderr)
            return None
        return record

    def read_all(self) -> list[ComplianceLogRecord]:
        """读取全部记录（审计/复盘用）；文件不存在返回空列表。"""
        if not self._path.exists():
            return []
        records: list[ComplianceLogRecord] = []
        with self._path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                raw = json.loads(line)
                records.append(
                    ComplianceLogRecord(
                        ts=raw["ts"],
                        event_type=raw["event_type"],
                        source=raw["source"],
                        payload=raw.get("payload", {}),
                    )
                )
        return records
