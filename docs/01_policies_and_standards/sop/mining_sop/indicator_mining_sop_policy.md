---
ttl: permanent
doc_type: policy
rule_form: procedural
verifiability: manual
title: 指标挖矿 SOP——TASC 论文定向检索+公式可验证性唯一准入闸+时盒停手立卡（技术指标公式移植入库生产线）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-09-21
topic: mining_sop
---

# 指标挖矿 SOP——学术技术指标移植入库生产线（真源）

> **一句话**：本册把"矿脉定向检索 → 逐轮时盒 → 公式可验证性准入闸 → 立卡施工 → 数值正确性证据链 → 注册表入库"缝成一条指标生产线；面向技术指标族（IND-* 域）的学术/文献指标移植——论文说什么就验什么，**公式可验证性为唯一准入闸**；源断或验不过 = 时盒到点**停手立卡**，禁现场硬凑施工。
> **定位**：[mining_sop_policy.md](mining_sop_policy.md)（通用挖矿方法论：六向寻路+防噪音四闸+矿脉枯竭终止+挖后自审闸）在**指标域**的专用实例，与 [factor_mining_sop_policy.md](factor_mining_sop_policy.md)（因子域）、[skeleton_mining_policy.md](skeleton_mining_policy.md)（骨架域）、[trading_decision_map_pathfinding_policy.md](trading_decision_map_pathfinding_policy.md)（地图域）并列；语义冲突时按域归真源（指标口径归本册，alpha 判据归 factor 册+exam_policy）。

## 0. 晋升声明（正典化记录）

- **正典化日期**：2026-09-21。
- **来源**：`docs/_working/archive/2026-09/tilib_clearance/tilib_clear_a3_mining_report.md`（波3 M-L6 学术自适应指标挖矿报告，2026-09-20 tilib 清欠班实战沉淀）**原册随档**——正文方法论实质全量迁入本册，原册保持 task_bound 战例存档，不改不删。
- **净零声明**：本册 = 通用挖矿 SOP 的指标域实例化 + a3 原册方法论收编，未新立第二套通用挖矿通法（通法仍唯一归 mining_sop_policy）；对价即 a3 原册降为随档战例，一进一出。
- **与 factor_mining_sop 的分工声明（两族互斥不重叠）**：
  - **指标族（本册）** = 技术指标**公式移植入库**：TASC 论文/权威文献 → 可验证公式 → 指标注册表条目+实现列+测试。质量闸只有一道 = **公式正确性**（§4 数值正确性证据链）；准入即入库，**无 IC/回测/考试段**——本册不判 alpha 优劣。
  - **因子族**（[factor_mining_sop_policy.md](factor_mining_sop_policy.md)） = alpha 因子**挖掘考尺**：数据 → 表达式 → 回测 backlog（IC 大海选→预注册→E4 正考→组队），质量闸 = 考试判据（exam_policy）。
  - **互斥边界**：指标入库后其列可被因子表达式**消费**——消费关系不构成重复立卡：因子引用指标列不回指标注册表立条，指标册也不因某指标"预测力弱"判死（那是因子族考试管辖）。同一变换两族都想要时：公式正确性归本册先行，alpha 价值归 factor 册另行立卡，各走各闸。

## 1. 定向检索法（矿脉锚定 + 逐轮协议）

1. **矿脉锚定**：从 TASC（Technical Analysis of Stocks & Commodities）期号谱系入手（作者+年月）锁定新论文清单，再逐篇定向检索公式源。谱系成例：Ehlers Precision Trend（2024-09）/ Linear Predictive Filters+Griffiths 预测器（2025-01）/ 双高通去滞后 Lag Removal（2025-04）/ Adaptive SuperSmoother Improved Filter（MESA）/ Continuation Index（2025-09）/ Auto Tune Filter（2026-05）。
2. **逐轮结构**：每轮一行进挖矿日志（轮｜矿脉方向｜判定｜关键产出）；判定只有两态 **signal / 受阻**；日志随交付件落档，禁无日志交稿（mining_sop_policy 同款铁律）。
3. **公式源权威序**（时盒内按序打满）：
   - ① 作者官网/官方 PDF 原文（成例：mesasoftware.com）；
   - ② 作者技术博客的代码转译全文（成例：financial-hacker.com Ehlers C 转译，系数逐一可核）；
   - ③ 平台官方移植（成例：TradingView Pine）仅作**存在性核对**，不作公式源；
   - ④ 镜像站/聚合站（traders.com、GitHub 镜像）最末——易 403/超时，只配扫尾。
4. **教训回填**：R3 受阻复盘"30 分钟时盒未走官网直连是误判"——时盒内先把权威源直连打满再谈停手；波5 按同配方官网直取 PDF 即清偿（GPRED/CONTINUATION）。

## 2. 时盒停手立卡（铁律）

1. 每轮 **30 分钟时盒硬顶**；到点判定若为受阻（403 / 需 PDF 解析 / 搜索超时）→ **停手**，立卡登记"矿脉方向+死因+下一班配方"，禁现场硬凑施工、禁无限轮换镜像重试。
2. **立卡 ≤3 / 波**（施工容量上限）；立卡字段 = why（TASC 出处+口径+库内缺位证据）+ 产出（列名/工时）。
3. 已立卡未清偿 = 债务留台账"停手/待 Owner"节（成例：Auto Tune Filter 登记债，公式源=mesasoftware The AutoTune Filter.pdf，下一班同配方直取）；扩波清偿须 Owner 追加令。

## 3. 准入闸与防噪音

1. **唯一准入闸 = 公式可验证性**：差分方程/系数可逐行核对才准立卡施工；"只有名字没有式"一律挡在闸外。
2. **通用防噪音四闸照跑**（mining_sop_policy §5，指标域口径）：
   - 来源可溯：TASC 期号/年月 + 公式源 URL 全部落档；
   - 交叉验证：系数与作者正典式一致（成例：HighPass3 系数对上 Ehlers Cycle Analytics 的 exp(−1.414π/L) 族）；
   - A 股适配：纯单标的 OHLCV 确定性变换优先（T+1/涨跌停不影响口径）；引入外部状态/盘中数据的当场记 skip 及原因；
   - 可回测+数据可得：输入列在位（成例：只需 close，kline_daily 在位）。
3. **库内同义扫描**（防重复立条，立卡前必查）：对注册表既有条目做口径覆盖扫描，同义不立——先例 LINEARREG_BAR=linearreg、PSL=PSY、MSW=ht_sine（同一列两条目违反唯一性，ALGO 去重 gate 硬拦）；既有均线/滤波族不覆盖新口径才准立（成例：SuperSmoother/HighPass 库内缺位，hma/zlema/kama 不覆盖其口径；ht_dcperiod 已有 → 瞬时频率族不重复立条）。

## 4. 数值正确性证据链（质量闸语义，入库必过）

1. **黄金参照**：有 TA-Lib 对应的逐位对照（0.0 偏差 / golden 1e-12~1e-13 级）——TA-Lib **仅测试用**，生产代码保持零 TA-Lib 依赖（设计 memo §2 口径）。
2. **双实现互证**：无 TA-Lib 对应的用两条独立实现路径互证（成例：SUPERSMOOTHER/HIGHPASS/PTREND 互证 1e-12）。
3. **性质测试**：文献公式移植无参照时，用性质测试钉行为（常数输入恒等 / 单调收敛 / 正弦周期恢复；成例：GPRED 正弦领先 corr=0.9462）。
4. **手工微样本**：小样本手算值写死进测试，防全链路同源盲区。
5. **全量回归**：目录测试 ×2 轮通过才准入库提交；证据随测试落档（[亲验] 级数值须复核留痕）。

## 5. 入库与产物

- **产出三件套**：指标注册表条目（真源=`docs/01_policies_and_standards/_registry/catalogs/technical_indicator_registry.yaml`，REG-IND-001，unique_key=indicator_id）+ 实现列（schema 同步走既定配方）+ 测试文件。
- **提交**：一律 GitCommitGateway / git_commit.py 正门，改前 claim、毕后 release；提交后 `git log -1 --name-only` 核实归属。
- **台账**：每波向战役台账追加一行（波次｜指标｜commit｜测试数｜状态）；受阻与立卡债落"停手/待 Owner"节。

## 6. 实战回填记录

| 日期 | 先例 | 回填段落 |
|------|------|---------|
| 2026-09-20 | tilib 波3：R1-R4 逐轮日志+三卡全施工（Precision Trend/SuperSmoother/HighPass3，双实现互证 1e-12+手算微样本） | §1/§3/§4 |
| 2026-09-20 | R3 受阻停手立卡（traders.com 403 / mesasoftware PDF 未解析 / GitHub 镜像超时，30 分钟时盒到点即停）+复盘"未走官网直连是误判" | §2/§1.4 |
| 2026-09-20 | 库内同义剔除三先例（LINEARREG_BAR/PSL/MSW）与缺位判定（SuperSmoother/HighPass 立条） | §3.3 |
| 2026-09-20 | 波5 官网 PDF 直取清偿（CONTINUATION/GPRED，IND-CYC-007/008；性质测试正弦恢复 corr=0.9462） | §1.3/§4.3 |
| 2026-09-21 | 本册晋升（a3 原册收编随档 + 与 factor_mining_sop 分工划界） | §0 |
