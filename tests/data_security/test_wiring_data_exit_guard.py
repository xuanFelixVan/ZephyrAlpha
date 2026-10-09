# [BLUEPRINT] MOD-DATSEC-006 | docs/03_modules/_domain_data_security/data_masking_engine/blueprint.md | wiring 抢救配套测试（车道 2a st-chiefc-20261009）
# [MODULE] tests.data_security.test_wiring_data_exit_guard
# [DEPENDENCIES] zephyr.data_security.wiring；pytest；yaml
# [INVARIANTS] 审计 sink=内存 list，规则册 fixture 落 tmp_path，禁写 data/ 生产路径
# [TTL] permanent
"""DataExitGuard（MOD-DATSEC-006）最小可红行为测试：词表闭合/allowlist/Fail-Closed/规则册装配。"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from zephyr.data_security.data_access_auditor import DataAccessAuditError
from zephyr.data_security.data_masking_engine import DataMaskingError
from zephyr.data_security.wiring import (
    MASK_KIND_VOCABULARY,
    RULEBOOK_RELPATH,
    DataExitGuard,
    load_rulebook,
)


def _guard() -> DataExitGuard:
    records: list = []
    return DataExitGuard(
        rules={
            "dashboard_local": {"user_id": "none", "name": "full"},
            "analyst": {"user_id": "hash"},
        },
        audit_sink=records.append,
    )


def test_rulebook_relpath_declaration() -> None:
    assert RULEBOOK_RELPATH == "config/data_masking_policy.yaml"


def test_kind_vocabulary_closed() -> None:
    assert frozenset({"none", "full", "partial", "hash", "fpe"}) == MASK_KIND_VOCABULARY


def test_unknown_kind_fails_closed() -> None:
    with pytest.raises(DataMaskingError):
        DataExitGuard(rules={"r": {"f": "bogus"}}, audit_sink=(lambda _rec: None))


def test_unknown_role_fails_closed() -> None:
    with pytest.raises(DataMaskingError):
        _guard().mask_value("ghost", "user_id", "x")


def test_none_kind_identity_keeps_value_and_type() -> None:
    """出厂 dashboard_local 零行为变更：kind=none 恒等放行且值类型不变。"""
    value = 12345
    out = _guard().mask_value("dashboard_local", "user_id", value)
    assert out is value


def test_mask_payload_allowlist_semantics() -> None:
    """allowlist：未注册字段原样放行，注册字段被变换（full≠原值）。"""
    payload = {"user_id": "u-1", "name": "张三", "memo": {"free_text": "keep-me"}}
    out = _guard().mask_payload(payload)
    assert out["memo"]["free_text"] == "keep-me"
    assert out["name"] != "张三"


def test_fields_of_sorted_and_unknown_role_raises() -> None:
    guard = _guard()
    assert guard.fields_of("dashboard_local") == ("name", "user_id")
    with pytest.raises(DataMaskingError):
        guard.fields_of("ghost")


def test_guard_exit_returns_masked_and_records_event() -> None:
    records: list = []
    guard = DataExitGuard(
        rules={"dashboard_local": {"user_id": "none"}},
        audit_sink=records.append,
    )
    out = guard.guard_exit("/api/position", {"user_id": "u-1"}, row_count=3)
    assert out == {"user_id": "u-1"}
    assert len(records) >= 1  # AccessEvent 经 DataAccessAuditor 采集落 sink


def test_reveal_non_whitelisted_role_blocked() -> None:
    """FPE 还原白名单外角色 Fail-Closed（默认白名单仅 data_owner）。"""
    with pytest.raises(DataAccessAuditError):
        _guard().reveal_payload({"x": "1"}, role="analyst")


def test_from_rulebook_assembles_roles(tmp_path: Path) -> None:
    book = {
        "data_exit": {
            "default_role": "viewer",
            "fpe_reveal_roles": ["data_owner"],
            "roles": {
                "viewer": {"description": "只读", "fields": {"phone": "full"}},
                "data_owner": {"fields": {}},
            },
        }
    }
    rulebook = tmp_path / "policy.yaml"
    rulebook.write_text(yaml.safe_dump(book, allow_unicode=True), encoding="utf-8")
    guard = DataExitGuard.from_rulebook(rulebook, audit_sink=(lambda _rec: None))
    assert guard.default_role == "viewer"
    assert guard.fields_of("viewer") == ("phone",)


def test_load_rulebook_missing_file_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_rulebook(tmp_path / "nope.yaml")
