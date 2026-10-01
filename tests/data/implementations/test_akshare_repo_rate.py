# [MODULE] tests.data.implementations.test_akshare_repo_rate
# [TTL] permanent
# ttl: permanent
# completes_when: RepoRate 日期格式回归保护随 provider 生命周期常驻
# [TESTS] src/zephyr/data/implementations/akshare_provider.py (_fetch_repo_rates/_transform_repo)
# tests/ 目录 CREATE-GUARD 豁免（根宪法 §1 补充铁律）
"""RepoRate 'frValueMap' KeyError 修复（st-ffchief-20261001 lane-datapipe P1）回归测试。

根因（2026-10-01 实测取证）：
    akshare 1.18.75 repo_rate_hist 内部对 start_date/end_date 做
    [:4]/[4:6]/[6:] 紧凑切片拼参（site-packages/akshare/rate/repo_rate.py），
    provider 原传 %Y-%m-%d（"2026-09-01"）被拼成 "2026--0-9-01"，
    chinamoney FrrHis 接口对非法日期返回空/兜底 records，
    pd.DataFrame 后无 frValueMap 列 → KeyError('frValueMap')，
    macro_data_incremental 单日 215 连败。

实弹证据（2026-10-01，akshare 1.18.75）：
    - ak.repo_rate_hist(start_date='2026-09-01', end_date='2026-10-01')
      → KeyError('frValueMap')（复现连败）。
    - ak.repo_rate_hist(start_date='20260901', end_date='20261001')
      → shape=(22, 7)，cols=[date, FR001, FR007, FR014, FDR001, FDR007,
      FDR014]，2026-09-30 行 FR001=1.39/FR007=1.38/FR014=1.41。
    - 上游结构未变（records[].frValueMap 仍在），变的是参数格式容忍度。
"""

from __future__ import annotations

import sys
import types

import pandas as pd
import pytest

from zephyr.data.implementations.akshare_provider import AkshareIngestProvider
from zephyr.data.policy_registry import SourcePolicy

_REPO_COLS = ["date", "FR001", "FR007", "FR014", "FDR001", "FDR007", "FDR014"]


def _policy() -> SourcePolicy:
    # 测试零重试：失败路径立即抛出，不烧退避等待
    return SourcePolicy(rpm=0, max_retries=0)


def _fake_akshare(monkeypatch: pytest.MonkeyPatch, fn) -> None:
    """注入带 repo_rate_hist 的伪 akshare 模块（provider 方法内延迟 import）。"""
    stub = types.ModuleType("akshare")
    stub.repo_rate_hist = fn  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "akshare", stub)


def test_fetch_repo_rates_passes_compact_dates(monkeypatch: pytest.MonkeyPatch):
    """核心回归：repo_rate_hist 必须收到紧凑 YYYYMMDD 日期参数。

    akshare 内部按 start_date[:4]/[4:6]/[6:] 切片，传 %Y-%m-%d 会拼出
    "2026--0-9-01" 触发上游空响应 → KeyError('frValueMap') 215 连败。
    """
    captured: dict = {}

    def fake_repo_rate_hist(start_date: str = "", end_date: str = "") -> pd.DataFrame:
        captured["start_date"] = start_date
        captured["end_date"] = end_date
        return pd.DataFrame(
            {
                "date": ["2026-09-30"],
                "FR001": [1.39],
                "FR007": [1.38],
                "FR014": [1.41],
                "FDR001": [1.3655],
                "FDR007": [1.3626],
                "FDR014": [1.40],
            }
        )

    _fake_akshare(monkeypatch, fake_repo_rate_hist)
    provider = AkshareIngestProvider()
    df = provider._fetch_repo_rates(_policy())
    assert len(df) == 1
    # 紧凑 8 位日期断言（本测试的存在意义）
    for key in ("start_date", "end_date"):
        assert len(captured[key]) == 8, f"{key} 必须是 YYYYMMDD 紧凑格式，实际={captured[key]!r}"
        assert captured[key].isdigit(), f"{key} 必须是纯数字，实际={captured[key]!r}"
    assert captured["start_date"] < captured["end_date"]


def test_repo_rate_new_structure_transform():
    """新结构 transform：date/FR001..FDR014 七列 → (date, 回购_X, val, %, daily)。"""
    df = pd.DataFrame(
        {
            "date": ["2026-09-30", "2026-09-29"],
            "FR001": [1.39, 1.37],
            "FR007": [1.38, 1.41],
            "FR014": [1.41, 1.45],
            "FDR001": [1.3655, 1.34],
            "FDR007": [1.3626, 1.39],
            "FDR014": [1.40, 1.39],
        }
    )
    provider = AkshareIngestProvider()
    rows = provider._transform_repo(df)
    assert len(rows) == 12  # 2 日 × 6 期限
    first = rows[0]
    assert first[0] == "2026-09-30"
    assert first[1] == "回购_FR001"
    assert first[2] == 1.39
    assert first[3] == "%"
    assert first[4] == "daily"


def test_repo_rate_empty_and_none_df_safe():
    """空/None DataFrame 不抛异常（上游偶发空响应时降级为 0 行）。"""
    provider = AkshareIngestProvider()
    assert provider._transform_repo(None) == []
    assert provider._transform_repo(pd.DataFrame(columns=_REPO_COLS)) == []


def test_old_dashed_format_would_mangle():
    """文档化断言：dashed 格式经 akshare 切片逻辑必然拼出非法参数。"""
    dashed = "2026-09-01"
    # akshare repo_rate.py 的拼参逻辑原样复刻
    mangled = "-".join([dashed[:4], dashed[4:6], dashed[6:]])
    assert mangled == "2026--0-9-01"
    assert len(mangled) != 10 or not mangled[4:6].isdigit()  # 非法月字段
