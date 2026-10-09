# [MODULE] tests.data.implementations.test_akshare_etf_benchmark
# [TTL] permanent
# ttl: permanent
# completes_when: _fetch_etf_benchmark 治本验收后随 provider 生命周期常驻（回归保护）
# [TESTS] src/zephyr/data/implementations/akshare_provider.py (_fetch_etf_benchmark)
# tests/ 目录 CREATE-GUARD 豁免（根宪法 §1 补充铁律）
"""_fetch_etf_benchmark 重写（99 #19）单元测试 + 真调烟测留证。

实弹证据（2026-09-29，akshare 1.18.75，小样本真调）：
    - ak.index_stock_info()：现为无参签名，旧 provider 调法
      index_stock_info(symbol="000300") 实调 TypeError（unexpected keyword
      argument 'symbol'）——旧代码不仅丢弃返回值恒 rows=[]，调用本身就崩，
      且异常被 except 吞掉后仍 yield SUCCESS 假绿。
    - ak.fund_etf_fund_info_em(fund="510300", start_date="20260901",
      end_date="20260915")：rows=11, cols=[净值日期, 单位净值, 累计净值,
      日增长率, 申购状态, 赎回状态]——ETF 净值时序，与 etf_benchmark 表列
      （指数元数据 publisher/base_date/base_point/adjust_cycle）语义不符，
      原 tasks.yaml 声明判错（已同步修正为 index_csindex_all）。
    - ak.index_csindex_all()：rows=2370, cols=[指数代码, 指数简称, 指数全称,
      基日, 基点, 指数系列, 样本数量, 最新收盘, 近一个月收益率, 资产类别,
      指数热点, 指数币种, 合作指数, 跟踪产品, 指数合规, 指数类别, 发布时间]
      ——与表列一一对应，选定为本表真源接口。
"""

from __future__ import annotations

import os
import sys
import types
from datetime import date

import pandas as pd
import pytest

from zephyr.data.implementations.akshare_provider import _TBL_ETF_BENCHMARK, AkshareIngestProvider
from zephyr.data.policy_registry import SourcePolicy
from zephyr.data.provider_base import FetchPayload


def _payload() -> FetchPayload:
    return FetchPayload(table=_TBL_ETF_BENCHMARK, symbols=None, start=date(2026, 9, 29), end=date(2026, 9, 29))


def _policy() -> SourcePolicy:
    # 测试零重试：失败路径立即抛出，不烧退避等待
    return SourcePolicy(rpm=0, max_retries=0)


def _fake_akshare(monkeypatch: pytest.MonkeyPatch, fn) -> None:
    """向 sys.modules 注入带 index_csindex_all 的伪 akshare 模块（provider 方法内延迟 import）。"""
    stub = types.ModuleType("akshare")
    stub.index_csindex_all = fn  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "akshare", stub)


def test_etf_benchmark_happy_path(monkeypatch: pytest.MonkeyPatch):
    """正常路径：列映射/类型口径/last_key=最大 publish_date。"""
    df = pd.DataFrame(
        {
            "指数代码": ["000300", "000905", "", "000852"],
            "指数全称": ["沪深300指数", "中证500指数", "无码指数", "中证1000指数"],
            "指数简称": ["沪深300", "中证500", "无码", "中证1000"],
            "发布时间": ["2005-04-08", "2007-01-15", "2020-01-01", "2014-10-17"],
            "基日": ["2004-12-31", "2004-12-31", "2020-01-01", "2004-12-31"],
            "基点": [1000.0, 1000.0, 1000.0, 1000.0],
        }
    )
    _fake_akshare(monkeypatch, lambda: df)
    provider = AkshareIngestProvider()
    results = list(provider._fetch_etf_benchmark(_payload(), _policy()))
    assert len(results) == 1
    res = results[0]
    assert res.error is None
    assert res.table == "c1_market.etf_benchmark"
    assert res.columns == [
        "index_code",
        "index_full_name",
        "index_short_name",
        "publisher",
        "publish_date",
        "base_date",
        "base_point",
        "adjust_cycle",
    ]
    # 缺指数代码行被丢弃（3 条有效）
    assert len(res.rows) == 3
    row = res.rows[0]
    assert row[0] == "000300"
    assert row[1] == "沪深300指数"
    assert row[2] == "沪深300"
    assert row[3] == "中证指数有限公司"
    assert row[4] == "2005-04-08"
    assert row[5] == "2004-12-31"
    assert row[6] == 1000.0
    assert row[7] == ""  # adjust_cycle 源不提供，如实留空
    # last_key=行集最大 publish_date（date_col 锚口径，非 today() 假新鲜）
    assert res.last_key == "2014-10-17"


def test_etf_benchmark_missing_publish_date_dropped(monkeypatch: pytest.MonkeyPatch):
    """缺发布时间（新鲜度锚）的行丢弃——publish_date 为 Date 非空列，禁拍哨兵日期。"""
    df = pd.DataFrame(
        {
            "指数代码": ["000300", "000905"],
            "指数全称": ["沪深300指数", "中证500指数"],
            "指数简称": ["沪深300", "中证500"],
            "发布时间": ["2005-04-08", None],
            "基日": ["2004-12-31", "2004-12-31"],
            "基点": [1000.0, 1000.0],
        }
    )
    _fake_akshare(monkeypatch, lambda: df)
    provider = AkshareIngestProvider()
    results = list(provider._fetch_etf_benchmark(_payload(), _policy()))
    res = results[0]
    assert res.error is None
    assert len(res.rows) == 1
    assert res.rows[0][0] == "000300"
    assert res.last_key == "2005-04-08"


def test_etf_benchmark_empty_df_is_error_not_fake_green(monkeypatch: pytest.MonkeyPatch):
    """源返回空 → error 显式报红（治 99 #19 假绿：禁 rows=[] 仍 SUCCESS）。"""
    _fake_akshare(monkeypatch, lambda: pd.DataFrame())
    provider = AkshareIngestProvider()
    results = list(provider._fetch_etf_benchmark(_payload(), _policy()))
    assert len(results) == 1
    res = results[0]
    assert res.rows == []
    assert res.last_key == ""
    assert res.error  # 报错不静默


def test_etf_benchmark_exception_is_error(monkeypatch: pytest.MonkeyPatch):
    """接口抛异常 → error 结果（治旧实现 except 吞异常后假绿 SUCCESS）。"""

    def _boom():
        raise RuntimeError("csindex 反爬 403")

    _fake_akshare(monkeypatch, _boom)
    provider = AkshareIngestProvider()
    results = list(provider._fetch_etf_benchmark(_payload(), _policy()))
    res = results[0]
    assert res.rows == []
    assert "csindex 反爬 403" in res.error
    assert res.last_key == ""


@pytest.mark.skipif(os.environ.get("ZEPHYR_LIVE_AKSHARE") != "1", reason="真调烟测：仅 ZEPHYR_LIVE_AKSHARE=1 时运行")
@pytest.mark.filterwarnings(
    "ignore::UserWarning"
)  # akshare 导入链 py_mini_racer 的 pkg_resources 弃用告警，与被测逻辑无关
def test_live_smoke_etf_benchmark():
    """真调烟测（99 #19 验收留证）：走 provider 全链路实调 akshare。"""
    provider = AkshareIngestProvider()
    results = list(provider._fetch_etf_benchmark(_payload(), SourcePolicy(rpm=0, max_retries=1)))
    assert len(results) == 1
    res = results[0]
    assert res.error is None, f"真调失败: {res.error}"
    assert len(res.rows) > 0, "真调行数必须 >0"
