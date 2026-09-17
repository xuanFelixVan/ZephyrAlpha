---
ttl: task_bound
rule_form: data
verifiability: manual
title: 全仓审核底数真源（对象表；执行归属见两份新案）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-16
---

# 全仓审核底数真源（v1.5）

> **归属重划（Owner 2026-09-17 裁定）**：本案原七战场已拆成两份执行案——
> ① [kimi_deep_adjudication.md](kimi_deep_adjudication.md)=Kimi 深度裁定主案 v1.1（只给最强模型的十五战场：钱闸数学/战役可行性/**策略切换判据**/待裁项预消化/审审校器/定尺子/**测试有效性**/经济解释/成本与账实/数据外推/**前视偏差**/契约/减法/同族错误抽样/实验规格）；
> ② [flash_verify_directive.md](flash_verify_directive.md)=Flash 机械复验案（接线核对、全量漂移扫描、八分包机械面、测试套、红蓝执行、长任务编排）。
> 本文件降级为**全仓底数与审核对象真源**（§1 底数、§2 A1-A8 对象表、§5 五通道拓扑继续有效并被两案引用）；§0/§3/§4/§6 的优先级与执行序由上述两案接管，勿再按本节开工。
> **一句话**：本文件=主力会话挖矿产出的审核对象底册；分工=模型分派判据（**推理密度 × token 体积**，09-17 修正：时间长度不再是要素——等待不耗配额，轮询才耗）——强模型只做弱模型错了发现不了的判断。
> **前置阅读**：`docs/01_policies_and_standards/sop/review_sop/deep_review_policy.md`（六轴法真源）+ `defect_pattern_checklist.md`（14 条缺陷模式，每域开审前逐条对照）。

## 0. 优先级与 token 预算（好钢用在刀刃上）

| 序 | 战场 | 优先级 | 理由 | 建议token占比 |
|---|------|-------|------|-------------|
| A | 钱闸数学 T1-β | P0·最先 | 输入小推理密=保险；错=全仓回测全错 | 15% |
| B | 八分包 T2 验收 | P0 | 昨夜 60+ 笔新落库未经验收 | 20% |
| C | 全仓文档vs代码漂移 | P1·大菜 | 只有长上下文模型能干 | 30% |
| D | 核心算法+通道深度 | P1 | 542 模块按风险抽样+全量通道 | 20% |
| E | 治理链路 | P2 | 门禁/规则/注册表自洽 | 5% |
| F | 红蓝对抗 | P2 | 对 A/B 抽 3 个最高风险件加试双角色 | 10% |
| G | 世界地图总览 | 收官 | 剩余 token 建/合/废/挂建议 | 剩余 |

**执行顺序（从大到小，Owner 2026-09-16 裁定）**：A 并行最先（输入小=保险）→ **C 全局俯瞰先做**（先看全局有没有结构性/逻辑性问题）→ B/D 按族群·区域性板块审 → 族群干净后下钻模块级细审 → E/F → G 收官。禁一上来就钻单模块（局部没问题≠全局逻辑没断）。

## 1. 全仓底数（真源统计，2026-09-16 实测）

| 层 | 数量 | 真源入口 |
|---|------|---------|
| 蓝图模块 | **542**（signal 72/risk 41/cross_layer 26/position 20/infra_ops 20/autonomy 18/…共 40+ 域） | `docs/03_modules/**/blueprint.md` |
| 治理机生模块 | 412 | GOMAP（`generate_governance_map.scan()`） |
| 注册表 | **73**（tier0 核心 11/治理 28/运行时 34） | `docs/registry_of_registries.yaml`（ROOR） |
| 交易决策地图 | 138 节点（R1-R8 引用校验） | `config/trading_decision_map.yaml` |
| 策略生产全景图 | 15 节点 | 图九（validate_strategy_production_map） |
| 规则 YAML | 86 | `docs/01_policies_and_standards/rules/trae_*.yaml` |
| SOP 方法论 | 九族 24 文件 | `docs/01_policies_and_standards/sop/README.md` |
| 源码 | 3563 .py | `src/` |
| 脚本 | 983 .py | `scripts/` |
| 测试 | 3394 文件（全绿基线：infra 1968+audit 1615 连续多轮 0 失败） | `tests/` |
| 前端 | 46 .py | `src/zephyr/frontend/` |
| 全景图 | 十图（align_all 六维硬 0，2026-09-16） | `scripts/governance/d5_architecture/generators/align_all.py` |
| 八分包交付 | 8 分包+12 跨线+60+ commit | `docs/_working/greatwall_integration/2026-09-16-eight-greatwall-e2e-integration.md`（155d2a16） |

## 2. 战场 A：钱闸数学审查 T1-β（P0 最先）

| # | 审核对象 | 入口 | 核心问句 |
|---|---------|------|---------|
| A1 | 防噪音四闸（来源可溯/交叉验证/A股适配/可回测数据可得） | `sop/mining_sop/mining_sop_policy.md` §5 | 闸逻辑数学上是否可漏过假发现？ |
| A2 | Wilson 区间实现 | grep `wilson`（src/） | 边界 n=0/z 值/单双侧是否正确 |
| A3 | FDR 多重检验校正 | grep `fdr\|benjamini\|bh_procedure` | 多策略族校正口径、m 的取法 |
| A4 | DSR（Deflated Sharpe） | `zephyr` 内 DSR 实现+台账 num_trials | trial 计数真实性（e58d28df99 修过一次，复核存量） |
| A5 | ANOVA/统计检验 | grep `anova\|f_oneway` | 前提检验（正态/方差齐性）缺不缺 |
| A6 | binomial_ge_pvalue | `33b9593ad9` 刚修的退化分支 | p0∈{0,1} 之外还有无退化输入 |
| A7 | metamorphic 63 条不变式 | 分包五交付（30a8c43334） | 不变式本身数学对不对、覆盖够不够 |
| A8 | 回测引擎无真值断言 | `_c4_engine`/回测链 | metamorphic testing 清单是否有漏（对照 review_sop §8 立卡） |

## 3. 战场 B：八分包 T2 验收（P0，昨夜新落库）

| 分包 | 验收入口 | 重点问句 |
|------|---------|---------|
| 一 Kronos 微调 | `4453bf16`+训练链 CH→prep→pkl→两段式 | val loss 0.0155/3.353 的口径真实？tokenizer 错位修复（50944b2a）彻底？ |
| 二 资源排班 B1-B4 | 58 实体注册表+采样器+冲突闸+周历视图 | 采样零侵入是否真零侵入（性能面）？三码冲突闸漏判面？ |
| 三 治理收官 | 裁定#255/#256+四层合围 | 水位门/收割闭环/VRAM 门的边界条件 |
| 四+五 量化 P0 | 裁定#257 全链 | chip 量纲 VWAP 界内率 5272/5272 复算；ALG-01 重做（12.6→99.6）口径复核；pf_alloc 挂触发定性是否成立 |
| 五 审查方法论 | 63 条不变式+mutation 100% | 杀伤率 50→100% 的整改是否引入假杀 |
| 六 全景图收口 | 裁定#258-#263+GOMAP f299d2fa | 六库僵尸归档死链举证抽查；主索引 44→55 对账 |
| 七 ALGO_FLOW | 批9 707 文件+orchestrator 73 件+新门禁 | 427 锚硬校验抽查 20 条；ALGO-NOTE-SYNC 行号锚治本（cc3862512f） |
| 八 F-06 | 批7+红蓝补刀 | 原挂点 33 passed 根治实证复核 |

**12 条跨线接线**（五角星）：逐条按 `155d2a16` 方案文档拓扑复核——接线两端是否真消费（grep 反查），防"纸面接线"。

## 4. 战场 C：全仓文档vs代码漂移审计（大菜，长上下文）

- **对法**：542 蓝图的 [INVARIANTS]/[ERROR_CONTRACT]/[TESTS] 头 ←→ 源码实际行为逐域对照；蓝图 FRONTMATTER-SYNC reconciler 两次超时（GATE-BLUEPRINT-FRONTMATTER-SYNC timed out ×4）说明该链路有债——重点查。
- **高危模式**（对照 defect_pattern_checklist）：双份承载漂移/幽灵引用/假完成状态/孤儿死码/YAML 静默缺陷。
- **已知在途债**：autoclaw ALGO_FLOW 链接门禁残余 ~2225 文件（六大域未动）；S19 14 条硬违规暂计软（长城清欠中）——审这两块的漂移密度。
- **产出**：漂移清单（file:line 锚点+严重级 P0-P3）。

## 5. 战场 D：核心算法与通道深度（542 模块分层抽样+全量通道）

- **抽样法**（举一反三的骨架，Kimi 可扩充）：每域抽 ①资金/仓位直接相关 ②近期返工热区（git log 高频）③零测试覆盖 ④AI 自报 maturity=production 但无 E2E——四类必审，其余按风险。
- **通道审查**（管线级，优先于单模块）：
  1. 数据通道：`python -m zephyr.data` 7 子命令→业务库→特征→信号（断更死源模式：399106 成例，普查数据源存活）
  2. 决策通道：TDM 138 节点的 parent_node 链+factor_refs/data_refs 悬空
  3. 执行通道：策略→plan_engine→position→ex_sor（钱经过的每一步）
  4. 治理通道：reconciler 事件触发合规（禁 cron/sleep-loop）+提交队列 dead 循环
  5. 启动通道：boot_autostarch 派+reaper+健康检查
- **每模块问句**：输入契约谁保证？输出谁消费（grep 反查零消费=孤儿）？失败模式？

## 6. 战场 E：治理链路（P2）

- 86 规则 YAML ←→ gate 实现一致（N-16 双份承载模式）；73 注册表 ←→ ROOR 对账；规则预算净零审计。
- 昨夜新门禁（ALGO-FLOW-LINK 等）own-scope 合规。

## 7. Kimi 自挖指令（开审前必做——先扩充清单再开审）

> 本清单是主力会话挖的底册，但**主力会话有系统性盲区**。Kimi 开工先做一轮"清单的自挖"（约 10% token）：
> 1. **六向扫清单**：上游（还有哪些该审没列）/下游（审出后喂给谁缺环）/旁系（邻域连坐）/深度（每项问句够不够狠）/红蓝（反着问：清单漏了什么最贵）/新鲜度（昨夜 latest commits 有没有新面）。
> 2. **产出 `kimi_audit_checklist_v2_addendum`**（追加清单，不改底册），注明新增理由。
> 3. 然后按 §0 优先级开审；底册+增补清单合并执行。

## 8. 修复权限分级（Owner 2026-09-16 裁定：自己找的自己修，但分级）

- **Kimi 直接修（低风险类）**：文档错漏/死链/假完成状态文案/注释与蓝图头失真——直改+自查后记入报告"已修复清单"；正式区文档（docs/01..）改前留 before/after 摘录。
- **边查边修（热上下文当场修，Owner 2026-09-16 二次裁定）**：查到问题当场产修复，不攒批——重新建上下文才是贵的，当场修命中 KV 缓存≈白送。
  - 文档类（含正式区）：直接改文件。
  - 代码类（src//scripts//config/）：与施工 AI 同权同责——
    冷启动：`export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:/c/Users/fanzi/AppData/Local/Programs/Python/Python312/Scripts:$PATH"` → `python scripts/lock_files.py cleanup && python -m zephyr.trading.process_reaper --status`
    改前取号：`python scripts/lock_files.py acquire <文件> kimi-audit`
    改完提交（禁裸 git commit）：`python scripts/git_commit.py --session kimi-audit --skip-preflight --allow-non-worktree --allow-overlap --files "<逗号分隔>" --message "fix(<域>): <一句话根因> [GW:kimi-audit:non-worktree]"`
    禁无 claim 直改工作区——并发会话的队列回滚会静默吞无主编辑（真实事故在案）：报备不是限制，是防你的活被当垃圾扫掉。
  - P0 钱闸/资金路径/破坏性数据操作：即使能修也先标注"插队"交主力复核后再动（double-check 钱闸）。
- 每条发现：file:line 锚点+复现路径+严重级 P0-P3+修复建议；**禁编造锚点**（抽查复核制）。
- P0 双角色加试：审查者产出后，自己切换"复算反驳者"给最强三条反驳再定级（2×token）。
- 产出落点：`docs/_working/kimi_audit_reports/`（每战场一份报告+一份 executive summary）。
- 误报记档：复核判为误报的进误报档案（镜像 deep_review_policy §误报档案），长期修正审查策略。
- **§8 全节已由 [kimi_deep_adjudication.md §5 三问边界](kimi_deep_adjudication.md) 接管**（2026-09-17）：纯技术判据可定=直改；需长回测验证=只挂单；花真钱/改门位/砍战役/删资产=只出裁定书。独占执行期无主力会话兜底，P0 钱闸修复照做但单列"P0 修复待复核"清单交 Owner 逐条过 commit。

## 9. 收官（战场 G）

- 世界地图总览：十图+542 模块+73 注册表的全景叙事；统盘建/合/废/挂建议（按 mining_sop §6 终局全貌量尺：Owner 只做四类事，一切可自动化者全自动化）。
- 给 Owner 的三句话总评+最危险的三个洞。
