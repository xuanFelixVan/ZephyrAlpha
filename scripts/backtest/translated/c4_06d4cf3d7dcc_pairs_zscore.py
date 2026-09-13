# [BLUEPRINT] MOD-BT-060 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_06d4cf3d7dcc_pairs_zscore
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_config; numpy; pandas
# [CONSUMERS] C4 快筛批测（scripts/backtest/c4_batch_screen.py）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] PIT（T 日执行用 ≤T-1 信号）；成本=冻结土规
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)
# [TESTS] tests/backtest/test_c4_batch_smoke.py
# [A_module] module_id=MOD-BT-060 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 060: 双股价差 zscore 轮动（原文: 2020年度精选策略/02 我好像破解了聚宽擂台排第一的策略）。

原文逻辑: 固定配对 600887（伊利）×600036（招行），回归比 1.0；价差序列
  spread=close2-1.0×close1 的 120 日 z-score；z>1 → 全仓标的2，z<-1 → 全仓标的1，
  |z|<=1 → 若 z>=0 维持标的1 方向（原文 get_signal 对 side1 返回后 change_positions 保守持有）。
译文实现: 逐日 zscore 状态机（持有方=单标的全仓，信号 T-1 确认 T 收盘执行）；
  z 进入 [-1,1] 区间时维持原方向（原文语义：无新信号不换仓）。
因子拆解: 价差 zscore（配对平稳性）——统计价差，非 factor_registry 因子。
翻译差异声明:
  D1 标的: 固定两标的与原文一致
  D2 执行时点: 原文 handle_data 当日 → T 日收盘（引擎 T+1 起算收益）
  D3 状态语义: 原文 side1/side2 中间态的换仓细节按"无新信号维持"实现（原文 change_positions
     对 side1 不调仓的保守读法）
  D4 因子登记: 价差 zscore 不入 factor_registry
  D5 框架样板: 状态打印壳不翻译

[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-12 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

from _c4_engine import emit, load_px, run_backtest, wide

logger = logging.getLogger(__name__)

STRATEGY_ID = "CAND-06d4cf3d7dcc"
WINDOW_KIND = "stock"
_S1, _S2, _WIN, _RATIO = "600887", "600036", 120, 1.0


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=int(_WIN * 1.6)))[:10]
    px = load_px(load_start, end, fields=("close",))
    closes = wide(px)
    syms = [s for s in (_S1, _S2) if s in closes.columns]
    closes = closes[syms]
    spread = closes[_S2] - _RATIO * closes[_S1]
    z = (spread - spread.rolling(_WIN).mean()) / spread.rolling(_WIN).std()
    dates = closes.index[(closes.index >= pd.Timestamp(start)) & (closes.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=closes.columns)
    pos = ""  # '', S1, S2
    for dt in dates:
        zc = z.shift(1).loc[dt]
        if pd.notna(zc):
            if zc > 1:
                pos = _S2
            elif zc < -1:
                pos = _S1
            elif -1 <= zc <= 1 and zc >= 0 and pos == "":
                pos = _S1
        if pos:
            weights.loc[dt, pos] = 1.0
    return weights, closes


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 固定配对", "D2 收盘口径", "D3 中间态保守读法",
                                               "D4 价差不入库", "D5 壳不译"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
