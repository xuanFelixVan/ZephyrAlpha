---
ttl: task_bound
completes_when: 模块晋升 docs/03_modules（H-01 解冻）或工单废弃
---

# MOD-AUTO-L1-001~005（暂编号）上架流水线与 ECB 首源蓝图

## 定位

骨架 §1 工段③"自动上架"执行件：源卡片驱动的 probe/apply/verify 编排 + 首个免费源
ECB（frankfurter.app）端到端验证。L1.1 批（st-autolnk-20260917b）把采集核心升格
DataScheduler 正门 provider 路由，Windows 任务通道降为人工/过渡双轨（退役=H-06）。

## ALGO_FLOW

- I1: config/source_cards/*.yaml（源卡片：table/schema_module/ingest 脚本/回补窗）
- A1: onboard_source.probe/apply/verify（沙箱零落库→DDL 建表+回补+登记→三核）
- A2: fx_ecb_provider.fetch（capability=fx_ecb_daily；per-base 拉 frankfurter 序列→parse_series 行元组；异常吞成 FetchResult(error) 不抛）
- O1: 正门=DataScheduler 槽位 daily_alt_fx(23:35 工作日)→c1_market.alt_fx_rate_ecb；旁路=fx_ecb_ingest.py CLI（Windows 任务/人工补跑，复用同一 provider）

## 关键不变量

- last_key=各货币对最迟日期（min of per-base max）——任一对缺价游标不越它，下一班自愈，防对级数据洞。
- provider 只拉不写 CH（写=调度器 BufferedWriter 正道）；脚本旁路才直连 write_result。
- 零配置降级：网络失败 fail-visible（FetchResult.error→调度器告警），禁伪装空成功。

## 消费方

DataScheduler（正门班次）、fx_ecb_ingest CLI（人工）、①号源发现工段未来新源照抄此模板。
