---
ttl: task_bound
title: 分册06 机构对照与先进做法分级——骨架对照/可直接引入/关注不必急/项目已具备
topic: institutional_benchmark
created: "2026-09-24"
owner: ZephyrAlpha-Owner
---

# 分册06：机构对照与先进做法分级

> **大白话开场**：这一册回答"我们跟机构比，骨架对不对？哪些先进做法值得搬、哪些看了也别急、哪些我们已经有了"。**每条机构论断注出处（书/论文名），每条本仓论断带文件路径**。

## 1. 骨架层对照（本仓四段流水 vs 机构正统）

| 段 | 本仓实现（路径证据） | 机构正统对照 | 差距判定 |
|----|---------------------|-------------|---------|
| ① regime 识别 | `src/zephyr/regime/core/regime_detector.py` REGIME_STATES 7 态（r1/r2/r3/r4/r10/r11/r12，HMM+overlay）；六段情绪轴 `src/zephyr/signal_ashare/core/environment_switch.py` SIX_STATES | 机构主流=HMM/GMM 状态识别 + 宏观叠加（日频样本下 HMM 仍是主流；见 §3 关注项） | **同构**。注意点：仓内 r 态存在双词表（7 态 vs 锚定表 4 档语义不同，逐日一致率实测 21.09%，见附录C §5——这是本段最大隐患） |
| ② 条件配置 | `src/zephyr/backtest/regime_validation/condition_package.py`（条件胞=情绪档×状态档，30 日地板，闭卷纪律）；六段预算带 daily_decision_orchestrator BUDGET_BANDS | 条件化资产配置（regime-conditional allocation）：按状态桶配置策略暴露；分桶报告（回测 SOP README §7 护栏3"分状态报告，跨状态平均=无效结论"已是机构级纪律） | **同构且部分超前三件套**（预注册/闭卷/成本门，见分册02） |
| ③ meta-labeling（二次判定） | `MOD-SIG-115 pattern_to_signal_mapper`：强度=置信度×胜率加权（win_rate_provider 注入，None=无统计退化）；`src/zephyr/signal_ashare/strategy_signal/pattern_evidence_certifier.py`（证据认证） | López de Prado (2018) *Advances in Financial Machine Learning* §3.8 *How to Use Meta-Labeling*（Wiley）：一次模型出方向、二次模型判断"这次信不信"并按置信度定仓位大小（[Hudson & Thames 实例](https://hudsonthames.org)） | **语义同构，形态更简**：本仓用"证据×胜率"替代 ML 二次模型——样本量下这是正确选择（5,026 交易日撑不起端到端 ML 标签器），机构做 ML 版的前提是 tick 级大样本 |
| ④ 多策略 pod | `src/zephyr/pf_core/strategy_engine/framework_composer.py`（合成面板 Σw=1、死成员披露、RSC-2 收缩节流）+ sleeve 体系（打板/多因子/事件驱动 sleeve，`data/runtime/strategy_registry_snapshot.json`）+ PP-001 配比 | 多策略 pod / manager allocation：子策略独立核算+上层风险预算分配+对冲基金平台式监控 | **同构**。附加分：收缩节流"剩余质量落现金禁再归一化"（裁定#270）比常见"权重重归一"更保守 |

**骨架结论**：本仓"regime→条件配置→meta 判定→多策略 pod"四段=机构正统骨架的合规变体，无结构性缺失；真正的风险不在骨架缺段，而在**段间词表分叉**（附录C）与**样本量纪律**（分册03）。

## 2.【可直接引入】——已具备条件或挂点现成

| 做法 | 出处 | 本仓挂点 | 引入成本 |
|------|------|---------|---------|
| 缩水夏普 PSR/DSR | Bailey & López de Prado 2014, JPM（davidhbailey.com） | `src/zephyr/simulation/deflated_sharpe_calculator.py` 全仓唯一真源已在役 | 无（已引入） |
| PBO/CPCV | Bailey et al. 2017 JCF；López de Prado 2018 AFML Wiley | G2 门已立法（62 号 §4.13），引擎字段接线待 | 小（接线+purge 参数入预注册） |
| 贝叶斯收缩（薄格借样） | Robinson 2016 varianceexplained.org；Bayes Rules! ch3 | `__baseline__` 行=现成先验（pattern_win_rate_provider） | 小（分册03 §2 公式+α 预注册） |
| contextual bandit（上下文老虎机） | Chu et al. 2011 LinUCB（[proceedings.mlr.press](https://proceedings.mlr.press)）；Cartea, Jaimungal & Tang 2023 *Bandits for Algorithmic Trading with Signals*（[SSRN](https://papers.ssrn.com)）；Ni et al. 2023 contextual combinatorial bandit portfolio（[ScienceDirect](https://www.sciencedirect.com)） | sleeve/pod 配比层（framework_composer 面板权重）+ regime 上下文（七态）——bandit 的"上下文"=六段/r 态，"臂"=sleeve 配比 | 中（先离线模拟器考，走 E4 正门；样本要求低于 RL） |
| tick 盘口失衡执行信号（OBI） | Cont, Kukanov & Stoikov 2014, JF *The Price Impact of Order Book Events*（OFI）；方法卡评级见 METHOD_MINING_t0.md 卡 5.1 | `STR-VREV-024 盘口失衡反转做T`（strategy_registry active）+ tick_depth_5（2026-07→今）；结论口径=**执行增强 HIGH/独立信号 LOW** | 小（定位为执行层；独立做T 被成本门判死） |

## 3.【关注不必急】——原理成立，本仓现在做是烧钱

| 做法 | 出处/理由 | 为什么现在不急 |
|------|-----------|---------------|
| 深度学习状态识别 | DL regime 模型需大样本；日频 5,026 交易日的闭卷窗撑不起深度模型，**HMM 在日频样本下仍是机构主流**（同结论见 memo29 B 类：S15.30 HMM 市场体制识别=regime_detector 模块设计，62 号 §4 已登记 Wasserstein HMM） | 等分钟/tick 特征层铺厚后再评；届时也先考 HMM 基线增量（消融闸） |
| RL 执行 | Jiang, Xu & Weissman 2021/2023（METHOD_MINING_t0 卡 9.2 转引）；卡评级"LOW 首发，规则版先行" | 报撤单合规红线（程序化细则 2025-07-07）+黑盒不可解释；规则版执行件未验证完不投 RL |
| NLP 另类数据 alpha | LLM 情绪信号同源拥挤（METHOD_MINING_t0 卡 8.3 与 9.1 判读）；本仓 sentiment 管道已建（news_sentiment_window + emotion_index C6 成分） | 已有管道优先做"情绪→开盘过冲"类**条件配置**消费（低频、可考），不做高频 alpha 竞速 |

## 4.【项目已具备】——与机构先进实践对齐的既有资产（防"别人有的都是好的"错觉）

| 资产 | 机构对应 | 路径 |
|------|---------|------|
| PIT 点时语义 | point-in-time 数据库（机构数据组的 PIT 纪律） | industry_class valid_from/valid_to（position_recipe_grid_schema industry_anchor）；`src/zephyr/simulation/look_ahead_bias_detector.py`（MOD-SIM-022）；闭卷窗纪律（condition_package） |
| 预注册纪律 | 机构预注册研究流程（preregistration） | `config/search_space_prereg.yaml`（冻结语义+族登记+ledger_required）；exam_policy §1 准入四条 |
| 漂移监控文化 | 模型风险监控（MRM） | memo55 三问体系+五判据退役+阈值注册表 REG-ATH-001（分册05） |
| kill switch | 机构风控熔断 | `zephyr.security.access_control.kill_switch`（宪法 §7 核心系统速查） |
| 负结果台账 | 研究完整性（防文件柜偏差） | exam_policy §5+prereg honesty negatives.csv |
| 分状态报告纪律 | regime-conditioned reporting | 回测 SOP README §7 护栏3（跨状态平均=无效结论） |

## 5. 一段话版

**骨架=机构正统（四段同构），短板在词表分叉与薄样本；直接引入五件（DSR/PBO/CPCV/收缩/bandit/OBI 执行）都有现成挂点；DL/RL/NLP 三件按"样本与合规"两条闸暂缓；PIT/预注册/漂移监控/kill switch/负结果台账五项已具备且不输机构。**
