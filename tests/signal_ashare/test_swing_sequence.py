# [TESTS] tests/signal_ashare/test_swing_sequence.py
# [TTL] permanent
# 波10 G-C.2（MOD-SIG-147）摆动序列单测。
#
# C253 dossier_institution 采纳——镜像测试三纪律（StatOasis 证据链，本套件落地）：
#   纪律①镜像测试：判据与其反面必须同测——LH 用例必配 HH/LL 镜像用例，
#     序列取反（高低互换+价格翻转）后顶底标注须对称成立；"只有单方向成立"
#     的判据是噪声不是结构。
#   纪律②最小样本门槛：样本不足（<2 个同向摆动点）不产标注不造序列，
#     显式空降级（对应 StatOasis"过滤后信号<15% 即弃用"的诚实读数立场）。
#   纪律③全网格一致性：容差边界用例必须成网格测（容差内/EQ、容差外/LH、
#     容差外/HH 三态都要有）——"只在单一阈值有效的判据是参数不是判据"。

import pytest

from zephyr.signal_ashare.swing_sequence import (
    REL_EQ,
    REL_HH,
    REL_HL,
    REL_LH,
    REL_LL,
    SWING_HIGH,
    SWING_LOW,
    DoublePeak,
    SwingConfig,
    detect_swing_sequence,
)

# 系列注：chanlun 分型为严格三 K 判据（高与低同向越界）+ 包含处理，
# 用例序列均为手工验证的锯齿形（每顶/底邻根在高低两维同向回落）。


class TestDetection:
    def test_labels_lh_then_hl(self):
        # 顶: 11.0→11.5(HH)→11.05(LH)；底: 9.0→9.9(HL)
        highs = [10.0, 11.0, 10.2, 11.5, 10.5, 11.05, 10.3]
        lows = [9.8, 10.5, 9.0, 10.8, 9.9, 10.0, 8.9]
        seq = detect_swing_sequence(highs, lows)
        assert seq.n_fractals >= 4
        hrels = [lb.relation for lb in seq.high_labels]
        lrels = [lb.relation for lb in seq.low_labels]
        assert REL_LH in hrels and REL_HL in lrels

    def test_hh_ll_mirror_directions(self):
        # 顶逐级抬高(HH)，底逐级走低(LL)
        highs = [10.0, 11.0, 10.2, 11.5, 10.6, 11.8, 10.9]
        lows = [9.2, 10.3, 9.5, 10.6, 9.0, 10.0, 8.8]
        seq = detect_swing_sequence(highs, lows)
        hrels = [lb.relation for lb in seq.high_labels]
        lrels = [lb.relation for lb in seq.low_labels]
        assert hrels == [REL_HH, REL_HH]
        assert lrels == [REL_LL]

    def test_anchors_point_to_original_bars(self):
        # 锚点回指原始 K 下标（chanlun 透传）
        highs = [10.0, 11.0, 10.2, 11.5, 10.5, 11.05, 10.3]
        lows = [9.8, 10.5, 9.0, 10.8, 9.9, 10.0, 8.9]
        seq = detect_swing_sequence(highs, lows)
        for p in (*seq.highs, *seq.lows):
            assert 0 <= p.anchor_idx < len(highs)

    def test_double_peak_eq_within_tolerance(self):
        # 双顶：11.0 与 11.02 价差 ≈0.18% ≤ 0.3% 容差 → EQ 双峰
        highs = [10.5, 11.0, 10.5, 11.02, 10.5]
        lows = [9.9, 10.2, 9.9, 10.2, 9.9]
        seq = detect_swing_sequence(highs, lows)
        dp = seq.last_double_peak
        assert isinstance(dp, DoublePeak)
        assert dp.kind == SWING_HIGH
        assert dp.is_equal_within_tolerance is True

    def test_double_peak_beyond_tolerance_not_eq(self):
        # 两顶差 ≈3.6% > 0.3% → 非并列（已分出 LH/HH）
        highs = [10.5, 11.0, 10.5, 11.4, 10.5]
        lows = [9.9, 10.2, 9.9, 10.2, 9.9]
        seq = detect_swing_sequence(highs, lows)
        dp = seq.last_double_peak
        assert dp is not None
        assert dp.kind == SWING_HIGH
        assert dp.is_equal_within_tolerance is False

    def test_double_peak_low_fallback(self):
        # 顶序列仅 1 点（<2 不成双峰）、底序列双点 → 双峰回落取底序列（kind=low）
        highs = [9.5, 9.0, 9.6, 9.1, 9.7]
        lows = [8.8, 8.2, 8.4, 8.0, 8.1]
        seq = detect_swing_sequence(highs, lows)
        assert len(seq.highs) == 1
        assert len(seq.lows) == 2
        dp = seq.last_double_peak
        assert dp is not None and dp.kind == SWING_LOW

    def test_min_sample_gate_no_labels(self):
        # 纪律②最小样本门槛：单边无回撤序列 0 分型 → 标注空、双峰 None（不造序列）
        seq = detect_swing_sequence([10.0, 10.2, 10.4, 10.6, 10.8], [9.8, 10.0, 10.2, 10.4, 10.6])
        assert seq.n_fractals == 0
        assert seq.high_labels == () and seq.low_labels == ()
        assert seq.last_double_peak is None


class TestMirrorDiscipline:
    def test_discipline1_full_mirror_symmetry(self):
        # 纪律①：序列取反（高低互换+价格翻转）后，顶标注镜像=底标注
        highs = [10.0, 11.0, 10.2, 11.5, 10.6, 11.8, 10.9]
        lows = [9.2, 10.3, 9.5, 10.6, 9.0, 10.0, 8.8]
        seq_fwd = detect_swing_sequence(highs, lows)
        seq_rev = detect_swing_sequence([20.0 - lo for lo in lows], [20.0 - hi for hi in highs])
        fwd_h = [lb.relation for lb in seq_fwd.high_labels]
        rev_l = [lb.relation for lb in seq_rev.low_labels]
        fwd_l = [lb.relation for lb in seq_fwd.low_labels]
        rev_h = [lb.relation for lb in seq_rev.high_labels]
        mirror = {"LH": "HL", "HH": "LL", "HL": "LH", "LL": "HH", "EQ": "EQ"}
        assert fwd_h == [mirror[r] for r in rev_l]
        assert fwd_l == [mirror[r] for r in rev_h]

    def test_discipline3_tolerance_grid(self):
        # 纪律③容差网格：同一对顶在紧/宽两档容差下 EQ 态可辨（0.18% 价差）
        highs = [10.5, 11.0, 10.5, 11.02, 10.5]
        lows = [9.9, 10.2, 9.9, 10.2, 9.9]
        tight = detect_swing_sequence(highs, lows, SwingConfig(tolerance_pct=0.05))
        wide = detect_swing_sequence(highs, lows, SwingConfig(tolerance_pct=0.5))
        assert tight.last_double_peak.is_equal_within_tolerance is False  # 容差外
        assert wide.last_double_peak.is_equal_within_tolerance is True  # 容差内=EQ
        # 默认档（0.3%）与宽档同态
        default = detect_swing_sequence(highs, lows)
        assert default.last_double_peak.is_equal_within_tolerance is True
        assert REL_EQ  # 常量在册（EQ=容差内并列语义锚）


class TestConfigAndFailClosed:
    def test_config_validation(self):
        with pytest.raises(ValueError):
            SwingConfig(tolerance_pct=-0.1)
        with pytest.raises(ValueError):
            SwingConfig(min_bars=3)

    def test_fail_closed_passthrough(self):
        # chanlun 校验透传：根数不足 / 序列不等长 → ValueError
        with pytest.raises(ValueError):
            detect_swing_sequence([10.0, 11.0], [9.8])
        with pytest.raises(ValueError):
            detect_swing_sequence([10.0, 11.0, 10.5], [9.8, 10.0])

    def test_json_serializable(self):
        highs = [10.0, 11.0, 10.2, 11.5, 10.5, 11.05, 10.3]
        lows = [9.8, 10.5, 9.0, 10.8, 9.9, 10.0, 8.9]
        seq = detect_swing_sequence(highs, lows)
        d = seq.to_dict()
        assert isinstance(d, dict) and d["n_fractals"] == seq.n_fractals
