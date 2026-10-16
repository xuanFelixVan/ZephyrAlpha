---
ttl: permanent  # st-docconsol-20261014 改：原 task_bound 随 _working 搬迁落 _archive permanent zone 按 DCR-003 转 permanent（正文字节零改动）
session: st-infoaxis-20261013
date: 2026-10-14
title: 信息供给轴＋日内做T 总包·交付文档（99_delivery）
status: finalizing
goal_block:
  goal_statement: 六域产出物事件研究验证＋目标机制三件上线＋151 核心节点读数在产——战役交付留痕
  output_contract: 交付清单＋验证读数＋遗留/移交＋P1 呈批状态
  exam_ref: 管线级验证读数（判据数值未冻结＝打靶判定后置的边界声明）
  campaign_ref: st-infoaxis-20261013（裁定#516）
---

# 99_delivery.md 战役交付文档

## §一 交付清单（按域）

| 域 | 交付件 | 真数验证 | 落地 |
|---|---|---|---|
| 目标机制 Q5 | TDM 186 节点 goal 块（+1438 行）＋注入器/探针 | --check 零漂移＋5 测试 | 袋（Q5 大袋） |
| 目标机制 Q6 | goal_readiness_aggregator＋表 c1_market.goal_readiness_daily | **187 行在产**（绿10/黄76/红65/挂起35；分母 151 机械复现）＋8 测试 | 热修袋 |
| 目标机制 Q7 | CAMPAIGN-GOAL-BLOCK 门（own-scope 142）＋预告 00:48 | 7 测试；自举两段 enabled=false→翻真随门模块上 dev | Q6/Q7 袋＋收班翻真 |
| 传导链 | chain_direction_semantics（六类×角色矩阵）＋resolver.resolve_directed | 涨价客户侧反号/断供双侧负实测＋6 测试 | 传导链袋 |
| 股权穿透 | equity_link_signals 三信号族＋表 | **702 行在产**（牛散 200 含徐开东等实证榜/联动 500/质押 2）＋5 测试 | 股权袋 |
| 研报 | expectation_revision_assembler 双流＋双表 | **评级 47 事件＋三件套 4195 行**（真数 2026-09-30 窗）＋5 测试 | 热修袋 |
| 财报 | pead_assembly（MOD-SIG-164）＋表 | **2,824 SUE 事件在产**（Q3 披露季 75 日窗）＋6 测试 | 热修袋 |
| 千股千评·互动易 | IrmProvider 工厂接线（死水根因闭合）＋retail_comment_signals＋表 | **88,372 行 1:1 回填**＋独立复算逐位一致＋15+5 测试 | 热修袋＋千股千评袋 |
| 日内做T | orderflow_features（CKS OFI＋micro-price）＋L3-11-1/2 v2 现势窗考卡 | 真数 OFI（000002@10-09 200 帧负 OFI 卖压自洽）＋5+7 测试 | 做T袋 |
| A02 口径更正 | l9_readiness A02 行引用式更正（Q10）＋AGG note_confirmed | 16 存量测试绿 | Q5 大袋（五文件版） |

测试总计：**67/67 两轮全绿**（完工判据 #3 连续两轮问题=0 ✓）。

## §二 事件研究验证读数（管线级——判据数值未冻结，判定后置声明）

- PEAD：SUE 五档 × fwd5/fwd20（1,738 事件全价覆盖）。本窗读数：正 SUE 档前瞻为负
  （反转形态）——读数如实记录，达标判定待 B4 判据冻结后打靶（禁看数挪门柱纪律）。
- 评级变动：downgrade fwd1=-1.05%/fwd5=-2.15%（方向经济合理）；upgrade n=10 窗弱。
- 六域管线全部端到端真数跑通（输入→装配→CH 落表→读数面）。

## §三 基础设施遗留（移交维护线）

1. write_tsv 分块误报 True（CH HTTP 间歇尾段）＝#ARCH-352 同族——exprev trio 表
   1,400/4,195 键部分落地，maybe_emit 日批幂等重写逐日收敛；根治属 ch_writer 维护面。
2. 队列 landing "dev 已删"误判（worktree 分支头 base_head）——本役以 --base-head dev
   显式传参绕过；结构性修复（B 段自动取目标分支头）建议维护线立项。
3. 袋携旧 CAPCAN 回写冲账本（挂图申报被冲两轮）——本役以"新册随袋"防再冲；根治
   属 enqueue/bootstrap 面。
4. tick 源 10-12/13 两交易日缺口（max trade_date=10-09）＋tick_subscriber_biz.heartbeat
   文件未见——挂机源脆弱性实证（Owner 口径），tick_subscriber 归数据班。
5. q-0007 撞复发熔断 142 次（auto-retry 循环空转）——熔断对 cascade_stale 类死因的
   自动重试策略建议维护线复核。

## §四 P1 呈批状态（20_ruling_package.md）

- A 保留面 4 项**停等 Owner**：A1 研报数据采购（默认不采先吃仓内）/A2 股权数据源
  （默认免费挖掘先行）/A3 SQLite 小图退役（轨 B）/A4 ig_sector_bridge 权限修复（一处
  GRANT 级处方）。
- B 判据数值 6 项：框架已呈，打靶前逐批冻结。
- C 技术口径 7 项默认先行（151 分母/宏观 S0 并入 L1/IrmProvider 修管线/考卡现势窗/
  桥延迟防前视/A 股修正系数/严红线口径）。
- D 重大发现 4 条通报（研报前提修正/PEAD 定位/tick 现实/G5 权限根因）。

## §五 跳过留裁清单

- 无跳过件。停等项全部为 §五 保留面（花钱/退役判死/权限变更），已在 P1 呈批。
- 后置件（非跳过，有明确后续）：预告/快报两时点表未物化（P1 补呈 A5）；做T 三模块
  运行时接线留 P4 验证后收尾件；LLM 蒸馏腿（S5 二段）走 LSG 后置。

## §六 落地清单

（看护二班执行中——落地后回填 qid→hash 表）

## §七 收班序列

release claims（8 件已清）→ 本档＋台账随袋落 dev → staging 确认 TTL → handoff 交接
包（本档即交接面）→ worktree archive --execute → 向 Owner 终报。
