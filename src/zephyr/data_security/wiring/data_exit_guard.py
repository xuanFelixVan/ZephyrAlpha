# [BLUEPRINT] MOD-DATSEC-003 | docs/03_modules/_domain_data_security/data_masking_engine/blueprint.md | §F128 接点②
# [MODULE] zephyr.data_security.wiring.data_exit_guard
# [DOMAIN] D_DATA_SEC
# [DEPENDENCIES] zephyr.data_security.data_masking_engine；zephyr.data_security.data_access_auditor；zephyr.data_security.wiring.audit_sink；yaml
# [CONSUMERS] zephyr.frontend.dashboard.api_server（/api/position 出口挂载——数据出口统一护栏）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 规则册词表闭合(none|full|partial|hash|fpe)；allowlist 语义（未注册字段原样放行，
#   只动规则册点名的字段）；未知角色 Fail-Closed；kind=none 恒等放行且值类型不变（出厂
#   dashboard_local=零行为变更）；FPE 可逆件还原凭 fpe_reveal_roles 白名单（白名单真源=规则册
#   YAML），非白名单角色 Fail-Closed；每次出口一条 AccessEvent（source=PARQUET 文件桥通道，
#   SourceType 词表闭合无 FILE 项）经
#   DataAccessAuditor 采集（敏感表追踪+三维异常检测）；同输入必同输出（随机源无关 kinds）
# [MODIFY-GUARD] docs/03_modules/_domain_data_security/data_masking_engine/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 未知角色/未知 kind/白名单外还原抛 DataMaskingError|DataAccessAuditError
#   （Fail-Closed 透传 MOD-DATSEC-003/002 契约）；规则册缺文件抛 FileNotFoundError（装配期）
# [TESTS] tests/data_security/test_wiring_data_exit_guard.py
# [A_module] module_id=MOD-DATSEC-006 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
DataExitGuard — 数据出口脱敏+访问审计护栏（MOD-DATSEC-006，F128 接点②）。

F128 接线复活（st-menu-t1b2-20260930，Owner 2026-09-30 夜批 known-gap→接线复活）。
挖矿卡 docs/_working/night_sweep/b_audit/nb1_b2_f128_data_security_wiring.md
接点②：dashboard/导出面响应序列化层挂 DataMaskingEngine.mask_field——字段清单来自
规则册 YAML（``config/data_masking_policy.yaml``：role→field→kind），此册同时是
缺口①（脱敏规则册真源）落位；出口事件经 DataAccessAuditor 统一采集（缺口②落盘
真源=audit.jsonl_sink），敏感表追踪+三维异常检测激活（F128 缺口③效果尺的事件面）。

订阅纪律（本夜施工约束"只订阅不改写方行为"）：护栏挂响应出口边界，不改数据生产
逻辑；出厂角色 dashboard_local 字段 kind 全 none=恒等放行（零行为变更），翻转到
dashboard_external（脱敏生效）=Owner 配置门位（宪法 §5）。

# [ALGO_FLOW] external: docs/03_modules/_domain_data_security/algo_flow/wiring__init__.yaml
"""

from __future__ import annotations

import dataclasses
import datetime
import itertools
import logging
from pathlib import Path
from typing import Any, Callable, Final, Mapping

import yaml

from zephyr.data_security.data_access_auditor import (
    AccessAction,
    AccessEvent,
    DataAccessAuditError,
    DataAccessAuditor,
    SourceType,
)
from zephyr.data_security.data_masking_engine import DataMaskingEngine, DataMaskingError, MaskKind
from zephyr.data_security.wiring.audit_sink import DEFAULT_SINK_RELPATH, JsonlAuditSink

_log = logging.getLogger(__name__)

__all__: Final = ["DataExitGuard", "ExitPolicy", "MASK_KIND_VOCABULARY", "RULEBOOK_RELPATH"]

#: 规则册 kind 词表（闭合）
MASK_KIND_VOCABULARY: Final = frozenset({"none", "full", "partial", "hash", "fpe"})

#: 规则册出厂相对路径（真源声明处）
RULEBOOK_RELPATH: Final = "config/data_masking_policy.yaml"

#: FPE 可逆件出厂还原白名单（规则册缺省时的兜底——仅数据属主角色）
_DEFAULT_FPE_REVEAL_ROLES: Final = ("data_owner",)


def load_rulebook(path: str | Path | None = None) -> dict[str, Any]:
    """读规则册 YAML（相对路径锚 REPO_ROOT；缺文件 Fail-Closed 抛 FileNotFoundError）。"""
    p = Path(path) if path is not None else Path(RULEBOOK_RELPATH)
    if not p.is_absolute():
        from zephyr.shared.io.paths import REPO_ROOT  # noqa: PLC0415 延迟 import 避免环

        p = REPO_ROOT / p
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise DataMaskingError(f"规则册根必须是映射: {p}")
    return data


def _normalize_rules(rules: Mapping[str, Mapping[str, str]]) -> dict[str, dict[str, str]]:
    """规则规范化+词表校验（Fail-Closed；与 __init__ 解耦防复杂度超标）。"""
    if not rules:
        raise DataMaskingError("rules 为空（无角色字段策略声明）")
    normalized: dict[str, dict[str, str]] = {}
    for role, fields in rules.items():
        if not role:
            raise DataMaskingError("角色名为空")
        row: dict[str, str] = {}
        for field, kind in (fields or {}).items():
            kind_str = str(getattr(kind, "value", kind)).lower()
            if kind_str not in MASK_KIND_VOCABULARY:
                raise DataMaskingError(f"未知 kind: {field}={kind_str!r}（词表闭合 {sorted(MASK_KIND_VOCABULARY)}）")
            row[field] = kind_str
        normalized[role] = row
    return normalized


def _sync_engine_policies(engine: DataMaskingEngine, normalized: Mapping[str, Mapping[str, str]]) -> None:
    """规则册→引擎策略表同步（fpe 不入引擎动态脱敏表——可逆件由护栏 fpe_encrypt 直通）。"""
    for role, fields in normalized.items():
        for field, kind in fields.items():
            if kind != "fpe":
                engine.register_policy(role, field, MaskKind(kind))


@dataclasses.dataclass(frozen=True)
class ExitPolicy:
    """出口策略捆绑（default_role/fpe_reveal_roles/sensitive_tables——参数对象防长参数表）。"""

    default_role: str = "dashboard_local"
    fpe_reveal_roles: tuple[str, ...] = _DEFAULT_FPE_REVEAL_ROLES
    sensitive_tables: Mapping[str, str] | None = None

    def __post_init__(self) -> None:
        if not self.default_role:
            raise DataMaskingError("default_role 为空")
        if not self.fpe_reveal_roles:
            raise DataMaskingError("fpe_reveal_roles 为空（至少保留数据属主还原通道）")


class DataExitGuard:
    """数据出口护栏（角色字段脱敏 + DataAccessAuditor 出口事件采集 + FPE 白名单还原）。"""

    def __init__(
        self,
        *,
        rules: Mapping[str, Mapping[str, str]],
        engine: DataMaskingEngine | None = None,
        auditor: DataAccessAuditor | None = None,
        audit_sink: Callable[[object], None] | None = None,
        policy: ExitPolicy | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        normalized = _normalize_rules(rules)
        pol = policy or ExitPolicy()
        if pol.default_role not in normalized:
            raise DataMaskingError(f"未知缺省角色: {pol.default_role!r}")
        self._rules = normalized
        self._policy = pol
        self._engine = engine or DataMaskingEngine()
        _sync_engine_policies(self._engine, normalized)
        self._clock = clock or datetime.datetime.now
        self._event_seq = itertools.count(1)
        self._audit_sink = audit_sink if audit_sink is not None else JsonlAuditSink(DEFAULT_SINK_RELPATH)
        self._auditor = auditor or DataAccessAuditor(
            audit_sink=self._audit_sink,
            alert_sink=self._audit_sink,
            sensitive_tables=dict(pol.sensitive_tables or {}),
        )

    # ── 装配 ─────────────────────────────────────────────────────────────

    @classmethod
    def from_rulebook(
        cls,
        path: str | Path | None = None,
        *,
        audit_sink: Callable[[object], None] | None = None,
        engine: DataMaskingEngine | None = None,
        auditor: DataAccessAuditor | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> DataExitGuard:
        """从规则册 YAML 装配（roles/default_role/fpe_reveal_roles/sensitive_tables 四段）。"""
        book = load_rulebook(path)
        exit_cfg = book.get("data_exit") or {}
        roles = exit_cfg.get("roles")
        if not isinstance(roles, dict) or not roles:
            raise DataMaskingError(f"规则册缺 data_exit.roles 映射: {path or RULEBOOK_RELPATH}")
        # 角色配置形态：{role: {description: str, fields: {field: kind}}}——只取 fields 为规则
        rules: dict[str, Mapping[str, str]] = {}
        for role_name, role_cfg in roles.items():
            if isinstance(role_cfg, dict) and "fields" in role_cfg:
                rules[str(role_name)] = role_cfg.get("fields") or {}
            else:
                rules[str(role_name)] = role_cfg or {}
        pol = ExitPolicy(
            default_role=str(exit_cfg.get("default_role", "dashboard_local")),
            fpe_reveal_roles=tuple(exit_cfg.get("fpe_reveal_roles") or _DEFAULT_FPE_REVEAL_ROLES),
            sensitive_tables=exit_cfg.get("sensitive_tables") or None,
        )
        return cls(rules=rules, engine=engine, auditor=auditor, audit_sink=audit_sink, policy=pol, clock=clock)

    # ── 脱敏 ─────────────────────────────────────────────────────────────

    def mask_value(self, role: str, field: str, value: object) -> object:
        """单字段按角色策略脱敏（kind=none 恒等放行且类型不变；fpe 走可逆加密；其余过引擎）。"""
        row = self._rules.get(role)
        if row is None:
            raise DataMaskingError(f"未知角色: {role!r}（未在规则册注册）")
        kind = row.get(field)
        if kind is None or kind == "none":
            return value
        text = value if isinstance(value, str) else str(value)
        if kind == "fpe":
            return self._engine.fpe_encrypt(text)
        return self._engine.mask_field(role, field, text)

    def mask_payload(self, payload: object, *, role: str | None = None) -> object:
        """递归脱敏：dict 按键查规则（allowlist——未注册字段原样放行），list 逐项，标量透传。"""
        r = role or self._policy.default_role
        if r not in self._rules:
            raise DataMaskingError(f"未知角色: {r!r}（未在规则册注册）")
        if isinstance(payload, dict):
            return {
                k: (self.mask_value(r, str(k), v) if str(k) in self._rules.get(r, {}) else self.mask_payload(v, role=r))
                for k, v in payload.items()
            }
        if isinstance(payload, list):
            return [self.mask_payload(v, role=r) for v in payload]
        return payload

    # ── 出口采集 ─────────────────────────────────────────────────────────

    def guard_exit(
        self,
        endpoint: str,
        payload: object,
        *,
        row_count: int = 0,
        role: str | None = None,
        table_name: str | None = None,
    ) -> object:
        """出口边界：脱敏 → AccessEvent 采集（EXPORT/FILE 通道）→ 返回脱敏产物。"""
        r = role or self._policy.default_role
        masked = self.mask_payload(payload, role=r)
        table = table_name or f"qmt_bridge:{endpoint}"
        event = AccessEvent(
            event_id=f"datsec-{int(self._clock().timestamp() * 1000):d}-{next(self._event_seq):04d}",
            subject=f"dashboard:{endpoint}",
            action=AccessAction.EXPORT,
            source=SourceType.PARQUET,  # 文件桥通道：SourceType 词表闭合（clickhouse/sqlite/parquet）无 FILE 项，取文件语义 PARQUET
            table_name=table,
            row_count=max(int(row_count), 0),
            occurred_at=self._clock(),
        )
        try:
            self._auditor.record(event)
        except DataAccessAuditError:
            _log.exception("出口事件采集被拒（Fail-Closed 记日志，脱敏产物照常返回）: %s", event.event_id)
        return masked

    # ── FPE 可逆件还原（白名单通道） ─────────────────────────────────────

    def reveal_payload(self, payload: object, *, role: str, table_name: str | None = None) -> object:
        """FPE 密文还原（仅 fpe_reveal_roles 白名单角色；非白名单 Fail-Closed）。

        递归把 fpe 字段的密文 fpe_decrypt 回原值；还原动作本身记一条 QUERY 事件
        （敏感表追踪面）。full/partial/hash 为不可逆脱敏，不参与还原。
        """
        if role not in self._policy.fpe_reveal_roles:
            raise DataAccessAuditError(f"FPE 还原白名单外角色: {role!r}（真源=规则册 data_exit.fpe_reveal_roles）")
        fpe_fields = {f for f, k in self._rules.get(role, {}).items() if k == "fpe"}
        if not fpe_fields:
            fpe_fields = {f for row in self._rules.values() for f, k in row.items() if k == "fpe"}

        def _reveal(node: object) -> object:
            if isinstance(node, dict):
                return {
                    k: (self._engine.fpe_decrypt(str(v)) if str(k) in fpe_fields and isinstance(v, str) else _reveal(v))
                    for k, v in node.items()
                }
            if isinstance(node, list):
                return [_reveal(v) for v in node]
            return node

        revealed = _reveal(payload)
        event = AccessEvent(
            event_id=f"datsec-{int(self._clock().timestamp() * 1000):d}-{next(self._event_seq):04d}",
            subject=f"reveal:{role}",
            action=AccessAction.QUERY,
            source=SourceType.PARQUET,  # 文件桥通道：SourceType 词表闭合（clickhouse/sqlite/parquet）无 FILE 项，取文件语义 PARQUET
            table_name=table_name or "fpe_reveal",
            row_count=0,
            occurred_at=self._clock(),
        )
        try:
            self._auditor.record(event)
        except DataAccessAuditError:
            _log.exception("还原事件采集被拒: %s", event.event_id)
        return revealed

    # ── 查询面 ───────────────────────────────────────────────────────────

    @property
    def default_role(self) -> str:
        return self._policy.default_role

    def fields_of(self, role: str) -> tuple[str, ...]:
        """角色字段清单（确定性排序；未知角色 Fail-Closed）。"""
        row = self._rules.get(role)
        if row is None:
            raise DataMaskingError(f"未知角色: {role!r}")
        return tuple(sorted(row))

    def sensitive_events(self, table_name: str | None = None) -> list[AccessEvent]:
        """敏感表出口事件追踪（透传 DataAccessAuditor）。"""
        return self._auditor.sensitive_events(table_name=table_name)
