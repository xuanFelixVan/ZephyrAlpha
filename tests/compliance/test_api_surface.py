"""compliance/api 公共出口冒烟测试（43 号施工挂载面）。"""

from __future__ import annotations

import zephyr.compliance.api as cmp_api


def test_api_surface_importable():
    """zephyr.compliance.api 导出全部 7 模块公共符号。"""
    expected = {
        "ChecklistCompletionChecker",
        "DisciplineGuard",
        "KillSwitchLite",
        "LicenseUsageAuditor",
        "FeatureGate",
        "TradingComplianceDetector",
        "ComplianceReportRegistry",
        "ReportGate",
        "ComplianceLogger",
    }
    assert expected <= set(cmp_api.__all__)
    for name in cmp_api.__all__:
        assert getattr(cmp_api, name) is not None
