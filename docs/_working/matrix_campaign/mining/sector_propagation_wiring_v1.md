---
ttl: task_bound
campaign: mx07-W5
status: in_progress
---

# W5 施工留档：板块传导后处理（L2-06）+ 板块强度四路接线（L2-01）

- 车道: st-mx07-W5 | 日期: 2026-10-08 | 性质: C 道规格卡照卡施工（M-2+M-3）
- 施工队列锚: `docs/_working/matrix_campaign/construction_queue_v1.yaml:28-29`
  （M-2=L2 板块传导后处理 one-hot×查表 / M-3=L2-01 板块强度四路子分，均小模块）

## 1. 勘察结论（先勘察后动工，2026-10-08 12:51-13:10）

### 1.1 规格真源（file:line）
- **C 道规格卡**:
  - `docs/_working/matrix_campaign/mining/m2_exit_sector/spec_l2_TDM-E-L2-06_conduction.md`（传导，M 级）
  - `docs/_working/matrix_campaign/mining/m2_exit_sector/spec_l2_TDM-E-L2-01_strength.md`（强度四路，M 级）
  - 总索引: `docs/_working/matrix_campaign/mining/m2_exit_sector/00_exit_sector_index.md`（42 节点，
    "最快落地"第 3/5 位即 L2-06/L2-01）
- **TDM 真源**: `config/trading_decision_map.yaml`
  - `TDM-E-L2-01`:696 板块强度综合（实现锚=MOD-SIG-142 sector_strength_aggregator，等权 0.25×4）
  - 四路清单（§1 规格卡+TDM 子节点，**不自拟**）:
    - `TDM-E-L2-01-1`:732 结构强度（涨停比/梯队/趋势，0-10）
    - `TDM-E-L2-01-2`:765 动量活跃度排名（成交额占比+环比，保符号）
    - `TDM-E-L2-01-3`:797 多周期动量加权（q3/q5/q20=0.2/0.3/0.5）
    - `TDM-E-L2-01-4`:828 板块资金流（3 日累计+当日大单；缺→降权归一标 degraded）
  - `TDM-E-L2-06`:1243 板块个股传导（只传强度调节分+龙头定位，只调分不重排名）
  - `TDM-E-L2-06-1`:1273 三级放行（板块>6 ∧ 个股>5 ∧ 额>2 亿）；`-06-3`:1337 强度加权（10→+15%/6→+5%/<6→-10%）

### 1.2 在库件现状（勿重复造轮）
- **MOD-SIG-142** `src/zephyr/signal_ashare/core/sector_strength_aggregator.py`（design）:
  四路合分核已在（纯函数，子分由调用方注入）；头注 CONSUMERS 明示
  "TDM-E-L2-06 传导（强度调节分上游，**待接线**）/ L3 候选池消费（**待接线**）"。
- **MOD-SIG-144** `src/zephyr/signal_ashare/core/sector_strength_wiring.py`（production）:
  日频报告→四维跨截面排名归一→142 合分的**生产接线**已在（走 sector_report_builder JSON）。
- **MOD-SIG-136** `src/zephyr/signal_ashare/core/sector_conduction.py`（design）:
  传导系数核已在（三锚点+6→10 线性插值变体）；头注明示 "G05 打分池（**待接线**）"。
- **缺口判定**: 缺的是**回测引擎侧**接线——规格卡 L2-01 §4 明示
  `scripts/backtest/sector_surface.py`（新件）+ executor 新增模块维 `X_sector`；
  L2-06 §4 明示 evaluate_recipe 在 A1/A2 后、B Top-N 前插入传导后处理段。
  此即本车道施工面（引擎考卷语义），生产接线（144）不在本卡范围不动。

### 1.3 他班在途核查（不抹他班成果，不重做）
- st-tdm20 W4（62bef2a8da3）: `_apply_industry_topk_overlay`（行业动量 Top-K 两层排序）
  已在 executor:1107 ——系挖矿 M3"最简版"，与 L2-01 四路子分是**两物**（其自身卡注明
  "本卡即 M3 完整化"），不冲突不重做；本批不触碰该函数。
- st-fcd-merge/sector_line 系（d553b160ebe 等）: GPU 输入包/冻结基线（scripts/sector_line/），
  数据管线非引擎接线，零交集。
- st-mx07-L5: internal_compute_provider 指标链物化，与 executor X 族 overlay 面无交叠。
- schema X_stop/X_breaker（T3b 20261007 袋B）已落：`X_sector` 沿同款先例
  （baseline 'off' + active_if "phase >= 3" 折叠相零漂移）。
- 工作区 sector_* blueprint.md 多个 M 标记=他会话在途（信号域蓝图面），非本车道触碰面。

## 2. 施工方案（照卡）

1. **commit1（先行）**: capability 册 creation_token（sector-surface-20261008）插
   creation_tokens 末尾 di_seam_exemptions 锚前，safe_write_text CAS。
2. **新件** `scripts/backtest/sector_surface.py`（MOD-BT-238）:
   `build_sector_panel(start,end)`（行业聚合宽表：IND_close/IND_amount/sealed_up/资金流，
   只读走 _c4_engine.run_query 既有通道）+ `sector_strength(panel)`（四路子分→合分
   clamp[0,100]+Top15% 候选池掩码+缺维 fallback 标 degraded）+ `build_sector_context`。
3. **引擎接线** factory_grid_executor.py: evaluate_recipe 增可选参 sector_ctx；
   combined 解析后（cache 命中面外）、Top-N 前插 `X_sector` 可选段：
   strength_top15=候选池行业掩码 / conduction=先 gate 后 weight（查表 ≥9→1.15/≥6→1.05/<6→0.90，
   只调分不重排名）；传导改分后 rank 预算作废置 None（跨行业重排真实语义）。
4. **schema** config/position_recipe_grid_schema.yaml 增 `X_sector=['off','strength_top15','conduction']`
   （baseline off，phase>=3，折叠相零漂移；沿 X_stop/X_breaker 先例）。
5. **单测** tests/backtest/test_sector_surface_wiring.py: 四路数学/传导档位/gate 三关/
   零漂移（off 逐位相等）/fail-closed/池保底。
6. 对拍读数: 合成面板逐值断言 + 真数窗 smoke（只读）留档本文件 §4。

## 3. 自裁记录
- schema 增维是否需前置裁定: 规格卡 L2-01 §4 写"schema 修订→裁定前置"；
  判 X_stop/X_breaker（20261007 袋B）同型先例已开（禁删维不变、折叠相零漂移、
  新维纯增），且本车道任务卡 Owner 全权授权连续执行——**自裁：按先例施工**，
  裁定面（X_sector 进正式考卷 phase3 展开）留给 T3b 序，本批只落引擎+折叠维。
- 共享热册收编策略演变（13:25-13:45 实录）: ①初判"不收编"（L5 先例）→②预检证实
  CREATE-GUARD 读盘面（token 在盘即过）但 TRANSLATION-COVERAGE 读袋面（册必须随袋）
  →③改外科术（HEAD 基底+仅本车道条目）→④gateway claim 实测两册均被 st-mx07-W6
  持有（并行 token 袋在途）→**终裁：夜战常态归属各自认领**——工作区全量版还原
  （wq87/rowvec 面零丢失），.md 与翻译条目随 W6 袋吸收落地，W5 内容袋押后续投；
  若 W6 袋死信则按 dispatch_blockers W5 条目处方接手。协调条目已登记
  dispatch_blockers.md [st-mx07-W5]。

## 4. 对拍读数（施工后回填）

### 4.1 合成面板单测（2026-10-08，pytest 14/14 绿，~6.7s）
- 四路极端离散：A 行业（上行+封板+资金流入）末日合分=100.0（逐值断言）；
  B 行业=37.5（=0.25×(0+50+50+50)，双行业 rank-pct 下限 1/n 数学事实）。
- 预热窗（mom20+diff5）前 20 日 NaN=诚实缺供；有分行保底 1（85 分位≤max 内蕴）。
- 降级归一：flow 缺席→三路重归一 A=100/B=33.33+degraded 标记在册。
- clamp：adj=-200 → 双行业 0.0。
- 传导三档查表：9.5/9.0→1.15；8.9/6.0→1.05；5.9/0→0.90（封闭口径逐值）。
- gate 三关逐关：板块关不过（弱板块强票）→NaN 不放行（gate 先行，打折也不进池）；
  个股关恰 5.0 拦（严格 >5）；流动性关 1e8<2e8 拦。
- mode 校验前置（unknown mode ValueError 先于行业锚 fail-closed）；缺行业锚 RuntimeError。
- 零漂移：evaluate_recipe X_sector='off' vs 缺省=逐位 assert_frame_equal 相等。
- fail-closed：conduction 缺 sector_ctx → RuntimeError。
- phase=1 折叠：N_raw=362880 不变+全 recipes X_sector='off'；schema 声明面断言。

### 4.2 真数窗 smoke（2026-08-01~09-30，只读 CH，EXIT=0，ELAPSED=3.8s）
- 首跑实钓两处修复：①money_flow 同行业多票 pivot 重复键→pivot_table(sum)
  （板块流=Σ成员流）；②CH Decimal 列与 float 加法 TypeError→astype(float) 强转。
- 读数：score 42 日×31 行业（=sws2021_l1 全集）；分值域 [12.1, 94.4]；
  池行 22/42（前 ~20 日=动量预热诚实 NaN）；末日池={医药生物, 房地产, 汽车, 美容护理,
  食品饮料}（5/31≈16%，Top15%+ge 语义）；TOP3=房地产 86.0/医药生物 81.2/食品饮料 78.9，
  BOTTOM3=计算机 26.2/有色金属 25.0/石油石化 23.8；degraded_flags=()（money_flow 在线）。

### 4.3 回归披露
- test_factory_grid_stage_cost_tiers 7 例红=HEAD 预存（`_load_mkt_cap_wide(...)` 无条件
  `.reindex` 链在 HEAD:1377 同在，monkeypatch 返 None 即炸；本批对该链零触碰，
  `git show HEAD:` 对照在案）。其余 71 例绿（含新 14 例）。

## 5. claim 状态
- scripts/backtest/sector_surface.py / factory_grid_executor.py /
  config/position_recipe_grid_schema.yaml / tests/research/backtest/test_sector_surface_wiring.py /
  本文件 —— 均已 lock_files.py acquire（st-mx07-W5）
- 误 claim 已弃：tests/backtest/test_sector_surface_wiring.py（实际落位 tests/research/backtest/，
  TTL 自过期）
- 热文件不收编（st-mx07-L5 先例，归属其主后续袋收口）：
  - capability_canonical_file_registry.yaml（staged 侧他会话 926/928 在途重排+工作区他班 token +5 行）
  - module_translation_registry.yaml（工作区混有 st-mx07-L5 D_FACTOR bench_scaling 等在途条目）

## 6. 遗留与风险
- X_sector 进正式考卷（phase=3 展开）=裁定前置，本批只落引擎+折叠维（§3 自裁）。
- conduction 的个股强度代理=合成因子截面 rank（卡 §6 v1 口径）；十档查表系三段平段，
  MOD-SIG-136 活体线性插值变体语义不同源（卡=查表为施工真源），两者并行披露不混用。
- money_flow 2021 起才有实测：更早考窗自动走三路降级归一（degraded 如实标记）。
- capability/翻译两册在途面收口后建议由 token 袋一并核对本批两条目（token=sector-surface-20261008，
  翻译 module_path=scripts/backtest/sector_surface.py）。
