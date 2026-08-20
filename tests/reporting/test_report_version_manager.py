# [BLUEPRINT] MOD-RPT-013 | docs/03_modules/_domain_reporting/report_version_manager/blueprint.md
# [MODULE] tests.reporting.test_report_version_manager
# [DOMAIN] D_REPORTING
# [INVARIANTS] 版本号per report_id单调递增; 哈希链prev_hash(v_n)=record_hash(v_{n-1}); append-only禁止修改; content须dict; frozen不可变
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidVersionInputError(ZA-RPT-0002)
# [TESTS] self
# [A_module] module_id=MOD-RPT-013 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-RPT-013 Report Version Manager 单元测试.

覆盖（blueprint §9）:
  - 版本存储: store() 自动版本号递增 + 哈希链链接
  - 哈希链完整性: content_hash/record_hash/prev_hash 计算正确
  - 差异引擎: additions/deletions/modifications 键级 diff
  - 快照管理: get_version/get_latest/list_versions/list_reports
  - append-only 不可变: ReportVersion/VersionDiff frozen
  - 篡改检测: verify_chain 检测内容篡改/版本号跳号/prev_hash断裂/record_hash伪造
  - 多报告隔离: 不同 report_id 互不干扰
  - 线程安全: 并发 store 无丢失
  - 边界值: 空报告/空内容/content非dict/版本不存在/同版本diff
"""

from __future__ import annotations

import dataclasses
import threading
from datetime import UTC, datetime
from typing import Any

import pytest

from zephyr.reporting.report_version_manager import (
    InvalidVersionInputError,
    ReportVersion,
    ReportVersionManager,
    VersionDiff,
    _compute_content_hash,
    _compute_record_hash,
)

# ── 版本存储测试 ──


class TestStore:
    def test_first_version_number_is_one(self) -> None:
        """首版本号=1, prev_hash=""。"""
        mgr = ReportVersionManager()
        v = mgr.store("daily_pnl", {"total": 100})
        assert v.report_id == "daily_pnl"
        assert v.version_number == 1
        assert v.prev_hash == ""
        assert v.version_id  # UUID 非空
        assert v.schema_version == "1.0"

    def test_version_number_monotonic_increment(self) -> None:
        """版本号 per report_id 单调递增。"""
        mgr = ReportVersionManager()
        v1 = mgr.store("rpt", {"v": 1})
        v2 = mgr.store("rpt", {"v": 2})
        v3 = mgr.store("rpt", {"v": 3})
        assert v1.version_number == 1
        assert v2.version_number == 2
        assert v3.version_number == 3

    def test_prev_hash_links_to_previous_record_hash(self) -> None:
        """prev_hash(v_n) = record_hash(v_{n-1})。"""
        mgr = ReportVersionManager()
        v1 = mgr.store("rpt", {"a": 1})
        v2 = mgr.store("rpt", {"a": 2})
        v3 = mgr.store("rpt", {"a": 3})
        assert v1.prev_hash == ""
        assert v2.prev_hash == v1.record_hash
        assert v3.prev_hash == v2.record_hash

    def test_content_hash_computed_correctly(self) -> None:
        """content_hash = SHA-256(canonical_json(content))。"""
        mgr = ReportVersionManager()
        content = {"b": 2, "a": 1, "c": [1, 2, 3]}
        v = mgr.store("rpt", content)
        assert v.content_hash == _compute_content_hash(content)

    def test_record_hash_computed_correctly(self) -> None:
        """record_hash 含版本号/时间戳/content_hash/prev_hash。"""
        mgr = ReportVersionManager()
        v = mgr.store("rpt", {"x": 1})
        expected = _compute_record_hash(
            v.version_id,
            v.timestamp,
            v.report_id,
            v.version_number,
            v.content_hash,
            v.prev_hash,
        )
        assert v.record_hash == expected

    def test_content_defensive_copy(self) -> None:
        """store 后修改外部 dict 不影响已存储版本。"""
        mgr = ReportVersionManager()
        content = {"total": 100}
        v = mgr.store("rpt", content)
        content["total"] = 999  # 外部修改
        assert v.content["total"] == 100

    def test_reject_non_dict_content(self) -> None:
        """content 非 dict 拒绝。"""
        mgr = ReportVersionManager()
        with pytest.raises(InvalidVersionInputError) as exc_info:
            mgr.store("rpt", [1, 2, 3])  # type: ignore[arg-type]
        assert exc_info.value.error_code == "ZA-RPT-0002"
        assert "dict" in exc_info.value.message

    def test_reject_string_content(self) -> None:
        """content 为字符串拒绝。"""
        mgr = ReportVersionManager()
        with pytest.raises(InvalidVersionInputError):
            mgr.store("rpt", "not a dict")  # type: ignore[arg-type]

    def test_empty_dict_content_allowed(self) -> None:
        """空 dict content 允许。"""
        mgr = ReportVersionManager()
        v = mgr.store("rpt", {})
        assert v.content == {}
        assert v.content_hash  # 仍有哈希

    def test_nested_dict_content(self) -> None:
        """嵌套 dict content 支持。"""
        mgr = ReportVersionManager()
        content = {"metrics": {"sharpe": 1.5, "max_dd": -0.1}, "trades": 10}
        v = mgr.store("rpt", content)
        assert v.content == content
        assert v.content_hash == _compute_content_hash(content)


# ── 快照管理测试 ──


class TestSnapshotManagement:
    def test_get_version_returns_specific_version(self) -> None:
        """get_version 返回指定版本。"""
        mgr = ReportVersionManager()
        v1 = mgr.store("rpt", {"v": 1})
        mgr.store("rpt", {"v": 2})
        result = mgr.get_version("rpt", 1)
        assert result is not None
        assert result.version_id == v1.version_id

    def test_get_version_nonexistent_returns_none(self) -> None:
        """版本不存在返回 None。"""
        mgr = ReportVersionManager()
        mgr.store("rpt", {"v": 1})
        assert mgr.get_version("rpt", 99) is None

    def test_get_version_nonexistent_report_returns_none(self) -> None:
        """report_id 不存在返回 None。"""
        mgr = ReportVersionManager()
        assert mgr.get_version("no_such", 1) is None

    def test_get_latest(self) -> None:
        """get_latest 返回最新版本。"""
        mgr = ReportVersionManager()
        mgr.store("rpt", {"v": 1})
        mgr.store("rpt", {"v": 2})
        v3 = mgr.store("rpt", {"v": 3})
        latest = mgr.get_latest("rpt")
        assert latest is not None
        assert latest.version_number == 3
        assert latest.version_id == v3.version_id

    def test_get_latest_empty_returns_none(self) -> None:
        """无版本时 get_latest 返回 None。"""
        mgr = ReportVersionManager()
        assert mgr.get_latest("rpt") is None

    def test_list_versions_ascending(self) -> None:
        """list_versions 按版本号升序。"""
        mgr = ReportVersionManager()
        mgr.store("rpt", {"v": 1})
        mgr.store("rpt", {"v": 2})
        mgr.store("rpt", {"v": 3})
        versions = mgr.list_versions("rpt")
        assert len(versions) == 3
        assert [v.version_number for v in versions] == [1, 2, 3]

    def test_list_versions_empty(self) -> None:
        """无版本时 list_versions 返回空列表。"""
        mgr = ReportVersionManager()
        assert mgr.list_versions("rpt") == []

    def test_list_versions_returns_copy(self) -> None:
        """list_versions 返回副本, 修改不影响内部存储。"""
        mgr = ReportVersionManager()
        mgr.store("rpt", {"v": 1})
        versions = mgr.list_versions("rpt")
        versions.clear()
        assert len(mgr.list_versions("rpt")) == 1

    def test_list_reports(self) -> None:
        """list_reports 列出所有 report_id。"""
        mgr = ReportVersionManager()
        mgr.store("rpt_a", {"v": 1})
        mgr.store("rpt_b", {"v": 1})
        mgr.store("rpt_c", {"v": 1})
        reports = mgr.list_reports()
        assert set(reports) == {"rpt_a", "rpt_b", "rpt_c"}

    def test_list_reports_empty(self) -> None:
        """无报告时 list_reports 返回空列表。"""
        mgr = ReportVersionManager()
        assert mgr.list_reports() == []


# ── 差异引擎测试 ──


class TestDiff:
    def test_diff_additions(self) -> None:
        """新增键 → additions。"""
        mgr = ReportVersionManager()
        mgr.store("rpt", {"a": 1})
        mgr.store("rpt", {"a": 1, "b": 2})
        d = mgr.diff("rpt", 1, 2)
        assert d.from_version == 1
        assert d.to_version == 2
        assert d.additions == {"b": 2}
        assert d.deletions == {}
        assert d.modifications == {}
        assert d.has_changes is True

    def test_diff_deletions(self) -> None:
        """删除键 → deletions。"""
        mgr = ReportVersionManager()
        mgr.store("rpt", {"a": 1, "b": 2})
        mgr.store("rpt", {"a": 1})
        d = mgr.diff("rpt", 1, 2)
        assert d.deletions == {"b": 2}
        assert d.additions == {}
        assert d.modifications == {}

    def test_diff_modifications(self) -> None:
        """修改值 → modifications。"""
        mgr = ReportVersionManager()
        mgr.store("rpt", {"a": 1})
        mgr.store("rpt", {"a": 2})
        d = mgr.diff("rpt", 1, 2)
        assert d.modifications == {"a": (1, 2)}
        assert d.additions == {}
        assert d.deletions == {}

    def test_diff_mixed_changes(self) -> None:
        """混合变更: 增+删+改。"""
        mgr = ReportVersionManager()
        mgr.store("rpt", {"a": 1, "b": 2, "c": 3})
        mgr.store("rpt", {"a": 1, "b": 99, "d": 4})
        d = mgr.diff("rpt", 1, 2)
        assert d.additions == {"d": 4}
        assert d.deletions == {"c": 3}
        assert d.modifications == {"b": (2, 99)}

    def test_diff_no_changes_same_content(self) -> None:
        """内容相同 → 无差异。"""
        mgr = ReportVersionManager()
        mgr.store("rpt", {"a": 1})
        mgr.store("rpt", {"a": 1})
        d = mgr.diff("rpt", 1, 2)
        assert d.has_changes is False
        assert d.additions == {}
        assert d.deletions == {}
        assert d.modifications == {}

    def test_diff_same_version(self) -> None:
        """同版本 diff → 无差异。"""
        mgr = ReportVersionManager()
        mgr.store("rpt", {"a": 1})
        d = mgr.diff("rpt", 1, 1)
        assert d.has_changes is False

    def test_diff_reverse_direction(self) -> None:
        """反向 diff: from > to 仍正确。"""
        mgr = ReportVersionManager()
        mgr.store("rpt", {"a": 1})
        mgr.store("rpt", {"a": 2})
        d = mgr.diff("rpt", 2, 1)
        # v2→v1: a 从 2 变 1
        assert d.modifications == {"a": (2, 1)}
        assert d.from_version == 2
        assert d.to_version == 1

    def test_diff_from_version_not_exist(self) -> None:
        """from_version 不存在 → InvalidVersionInputError。"""
        mgr = ReportVersionManager()
        mgr.store("rpt", {"a": 1})
        with pytest.raises(InvalidVersionInputError) as exc_info:
            mgr.diff("rpt", 99, 1)
        assert exc_info.value.error_code == "ZA-RPT-0002"

    def test_diff_to_version_not_exist(self) -> None:
        """to_version 不存在 → InvalidVersionInputError。"""
        mgr = ReportVersionManager()
        mgr.store("rpt", {"a": 1})
        with pytest.raises(InvalidVersionInputError):
            mgr.diff("rpt", 1, 99)

    def test_diff_report_not_exist(self) -> None:
        """report_id 不存在 → InvalidVersionInputError。"""
        mgr = ReportVersionManager()
        with pytest.raises(InvalidVersionInputError):
            mgr.diff("no_such", 1, 2)


# ── 哈希链完整性验证 ──


class TestVerifyChain:
    def test_verify_chain_empty_report(self) -> None:
        """空报告(无版本)视为完整链。"""
        mgr = ReportVersionManager()
        assert mgr.verify_chain("rpt") is True

    def test_verify_chain_single_version(self) -> None:
        """单版本链完整。"""
        mgr = ReportVersionManager()
        mgr.store("rpt", {"a": 1})
        assert mgr.verify_chain("rpt") is True

    def test_verify_chain_multiple_versions(self) -> None:
        """多版本链完整。"""
        mgr = ReportVersionManager()
        for i in range(5):
            mgr.store("rpt", {"v": i})
        assert mgr.verify_chain("rpt") is True

    def test_verify_chain_detects_content_tamper(self) -> None:
        """篡改版本内容 → verify_chain 返回 False。"""
        mgr = ReportVersionManager()
        mgr.store("rpt", {"a": 1})
        mgr.store("rpt", {"a": 2})
        # 篡改：绕过 frozen 替换内部存储的 content
        mgr._store["rpt"][0] = dataclasses.replace(mgr._store["rpt"][0], content={"a": 999})
        assert mgr.verify_chain("rpt") is False

    def test_verify_chain_detects_record_hash_tamper(self) -> None:
        """伪造 record_hash → verify_chain 返回 False。"""
        mgr = ReportVersionManager()
        mgr.store("rpt", {"a": 1})
        mgr.store("rpt", {"a": 2})
        # 篡改 record_hash（但保持 content_hash 不变 → record_hash 重算不匹配）
        mgr._store["rpt"][1] = dataclasses.replace(mgr._store["rpt"][1], record_hash="fake_hash_value")
        assert mgr.verify_chain("rpt") is False

    def test_verify_chain_detects_prev_hash_break(self) -> None:
        """prev_hash 断裂 → verify_chain 返回 False。"""
        mgr = ReportVersionManager()
        mgr.store("rpt", {"a": 1})
        mgr.store("rpt", {"a": 2})
        # 篡改 v2 的 prev_hash（不再指向 v1.record_hash）
        mgr._store["rpt"][1] = dataclasses.replace(mgr._store["rpt"][1], prev_hash="wrong_prev_hash")
        assert mgr.verify_chain("rpt") is False

    def test_verify_chain_detects_version_number_gap(self) -> None:
        """版本号跳号 → verify_chain 返回 False。"""
        mgr = ReportVersionManager()
        mgr.store("rpt", {"a": 1})
        mgr.store("rpt", {"a": 2})
        # 篡改 v2 的 version_number 为 5（跳号）
        mgr._store["rpt"][1] = dataclasses.replace(mgr._store["rpt"][1], version_number=5)
        assert mgr.verify_chain("rpt") is False


# ── append-only 不可变测试 ──


class TestImmutability:
    def test_report_version_frozen(self) -> None:
        """ReportVersion frozen=True, 不可修改字段。"""
        mgr = ReportVersionManager()
        v = mgr.store("rpt", {"a": 1})
        with pytest.raises(dataclasses.FrozenInstanceError):
            v.version_number = 999  # type: ignore[misc]

    def test_report_version_content_cannot_be_reassigned(self) -> None:
        """ReportVersion.content 不可重新赋值。"""
        mgr = ReportVersionManager()
        v = mgr.store("rpt", {"a": 1})
        with pytest.raises(dataclasses.FrozenInstanceError):
            v.content = {"b": 2}  # type: ignore[misc]

    def test_version_diff_frozen(self) -> None:
        """VersionDiff frozen=True, 不可修改字段。"""
        mgr = ReportVersionManager()
        mgr.store("rpt", {"a": 1})
        mgr.store("rpt", {"a": 2})
        d = mgr.diff("rpt", 1, 2)
        with pytest.raises(dataclasses.FrozenInstanceError):
            d.from_version = 999  # type: ignore[misc]

    def test_version_diff_default_empty(self) -> None:
        """VersionDiff 默认 additions/deletions/modifications 为空 dict。"""
        d = VersionDiff(from_version=1, to_version=2)
        assert d.additions == {}
        assert d.deletions == {}
        assert d.modifications == {}
        assert d.has_changes is False


# ── 多报告隔离测试 ──


class TestMultiReportIsolation:
    def test_independent_version_numbers(self) -> None:
        """不同 report_id 版本号独立计数。"""
        mgr = ReportVersionManager()
        mgr.store("rpt_a", {"v": 1})
        mgr.store("rpt_b", {"v": 1})
        mgr.store("rpt_b", {"v": 2})
        mgr.store("rpt_a", {"v": 2})
        assert mgr.get_latest("rpt_a").version_number == 2  # type: ignore[union-attr]
        assert mgr.get_latest("rpt_b").version_number == 2  # type: ignore[union-attr]

    def test_independent_hash_chains(self) -> None:
        """不同 report_id 哈希链独立。"""
        mgr = ReportVersionManager()
        a1 = mgr.store("rpt_a", {"v": 1})
        b1 = mgr.store("rpt_b", {"v": 1})
        a2 = mgr.store("rpt_a", {"v": 2})
        b2 = mgr.store("rpt_b", {"v": 2})
        # rpt_a 链: a1←a2
        assert a2.prev_hash == a1.record_hash
        # rpt_b 链: b1←b2
        assert b2.prev_hash == b1.record_hash
        # 两链不交叉
        assert a2.prev_hash != b2.prev_hash

    def test_list_reports_isolated(self) -> None:
        """list_reports 仅返回有版本的 report_id。"""
        mgr = ReportVersionManager()
        mgr.store("rpt_a", {"v": 1})
        # rpt_b 仅查询未存储
        assert mgr.get_latest("rpt_b") is None
        assert set(mgr.list_reports()) == {"rpt_a"}

    def test_diff_isolated_per_report(self) -> None:
        """diff 仅在指定 report_id 范围内计算。"""
        mgr = ReportVersionManager()
        mgr.store("rpt_a", {"a": 1})
        mgr.store("rpt_a", {"a": 2})
        mgr.store("rpt_b", {"b": 1})
        # rpt_a 的 diff 不受 rpt_b 影响
        d = mgr.diff("rpt_a", 1, 2)
        assert d.modifications == {"a": (1, 2)}


# ── 线程安全测试 ──


class TestThreadSafety:
    def test_concurrent_store_no_loss(self) -> None:
        """并发 store: 无版本丢失, 版本号唯一。"""
        mgr = ReportVersionManager()
        n_threads = 8
        n_per_thread = 25
        barrier = threading.Barrier(n_threads)

        def worker(tid: int) -> None:
            barrier.wait()
            for i in range(n_per_thread):
                mgr.store("rpt", {"thread": tid, "i": i})

        threads = [threading.Thread(target=worker, args=(t,)) for t in range(n_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        versions = mgr.list_versions("rpt")
        assert len(versions) == n_threads * n_per_thread
        # 版本号 1..N 唯一无重复
        numbers = [v.version_number for v in versions]
        assert sorted(numbers) == list(range(1, n_threads * n_per_thread + 1))
        assert len(set(numbers)) == len(numbers)  # 无重复

    def test_concurrent_store_verify_chain(self) -> None:
        """并发 store 后哈希链仍完整。"""
        mgr = ReportVersionManager()
        n_threads = 4
        n_per_thread = 20
        barrier = threading.Barrier(n_threads)

        def worker() -> None:
            barrier.wait()
            for i in range(n_per_thread):
                mgr.store("rpt", {"v": i})

        threads = [threading.Thread(target=worker) for _ in range(n_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert mgr.verify_chain("rpt") is True

    def test_concurrent_multi_report(self) -> None:
        """并发操作多个 report_id 互不干扰。"""
        mgr = ReportVersionManager()
        n_reports = 4
        n_per_report = 10
        barrier = threading.Barrier(n_reports)

        def worker(rid: str) -> None:
            barrier.wait()
            for i in range(n_per_report):
                mgr.store(rid, {"v": i})

        threads = [threading.Thread(target=worker, args=(f"rpt_{r}",)) for r in range(n_reports)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        for r in range(n_reports):
            rid = f"rpt_{r}"
            assert len(mgr.list_versions(rid)) == n_per_report
            assert mgr.verify_chain(rid) is True


# ── 哈希计算工具测试 ──


class TestHashUtils:
    def test_canonical_json_sorted_keys(self) -> None:
        """canonical_json 排序键, 相同内容不同顺序哈希一致。"""
        from zephyr.reporting.report_version_manager import _canonical_json

        c1 = {"b": 2, "a": 1}
        c2 = {"a": 1, "b": 2}
        assert _canonical_json(c1) == _canonical_json(c2)

    def test_content_hash_deterministic(self) -> None:
        """相同内容 content_hash 一致。"""
        mgr = ReportVersionManager()
        v1 = mgr.store("rpt", {"a": 1, "b": [1, 2]})
        v2 = mgr.store("rpt2", {"b": [1, 2], "a": 1})
        assert v1.content_hash == v2.content_hash

    def test_different_content_different_hash(self) -> None:
        """不同内容 content_hash 不同。"""
        v1_hash = _compute_content_hash({"a": 1})
        v2_hash = _compute_content_hash({"a": 2})
        assert v1_hash != v2_hash

    def test_record_hash_includes_all_fields(self) -> None:
        """record_hash 包含所有关键字段, 任一变化则哈希不同。"""
        ts = datetime.now(UTC)
        base = _compute_record_hash("id1", ts, "rpt", 1, "chash", "")
        # version_id 变化
        assert base != _compute_record_hash("id2", ts, "rpt", 1, "chash", "")
        # version_number 变化
        assert base != _compute_record_hash("id1", ts, "rpt", 2, "chash", "")
        # content_hash 变化
        assert base != _compute_record_hash("id1", ts, "rpt", 1, "other", "")
        # prev_hash 变化
        assert base != _compute_record_hash("id1", ts, "rpt", 1, "chash", "prev")
