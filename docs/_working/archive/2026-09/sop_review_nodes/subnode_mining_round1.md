---
ttl: task_bound
rule_form: data
verifiability: manual
title: 深度审查 SOP §8 子节点第一轮挖矿归档（四报告全文）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-09-15
topic: deep_review
scope: global
depends_on:
  - deep_review_policy
---

# §8 子节点第一轮挖矿归档（2026-09-15，四子代理并发）

> **定位**：[deep_review_policy](../deep_review_policy.md) §8 四个并发挖矿子节点的完整报告归档。裁定结论已回写母文件 §8；本文件是证据全文（子代理产出经主力会话四闸复核：缺陷模式库锚点抽查 6/6 属实；LLM debate 的"53→80%"经溯源降级为待验证——见其报告 §1）。

## 子节点 1：缺陷模式库 → 已建成（独立文件）

**裁定**：立卡落地为 [defect_pattern_checklist.md](../defect_pattern_checklist.md) v1.0.0（14 条模式，每条带 commit 锚点+审查问句+轴标签）。锚点抽查 6/6 属实。维护机制：T3 事故复盘同批追加；固化进 gate 后退役。本节只留裁定，全文见该文件。

## 子节点 2：mutation testing → 立卡（窄试点）

**裁定**：mutmut（v3.8.0 活跃，Windows 需 WSL）限 P0 纯逻辑单文件+对应窄测试，深度审查触发时手跑，不进流水线、不加 gate。边界认知：mutation score 测"测试敏感度"，测不出 oracle（断言期望值）本身错误——恰是人工审查互补面。驳回：全仓变异、自建增量缓存设施。

### 报告全文

**1 工具现状（2025–2026）**
- **mutmut**：v3.8.0，2026-09-12 发布，活跃（[PyPI](https://pypi.org/project/mutmut/)）。v3 用 trampoline+并行，速度最佳。**关键限制：Windows 必须走 WSL**（双源：[GitHub](https://github.com/boxed/mutmut)+PyPI）。
- **cosmic-ray**：v8.7.0，2026-08-09，活跃（[PyPI](https://pypi.org/project/cosmic-ray/)）。Windows 支持查无（受阻，待验证）。
- **mutatest**：2022-02 后停更≈4.5 年，判弃维护（[PyPI](https://pypi.org/project/mutatest/)）。

**2 局部变异可行性：可行，且是业界常规**
- Stryker 官方 `incremental`+`mutate` glob，"只变异目标代码"是工具一等公民（[Stryker 配置文档](https://stryker-mutator.io/docs/stryker-js/configuration/)；[Microsoft Learn 2026](https://learn.microsoft.com/en-us/dotnet/core/testing/mutation-testing) 独立佐证）。
- OneUptime（2026-01）推荐 Focused Mutation Testing：只对高危区域变异+渐进采纳（[来源](https://oneuptime.com/blog/post/2026-01-30-mutation-testing-strategies/view)）。
- mutmut 支持 `paths_to_mutate` 限定单文件（官方 README，单源待验证）。必须"窄文件+窄测试"，禁全仓。

**3 对"审测试本身"的适配度**
- **能查**：弱断言/永真断言（变异体存活即暴露，Drizz 2026-06 与 OneUptime 双源）；mock 过度路径同理（机制推断+单源，待验证）。
- **查不出**：①等价变异体噪声，比例可观（[arXiv 2404.09241，2024](https://arxiv.org/html/2404.09241v1)）；②**oracle 错误**——断言期望值本身写错、测试逻辑写反但碰巧杀死变异体（[Drizz](https://www.drizz.dev/post/mutation-testing-explained-how-it-improves-your-tests) 明言无法验证 oracle 正确性，单源+推理）。结论：mutation score 是"测试敏感度"度量，不是"断言正确性"度量。

**4 裁定：立卡（窄试点）**——先试 P0 钱路径纯逻辑、无 DB/网络依赖的资金分配计算模块；WSL2 Python 3.12+pytest，mutmut 限定单文件+对应测试，一次性跑、结果入深度审查记录。挂起条件：WSL 试点受阻再评估 cosmic-ray。

## 子节点 3：metamorphic testing → 立卡（首批 4 条不变式）

**裁定**：首批 4 条≈8-10h（S11：价格缩放不变+资产置换不变；四闸：样本置换不变+效应量↑→p 值↓单调）。工具=hypothesis+pytest 双跑，零新依赖。挂起：窗口滚动稳定性、延迟 MR（二批）。驳回：引入专门 MT 框架。**勘误**：《Correctness of Backtest Engines》实为 Löw/Maier-Paape/Platen，arXiv:1509.08248（2015）/JOIS 2017，非 2025 年文献（母文件 §8 原记录有误，已改）。

### 报告全文

**1 不变式清单（逐条 MR 为锚+推导，标"待验证"者如实）**
- **货币/价格缩放不变**：价格×k → 收益率/信号/夏普不变，P&L×k（锚：Xie 等 JSS 2010 尺度 MR 家族；[Löw/Maier-Paape/Platen, JOIS 2017](https://doi.org/10.21314/jois.2017.085)，[arXiv:1509.08248](https://arxiv.org/abs/1509.08248)——模型蜡烛+已知解法证回测引擎正确性）
- **资产置换不变**：权重随资产重排对应置换，组合收益不变（锚：Xie 2010 置换 MR；[ISSTA 2018](https://doi.org/10.1145/3213846.3213858)）
- **成本单调**：佣金/滑点↑→净收益单调不增（数学事实，推导）
- **延迟 MR（无未来函数）**：信号延迟 1 bar 收益不应暴涨，暴涨=lookahead bug（实践惯例，单源待验证）
- **合成已知解回放**：斜率/正弦模型蜡烛→解析正确 P&L（Löw 2015/2017 真源）
- **自融资恒等**：Σ现金流=期末权益−期初权益（会计恒等式）
- **统计链三条**：样本置换不变；效应量↑→p 值↓；H0 模拟下 p 值均匀 U(0,1)（锚：[Barr 等 IEEE TSE 2014 oracle 综述](https://doi.org/10.1109/TSE.2014.2372785)）
- **勘误**：可检索的《Correctness of Backtest Engines》=2015(arXiv)/2017(JOIS) 非 2025（百度学术页 403 受阻，OpenAlex 无 2025 条目）；量化专用 MR 系统目录**查无现成文献**（多轮检索，如实记录）。

**2 工具选型**：hypothesis 够用（官方 [numpy 策略](https://hypothesis.readthedocs.io/en/latest/numpy.html)；numpy 官方测试自用 hypothesis，[conftest.py](https://raw.githubusercontent.com/numpy/numpy/main/numpy/conftest.py) 已核；[arXiv 2211.12003](https://arxiv.org/abs/2211.12003) 证明 PBT 工具可承载 MT）。最简路径：pytest 双跑参数化，零新依赖。方法论源：[Chen 等 ACM CSUR 2018](https://doi.org/10.1145/3143561)、[软件学报 2023 综述](https://www.jos.org.cn/html/2023/1/6425.htm)。

**3 两对象适配**：S11 runner 先做①价格缩放不变（抓单位 bug）②置换不变（抓权重/列错位）③延迟 MR（抓 lookahead，价值最高但容差设计重，二批）；四闸统计检验做①置换不变②效应量–p 值单调③（二批）H0 下 p 值均匀校准（识别口径漂移，呼应 DSR 翻案教训）。

**4 工作量**：首批 4 条每条 1–2h+strategy 基建 2h≈8–10h；二批延迟 MR、自融资恒等+3h。

## 子节点 4：LLM 交叉评审/debate → 立卡（收窄版：双角色单轮跨模型）

**裁定**：P0 对象审查配"审查者+复算反驳者"双角色单轮（约 2×token）：A 产出公式级断言清单→B 隔离推理链独立复算+攻击断言找反例→数值对拍实证门裁决，分歧升 Owner。**驳回**：把"53→80%"当普适定律（溯源后定级博客单实验待验证）；**挂起**：N-agent 多轮辩论（token 平方涨+饱和任务反有害）。

### 报告全文

**1 检出率溯源**：53%→80% 出自 Milvus/Zilliz 官方博客自跑实验（[中文版 2026-02-26](https://milvus.io/zh/blog/ai-code-review-gets-better-when-models-debate-claude-vs-gemini-vs-codex-vs-qwen-vs-minimax.md)；[英文 Medium 2026-07](https://milvusio.medium.com/ai-code-review-gets-better-when-models-debate-claude-vs-gemini-vs-codex-vs-qwen-vs-minimax-cf9a995c0b0d)），知乎等三处均为转载壳。**查无对应同行评审论文**；原文方法细节（数据集、轮数、成本倍数）核实受阻——该数字定级"业界博客单实验，待验证"。

**2 双角色做法（可溯源）**：①[Refute-or-Promote（arXiv 2604.19049，2026-04）](https://arxiv.org/abs/2604.19049)：四阶段门控，创意轨/对抗轨分离+跨模型 Critic+实证门；171 候选杀约 79%，产出 4 CVE，总成本约 $250；且记录 80+ agent 共识同错——**反"投票裁决"**。②[Du et al. 2023（arXiv 2305.14325）](https://arxiv.org/abs/2305.14325)：3 agent×2 轮无 judge，GSM8K 77→85，自认 computationally expensive。③[Khan et al.（Google DeepMind，ICML 2024）](https://blog.csdn.net/qq_36158230/article/details/152956479)：非专家 judge+强辩手，judge 准确率 48→76%。④[辩论失败分析（arXiv 2510.20963，2025-10）](https://arxiv.org/abs/2510.20963)：竞争式互驳被 cheap-talk 攻破，**协作式挑错在错误检测最高 +10pp，饱和任务反有害**。

**3 P0 适用性**：四闸数学代码瓶颈是**独立复算**而非观点辩论。适用"审查者+复算反驳者"双角色：反驳者只看断言不看推理链，用黄金值对拍/scipy 交叉复算+实证门机械裁决；不适用 5-agent 多轮互驳（token 平方涨、饱和型任务风险）。

**4 成本性价比**：Du 式 MAD token 约 4-6×；R-o-P 门控式约 $1.5/候选。Owner 有限窗口下：**单模型审查+第二模型单轮复算反驳（约 2×token）性价比最优**；"80%"在数学密集小模块上无实证。

**5 指令模板要点**：①B 隔离 A 的推理链防锚定；②每条断言须附可执行验算（脚本/黄金值）；③输出结构化（断言/反例/数值证据）；④写明"共识≠正确"警示。

## 修订记录

| 日期 | 版本 | 改动内容 | 为什么改 |
|---|---|---|---|
| 2026-09-15 | 1.0.0 | 初稿：四子节点并发挖矿报告归档+裁定 | deep_review_policy §8 子节点第一轮挖矿收口；全文留档防"结论在聊天里发霉" |
