# [BLUEPRINT] MOD-RPT-017 | docs/03_modules/_domain_reporting/report_watermark_tracker/blueprint.md
# [MODULE] tests.reporting.test_report_watermark_tracker
# [DOMAIN] D_REPORTING
# [INVARIANTS] ReportWatermark frozen不可变; 哈希链prev_hash(w_n)=record_hash(w_{n-1}); content须dict; signature绑定source+content+timestamp
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidWatermarkInputError(ZA-RPT-0004)
# [TESTS] self
# [A_module] module_id=MOD-RPT-017 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-RPT-017 Report Watermark Tracker 单元测试.

覆盖（blueprint §7）:
  - 水印加盖: 字段正确 / content_hash / signature / 链接
  - 完整性校验: 内容匹配 / 内容篡改检测 / 签名伪造检测
  - 哈希链: 单水印 / 多水印链接 / 篡改检测 / record_hash伪造
  - 来源追溯: 多来源 / list_sources / list_watermarks
  - frozen不可变 / 线程安全 / 边界值
"""

from __future__ import annotations

import dataclasses
import threading

import pytest

from zephyr.reporting.report_watermark_tracker import (
    InvalidWatermarkInputError,
    ReportWatermark,
    WatermarkTracker,
    _compute_content_hash,
    _compute_record_hash,
    _compute_signature,
)

# ── 水印加盖测试 ──


class TestStamp:
    def test_first_watermark_fields(self) -> None:
        """首水印字段正确, prev_watermark_hash=""。"""
        tracker = WatermarkTracker()
        wm = tracker.stamp("rpt_001", {"total": 100}, "PnlCalculator")
        assert wm.report_id == "rpt_001"
        assert wm.source == "PnlCalculator"
        assert wm.prev_watermark_hash == ""
        assert wm.watermark_id  # UUID 非空
        assert wm.schema_version == "1.0"
        assert wm.timestamp is not None

    def test_content_hash_computed(self) -> None:
        """content_hash = SHA-256(canonical_json(content))。"""
        tracker = WatermarkTracker()
        content = {"b": 2, "a": 1}
        wm = tracker.stamp("rpt", content, "Engine")
        assert wm.content_hash == _compute_content_hash(content)

    def test_signature_computed(self) -> None:
        """watermark_signature = SHA-256(source + content_hash + timestamp)。"""
        tracker = WatermarkTracker()
        content = {"x": 1}
        wm = tracker.stamp("rpt", content, "RiskEngine")
        expected = _compute_signature("RiskEngine", wm.content_hash, wm.timestamp)
        assert wm.watermark_signature == expected

    def test_record_hash_computed(self) -> None:
        """record_hash 含所有字段。"""
        tracker = WatermarkTracker()
        wm = tracker.stamp("rpt", {"a": 1}, "Src")
        expected = _compute_record_hash(
            wm.watermark_id, wm.report_id, wm.source, wm.timestamp,
            wm.content_hash, wm.watermark_signature, wm.prev_watermark_hash,
        )
        assert wm.record_hash == expected

    def test_chain_linking_multiple_stamps(self) -> None:
        """多次加盖: prev_watermark_hash 链接前一水印 record_hash。"""
        tracker = WatermarkTracker()
        wm1 = tracker.stamp("rpt", {"v": 1}, "SrcA")
        wm2 = tracker.stamp("rpt", {"v": 2}, "SrcB")
        wm3 = tracker.stamp("rpt", {"v": 3}, "SrcA")
        assert wm1.prev_watermark_hash == ""
        assert wm2.prev_watermark_hash == wm1.record_hash
        assert wm3.prev_watermark_hash == wm2.record_hash

    def test_reject_non_dict_content(self) -> None:
        """content 非 dict 拒绝。"""
        tracker = WatermarkTracker()
        with pytest.raises(InvalidWatermarkInputError) as exc_info:
            tracker.stamp("rpt", [1, 2], "Src")  # type: ignore[arg-type]
        assert exc_info.value.error_code == "ZA-RPT-0004"

    def test_reject_empty_source(self) -> None:
        """source 为空拒绝。"""
        tracker = WatermarkTracker()
        with pytest.raises(InvalidWatermarkInputError):
            tracker.stamp("rpt", {"a": 1}, "")

    def test_reject_whitespace_source(self) -> None:
        """source 纯空白拒绝。"""
        tracker = WatermarkTracker()
        with pytest.raises(InvalidWatermarkInputError):
            tracker.stamp("rpt", {"a": 1}, "   ")

    def test_source_stripped(self) -> None:
        """source 前后空白被去除。"""
        tracker = WatermarkTracker()
        wm = tracker.stamp("rpt", {"a": 1}, "  Engine  ")
        assert wm.source == "Engine"

    def test_empty_dict_content_allowed(self) -> None:
        """空 dict content 允许。"""
        tracker = WatermarkTracker()
        wm = tracker.stamp("rpt", {}, "Src")
        assert wm.content_hash  # 仍有哈希


# ── 水印查询测试 ──


class TestQuery:
    def test_get_watermark_latest(self) -> None:
        """get_watermark 返回最新水印。"""
        tracker = WatermarkTracker()
        tracker.stamp("rpt", {"v": 1}, "SrcA")
        wm2 = tracker.stamp("rpt", {"v": 2}, "SrcB")
        latest = tracker.get_watermark("rpt")
        assert latest is not None
        assert latest.watermark_id == wm2.watermark_id

    def test_get_watermark_none(self) -> None:
        """无水印返回 None。"""
        tracker = WatermarkTracker()
        assert tracker.get_watermark("no_such") is None

    def test_list_watermarks_ascending(self) -> None:
        """list_watermarks 按时间升序。"""
        tracker = WatermarkTracker()
        wm1 = tracker.stamp("rpt", {"v": 1}, "SrcA")
        wm2 = tracker.stamp("rpt", {"v": 2}, "SrcB")
        wm3 = tracker.stamp("rpt", {"v": 3}, "SrcA")
        wms = tracker.list_watermarks("rpt")
        assert len(wms) == 3
        assert wms[0].watermark_id == wm1.watermark_id
        assert wms[2].watermark_id == wm3.watermark_id

    def test_list_watermarks_empty(self) -> None:
        """无水印返回空列表。"""
        tracker = WatermarkTracker()
        assert tracker.list_watermarks("no_such") == []

    def test_list_watermarks_returns_copy(self) -> None:
        """list_watermarks 返回副本。"""
        tracker = WatermarkTracker()
        tracker.stamp("rpt", {"v": 1}, "SrcA")
        wms = tracker.list_watermarks("rpt")
        wms.clear()
        assert len(tracker.list_watermarks("rpt")) == 1

    def test_list_sources(self) -> None:
        """list_sources 去重排序。"""
        tracker = WatermarkTracker()
        tracker.stamp("rpt_a", {"v": 1}, "EngineC")
        tracker.stamp("rpt_a", {"v": 2}, "EngineA")
        tracker.stamp("rpt_b", {"v": 1}, "EngineB")
        tracker.stamp("rpt_b", {"v": 2}, "EngineA")
        sources = tracker.list_sources()
        assert sources == ["EngineA", "EngineB", "EngineC"]

    def test_list_sources_empty(self) -> None:
        """无水印时 list_sources 返回空列表。"""
        tracker = WatermarkTracker()
        assert tracker.list_sources() == []


# ── 完整性校验测试 ──


class TestVerifyWatermark:
    def test_content_matches(self) -> None:
        """内容匹配 → True。"""
        tracker = WatermarkTracker()
        content = {"total": 100, "fee": 5}
        wm = tracker.stamp("rpt", content, "Engine")
        assert tracker.verify_watermark(wm, content) is True

    def test_content_tampered(self) -> None:
        """内容篡改 → False。"""
        tracker = WatermarkTracker()
        wm = tracker.stamp("rpt", {"total": 100}, "Engine")
        assert tracker.verify_watermark(wm, {"total": 999}) is False

    def test_content_key_order_irrelevant(self) -> None:
        """键顺序不影响 content_hash。"""
        tracker = WatermarkTracker()
        wm = tracker.stamp("rpt", {"a": 1, "b": 2}, "Engine")
        assert tracker.verify_watermark(wm, {"b": 2, "a": 1}) is True

    def test_empty_content_match(self) -> None:
        """空 dict 内容匹配。"""
        tracker = WatermarkTracker()
        wm = tracker.stamp("rpt", {}, "Engine")
        assert tracker.verify_watermark(wm, {}) is True

    def test_signature_forgery_detected(self) -> None:
        """签名伪造 → False。"""
        tracker = WatermarkTracker()
        wm = tracker.stamp("rpt", {"a": 1}, "Engine")
        # 伪造签名
        forged = dataclasses.replace(wm, watermark_signature="fake_sig")
        assert tracker.verify_watermark(forged, {"a": 1}) is False


# ── 哈希链验证测试 ──


class TestVerifyChain:
    def test_empty_chain(self) -> None:
        """无水印视为完整链。"""
        tracker = WatermarkTracker()
        assert tracker.verify_chain("rpt") is True

    def test_single_watermark(self) -> None:
        """单水印链完整。"""
        tracker = WatermarkTracker()
        tracker.stamp("rpt", {"a": 1}, "Src")
        assert tracker.verify_chain("rpt") is True

    def test_multiple_watermarks(self) -> None:
        """多水印链完整。"""
        tracker = WatermarkTracker()
        for i in range(5):
            tracker.stamp("rpt", {"v": i}, f"Src{i % 2}")
        assert tracker.verify_chain("rpt") is True

    def test_detect_record_hash_tamper(self) -> None:
        """伪造 record_hash → False。"""
        tracker = WatermarkTracker()
        tracker.stamp("rpt", {"a": 1}, "SrcA")
        tracker.stamp("rpt", {"a": 2}, "SrcB")
        tracker._store["rpt"][1] = dataclasses.replace(
            tracker._store["rpt"][1], record_hash="fake_record_hash"
        )
        assert tracker.verify_chain("rpt") is False

    def test_detect_prev_hash_break(self) -> None:
        """prev_hash 断裂 → False。"""
        tracker = WatermarkTracker()
        tracker.stamp("rpt", {"a": 1}, "SrcA")
        tracker.stamp("rpt", {"a": 2}, "SrcB")
        tracker._store["rpt"][1] = dataclasses.replace(
            tracker._store["rpt"][1], prev_watermark_hash="wrong_prev"
        )
        assert tracker.verify_chain("rpt") is False

    def test_detect_signature_tamper(self) -> None:
        """签名篡改 → False。"""
        tracker = WatermarkTracker()
        tracker.stamp("rpt", {"a": 1}, "SrcA")
        tracker._store["rpt"][0] = dataclasses.replace(
            tracker._store["rpt"][0], watermark_signature="forged_sig"
        )
        assert tracker.verify_chain("rpt") is False

    def test_multi_report_chains_independent(self) -> None:
        """不同 report_id 哈希链独立验证。"""
        tracker = WatermarkTracker()
        tracker.stamp("rpt_a", {"a": 1}, "SrcA")
        tracker.stamp("rpt_a", {"a": 2}, "SrcA")
        tracker.stamp("rpt_b", {"b": 1}, "SrcB")
        assert tracker.verify_chain("rpt_a") is True
        assert tracker.verify_chain("rpt_b") is True
        # 篡改 rpt_a 不影响 rpt_b
        tracker._store["rpt_a"][0] = dataclasses.replace(
            tracker._store["rpt_a"][0], record_hash="tampered"
        )
        assert tracker.verify_chain("rpt_a") is False
        assert tracker.verify_chain("rpt_b") is True


# ── 不可变测试 ──


class TestImmutability:
    def test_watermark_frozen(self) -> None:
        """ReportWatermark frozen=True。"""
        tracker = WatermarkTracker()
        wm = tracker.stamp("rpt", {"a": 1}, "Src")
        with pytest.raises(dataclasses.FrozenInstanceError):
            wm.source = "Hacked"  # type: ignore[misc]

    def test_watermark_content_hash_frozen(self) -> None:
        """content_hash 不可重新赋值。"""
        tracker = WatermarkTracker()
        wm = tracker.stamp("rpt", {"a": 1}, "Src")
        with pytest.raises(dataclasses.FrozenInstanceError):
            wm.content_hash = "fake"  # type: ignore[misc]


# ── 线程安全测试 ──


class TestThreadSafety:
    def test_concurrent_stamp_no_loss(self) -> None:
        """并发 stamp: 无水印丢失。"""
        tracker = WatermarkTracker()
        n_threads = 8
        n_per_thread = 20
        barrier = threading.Barrier(n_threads)

        def worker(tid: int) -> None:
            barrier.wait()
            for i in range(n_per_thread):
                tracker.stamp("rpt", {"thread": tid, "i": i}, f"Src{tid}")

        threads = [threading.Thread(target=worker, args=(t,)) for t in range(n_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        wms = tracker.list_watermarks("rpt")
        assert len(wms) == n_threads * n_per_thread
        assert tracker.verify_chain("rpt") is True

    def test_concurrent_multi_report(self) -> None:
        """并发多报告互不干扰。"""
        tracker = WatermarkTracker()
        n_reports = 4
        n_per = 15
        barrier = threading.Barrier(n_reports)

        def worker(rid: str) -> None:
            barrier.wait()
            for i in range(n_per):
                tracker.stamp(rid, {"v": i}, "Src")

        threads = [
            threading.Thread(target=worker, args=(f"rpt_{r}",))
            for r in range(n_reports)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        for r in range(n_reports):
            rid = f"rpt_{r}"
            assert len(tracker.list_watermarks(rid)) == n_per
            assert tracker.verify_chain(rid) is True


# ── 哈希工具测试 ──


class TestHashUtils:
    def test_content_hash_deterministic(self) -> None:
        """相同内容（不同键序）哈希一致。"""
        h1 = _compute_content_hash({"b": 2, "a": 1})
        h2 = _compute_content_hash({"a": 1, "b": 2})
        assert h1 == h2

    def test_different_content_different_hash(self) -> None:
        """不同内容哈希不同。"""
        assert _compute_content_hash({"a": 1}) != _compute_content_hash({"a": 2})

    def test_signature_includes_source(self) -> None:
        """签名含 source, 不同 source 签名不同。"""
        from datetime import UTC, datetime
        ts = datetime.now(UTC)
        ch = "abc123"
        sig1 = _compute_signature("SrcA", ch, ts)
        sig2 = _compute_signature("SrcB", ch, ts)
        assert sig1 != sig2

    def test_record_hash_includes_all_fields(self) -> None:
        """record_hash 含所有字段, 任一变化则不同。"""
        from datetime import UTC, datetime
        ts = datetime.now(UTC)
        base = _compute_record_hash("wid", "rpt", "Src", ts, "ch", "sig", "")
        assert base != _compute_record_hash("wid2", "rpt", "Src", ts, "ch", "sig", "")
        assert base != _compute_record_hash("wid", "rpt2", "Src", ts, "ch", "sig", "")
        assert base != _compute_record_hash("wid", "rpt", "Src2", ts, "ch", "sig", "")
        assert base != _compute_record_hash("wid", "rpt", "Src", ts, "ch2", "sig", "")
        assert base != _compute_record_hash("wid", "rpt", "Src", ts, "ch", "sig2", "")
        assert base != _compute_record_hash("wid", "rpt", "Src", ts, "ch", "sig", "prev")
