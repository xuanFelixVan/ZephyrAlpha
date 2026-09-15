# [BLUEPRINT] MOD-L00-004 | (auto-injected by S4 reconciler, module_id corrected 2026-07-23)
# [TTL] permanent
"""alerter 单测（MOD-L00-004 阶段2 + 阶段3 告警通道 audit 8.3）。

测试内容：
- notify 写日志 + 写失败汇总文件
- 失败汇总文件 JSON 格式正确
- check_daily_failure_rate 阈值判断
- check_consecutive_failures 连续失败告警
- list_failure_files / read_failure_file 查询

（外推通道 feishu/SMTP 及其测试已于 2026-09-15 随 Owner 裁撤通知通道一并移除）

用 tmp_path fixture 隔离测试 failures/ 目录。
"""

import json

import pytest

from src.zephyr.data.alerter import (
    LEVEL_CRITICAL,
    LEVEL_ERROR,
    LEVEL_INFO,
    LEVEL_WARN,
    Alerter,
)


@pytest.fixture
def alerter(tmp_path):
    """用临时目录的 Alerter。"""
    return Alerter(failures_dir=tmp_path / "failures")


class TestNotify:
    """notify 测试。"""

    def test_error_writes_failure_file(self, alerter, tmp_path):
        """ERROR 级别应写失败汇总文件。"""
        ok = alerter.notify("kline_daily", "连接超时", level=LEVEL_ERROR, source="akshare")
        assert ok is True
        files = list((tmp_path / "failures").glob("*.json"))
        assert len(files) == 1

    def test_critical_writes_failure_file(self, alerter, tmp_path):
        """CRITICAL 级别应写失败汇总文件。"""
        ok = alerter.notify("kline_daily", "配额耗尽", level=LEVEL_CRITICAL, source="akshare")
        assert ok is True
        files = list((tmp_path / "failures").glob("*.json"))
        assert len(files) == 1

    def test_warn_no_failure_file(self, alerter, tmp_path):
        """WARN 级别不写失败汇总文件。"""
        ok = alerter.notify("kline_daily", "慢查询", level=LEVEL_WARN)
        assert ok is True
        files = list((tmp_path / "failures").glob("*.json"))
        assert len(files) == 0

    def test_info_no_failure_file(self, alerter, tmp_path):
        """INFO 级别不写失败汇总文件。"""
        ok = alerter.notify("kline_daily", "开始执行", level=LEVEL_INFO)
        assert ok is True
        files = list((tmp_path / "failures").glob("*.json"))
        assert len(files) == 0

    def test_failure_file_content(self, alerter, tmp_path):
        """失败汇总文件 JSON 格式正确。"""
        alerter.notify(
            "margin_trading",
            "SSL错误",
            level=LEVEL_ERROR,
            source="akshare",
            extra={"retry_count": 3},
        )
        files = list((tmp_path / "failures").glob("*.json"))
        with open(files[0], encoding="utf-8") as f:
            data = json.load(f)
        assert data["task_id"] == "margin_trading"
        assert data["source"] == "akshare"
        assert data["error"] == "SSL错误"
        assert data["level"] == LEVEL_ERROR
        assert data["extra"]["retry_count"] == 3
        assert "timestamp" in data

    def test_notify_no_exception(self, alerter):
        """notify 不应抛异常（即使参数异常）。"""
        ok = alerter.notify("", "", level=LEVEL_ERROR)
        assert ok in (True, False)  # 不抛异常即可


class TestDailyFailureRate:
    """check_daily_failure_rate 测试。"""

    def test_rate_below_threshold(self, alerter):
        """失败率 <= 5% 不告警。"""
        assert alerter.check_daily_failure_rate(total=100, failed=3) is False
        assert alerter.check_daily_failure_rate(total=100, failed=5) is False  # 等于阈值

    def test_rate_above_threshold(self, alerter, tmp_path):
        """失败率 > 5% 告警。"""
        # 10/100 = 10% > 5%，会写 WARN 级别告警（不写失败汇总文件）
        result = alerter.check_daily_failure_rate(total=100, failed=10)
        assert result is True
        # WARN 不写失败文件
        files = list((tmp_path / "failures").glob("*.json"))
        assert len(files) == 0

    def test_zero_total(self, alerter):
        """total=0 不告警。"""
        assert alerter.check_daily_failure_rate(total=0, failed=0) is False


class TestConsecutiveFailures:
    """check_consecutive_failures 测试。"""

    def test_below_threshold(self, alerter):
        """连续失败 < 3 天不告警。"""
        assert alerter.check_consecutive_failures("kline_daily", 2) is False

    def test_at_threshold(self, alerter, tmp_path):
        """连续失败 >= 3 天告警（CRITICAL）。"""
        result = alerter.check_consecutive_failures("kline_daily", 3)
        assert result is True
        # CRITICAL 写失败文件
        files = list((tmp_path / "failures").glob("*.json"))
        assert len(files) == 1

    def test_custom_threshold(self, alerter):
        """自定义阈值。"""
        assert alerter.check_consecutive_failures("kline_daily", 2, threshold=5) is False
        assert alerter.check_consecutive_failures("kline_daily", 5, threshold=5) is True


class TestQueryFailures:
    """list_failure_files / read_failure_file 测试。"""

    def test_list_empty(self, alerter, tmp_path):
        """无失败文件时返回空列表。"""
        assert alerter.list_failure_files() == []

    def test_list_all(self, alerter, tmp_path):
        """列出所有失败文件。"""
        alerter.notify("task_a", "err1", level=LEVEL_ERROR)
        alerter.notify("task_b", "err2", level=LEVEL_ERROR)
        files = alerter.list_failure_files()
        assert len(files) == 2

    def test_list_by_date(self, alerter, tmp_path):
        """按日期过滤。

        alerter 文件名用 UTC 日期（now_utc().strftime("%Y%m%d")），
        与文件内 timestamp（UTC）保持一致；查询也须用 UTC 日期，
        否则在 UTC<local 的时区窗口（如 CST 00:00-08:00 = UTC 前一天）
        会因日期错位而漏匹配。B2 告警通道验证发现并修复（#ARCH-CH-023）。
        """
        from zephyr.shared.utils.time_utils import now_utc

        alerter.notify("task_a", "err1", level=LEVEL_ERROR)
        today_utc = now_utc().strftime("%Y%m%d")
        files = alerter.list_failure_files(date=today_utc)
        assert len(files) == 1
        files_other = alerter.list_failure_files(date="20250101")
        assert len(files_other) == 0

    def test_read_failure_file(self, alerter, tmp_path):
        """读取失败文件内容。"""
        alerter.notify("task_a", "err1", level=LEVEL_ERROR, source="akshare")
        files = alerter.list_failure_files()
        data = alerter.read_failure_file(files[0])
        assert data is not None
        assert data["task_id"] == "task_a"
        assert data["error"] == "err1"

    def test_read_nonexistent_file(self, alerter):
        """读取不存在的文件返回 None。"""
        assert alerter.read_failure_file("nonexistent.json") is None
