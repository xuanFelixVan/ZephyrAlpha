"""orderflow_features 一档特征件测试（st-infoaxis P2 做T首刀）。"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.signal_intraday.orderflow_features import Tick, compute_features  # noqa: E402


def _t(ts, p, b, a, bv, av):
    return Tick(timestamp=ts, price=p, bid_price=b, ask_price=a, bid_volume=bv, ask_volume=av)


def test_empty_and_single():
    f0 = compute_features([])
    assert f0.n_ticks == 0 and f0.ofi_sum is None
    f1 = compute_features([_t("09:30:00", 10.0, 9.99, 10.01, 100, 100)])
    assert f1.ofi_sum is None and f1.imbalance_last == 0.0
    assert abs(f1.micro_price - 10.0) < 1e-9  # 对称盘口公允价=中间价


def test_ofi_bid_buildup_positive():
    # 买方挂单增（价不落）→ 正 OFI
    ticks = [
        _t("09:30:00", 10.0, 9.99, 10.01, 100, 100),
        _t("09:30:03", 10.0, 9.99, 10.01, 200, 100),
        _t("09:30:06", 10.0, 9.99, 10.01, 300, 100),
    ]
    f = compute_features(ticks)
    assert f.ofi_sum == 200.0  # 两帧各 +100
    assert f.ofi_normalized is not None and f.ofi_normalized > 0


def test_ofi_price_fall_excluded():
    # bid 价下移时 Δbid_vol 不计（CKS 口径：价变动归价格项非量项）
    ticks = [
        _t("09:30:00", 10.0, 9.99, 10.01, 100, 100),
        _t("09:30:03", 10.0, 9.97, 10.01, 500, 100),
    ]
    f = compute_features(ticks)
    assert f.ofi_sum == 0.0


def test_imbalance_and_micro_price_skew():
    ticks = [_t("09:30:00", 10.0, 9.99, 10.01, 300, 100)]
    f = compute_features(ticks)
    assert abs(f.imbalance_last - 0.5) < 1e-9  # (300-100)/400
    assert f.micro_price is not None and f.micro_price > 10.0  # 重买盘公允价偏上（向 ask 靠拢）
    assert f.micro_price_offset_bps is not None and f.micro_price_offset_bps > 0


def test_zero_depth_guard():
    ticks = [_t("09:30:00", 10.0, 9.99, 10.01, 0, 0)]
    f = compute_features(ticks)
    assert f.imbalance_last is None and f.micro_price is None
