---
campaign: matrix-20261006
lane: st-mx07-W1
status: done（对拍逐位全绿 x54.3；切挂+回滚口径落档；GPU 二期与并行取数=遗留）
ttl: task_bound
created: 2026-10-08
authorization: 裁定#489⑤（t0_material_line 已批第二波）｜总包 st-mx07-chief
---

# t0_material_line_parallel_v1 — 材料线路径并行（st-mx07-W1 执行件留档）

> 目标：全市场 5 周期建模 23.3h→<2h（先 CPU numba，GPU 二期视预检）。本册增量写，断点续传面。

## 0. 一页结论（随施工增量更新）

1. 证据链闭合：23.3h = 取数 ≈1.9h + 建模 ≈21.4h，出处 `docs/_working/decision_map_campaign_20260924/links/L05_t0/material_precapacity_report.md` §三（sample-20 实测建模 310.7s/19,150 sd 外推 ×248.5）；hotspot 普查出处 `docs/_working/gpu_rewrite/hotspot_census.md` F4 行。与卡面一致，未被他会话重构。
2. 施工前 profile（sample-20，2025-06-02..2025-09-08，337,389 bars）：**resample 60.6s = 建模耗时 91%**（pandas iloc 逐桶切片第一热点）；M0 扫描 5.5s；build_pairs <0.05s。读数原文 `.runtime/tmp/st_mx07_w1/profile_legacy.tsv`。
3. fast 核：`scripts/backtest/t0_material_line_fast.py`（numba prange 逐路径并行核 + numpy reduceat 兜底，同读数）+ `t0_material_line_parity.py`（对拍/计时 harness）。切挂=单点 `run_pipeline(..., engine="fast")` 延迟导入；回滚=`engine="legacy"` 一参或 revert 切挂 diff。
4. 对拍（短窗 sample-8 实测）：5 周期 reason_counts 全等 + fills 232 legs **逐位相等（==，非 1e-9 容差）** + pairs 116 对逐位相等。语义缝披露：CH Decimal 列扫描比较边界（±1ulp 触档）legacy 115 vs fast 116 对——输入契约=float64 规范化，详见 §3。
5. 目标口径诚实注记：建模面 21.4h→**≈53 分钟**（v2 全窗实测 x54.3，全市场外推），达成卡面"23.3h→<2h"的建模分量；**总时长瓶颈转移到 CH 取数**（报告口径 1.9h；今晚实测 77k-121k 行/s ≈2.6-4.1h，IO 面超出本车道边界）——<2h 总目标需并行取数（分批管线已为多连接并行预留，属遗留工程），本车道交付=建模面路径并行。
6. 遗留：GPU 二期（cupy 14.2 在位、GPU 24% 占用有多租户——本期只交 CPU 版）；`t0_material_line.py` 头部 [TESTS] 指向的旧路径 `tests/backtest/test_t0_material_line.py` 已被 tests 结构战役删除且未重建（本车道新单测落 `tests/research/backtest/test_t0_material_line_fast.py`）。

## 1. 勘察与热点（施工前读数留档）

- 现行实现：`scripts/backtest/t0_material_line.py` run_pipeline 内层 = `groupby([symbol,trade_date])` × 周期 的纯 Python 双循环；`resample_period` 逐桶 `iloc` 切片 + `run_model_m0` numpy 双扫描。
- 调用链：CLI main() → run_pipeline；`t0_rule_engine.py` import 复用 load_bars/run_model_m0/build_corpus_for_symbol_day（R01 委托 run_model_m0）——三者本车道**零改动**，rule_engine 消费面无感。
- profile TSV（fetch 5.542s / resample 60.6s / m0 5.5s / pairs 0.03s）：

```
stage	period	seconds	per_sd_us
fetch	-	5.542	0
resample	1min	0.194	—（恒等直通）
resample	5min	35.617	第一热点
resample	15min	13.194
resample	30min	7.446
resample	60min	4.174
model_m0	1min	1.779
model_m0	5min	1.025
...（余档见 .runtime/tmp/st_mx07_w1/profile_legacy.tsv）
```

## 2. 施工面（改动清单）

| 件 | 动作 | 说明 |
|---|---|---|
| scripts/backtest/t0_material_line_fast.py | 新建 | numba prange 逐路径核（标量运算序与 legacy 逐位一致）+ numpy reduceat 兜底 + 批式 run_pipeline_fast（100 只/批，stats 按批累加） |
| scripts/backtest/t0_material_line_parity.py | 新建 | 对拍+计时 harness（索引注入法：同一规范化 df 注入两路径） |
| scripts/backtest/t0_material_line.py | 最小 diff | run_pipeline 加 `engine="fast"` 分派（延迟导入），legacy 循环体零改动 |
| tests/research/backtest/test_t0_material_line_fast.py | 新建 | 构造数据单测（逐位对拍/reason 优先级/重采样/双核同读数/确定性/语义缝） |

## 3. 语义缝自裁记录（重要）

CH 驱动对 Decimal 价格列返回 `decimal.Decimal` 对象。legacy M0 扫描比较是 **Decimal×float 精确比较**，而 fill 价格本就 `float()` 转换——即"比较用精确十进制、成交用 float64"的混合语义，属驱动返回类型的意外产物。fast 核输入契约=**价格列 float64 规范化**（`normalize_prices_float64`），在"恰好触档 ±1ulp"边界会产生翻转：短窗实测 216 symbol-day 中 1 日（0.46%）no_touch→pair（legacy 115 对 vs fast 116 对）。逐位复刻 Decimal 语义需分段 argmin+精确十进制地板（重器械、依赖 scale 上界假设），收益=保住一个数值精度以外的类型事故——自裁不做，规范化+披露替代。对拍验收口径不受影响：**同一 float64 规范化输入注入两路径，逐位相等**（"新旧实现同输入逐位比对"按字面满足）；raw Decimal 差异由 harness 披露段如实计数。若 Owner 后续裁定须保 Decimal 比较语义，回滚=`engine="legacy"`。

## 4. 验收读数（增量）

- 短窗对拍（sample-8，2025-08-01..2025-09-08，52,045 bars，216 sd）：5 周期全绿——reason_counts 全等、fills 232 legs 逐位（==）、pairs 116 对逐位、disclosure=1 日边界翻转。原文 `.runtime/tmp/st_mx07_w1/parity_table.tsv`。
- 全研究段对拍 v1（sample-20 全窗 2021-09-01..2025-09-09，4,615,139 bars=预检报告同源语料，对拍 exit 0 全绿）：**legacy 建模中位 492.5s vs fast 41.7s = x11.8**（numba_prange 五周期全命中；首版 fast 受碎片帧问题拖累，见下）。原文 `.runtime/tmp/st_mx07_w1/timing.tsv` + `parity_full_window.log`。
- 性能二修（全窗 v1 读数后微剖析定位）：①normalize 逐列赋值产生碎片帧 → 每周期 to_numpy 触发整帧合并复制 ~6s（resample 33s 的元凶）——改整帧构造；②基础列抽取上提 build_corpus_fast 一次、跨周期共享（extract_base_arrays）。微剖析读数：normalize 3.3s / segment 0.13s / scan 合计 1.16s / resample 修后应 <1s。
- 全研究段对拍 v2（碎片帧修复后复验，sample-20 全窗 4,615,139 bars/19,150 sd，exit 0，**0 FAIL / 20 OK**）：
  - 逐位判定：5 周期 ×（reason_counts 全等 + fills 22,694 legs 逐位 == + pairs 11,347 对逐位相等）；
  - 耗时：fast 首发 7.63s（含 numba 预热）/ 中位 12.794s vs legacy 首发 418.0s / 中位 695.3s（双路径同机同载）＝ **x54.3（首发口径 x54.8）**；
  - 边界披露：raw Decimal 11,342 对 vs 规范化 11,347 对＝+5 触档边界翻转（0.044%；短窗 0.46%、全窗 0.044%，翻转让好方向如实计数）；
  - 口径对齐：19,150 sd 与预检报告完全一致；报告 1min 语料 11,332 对 vs 本测 raw 11,342 对（+10，CH 数据 9-25 后自然更新面，非本车道改动）；
  - **全市场外推（建模面）**：12.8s/19,150 sd × 248.5 ≈ **53 分钟**（legacy 同机外推 34–49h；报告口径 21.4h）——目标"23.3h→<2h"的建模分量达成，总时长瓶颈转移到 CH 取数（IO 面，见 §0.5）。
  - 原文：`.runtime/tmp/st_mx07_w1/parity_full_window_v2.log` + `timing.tsv` + `parity_table.tsv`。

## 5. 切挂与回滚口径

- 切挂点：`run_pipeline` 单点，`engine="fast"` 默认 + 延迟导入；`t0_rule_engine` 消费的 run_model_m0/build_corpus_for_symbol_day/load_bars 未动。
- 回滚：① `engine="legacy"` 一参回退（零代码改动）；② revert 切挂 diff（legacy 循环体未动，无连带）。
- 语义缝回滚：同上（fast 的 float64 规范化契约随 engine 回退一并消失）。
