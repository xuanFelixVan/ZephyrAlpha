# [BLUEPRINT] MOD-DATSEC-002 | docs/03_modules/_domain_data_security/data_access_auditor/blueprint.md | §F128 接线审计落盘
# [MODULE] zephyr.data_security.wiring.audit_sink
# [DOMAIN] D_DATA_SEC
# [DEPENDENCIES] stdlib（json/logging/datetime/pathlib/dataclasses/enum）；zephyr.shared.io.paths.REPO_ROOT
# [CONSUMERS] zephyr.data_security.wiring.lsg_masking_front / zephyr.data_security.wiring.data_exit_guard
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] fail-open（落盘失败仅记日志绝不阻断主流程，对齐三实体 audit_sink 惯例）；JSONL 追加一行一事件；
#   datetime/Enum/dataclass 统一可序列化；相对路径锚定 REPO_ROOT；同输入必同输出（随机源无关）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 构造期：空 path 抛 DataMaskingError（Fail-Closed）；运行期：OSError 全吞（fail-open 审计）
# [TESTS] tests/data_security/test_wiring_audit_sink.py
# [A_module] module_id=MOD-DATSEC-004 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""JsonlAuditSink — F128 接线统一审计落盘 sink（MOD-DATSEC-004）。

F128 接线复活（st-menu-t1b2-20260930，Owner 2026-09-30 夜批 known-gap→接线复活）
回填缺口②（审计落盘真源未声明）：LSG l1 前置（MaskingAuditRecord）与数据出口
（AccessEvent/AccessAnomaly）两通道事件统一追加到规则册
``config/data_masking_policy.yaml`` 的 ``audit.jsonl_sink`` 声明路径——
一行一事件 JSONL，dataclass/datetime/Enum 自动序列化。

fail-open：审计落盘失败只 ``log.exception``，绝不向上抛——对齐三实体
（MOD-DATSEC-001/002/003）``audit_sink`` 注入惯例"审计失败不阻断主流程"。

# [ALGO_FLOW] external: docs/03_modules/_domain_data_security/algo_flow/wiring__init__.yaml
"""

from __future__ import annotations

import dataclasses
import datetime
import enum
import json
import logging
from pathlib import Path
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = ["JsonlAuditSink"]

#: 规则册声明的出厂落盘路径（相对 REPO_ROOT；真源=config/data_masking_policy.yaml audit.jsonl_sink）
DEFAULT_SINK_RELPATH: Final = "data/audit/data_security_wiring/audit.jsonl"


def _jsonify(value: object) -> object:
    """dataclass/datetime/Enum/Path 递归转 JSON 原生类型（其余交给 json 兜底）。"""
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {k: _jsonify(v) for k, v in dataclasses.asdict(value).items()}
    if isinstance(value, datetime.datetime):
        return value.isoformat()
    if isinstance(value, enum.Enum):
        return value.value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _jsonify(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonify(v) for v in value]
    return value


class JsonlAuditSink:
    """F128 接线统一审计落盘（JSONL 追加，fail-open）。"""

    def __init__(
        self,
        path: str | Path,
        *,
        repo_root: str | Path | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        if not path:
            raise ValueError("path 为空（审计落盘路径必填）")
        self._clock = clock or datetime.datetime.now
        self._path = self._resolve(path, repo_root)

    @staticmethod
    def _resolve(path: str | Path, repo_root: str | Path | None) -> Path:
        p = Path(path)
        if not p.is_absolute():
            if repo_root is not None:
                p = Path(repo_root) / p
            else:
                from zephyr.shared.io.paths import REPO_ROOT  # noqa: PLC0415 延迟 import 避免环

                p = REPO_ROOT / p
        return p

    @property
    def path(self) -> Path:
        """落盘路径（只读视图，测试断言用）。"""
        return self._path

    def __call__(self, record: object) -> None:
        """追加一行事件（fail-open：任何落盘异常吞掉并记日志）。"""
        payload = {"_written_at": self._clock().isoformat(), **_jsonify(record)}
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
        except OSError:
            _log.exception("F128 接线审计落盘失败（fail-open 放行）: %s", self._path)
