# [BLUEPRINT] MOD-GOV-054 | docs/03_modules/_domain_governance/api_doc_version_syncer/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-GOV-054 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.governance.docs.test_api_doc_version_syncer
# [TESTS] src/zephyr/governance/docs/api_doc_version_syncer.py
"""MOD-GOV-054 单元测试：api_doc_version_syncer API 文档版本同步器。

蓝图验收（B14-04654/CAND-REGSYNC-002，A9 XS-15）：
API 版本/签名变更扫描（注入 api_scanner）→ 文档与 changelog 更新
（注入 doc_writer，dry-run 先行）→ 差异超阈值人工确认 +
非交易时段判定（注入）。
scanner/writer/时段/确认/时钟全注入内存替身，不触盘不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.governance.docs.api_doc_version_syncer",
    reason="api_doc_version_syncer not importable",
)

from zephyr.governance.docs.api_doc_version_syncer import (  # noqa: E402
    ApiDocSyncError,
    ApiDocVersionSyncer,
    ApiSignature,
    ChangeKind,
    DocTarget,
)

_T0 = datetime.datetime(2026, 8, 26, 20, 30, 0)

_V1 = {
    "risk_api": ApiSignature("risk_api", "1.0.0", "check(pos) -> bool"),
    "quote_api": ApiSignature("quote_api", "2.1.0", "fetch(sym) -> Quote"),
}


def _syncer(
    snapshot=None,
    *,
    baseline=None,
    writer=None,
    trading=False,
    confirmer=None,
    threshold=5,
) -> ApiDocVersionSyncer:
    writes: list = []
    return ApiDocVersionSyncer(
        api_scanner=lambda: list((snapshot if snapshot is not None else _V1).values()),
        doc_writer=writer if writer is not None else writes.append,
        trading_hours=lambda: trading,
        human_confirmer=confirmer,
        diff_threshold=threshold,
        baseline=baseline,
        clock=lambda: _T0,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 构造 / 扫描校验（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestInitAndScan:
    def test_invalid_threshold_raises(self) -> None:
        with pytest.raises(ApiDocSyncError):
            _syncer(threshold=-1)

    def test_empty_changelog_path_raises(self) -> None:
        with pytest.raises(ApiDocSyncError):
            ApiDocVersionSyncer(changelog_path="")

    def test_scanner_not_injected_raises(self) -> None:
        syncer = ApiDocVersionSyncer(trading_hours=lambda: False)
        with pytest.raises(ApiDocSyncError):
            syncer.scan_changes()

    def test_scanner_error_wrapped(self) -> None:
        def _boom():
            raise RuntimeError("index down")

        syncer = ApiDocVersionSyncer(api_scanner=_boom)
        with pytest.raises(ApiDocSyncError):
            syncer.scan_changes()

    def test_invalid_entry_raises(self) -> None:
        syncer = ApiDocVersionSyncer(api_scanner=lambda: ["not-a-signature"])
        with pytest.raises(ApiDocSyncError):
            syncer.scan_changes()
        bad = ApiDocVersionSyncer(api_scanner=lambda: [ApiSignature("risk_api", "", "sig")])
        with pytest.raises(ApiDocSyncError):
            bad.scan_changes()

    def test_duplicate_api_id_raises(self) -> None:
        dup = [ApiSignature("a", "1", "s1"), ApiSignature("a", "2", "s2")]
        syncer = ApiDocVersionSyncer(api_scanner=lambda: dup)
        with pytest.raises(ApiDocSyncError):
            syncer.scan_changes()


# ──────────────────────────────────────────────────────────────────────────────
# diff（版本/签名变更检测）
# ──────────────────────────────────────────────────────────────────────────────


class TestDiff:
    def test_no_baseline_all_added(self) -> None:
        changes = _syncer().scan_changes()
        assert [(c.api_id, c.kind) for c in changes] == [
            ("quote_api", ChangeKind.ADDED),
            ("risk_api", ChangeKind.ADDED),
        ]

    def test_no_change_empty(self) -> None:
        assert _syncer(baseline=_V1).scan_changes() == ()

    def test_modified_on_version_bump(self) -> None:
        baseline = dict(_V1)
        snapshot = dict(_V1)
        snapshot["risk_api"] = ApiSignature("risk_api", "1.1.0", "check(pos) -> bool")
        changes = _syncer(snapshot, baseline=baseline).scan_changes()
        assert len(changes) == 1
        assert changes[0].kind is ChangeKind.MODIFIED
        assert changes[0].old_version == "1.0.0"
        assert changes[0].new_version == "1.1.0"

    def test_modified_on_signature_change_same_version(self) -> None:
        baseline = dict(_V1)
        snapshot = dict(_V1)
        snapshot["risk_api"] = ApiSignature("risk_api", "1.0.0", "check(pos, lev) -> bool")
        changes = _syncer(snapshot, baseline=baseline).scan_changes()
        assert [c.kind for c in changes] == [ChangeKind.MODIFIED]

    def test_removed_detected(self) -> None:
        snapshot = {"risk_api": _V1["risk_api"]}
        changes = _syncer(snapshot, baseline=_V1).scan_changes()
        assert [(c.api_id, c.kind) for c in changes] == [
            ("quote_api", ChangeKind.REMOVED),
        ]


# ──────────────────────────────────────────────────────────────────────────────
# 交易时段门禁
# ──────────────────────────────────────────────────────────────────────────────


class TestTradingHours:
    def test_trading_hours_blocked(self) -> None:
        with pytest.raises(ApiDocSyncError):
            _syncer(trading=True).sync()

    def test_trading_hours_not_injected_raises(self) -> None:
        syncer = ApiDocVersionSyncer(api_scanner=lambda: list(_V1.values()))
        with pytest.raises(ApiDocSyncError):
            syncer.sync()

    def test_trading_hours_error_wrapped(self) -> None:
        def _boom():
            raise RuntimeError("calendar down")

        syncer = ApiDocVersionSyncer(
            api_scanner=lambda: list(_V1.values()),
            trading_hours=_boom,
        )
        with pytest.raises(ApiDocSyncError):
            syncer.sync()


# ──────────────────────────────────────────────────────────────────────────────
# dry-run / 落写
# ──────────────────────────────────────────────────────────────────────────────


class TestSync:
    def test_dry_run_no_write(self) -> None:
        writes: list = []
        result = _syncer(writer=writes.append).sync(dry_run=True)
        assert result.dry_run is True
        assert result.applied is False
        assert writes == []
        paths = [u.path for u in result.updates]
        assert "docs/api/risk_api.md" in paths
        assert "CHANGELOG.md" in paths

    def test_dry_run_default(self) -> None:
        writes: list = []
        _syncer(writer=writes.append).sync()  # 默认 dry_run=True
        assert writes == []

    def test_apply_writes_doc_and_changelog(self) -> None:
        writes: list = []
        result = _syncer(writer=writes.append).sync(dry_run=False)
        assert result.applied is True
        assert len(writes) == 3  # 2 doc + 1 changelog
        changelog = [w for w in writes if w.target is DocTarget.CHANGELOG][0]
        assert "added" in changelog.content
        assert _T0.isoformat() in changelog.content
        doc = [w for w in writes if w.path == "docs/api/risk_api.md"][0]
        assert "version: 1.0.0" in doc.content
        assert "check(pos) -> bool" in doc.content

    def test_baseline_advances_after_apply(self) -> None:
        writes: list = []
        syncer = _syncer(writer=writes.append)
        syncer.sync(dry_run=False)
        assert syncer.scan_changes() == ()  # baseline 已推进

    def test_dry_run_does_not_advance_baseline(self) -> None:
        syncer = _syncer()
        syncer.sync(dry_run=True)
        assert len(syncer.scan_changes()) == 2  # baseline 未动

    def test_writer_not_injected_fail_closed(self) -> None:
        syncer = ApiDocVersionSyncer(
            api_scanner=lambda: list(_V1.values()),
            trading_hours=lambda: False,
        )
        with pytest.raises(ApiDocSyncError):
            syncer.sync(dry_run=False)

    def test_writer_error_wrapped_baseline_kept(self) -> None:
        def _bad_writer(update):
            raise OSError("disk full")

        syncer = _syncer(writer=_bad_writer)
        with pytest.raises(ApiDocSyncError):
            syncer.sync(dry_run=False)
        assert len(syncer.scan_changes()) == 2  # 写入失败 baseline 不推进

    def test_removed_doc_content(self) -> None:
        writes: list = []
        snapshot = {"risk_api": _V1["risk_api"]}
        _syncer(snapshot, baseline=_V1, writer=writes.append).sync(dry_run=False)
        doc = [w for w in writes if w.path == "docs/api/quote_api.md"][0]
        assert "status: removed" in doc.content
        assert "last_version: 2.1.0" in doc.content


# ──────────────────────────────────────────────────────────────────────────────
# 超阈值人工确认
# ──────────────────────────────────────────────────────────────────────────────


class TestHumanConfirm:
    def test_over_threshold_no_confirmer_raises(self) -> None:
        with pytest.raises(ApiDocSyncError):
            _syncer(threshold=1).sync()  # 2 变更 > 1

    def test_over_threshold_confirmed_ok(self) -> None:
        seen: list = []
        result = _syncer(
            threshold=1,
            confirmer=lambda changes: seen.append(len(changes)) or True,
        ).sync()
        assert seen == [2]
        assert len(result.changes) == 2

    def test_over_threshold_rejected_raises(self) -> None:
        with pytest.raises(ApiDocSyncError):
            _syncer(threshold=1, confirmer=lambda changes: False).sync()

    def test_under_threshold_no_confirm_needed(self) -> None:
        result = _syncer(threshold=5).sync()  # 2 ≤ 5，无需确认
        assert len(result.changes) == 2

    def test_determinism_same_input_same_output(self) -> None:
        def _run() -> tuple:
            result = _syncer().sync(dry_run=True)
            return (
                tuple((c.kind, c.api_id, c.old_version, c.new_version) for c in result.changes),
                tuple((u.target, u.path, u.content) for u in result.updates),
            )

        assert _run() == _run()
