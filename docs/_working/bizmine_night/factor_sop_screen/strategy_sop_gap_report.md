---
ttl: task_bound
rule_form: data
verifiability: manual
title: 挖策略 SOP 缺口报告——sop_c 只覆盖入库，挖掘/考试段无册
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-19
status: draft（移交 Owner 裁定归宿）
session: st-bizmine-f-20260919
---

# 挖策略 SOP 缺口报告

> **一句话**：策略生产线现有三本真源——mining_sop_policy（挖矿方法论，止于"挖到候选"）、sop_b_node_loop（单节点回测七步循环，从"对象已注册"起算）、sop_c_strategy_library_intake（外部源码入库漏斗，从"600 条源码已到手"起算）——三本各管一段，**"策略假设怎么生成、因子怎么组装成策略、E4 正考怎么考、负结果去哪里"四段无册**。本报告列缺口清单与建议归宿，禁直改 sop/，归宿由 Owner 裁定。

## 1. 现状覆盖审计（真源证据）

| 段 | 覆盖册 | 起点止点 |
|----|--------|---------|
| 挖矿方法论 | mining_sop_policy v1.4 | 六向寻路→防噪音四闸→矿脉枯竭→挖后自审闸；产出=候选+立卡 |
| 单节点回测 | sop_b_node_loop v1.0 | 前置=对象已在 SOP-A 注册且阈值预注册；①调研→⑦归档三出口 |
| 外部策略入库 | sop_c v1.0 | 600 条聚宽源码→盘点/粗筛/翻译/快筛/去重/入库/挂图/配比；含双窗口及格门槛 |
| 预注册先例 | p3_prereg/（_working） | 封闭族 N_eff/考窗冻结/数据面复核，未升 sop/ |
| E4 正考执行器 | scripts/backtest/f06_e4_wfa_exam.py | 可执行；流程语义散在脚本与战役令，无 SOP 册 |

## 2. 缺口清单（G1-G10，每条=现状证据/风险/建议归宿/优先级）

| # | 缺口 | 现状证据 | 风险 | 建议归宿 | 优先级 |
|---|------|---------|------|---------|--------|
| G1 | **策略假设生成段无册**：新策略从哪来（行情观察/Owner 论点/挖矿候选/外部源码之外的来源）无标准动作；sop_b ①是"节点级算法调研"（≥3 候选算法），不回答"这个策略想法该不该立项" | sop_b §0 前置即要求"已注册"，注册前的立项动作无册 | 想法随手开考，N_eff 失控、留痕断链 | 新增 strategy_mining_sop 或并入 mining_sop 作"策略域实例"（骨架先例 skeleton_mining_policy 同款做法） | 高 |
| G2 | **因子→策略组装段无册**：IC 筛出的因子如何组装成策略（单因子规则化/多因子加权/择时状态挂接/仓位映射）无标准流程与验收；factor_registry 与 strategy_registry 之间的桥没有文档 | 两注册表各自有 schema，无"组装卡"定义；sop_c C6 只管外部源码入库 | 因子→策略的组装随意，考试对象（factor vs strategy）验证层错配（sop_b §2 映射表存在但无组装前置） | factor_mining_sop（本战役 F 车道 v0.1 工作稿）S6-S7 扩篇或独立 assembly_sop | 高 |
| G3 | **E4 正考未 SOP 化**：考什么窗/什么成本/通过线/三态出口散在 f06 脚本+战役令 §2+sop_b ⑥三处；"何时允许点火一次考试"无准入判据 | f06_e4_wfa_exam.py 只可运行不可改；战役令 §2 诚实条款是临时法 | 各车道考试口径漂移；考试结论不可比 | 独立 exam_policy（归宿建议 backtest_system_sop/sop_e_exam.md），与 sop_b ⑥互挂。**已销项 resolved 2026-09-19**：新立 docs/01_policies_and_standards/sop/backtest_system_sop/exam_policy.md（裁定#365） | 高 |
| G4 | **regime 条件化考试条款缺失**：sop_b ④"六段状态"与⑤"分状态不稳剪"存在，但无 PIT 状态轴选定/桶边界 IS 钉死/每因子必报"什么状态下有效"条款 | bizmine 战役 §0 断环结论="没有任何状态×因子条件化考试"；R/F 车道正在用临时条款补 | 考试不看状态→夏普上不去（Owner 论点）；状态轴乱选→选择性报告 | factor_mining_sop §2 条款转正（Owner 裁定归宿）。**已销项 resolved 2026-09-19**：docs/01_policies_and_standards/sop/mining_sop/factor_mining_sop_policy.md §2（裁定#365） | 高 |
| G5 | **复权链断供结论分级规则未入册**：adj_factor 恒 1，一切日线结论=暂定——该规则只活在战役令与车道报告，无 permanent 归宿 | kline_daily.adj_factor 实查恒 1；各战役令重复声明 | 复权修复前后的结论被混用；"暂定"标签丢失 | 诚实条款升 permanent（归宿=backtest_system_sop README 或 data_ops_policy 复权节）。**已销项 resolved 2026-09-19**：并入 exam_policy.md §4（裁定#365） | 中 |
| G6 | **成本双口径声明规则未入册**：引擎现行五项 vs Owner-001 滑点档并存，报告必须写明用哪个——现为战役令临时条款 | matching_logic.py:69-76 / cost_model_calibration.py:229-235 双口径事实存在 | 报告口径混用→结果不可比（红蓝对抗四向之一） | 并入 G3 exam_policy 或 sop_b ⑥注。**已销项 resolved 2026-09-19**：并入 exam_policy.md §3（裁定#365） | 中 |
| G7 | **假设状态机无注册表支撑**：candidate→screening→preregistered→sandbox→exam→verified→dead 的流转无字段定义，各注册表 status 取值各异 | factor_registry status=candidate/…；strategy_registry lifecycle 另一套 | 生命周期审计靠人肉；死因子复活无据 | 注册表 schema 对齐批（属 RULE-SSOT 架构数据，走 apply_*.py，非文档批） | 中 |
| G8 | **零结果/负结果台账未制度化**：另类挖矿 0/5 前科=负结果散落聊天与临时件；"没找到写清排除了什么"只在 sop_b ⑦判死出口 | 无全局负结果台账；本战役首次建 screen_results 全量入册 | 同一死矿被反复挖（重复试错成本）；DSR 校正缺试验次数原料 | 台账 schema 并入 G3 exam_policy（试验次数喂 Deflated Sharpe 的数据基础）。**已销项 resolved 2026-09-19**：并入 exam_policy.md §5（裁定#365） | 高 |
| G9 | **组队备料→配比衔接未文档化**：B-15 Owner 门位（只备料禁部署结论）与 sop_c C6 配比（PP-001 归因定权）之间的交接件无定义 | bizmine R 车道组队备料件为首个实例 | 备料件被误读为部署建议 | sop_c C6 增"备料交接"小节（Owner 门位显式化） | 低 |
| G10 | **数据面复核义务未入册**：P3 先例证明 prereview/上游清单的覆盖声称必须考前实查（consensus"9.6 年完整"实查 2022 后断供），该义务未成文 | p3_prereg/P3-B-NARROWING §5 | 按过时数据面设计考窗→考试作废重跑 | factor_mining_sop S4 第三关转正 | 中 |

## 3. 规范预算与净零声明

按宪法 §4 净零原则：G1-G10 的归宿以**合并增补既有册为主**（G1 并 mining_sop 实例、G3+G5+G6+G8 合并为一本 exam_policy、G4 并 factor_mining_sop、G9 并 sop_c），避免册数膨胀；新立册仅 exam_policy 一本候选。裁决权在 Owner。

## 4. 移交清单

- [x] 本报告落盘 `docs/_working/bizmine_night/factor_sop_screen/`
- [x] 同批产出 factor_mining_sop_v0_1.md（G2/G4/G10 的 v0.1 载体）
- [x] Owner 裁定各缺口归宿（裁定#365：G4 并 factor_mining_sop、G3+G5+G6+G8 合并新立 exam_policy；其余按 §3 归宿另批）
- [ ] 裁定后由对应车道开施工批（禁直改 sop/，走 construction_workflow）

## 5. 销项记录（2026-09-19 施工批，裁定#365）

- **resolved（本批 5 条）**：G3/G5/G6/G8 → 新立 `docs/01_policies_and_standards/sop/backtest_system_sop/exam_policy.md`（净零对账：新立 1 本销 4 条）；G4 → `docs/01_policies_and_standards/sop/mining_sop/factor_mining_sop_policy.md`（v0.1 转正，§2 随迁升 permanent）。
- **载体同批落地**：G10（S4 第三关数据面复核已成 permanent 条款）；G2 部分覆盖（S6-S7 已入册，组装卡 schema 细化按 §3 归宿另批）。
- **未销项（另批施工）**：G1（并 mining_sop 实例）、G7（注册表 schema 对齐批，RULE-SSOT 架构数据走 apply_*）、G9（并 sop_c C6 增"备料交接"节）。
- 施工件：`factor_mining_sop_v0_1.md` 已标 superseded 存档（头部有转正指针）。
