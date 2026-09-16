# [BLUEPRINT] MOD-SOWNER-001 | docs/03_modules/_domain_ashare_signal/blueprint.md
# [MODULE] zephyr.strategy_factory.owner_band_t.td_sequence
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] pandas
# [CONSUMERS] zephyr.strategy_factory.owner_band_t.signals; zephyr.strategy_factory.owner_band_t.engine; tests/strategy_factory/test_s_owner_001_td_sequence.py
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 纯函数无 I/O；只用 ≤i 期数据（无未来函数，close[i-4]/low[i-2] 均为历史位移）；计数语义与卡面冻结口径一致
# [MODIFY-GUARD] 语义变更=考试冻结口径变更，冻结期禁改
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError(输入长度不一致)
# [TESTS] tests/strategy_factory/test_s_owner_001_td_sequence.py
# [A_module] module_id=MOD-SOWNER-001 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""TD 序列（DeMark TD Sequential）自实现——Buy Setup / Buy Countdown / TD 极值。

口径（与 E4 冻结文档 §3 一致）：
  * Buy Setup: 连续 close[i] < close[i-4] 计数，中断即归零；计满 9 视为 setup 完成。
  * Buy Countdown: setup 完成后启动，close[i] <= low[i-2] 非连续计数至 13；
    中断条件=出现完整 Sell Setup（连续 9 根 close[i] > close[i-4]）或新 Buy Setup 完成。
  * TD 极值: 当日 low <= 本轮 setup+countdown 阶段已出现的最低 low（底部耗竭信号）。
  * "计数值<0" 入场口径的落地: countdown 进行中 c-13<0 且 c>=8（即 8<=c<=12）。

纯 pandas 实现，主循环一遍 O(n)，零新依赖。
"""

from __future__ import annotations

import pandas as pd

SETUP_THRESHOLD = 9
COUNTDOWN_THRESHOLD = 13
SETUP_LOOKBACK = 4
COUNTDOWN_LOOKBACK = 2


def td_sequential(close: pd.Series, low: pd.Series) -> pd.DataFrame:
    """计算 TD Buy Setup/Countdown/极值。

    :param close: 日收盘（升序索引）
    :param low: 日最低（与 close 同索引）
    :return: DataFrame[setup_count, setup_id, countdown_count, exhaustion]
        setup_count: 当日连续 close<close[4] 计数（1..9，中断归零）
        setup_id:    当前所属（或刚完成的）setup 轮次编号（0 起，前 LOOKBACK 期=nan）
        countdown_count: 本轮 countdown 已计数（0..13）
        exhaustion:  当日 low<=阶段最低 low（bool）
    """
    if len(close) != len(low):
        raise ValueError(f"close/low 长度不一致: {len(close)} vs {len(low)}")
    n = len(close)
    c = close.to_numpy(dtype=float)
    l = low.to_numpy(dtype=float)
    setup_count = [0] * n
    setup_id = [float("nan")] * n
    countdown_count = [0] * n
    exhaustion = [False] * n

    sid = -1
    cur_setup = 0
    phase_done = False  # setup 已计满、countdown 阶段进行中
    pending_cd = False  # setup 恰在上一根 bar 完成（countdown 自次根起计）
    countdown = 0
    phase_low = float("inf")  # 本轮 setup+countdown 阶段最低 low
    sell_run = 0  # 连续 close>close[4] 计数（Sell Setup 中断判据）

    for i in range(n):
        if i < SETUP_LOOKBACK:
            setup_count[i] = 0
            continue
        up = c[i] > c[i - SETUP_LOOKBACK]
        down = c[i] < c[i - SETUP_LOOKBACK]
        # Sell Setup 连续计数（仅作 countdown 中断判据）
        sell_run = sell_run + 1 if up else 0

        # 上一根 bar 完成 setup → 本根起进入 countdown 阶段
        if pending_cd:
            phase_done = True
            pending_cd = False

        # --- Buy Setup 计数（countdown 阶段内不重启；封顶 9）---
        if down:
            if not phase_done:
                cur_setup += 1
                if cur_setup == 1:
                    sid += 1
                    phase_low = float("inf")  # 新阶段：极值基线清零
                    countdown = 0
                cur_setup = min(cur_setup, SETUP_THRESHOLD)
                if cur_setup >= SETUP_THRESHOLD:
                    pending_cd = True  # 次根起计 countdown
            # phase_done 中: 保持显示 9（setup 轮进行中），不重启
        else:
            cur_setup = 0

        # --- Buy Countdown（phase_done 且非 setup 完成当根；非连续计数）---
        if phase_done and not pending_cd:
            if sell_run >= SETUP_THRESHOLD:
                phase_done = False  # Sell Setup 完成，countdown 作废
                countdown = 0
            elif c[i] <= l[i - COUNTDOWN_LOOKBACK]:
                countdown = min(countdown + 1, COUNTDOWN_THRESHOLD)

        # --- TD 极值: 当日 low 创阶段（不含当日）新低 ---
        in_phase = cur_setup > 0 or phase_done
        if in_phase:
            exhaustion[i] = phase_low < float("inf") and l[i] <= phase_low
            phase_low = min(phase_low, l[i])

        setup_count[i] = cur_setup
        setup_id[i] = float(sid) if in_phase else float("nan")
        countdown_count[i] = countdown if (phase_done or countdown > 0) else 0

    return pd.DataFrame(
        {
            "setup_count": setup_count,
            "setup_id": setup_id,
            "countdown_count": countdown_count,
            "exhaustion": exhaustion,
        },
        index=close.index,
    )
