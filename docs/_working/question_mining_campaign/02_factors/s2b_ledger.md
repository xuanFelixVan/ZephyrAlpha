---
ttl: task_bound
title: S2b 因子挖矿台账（后半：factor_registry 第 89~175 因子 + 两类横切）· st-pqmine-20260927
agent: S2b
date: 2026-09-27
status: 挖干（登记面+账实面）+ 出题待考（实证面）
---

# S2b 挖矿台账

## 一、探了什么（矿区与路径）

| 步骤 | 动作 | 结果 |
|------|------|------|
| 1 | 读 00_charter.md / results_all.yaml（前 100 行学五要素）/ RETIREMENT_REGISTER.md（30 题退役名单+禁翻案铁律） | 完成 |
| 2 | 解析 factor_registry.yaml（12612 行，175 条目），取按出现序第 89~175 因子（FCT-EVENT-003~017/SENT-006~028/LIQ-034~062/QUAL-001~002/MOM-029~030/INTRADAY-029~030/FQ-001~006/GR-001~002/EXP-001~006）全字段 | 完成 |
| 3 | 本段 87 条 22 个 schema 字段完整度统计 + 三段结构识别（概念批 89~143 无代码无 IC / 已实现批 144~156 有符号无 path / 代码锚批 157~175 双锚+14 个有 IC） | 完成，事实见下 |
| 4 | 账实双向核验：31 个 code_symbol 逐个打开实现文件正则匹配 def/class 符号 | 31/31 全部可解析（正向账实干净，反向 code_path 断链 13 条） |
| 5 | 头部规则重算：algorithm_status 推导规则（L10）逐条复算 | 本段违例 21/87（S2a 段 0 违例——同规则两段对照） |
| 6 | 外键核验：benchmark_registry.yaml（9 个注册 ID）/ benchmark 沪深300 正名 L81 alias L84 | EXP 族 6 条 benchmark_id=BMK-INDEX-000300 未注册 |
| 7 | 词表核验：v2.0 标签词表（L11）逐 tag 比对 | 词表外 3 值 25 条目次（44号升级×12/市场级择时×12/换手×1） |
| 8 | doc_ref 可回查性：全仓 glob（44号*/ICBATCH_report.md/29_factor_strategy_extraction.md） | 17/87 悬空（"44号"×13、"ICBATCH_report.md"×4） |
| 9 | PIT-数据类错配关键词审计 + pit_policy 枚举归一化扫描 | price_only 错配 5 条；publish_date 5 种写法（3 条括号注释） |
| 10 | strategy_registry.yaml 跨表 FCT-* 引用 regex 全扫 | 7 处引用全落本段（INTRADAY-029×4/030×1/MOM-030×2），belongs_to_strategies 回填 0/3——闭合 S2A-009 开放后半 |
| 11 | 283 既有题去重：grep FCT- 零命中；退役 30 题逐簇对照（均线斜率/尾盘主买/PEAD/股东户数/宽度拐点/波动状态/加密传导/EP） | 零同义题；涉已退役簇条目（EVENT-014/MOM-029）仅出账实自洽面 |
| 12 | 与 S2a 草稿（已产出 s2a_candidates.yaml）逐题对读去重 | 7 对同族异段互补对（见 §五），违例集不相交 |
| 13 | meta_question 枚举确认（VALID_LAYERS=L0..L6 / statuses 含 draft / frequencies 7 值 / origins=manual 类） | 完成；layer 语义按 chain_piling_campaign/01_layer_charter.md：登记治理=L6、因子评估=L4、数据依赖=L1 |

**未做**：CH 数据实证零调用。理由：①本段出题面以登记账实/口径自洽为主（28/29 题的 threshold 只需读注册表或做结构比对即可机判）；②S2B-018/027 的相关性补算属复考阶段动作，判据已写进 threshold；③闭卷纪律下不重跑任何已退役簇的 IC。

## 二、核心事实（全部 file:line 可回查）

**本段三段结构**：89~143 概念批（55 条：EVENT/SENT/LIQ/QUAL-001，无 code 无 IC，多为经验规则/操盘手法）；144~156 已实现批（13 条 SENT-016~028，code_symbol 有而 code_path 空）；157~175 代码锚批（19 条，双锚齐 18 条+MOM-030 无代码，ic 非空 14）。

1. **全池横切（175 口径）**：ic 14/175、correlation_group 0/175、redundancy_status 0/175、null_rate/drift_psi/last_quality_scan_at 0/175、code_fingerprint 0/175、decay_halflife 1/175（QUAL-002=2 且 method/scan_at 双空）、last_decay_scan_at 0/175。
2. **algorithm_status 推导规则（L10）违例 21/87**：code_path 非空应=quantized 实=None 18 条（157~175 段）；LIQ-046(L9550)/LIQ-057(L10364) 无代码而=quantized；MOM-030 应=pending_backtest 实=None。S2a 前 88 段同规则 0 违例——规则在代码落地批批量失守。
3. **登记五要素缺口**：tags 空 22/87（19 代码锚+EVENT-004/SENT-008/LIQ-039）；params={} 78/87。
4. **doc_ref 悬空 17/87**："44号 §…"×13（全仓无 *44号* 文件）、"ICBATCH_report.md（2026-08-24）"×4（全仓零命中）；对照 docs/_archive/29_factor_strategy_extraction.md 存在。
5. **benchmark 外键悬空 6/87**：EXP 族 benchmark_id=BMK-INDEX-000300 未注册（benchmark_registry.yaml 仅 9 ID，沪深300=BMK-INDEX-001，alias 含 000300，L81/L84）；universe UNI-RULE-001 全库命中无悬空。
6. **regime 强制项倒挂**：regime_valid 填 9/87 全在概念批（SENT-008~012/LIQ-041/042/048/061），regime_invalid 全库 0/175，已落地代码的 SENT-016~028 批两字段全空——落地批比概念批更缺标注。
7. **双向锚定反向断链**：SENT-016~028 的 13 条 code_symbol 非空而 code_path=''；正向符号解析 31/31 通过（futures_basis_monitor/option_sentiment/market_sentiment_analyzer/sector_divergence/momentum_factor/value_factor/intraday_snapshot_factors/fundamentals/expectations 全部命中 def/class）。
8. **ic=null 三义性实例**：EXP-002 last_evaluated_at=2026-09-16+evidence 记 data-gap（IC=NaN，research_report 预测槽位快照语义污染）与 EXP-001/003/005 未评估在 ic 字段不可区分（本段 evaluated 15 vs ic 14 的差=1 即它）。
9. **FQ-003(L12145) 状态-证据矛盾**：status=deprecated 而 evidence 记"未达晋级门槛，保持 candidate（不删条目）"，无变更事由——全库唯一 deprecated 即违例。
10. **晋级链路正面基线**：FQ-001（L12101 IC=+0.0284/t_p=0.0014/覆盖98.8%）、FQ-002（L12140 +0.0246/0.0046/99.4%）按 L21 预注册门槛忠实晋级且 OOS 未达线如实记录；FQ-004/GR-001 走 L25 域条件化条款，params.domain 结构化（axis=market_cap_tercile+buckets）+域内达标留痕——S2B-016 预判 pass。
11. **OOS 复核条款缺口**：生命周期五态（L19-20）与晋级门槛（L21）无任何 OOS 判据节点，而 FQ-001/002 的 OOS 2024+ IC=0.0061/0.0077 均未达线。
12. **去马甲执行不对等**：FQ-002 对 FQ-001 有相关性留痕（0.2813<0.85），而 INTRADAY-029/030（IC -0.0174/-0.0182、turnover 同 0.0637、同文件）与 LIQ-049(L9772)/057(L10364)（057 formula 自述"与 F8.29 并列"却 variant_of=null）零留痕；全库 variant_of 非空仅 SENT-028→SENT-020 一例（正例）。
13. **PIT 错配 5 条**：EVENT-014 PEAD（L7624，财报公告）、LIQ-058（融资+北向）、QUAL-001（业绩预告/一致预期）、EVENT-006（利率汇率）、EVENT-003（公告/研报）——pit_policy=price_only；正确对照=本段 FQ 族 8 条 statement_announce_date + EXP 族 publish_date。
14. **pit_policy 枚举漂移**：publish_date 5 种写法（EXP-001/002/003 括号注释长文案+全半角括号混用）。
15. **inputs 断链**：31 个已实现因子仅 SENT-028（L11785）inputs 非空；EXP-002 的 data-gap 事故即上游依赖不可追溯的实害案例。
16. **换手/容量无字段化口径**：turnover 非空 4（MOM-029=0.5345 高换手）、capacity 非空 4（2.18/0.28/8.08/8.1 无单位；唯一线索=MOM-029 evidence"10%ADV20 约束均值 2.18 亿"）；FQ 族 SOP-B6 成本回测（can_deploy 判定）仅存散文。
17. **direction 占位未校正**：14 个有 IC 因子 direction 全 None（MOM-029 IC=-0.0634/IR=-0.4079/oos_pos=0.45 而方向字段缺失）。
18. **消费账反向断链**：strategy_registry 引用 7 处全落本段三因子，belongs_to_strategies 本段 0/87 回填——闭合 S2A-009 遗留的后半题（S2B-029）。

## 三、产出

- `s2b_candidates.yaml`：**29 题草稿**（S2B-001~029），格式与 S2a 对齐（candidate_id/layer/status/frequency/origin/question/threshold/min_confidence/expected_outcome/dedup_note），root=top-level sequence（与 s2a_candidates.yaml 同构）。
  - 甲 横切①全池覆盖率（175 口径，S2b 专责）：6 题（001-006）
  - 乙 横切②登记账实：14 题（007-015、019、021、026、028、029）
  - 丙 经典六面：有效性 2（018/027）、衰减 2（004/025）、容量 1（024）、换手成本 1（023）、相关簇 4（005/018/019/027）、数据依赖 2（020/022）
  - 层分布：L6×25 / L4×3 / L1×1；frequency：static×1 以外 monthly/weekly/quarterly 为主
- 三态预期：expected_fail 27（登记侧缺口）、expected_pass 1（S2B-016 晋级链路正基线）、政策缺口确认 1（S2B-017 OOS 条款）。
- 枚举合规：status=draft、frequency∈{weekly,monthly,quarterly,static}、均经 meta_question_registry.py 词表加载源核实。

## 四、自审三态（charter §五）

| 维度 | 态 | 说明 |
|------|-----|------|
| 登记完整性+账实面 | **挖干** | 本段 87 条 22 字段全统计、31 个 code_symbol 逐个开文件核验、全池横切字段 175 口径穷尽、跨表外键/词表/引用全扫；违例清单穷尽，无"还有几条坏账"未知项 |
| 实证面 | **未干（设计完毕、待考）** | S2B-018/027 的秩相关补算、S2B-016 的 evidence 数值复核等判据已机解化，数字结论须复考阶段现算——挖矿阶段交付"可考的题"即产出 |
| 受阻项 | **零受阻** | 未跑 CH 实证系主动避让（复考阶段+S1 界）；"44号"批原文若在库外（微信群文档），S2B-009 的 fail 结论不受影响（可回查性本身就是考点） |

**六向速记（挖干判据）**：真源=FR yaml（REG-FCT-001，schema v2.1，permanently active）；写者=MOD-GOVERNANCE（本段全部 owner=MOD-GOVERNANCE，87/87）；消费者=strategy_registry（7 处引用）+410 面板/信号管线（code_symbol 31 条）；漂移史=三段结构即三次入库潮（08-15 翻译拆解/08-22 44号升级/08-30~09-16 代码锚回填），漂移=派生字段失养 21 条+悬空 doc_ref 17 条；冲突面=与 S1（数据源）、S3（策略消费）、90_consolidated（汇总去重）三界，已用 dedup_note 显式切分；净零方案=不新增字段者修账（回填/清洗/挂链），需新增者（eval_status/cost/unit/eval_window）已在题面声明替代旧的散文承载，供 Owner 门位裁决。

## 五、与 S2a 的同族异段声明（7 对互补，违例集不相交）

| S2b | S2a | 关系 |
|-----|-----|------|
| S2B-007（推导规则 21 违例 fail） | S2A-008（0 违例 pass 基线） | 同规则两段对照，合并=全池结论 |
| S2B-008（tags 22/params 78） | S2A-001（params 85/tags 1） | 同门异段 |
| S2B-012（落地批 regime 全空倒挂） | S2A-006（翻译批 39.8%） | 同条款异批 |
| S2B-020（错配 5 条含正确对照） | S2A-004（88/88 齿轮占位） | 同审计异段 |
| S2B-022（已实现 31 条 inputs） | S2A-007（前 88 仅 CRYPTO 3 条） | 同字段异前提 |
| S2B-006（枚举外 5 条+size 零使用+前缀模式） | S2A-002/003（枚举外 3 条+id 错位 1） | 同域异违例集 |
| S2B-029（被引 3 因子回填 0/3，闭合其开放后半） | S2A-009（前 88 零被引自洽 pass） | 显式交接题 |

其余 22 题与 S2a 28 题无对象/判据重叠（S2a 有效性实证题 012~019 落在前 88 段具体因子，本段无同义面）。

## 六、与退役 30 题的隔离声明（禁翻案自查）

- 逐簇对照 RETIREMENT_REGISTER.md：均线斜率族（PQ-0011/0110-0112）、尾盘主买族（0113-0115）、EP（0023/0024）、股东户数（0028/0088）、加密费率传导（0029/0048）、波动状态族（0046/0081）、宽度拐点（0082）、板块动量自相关（0039）、PEAD（0122-0124）、情绪极值（0037/0091）**零复考、零换参重跑**。
- 两题涉近邻已显式切分并写入 dedup_note/pit_note：S2B-020（EVENT-014 只审 pit_policy 声明自洽，不跑 PEAD 任何 IC）；S2B-028（MOM-029 只审 direction 字段与已存 IC 的符号自洽，≠均线斜率族合成信号、≠动量择时叠加）。
- 若实证题复考产出 no_alpha 证据，按增补令#5 如实登记退役、禁修参翻案——题面已按此预期措辞。

## 七、移交接办

1. 90_consolidated 汇总时：29 题实测预填数字可直接当 expected_outcome 锚点（预计 fail 27/pass 1/政策缺口 1）；同族 7 对建议按"合并为全池单题"或"两段双题保留"显式裁定，勿静默去重。
2. S2B-017（OOS 条款缺口）与 S2B-014（eval_status 字段）属规则/schema 增补类，走新规则入库闸（Owner 门位），非 exam_loop 可闭环。
3. 注册时 PQ 号顺延（PQ-0284+），candidate_id→q_id 映射由 intake 正门机生；S2A-009 的开放后半由 S2B-029 正式闭合，汇总时两题应合并判读。
4. "44号"批原文（SENT-016~028 的 13 条出处）需 Owner 或档案侧补归档，S2B-009 复判依赖。
