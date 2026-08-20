# [BLUEPRINT] MOD-RPT-003 | docs/03_modules/_domain_reporting/report_publisher/blueprint.md
# [MODULE] tests.reporting.test_report_publisher_senders
# [DOMAIN] D_REPORTING
# [INVARIANTS] 默认仍PENDING不破坏现状; 注入sender实发SENT/FAILED; sender异常不阻断归档哈希链
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
# [TTL] permanent
"""ReportPublisher WEBHOOK/EMAIL 注入式实发测试（54 号 §3.7，AI-NIGHT-001 包P）。"""

from __future__ import annotations

from zephyr.reporting.report_publisher import (
    DistributionChannel,
    DistributionStatus,
    ReportPublisher,
    ReportSource,
)


def _publish(pub: ReportPublisher, channels: list[DistributionChannel]):
    archived = pub.publish(
        report_id="RPT-T1",
        source=ReportSource.RISK,
        report_type="daily_risk",
        content={"risk_level": "HIGH"},
        channels=channels,
    )
    return archived, pub.list_distributions(archived.archive_id)


class TestDefaultPendingUnchanged:
    def test_no_sender_webhook_email_stay_pending(self):
        pub = ReportPublisher()
        _, dists = _publish(
            pub, [DistributionChannel.ARCHIVE, DistributionChannel.WEBHOOK, DistributionChannel.EMAIL]
        )
        by_channel = {d.channel: d.status for d in dists}
        assert by_channel[DistributionChannel.ARCHIVE] is DistributionStatus.SENT
        assert by_channel[DistributionChannel.WEBHOOK] is DistributionStatus.PENDING
        assert by_channel[DistributionChannel.EMAIL] is DistributionStatus.PENDING


class TestInjectedSenders:
    def test_webhook_sender_success_marks_sent(self):
        seen: list[str] = []
        pub = ReportPublisher(
            webhook_sender=lambda archived: seen.append(archived.archive_id) or True
        )
        archived, dists = _publish(pub, [DistributionChannel.WEBHOOK])
        assert dists[0].status is DistributionStatus.SENT
        assert seen == [archived.archive_id]

    def test_email_sender_success_marks_sent(self):
        pub = ReportPublisher(email_sender=lambda archived: True)
        _, dists = _publish(pub, [DistributionChannel.EMAIL])
        assert dists[0].status is DistributionStatus.SENT
        assert dists[0].error_message == ""

    def test_sender_soft_fail_marks_failed(self):
        pub = ReportPublisher(webhook_sender=lambda archived: False)
        _, dists = _publish(pub, [DistributionChannel.WEBHOOK])
        assert dists[0].status is DistributionStatus.FAILED
        assert "软失败" in dists[0].error_message

    def test_sender_exception_marks_failed_not_raised(self):
        def _boom(archived):
            raise ConnectionError("webhook unreachable")

        pub = ReportPublisher(email_sender=_boom)
        archived, dists = _publish(
            pub, [DistributionChannel.ARCHIVE, DistributionChannel.EMAIL]
        )
        email_dist = next(d for d in dists if d.channel is DistributionChannel.EMAIL)
        assert email_dist.status is DistributionStatus.FAILED
        assert "ConnectionError" in email_dist.error_message
        # 归档链不受 sender 异常影响
        assert pub.verify_chain() is True
        assert pub.get_report(archived.archive_id) is not None

    def test_partial_injection_other_channel_stays_pending(self):
        pub = ReportPublisher(webhook_sender=lambda archived: True)
        _, dists = _publish(pub, [DistributionChannel.WEBHOOK, DistributionChannel.EMAIL])
        by_channel = {d.channel: d.status for d in dists}
        assert by_channel[DistributionChannel.WEBHOOK] is DistributionStatus.SENT
        assert by_channel[DistributionChannel.EMAIL] is DistributionStatus.PENDING
