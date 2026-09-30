---
ttl: task_bound
title: "NB1 B5 裁定卡：CN-MACRO 宏观指标整族 16 条（MAC-001~016）——价值确认+复活接入处方"
session: st-nightsweep2-nb1-20260930
updated: 2026-09-30
---

# B5 CN-MACRO 宏观指标整族 16 条 · 价值挖矿裁定卡

## 事项

对象=macro_indicator_registry.yaml（REG-MAC-001）indicators 全族：MAC-CN-001~011+MAC-US-001~004+MAC-CN-016（实测 **16 条**；注意册头 entry_count=15 为**漂移 1**，CN-016 后补未回填计数）。Owner 三问：①宏观因子对大盘状态判定 L01 的价值 ②edb_data/FRED 断供现状能否复活 ③复活则写接入大盘月线/周线处方。

## 六向台账快照

| 向 | 实测 |
|---|---|
| 通道 | REG-MAC-001（SSoT，v1.2.0，schema v2.0）→ TDM-E-L1-S0 宏观环境传感器（config/trading_decision_map.yaml:450-451）+ EVT-MACRO-001（event_calendar_registry:373） |
| 原料 | **活源=c1_market.macro_data（akshare，291K 行，任务 macro_data_incremental，akshare_provider._fetch_macro_data:1147 现役，GDP/CPI/PMI/货币供应量）**；PIT vintage 层已建=src/zephyr/data/macro_vintage.py（WO-B3，ALFRED 式 vintage 模型，pub_ts 口径，零 ALTER 业务表）；死源=c1_market.edb_data（0 行，iFind EDB 配额 -4318 耗尽，known_data_gaps status=accepted） |
| 状态 | 注册表 16 条全 candidate（0 active）；TDM 挂 8 条 macro_refs（CN-005/006/007/008/009/011+US-001/002）；**src 侧零代码消费 MAC-*（grep 实证）**——TDM 声明面与代码消费面断裂 |
| 消费方 | 声明消费=TDM-E-L1-S0（module_ref=policy_expectation_analyzer.py MOD-ALT-010，但该件实做政策表态/LLM 打分，**不消费 MAC 数值**）；used_by 字段填 regime/macro_timing/sector_rotation（自声明） |
| 缺口 | ①MAC 指标 ID ↔ macro_data akshare 序列的**映射表不存在**（数据在、名字对不上）②L1-S0 无真消费模块（四组信号 A 货币/B 流动性信用/C 海外/D 增长政策只有叙事无代码）③FRED SRC-FRED-001（美 22 序列）无活 fetcher（foreign_market_coverage/scheduler 提及但未见 US 宏观拉取腿）④entry_count 15≠16 ⑤edb_data 空壳表处置（归 B6 分层） |
| 处方 | 见"复活接入处方"（下） |

## 三审结论

1. **价值审（通过，高——Owner 裁定背书）**：TDM-E-L1-S0 明文"Owner 裁定：宏观完全交给系统算法（人工不消费），四组信号全上"，方法论=复用周级三步法（滚动分位→加权合成→天气分 0-100）喂月级谨慎度修正；A股范式权重修正（政策/产业因子↑总量↓，广发链）。**全网佐证**：货币信用四象限框架+M1-M2 剪刀差前瞻性+信用脉冲领先 6-9 月是卖方主流（东方财富《量化策略(一)：宏观择时》对各宏观因子正/反向测评）； caution=2021 年后信用周期对大盘领先性钝化（鑫选 ETF 实证）→ 必须月线定 regime、周线做确认、滚动样本外检验——与 TDM 设计的月级修正+灰度裁噪（相关性去重）吻合。
2. **真源唯一性审（通过）**：REG-MAC-001 是宏观指标定义唯一 SSoT（发布机构/频率/PIT 滞后/修订政策/市场影响），对标聚宽宏观谱系+FRED 治理；数值数据唯一活源=macro_data（akshare）；vintage 存证唯一真源=macro_vintage.py 通道。仓内无第二套宏观定义册（ROOR 复核）；无需融合外部实现。
3. **数据持续性审（通过——有持续数据，走数据三流程）**：edb_data 断供**不等于族死**：akshare macro_data 291K 行+增量任务在册（且 architecture_issue_registry:11629 在案"扩展 akshare_provider macro_data 8 类利率/宏观指标免费替代"——执行属 st-zc9-lane-d 领地，本卡只引用）；FRED 免费公开 API 无断供（美序列可另起小源）。**结论：族活，缺的是"映射+消费"两根线，不是数据。**

## 复活接入处方（对齐 L01_regime 数据面，供 NB2/数据道施工）

- **R1 映射表（前置，P0）**：建 `config/macro_indicator_series_map.yaml`（唯一新配置）：MAC-{CN|US}-NNN → (source=akshare|fred, series_code, unit, transform=yoy|level|diff, seasonal_adjusted)。初版覆盖 TDM 已挂 8 条（CN-005 Shibor/006 社融/007 M1-M2 剪刀差/008 信用利差/009 两融/011 PMI、US-001 美债 10Y/US-002 美元指数）+CN-001~004；映射即"翻译层"，禁散落硬编码。
- **R2 PIT 读视图（P0）**：沿 macro_vintage.py 既有 pub_ts 通道出 `macro_indicator_read` 视图（indicator_id, obs_date, pub_ts, value）——回测 as_of 语义取数，PIT 铁律（注册表治理规则#1）天然满足。
- **R3 消费模块（P1）**：新建 regime/features/macro_regime_sensor.py（TDM-E-L1-S0 的 module_ref 改指它，policy_expectation_analyzer 回归纯政策表态）：输入 R2 视图，输出四组信号分（A 货币/B 流动性信用/C 海外/D 增长政策）→ 加权合成宏观天气分 0-100 → L01 月级谨慎度修正因子；周级消费=同一 read 视图按周频采样做确认信号（不另建管线）。先红样后接线，测试走 tmp_path。
- **R4 FRED 腿（P2）**：MAC-US-001~004 经 FRED 免费 API（DGS10/DTWEXBGS 等 4 序列起步，22 序列分批），落同一 macro_data 通道（source=fred 列区分），勿另立表。
- **R5 册务（P0，半小时）**：entry_count 15→16 修正+16 条 status 候选→active 的转正随 R3 上线一并走 safe_write_text CAS；edb_data 表退役归 B6 卡处置。

## 三态裁定建议

**【保留+接线】（融合=数据已在仓、缺映射与消费两线；R1-R5 处方如上）**。零删除、零退役、零新表（vintage 视图复用）。

## 自审闸三态

**挖干（置信度=高，R4 FRED 序列细节除外）**。可复算：注册表 16 条枚举+TDM:450-451+macro_data 任务链（tasks/akshare_provider:1147/architecture_issue:2905,11629）+macro_vintage.py 现读+edb_data 三处死因互证（workorders_data_exam_factory:18/known_data_gaps/C267b）+全网宏观择时佐证。未干残余：①FRED 具体 22 序列清单未逐条核（SRC-FRED-001 只见定义未见序列表）；②CH VM 9000 本夜不可达（实测 SocketTimeout），macro_data 行数 291K 引自 architecture_issue_registry 在案数非本夜 live 复数——CH 复活后应补 `SELECT count(),max(obs_date) FROM c1_market.macro_data` 终验。
