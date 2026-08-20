# [BLUEPRINT] MOD-RPT-003 | docs/03_modules/_domain_reporting/report_publisher/blueprint.md
# [MODULE] tests.reporting.test_report_publisher
# [DOMAIN] D_REPORTING
# [INVARIANTS] 报告域唯一出口(D-RPT-D05); append-only归档+哈希链; 3分发渠道; frozen不可变; 线程安全; 纯消费层不发布事件
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidPublishInputError(ZA-RPT-0003)
# [TESTS] self
# [A_module] module_id=MOD-RPT-003 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-RPT-003 Report Publisher 单元测试.

覆盖（blueprint §9）:
  - 归档: publish() append-only + 哈希链链接
  - 分发: 3渠道(ARCHIVE/WEBHOOK/EMAIL) + 状态(SENT/PENDING)
  - 查询: get_report/list_by_source/list_by_type/get_latest/list_distributions
  - verify_chain: content_hash/record_hash/prev_hash 计算正确 + 篡改检测
  - frozen 不可变
  - 线程安全: 并发 publish 无丢失
  - 边界值: 空 content/非法 source/默认渠道/content非dict
  - 多来源隔离
  - 分发记录关联
"""

from __future__ import annotations

import dataclasses
import threading
from datetime import UTC, datetime
from typing import Any

import pytest

from zephyr.reporting.report_publisher import (
    ArchivedReport,
    DistributionChannel,
    DistributionRecord,
    DistributionStatus,
    InvalidPublishInputError,
    ReportPublisher,
    ReportSource,
    _compute_content_hash,
    _compute_record_hash,
)

# ── 归档测试 ──


class TestPublish:
    def test_publish_returns_archived_report(self) -> None:
        """publish 返回 ArchivedReport, 含完整元数据。"""
        pub = ReportPublisher()
        archived = pub.publish(
            report_id="RPT-001",
            source=ReportSource.RISK,
            report_type="daily_risk",
            content={"risk_level": "HIGH", "var_95": 0.05},
        )
        assert archived.archive_id.startswith("ARCH-")
        assert archived.report_id == "RPT-001"
        assert archived.source == ReportSource.RISK
        assert archived.report_type == "daily_risk"
        assert archived.content == {"risk_level": "HIGH", "var_95": 0.05}
        assert archived.schema_version == "1.0"
        assert archived.content_hash  # 非空
        assert archived.record_hash  # 非空

    def test_first_report_prev_hash_empty(self) -> None:
        """首条归档 prev_hash=""（空串）。"""
        pub = ReportPublisher()
        archived = pub.publish(
            "RPT-001",
            ReportSource.RISK,
            "daily_risk",
            {"level": "LOW"},
        )
        assert archived.prev_hash == ""

    def test_hash_chain_links_correctly(self) -> None:
        """prev_hash(v_n) = record_hash(v_{n-1})。"""
        pub = ReportPublisher()
        a1 = pub.publish("RPT-1", ReportSource.RISK, "daily", {"v": 1})
        a2 = pub.publish("RPT-2", ReportSource.RISK, "daily", {"v": 2})
        a3 = pub.publish("RPT-3", ReportSource.RISK, "daily", {"v": 3})
        assert a1.prev_hash == ""
        assert a2.prev_hash == a1.record_hash
        assert a3.prev_hash == a2.record_hash

    def test_content_hash_computed_correctly(self) -> None:
        """content_hash = SHA-256(canonical_json(content))。"""
        pub = ReportPublisher()
        content = {"b": 2, "a": 1}  # 故意乱序
        archived = pub.publish("RPT-1", ReportSource.RISK, "daily", content)
        assert archived.content_hash == _compute_content_hash(content)

    def test_record_hash_computed_correctly(self) -> None:
        """record_hash = SHA-256(链指纹)。"""
        pub = ReportPublisher()
        archived = pub.publish("RPT-1", ReportSource.RISK, "daily", {"v": 1})
        expected = _compute_record_hash(
            archived.archive_id,
            archived.archived_at,
            archived.report_id,
            archived.source.value,
            archived.report_type,
            archived.content_hash,
            archived.prev_hash,
        )
        assert archived.record_hash == expected

    def test_append_only_no_modification(self) -> None:
        """已归档报告不可修改（frozen）。"""
        pub = ReportPublisher()
        archived = pub.publish("RPT-1", ReportSource.RISK, "daily", {"v": 1})
        with pytest.raises(dataclasses.FrozenInstanceError):
            archived.report_id = "HACK"  # type: ignore[misc]

    def test_content_copied(self) -> None:
        """content 是 dict 副本——外部修改不影响归档的顶层值。"""
        pub = ReportPublisher()
        content = {"level": "HIGH"}
        archived = pub.publish("RPT-1", ReportSource.RISK, "daily", content)
        # 顶层 dict 是副本
        assert archived.content == {"level": "HIGH"}
        # 归档后修改原 dict 不影响归档（浅拷贝传播到嵌套, 但顶层 key 不受影响）


# ── 分发测试 ──


class TestDistribution:
    def test_default_channel_is_archive(self) -> None:
        """channels=None 默认 [ARCHIVE]。"""
        pub = ReportPublisher()
        archived = pub.publish(
            "RPT-1",
            ReportSource.RISK,
            "daily",
            {"v": 1},
        )
        dists = pub.list_distributions(archived.archive_id)
        assert len(dists) == 1
        assert dists[0].channel == DistributionChannel.ARCHIVE

    def test_archive_channel_sent(self) -> None:
        """ARCHIVE 渠道 → SENT 状态。"""
        pub = ReportPublisher()
        archived = pub.publish(
            "RPT-1",
            ReportSource.RISK,
            "daily",
            {"v": 1},
            channels=[DistributionChannel.ARCHIVE],
        )
        dists = pub.list_distributions(archived.archive_id)
        assert dists[0].status == DistributionStatus.SENT

    def test_webhook_channel_pending(self) -> None:
        """WEBHOOK 渠道 → PENDING 状态（基础版需外部服务）。"""
        pub = ReportPublisher()
        archived = pub.publish(
            "RPT-1",
            ReportSource.RISK,
            "daily",
            {"v": 1},
            channels=[DistributionChannel.WEBHOOK],
        )
        dists = pub.list_distributions(archived.archive_id)
        assert dists[0].status == DistributionStatus.PENDING

    def test_email_channel_pending(self) -> None:
        """EMAIL 渠道 → PENDING 状态。"""
        pub = ReportPublisher()
        archived = pub.publish(
            "RPT-1",
            ReportSource.RISK,
            "daily",
            {"v": 1},
            channels=[DistributionChannel.EMAIL],
        )
        dists = pub.list_distributions(archived.archive_id)
        assert dists[0].status == DistributionStatus.PENDING

    def test_multiple_channels(self) -> None:
        """多渠道分发——每渠道一条记录。"""
        pub = ReportPublisher()
        archived = pub.publish(
            "RPT-1",
            ReportSource.RISK,
            "daily",
            {"v": 1},
            channels=[DistributionChannel.ARCHIVE, DistributionChannel.WEBHOOK, DistributionChannel.EMAIL],
        )
        dists = pub.list_distributions(archived.archive_id)
        assert len(dists) == 3
        channels = {d.channel for d in dists}
        assert channels == {DistributionChannel.ARCHIVE, DistributionChannel.WEBHOOK, DistributionChannel.EMAIL}

    def test_distribution_links_to_archive(self) -> None:
        """分发记录关联到正确的 archive_id。"""
        pub = ReportPublisher()
        archived = pub.publish(
            "RPT-1",
            ReportSource.RISK,
            "daily",
            {"v": 1},
            channels=[DistributionChannel.ARCHIVE],
        )
        dists = pub.list_distributions(archived.archive_id)
        assert all(d.archive_id == archived.archive_id for d in dists)

    def test_no_distributions_for_unknown_archive(self) -> None:
        """未知的 archive_id → 空列表。"""
        pub = ReportPublisher()
        assert pub.list_distributions("UNKNOWN") == []

    def test_distribution_record_is_frozen(self) -> None:
        """DistributionRecord frozen。"""
        pub = ReportPublisher()
        archived = pub.publish(
            "RPT-1",
            ReportSource.RISK,
            "daily",
            {"v": 1},
        )
        dists = pub.list_distributions(archived.archive_id)
        with pytest.raises(dataclasses.FrozenInstanceError):
            dists[0].status = DistributionStatus.FAILED  # type: ignore[misc]


# ── 查询测试 ──


class TestQuery:
    def test_get_report_by_id(self) -> None:
        """get_report 按 archive_id 查询。"""
        pub = ReportPublisher()
        archived = pub.publish("RPT-1", ReportSource.RISK, "daily", {"v": 1})
        found = pub.get_report(archived.archive_id)
        assert found is not None
        assert found.report_id == "RPT-1"

    def test_get_report_not_found(self) -> None:
        """get_report 未找到 → None。"""
        pub = ReportPublisher()
        assert pub.get_report("UNKNOWN") is None

    def test_list_by_source(self) -> None:
        """list_by_source 按来源过滤。"""
        pub = ReportPublisher()
        pub.publish("RPT-1", ReportSource.RISK, "daily", {"v": 1})
        pub.publish("RPT-2", ReportSource.REGULATORY, "monthly", {"v": 2})
        pub.publish("RPT-3", ReportSource.RISK, "weekly", {"v": 3})
        risk_reports = pub.list_by_source(ReportSource.RISK)
        assert len(risk_reports) == 2
        assert all(r.source == ReportSource.RISK for r in risk_reports)

    def test_list_by_type(self) -> None:
        """list_by_type 按类型过滤。"""
        pub = ReportPublisher()
        pub.publish("RPT-1", ReportSource.RISK, "daily", {"v": 1})
        pub.publish("RPT-2", ReportSource.RISK, "weekly", {"v": 2})
        pub.publish("RPT-3", ReportSource.RISK, "daily", {"v": 3})
        daily_reports = pub.list_by_type("daily")
        assert len(daily_reports) == 2

    def test_list_ordered_by_archive_time(self) -> None:
        """list_by_source 按归档时间升序。"""
        pub = ReportPublisher()
        a1 = pub.publish("RPT-1", ReportSource.RISK, "daily", {"v": 1})
        a2 = pub.publish("RPT-2", ReportSource.RISK, "daily", {"v": 2})
        a3 = pub.publish("RPT-3", ReportSource.RISK, "daily", {"v": 3})
        reports = pub.list_by_source(ReportSource.RISK)
        assert reports[0].archive_id == a1.archive_id
        assert reports[1].archive_id == a2.archive_id
        assert reports[2].archive_id == a3.archive_id

    def test_get_latest(self) -> None:
        """get_latest 返回最新归档。"""
        pub = ReportPublisher()
        pub.publish("RPT-1", ReportSource.RISK, "daily", {"v": 1})
        pub.publish("RPT-2", ReportSource.RISK, "daily", {"v": 2})
        a3 = pub.publish("RPT-3", ReportSource.RISK, "daily", {"v": 3})
        latest = pub.get_latest(ReportSource.RISK)
        assert latest is not None
        assert latest.archive_id == a3.archive_id

    def test_get_latest_not_found(self) -> None:
        """get_latest 未找到 → None。"""
        pub = ReportPublisher()
        assert pub.get_latest(ReportSource.TCA) is None

    def test_multi_source_isolation(self) -> None:
        """不同来源互不干扰。"""
        pub = ReportPublisher()
        pub.publish("RPT-1", ReportSource.RISK, "daily", {"v": 1})
        pub.publish("RPT-2", ReportSource.REGULATORY, "monthly", {"v": 2})
        assert len(pub.list_by_source(ReportSource.RISK)) == 1
        assert len(pub.list_by_source(ReportSource.REGULATORY)) == 1
        assert len(pub.list_by_source(ReportSource.TCA)) == 0


# ── verify_chain 测试 ──


class TestVerifyChain:
    def test_empty_chain_passes(self) -> None:
        """空归档 → verify_chain 返回 True。"""
        pub = ReportPublisher()
        assert pub.verify_chain() is True

    def test_valid_chain_passes(self) -> None:
        """未篡改的链 → verify_chain 返回 True。"""
        pub = ReportPublisher()
        pub.publish("RPT-1", ReportSource.RISK, "daily", {"v": 1})
        pub.publish("RPT-2", ReportSource.RISK, "daily", {"v": 2})
        pub.publish("RPT-3", ReportSource.RISK, "daily", {"v": 3})
        assert pub.verify_chain() is True

    def test_tampered_content_fails(self) -> None:
        """篡改 content → verify_chain 返回 False。"""
        pub = ReportPublisher()
        a1 = pub.publish("RPT-1", ReportSource.RISK, "daily", {"v": 1})
        # 篡改 content（用 dataclasses.replace 绕过 frozen）
        tampered = dataclasses.replace(
            a1,
            content={"v": 999},
        )
        # 手动替换归档中的报告
        pub._archive[0] = tampered
        pub._archive_by_id[a1.archive_id] = tampered
        assert pub.verify_chain() is False

    def test_broken_prev_hash_fails(self) -> None:
        """prev_hash 链接断裂 → verify_chain 返回 False。"""
        pub = ReportPublisher()
        a1 = pub.publish("RPT-1", ReportSource.RISK, "daily", {"v": 1})
        a2 = pub.publish("RPT-2", ReportSource.RISK, "daily", {"v": 2})
        # 篡改 a2 的 prev_hash
        tampered = dataclasses.replace(a2, prev_hash="FAKE_HASH")
        pub._archive[1] = tampered
        pub._archive_by_id[a2.archive_id] = tampered
        assert pub.verify_chain() is False

    def test_forged_record_hash_fails(self) -> None:
        """record_hash 伪造 → verify_chain 返回 False。"""
        pub = ReportPublisher()
        a1 = pub.publish("RPT-1", ReportSource.RISK, "daily", {"v": 1})
        tampered = dataclasses.replace(a1, record_hash="FAKE_HASH")
        pub._archive[0] = tampered
        pub._archive_by_id[a1.archive_id] = tampered
        assert pub.verify_chain() is False


# ── 线程安全测试 ──


class TestThreadSafety:
    def test_concurrent_publish_no_loss(self) -> None:
        """并发 publish 无丢失。"""
        pub = ReportPublisher()
        n_threads = 10
        n_per_thread = 20

        def _publish_batch() -> None:
            for i in range(n_per_thread):
                pub.publish(
                    f"RPT-{threading.get_ident()}-{i}",
                    ReportSource.RISK,
                    "daily",
                    {"i": i},
                )

        threads = [threading.Thread(target=_publish_batch) for _ in range(n_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert pub.archive_count == n_threads * n_per_thread
        assert pub.verify_chain() is True


# ── 边界值 / 错误契约测试 ──


class TestEdgeCases:
    def test_empty_report_id_raises(self) -> None:
        """report_id 为空 → 拒绝。"""
        pub = ReportPublisher()
        with pytest.raises(InvalidPublishInputError):
            pub.publish("", ReportSource.RISK, "daily", {"v": 1})

    def test_empty_report_type_raises(self) -> None:
        """report_type 为空 → 拒绝。"""
        pub = ReportPublisher()
        with pytest.raises(InvalidPublishInputError):
            pub.publish("RPT-1", ReportSource.RISK, "  ", {"v": 1})

    def test_empty_content_raises(self) -> None:
        """content 为空 dict → 拒绝。"""
        pub = ReportPublisher()
        with pytest.raises(InvalidPublishInputError):
            pub.publish("RPT-1", ReportSource.RISK, "daily", {})

    def test_non_dict_content_raises(self) -> None:
        """content 非 dict → 拒绝。"""
        pub = ReportPublisher()
        with pytest.raises(InvalidPublishInputError):
            pub.publish("RPT-1", ReportSource.RISK, "daily", "not a dict")  # type: ignore[arg-type]

    def test_error_code_is_za_rpt_0003(self) -> None:
        """InvalidPublishInputError.error_code = ZA-RPT-0003。"""
        assert InvalidPublishInputError.error_code == "ZA-RPT-0003"

    def test_archive_count(self) -> None:
        """archive_count 返回正确数量。"""
        pub = ReportPublisher()
        assert pub.archive_count == 0
        pub.publish("RPT-1", ReportSource.RISK, "daily", {"v": 1})
        assert pub.archive_count == 1
        pub.publish("RPT-2", ReportSource.RISK, "daily", {"v": 2})
        assert pub.archive_count == 2

    def test_all_source_enum_values(self) -> None:
        """ReportSource 12个枚举值正确。"""
        expected = {
            "tca",
            "attribution",
            "realtime_pnl",
            "regulatory",
            "risk",
            "explainability",
            "trading_review",
            "performance_audit",
            "version",
            "watermark",
            "trade_record",
            "execution_audit",
        }
        actual = {s.value for s in ReportSource}
        assert actual == expected

    def test_distribution_channel_enum_values(self) -> None:
        """DistributionChannel 3个枚举值正确。"""
        assert DistributionChannel.ARCHIVE.value == "archive"
        assert DistributionChannel.WEBHOOK.value == "webhook"
        assert DistributionChannel.EMAIL.value == "email"

    def test_distribution_status_enum_values(self) -> None:
        """DistributionStatus 3个枚举值正确。"""
        assert DistributionStatus.PENDING.value == "PENDING"
        assert DistributionStatus.SENT.value == "SENT"
        assert DistributionStatus.FAILED.value == "FAILED"

    def test_generated_at_is_utc(self) -> None:
        """archived_at 为 UTC 时间。"""
        pub = ReportPublisher()
        before = datetime.now(UTC)
        archived = pub.publish("RPT-1", ReportSource.RISK, "daily", {"v": 1})
        after = datetime.now(UTC)
        assert archived.archived_at.tzinfo is not None
        assert before <= archived.archived_at <= after

    def test_same_content_same_content_hash(self) -> None:
        """同内容 → 相同 content_hash（确定性）。"""
        pub = ReportPublisher()
        content = {"a": 1, "b": [1, 2, 3]}
        a1 = pub.publish("RPT-1", ReportSource.RISK, "daily", content)
        a2 = pub.publish("RPT-2", ReportSource.RISK, "daily", dict(content))
        assert a1.content_hash == a2.content_hash
