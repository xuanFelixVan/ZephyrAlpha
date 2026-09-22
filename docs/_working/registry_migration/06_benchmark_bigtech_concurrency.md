---
ttl: task_bound
title: "对标调研·大厂并发提交管理（Google/Meta/GitHub/Zuul/Uber/Bazel LSC/结构化合并，22 源）"
session: st-regfix-lane0b-20260923
---

# 大厂并发提交管理调研
**——几百~几千程序员对同一主干/共享文件的高并发提交治理（2026-09-23）**

> 调研方法：全部结论来自公开网络检索与原文阅读（来源清单见文末）。CACM/Piper 论文原文多次直连被 403，关键数字经 Google Research 官方页面+多个独立二手来源交叉印证后采用。凡未能核实的点均显式标注「未能证实」。

## 1. Google：Piper / Critique 单主干

- **单一代码库+单一主干**：约 25,000 名工程师全部代码在自研版本系统 Piper 单仓（~20 亿行、~86TB、**每天约 40,000 次提交**）。后端为 Google 基础设施，集中式服务提供一致性。
- **CitC 云工作区**：云端快照式工作区（指针+用户改动叠加层），不检出完整副本。
- **评审前移**：变更（CL）先上传 Critique 评审；Tricorder 静态分析自动跑；≥1 LGTM+OWNERS 批准+无未解决评论才可提交。
- **presubmit**：评审时与提交时运行的预提交钩子（自动测试/项目不变量），失败阻断。
- **submit queue（全局提交队列）**：批准后的 CL 进队列，与待提交变更组批量测试，通过才落主干——主干提交序列全部被验证过。
- **冲突粒度**：文本/文件级；社会约定小 CL（"100 行通常合理，1000 行通常过大"；可仅因过大拒收）；提交按最新主干状态重放验证，冲突即失败。
- **吞吐**：25,000 开发者/日 40,000 提交；读写比约 99.9%:0.3%。
- **失败路径**：presubmit 失败本地修；主干破坏快速修或 revert；紧急情况允许 post-commit review。
- Google BUILD 文件专用语义合并工具（传闻 Mergeable）：**未能证实**。

## 2. Meta：Sapling（Mercurial 系）+ Commit Cloud + stacked diffs

- **Sapling**：源自 Mercurial 的规模化前端，服务端+虚拟文件系统支撑数千万文件/提交/分支。
- **stacked commits 是标准工作流**：任意堆叠；`sl goto`+`sl amend` 自动 rebase 栈顶；`sl restack` 一次性重建；mutation 历史记录使栈可算法化重建。
- **Commit Cloud**：提交即自动上传云端，跨设备/人共享一个 hash。
- **落地**：批准的 commit 逐个"落"（远端 cherry-pick）；每个提交必须自洽（lint/test/build 全绿）才能进栈。
- **feature gate 隐藏未完成功能**（Gatekeepers 类）——master 保持绿的前提。
- 冲突粒度：文本级，但以"单 commit=原子评审与落地单元"把冲突窗口切到最小；恢复命令丰富（undo/absorb/hide）。
- Meta 内部落地侧序列化机制的公开细节有限，**未能证实**。

## 3. Merge Queue 家族

### 3a. GitHub Merge Queue（2023-07 GA）
- PR 入队即分组进 merge_group（目标分支最新+排前面的所有 PR），临时分支 `gh-readonly-queue/{base}/pr-N` 按 FIFO 验证，最深组合过检才真合并。
- 可配：最少/最多合并 PR 数（1-100）、等待超时、构建并发（1-100）。
- **冲突即出队**；失败/超时/冲突 PR 移出后队列自动重组。换序代价极高（jumping the queue 造成在途 PR 全量重建）。
- GitHub 自家：**月 500+ 工程师合 2,500 PR**；GA 前已处理 30,000+ PR；平均等待时间降 33%。
- 设计目标原话："有问题的 PR 不应阻塞其他人"（系统吞吐优先于单 PR 公平）。
- "warm batch/rollup"术语不在官方文档，仅第三方使用。

### 3b. Zuul + Gerrit（OpenDev/OpenStack）
- **投机执行（speculative execution）**：假设队首 A-E 全成功，把 A、A+B、…各组合并行 checkout 测试；全过则按序一次性合并——结构性消灭"各自过检、合在一起挂掉"的假阴性。
- 实际 merge 严格串行；测试投机并行。
- **流控窗口**（TCP 拥塞控制思想）：窗口从 20 起，每成功合并 +1、每失败减半；串行管线窗口=1。
- 失败变更剔除，其后项对新分支顶重新测试。

### 3c. Uber SubmitQueue
- planner 引擎+**投机树**并行验证多条合并路径；**逻辑回归预测合并成功率（97% 准确率）**优先验证大概率路径；冲突判定用构建系统 target 集合（**语义/目标级而非纯文本级**）。
- 动机数据：SubmitQueue 前 iOS 主干一周采样仅 **52% 时间绿**；16 个并发可能冲突变更 40% 冲突/破坏概率；朴素串行队列在 1,000 变更/天×30 分钟构建下最后一单等 20+ 天；上线后**主干一年以上全程绿**。
- 2025 ICSE-SEIP 论文（arXiv:2501.03440）：ML 构建时长预测+概率化调度，CI 资源降约 53%、CPU 降 44%。

## 4. Bazel/Google 共享 BUILD 文件治理（LSC 流程）

- **buildifier/buildozer**：BUILD 文件格式化+程序化编辑，使修改变成**机器人可确定性重放**的操作。
- **LSC（Large-Scale Change）五步**：①工具作者提案→LSC 委员会授权；②Rosie 按"项目边界+所有权规则"切成互不依赖 shard（有依赖文件同 shard），每 shard 独立可测试可提交；③两阶段验证（TAP 列车：每 3 小时一班，先各跑 1,000 条采样测试，合并后对受影响测试并集做合并后验证，失败按变更归因定责）；④评审自动化（OWNERS 自动配审+无响应自动加人+全局批准人只查异常）；⑤事后防回潮（Tricorder 在他人 review 时自动标记对已弃用符号的新引用）。
- shard 被当"cattle, not pets"——被拒/回滚重新生成即可（工具可重跑）。
- 吞吐：`scoped_ptr→unique_ptr` LSC 峰值**每天 700+ 独立变更、触 15,000+ 文件**；经验法则：超过约 500 处编辑，工具化优于人工。

## 5. 语义/结构化合并技术

- **git merge driver**：`.gitattributes` 可为路径指定合并驱动；内建 `union`=按行并集（适合"双方各自追加"的清单类文件）；自定义 driver 收 base/ours/theirs 三方。
- **weave（Ataraxy-Labs/weave，开源 Rust）**：tree-sitter 实体级 git merge driver；按"名称+类型+作用域"跨版本匹配实体，同一 map 对象不同 key 的修改自动合并（YAML/JSON 等 38 种格式）；同实体双改才做实体内三向合并，真不兼容报实体级冲突（带实体名/置信度/拒绝原因）；README 声称较行级合并减少约 95% 假冲突，明确面向"多个 AI agent 独立编辑同一文件"场景；诚实披露真实基准中也有 86 处回归（344 胜/86 负）。
- **JSON Patch (RFC 6902) / JSON Merge Patch (RFC 7386)**：add/remove/replace/move/test 补丁运算——把并发写表达为可重放的条目级 patch 流，冲突成为"同 key 双写"的可判定问题。
- mergekit：确认为 LLM 模型合并工具包（同名混淆澄清）。

## 6. 行业共识（trunk-based vs merge queue vs feature flag）

- **DORA（Accelerate）**：活跃分支 ≤3、每天至少向 trunk 合并一次、无冻结无集成阶段的团队交付速度/稳定性/可用性更高；分支寿命不超过几小时；配套小批次+commit 前自动化+分钟级构建+红了立即修或快滚。
- **merge queue 与 trunk-based 互补**：merge queue 是 trunk-based 在高并发下的护城河——"合入主干的一切按其最终形态被验证"。
- **feature flag**：解耦"落地顺序≠发布顺序"（trunk 上始终可部署代码）。
- **反向教训（DORA）**：重评审流程诱发大批量囤积——"延迟评审→变更更大→评审更慢→缺陷更多"向下螺旋；异步评审拖慢合并直接增大冲突风险（与"AI 长任务持锁改共享文件"风险同构）。

## 关键设计原则提炼（面向多 AI 会话共享 YAML 注册表）

1. 写入必须经单一串行入口（submit queue 模式）——事故说明绕过队列的整文件覆盖写仍存在旁路。
2. 投机并行验证+串行落地——"按落地后真实形态验证"消灭"各自过检、合在一起互踩"（Zuul）。
3. 失败即出队、自动重组，坏会话不阻塞队列（GitHub 设计目标）。
4. 冲突判定从文件级降到条目/key 级（weave/RFC 6902/Uber target 级）。
5. 写操作表达为可重放声明式增量（patch 流），非镜像快照（Rosie"工具可重跑"）。
6. 单一真源+单一版本原则——禁影子副本；YAML=DB 双写必须机械单向可推导。
7. 共享文件机器可读所有权（OWNERS 语义），争议由条目级 owner 裁定。
8. 破坏性/大批量改动走 LSC 式专用通道（提案授权→所有权分片→两阶段验证→失败归因）。
9. 短事务纪律：小变更、短生命周期、当日多次合并（DORA/Google 小 CL）。
10. 热文件乐观并发+写前基线校验（CAS）——落地器校验"我基于的版本==当前版本"。
11. 落地后静态防线拦截回潮（Tricorder 标记对已弃用项的新引用——防"删除的条目被旧上下文会话加回来"）。
12. 一切可回滚可恢复（undo/evolve/shard 重生成/坏变更剔除重排）+presubmit 前移（1174 条未落地损失的本质=缺这条链路）。

## 参考资料清单

1. https://research.google/pubs/pub45424.html （Piper 论文官方页）
2. https://dl.acm.org/doi/10.1145/2850585.2850595 （CACM 原文）
3. https://abseil.io/resources/swe-book/html/ch19.html （SWE at Google Ch.19 Critique）
4. https://google.github.io/eng-practices/review/developer/small-cls.html （Small CLs）
5. https://engineering.fb.com/2022/11/15/developer-tools/sapling-source-control-scalable/ （Sapling）
6. https://jg.gg/2018/09/29/stacked-diffs-versus-pull-requests/ （Stacked Diffs vs PR）
7. https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue （Merge Queue 文档）
8. https://github.blog/engineering/engineering-principles/how-github-uses-merge-queue-to-ship-hundreds-of-changes-every-day （GitHub 自用数据）
9. https://zuul-ci.org/docs/zuul/discussion/gating.html （Zuul 投机执行/窗口）
10. https://blog.acolyer.org/2019/04/18/keeping-master-green-at-scale/ （Uber SubmitQueue 论文评述）
11. https://arxiv.org/abs/2501.03440 （Uber CI at Scale, ICSE-SEIP 2025）
12. https://abseil.io/resources/swe-book/html/ch22.html （SWE at Google Ch.22 LSC）
13. https://github.com/bazelbuild/buildifier （buildifier）
14. https://github.com/google/copybara （Copybara）
15. https://github.com/Ataraxy-Labs/weave （实体级 merge driver）
16. https://git-scm.com/docs/gitattributes （git merge drivers）
17. https://datatracker.ietf.org/doc/html/rfc6902 （JSON Patch）
18. https://datatracker.ietf.org/doc/html/rfc7386 （JSON Merge Patch）
19. https://dora.dev/devops-capabilities/technical/trunk-based-development/ （DORA trunk-based）
20. https://trunkbaseddevelopment.com/ （trunk-based 参考站）
21. https://newsletter.thepragmaticengineer.com/p/stacked-diffs （Pragmatic Engineer）
22. https://github.com/arcee-ai/mergekit （同名澄清用）

**未证实项汇总**：Piper 原文全文细节（403，二手交叉印证）；Google BUILD 语义合并工具；GitHub"warm batch"官方术语；Meta 内部落地序列化器细节；Uber 原博文 404（经论文印证）。

**核心结论一句话**：六范式公共骨架="条目级/目标级冲突判定+单一串行落地入口+投机并行验证+失败出队重组+工具可重放+落地后防线拦截回潮"；治本动作=把"AI 会话→注册表"写路径从"读-改-整文件写"重构为"声明式条目级 patch→队列串行合并落地"，热文件保留 CAS 基线校验。
