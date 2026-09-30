# [MODULE] tests.data.implementations.test_realtime_snapshot_tencent
# [TTL] permanent
# ttl: permanent
# completes_when: realtime_snapshot 换源验收后随 provider 生命周期常驻（回归保护）
# [TESTS] src/zephyr/data/implementations/akshare_provider.py (_fetch_realtime_snapshot/_parse_qt_gtimg_text)
"""realtime_snapshot 腾讯源换源（99 #20）单元测试 + 真调烟测留证。

换源试验实测（2026-09-29，三候选对照）：
    - 东财 stock_zh_a_spot_em：高频触发 IP 级 TCP RST 封锁（#ARCH-AKSHARE-ANTICRAWLER-001 在案），弃。
    - 新浪 stock_zh_a_spot：hq.sinajs.cn 无 Referer 直探 HTTP 403 Forbidden（112 次降级件根因），
      带 Referer 可用但 akshare 接口层仍走旧通道，弃。
    - akshare stock_zh_a_spot_tx（腾讯 mstats）：可用（5569 行/12.9s）但列集仅 zxj 现价，
      无 open/high/low，快照会丢 OHLC，弃。
    - 直连 qt.gtimg.cn（选定）：6/6 只（含 BJ）全返、88 字段含 OHLC+量额、GBK 纯文本非
      HTML、零鉴权。量纲交叉验证 600519.SH 同日 close=1243.88 / 28218手×100=2,821,830 股 /
      348872万×10000=3,488,720,000 元 与存量行精确吻合。
"""

from __future__ import annotations

import os
import sys
import types
from types import SimpleNamespace

import pytest

from zephyr.data.implementations.akshare_provider import _QT_GTIMG_URL, AkshareIngestProvider
from zephyr.data.policy_registry import SourcePolicy
from zephyr.data.provider_base import FetchPayload


def _payload() -> FetchPayload:
    from datetime import date

    return FetchPayload(
        table="c1_market.realtime_snapshot",
        symbols=None,
        start=date(2026, 9, 29),
        end=date(2026, 9, 29),
        incremental=True,
    )


def _policy() -> SourcePolicy:
    return SourcePolicy(rpm=0, max_retries=0)


def _qt_line(
    code: str, name: str, close: str, open_: str, high: str, low: str, vol_hand: str, amt_wan: str, n_fields: int = 88
) -> str:
    """构造一段 qt.gtimg.cn 应答（字段索引对齐真源：2=代码 3=现价 5=今开 6=量手 33=最高 34=最低 37=额万）。"""
    fields = ["~"] * n_fields
    f = [""] * n_fields
    f[1] = name
    f[2] = code
    f[3] = close
    f[4] = close  # 昨收占位
    f[5] = open_
    f[6] = vol_hand
    f[33] = high
    f[34] = low
    f[37] = amt_wan
    return f'v_sh{code}="{"~".join(f)}"'


def test_parse_qt_gtimg_text_happy_path():
    """解析：字段索引/量纲换算（手→股 ×100、万元→元 ×10000）。"""
    text = _qt_line("600519", "贵州茅台", "1243.88", "1236.00", "1244.01", "1228.10", "28218", "348872") + ";"
    rows = AkshareIngestProvider._parse_qt_gtimg_text(text)
    assert len(rows) == 1
    code, open_, high, low, close, vol, amt = rows[0]
    assert code == "600519"
    assert open_ == 1236.00
    assert high == 1244.01
    assert low == 1228.10
    assert close == 1243.88
    assert vol == 2821800  # 28218 手 ×100
    assert amt == 3488720000.0  # 348872 万元 ×10000


def test_parse_qt_gtimg_text_skips_junk_and_suspended():
    """残段（字段<38）与零现价（停牌）行跳过，不抛异常不拍哨兵值。"""
    text = (
        'v_pv_none="1~";'  # 残段
        + _qt_line("000001", "平安银行", "11.30", "11.28", "11.41", "11.27", "715341", "81058")
        + ";"
        + _qt_line("600000", "浦发银行", "0.00", "0.00", "0.00", "0.00", "0", "0")
        + ";"
    )
    rows = AkshareIngestProvider._parse_qt_gtimg_text(text)
    assert len(rows) == 1
    assert rows[0][0] == "000001"


def _fake_akshare_module(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "akshare", types.ModuleType("akshare"))


def test_fetch_realtime_snapshot_tencent_happy(monkeypatch: pytest.MonkeyPatch):
    """换源主链路：代码→前缀码→批量拉取→映射落行（data_source=tencent_qt）。"""
    text = (
        _qt_line("600519", "贵州茅台", "1243.88", "1236.00", "1244.01", "1228.10", "28218", "348872")
        + ";"
        + _qt_line("000001", "平安银行", "11.30", "11.28", "11.41", "11.27", "715341", "81058")
        + ";"
    )
    calls: list[str] = []

    def fake_get(url, timeout=30, headers=None, params=None):
        calls.append(url)
        return SimpleNamespace(content=text.encode("gbk"))

    provider = AkshareIngestProvider()
    monkeypatch.setattr(provider, "_get_all_a_symbols", lambda ak, policy: ["600519", "000001"])
    monkeypatch.setattr(provider, "_http_get", fake_get)
    _fake_akshare_module(monkeypatch)
    results = list(provider._fetch_realtime_snapshot(_payload(), _policy()))
    assert len(results) == 1
    res = results[0]
    assert res.error is None
    assert len(calls) == 1 and calls[0].startswith(_QT_GTIMG_URL)
    assert len(res.rows) == 2
    symbols = {r[1] for r in res.rows}
    assert symbols == {"600519.SH", "000001.SZ"}
    row = next(r for r in res.rows if r[1] == "600519.SH")
    assert row[5] == 1243.88  # close
    assert row[6] == 2821800  # volume 股
    assert row[8] == "tencent_qt"
    assert res.last_key  # snapshot_time 断点键非空


def test_fetch_realtime_snapshot_ts_is_shanghai_local(monkeypatch: pytest.MonkeyPatch):
    """chgo 件3 移交缺陷回归尺：snapshot_time 必须是本地（Asia/Shanghai）墙钟而非 UTC。

    now_utc 冻结在 2026-09-30T04:00:00Z，本地渲染应为 12:00:00（+8h）；若实现回退成
    裸 strftime（UTC 墙钟直写 Asia/Shanghai 列）则本例转红（00:00 != 12:00）。
    """
    from datetime import datetime
    from datetime import timezone as _tz

    from zephyr.data.implementations import akshare_provider as ap

    text = _qt_line("600519", "贵州茅台", "1243.88", "1236.00", "1244.01", "1228.10", "28218", "348872")

    def fake_get(url, timeout=30, headers=None, params=None):
        return SimpleNamespace(content=text.encode("gbk"))

    provider = AkshareIngestProvider()
    monkeypatch.setattr(provider, "_get_all_a_symbols", lambda ak, policy: ["600519"])
    monkeypatch.setattr(provider, "_http_get", fake_get)
    _fake_akshare_module(monkeypatch)
    fixed = datetime(2026, 9, 30, 4, 0, 0, tzinfo=_tz.utc)
    monkeypatch.setattr(ap, "now_utc", lambda: fixed)
    results = list(provider._fetch_realtime_snapshot(_payload(), _policy()))
    row = next(r for r in results[0].rows if r[1] == "600519.SH")
    ts = str(row[0])
    assert "12:00:00" in ts, f"snapshot_time 应为上海本地墙钟 12:00:00，实得 {ts}（UTC 直写回退）"


def test_fetch_realtime_snapshot_chunking(monkeypatch: pytest.MonkeyPatch):
    """180 只代码 → 3 批请求（80+80+20）。"""
    codes = [f"{600000 + i}" for i in range(180)]
    text = _qt_line("600519", "贵州茅台", "1243.88", "1236.00", "1244.01", "1228.10", "28218", "348872") + ";"
    calls: list[str] = []

    def fake_get(url, timeout=30, headers=None, params=None):
        calls.append(url)
        return SimpleNamespace(content=text.encode("gbk"))

    provider = AkshareIngestProvider()
    monkeypatch.setattr(provider, "_get_all_a_symbols", lambda ak, policy: codes)
    monkeypatch.setattr(provider, "_http_get", fake_get)
    _fake_akshare_module(monkeypatch)
    results = list(provider._fetch_realtime_snapshot(_payload(), _policy()))
    assert len(calls) == 3
    # 每批 ≤80：前两批 80 只、末批 20 只
    assert calls[0].count(",") == 79 and calls[2].count(",") == 19
    assert results[0].error is None


def test_fetch_realtime_snapshot_empty_parse_is_error(monkeypatch: pytest.MonkeyPatch):
    """全部解析为空 → error 报红（禁 rows=[] 假绿 SUCCESS）。"""

    def fake_get(url, timeout=30, headers=None, params=None):
        return SimpleNamespace(content=b'v_pv_none="1~";')

    provider = AkshareIngestProvider()
    monkeypatch.setattr(provider, "_get_all_a_symbols", lambda ak, policy: ["600519"])
    monkeypatch.setattr(provider, "_http_get", fake_get)
    _fake_akshare_module(monkeypatch)
    results = list(provider._fetch_realtime_snapshot(_payload(), _policy()))
    res = results[0]
    assert res.rows == []
    assert res.error  # 显式报红


def test_fetch_realtime_snapshot_http_fail_is_error(monkeypatch: pytest.MonkeyPatch):
    """HTTP 失败 → error 结果（治 99 #20：原新浪 403 反爬静默降级 112 件的根型）。"""

    def fake_get(url, timeout=30, headers=None, params=None):
        raise RuntimeError("HTTP 403 Forbidden")

    provider = AkshareIngestProvider()
    monkeypatch.setattr(provider, "_get_all_a_symbols", lambda ak, policy: ["600519"])
    monkeypatch.setattr(provider, "_http_get", fake_get)
    _fake_akshare_module(monkeypatch)
    results = list(provider._fetch_realtime_snapshot(_payload(), _policy()))
    res = results[0]
    assert res.rows == []
    assert "403" in res.error


@pytest.mark.skipif(os.environ.get("ZEPHYR_LIVE_QT") != "1", reason="真调烟测：仅 ZEPHYR_LIVE_QT=1 时运行")
@pytest.mark.filterwarnings("ignore::UserWarning")
def test_live_smoke_realtime_snapshot_tencent():
    """真调烟测（99 #20 验收留证）：6 只真实代码走 qt.gtimg.cn 实链路（只读）。"""
    provider = AkshareIngestProvider()
    monkey_codes = ["600519", "000001", "601318", "300750", "920002", "000333"]
    real_get = AkshareIngestProvider._http_get  # 真实 HTTP
    provider._get_all_a_symbols = lambda ak, policy: monkey_codes  # type: ignore[method-assign]
    results = list(provider._fetch_realtime_snapshot(_payload(), SourcePolicy(rpm=0, max_retries=1)))
    assert len(results) == 1
    res = results[0]
    assert res.error is None, f"真调失败: {res.error}"
    assert len(res.rows) >= 6, f"真调行数应 ≥6，实际 {len(res.rows)}"
