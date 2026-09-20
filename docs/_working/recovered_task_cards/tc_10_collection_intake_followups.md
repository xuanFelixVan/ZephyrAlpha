---
card_id: TC-10
title: 收藏情报拆解线后续（期权 PCR / 批 10 筹码 / P2 小活 / 密钥核对 / 巡检）
verdict: 稳态待令（置信度高：主体三笔提交全部固化为 HEAD 祖先、15 件交付物零缺失；六项后续无一项开工，维持"等 Owner 点单"合法稳态——但发现一处带时限的真缺口：批 10 范围登记分裂）
category: B类-时限窗口（批10挂接）+ G类-待令稳态（其余）
priority: P0（仅批 10 挂接修订一件，时间窗 1-2 天）；其余 P3 待令
size: 主动工作量小；PCR 批中；其余小
source: 任务原文见 C:\Users\fanzi\Desktop\新建 文本文档 (2).txt 第 763-845 行（"十："节，st-collintake-20260920 交接令）
investigated_at: 2026-09-21
head_at_investigation: c968ad6042
ttl: task_bound
completes_when: 全部卡执行完毕并归档后转 archived
---

# TC-10 收藏情报拆解线后续

## 0. 一句话结论

主体三笔（9d609be2a3/924c4e7376/8f7d91fb22）已固化、15 件交付物全在 HEAD，六项后续维持"等 Owner 点单"的合法稳态——这本身不是欠账。但挖出一个**带时限的真缺口**：收藏情报线声称"筹码集中度并入批 10"（cost_15/85 两列+CHIP_CONC_90/70 两指标），而 unified 战役 WO-4 的批 10 目标清单不含这些扩项——WO-4 状态"活"、时间盒仅 1-2 天，若不在其开工前回写，70% 集中度将永久缺列、P1 项变二次返工。另：.env 自 09-16 未动（曝光后超过 3 天未轮换，Owner 催办项）；月度巡检未挂自动化。

## 1. 背景与来龙去脉

Owner 交付一包小红书/视频收藏，st-collintake 拆成 25 条四路挖矿，判定 9A/8B/3C/5DE，三笔提交落库。交接令末尾列六项后续：1=Owner 手动换钥匙（AI 待命核对）；2=P1 期权 PCR 数据批；3=P1 批 10 筹码集中度搭批；4=P2 三小活（trade_when 白名单/E4 拥挤度/pf_alloc 接电立项）；5=月度巡检自动化；6=红线（未拍板不动）。

## 2. 调查结论（2026-09-21 实测）

| 原文声称 | 实测现状 | 证据 | 等级 |
|---|---|---|---|
| 主体三笔已落库 | 三笔全 HEAD 祖先（09-20 23:15 / 09-21 00:13 / 00:15）；collection_intake 恰 15 文件零缺失，抽验四件内容与交接令一致 | merge-base + git ls-tree + cat-file | A |
| 后续 1：Owner 换钥匙中 | **仍未换/未登记**：.env mtime=2026-09-16 15:05（早于 09-18 曝光，曝光后从未改写）；secret_registry.yaml 无 09-18 后轮换记录；全程未读任何密钥值 | stat mtime + git log --grep 轮换 | A |
| 后续 2：P1 期权 PCR 等点单 | 未开工：option_daily_stats 全仓零命中；tasks.yaml 仅四个既有 option 任务；option_sentiment.py 头部 INVARIANTS 明示 pcr_basis 恒为 volume（现算、无 OI 列） | grep + 读文件头 | A |
| 后续 3：P1 批 10 筹码等点单 | **未开工，但登记载体已变更+范围分裂**：chips_cost_15/cost_85/CHIP_CONC 在 src/scripts/注册表零命中（注册表实测 140 条=批 9-4 自然 +2，交接令写 138 已漂移）；批 10 已被 unified 战役收编（p2_backlog_master_ledger_v1_0.md:56 状态活、p2_workorders_v1_0.md:39 甲线 W4·WO-4、1-2 天时间盒）——**WO-4 范围不含 cost_15/85 扩项，intake 侧的"并入"从未回写进 unified 台账** | grep + unified 两文档原文 | A |
| 后续 4①：trade_when 白名单 | 未加：config/factor_mining_whitelist.yaml 零命中 | grep | A |
| 后续 4②：E4 拥挤度 | 未动：regime_validation/ 零命中，最后提交 09-16 | grep + git log | A |
| 后续 4③：pf_alloc 接电立项 | 未立项：近 3 天仅危机闸 FLOWTHROUGH 与 NaN 修复；"零生产调用方=不接线挂触发"裁定仍生效 | git log + ruling_registry:1975/1987 | A |
| 后续 5：月度巡检 | 未挂：schtasks 六个 ZephyrAlpha 系任务无巡检项；scripts/ 无巡检脚本 | schtasks 只读 + git ls-files | A |
| 挖根：Owner 点单没 | 没有：09-20 以来 95 笔提交无 PCR/筹码/trade_when 开工；裁定册尾部最新 #387 无相关新裁定 | git log 通读 + registry 尾部 | A |

### 病根

1. **批 10 范围登记分裂（新发现的真实缺口）**："并入"只存在于 intake 侧文档（README:81、factor_spec_chip_concentration.md），从未回写进 unified 台账——两线各说各话。WO-4 按原文施工完毕后 90% 集中度可由 cost_95/5 派生，但 70% 集中度永久缺列。
2. 任务性质判定成立：六项后续中 2/3/4 明文"等 Owner 点单"、1 是 Owner 手动、5 可选——"待令"是合法稳态不是欠账；但交接令要求的"向 Owner 报到待令"一步无证据显示有会话做过。
3. 安全项带时间压力：暴露窗口 09-18 实证，.env 停在 09-16——按"已泄露对待"已超 3 天而未处置，且这 3 天系统仍在满负荷跑。
4. WO-4 目标数"138 到 141"基于旧基线（实测已 140），施工时需按当日实测重算，防计数类 gate 误报。

## 3. 上下游

- 前置：后续 2 需要 akshare 接口实测可用+Owner 点单；后续 3 挂接需要 unified 台账编辑权限（热文件避让）；后续 4③ 需解除 pf_alloc"挂触发"裁定。
- 下游消费方：PCR 到 MOD-SIG-059 三件套到情绪注解维度；筹码集中度到 E1C 挖矿+E4 重考；eng_quantcombine 到组合层立项（与 TC-07 共享设计输入）。

## 4. 剩余工作清单（可执行）

| 步骤 | 做什么 | 涉及文件全路径 | 验收判据 | 路由与触发条件 |
|---|---|---|---|---|
| 1（**唯一可立即做、带时限**） | 批 10 扩项挂接修订：把 cost_15/85 两列+CHIP_CONC_90/70 两指标写进 WO-4 范围，口径按当日实测基线重算 | D:\ZephyrAlpha\docs\_working\unified_campaign\p2_workorders_v1_0.md:39、p2_backlog_master_ledger_v1_0.md:56 | WO-4 范围含扩项；两台账一致 | Flash 可立即做（热文件走 claim+队列）；**触发=立即，赶在 WO-4 开工前（1-2 天窗）** |
| 2 | P1 期权 PCR 数据批：akshare option_daily_stats_sse/szse 到新表 c1_market.option_daily_stats（三口径 PCR 列，DateTime64(3)+显式时区）到日频增量任务到 option_sentiment 改读表扩三口径到历史回补到假设卡过 E4；施工前走 construction_workflow_policy 15 步 | src/zephyr/data/config/tasks.yaml、src/zephyr/signal_ashare/sentiment/option_sentiment.py、新表、docs/_working/collection_intake/factors/factor_spec_options_pcr.md（施工依据） | tasks.yaml 有 option_daily_stats 任务；pcr_basis 扩三口径；E4 出证 | **触发=Owner 点单 P1** |
| 3 | 批 10 本体施工（主权在 unified 甲线 W4） | technical_indicator_registry.yaml + 批 10 采集器 | 注册表可 grep 到 chips_cost_15/cost_85/CHIP_CONC_90/70 | **触发=WO-4 排到或 Owner 单独点单**；前置=读裁定 #257④+批 10 配方（.aidrafts/st-tilib-clear-20260920/.../2026-09-15-tilib-handoff.md） |
| 4 | P2 三小活：trade_when 白名单+E4 拥挤度维度+组合层立项（以 eng_quantcombine 第 8 节为输入） | config/factor_mining_whitelist.yaml、src/zephyr/backtest/regime_validation/、立项文档 | 白名单+引擎算子表双向交集通过；E4 出证含拥挤度 | **触发=Owner 点单**；③另需解除 pf_alloc 挂触发裁定 |
| 5 | Owner 换钥匙后核对（AI 待命）：只报键名/格式，绝不打印值 | .env（只 stat）、config/secret_registry.yaml | .env mtime 晚于 09-20；registry 有轮换登记 | **触发=Owner 主动叫核对**；当前状态=催办 Owner（已超 3 天未轮换） |
| 6 | 月度巡检自动化：du .zcode 体积+repoSnapshot 键巡检，可搭现有 IOCheck-Monthly 车辆 | scripts/ 新巡检脚本（.ps1 纯 ASCII）+计划任务 | schtasks 出现巡检任务 | **触发=Owner 点头挂自动化** |

## 5. 与其他任务卡的关系

- TC-06：R3 TradeRecord/R4 做T 与本卡 P2 小活同域——引用口径吃 TC-06 的 #331 改号与 #386 禁复试图救。
- TC-07：eng_quantcombine 是两边共同设计输入，立项互认同源。
- unified 战役（不在 11 卡内但强关联）：WO-4 是批 10 施工主权方，本卡只拥有"扩项挂接"半个动作。

## 6. 风险与避让红线

1. 挂接修订是热文件编辑（unified 台账）：claim+safe_write_text CAS+队列正门。
2. 密钥核对红线：全程只 stat/grep 键名与 mtime，绝不 cat .env 或打印任何值。
3. WO-4 时间盒 1-2 天且状态活：挂接修订若错过窗，及时降级为"批 10 后追加批"并登记，勿硬闯他线施工。
4. 基线数字漂移（138 实为 140）：施工按当日实测重算。

## 7. 执行冷启动提示

按 AGENTS.md 第 0 节冷启动；新建表走 RULE-SCHEMA-TZ（DateTime64(3)+显式时区）；破坏性操作只有严格机械可证才许自动（Owner 铁律）。
