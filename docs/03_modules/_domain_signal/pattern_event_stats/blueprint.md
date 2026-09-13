---
blueprint_id: MOD-SIG-145
module_name: pattern_event_stats
domain: D_ASHARE_SIGNAL
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-09-14
last_updated: 2026-09-14
owner: ZephyrAlpha-Owner
---

# MOD-SIG-145 pattern_event_stats 蓝图

> 设计真源：2026-09-14 图形库全网对照缺口分析（Owner 拍板图形库全链批，会话
> st-pattern-20260914）。代码（拟）：`src/zephyr/signal_ashare/strategy_signal/pattern_event_stats/`。
> 上游：MOD-SIG-091 unified_pattern_engine（PatternEvent 生产者）；
> 下游：MOD-SIG-115 pattern_to_signal_mapper（historical_win_rate 消费者）。

## 0. 定位

统一图形识别引擎的 win_rate_provider 注入契约至今无实现侧（MOD-SIG-091 蓝图
明言"引擎不自建统计"）——MOD-SIG-115 的强度=置信度×胜率加权一直空转。本模块
补齐图形证据闭环：

    PatternEvent（引擎扫描产出）→ pattern_event 落库（CH，PIT strict）
    → 前视窗口胜率统计物化（+1/+5/+10/+20 日，regime 切片）
    → win_rate_provider 只读出口（喂 MOD-SIG-115 + REG-PAT-001 evidence 回填）

四件事：事件存储 / 历史回填扫描器 / 胜率统计物化 / 只读 provider。
背景依据：JFQA 2016 对冲基金实证（TA 超额挂高情绪 regime）+ 2026-09 37 万形态
检测实证（"完美"形态反而跑输）→ 证据先于目录扩张。

## 1. 数据契约（拟，W1 已落地）

- `c1_market.market_pattern_event`（CH 表，DatabaseService/ch_writer 正门，
  pit_policy=strict；DDL 真源 schemas/categories/market_pattern_event.py，
  apply 脚本 scripts/ch/apply_pattern_event_ddl.py）：
  event_id / pattern_id / pattern_class / direction / confidence / timeframe /
  symbol / anchor_trade_date / confirmed_at / name / key_points(json) /
  regime_tag / scan_run_id / data_source；ReplacingMergeTree(computed_at)，
  分区 toYYYYMM(anchor_trade_date)。沿 market_signal_history 先例落 c1_market
  （单用户系统不为一张表建第二库，c1_signal 预留名不建）。
  锚=确认 bar 收盘，仅已完成 bar 入库（盘中未确认形态禁入）。
- `c1_market.market_pattern_win_rate`（物化统计表，W3）：pattern_id / timeframe /
  regime_tag / fwd_window(+1/+5/+10/+20) / n_events / hit_rate /
  avg_fwd_ret / baseline_ret / low_sample / updated_at。
- 回填范围：日线 2021-09-01 起全 A 股；增量任务 pattern_event_incremental
  挂现有自动化框架（kline 落地后事件触发，禁 cron 自轮询）。

## 2. 口径裁定（防前视）

- 形态确认时刻=形态所需最后一根 bar 收盘完成；前视收益=确认收盘→t+N 收盘。
- regime_tag=确认日所属 regime 态（接 src/zephyr/regime 现成 builder 体系）。
- 胜率判据 per direction：多=前视收益>0；空=前视收益<0；中性=绝对收益>阈值
  （阈值进参数表，不散落）。
- n_events<n_min（默认 30）的统计行置 low_sample=true，provider 对外按 None
  语义返回（保持 MOD-SIG-091 契约：无统计=None，引擎行为退化不变）。

## 3. 收编与交接

- 5 条 PAT-CANDLE 实现自 `factor/technical_indicators/reversal.py`
  （CandlestickPattern）整体移交本域——蜡烛实现权移交裁定 2026-09-14
  （指标会话交底：IND-REV-001 届时改薄视图或走退役流程，注册表净删挂 Owner 门位）；
  蜡烛事件同样落本表。
- REG-PAT-001 条目级 evidence 字段的回填通道=本模块统计表（生成器产出，禁手填）。

## 4. 施工波次

- W1：表 DDL（admin 通道）+ store 读写 + 单测（tmp_path 隔离，禁写生产路径）。
- W2：回填扫描器（批量 / 断点续扫 / scan_run_id 幂等）+ 全量历史回填。
- W3：胜率统计物化任务 + win_rate_provider 接线 MOD-SIG-115。
- W4：REG-PAT-001 evidence 回填 + 增量任务上线。

## 5. 边界

- 不做：形态识别算法本身（归 MOD-SIG-091 腿）、97 形态→信号映射（归
  MOD-SIG-115）、技术指标计算（归指标库会话）。
- provider 注入失败→None：引擎与映射器行为退化为现状（fail-open 契约保持）。
