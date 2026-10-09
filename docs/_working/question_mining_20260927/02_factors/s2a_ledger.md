---
ttl: task_bound
title: S2a 因子挖矿台账·收口版（factor_registry 第 1~88 因子）· st-pqmine-20260927
agent: S2a（重拉瘦身收口版）
date: 2026-09-27
status: 挖干（登记面）+ 出题待考（实证面）+ 收口完成（20 题）
---

# S2a 挖矿台账（收口版）

## 〇、本轮定性（重拉说明）

前次 S2a 运行在 API 限频中断前**已完整写出 28 题初稿与台账**（文件当时已落盘）。本轮为瘦身重拉：
不重复挖矿，改为【逐项机器复核初稿全部事实锚点 → 按新目标（15-20 题、族级优先）裁剪收口 → 修正复核发现的错漏】。最终交付 20 题，原编号保留（S2b 稿 dedup_note 的 S2A-xxx 交叉引用不受影响）。

## 一、探了什么（矿区与路径）

| 步骤 | 动作 | 结果 |
|------|------|------|
| 1 | 读 00_charter.md / results_all.yaml（学五要素格式）/ RETIREMENT_REGISTER.md（30 题退役名单+禁翻案铁律） | 完成（两轮均做） |
| 2 | 解析 factor_registry.yaml（12612 行，175 条目），取按出现序前 88 因子全字段 | 前次完成；本轮复核 |
| 3 | 前 88 因子 22 字段完整度统计 | 前次完成；本轮 python 逐项复算吻合（见 §二） |
| 4 | factor_class 枚举合规 + factor_id 前缀↔class 一致性 | 前次完成；本轮复核吻合 |
| 5 | doc_ref 锚点在 docs/_archive/29_factor_strategy_extraction.md 回查 | 在库可回查（本轮复核 archive 存在） |
| 6 | strategy_registry.yaml 跨表 FCT-* 引用扫描 | 本轮复核：MOM-030×2/INTRADAY-030×1/INTRADAY-029×4，与前次记录逐一吻合 |
| 7 | 283 既有题 + 退役 30 题关键词去重 | 前次逐词核对（见各题 dedup_note）；本轮抽检退役簇切分成立 |
| 8 | meta_question 枚举核实 | 本轮以 data/capability_cards/meta_question_registry.yaml input_schema 为准：layer L0-L6 / status 含 draft / frequency={daily,weekly,monthly,quarterly,event,realtime/static} |

**未做**：CH 数据实证（DatabaseService reader）零调用。理由：①前 88 因子 code_path 全空，任何实证题都须按 formula 现场构造，属复考阶段动作而非挖矿阶段；②数据覆盖率实证与 S1 矿区（01_sources）重叠，避让；③闭卷纪律下实证题的判据已写进 threshold，留给 exam_loop 执行。

## 二、本轮复核结果（对前次初稿的事实审计）

1. **全部吻合**：front88 边界（INTRADAY-015 起、EVENT-002 止，共 88）；code_path/code_symbol/belongs_to_strategies/regime_invalid 空 88/88；params/inputs/evidence/outputs 空 85/88（仅 CRYPTO 3 因子填）；regime_valid 空 53/88；tags 缺 FCT-MOM-010；pit_policy 88/88='price_only'；lookback_period 85/88=1；枚举外 class 3 例（TECH-069 risk_rule L2360 / TECH-070 technical_indicator L2435 / MOM-002 knowledge_only L4434）；MOM-015 class=sentiment（id-class 错位）；CRYPTO-VOL-001 params={lookback_days:20, annualization_factor:365}；20 个抽查 file:line 锚点全部命中；strategy_registry 交叉引用计数吻合。
2. **修正 1——锚点**：FCT-MOM-008 块首实际在 L4879（初稿写 L4878~4880），S2A-012/022 已改为 "L4879 起"。
3. **修正 2——枚举**：input_schema frequency 词表为 `event`（无 event_driven），S2A-015/019 已改 frequency: event。
4. **软化 1**：doc_ref 可回查结论由"100% 机器验证"改为"在库可回查"（本轮复核方式为 archive 存在性+锚点抽样，未逐条复算 87 锚点）。
5. reaper 存活（scanned=0/killed=0，非"计划任务不存在"态；仅有 ALERT-SYS-001 系统水位告警，不阻断文档写入）。

## 三、产出（20 题，S2A-001~026 缺 003/008/014/016/017/018/027/028）

- `s2a_candidates.yaml`：20 题草稿，全五要素+threshold 可机解+origin file:line。
  - 甲 登记完整性/依赖在册（static）：6 题（001/002/004/005/006/007/009 中 003、008 被裁）
  - 乙 相关簇/去马甲（族级）：2 题（010 量能族 6 因子、011 均值回归子簇 3 因子）
  - 丙 有效性：4 题（012 PTH/013 缺口回补标定/015 连板周期律/019 议息断言——均带登记原生可证伪数字）
  - 丁 衰减/容量/换手成本：3 题（020/021/022，覆盖 charter 六面②③④）
  - 戊 数据依赖（族级）：5 题（023 分时族 14/024 ETF 族/025 研报底座/026 加密族声明，027 并入 026）
- 预期 fail/pass 分布：登记面 7 题预判 fail（001/002/004/005/006/007 + 009 后半），实证面以"待考+预判"如实标注；无 insufficient 型废题。

## 四、裁剪记录（8 题摘要留存，供汇总方按需复活）

| 被裁题 | 考点一行摘要 | 裁剪理由 |
|--------|-------------|---------|
| S2A-003 | id 前缀↔class 一致性（错位仅 MOM-015 1 例） | 单例低信息量，事实已录入 002/004 的 origin |
| S2A-008 | algorithm_status 派生规则前 88 段零违例（pass 基线） | 唯一 pass 型登记题，发现价值最低；规则违规面由 S2B-007（89+ 段 21 例）单腿即可成立 |
| S2A-014 | RSI6<20 裸信号反弹率+ADX 门控增益 | 教科书型，同类登记原生数字题（013/015/019）信息量更高 |
| S2A-016 | 板块拥挤度>90 分位+动量衰减→回撤>60% | 拥挤度两腿中融资腿缺数据，仅子集可复算，判据不完整 |
| S2A-017 | 科技 vs 老登跷跷板（ρ<0 占比>50%） | 阈值系挖矿自设非登记原生，出处强度弱于保留题 |
| S2A-018 | 地量（250 日<5% 分位）见底两腿检验 | 事件稀疏（n≈20-40）检验功效低，登记原文自认"不等于见底" |
| S2A-027 | BTC 波动阈值 80%/40% 分位-绝对二义声明审计 | 与 S2A-026 同族同性质（登记声明完备性），考点已并入 026 题面 |
| S2A-028 | 均线排列 9 态状态机日频翻转率>20% | 单因子成本面，丁面已有 3 题覆盖④；考点独立性强，列为第一候补 |

## 五、自审三态（charter §五）

| 维度 | 态 | 说明 |
|------|-----|------|
| 登记完整性面 | **挖干** | 前 88 因子 22 个 schema 字段全部统计并经第二轮独立复算，违例清单穷尽；89+ 段属 S2b 界 |
| 实证面 | **未干（设计完毕、待考）** | 13 题实证/结构题的判据已机解化，数字结论须闭卷窗数据现算——出"可考的题"即挖矿使命 |
| 受阻项 | **零受阻** | 未跑 CH 实证系主动避让（S1 界+复考阶段）；无 insufficient 型废题 |

## 六、与退役 30 题的隔离声明（禁翻案自查）

- 出题全程对照 RETIREMENT_REGISTER.md：均线斜率族（PQ-0011/0110-0112）、尾盘主买族（0113-0115）、EP（0023/0024）、股东户数（0028/0088）、加密费率传导（0029/0048）、波动状态族（0046/0081）、宽度拐点（0082）、板块动量自相关（0039）、PEAD（0122-0124）**零复考、零换参重跑**。
- 近邻显式切分已写入 dedup_note：S2A-026（BTC 登记声明审计≠波动状态预测力）、S2A-019（议息断言检验≠SL-A10 方法论重放）、S2A-020（IC 衰减匹配≠PQ-0081 波动 AR1 半衰期）。
- 若实证题复考 fail(no_alpha)，按增补令#5 如实登记退役、禁修参翻案——题面已按此预期措辞。

## 七、移交接办

1. 90_consolidated 汇总时：登记面题（001~009 组）实测预填数字可直接当 expected_outcome 锚点（预判 6 fail + 009 前半 pass）。
2. S2b（89~175 段）与本稿的互补关系已在各 dedup_note 标注（006↔B-012、007↔B-022、010/011↔B-005/018/027、020↔B-004、021↔B-024、022↔B-023）；合并后构成全池结论。
3. 注册时 PQ 号顺延（PQ-0284+），candidate_id→q_id 映射由 intake 正门机生；frequency=event 两题（015/019）入 intake 时对齐词表已核。
