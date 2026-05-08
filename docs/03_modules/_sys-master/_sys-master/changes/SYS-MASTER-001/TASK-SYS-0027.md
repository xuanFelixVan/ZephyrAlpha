---
task_id: "TASK-SYS-0027"
source_blueprint: "SYS-MASTER-001"
source_section: "§40 市场数据管线与回测引擎 + §91 企业行为与参考数据管线"

title: "市场数据管线(AkshareProvider/DataValidator/FeatureStore三级) + 回测引擎(滑点/佣金/冲击模拟+基准对比沪深300/中证500/国债指数) + 企业行为七类管线(分红/拆分/送股配股/并购/退市/代码变更/行业分类)体系搭建"
description: |
  将 §40 市场数据管线与回测引擎 + §91 企业行为与参考数据管线合并落地为端到端行情→回测→事件校正全链路。
  §40 定义：
  （1）市场数据管线——AkshareProvider 拉取A股日线/分钟线→sqlite → DataValidator 完整性/及时性/有效性校验（§29）→ FeatureStore 因子计算+特征存储（§42.1）。
  （2）回测引擎——执行模拟（考虑滑点+佣金+冲击 §64.2）· 基准对比（沪深300/中证500/国债指数）· 输出（年化收益/MaxDD/Sharpe/Calmar + 逐日PnL + Turnover）。
  §91 定义：
  （1）七类企业行为必须处理——现金分红（复权价格+累计分红因子,P0）/股票拆分合股（adjustment_factor,P0）/送股配股（除权价计算+股数调整,P0）/并购收购（现金换股比例→模拟平仓价格,P1）/退市（检测+告警+Owner确认,P1）/代码变更（symbol_map+自动redirect,P0）/行业分类变更（日级GICS tracking,P1）。
  （2）企业行为数据管线——Source(akshare/baostock)→Validator(事件完整性+多源交叉验证)→Transform(复权因子 bwd_adj_factor/fwd_adj_factor → time series)→Apply(所有价格列×adj_factor→因子重算→特征存储更新)→Verify(随机10只股票×5次行为→价格正确性)。
  （3）每日盘前检查5项——今日除权除息事件预加载 adj_factor·代码变更更新 symbol_map·昨日退市公告通知·本月股东大会提醒·adj_factor序列连续性（PctChg<50% day-over-day）。
  （4）回溯修复协议——发现企业行为数据错误（<T-7以内）→修复源数据→重算受影响区间 adj_factor→重跑因子+信号→回测结果对比前版本 Δ报告→Owner审阅。
  本卡搭建 market_data_pipeline.py + backtest_engine.py + corporate_actions.py。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\market_data_pipeline.py"
    description: "§40 AkshareProvider 日线/分钟线→DataValidator(§29)→FeatureStore(§42.1)三级管线"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\backtest_engine.py"
    description: "§40 回测引擎——滑点+佣金+冲击模拟+基准(沪深300/中证500/国债)+输出(收益/MaxDD/Sharpe/Calmar/逐日PnL/Turnover)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\corporate_actions.py"
    description: "§91 七类企业行为(分红P0/拆分P0/送股P0/并购P1/退市P1/代码变更P0/行业变更P1) + 管线+每日盘前5项检查+回溯修复"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\market_data_pipeline.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\backtest_engine.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\corporate_actions.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l*\\**\\*.py"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    reason: "§40 AkshareProvider管线+回测引擎 + §91 七类企业行为+管线+盘前检查+回溯修复"

assigned_model: "deepseek"
assigned_pipeline: "A/B hybrid"
pipeline_modules:
  - "M1"
  - "M2"
  - "M3"
estimated_tokens: 28000
timeout_minutes: 75

acceptance_criteria:
  - "market_data_pipeline.py 实现 MarketDataPipeline——AkshareProvider.fetch(symbol,start,end,interval)→DataFrame· DataValidator(完整性:缺行/预期<0.1% + 及时性:±5min + 有效性:价/量>0无NaN + 一致性:多源agree §29)→FeatureStore写入(§42.1 schema)"
  - "backtest_engine.py 实现 BacktestEngine——execution_sim(slippage+commission+impact §64.2 FF model)· benchmark_compare(沪深300/中证500/国债指数)· output(annual_return/MaxDD/Sharpe/Calmar + daily_PnL_series + Turnover)"
  - "corporate_actions.py 实现 CorporateActionType 枚举(7类: CASH_DIV/STOCK_SPLIT/BONUS_SHARE/MERGER/DELIST/SYMBOL_CHANGE/GICS_CHANGE)——各含 priority(P0/P1)+handler func"
  - "corporate_actions.py 实现 CAPipeline——Source(akshare/baostock)→Validator(完整性+交叉验证)→Transform(bwd_adj_factor/fwd_adj_factor time series)→Apply(价格×adj_factor→因子重算→特征存储更新)→Verify(随机10只×5行为验证)"
  - "corporate_actions.py 实现 DailyPreCheck——5项(除权除息预加载/代码变更更新/退市通知/股东大会提醒/adj_factor连续性 PctChg<50%)→盘前08:00自动运行"
  - "corporate_actions.py 实现 BackwardRepair——发现错误(<T-7)→修复源→重算adj_factor→重跑因子+信号→回测对比Δ报告"

rollback_instructions: |
  1. 删除 market_data_pipeline.py / backtest_engine.py / corporate_actions.py
  2. 从 script_manifest.yaml 移除注册

depends_on:
  - "TASK-SYS-0006"
blocked_by: []
status: "done"
tags_fn:
  - "trading"
tags_ly: "cross_layer"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "SYS-MASTER-001"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
