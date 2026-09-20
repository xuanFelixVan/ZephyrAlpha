---
ttl: task_bound
rule_form: data
verifiability: manual
title: Flash 包3——E7 涨跌停可成交性闸修复作业簿（_c4_engine 引擎洞）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-18
session: st-flashbiz-20260918
---

# 包3 · E7 引擎洞修复：_c4_engine 涨跌停可成交性闸

洞实证（lane E，e7_result.json）：向量化 T+1 无涨跌停闸——涨停封死收盘照常买入成交。
两笔真红：CAND-4440d07f973f 买 601162@2024-09-25（收盘=涨停 3.30）；CAND-e2e7f033d97c 买 000016@2025-04-10（收盘=涨停 4.64）。

## 1. 修复内容（scripts/backtest/translated/_c4_engine.py）

1. **`_load_seal_masks(index, columns)`**：封板掩码装载——raw close（kline_daily）vs limit_up/limit_down（stk_limit），**单位对齐原始价**（E7 假绿追加 §3 教训：hfq 直比涨停价=单位错配误报）；封板判定容差 1e-4（`close_raw >= limit_up*(1-1e-4)`，E7 探针同口径）；缺价/停牌/NULL 限制/非股票标的（ETF 等 stk_limit 无行）→ False 不闸（fail-open，不编造可成交性；原料查询故障同样 fail-open 放行）。
2. **`apply_fillability_gate(weights, gate_limits)`**：闸语义——向量化框架下 w_t 隐含成交价=close_t：目标权重较已执行权重**增加且当日封涨停 → 买单不可成交，已执行权重保持前值**；减少且封跌停 → 卖单不可成交同理；未封板日正常生效；等权不变（|Δ|≤1e-12 视为无交易）。
3. **`run_backtest` / `daily_net_returns` 增 `gate_limits: bool = True`**：默认开（修复生效全量消费方）；False=旧行为仅供反例对照。
4. 头部 INVARIANTS/TESTS 行同步更新（[TESTS] 增锚 test_c4_limit_gate.py）。

## 2. 反例测试（tests/backtest/test_c4_limit_gate.py，7 件全绿）

- `test_seal_masks_contain_real_counterexamples`（×2 真实反例）：掩码必须命中 601162@2024-09-25 与 000016@2025-04-10 封板（原始价口径、只读 CH）+ 阳性对照（掩码非全 True）+ 反例当日未同时封跌停。
- `test_gate_blocks_real_limit_up_buy`（×2）：**闸后两笔真实反例的买入目标权重必须不生效（=0）——这两笔已变红（被拦）**；gate_limits=False 必须复现旧行为（洞对照通道）。
- `test_gate_blocks_limit_down_sell_synthetic`：合成掩码测跌停禁卖（持仓被锁、次日未封板正常清仓）。
- `test_gate_failopen_on_missing_data`：无涨跌停数据标的（510300）不闸误伤。
- `test_gate_changes_backtest_output_real`：端到端真实反例窗口内闸开/关净收益路径可区分（防无鉴别力假绿）。

## 3. 验收记录

- 新测试：`pytest tests/backtest/test_c4_limit_gate.py` → **7 passed**（2026-09-18 02:1x）。
- 回归：test_c4_batch_smoke + test_c4_deflated_sharpe_runner + test_c4_auto_oos + test_c4_pit_universal_gate + test_f06_e4_wfa_exam → **58 passed, 1 xfailed**（E4 宇宙轴 xfail 钉保持原状，本修不动 PIT 宇宙轴——那是 S14 族另一处洞）。

## 4. 边界与诚实清单

1. 闸默认开启会轻微改变既有批考产物口径（被封板挡掉的成交不再计收益）——属修复性口径变更，非漂移；历史 verdict 行 append-only 保留。
2. fail-open 语义：闸原料不可得时不阻断回测（不伪装已闸）；stk_limit 不覆盖 ETF/可转债——这些品种无闸（如需另立品种闸登记）。
3. biz4 E4 考试（包4）即在本闸开启后的引擎上跑，登记对照三值全过（偏差在容差内）。
4. 级联语义：封板多日逐日保持前值，解锁日目标权重自然生效（无重试爆炸问题）。
