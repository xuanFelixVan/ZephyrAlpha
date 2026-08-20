# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] tests.zephyr.data.test_capability_semantic_gate
# [DOMAIN] D_DATA
# [A_module] module_id=MOD-TEST-DATA-SEMGATE | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""capability 语义注册表 + API 白名单 gate 单元测试（17 号 §5.8 施工项 2+3 合并 MVP）。

覆盖:
  - 验收用例 1：#ARCH-DATA-001 形态——_fetch_hk_trade_calendar 调
    ak.tool_trade_date_hist_sina（A股 API 冒充港股日历）→ 检出
  - 验收用例 2：#ARCH-CH-INDUSTRY-CLASS-MIGRATE 形态——_fetch_industry_class 调
    白名单外 API（tdx 板块成分冒充申万行业）→ 检出
  - 通过形态：exchange_calendars.XHKG / ak.tool_trade_date_hist_sina / THS_ 前缀
  - 过度工程防线：未登记 capability 不校验
  - 通配符：THS_* 前缀命中 / 非前缀不命中
  - 退化：语法错误 fail-open；无 _fetch_<cap> 方法（未实现）不校验；文件变体
"""

from __future__ import annotations

from zephyr.data.capability_semantic_gate import (
    DEFAULT_SEMANTIC_REGISTRY,
    CapabilitySemanticEntry,
    check_capability_api_whitelist,
    check_capability_api_whitelist_content,
)

HK_OK = """
import exchange_calendars as xcals


class P:
    def _fetch_hk_trade_calendar(self, payload):
        cal = xcals.get_calendar("XHKG")
        return cal
"""

# #ARCH-DATA-001 历史 bug 形态：hk_trade_calendar 用 A股 sina API
HK_BUG = """
import akshare as ak


class P:
    def _fetch_hk_trade_calendar(self, payload):
        return ak.tool_trade_date_hist_sina()
"""

# INDUSTRY-CLASS-MIGRATE 历史 bug 形态：industry_class 用 mootdx 板块成分
INDUSTRY_BUG = """
import akshare as ak


class P:
    def _fetch_industry_class(self, payload):
        return ak.stock_board_industry_cons_em(symbol="BK0475")
"""

TRADE_CAL_OK = """
import akshare as ak


class P:
    def _fetch_trade_calendar(self, payload):
        return ak.tool_trade_date_hist_sina()
"""


class TestAcceptanceHistoricalBugs:
    """17 号 §5.8 验收：gate 须检出两个历史 bug。"""

    def test_arch_data_001_detected(self):
        violations = check_capability_api_whitelist_content(HK_BUG)
        assert len(violations) == 1
        assert "hk_trade_calendar" in violations[0]
        assert "akshare.tool_trade_date_hist_sina" in violations[0]  # 别名归一化为规范模块名
        assert "登记或换 API" in violations[0]

    def test_industry_class_migrate_detected(self):
        violations = check_capability_api_whitelist_content(INDUSTRY_BUG)
        assert len(violations) == 1
        assert "industry_class" in violations[0]
        assert "akshare.stock_board_industry_cons_em" in violations[0]


class TestPassForms:
    def test_hk_exchange_calendars_ok(self):
        assert check_capability_api_whitelist_content(HK_OK) == []

    def test_trade_calendar_ak_ok(self):
        assert check_capability_api_whitelist_content(TRADE_CAL_OK) == []

    def test_ths_wildcard_ok(self):
        content = """
class P:
    def _fetch_industry_class(self, payload):
        return THS_DataPool("block", "2026-08-20")
"""
        # THS_DataPool 非 import alias 调用（未 import）→ 不提取 → 不校验
        assert check_capability_api_whitelist_content(content) == []


class TestWildcard:
    def test_ths_prefix_match(self):
        """THS_* 通配：规范模块名 THS_iFinD.* 前缀命中 → 放行。"""
        content = """
import THS_iFinD


class P:
    def _fetch_industry_class(self, payload):
        return THS_iFinD.THS_DataPool("block")
"""
        assert check_capability_api_whitelist_content(content) == []

    def test_non_whitelisted_source_blocked(self):
        """mootdx（INDUSTRY-CLASS bug 源）不在白名单 → 拦截。"""
        content = """
import mootdx


class P:
    def _fetch_industry_class(self, payload):
        return mootdx.block("880")
"""
        violations = check_capability_api_whitelist_content(content)
        assert len(violations) == 1
        assert "mootdx.block" in violations[0]

    def test_stdlib_pandas_not_extracted(self):
        """stdlib/pandas 工具调用不是数据源 API（2026-08-20 真实扫描误报收敛）。"""
        content = """
import time
from datetime import timedelta
import pandas as pd
import exchange_calendars as xcals


class P:
    def _fetch_hk_trade_calendar(self, payload):
        t0 = time.monotonic()
        cal = xcals.get_calendar("XHKG")
        ts = pd.Timestamp("2026-08-20")
        return cal
"""
        assert check_capability_api_whitelist_content(content) == []


class TestOverEngineeringGuard:
    def test_unregistered_capability_not_checked(self):
        """未登记 capability（如 us_kline）不校验——过度工程防线。"""
        content = """
import yfinance as yf


class P:
    def _fetch_us_kline(self, payload):
        return yf.download("AAPL")
"""
        assert check_capability_api_whitelist_content(content) == []

    def test_method_absent_not_checked(self):
        """注册了但文件无 _fetch_<cap> 方法（该 provider 未实现此能力）→ 不校验。"""
        content = """
import akshare as ak


class P:
    def _fetch_other(self, payload):
        return ak.tool_trade_date_hist_sina()
"""
        assert check_capability_api_whitelist_content(content) == []


class TestCustomRegistry:
    def test_custom_entry_enforced(self):
        registry = (
            CapabilitySemanticEntry(
                capability_id="us_kline",
                market="us",
                variety="stock",
                allowed_apis=frozenset({"yfinance.download"}),
            ),
        )
        bad = """
import yfinance as yf


class P:
    def _fetch_us_kline(self, payload):
        return yf.Ticker("AAPL").history()
"""
        violations = check_capability_api_whitelist_content(bad, registry)
        assert len(violations) == 1
        assert "us_kline" in violations[0]
        assert "yfinance.Ticker" in violations[0]
        ok = """
import yfinance as yf


class P:
    def _fetch_us_kline(self, payload):
        return yf.download("AAPL")
"""
        assert check_capability_api_whitelist_content(ok, registry) == []


class TestDegenerate:
    def test_syntax_error_fail_open(self):
        assert check_capability_api_whitelist_content("def broken(:\n") == []

    def test_file_variant(self, tmp_path):
        p = tmp_path / "provider.py"
        p.write_text(HK_BUG, encoding="utf-8")
        assert len(check_capability_api_whitelist(p)) == 1

    def test_file_missing_fail_open(self, tmp_path):
        assert check_capability_api_whitelist(tmp_path / "nope.py") == []

    def test_registry_default_three_entries(self):
        """初始登记 3 条（17 号 §5.8 定稿）。"""
        assert {e.capability_id for e in DEFAULT_SEMANTIC_REGISTRY} == {
            "hk_trade_calendar",
            "trade_calendar",
            "industry_class",
        }
