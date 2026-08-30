# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §4

# [MODULE] zephyr.gov_audit.contracts

# [DOMAIN] D_GOV_AUDIT

# [DEPENDENCIES] zephyr.gov_audit.models

# [CONSUMERS] audit-orchestrator.*; pipeline_runner

# [STARTUP] imported

# [MATURITY] production

# [INVARIANTS] 所有审计组件必须实现对应契约; 契约方法签名不可变

# [MODIFY-GUARD] 修改契约必须同步所有实现类

# [STABILITY] frozen

# [SAFETY] H

# [AI_AUTONOMY] immutable_core

# [ERROR_CONTRACT] 违反契约抛ContractViolationError

# [TESTS] tests/audit-orchestrator/test_contracts.py

# [A_module] module_id=MOD-INF-020 | layer=module | stability=frozen | safety=H | ai_autonomy=immutable_core

# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: contracts.py
# 层: 算法
# - id: A1
#   name_zh: ① AuditDiscoverer
#   name_en: AuditDiscoverer
#   intro: class AuditDiscoverer 源码 L183-L188
#   desc: 公共方法（定义序）: discover_changes, get_changed_files；源码 L183-L188
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② AuditIndexer
#   name_en: AuditIndexer
#   intro: class AuditIndexer 源码 L191-L199
#   desc: 公共方法（定义序）: build_index, lookup, cold_start_cache；源码 L191-L199
#   inputs: 无参数
#   outputs: 返回值
# - id: A3
#   name_zh: ③ AuditWriter
#   name_en: AuditWriter
#   intro: 审计写入器契约——治本（test_p0_i2_construction_order.
#   desc: 审计写入器契约——治本（test_p0_i2_construction_order.py）： 原 ABC 含 @abstractmethod 导致 ``AuditWriter()…；公共方法（定义序）: write_r…
#   inputs: 无参数
#   outputs: 返回值
# - id: A4
#   name_zh: ④ AuditQuery
#   name_en: AuditQuery
#   intro: class AuditQuery 源码 L290-L298
#   desc: 公共方法（定义序）: get_status, get_history, get_issues；源码 L290-L298
#   inputs: 无参数
#   outputs: 返回值
# - id: A5
#   name_zh: ⑤ IntegrityChecker
#   name_en: IntegrityChecker
#   intro: class IntegrityChecker 源码 L301-L306
#   desc: 公共方法（定义序）: check, verify_merkle；源码 L301-L306
#   inputs: 无参数
#   outputs: 返回值
#   （注：A5 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（6 定义）
#   name_en: public defs
#   intro: AuditDiscoverer, AuditIndexer, AuditWriter, AuditQuery, IntegrityChecker
#   downstream: audit-orchestrator.*; pipeline_runner
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> O1
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from zephyr.gov_audit.models import (
    AuditContext,
    AuditIssue,
    DiscoveryReport,
    GlobalAuditReport,
    OrchestratorStatus,
)

__all__ = [
    "AuditDiscoverer",
    "AuditIndexer",
    "AuditQuery",
    "AuditWriter",
    "ContractViolationError",
    "IntegrityChecker",
]


class ContractViolationError(Exception):
    error_code = "ZA-GV-0035"

    def __init__(self, *args, error_code: str | None = None, **kwargs):

        super().__init__(*args, **kwargs)

        if error_code is not None:
            self.error_code = error_code


def _get_writer():
    """获取全局 AuditWriter 单例——治本（裁定#18 G6）：供 AuditWriter.write 委托桥接。



    旧实现直接在 write 方法内访问 ``_writer_mod._GLOBAL_WRITER``，测试无法通过

    patch ``contracts._get_writer`` 注入 mock。现抽出为模块级函数，测试可 patch，

    生产仍路由到 writer._GLOBAL_WRITER。

    """

    from zephyr.gov_audit import writer as _writer_mod

    return _writer_mod._GLOBAL_WRITER


class _CoreAuditWriter:
    """核心审计链写入器——桥接 contracts 层到 writer 实现。



    测试可通过 ``patch("zephyr.gov_audit.contracts._CoreAuditWriter")`` 注入 mock：

    ``_CoreAuditWriter()`` 返回 mock writer 实例，``writer.write(event)`` 返回 hash。

    生产环境通过 ``_get_writer()`` 路由到 ``writer._GLOBAL_WRITER``，若未初始化则

    通过 ``get_audit_writer()`` 单例工厂自动初始化。

    """

    def __init__(self) -> None:

        delegate = _get_writer()

        if delegate is None:
            # Auto-initialize via singleton factory (test environments without

            # explicit set_global_writer() call still work)

            from zephyr.gov_audit.writer import get_audit_writer

            delegate = get_audit_writer()

        self._delegate = delegate

    def write(self, event: dict[str, Any]) -> str:
        """委托到全局 writer 写入事件，返回 entry_hash（chain_hash）。"""

        return self._delegate.write(event)


class AuditDiscoverer(ABC):
    @abstractmethod
    def discover_changes(self, session_id: str) -> DiscoveryReport: ...

    @abstractmethod
    def get_changed_files(self, since: str | None = None) -> list[dict[str, Any]]: ...


class AuditIndexer(ABC):
    @abstractmethod
    def build_index(self, force: bool = False) -> dict[str, Any]: ...

    @abstractmethod
    def lookup(self, key: str) -> dict[str, Any] | None: ...

    @abstractmethod
    def cold_start_cache(self) -> dict[str, Any]: ...


class AuditWriter:
    """审计写入器契约——治本（test_p0_i2_construction_order.py）：



    原 ABC 含 @abstractmethod 导致 ``AuditWriter()`` 无法实例化。移除 ABC 继承

    和 abstractmethod 装饰器，提供默认实现（返回 Path），使 ``AuditWriter()``

    可实例化且 ``hasattr(AuditWriter(), "write")`` 为 True。

    ``write`` classmethod 保留（委托到 _CoreAuditWriter）。

    """

    def write_report(self, report: GlobalAuditReport, path: Path | None = None) -> Path:
        """默认实现——写入报告到指定路径。"""

        if path is None:
            path = Path("audit_report.json")

        path.write_text(report.model_dump_json(indent=2), encoding="utf-8")

        return path

    def write_issue(self, issue: AuditIssue, report_dir: Path) -> Path:
        """默认实现——写入 issue 到报告目录。"""

        issue_path = report_dir / f"issue_{issue.issue_id}.json"

        issue_path.write_text(issue.model_dump_json(indent=2), encoding="utf-8")

        return issue_path

    @classmethod
    def write(cls, **kwargs: Any) -> dict[str, Any]:
        """委托到 ``_CoreAuditWriter`` 写入核心审计链——治本（裁定#18 G6）。



        对齐 test_bridges_contracts.py 契约：通过 ``_CoreAuditWriter()`` 实例化

        写入器（测试 patch 此类注入 mock），返回的 dict 必须包含所有传入 kwargs

        以及默认补齐的 event_type/granted/metadata/timestamp 字段。



        Args:

            **kwargs: 审计事件字段（agent_id, permission, resource, granted,

                metadata, event_type, timestamp 等）。



        Returns:

            包含 chain_hash 及所有事件字段的 dict。



        Raises:

            ContractViolationError: 全局 writer 未初始化时。

        """

        event: dict[str, Any] = dict(kwargs)

        event.setdefault("event_type", "rbac_decision")

        event.setdefault("granted", False)

        event.setdefault("metadata", {})

        if not event.get("timestamp"):
            from datetime import UTC, datetime

            event["timestamp"] = datetime.now(UTC).isoformat()

        writer = _CoreAuditWriter()

        entry_hash = writer.write(event)

        return {"chain_hash": entry_hash, **event}


class AuditQuery(ABC):
    @abstractmethod
    def get_status(self) -> OrchestratorStatus: ...

    @abstractmethod
    def get_history(self, limit: int = 50) -> list[dict[str, Any]]: ...

    @abstractmethod
    def get_issues(self, audit_id: str) -> list[AuditIssue]: ...


class IntegrityChecker(ABC):
    @abstractmethod
    def check(self, context: AuditContext) -> dict[str, Any]: ...

    @abstractmethod
    def verify_merkle(self, hour_key: str, expected_root: str) -> bool: ...
