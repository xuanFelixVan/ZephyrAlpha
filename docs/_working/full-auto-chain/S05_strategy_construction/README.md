---
ttl: task_bound
title: S05 策略构造与翻译挖矿文档
session: st-fullauto-20260915
date: 2026-09-15
---
# S05 策略构造与翻译（策略工厂 E3 段）

## 1 现状盘点（自动化状态+file:line 证据）

**结论先行：公式轨（C/C2）构造已全自动实弹（1 件落地）；假说轨（B/D）C3 翻译 MVP 已通（5 条台账）但只覆盖"可公式化子集"；翻译产能（5 条/周）与表达式空间（7 特征）是双瓶颈；creation_token 登记硬编码会话号是无人值守卫生隐患。**

### 1.1 两条构造轨
- **公式轨（已自动化）**：`factory_intake_pipeline.py auto_construct` L152-226——只处理 C/C2 台账（`_CONSTRUCT_LANES` L149）；E2 过审集直查 CH `_e2_passed_by_channel` L229-249（**不可达=空集 fail-closed 不构造** L248-249）；`validate_expr` 白名单校验 L198；幂等=constructed_manifest 已登记跳过 L163-168/191-193；生成考卷件 `generate_strategy_file` L205；creation_token 自动登记 L206-214（`scripts/governance/d3_metadata/batch_creation_tokens.py --created-by st-facbe-20260914`——**会话号硬编码**）；manifest 追加 L215-223。
- **假说轨（MVP 已自动化）**：`hypothesis_translator.py`（MOD-BT-190）：种子 SQL L57-61（`verdict='precheck_passed' AND birth_channel IN ('D','B') ORDER BY prechecked_at DESC LIMIT {limit}`，默认 `--seeds 5`）；E0 问闸 L155（local 轻档）；LLM 结构化翻译（translatable/expression/mechanism/top_n）L180-195；**DSL 校验失败纠错重试一次** L197-210；表达式级去重 L171-179/218-220（跨假说同式只出一张考卷）；非退化 sanity（常数/非有限→阴性）L222-229；不可公式化**如实记阴性** `_negative` L262-269（refusal_reason：模型拒翻/parse_fail/dsl 错误/eval 异常/degenerate_constant/dup_expression）；台账 translated_manifest.csv 只追加 L249-256。

### 1.2 机械翻译桥（MOD-BT-159）
- `factor_strategy_template.py`：模板填空零逻辑 L52-111（表达式/ID/参数=唯一自由度，build 统一由 `build_factor_weights` L120-170 承载）；**生成即编译自检** L211（`compile(content,...)`）；STRATEGY_ID=FACT-<md5_8> 内容寻址 L114-117；universe=窗内成交额 top40 与挖矿面板同口径 L192-201；特征工程单一真源锚=MOD-BT-155（`compute_features_importable` L185-189，FEATURES==7）。
- 产物：scripts/backtest/translated/c4_fact_*.py（D1-D5 差异声明为模板固定五条 L104）。

### 1.3 实弹证据与触发
- constructed_manifest.csv：**1 行**——CAND-32e5c7444cc0（C 车道）→ FACT-32e5c744 → c4_fact_4b200528.py（2026-09-15T03:39Z）。
- translated_manifest.csv：**5 行**——1 条 B 动量假说 + 4 条 D 三高环节假说（含阴性/阳性混合）。
- translated/ 目录 c4_*.py 共 **84 件**（含人工翻译存量+机器 fact 件）。
- 触发：FactoryLaneC 周六 10:00 依次 `construct` → `translate --seeds 5`（run_factory_lane_c.ps1:33-35）。

## 2 六向挖矿日志表

| 轮 | 方向 | 矿脉 | 判定 | 关键产出 |
|----|------|------|------|---------|
| 1 | ①上游 | E2 种子供给产能 | signal | 假说轨每周 LIMIT 5 条（ps1 硬编码 --seeds 5）；E2 过审存量持续增长时积压线性恶化；公式轨无上限（幂等全量） |
| 2 | ②下游 | 考卷件→C4 衔接 | signal | 构造件命名 c4_fact_*/c4_*.py 被 `c4_batch_screen.discover()`（L88-89）全量收卷；translated_manifest 与 strategy_screen 幂等独立（靠文件名四键判重），无跨台账核对件；c4_deferrals.csv 挂起行机制在 E4 侧承载 |
| 3 | ③机制 | NL→可执行策略可靠性（全网） | signal | QuantCode-Bench arxiv.org/abs/2604.15151（Khoroshilov et al.，2026，400 任务 Backtrader 基准：最强模型单轮通过率 70-76%、pass@5 仅 43%，蓝图已引并据此设计验收集+重试环）+ github.com/LimexAILab/QuantCode-Bench；HKUDS/Vibe-Trading（75+技能/452 因子，蓝图引）；RD-Agent(Q) arxiv.org/abs/2505.15155（2025，因子-模型双优化闭环） |
| 4 | ④后端 | 表达式空间与语义保持 | signal | FEATURES==7+白名单算子（lane_c_formula_miner.py:52-53 fail-closed）；**假说 horizon/universe 字段翻译即丢失**（prompt 输出约束只有 expression/mechanism/top_n，考卷语义固定日频 top_n 等权）——事件驱动/多腿/基本面假说只能阴性（L29-31 边界声明） |
| 5 | ④后端 | creation_token 登记链路 | signal | auto_construct L211-213 `--created-by st-facbe-20260914` 硬编码：无人值守周批会持续把 token 记到死会话名下（审计失真）；hypothesis_translator 生成件反而**无 token 登记调用**（依赖模板件入目录前登记的不变式声明 L14，周批无人执行） |
| 6 | ⑤前端 | 构造漏斗呈现 | noise | 无 E3 漏斗面板/翻译成功率报告页；登记不施工（归 S12/S13） |
| 7 | ⑥数据字段 | 去重粒度 | signal | 表达式级去重=字符串精确匹配（L218）：语义等价不同写法（如 ret_5d vs close/close.shift(5)-1）不去重 → 同因子多考卷浪费 E4 算力；D1-D5 差异声明模板化固定，逐策略语义未生成 |

**计数：signal 6 / noise 1 / 受阻 0**（全网搜索 1 次命中，无 429）。

## 3 业界与开源对照

- **可靠性基准**：QuantCode-Bench（arXiv 2026）证实 NL→可执行策略不能一次成型——本项目"白名单 DSL 约束+纠错重试一次+非退化 sanity+E4 独立考试"四件套与业界"约束生成+验证重试"惯例一致；差距=本项目仅重试 1 次（业界普遍 2-3 次+编译反馈循环），且验收集（35 条人工翻译）未入自动回路做回归。
- **语义保真**：RD-Agent(Q)（2025）与 Vibe-Trading（HKUDS）都强调假说→因子→代码的中间表示可追溯；本项目 translated_manifest 保留 hypothesis 原文+expression+mechanism 三件，溯源链完整度业界水平；horizon 丢失是保真缺口。
- **防幻觉边界**：本项目"不可公式化如实记阴性、禁硬翻"（L26-31）比业界普遍的强制翻译更保守，符合 Owner 北极星（宁窄勿错）；阴性台账=后续表达式空间扩展的复翻素材库（现无复翻机制，见 S05-G2）。
- A 股适配闸：模板固定 T+1 收盘执行+冻结土规成本（引擎侧），不做空——适配成立。

## 4 堵点与欠账清单

| # | 堵点 | 证据 | 断链等级 |
|---|------|------|---------|
| 1 | **假说轨翻译产能 5 条/周**，E2 过审积压时消化不及 | run_factory_lane_c.ps1:35（--seeds 5） | 中（S05→S06 吞吐瓶颈） |
| 2 | **creation_token --created-by 硬编码死会话号**；且假说轨生成件无显式 token 登记调用 | factory_intake_pipeline.py:211-213 | 中（治理审计失真，CREATE-GUARD 合规风险） |
| 3 | horizon/universe 假说字段翻译即丢失，考卷语义退化为统一"日频 top_n 等权" | hypothesis_translator.py:67-84（prompt 输出 schema 无 horizon） | 中（语义保真） |
| 4 | 表达式语义等价不去重（字符串精确匹配） | hypothesis_translator.py:171-179 | 低（E4 算力浪费） |
| 5 | 事件类/多腿假说无翻译路径（阴性归档后无复翻触发器） | hypothesis_translator.py:26-31 | 低（边界声明内的欠账，等表达式空间扩展） |
| 6 | 纠错重试仅 1 次；验收集（35 条人工翻译）未做自动回归 | hypothesis_translator.py:197-210 | 低 |
| 7 | D1-D5 差异声明=模板五条固定文案，非逐策略生成 | factor_strategy_template.py:104 | 低（E4 判定书可读性） |

## 5 施工项建议（具体到文件/函数/验收标准）

| 项 | 内容 | 验收标准 |
|----|------|---------|
| S05-G1 | creation_token 登记参数化：auto_construct L211-213 `--created-by` 改为 `st-factory-weekly`（或读环境变量/调用方传入）；同时给 hypothesis_translator 生成件补 batch_creation_tokens.py 调用 | 周六自动构造后 `creation_token` 注册表新增记录 created_by=任务身份；token 覆盖率=translated 新增 100% |
| S05-G2 | 翻译产能与复翻：ps1 `--seeds` 提至 15-20（配合 E0 轻档）；translated_manifest 增加阴性复翻——`run_translate` 支持消费 `translatable=false AND refusal_reason IN (dsl_*, eval_*)` 的历史行重试 | 连续两周 E2 过审假说积压不增长；dsl/eval 类阴性行有第二次判定 |
| S05-G3 | horizon 进考卷语义：翻译 prompt 输出 schema 加 horizon（5/10/20 日），`factor_strategy_template.build_factor_weights` 增 holding_days 参数（T+1 进 T+h 出）与引擎对齐 | 生成考卷件含 HORIZON 常量；_c4_engine.run_backtest 按 horizon 结算不报错 |
| S05-G4 | 语义等价去重：表达式先规范化（AST 归一化/算子交换律排序）再哈希判重，替换 L218 的字符串比对 | ret_5d 与其等价写法只出一张考卷（单测覆盖 3 组等价式） |
| S05-G5 | （挂起排期）验收集自动回归：35 条人工翻译做翻译器回归基准，每次 prompt/模型变更后跑——解锁条件=翻译器配置进入变更频繁期 | —— |

## 6 封矿结论

- **矿脉封矿**：7 轮后新矿脉只剩长尾（多模型复核、中英假说混合），登记待后续；连续两轮 noise 未达成但候选均已挂起/施工覆盖，封批。
- **方案封矿**：无。E3 双轨（公式桥+C3 翻译）在终局全貌核心有位（把"想法→可考卷"的人工翻译彻底消灭）；"全量 NL→任意代码翻译"为蓝图既定后续立项，非本班封矿对象。
- **终局视角**：公式轨已闭环，假说轨打完 G1-G3 后，"周六上午进货→预审→下午出考卷"全程无人值守成立；事件类假说依赖表达式空间扩展（ Owner 白名单审定门），属产能演进非断链。
