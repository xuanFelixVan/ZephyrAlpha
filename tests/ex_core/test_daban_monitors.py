# [A_test] module_id: MOD-EXE-daban_monitors_test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.ex_core.test_daban_monitors
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""打板监控族单元测试（§3.14 缺失#9 HoldingPeriodMicrostructureMonitor / §3.13 缺失#6 SignalDecayMonitor）。

覆盖：
  - HoldingPeriod：SaR>2% 降仓 / SaR>1% 预警 / latent build-up（OFI 持续下降）/
    latent+封单<50% 降仓 / 封单<70% 监控预警 / 正常 MONITOR / 空订单簿退化
  - SignalDecay：CUSUM 越 4σ（spec 原式连胜累积）→ENDOGENOUS REDUCE /
    方差压缩<60%→EXOGENOUS REDUCE / PSI>0.25→STOP / PSI>0.1→REDUCE / 正常 OK /
    样本不足不触发

依据：24_daban_strategy_detail.md v1.9.3 §3.14 缺失#9 / v1.9.2+v1.9.3 §3.13 缺失#6
"""

from __future__ import annotations

from zephyr.ex_core.daban_monitors import (
    HoldingPeriodMicrostructureMonitor,
    SignalDecayMonitor,
)

# ---------------------------------------------------------------------
# HoldingPeriodMicrostructureMonitor（§3.14#9）
# ---------------------------------------------------------------------


def _order_book(volumes, ofi=0.0):
    return {'bid_levels': [{'volume': v} for v in volumes], 'ofi': ofi}


class TestHoldingPeriodMonitor:
    def test_normal_monitor(self):
        """深盘口+小持仓+封单 90%→MONITOR。"""
        m = HoldingPeriodMicrostructureMonitor()
        out = m.monitor({'qty': 100}, _order_book([50000, 40000, 30000, 20000, 10000]), {'current': 9000, 'initial': 10000})
        assert out['action'] == 'MONITOR'

    def test_sar_reduce(self):
        """持仓相对深度过大→SaR>2%→REDUCE_50。

        depth=150000, concentration=50000/150000=1/3, qty=50000：
        sar = (50000/150000)*(1+1/3)*0.001 = 0.3333*1.3333*0.001 ≈ 0.00044 → 太小。
        需 qty/depth>15：qty=4_000_000/depth=150_000 → sar=(26.67)*(1.333)*0.001≈0.0356>0.02。
        """
        m = HoldingPeriodMicrostructureMonitor()
        out = m.monitor({'qty': 4_000_000}, _order_book([50000, 40000, 30000, 20000, 10000]), {'current': 9000, 'initial': 10000})
        assert out['action'] == 'REDUCE_50'
        assert 'SaR' in out['reason']

    def test_sar_alert_band(self):
        """SaR 落在 (1%, 2%]→ALERT。qty=1_600_000/depth=150_000→sar≈0.0142。"""
        m = HoldingPeriodMicrostructureMonitor()
        out = m.monitor({'qty': 1_600_000}, _order_book([50000, 40000, 30000, 20000, 10000]), {'current': 9000, 'initial': 10000})
        assert out['action'] == 'ALERT'
        assert 'SaR' in out['reason']

    def test_seal_below_70pct_alert(self):
        """封单剩余<70%→ALERT 监控。"""
        m = HoldingPeriodMicrostructureMonitor()
        out = m.monitor({'qty': 100}, _order_book([50000, 40000, 30000, 20000, 10000]), {'current': 6000, 'initial': 10000})
        assert out['action'] == 'ALERT'
        assert '封单剩余' in out['reason']

    def test_latent_buildup_alert(self):
        """OFI 持续下降（趋势<-0.3）→latent build-up→ALERT。"""
        m = HoldingPeriodMicrostructureMonitor()
        book = _order_book([50000, 40000, 30000, 20000, 10000])
        seal = {'current': 9000, 'initial': 10000}
        for ofi in [0.5, 0.5, 0.5, 0.5, 0.5, -0.5, -0.5, -0.5, -0.5, -0.5]:
            book['ofi'] = ofi
            out = m.monitor({'qty': 100}, book, seal)
        assert m.latent_buildup_detected is True
        assert out['action'] == 'ALERT'
        assert 'latent' in out['reason']

    def test_latent_plus_seal_below_50_reduce(self):
        """latent build-up + 封单<50%→REDUCE_50。"""
        m = HoldingPeriodMicrostructureMonitor()
        book = _order_book([50000, 40000, 30000, 20000, 10000])
        for ofi in [0.5, 0.5, 0.5, 0.5, 0.5, -0.5, -0.5, -0.5, -0.5, -0.5]:
            book['ofi'] = ofi
            out = m.monitor({'qty': 100}, book, {'current': 4000, 'initial': 10000})
        assert out['action'] == 'REDUCE_50'

    def test_degenerate_empty_order_book(self):
        """退化：空订单簿→depth=0 兜底不崩（sar 放大→保守 REDUCE_50，Fail-Closed）。"""
        m = HoldingPeriodMicrostructureMonitor()
        out = m.monitor({'qty': 100}, {}, {'current': 9000, 'initial': 10000})
        assert out['action'] == 'REDUCE_50'

    def test_degenerate_seal_initial_zero(self):
        """退化：seal initial=0→max(,1) 兜底不除零。"""
        m = HoldingPeriodMicrostructureMonitor()
        out = m.monitor({'qty': 100}, _order_book([50000, 40000, 30000, 20000, 10000]), {'current': 0, 'initial': 0})
        assert out['action'] == 'ALERT'  # seal_ratio=0<0.7

    def test_ofi_window_less_than_10_no_trend(self):
        """OFI 窗口<10 不做趋势判定→正常 MONITOR。"""
        m = HoldingPeriodMicrostructureMonitor()
        book = _order_book([50000, 40000, 30000, 20000, 10000], ofi=-5.0)
        out = m.monitor({'qty': 100}, book, {'current': 9000, 'initial': 10000})
        assert m.latent_buildup_detected is False
        assert out['action'] == 'MONITOR'


# ---------------------------------------------------------------------
# SignalDecayMonitor（§3.13#6）
# ---------------------------------------------------------------------


class TestSignalDecayMonitor:
    def test_ok_normal(self):
        """交替胜负+平稳溢价→OK。"""
        m = SignalDecayMonitor()
        for i in range(10):
            out = m.update(win=(i % 2 == 0), premium=0.02)
        assert out['level'] == 'OK'

    def test_cusum_endogenous_reduce(self):
        """CUSUM 越 4σ（spec 原式：win 步进 +0.2，连胜 11 场 S=2.2>2.0）→ENDOGENOUS REDUCE。"""
        m = SignalDecayMonitor()
        out = None
        for _ in range(11):
            out = m.update(win=True, premium=0.02)
        assert out['level'] == 'REDUCE'
        assert out['type'] == 'ENDOGENOUS'
        assert m.cascade_type == 'ENDOGENOUS'

    def test_cusum_losing_streak_not_trigger(self):
        """连败使 S 归零（步进 -0.8）→不触发 CUSUM（spec 原式语义锁定）。"""
        m = SignalDecayMonitor()
        for _ in range(15):
            out = m.update(win=False, premium=0.02)
        assert m.cusum_S == 0.0
        assert out['level'] == 'OK'

    def test_variance_compression_exogenous(self):
        """taker 买卖比方差压缩至历史 60% 以下→EXOGENOUS REDUCE。"""
        m = SignalDecayMonitor()
        out = None
        # 前 25 个样本高波动（0.5/1.5 交替，方差 0.25），胜负交替保持 CUSUM=0
        for i in range(25):
            out = m.update(win=(i % 2 == 0), premium=0.02, taker_bs_ratio_var=0.5 if i % 2 == 0 else 1.5)
            assert out['level'] == 'OK'
        # 后 10 个样本恒定 1.0（方差 0）→curr_var=0 < hist_var*0.6
        for i in range(10):
            out = m.update(win=(i % 2 == 0), premium=0.02, taker_bs_ratio_var=1.0)
        assert out['level'] == 'REDUCE'
        assert out['type'] == 'EXOGENOUS'
        assert m.cascade_type == 'EXOGENOUS'

    def test_psi_stop(self):
        """溢价分布剧烈漂移（0.01→0.08）→PSI>0.25→STOP。"""
        m = SignalDecayMonitor()
        out = None
        for i in range(30):
            premium = 0.01 if i < 15 else 0.08
            out = m.update(win=(i % 2 == 0), premium=premium)
        assert out['level'] == 'STOP'
        assert '重新校准' in out['reason']

    def test_psi_alert_reduce(self):
        """溢价分布轻度漂移→0.1<PSI<0.25→REDUCE。

        前半 12×0.01+3×0.04（ref 箱比 0.8/0.2），后半 9×0.01+6×0.04（cur 0.6/0.4）
        →PSI≈0.196。
        """
        m = SignalDecayMonitor()
        out = None
        premiums = [0.01] * 12 + [0.04] * 3 + [0.01] * 9 + [0.04] * 6
        for i, p in enumerate(premiums):
            out = m.update(win=(i % 2 == 0), premium=p)
        assert out['level'] == 'REDUCE'
        assert 'PSI' in out['reason']

    def test_psi_insufficient_samples_not_evaluated(self):
        """baseline_window<30→PSI 不评估→OK。"""
        m = SignalDecayMonitor()
        for i in range(29):
            premium = 0.01 if i < 15 else 0.08  # 分布漂移但样本不足
            out = m.update(win=(i % 2 == 0), premium=premium)
        assert out['level'] == 'OK'

    def test_variance_window_less_than_30_not_evaluated(self):
        """方差窗口<30→压缩检测不评估。"""
        m = SignalDecayMonitor()
        for i in range(29):
            out = m.update(win=(i % 2 == 0), premium=0.02, taker_bs_ratio_var=1.0)
        assert out['level'] == 'OK'
        assert m.cascade_type == 'UNKNOWN'
