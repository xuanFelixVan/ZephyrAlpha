# [MODULE] zephyr.ex_core.daban_monitors
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] stdlib; numpy
# [CONSUMERS] （首批实盘接线前暂无）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] SaR>2%或latent+封单<50%→降仓50%; CUSUM>4σ→REDUCE(ENDOGENOUS); 方差压缩<60%→REDUCE(EXOGENOUS); PSI>0.25→STOP/>0.1→REDUCE; 分级响应OK→REDUCE→STOP
# [MODIFY-GUARD] 24_daban_strategy_detail.md §3.14 缺失#9（v1.9.3）/ §3.13 缺失#6（v1.9.2+v1.9.3 升级）
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空订单簿→depth=0 兜底（sar 放大→保守降仓，Fail-Closed）
# [TESTS] tests/ex_core/test_daban_monitors.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: position(qty) + order_book(bid_levels/ofi) + seal_data(current/initial)（持仓微结构监控）
# I2: win/premium/taker_bs_ratio_var（信号衰减监控逐笔输入）
# F1: HoldingPeriodMicrostructureMonitor.monitor——SaR 前瞻滑点 + OFI latent build-up + 封单持续监控→分级响应
# F2: SignalDecayMonitor.update——CUSUM(内生) + 方差压缩(外生) + PSI(分布漂移) 三检测器
# O1: {action: MONITOR/ALERT/REDUCE_50, reason} / {level: OK/REDUCE/STOP, type?, reason}
# [/ALGO_FLOW]
"""打板监控族（24_daban_strategy_detail §3.14#9 + §3.13#6 施工）。

缺失#9 HoldingPeriodMicrostructureMonitor（首批实盘前必做）：T 日封板后→
收盘的持仓期间持续监控+渐进降仓，与 §3.13#2 DabanInstantCircuitBreaker
互补——后者瞬时熔断，本类持续监控。理论背书：arXiv:2604.20949 latent
regime 三态 DGP + arXiv:2603.09164 SaR 前瞻性滑点。

缺失#6 SignalDecayMonitor（实盘后即需）：信号失效分级监控 OK→REDUCE→STOP。
v1.9.3 two-type classification：CUSUM 管内生型级联，方差压缩管外生型兜底
（arXiv:2607.27070——critical slowing down 仅 5/7 内生级联有效，方差压缩
跨 6/7 事件），PSI 管次日溢价分布漂移。

spec 转写偏差登记（两处伪代码死锁/缺失补全，语义不变）：
  ① 方差压缩检测器：spec 字面为"len(variance_window)>=30 才 append"（永远
     到不了 30，检测器死锁）。落码为先 append 再评估——符合 spec 检测意图。
  ② _compute_psi 伪代码未给实现：落码为 baseline_window 前半参考分布 vs
     后半当前分布，固定 5 箱（对齐 ±5%/0%/+3%/+6% 溢价决策阈值），eps=1e-4
     平滑。
  ③ CUSUM 公式逐字按 spec（x-mu-k·σ 累积，mu=0.55/σ=0.5）——对胜率上偏
     敏感，连败使 S 归零不触发（spec 原式语义锁定）。
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

import numpy as np

__all__ = [
    "HoldingPeriodMicrostructureMonitor",
    "SignalDecayMonitor",
]

#: PSI 固定分箱边界（对齐打板溢价决策阈值：闷杀-5%/平开0%/一档止盈+3%/二档止盈+6%）
_PSI_BINS = [-np.inf, -0.05, 0.0, 0.03, 0.06, np.inf]


@dataclass
class HoldingPeriodMicrostructureMonitor:
    """持仓期间微结构监控（v1.9.3 补，封板后→收盘持续监控+渐进降仓）。"""

    sar_threshold_alert: float = 0.01    # SaR>1% 预警
    sar_threshold_reduce: float = 0.02   # SaR>2% 降仓
    ofi_window: deque = field(default_factory=lambda: deque(maxlen=20))
    latent_buildup_detected: bool = False

    def monitor(self, position: dict, order_book: dict, seal_data: dict) -> dict:
        bid_levels = order_book.get('bid_levels', [])
        depth = sum(l['volume'] for l in bid_levels[:5])  # ① SaR 前瞻性滑点评估
        concentration = (max(l['volume'] for l in bid_levels) / max(depth, 1)) if bid_levels else 0.0
        sar = (position.get('qty', 0) / max(depth, 1)) * (1 + concentration) * 0.001
        ofi = order_book.get('ofi', 0)  # ② 订单流不平衡（OFI）latent build-up 检测
        self.ofi_window.append(ofi)
        if len(self.ofi_window) >= 10:
            ofi_trend = np.mean(list(self.ofi_window)[-5:]) - np.mean(list(self.ofi_window)[:-5])
            if ofi_trend < -0.3:  # OFI 持续下降=latent build-up
                self.latent_buildup_detected = True
        seal_ratio = seal_data.get('current', 0) / max(seal_data.get('initial', 1), 1)  # ③ 封单持续监控
        if sar > self.sar_threshold_reduce or (self.latent_buildup_detected and seal_ratio < 0.5):  # 分级响应
            return {'action': 'REDUCE_50', 'reason': f'SaR={sar:.3f}>2%或latent+封单<50%→降仓50%'}
        if sar > self.sar_threshold_alert or self.latent_buildup_detected:
            return {'action': 'ALERT', 'reason': f'SaR={sar:.3f}>1%或latent build-up→预警'}
        if seal_ratio < 0.7:
            return {'action': 'ALERT', 'reason': f'封单剩余{seal_ratio:.0%}<70%→监控'}
        return {'action': 'MONITOR', 'reason': '持仓微结构正常'}


@dataclass
class SignalDecayMonitor:
    """打板信号失效监控（v1.9.2 补 CUSUM+PSI，v1.9.3 升级 two-type+方差压缩）。分级响应：OK→REDUCE→STOP。"""

    cusum_k: float = 0.5       # 偏移容差（0.5σ）——内生型
    cusum_h: float = 4.0       # 触发阈值（4σ）
    cusum_S: float = 0.0       # 累积和
    psi_alert: float = 0.1     # 轻微漂移
    psi_critical: float = 0.25 # 严重漂移
    variance_compression_threshold: float = 0.6  # v1.9.3 新增：方差压缩至历史 60% 触发预警（外生型兜底）
    variance_window: deque = field(default_factory=lambda: deque(maxlen=60))
    baseline_window: deque = field(default_factory=lambda: deque(maxlen=30))
    cascade_type: str = 'UNKNOWN'  # v1.9.3 新增：two-type classification——ENDOGENOUS / EXOGENOUS / UNKNOWN

    def update(self, win: bool, premium: float, taker_bs_ratio_var: float = None) -> dict:
        self.baseline_window.append(premium)
        mu, sigma = 0.55, 0.5
        self.cusum_S = max(0, self.cusum_S + ((1.0 if win else 0.0) - mu - self.cusum_k * sigma))  # CUSUM：监控胜率累积偏移（内生型）
        if self.cusum_S > self.cusum_h * sigma:
            self.cascade_type = 'ENDOGENOUS'
            return {'level': 'REDUCE', 'type': 'ENDOGENOUS', 'reason': f'CUSUM={self.cusum_S / sigma:.1f}σ>4σ→仓位减半'}
        if taker_bs_ratio_var is not None:  # v1.9.3 新增：方差压缩检测器（外生型兜底，跨 6/7 事件）
            self.variance_window.append(taker_bs_ratio_var)  # spec 死锁修正：先累积样本再评估（原式 len>=30 才 append 永远不触发）
            if len(self.variance_window) >= 30:
                hist_var = np.var(list(self.variance_window)[:-10])
                curr_var = np.var(list(self.variance_window)[-10:])
                if curr_var < hist_var * self.variance_compression_threshold:
                    self.cascade_type = 'EXOGENOUS'
                    return {'level': 'REDUCE', 'type': 'EXOGENOUS',
                            'reason': f'方差压缩{curr_var / hist_var:.0%}<60%→外生冲击预警+仓位减半'}
        if len(self.baseline_window) >= 30:  # PSI：监控次日溢价分布漂移
            psi = self._compute_psi()
            if psi > self.psi_critical:
                return {'level': 'STOP', 'reason': f'PSI={psi:.2f}>0.25→停止打板+重新校准'}
            elif psi > self.psi_alert:
                return {'level': 'REDUCE', 'reason': f'PSI={psi:.2f}>0.1→仓位减半'}
        return {'level': 'OK', 'reason': '信号质量正常'}

    def _compute_psi(self) -> float:
        """PSI 人口稳定性指数：baseline_window 前半=参考分布，后半=当前分布，
        固定 5 箱（_PSI_BINS），PSI=Σ(cur%-ref%)·ln(cur%/ref%)，eps=1e-4 平滑防除零。"""
        samples = list(self.baseline_window)
        half = len(samples) // 2
        ref, cur = samples[:half], samples[half:]
        if not ref or not cur:
            return 0.0
        eps = 1e-4
        ref_pct = np.clip(np.histogram(ref, bins=_PSI_BINS)[0] / len(ref), eps, None)
        cur_pct = np.clip(np.histogram(cur, bins=_PSI_BINS)[0] / len(cur), eps, None)
        return float(np.sum((cur_pct - ref_pct) * np.log(cur_pct / ref_pct)))
