---
ttl: task_bound
title: "接线挂载类24项两日后复审"
owner: st-datasop-20260930
language: zh
status: active
version: "1.0.0"
date: 2026-10-04
---

# AUDIT-B：消费接线+挂载考试 24 项两日后复审（2026-10-04）

> 核法：逐项 grep src/ 消费端 → 有新消费者=已接线（git log 归因）；辅证=census 零岛现值（updated_at 2026-10-01T04:43）+ CH 只读实查 + 登记册 git 史。本审计只读勘察+仅写本文件，零既有文件改动、零 git 写、CH 仅 SELECT。
> 事实锚：census=data/runtime/consumption_census_ledger.json（460 zero/329 active/8 retired）；wiring=docs/01_policies_and_standards/_registry/catalogs/wiring_registry.yaml（consumption_islands 20 条+island_transitions=[]）；TDM=config/trading_decision_map.yaml；STR 册=docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml。

## ① 结论速览

24 项中：**已落地 1（挂载草案§三六张 TDM mounts，e405020493a）+ 半接线 1（3-8 前半 llm_premarket 已接、style_regime_model 未接）**；其余 22 项零消费端变化=仍需接线/仍锁。10-02~10-04 多队施工（拆簇/裁定#480 手术/挂图九张/GOMAP）与本项目零交集，无并道冲突；他 aidrafts（st-chief-mount/st-tdm-mount-flash/st-tclose-fwire）与主区 TDM/wiring 逐字节一致=无在途未落地接线。

## ② 24 项逐项判定（一项一行）

| # | 项 | 判定 | 证据（census 零岛/grep/git） |
|---|---|---|---|
| 3-1 | emotion C1/C3/C4/C5/C6 拆露 | 仍需 | emotion_component 5 岩（C1_limitup_temp/C3_breadth/C4_volume/C5_margin/C6_news）仍 zero；src 仅 emotion_index_builder+census 引用；02960acd50=情绪指数重放复职非分量拆露。暖机 obs<120 压制至 2026-11，W-04 可 defer 不变 |
| 3-2 | intraday_l1_tracker 回接 | 仍需 | tracker:16/:44 "表空" stale 注释原样；limit_up_pool 无新消费者；板块拆解 proxy 未回接 |
| 3-3 | attribution_results 接线 | 仍需 | attribution_calculator/result_store 全仓仅自身两文件，零生产调用方；W-1 挂 decision_daily/sim_attribution_daily 下游或 defer |
| 3-4 | knowledge 写口 | 仍需 | 全仓零 INSERT INTO knowledge；d5 两验证器仍"有读无写"空转 |
| 3-5 | 溢价率因子族 | 仍需 | etf_nav/etf_benchmark census zero；api_server 命中=展示标签字典非分析消费；factor_registry 无新溢价卡（FCT-LIQ-027=2026-08-16 旧卡） |
| 3-6 | alt_stock_comment 关注度因子 | 仍需 | census zero；消费仅 cohort_daily_ledger（09-22 老聚合班）+bootstrap/l9；无 attention_index candidate 卡 |
| 3-7 | BOM 挂价两链 | 仍锁 | ig_node_binding 零消费面（仅 gate 文件名命中）；alt_fx_rate_ecb 仅 producer；BDI 仅既有 F4 regime 链；解锁=产业链图施工批未启动，defer 不变 |
| 3-8 | style_regime_model 接宏观传感器 | **半接线** | WO-1 第一消费者 llm_premarket_analysis 已接（080fdfeca3，10-01 06:47，st-datasop-20260930：caution_factor/tier 盘前注入+5 测试）；style_regime_model 仍未 import MacroRegimeSensor——剩余工作量缩窄为只接第二消费者 |
| 3-9 | sw_history PIT 用途 | 仍需 | sector_constituent_sw_history 全仓零读、census zero；W7 挂账 90 天门计龄中 |
| 3-10 | board_index_supply 正式接线 | 仍需 | board_index_supply.py 全仓唯一文件零外部调用方；CH 实证 board_index_tick 自 09-15 仍仅 4 个交易日（断档未修复）——W2"供给修复先行"未动 |
| 3-11 | daban 周窗契约 | 仍需 | tasks 周窗注释=2026-09-16 裁定#257⑤ 旧有，非 W-05 新书面化；无新增陈旧度告警（sleeve WARNING 纪律为既有 INVARIANTS） |
| 3-12 | 转债 list 接线 | 仍需 | convertible_bond_list census zero；api 命中=标签；与 clause 双表语义去重未做 |
| 3-13 | 期限结构接线 | 仍需 | futures_term_structure census zero；无 roll yield 卡；回补未启动 |
| 3-14 | AH 溢价 | 仍需 | kline_hk_daily census zero（fresh 但无人查原样）；无 AH 因子卡；hk_kline 并表/退役评审未动 |
| 3-15 | 基本面五岛 | 仍需 | shareholder_count/equity_pledge_summary/top10_circulating/share_change/industry_class_suppl 五表 census zero（fundamental_table 12 岛=10 活跃+2 retired 原样）；W2 质押断供先决未修 |
| 3-16 | ir/irm 扩产 | 仍需 | ir/irm 4 表 census zero；tasks.yaml refresh 任务=2026-09-18 D7 老登记非扩产决策；W8 裁定未做 |
| 3-17 | rights_issue 框架 | 仍锁 | rights_issue census zero；negative_veto.rights_issue_pending=2026-09-10 老负面否决清单字段非本表消费；公司行动事件框架未立项，defer 不变 |
| 3-18 | 板块码表直读 | 维持 defer | sector_code_name_map 全仓零直读；W8 低危暂缓声明原样 |
| 3-19 | EQW 扩面 | 未立项 | CH 实证 kline_index_calc 仍单条 EQW_ALLA；第二条等权未立项，W5 挂账不变 |
| 3-20 | 转债 iv 回补解锁 | 解锁条件未动 | CH 实证 convertible_bond_iv=11,481 行 max 09-30（与 10-01 读数零增长）；scripts 无回补脚本；known_data_gaps 无条目；defer 计龄中 |
| 4-1 | 策略 E4 队列 8 张 | 未消费 | strategy_screen 10-01 后仅 2 行（STR-VREV-025 sim_deviation，他卡）；VREV-017/018/019/024+MF-069/096+DABAN-022+MOMTREND-020 零考试行；strategy_registry 161 卡 139 candidate/19 active/3 deprecated 与 L13 读数一致（该册 09-22 后零 commit） |
| 4-2 | 挖矿候选 36 条 | 未入账 | factor/indicator 两册 10-01 后零 commit，无 S0-S7 立卡/考试；A 组 36 条中仅 14 条（EXP/FQ/GR/QUAL/CHIPS）随 09-29 §9C 首批入 wiring_registry，census indicator 115 零变化、factor 126→122 |
| 4-3 | §9C 续批 | 未发生 | census=460 zero（10-01 04:43 复扫）；wiring_registry consumption_islands=20 条（09-29 首批）零新增、island_transitions=[] 零使用；09-29→10-01 治愈 13（挂载 6+因子语义 4+MAC-CN-001/002/003 映射面 3=473→460 对账闭合）；10-01 后无新入账无续批，census 已 3 天未复扫 |
| 4-4 | VREV-018/019 显式挂载 | 未做 | TDM 零 STR-VREV-018/019 strategy_ref；两卡 census zero+wiring_registry unwired；strategy_registry 零 mount_route 字段。顺序不变：E4 卡级考试过→出显式 mounts 单 |

## ③ 新发现的接变化（10-01 以来落地台账）

| commit | 时间/归属 | 内容 | 对本项目影响 |
|---|---|---|---|
| e405020493a | 10-01 04:49 st-datasop-20260930 | 册面接线执行：W1+W2+**挂载草案§三 6 张落 TDM**（E-TIMING-001 verified+VREV-001/MOMTREND-002/019/MF-098/099 proposed，登记面非实弹）+黑户补注册 40（DS-306~345）+孤岛 20 条入账+census 复扫 | §三可销账；census 治愈 13 的来源 |
| 080fdfeca3 | 10-01 06:47 st-datasop-20260930 | WO-1：llm_premarket_analysis 接 MacroRegimeSensor.score()（caution_factor/tier 注入+异常降级） | 3-8 前半完成，style_regime_model 成唯一剩余落点 |
| 867d821d45 | 10-01 07:12 GAP-F-23 | USDCNH 离岸人民币日K接入（sina fx_susdcnh，3102 行 2014→2026-09-29，tasks 去 disabled） | L01b W5 外盘腿部分复活+L08 WO-10 usdcnh 寻源长尾销账；HSI/N225/KOSPI 待 provider 仍原状 |
| 02960acd50 | 10-01/02 全流通清场总包 | L13 情绪指数重放复职落地 | 情绪链修复侧写，非 3-1 分量拆露 |
| — | 10-02~10-04 多队 | 拆簇（st-construct）/裁定#480 手术（st-sA/sB/sC）/死信根治/挂图战役（图9/12/13、GOMAP F1/F2、tdm-mount-flash 蓝图 module_id 统一） | 与 24 项零交集；"挂载"热词属挂图（module→map）域，勿与策略挂载/数据接线混淆 |

## ④ 方案修正建议

1. **3-8 缩窄**：只需接 style_regime_model（复制 llm_premarket 注入契约区先例+降级纪律）；wiring_registry MAC 四岛 suggested_wiring_target 仍写旧落点 `regime_cycle_analyzer.py`——L08 已证不成立，续批入账时应修正为"macro_regime_sensor 下游（llm_premarket 已接/style_regime_model 待接）"。
2. **4-3 续批机制**：island_transitions 字段至今零使用——续批入账时启用它记录治愈轨迹（09-29→10-01 的 13 例治愈即无台账留痕，仅靠两版 census 差分复原）；且 census 复扫停 10-01，接线施工后须触发复扫才算入账闭环。
3. **无并道风险**：10-02~10-04 施工全在挂图/拆簇/手术域，24 项工单可直接移交施工批，方案本体（各车道 W 工单）无需改向；唯一顺序约束=3-15 先修 W2 质押断供、3-13/3-20 先回补历史、3-7/3-17 维持解锁条件挂账。
4. **4-1/4-4 顺序确认**：E4 考试队列零消费，VREV-018/019 显式挂载维持"卡级考试通过后出单"前置，不因 §三落地而跳道。

## ⑤ 自审闸三态

- 只读勘察：CH 仅 SELECT（DatabaseService reader）；零既有文件改动、零 git 写、零 commit——过。
- 产出：仅本文件一个新文件；CREATE-GUARD creation_token 留待总筹落地批次登记（同 L10b 先例）——留痕。
- 计数一致：24 项逐项有 census/grep/git/CH 四类证据至少一类，治愈 13 例两版 census 差分对账闭合——过。

## 切换记录

- 2026-10-04 v1.0.0 AUDIT-B 初稿：24 项逐项复审（落地 1/半接线 1/仍需 22）+10-01 落地台账 4 笔归因+方案修正 4 条。
