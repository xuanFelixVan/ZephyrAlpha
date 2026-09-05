---
ttl: task_bound
---

> **文档**：长城审计移交总管（强模型）B 类残余+Owner 裁定准备书
> **签发**：总管 STEWARD-20260905-001，2026-09-05；Owner 离线期间按 0.8 自主裁定框架作业
> **性质**：Owner 裁定项汇总（每项含证据链+总管建议+可直接执行的方案）；施工完成即失效，裁定结果应登记至 architecture_issue_registry 或对应蓝图
> **进度真源**：docs/_working/2026-09-05-audit-greatwall-report.md §9（B 类总账）

# 一、总管已施工项（不需裁定，备案）

| 项 | commit | 内容 |
|---|---|---|
| 词表门禁终清零 | b0a0aef7 | AI-16 五条 noqa 被 merge 吸收丢失（git 取证 0c4e7b796b 实锤）重植入+4 WARN 治本+startup_vocabulary v1.1.0 增设 scheduled_task |
| B1+B2 batch_id 批次写入方全链接线 | a14cd9a0 | 公共写 API+五建卡入口+create_and_ready（PENDING→READY 非法连带缺陷治本）+蓝图 §16.7.5 批次创建语义 |
| B3 RiskLimits 双 codegen 收敛 | 4dd2e2e4 | 副本降级 re-export shim（A13 范式）+三处反向映射改指 CTR-003 真源+顺带修两预存红测试 |
| B4 Timer 周期调仓改事件驱动 | 8d1929d4 | Timer 机制全删+ex_core.rebalance.requested receptacle+boot_hooks 第 11 消费方+CLI --interval 退役 |

# 二、B17 错误码四族处置（总管裁定：全部转 Owner，含逐项建议）

## 2.1 事实基线（总管实测复核）

- 六断言门禁 6 passed（本日复跑）；scripts/ 零未登记码；注册表 580 条（572 active+8 deprecated）
- AI-17"69 个未登记"对账：src 42 实测 + docs 12（蓝图预留叙事）+ 跨区重复计数；**去重后真未登记 54，其中可机械补登 0**

## 2.2 ①"69 未登记码"逐族处置建议

| 子族 | 数量 | 总管核实 | 建议 |
|---|---|---|---|
| tool_contracts.yaml 整批 | 34 | **零 .py raise 点**（抽验 ZA-GOV-0001/ZA-TSK-0001/ZA-GW-0001 全仓 .py 零命中；六断言方向 A 只扫 .py AST 定义点，故 6 passed） | **维持 AI-02 既有裁定**（"契约层码非登记范围"）。若 Owner 想收编：二选一——(a) 为 10 个 MCP server 落 `raise MCPError(error_code=...)` 真定义点后按普通码登记（行为变更，涉 12 个 server 文件）；(b) 注册表新增 `contract_declared` 条目形态（schema 变更，需同步修订断言 3）。总管倾向 (a)：YAML 契约声明了错误码但实现从未抛出=契约与实现脱节，本就是待施工面 |
| src 史注引用 | 8 | 全部为改号/勘正历史注释（ZA-INT-0004/5/6 改号史、ZA-PA-0006 勘正、ZA-POS-0042 幻影史注、ZA-REGIME-0050 头注、ZA-PA-0008/0013 预留声明） | 无需处置（历史记录非定义点，登记即幻影） |
| docs 独有（蓝图预留） | 12 | ZA-FE-0006、ZA-GV-0023、ZA-POS-0041/0043、ZA-REGIME-0011/0012/0013/0052/0053、ZA-SIG-0001、ZA-XS-0015、ZA-ZZZ-9999 | 蓝图预留码随预留类落位/关闭一并裁定（见 2.4） |
| ZA-POS-0020/0021/0022/0023 号段 | — | **已收口**（d53580c766：按实现为真源修正 strategy_book/firm_risk_aggregator 双层陈述，"落位需 Owner 重分配号段"留痕） | 无行动 |

## 2.3 ②FAC/MLS 前缀分配（26+ 异常类"未登记-申请中"）

- 事实：全仓 184 个 `ZA-XXX-UNREGISTERED-*` 占位标记（194 类级+12 模块级）；FAC 7 类（research/factor 域）+ MLS 4 类（ml_serve 域）+ AUDITTEST 若干，前缀均未入 domain_prefixes 36 表
- **建议**：新增三前缀（机械可做，但属命名空间治理=Owner 权限）：
  ```yaml
  # domain_prefixes 追加（建议值）
  - {prefix: FAC, domain: D_FACTOR, note: 因子挖掘/特征工程异常族}
  - {prefix: MLS, domain: D_ML_SERVE, note: 模型服务/推理适配异常族}
  # AUDITTEST 若保留需并入既有域或另立
  ```
- 前缀批准后，占位码转正为**机械批量施工**（2026-08-30 先例 860e4c2787 格式：类加 error_code 属性+注册表 introduced 转正条目+段内 max+1 顺延取号），总管可按域分批执行（预计 173 个可转，FAC/MLS/AUDITTEST 除外的前缀已声明域先行）

## 2.4 ③预留码族（ZA-PA-0008~0010/0013、ZA-POS-0041~0043）

- 事实：全部未登记；regime_meta_allocator 蓝图 L258-260 与 budget_change_handler 蓝图 L270-275 明文"预留码登记/关闭由 Owner 裁定"；ZA-PA-0013 类已存在（InvalidMaxDdInputError，仅缺 error_code 属性+注册条目，"治理闭环后回补"）
- **建议**（逐码）：
  - ZA-PA-0013：**批准即转正**（类在、号段无冲突、申请在案——总管可 10 分钟完成：加属性+登记）
  - ZA-PA-0008~0010、ZA-POS-0041~0043：蓝图预留类未落码——建议**关闭预留**（蓝图删除预留声明）或**落码**（施工新异常类）；六个月内无落码计划的预留按"错误声明比缺失更危险"原则建议关闭

## 2.5 ④ZA-REGIME-0050~0052（场景码家）

- 事实：chip_distribution_engine 纯降级标记（不抛错），蓝图 §8 三场景；AI-09 裁定"维持不登记（方向 B 活定义点要求）"仍成立
- **建议**：维持不登记；若需可追溯，蓝图 §8 已是真源（头注已诚实化）

# 三、B4 附注：risk_layer 对账 Timer（未纳入本批）

- 事实：trading_session.start() 同链路拉起第二个 Timer（risk_layer_orchestrator.start_reconcile_loop，300s 盘中对账）；**有蓝图背书**（MOD-EX-056 阶段2"每 5 分钟"）——与已删除的调仓 Timer（无蓝图背书）性质不同
- 建议：属蓝图规划位。若 Owner 要求全仓时间触发清零，需先修订 MOD-EX-056 蓝图（事件驱动对账替代源=对账事件，如订单回报/持仓变更触发），再同 B4 范式改造。**当前维持现状合规**（蓝图=Owner 批准的设计真源）

# 四、startup_vocabulary v1.1.0 增值备案（b0a0aef7 已施工）

- scheduled_task 合法值已生效（对齐 Owner 2026-08-28 批准的 process_reaper OS 托管设计+trae_060 L132 CI schedule 先例）；边界=仅限守护类 one-shot。若 Owner 不认可，revert 该词表变更即可（reaper 表头将回到 WARN 态需另行豁免）

# 五、B5 silent except 122 处（总管裁定：不做批量治理+1 处定点已修）

- 实测：infrastructure 122 处/63 文件（AST 口径与审计吻合）；全仓 744 处/365 文件——infrastructure 仅排第 3（gov_enforcement 133、governance 129 更高），治理五域合计占 47%
- 抽样 15 处分类：清理/关闭容忍 ~47%、控制流合法 ~40%、真吞错 ~13%（全部窄类型捕获，与 308 处 noqa 宽泛捕获零重叠——两群体不相交，BLE001/M12 门禁均不覆盖前者）
- **裁定**：①不做批量 logger 化（122 处中 ~87% 为合理形态，批量改写=高扰动低收益，违反最小变更原则）；②真吞错族以抽样发现为准定点修——capacity_assurance hash-chain 裸 pass 已修（91aca745）；event_store.py 坏事件静默跳过随 B6 event_store 退役裁定一并处置；③防复发建议（Owner 可选）：新增代码检查器（AST 窄捕获+pass 且无注释豁免→WARN），只拦新增不追存量
- **建议 Owner**：接受"抽样定点+新增门禁"路线，否决"122 处批量治理"（审计 B5 原问句的答案）

# 六、B12 运行时装配批 32 模块（总管裁定：维持现状+口径建议）

- 实测：32 实质模块（审计称 33，差 1 口径）；26 production/6 design；**32/32 生产零消费**（各有 ≥1 专属测试）；全部为 2026-08-25/26 六个 DIGEST"候选晋升"commit 引入
- 关键发现：Owner 2026-08-27 裁定三已确立三层装配架构（wiring_registry 台账已建：28 exempt+1 unwired；Layer-2 需求驱动装配；Layer-3 90 天 orphan 门禁）——**B12 的机制去留 Owner 已裁定过**（"不做 313 全量猜测性接线"）；2026-08-28 Owner 口径"production 转态 ≠ 功能翻开"与 AI-04"MATURITY=production 失实"两文本并存
- **建议 Owner**：二选一收口口径张力——(a) MATURITY 词表增设 wiring 维度（production_unwired）或 (b) 蓝图 §0.6 注记"MATURITY=代码成熟度，装配状态以 wiring_registry 为真源"；Layer-3 90 天门禁落地排期（openlineage_exporter 唯一 unwired 项是首查对象）
- 定点已修：asset_inventory 坏动态导入（91aca745）

# 七、B18 残余 10 表语义口径（总管裁定：逐表口径建议清单）

回填脚本 apply_roor_fix.py 用"max-list 启发式"（取 YAML 最大数组长度当 entry_count）——对单数组表正确，对多数组/非 YAML 表产生语义错误值。逐表建议：

| 表 | 现值 | 实测 | 建议口径 |
|---|---|---|---|
| REG-CAPCAN-001 | 367 | capabilities=370（lookup 实测 declared 370/alive 354） | 计数单位=capability 条目，回填 370；creation_tokens(1518)/di_seam(535) 是独立数组不入本表 |
| REG-GEN-001 | 1517 | creation_tokens=1518 | **语义错位**：1517 是 creation_tokens 数，与描述（生成器别名）不符——建议口径改"creation_token 登记记录"或 entry_count 改 19（生成器别名）二选一 |
| REG-SKILL-001 | 22 | skill_*.yaml=22 ✓ | 维持；描述类目（16 dom）更新为 19 dom |
| REG-ARCH-PANORAMA-001 | 39 | PG domains=74 | 单位=域定义，回填 74（或按 status 拆分注明） |
| REG-DEPGRAPH-001 | 9122 | nodes=7982 / nodes_metadata=9148 / edges=20279 | 单位三选一（建议 nodes_metadata，或描述加三值）；现值与任何表现值不符 |
| REG-STD-005~008 | 3×4 | trae_048 sections=22 | **max-list 误产物**：3=文件顶层 aliases 长度——建议按各表语义单位回填（5 状态/12 检查/3 级/4 文件） |
| REG-INV-001 | 0 | asset index total=24415 | **回填遗漏+口径矛盾**（描述"六大目录全部文件资产"）——entry_count=total_assets |
| REG-KB-001 | 4 | knowledge_entries=0 | 4=reserved_ranges 长度；描述自认"当前为空"——entry_count=0 + 计数单位注记 |
| REG-FUNC-DOMAIN-001 | （无字段） | — | 唯一缺 entry_count 的表——补 |
| 8 张业务表 | — | STR 146 vs 149 / FCT 140 vs 161 / RLM 111 vs 117 / DATAFLOW 206 vs 221 / ATH 35 vs 36 / UNI 6 vs 7 / BMK 8 vs 9 / CST 5 vs 6 | 回填时点后漂移（部分为排除 deprecated 口径）——建议统一口径"含 deprecated 全量"或"仅 active"并注明 |

- **建议 Owner**：批准"counting_rule 字段"入 ROOR schema（每表声明计数单位），后续由生成器自动回填（机械施工可派）；REG-STD-005~008/INV-001/KB-001 三族属确定性错误应优先修正

# 八、B20 残余裁定（总管裁定：三线收口）

- **120 字符串引用**：已裁定并施工——59+2 真实锚定（AI-00 修复脚本 src. 前缀 bug 漏网）已重锚 66 文件（adb2e755）；余下泛词巧合命中（__init__/models/db 等 32 条）维持 none 属实。**此项关闭**
- **tests [BLUEPRINT] 断链 115 条**（governance 20/scripts 12/sell_decision 10/ex_sor 8/position 8...）：其中 58 条连字符路径（下划线变体存在）为**机械可修**（AI-21 已修 531 条同型漏网）；57 条真缺失目标。建议：机械 58 条可派施工；真缺失 57 条随蓝图建设缺口一并处置
- **蓝图建设缺口 252 项**（重扫现值 271=缺蓝图 151+聚合未收录 120）：抽样裁定边界——**~20% 机械**（19 条连字符漂移+2 条域归属错配如 signal_ashare 指向 _domain_signal）、**~70% 内容工程**（蓝图未写/聚合索引缺口）、~10% design-memo 类。建议：机械族可派施工；内容工程族属 Owner 排期（蓝图建设专项，C 类台账债）
- **空 [CONSUMERS] 1349 文件**（现值，审计时点 1302）：抽样 10/10 均非真零消费（8 未回填+2 包入口隐式）——**主体是批量回填欠账非僵尸**。建议：不做模式级批量回填（回填需逐文件核实消费者，误填比空值危害大）；维持 HEADER-ANCHOR 新门禁方案（§6#16，AI-11-002 设计已备）只拦新增

# 九、B21 依赖镜像门禁设计（总管建议方案，D1 预算待批）

- 病灶：requirements.txt↔pyproject 依赖漂移曾实锤 2 包缺失（scikit-learn/tzdata，AI-01 人工实测才发现）
- 建议方案（对齐 SECRET-REGISTRY 拦截模式）：pre-commit 新增 gate-dep-mirror——读 pyproject [project].dependencies + requirements*.txt，双向 diff（pyproject 有而 requirements 无 / 反向），不一致即红；豁免通道走现有 noqa 登记+commit message 说明。实现 ~40 行（无网络，纯文件比对），优先级中
- **建议 Owner**：批准 D1 预算后可派施工（机械）

# 十、B6/B7/B9/B13/B14 退役/接线（总管深查后分流：已执行 2 项 / Owner 8 项）

## 已执行（证据推翻前轮 Owner 定性，B15 模板施工，6344c713）
- **B8 rule_watcher（439 行）**：前轮"蓝图锚背书"定性被推翻——governance_core_blueprint 无 §rule_watcher 章（锚悬空）、作战地图零锚定、零生产/零测试 import → 纯僵尸 salvage
- **B6 hooks 包（242 行）**：纯重复实现（活体=governance.ops_governance.event_hook 有真实消费方）→ salvage

## Owner 裁定项（规划语义浓度实证）
| 项 | 浓度 | 承载证据 | 总管建议 |
|---|---|---|---|
| B9 ashare_stop_loss_engine | **高** | BM-RC-05-A"六种A股止损模式"环节文件级点名+锚 production（Owner 交易方法论载体）；亏损限额分支另有 CAND-HARVEST-0135+35号裁定 | 保留待接线（Owner 交易能力规划）；建议蓝图补"接线里程碑"防止无限期悬置 |
| B13 nan_processor | **高** | 15号文 L112 Owner 裁定原文点名+**策略面冲突**（模块提供 bfill/linear/mean 六策略 vs 15号文禁前视填充） | 退役或删禁用策略：因 15号文已定"独立服务化暂无必要"，建议**退役**（判定依据=Owner 既有裁定，非新裁定）；若保留须删 bfill/linear/mean 三策略 |
| B7 semantic_audit/orchestrator | 高 | BM-SEL-11 primary 锚+蓝图规模跃迁规划（1500 模块/100 并发）；但 [TESTS] 声明不实（测试不测它）、MOD-INF-027 蓝图文件不存在 | 接线（补 CLI/事件入口）或退役+BM-SEL-11 锚改挂他模块；二选一需 Owner 定 |
| B6 event_store | 高 | MOD-INF-002 RI-13 复用规划专条（"独立落地/Phase 3 触发式/CQRS"） | 保留（Phase 3 规划位）；表头 frozen/evolving 自相矛盾应修 |
| B6 h1_cqrs_projectors | 中 | CQRS 读端规划（子蓝图 §4.3+数据架构 §12.4.2） | 保留 |
| B14 trading/ports (MOD-INF-035) | 中 | BM-EXE-02 primary（planned） | 保留待接线 |
| B14 gpu_consensus_scheduler（双实现） | 中 | BM-BUY-08 primary+蓝图 GAP-003 Phase 2；**双实现本身是问题**（behavioral_admission 569 行+trading 598 行零消费） | 双实现去留+合并方向需 Owner 定 |
| B14 integration/ports (MOD-INF-009) | 中 | BM-SEL-02-C primary | 保留待接线 |
| B14 ide_watcher (MOD-INF-019) | 中 | 蓝图 CircadianScheduler 调度规划（接线未落地；注意 CircadianScheduler 已被 trae_060 废止——规划本身过期） | 建议退役（规划载体已废止） |
| B14 embedding_provider_adapter | 中 | 15号文 S1.3 批量档配套规划+human_gated | 保留 |
| B14 multifactor 三件 | 无（文件级） | translation 无条目+蓝图锚不存在+MOD-L02-009/014 真源是别的文件；但模块 ID 与作战地图锚存在错位纠缠 | 可 salvage（B15 模板），因 ID 错位需先在 battle_map 确认锚由 decay_monitor/abs001_gate 满足——建议派施工前 Owner 过目一眼 |
| B14 api_client（480 行，审计记 248 行有误） | 中（弱） | shared_core B35 缺口条目（"有 HTTP 层缺模型语义层"） | 接线或退役随 B35 缺口裁定 |

# 十一、B10/B11 market_data 集群+redundant_source（Owner）

- AI-04 五信号实证（①③④⑤全中）+ 2026-08-27 Owner 裁定三框架（同 B12）：批量 salvage 涉 3 登记表+depgraph+RecoveryManager 进程内轮询守护属"结构性违规需机制裁定"
- **建议**：随 B12 三层装配架构 Layer-3 门禁统一处置（90 天无消费→自动 orphan 报告→Owner 批量裁定）；不建议单独 salvage（同族问题分批处置=口径漂移）

# 十二、裁定复核结论（REVIEW 项）

1. **dad7b9e36d 测试放宽**：**通过**——放宽仅 acknowledged 计数下限（18→15，防外部占位环节增删的防御性下限），违规孤儿环节==[] 的本体断言（L231/243 hard==[]）未动，无掩盖回归
2. **semantic_audit shim 方向**：**通过**——B3 施工复用 A13 范式并验证六路径类同一性；gov_audit 为实现真源方向与登记一致
3. **MOD-INF-016 不改号**：**通过**——#ARCH-058 在册（architecture_issue_registry 实测 10 处引用）；B3 收敛后副本 shim 保留 MOD-INF-016 锚与统一状态裁定一致
4. **蓝图缺口 252 项判定边界**：见 §八（20% 机械/70% 内容工程/10% memo 类）

# 十三、预存问题登记（非本任务引入，供 Owner 知悉）

0. **unified-asset-index 双写者+扫描口径分歧（新增，重要）**：审计报告 §8-9 预期"total_assets≈31847/Health B"不可复现——31847/B 由 `scripts/governance/generate_asset_index.py` 手动全量生成（该脚本现已归档至 _archive/prototype/，输出含 json_data 14545+other 7924 的宽扫描面）；后台 reconciler 写入者持续产出 24422/C（窄扫描面）且已被后续 wave 收编提交（HEAD=24415/C）。**需 Owner 裁定唯一真源写者+扫描口径**（建议：恢复 generate_asset_index.py 为活体并接入 atomic_write_if_changed，或修 reconciler 写入者对齐宽口径）；历史好态样本在 commit 73dbf90f

1. tests/infrastructure/test_cross_blueprint_e2e.py::test_e2e_finding_to_taskcard_full_chain 顺序依赖缺陷（ServiceRegistry task_repo 工厂跨测试依赖，2026-06-21 a5c1a81787 引入便捷函数所致；组合跑 25 全过/隔离跑红；全量 stash 复验非 steward 回归）——建议测试注入 repo 或便捷函数 dry_run 容忍未注册
2. CH 探测 404（ClickHouse kline_daily/stk_limit/news_sentiment_window/margin 表探测 TCP+HTTP 均失败，Gateway 运行期非阻断输出）——按项目记忆 CH 应打 172.24.30.100，疑似探测目标或服务端状态问题，建议环境侧排查
3. path_ownership_map.yaml YAML 解析错误（L52124 引号内文档分隔符，HEAD 预存）——派生再生时自愈
4. 资产索引工作区态 24395/C（残缺上下文扫描产物，已提交态 31847/B）——收尾批以主仓全量再生覆盖

# 十四、总管施工总账（七个 commit）

| # | commit | 内容 |
|---|---|---|
| 1 | b0a0aef7 | 词表门禁终清零（noqa merge 回归修复+4 WARN+startup v1.1.0） |
| 2 | a14cd9a0 | B1+B2 batch_id 批次写入方全链接线+PENDING→READY 连带缺陷 |
| 3 | 4dd2e2e4 | B3 RiskLimits 双 codegen 收敛+两预存红测试修复 |
| 4 | 8d1929d4 | B4 Timer 周期调仓改事件驱动 |
| 5 | adb2e755 | B20 [TESTS] none 误标 66 文件重锚（AI-00 前缀 bug） |
| 6 | 6344c713 | B16 四入口行数门禁全绿+B8/B6-hooks salvage |
| 7 | 91aca745 | B22①②④+B5/B12 定点治本（ops_guard 根修/13 xfail 摘除/redup 诚实化/REPO_ROOT 回显/hash-chain 留痕/坏导入修复） |
| 8 | （收尾批） | 派生波收编+资产索引主仓再生+本报告 §9 状态更新 |

**B 类 24 项总清算**：B1✅ B2✅ B3✅ B4✅ B5✅(定点+裁定) B6-hooks✅ B6-event_store→Owner B7→Owner B8✅ B9→Owner B10→Owner B11→Owner B12✅(裁定+定点) B13→Owner(建议退役) B14→分流(2 salvage 候选+5 Owner) B15✅(前序) B16✅ B17✅(裁定书§二) B18✅(裁定书§七) B19✅(前序) B20✅(66 重锚+裁定书§八) B21→设计备妥 B22✅(①②④施工+③⑤ Owner) B23✅(前序) B24✅(复核通过)
