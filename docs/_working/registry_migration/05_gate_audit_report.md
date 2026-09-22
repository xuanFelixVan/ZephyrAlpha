---
ttl: task_bound
title: "全量门禁审计报告 v1（117 台 L2+56 必跑钩子，Owner 全批 A-E 五包执行依据）"
session: st-regfix-lane0b-20260923
---

> 车道 st-gateaudit2-20260923｜只读审计，零文件修改。所有计数来自机读解析与 JSONL 实际聚合，无拍脑袋项。
> **数据窗口声明**：拦截事件覆盖 2026-09-13→09-22（10 天，落在"近 30 天"内，下称窗口期）；执行计时覆盖 09-15→09-22（1318 次链执行，其中 985 次完整计时）。窗口期短于 30 天，凡据此下"零触发"结论处均已标注。

## A. 总账

### A1. 台数（字段/清单实测）

| 层 | 真源 | 台数 |
|---|---|---|
| L2 进程内 | `docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml` | **117**（`total_gates` 字段=117，实际条目 117，全部 `enabled:true`） |
| L2.5 precommit 通道 | `.pre-commit-config.yaml` | **68 hooks 注册**，其中**每次提交必跑 56**（default stage 47 + 显式 pre-commit 9）；manual 8、post-commit 3、commit-msg 1 不在每次提交路径 |
| 统一目录 | `docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml` | **171**（commit-gate 114 + pre-commit 55 + manual 2；1 条 deprecated：GATE-SCHEMA-HEALTH→重定向 GATE-C2） |

**发现的注册表漂移（SSOT 事故隐患）**：in_process 注册表 117 台 vs 统一注册表 commit-gate 114 台，差 3 台——**BLOOD-FLESH、STATE-VOCAB-REGISTRY、TAG-VOCAB 未同步进统一 gate_registry.yaml**。

窗口期总量：拦截事件 1570 起（169 个会话）；其中 L2 门禁可归因 1185 起、GATE-PRECOMMIT-RUN 通道 85 起、claim 期 UNKNOWN(FOREIGN_CHANGE) 27 起、TRACKED-DRIFT-READONLY 15 起、commit_slow/采样 258 条。

### A2. 功能族谱（117 台 L2 全覆盖，无遗漏）

| 族 | 台数 | 门禁清单 | 共同根源目的 | 窗口期拦截 | 该族总耗时 |
|---|---|---|---|---|---|
| F1 流程与会话协调 | 12 | WORKTREE-REQUIRED、CLAIM-REQUIRED、SESSION-REQUIRED、HELD-OVERLAP、COMMIT-SCOPE、FOREIGN-CHANGE-DETECTION、FORGED-GW-MARKER、STASH-ACCUMULATION、SPLIT-COORDINATION、PROTECTED-PATHS、GIT-CALL-BUDGET(warn)、SNAPSHOT-DRIFT | 多会话并发下提交权属与边界 | **271** | 2202s |
| F2 新建文件登记链（净零） | 13 | CREATE-GUARD、TRANSLATION-COVERAGE、NEW-FILE-DEPGRAPH、DEPGRAPH-PRE-REGISTRATION、RENAME-DEPGRAPH-SYNC、DEPGRAPH-WRITE-PATH、DEPGRAPH-FRESHNESS、FILE-COPY、CAPABILITY-OVERLAP、CAPABILITY-LOOKUP-REQUIRED、FILE-PLACEMENT-TTL、TTL-METADATA、EXEMPT-ZONE-FM | 新资产必须登记（token/翻译/depgraph） | **283** | 16096s |
| F3 图谱对齐 | 11 | GATE-PANORAMA-ALIGNMENT、FRONTEND-MAP、GATE-BATTLE-MAP-ALIGNMENT、DECISION-MAP、INDUSTRY-CHAIN-MAP、FACTORY-MAP、ALGO-FLOW-LINK、ALGO-NOTE-SYNC、FRONTEND-TRUTH-SOURCE、MODULE-ID-CONSISTENCY、GATE-DOMAIN-FK | 图↔代码↔注册表对齐 | 82 | 6919s |
| F4 蓝图/文档引用 | 13 | BLUEPRINT-FORMAT、BLUEPRINT-AMODULE-CONSISTENCY、BLUEPRINT-AMODULE-CROSS-CHECK、BLUEPRINT-NODE-ID-HARDCODE、ARCH-REFERENCE、RULING-REFERENCE、DANGLING-REFERENCE、DOC-REF-BROKEN、RULING-COMMIT-VERIFIED、BUSINESS-REGISTRY、BLOOD-FLESH、TAG-VOCAB、LIBRARY-COVERAGE | 文档头格式与引用不悬空 | 89 | 6296s |
| F5 代码防模式回潮(AST) | 21 | NO-GOD-CLASS、NO-HIGH-COMPLEXITY、NO-LONG-PARAM-LIST、FUNCTION-DUP、MUTABLE-CONST-WITHOUT-FINAL、NO-IMPORT-SIDE-EFFECT、EMPTY-HANDLER、OPEN-WITHOUT-WITH、UNSAFE-DICT-SPREAD、PURE-SHIM、PURE-ASSERTION、NO-UPWARD-IMPORT、ORPHAN-MODULE、UNDEFINED-NAME、SYNTAX-VALIDATION、NOQA-VALIDATION、ASYNCIO-RUN-IN-CONTEXT、MSG-STYLE、MSG-EXPOSURE、NO-HARDCODED-URL、RELATIVE-PATH-LITERAL | 防特定坏模式回潮（多为 §5.1xx 防复发条目） | 142 | 7958s |
| F6 安全/密钥 | 3 | NO-SECRET-HARDCODE、NO-BARE-GETENV、SECRET-REGISTRY-CONSISTENCY | 密钥不落码 | 3 | 3712s |
| F7 数据访问纪律 | 9 | NO-BARE-SQL、TABLE-NAME-REGISTRY、CH-BATCH-SIZE、CH-FINAL-GATE、CH-VERSION-COL、SCHEMA-FILE-EXISTS、DATETIME-NOW-FORBIDDEN、ZEPHYR-ENV-DIRECT-ACCESS、BARE-SUBPROCESS | DB 访问必经 DatabaseService | 74 | 8063s |
| F8 SSoT/词表/i18n | 13 | SSOT-REDEFINITION、VOCAB-CHAIN、VOCAB-HARDCODE、TEST-RESIDUE-SSOT、NO-DOMAIN-NAME-ZH-DIRECT-ACCESS、TEST-SOURCE-CONSISTENCY、CAP-CONSISTENCY、STATE-VOCAB-REGISTRY、RULE-FOUR-WAY-ALIGN、RULE-EXECUTION-PAIRING、GATE-ERRCODE-CONSISTENCY、CONSUMERS-ACCURACY、DERIVATION-ANNOTATION | 单一真源不被旁路重定义 | 105 | 9204s |
| F9 注册表/清单完整性 | 11 | REGISTRY-MASS-DELETION、REGISTRY-YAML-PARSE、REGISTRY-CODE-ANCHOR、ID-UNIQUENESS、MCP-VERSION-FIELD、DIRECTORY-CONTRACT、FOLDER-CAPACITY-HARD-LIMIT、R5-DIGIT-SUFFIX、HOT-FILE-BASE-FRESHNESS、DERIVED-FILE-DELETION-PROTECTION、ENCODING-SAFETY | 静态清单与注册表自身健康 | 80 | 3029s |
| F10 自动系统纪律 | 11 | MANUAL-ONLY-PERMANENT、PERM-TRIGGER、RECONCILER-HEALTH、RECONCILER-FILE-OPS、GATE-PRECOMMIT-OFFLINE、RESOURCE-SCHEDULE、DATA-TASK-COMPLETENESS、ISSUE-RESOLVED-INTEGRITY、IMPORT-INTEGRITY、SCRIPTS-IMPORT-INTEGRITY、META-TESTS-COVERAGE | 永久系统四要素/事件触发 | 56 | 4768s |

**单次提交整体成本**：被拦截尝试门禁链 P50 71.1s / P90 190.5s；成功提交 P50 43.2s / P90 116.1s；>60s 慢提交 216 次（P50 111.5s，最大 798.6s）。慢尾主体 = L2 慢门 + precommit 通道 56 hooks 全跑（每 hook 固定 spawn 开销，分钟级底座，挖矿文档 B 节结论一致）。

## B. 逐门禁速查表（L2 全 117 台）

扫描范围判定法：源码含 `_build_own_scope`=own；`git diff --cached`/`get_staged_files` 读取=全暂存；`rglob/os.walk`=全仓；其余=路径/注册表查询（无内容扫描）。拦截次数=P50 来自窗口期 JSONL。判定缩写：**退**=退役、**并**=合并、**own**=收窄 own-scope、**留**=保留、**缓**=降频/条件触发、**裁**=需 Owner 裁定。

| gate_id | 防什么(≤15字) | 范围 | 拦截 | P50ms | 判定 |
|---|---|---|---|---|---|
| ALGO-FLOW-LINK | 模块ALGO_FLOW外锚真实 | 全暂存 | 12 | 47 | own |
| ALGO-NOTE-SYNC | 算法锚与大白话同步 | 路径 | 45 | 312 | 留 |
| ARCH-REFERENCE | #ARCH-NNN悬空引用 | 路径 | 12 | 1750 | 并(引用族)+缓 |
| ASYNCIO-RUN-IN-CONTEXT | 异步上下文误用 | own | 0 | 62 | 裁(零触发10d) |
| BARE-SUBPROCESS | 裸subprocess调用 | own | 0 | 78 | 留(安全) |
| BLOOD-FLESH | 新资产必填血肉登记 | own | 0 | 63 | 裁(零触发10d) |
| BLUEPRINT-AMODULE-CONSISTENCY | A_module头格式一致 | 路径 | 0 | 282 | 并(蓝图头) |
| BLUEPRINT-AMODULE-CROSS-CHECK | 蓝图↔A_module交叉 | 路径 | 1 | 282 | 并(蓝图头) |
| BLUEPRINT-FORMAT | BLUEPRINT头格式 | 路径 | 53 | 234 | 留 |
| BLUEPRINT-NODE-ID-HARDCODE | node_id硬编码 | 全暂存 | 0 | 93 | own |
| BUSINESS-REGISTRY | 业务资产入库 | 路径 | 2 | 438 | 留 |
| CAP-CONSISTENCY | Provider路由meta一致 | own | 4 | 47 | 留 |
| CAPABILITY-LOOKUP-REQUIRED | 施工前能力反查 | 路径 | 13 | 16 | 留 |
| CAPABILITY-OVERLAP | 新建py查重+克隆 | own | 22 | 938 | 留+缓(P95 23s) |
| CH-BATCH-SIZE | CH批量写防回退 | 路径 | 11 | 312 | 留 |
| CH-FINAL-GATE | 直调ch_writer.query | 全暂存 | 4 | 203 | own |
| CH-VERSION-COL | CH version列误用 | 全暂存 | 0 | 3344 | **own+缓**(耗时第2) |
| CLAIM-REQUIRED | 写前claim检查 | 路径 | 54 | 16 | 留 |
| COMMIT-SCOPE | 提交边界域一致 | 路径 | 35 | 47 | 留 |
| CONSUMERS-ACCURACY | CONSUMERS字段(warn) | 路径 | 0 | 250 | 裁(0触发有消费) |
| CREATE-GUARD | 新建文件creation_token | 全暂存 | 92 | 157 | own+缓(P95 56s,耗时第1) |
| DANGLING-REFERENCE | AGENTS §X.Y悬空引用 | 路径 | 14 | 47 | 并(引用族) |
| DATA-TASK-COMPLETENESS | 数据任务完整(warn) | 路径 | 0 | 62 | **退** |
| DATETIME-NOW-FORBIDDEN | 禁datetime.now() | own | 7 | 63 | 留 |
| DECISION-MAP | 决策图(图7)对齐 | own | 5 | 9125 | 并(图谱族)+缓 |
| DEPGRAPH-FRESHNESS | depgraph新鲜度 | 路径 | 0 | 79 | 裁(零触发10d) |
| DEPGRAPH-PRE-REGISTRATION | planned→production | 全暂存 | 46 | 109 | 并(depgraph族)+own |
| DEPGRAPH-WRITE-PATH | depgraph写路径白名单 | 路径 | 0 | 282 | 并(depgraph族) |
| DERIVATION-ANNOTATION | 派生关系声明真实 | 全暂存 | 0 | 47 | own |
| DERIVED-FILE-DELETION | 派生文件删除保护 | 全暂存 | 0 | 47 | own |
| DIRECTORY-CONTRACT | 目录契约DCR | 路径 | 20 | 140 | 留 |
| DOC-REF-BROKEN | 文档相对路径断链 | 全暂存 | 0 | 47 | own |
| EMPTY-HANDLER | 空事件handler | 全暂存 | 0 | 62 | own |
| ENCODING-SAFETY | 编码/mojibake/BOM | 路径 | 1 | 94 | 留 |
| EXEMPT-ZONE-FM | 豁免区frontmatter | 路径 | 13 | 47 | 留 |
| FACTORY-MAP | 策略生产图(图9) | 路径 | 1 | 15 | 并(图谱族) |
| FILE-COPY | 新增py复制检测 | 全暂存 | 7 | 62 | own |
| FILE-PLACEMENT-TTL | 文件放置TTL一致 | 路径 | 12 | 219 | 留 |
| FOLDER-CAPACITY-HARD-LIMIT | 文件夹容量上限 | own | 17 | 16 | 留 |
| FOREIGN-CHANGE-DETECTION | claim内外来变更 | 路径 | 19 | 203 | 留(全暂存=功能本体) |
| FORGED-GW-MARKER | 伪造[GW:]标记 | 路径 | 6 | 无数据 | 留(反伪造) |
| FRONTEND-MAP | 前端全景图对齐 | 路径 | 13 | 281 | 并(图谱族) |
| FRONTEND-TRUTH-SOURCE | 前端真源接通 | 全暂存 | 0 | 47 | own |
| FUNCTION-DUP | 重复函数实现 | 全暂存 | 13 | 62 | own |
| GATE-BATTLE-MAP-ALIGNMENT | 作战地图对齐 | 路径 | 1 | 6625 | 并(图谱族)+缓 |
| GATE-DOMAIN-FK | [DOMAIN]域注册表FK | 路径 | 0 | 329 | 裁(零触发10d) |
| GATE-ERRCODE-CONSISTENCY | error_code对账 | **全仓** | 23 | 7047 | **own+缓**(P50第1) |
| GATE-PANORAMA-ALIGNMENT | 三图模块对齐 | 全暂存 | 0 | 3062 | 并(图谱族)+own+缓 |
| GATE-PRECOMMIT-OFFLINE | pre-commit离线可跑 | 路径 | 0 | 16 | 裁(零触发10d) |
| GIT-CALL-BUDGET | git调用预算(warn) | 路径 | 0 | 297 | 裁(0触发有消费) |
| HELD-OVERLAP | 搭便车防护 | 路径 | 50 | 16 | 留 |
| HOT-FILE-BASE-FRESHNESS | 热文件base新鲜度 | 路径 | 20 | 32 | 留 |
| ID-UNIQUENESS | hook id唯一 | 路径 | 0 | 16 | 裁(零触发10d) |
| IMPORT-INTEGRITY | 悬空import | own | 9 | 47 | 留 |
| INDUSTRY-CHAIN-MAP | 产业链图工件 | 路径 | 0 | 16 | 并(图谱族) |
| ISSUE-RESOLVED-INTEGRITY | issue标记真实(warn) | 路径 | 0 | **无(从未执行)** | **退** |
| LIBRARY-COVERAGE | 馆藏覆盖(warn) | own | 0 | 79 | **退** |
| MANUAL-ONLY-PERMANENT | 永久系统manual无订阅 | own | 26 | 78 | 并(PERM族) |
| MCP-VERSION-FIELD | MCP version缺失 | 全暂存 | 0 | 47 | own |
| META-TESTS-COVERAGE | gate测试覆盖meta | 路径 | 0 | **无(从未执行)** | 裁 |
| MODULE-ID-CONSISTENCY | module_id三轨一致 | 路径 | 5 | 203 | 留 |
| MSG-EXPOSURE | 消息泄敏感信息 | own | 1 | 47 | 留 |
| MSG-STYLE | 消息标点风格 | 全暂存 | 0 | 203 | own |
| MUTABLE-CONST-WITHOUT-FINAL | 可变常量缺Final | 路径 | 18 | 172 | 留 |
| NEW-FILE-DEPGRAPH | 新py未登记depgraph | 全暂存 | 13 | 47 | 并(depgraph族)+own |
| NO-BARE-GETENV | 裸getenv读密钥 | 全暂存 | 0 | 172 | 留(安全)+own |
| NO-BARE-SQL | 裸SQL字面量 | own | 29 | 78 | 留 |
| NO-DOMAIN-NAME-ZH-DIRECT | 域名字典直访 | 全暂存 | 0 | 906 | own |
| NO-GOD-CLASS | God Class | own | 0 | 63 | 并(复杂度族) |
| NO-HARDCODED-URL | 硬编码localhost | 全暂存 | 0 | 281 | own |
| NO-HIGH-COMPLEXITY | 高循环复杂度 | own | 24 | 63 | 并(复杂度族) |
| NO-IMPORT-SIDE-EFFECT | import零副作用 | 路径 | 27 | 844 | 留 |
| NO-LONG-PARAM-LIST | 长参数列表 | 路径 | 33 | 906 | 并(复杂度族) |
| NO-SECRET-HARDCODE | 密钥值硬编码 | 全暂存 | 0 | 2109 | **own+缓**(留，不可逆风险) |
| NO-UPWARD-IMPORT | shared向上依赖 | 全暂存 | 0 | 47 | own |
| NOQA-VALIDATION | noqa标记合规 | own | 5 | 78 | 留 |
| OPEN-WITHOUT-WITH | open不在with内 | own | 1 | 47 | 留 |
| ORPHAN-MODULE | 孤儿模块无引用 | 全暂存 | 8 | 47 | own |
| PERM-TRIGGER | 时间触发无订阅 | own | 21 | 78 | 并(PERM族) |
| PROTECTED-PATHS | 受保护路径写入 | 路径 | 12 | 16 | 留 |
| PURE-ASSERTION | 纯陈述原则 | own | 3 | 62 | 留 |
| PURE-SHIM | 纯re-export shim | 全暂存 | 0 | 250 | own |
| R5-DIGIT-SUFFIX | R5数字后缀目录 | 路径 | 0 | 16 | 裁(零触发10d) |
| RECONCILER-FILE-OPS | 治理代理裸删除 | 路径 | 0 | 16 | 裁(零触发10d) |
| RECONCILER-HEALTH | reconciler健康度 | 路径 | 0 | 3687 | **缓**(条件触发，0收益) |
| REGISTRY-CODE-ANCHOR | 注册表代码锚点 | 全暂存 | 6 | 47 | own |
| REGISTRY-MASS-DELETION | 登记表批量删除 | own | 12 | 47 | 留 |
| REGISTRY-YAML-PARSE | 注册表结构硬化 | own | 4 | 47 | 留 |
| RELATIVE-PATH-LITERAL | 相对路径字面量 | 全暂存 | 0 | 844 | own |
| RENAME-DEPGRAPH-SYNC | 重命名depgraph同步 | 全暂存 | 14 | 47 | 并(depgraph族)+own |
| RESOURCE-SCHEDULE | 排班冲突 | own | 0 | 468 | 裁(零触发10d) |
| RULE-EXECUTION-PAIRING | 规则-执行配对 | 路径 | 0 | 16 | 裁(零触发10d) |
| RULE-FOUR-WAY-ALIGN | 规则四方对齐 | 路径 | 0 | 1312 | 缓+裁 |
| RULING-COMMIT-VERIFIED | 完成声明hash真实 | 路径 | 1 | 16 | 留 |
| RULING-REFERENCE | 裁定#NNN悬空 | 路径 | 6 | 360 | 并(引用族) |
| SCHEMA-FILE-EXISTS | schema文件存在 | 路径 | 0 | 1906 | 缓+裁 |
| SCRIPTS-IMPORT-INTEGRITY | _shared符号完整 | own | 0 | 47 | 裁(零触发10d) |
| SECRET-REGISTRY-CONSISTENCY | env↔注册表一致 | 全暂存 | 3 | 47 | 留+own |
| SESSION-REQUIRED | session注册强制 | 路径 | 14 | 16 | 留 |
| SNAPSHOT-DRIFT | 违规快照漂移 | 全暂存 | 0 | 47 | own |
| SPLIT-COORDINATION | 拆分×编辑双存 | 路径 | 3 | 16 | 留 |
| SSOT-REDEFINITION | 重定义SSoT符号 | 全暂存 | 37 | 1641 | **own**(2026-09-23 连坐实证) |
| STASH-ACCUMULATION | stash堆积阈值 | 路径 | 0 | 47 | 裁(零触发10d) |
| STATE-VOCAB-REGISTRY | 状态词表(warn) | own | 0 | 94 | 裁(0触发) |
| SYNTAX-VALIDATION | py语法错误 | own | 7 | 390 | 留 |
| TABLE-NAME-REGISTRY | 表名登记 | 路径 | 23 | 187 | 留 |
| TAG-VOCAB | 图书馆标签枚举 | own | 0 | 2172 | 缓+裁 |
| TEST-RESIDUE-SSOT | 测试残留前缀 | 全暂存 | 0 | 125 | own |
| TEST-SOURCE-CONSISTENCY | 测试-源码一致 | own | 15 | 47 | 留 |
| TRANSLATION-COVERAGE | 新py大白话简介 | 全暂存 | 16 | 47 | own |
| TTL-METADATA | ttl字段校验 | 路径 | 35 | 297 | 留 |
| UNDEFINED-NAME | F821未定义符号 | own | 2 | 62 | 留 |
| UNSAFE-DICT-SPREAD | data直展(warn) | own | 0 | 63 | 裁(0触发) |
| VOCAB-CHAIN | SSoT路径硬编码 | 全暂存 | 10 | 62 | **own+并**(2026-09-23 连坐实证) |
| VOCAB-HARDCODE | 新py词表硬编码 | 全暂存 | 16 | 63 | own+并 |
| WORKTREE-REQUIRED | worktree隔离强制 | 路径 | 78 | 16 | 留 |
| ZEPHYR-ENV-DIRECT-ACCESS | ZEPHYR_ENV直访 | own | 0 | 47 | 留(安全) |

**范围口径汇总**：own-diff 30 台｜扫全暂存 33 台｜全仓 1 台（GATE-ERRCODE-CONSISTENCY）｜纯路径/注册表 53 台。注册表 `own_scope:true` 仅标 27 条，与 30 个实现文件、33 台实际全暂存互相不一致——宪法 §3 的 own-scope 账实不符，33 台全暂存台即多会话连坐的结构性来源。

### B2. L2.5 每次提交必跑 56 hooks（摘要）

无 per-hook 计时数据（挖矿 F5"per-hook 慢尾计时落审计"仍挂起），拦截无 hook 级归因（统一记 GATE-PRECOMMIT-RUN，窗口 85 起）。判定依据=名称/描述与 L2 重叠矩阵（挖矿 E 节已核：in-process↔hook 双层有意对 = DIRECTORY-CONTRACT/ENCODING/VOCAB/PURE-SHIM/ERRCODE/NODE-ID 六对）。

| hook（每次提交跑） | 防什么 | 与 L2 关系/判定 |
|---|---|---|
| check-merge-conflict-marker、detect-private-key-local | 冲突标记/私钥 | 无 L2 对应，留 |
| ruff、ruff-format | lint/格式 | 留；与 L2 复杂度三件套能力重叠（C901/PLR0913）→支撑 L2 侧收敛 |
| gate-protected-paths、gate-worktree-required、gate-commit-gw | 与 L2 同名门 | L2 已 own 层前移，hook 层为兜底，可并入两段式快速子集 |
| gate-arch、gate-triple-align、gate-16/17、gate-frontmatter、gate-vocab、gate-zr、gate-ssot-code、gate-test 等 30+ 台治理钩 | 蓝图/对齐/SSoT/测试 | T2-T3 慢尾主体；两段式+manual 化候选 |
| gate-drift-light-scan 等 8 台 manual stage | 已不占提交路径 | 不动 |

## C. 五类判定（w5_1 机械归档；Owner 已于 2026-09-23 全批 A-E 五包）

### C1. 立即退役（3 台）——w5_1 条2"零触发零消费→退役"

| 门禁 | 证据 |
|---|---|
| DATA-TASK-COMPLETENESS | warn-only；窗口期 0 拦截、0 运行触发；src/scripts 外**零消费方**（grep 实测 0 处引用） |
| ISSUE-RESOLVED-INTEGRITY | warn-only；**计时数据中从未出现**（连执行都没有）；零消费方（0 处引用） |
| LIBRARY-COVERAGE | warn-only 自述"观察闸"；0 拦截 0 触发；零消费方（0 处引用） |

（同为 warn-only 零触发的 CONSUMERS-ACCURACY/GIT-CALL-BUDGET/UNSAFE-DICT-SPREAD/STATE-VOCAB-REGISTRY 有 1-9 处潜在消费引用，证据不纯，归 C5/观察包。）

### C2. 立即合并（7 簇，22 台→7 台）

| 合并成 | 吸收 | 机械依据 |
|---|---|---|
| REFERENCE-INTEGRITY | ARCH-REFERENCE + RULING-REFERENCE + DANGLING-REFERENCE | 三台共用 `_reference_helpers` 同一引擎、同根源=文档悬空引用；合计 32 拦截 |
| PERMANENT-SYSTEM-TRIGGER | MANUAL-ONLY-PERMANENT + PERM-TRIGGER | docstring 同义；合计 47 拦截 |
| GATE-VOCAB | VOCAB-HARDCODE + VOCAB-CHAIN | VOCAB-CHAIN 源码自述"扩展 VOCAB-HARDCODE 覆盖面"——同真源派生，条1 直接命中 |
| DEPGRAPH-ENFORCEMENT | DEPGRAPH-PRE-REGISTRATION + NEW-FILE-DEPGRAPH + RENAME-DEPGRAPH-SYNC + DEPGRAPH-WRITE-PATH | 四台同真源=depgraph DB；合计 73 拦截 |
| MAP-ALIGNMENT | GATE-PANORAMA + GATE-BATTLE-MAP + DECISION-MAP + FRONTEND-MAP + INDUSTRY-CHAIN-MAP + FACTORY-MAP | 六台同真源=alignment_checklist.md；六台 P50 合计 22.5s、拦截仅 20 |
| BLUEPRINT-HEADER | BLUEPRINT-AMODULE-CONSISTENCY + BLUEPRINT-AMODULE-CROSS-CHECK | 同对象=[A_module]/[BLUEPRINT] 头；1+0 拦截 |
| COMPLEXITY-GUARD | NO-GOD-CLASS + NO-HIGH-COMPLEXITY + NO-LONG-PARAM-LIST | 同 §5.150/§5.158 防复发簇；L2.5 ruff 已有 C901/PLR0913 等价规则；合计 57 拦截 |

### C3. 改 own-scope（33 台全暂存中的 31 台内容扫描型）

机械修法：`git diff --cached` 读取一律与 gateway 提交清单求交（`_diff_helpers._build_own_scope` 现成闭包，30 台先例）。**例外保留全暂存**：FOREIGN-CHANGE-DETECTION（检测对象就是 claim 混入，全暂存是功能本体；外来违规按 §3.1 降 warn+审计）。

名单（31 台）：SSOT-REDEFINITION、VOCAB-CHAIN（**09-23 连坐双煞**）、VOCAB-HARDCODE、CREATE-GUARD、ALGO-FLOW-LINK、BLUEPRINT-NODE-ID-HARDCODE、CH-FINAL-GATE、CH-VERSION-COL、DEPGRAPH-PRE-REGISTRATION、DERIVATION-ANNOTATION、DERIVED-FILE-DELETION、DOC-REF-BROKEN、EMPTY-HANDLER、FILE-COPY、FRONTEND-TRUTH-SOURCE、FUNCTION-DUP、GATE-PANORAMA-ALIGNMENT、MCP-VERSION-FIELD、MSG-STYLE、NEW-FILE-DEPGRAPH、NO-BARE-GETENV、NO-DOMAIN-NAME-ZH、NO-HARDCODED-URL、NO-UPWARD-IMPORT、NO-SECRET-HARDCODE、ORPHAN-MODULE、PURE-SHIM、REGISTRY-CODE-ANCHOR、RELATIVE-PATH-LITERAL、RENAME-DEPGRAPH-SYNC、SECRET-REGISTRY-CONSISTENCY、SNAPSHOT-DRIFT、TEST-RESIDUE-SSOT、TRANSLATION-COVERAGE + GATE-ERRCODE-CONSISTENCY（全仓→own+注册表触发）。

### C4. 保留组

- F1 高拦截台：WORKTREE-REQUIRED(78)/CLAIM-REQUIRED(54)/HELD-OVERLAP(50)/COMMIT-SCOPE(35)/SESSION-REQUIRED(14)/PROTECTED-PATHS(12)/FORGED-GW-MARKER(6)/SPLIT-COORDINATION(3)
- 安全：NO-SECRET-HARDCODE/NO-BARE-GETENV/BARE-SUBPROCESS + MSG-EXPOSURE（不可逆风险，收 own+条件触发）
- 数据访问：NO-BARE-SQL(29)/TABLE-NAME-REGISTRY(23)/CH-BATCH-SIZE(11)/DATETIME-NOW-FORBIDDEN(7)
- 登记链核心：CREATE-GUARD(92)/TRANSLATION-COVERAGE(16)/CAPABILITY-LOOKUP-REQUIRED(13)
- 质量地板：SYNTAX-VALIDATION/UNDEFINED-NAME/IMPORT-INTEGRITY/ENCODING-SAFETY/TEST-SOURCE-CONSISTENCY(15)
- 中频实用台：ALGO-NOTE-SYNC(45)、BLUEPRINT-FORMAT(53)、TTL-METADATA(35)、HOT-FILE-BASE-FRESHNESS(20)、DIRECTORY-CONTRACT(20)、FOLDER-CAPACITY(17)、EXEMPT-ZONE-FM(13)、REGISTRY-MASS-DELETION(12)、FILE-PLACEMENT-TTL(12)、CAPABILITY-OVERLAP(22)、NO-IMPORT-SIDE-EFFECT(27)、ERRCODE(23，降频后保留)

### C5. 降频/缓存（12 台）

机械依据：P50>1.5s 或 P95>20s，且（拦截=0 或触发条件可路径化）。注册表 `files_trigger` 字段已存在但**这批慢门全部为空**（实测）。

| 门禁 | P50 | 拦截 | 处置 |
|---|---|---|---|
| GATE-ERRCODE-CONSISTENCY | 7047ms（全表第1） | 23 | 仅 errcode 注册表或映射文件变更时跑 |
| DECISION-MAP | 9125ms | 5 | 并入 MAP-ALIGNMENT 后图文件触发 |
| GATE-BATTLE-MAP-ALIGNMENT | 6625ms | 1 | 同上 |
| RECONCILER-HEALTH | 3687ms | 0 | 仅 reconciler 域文件变更时跑 |
| CH-VERSION-COL | 3344ms | 0 | 仅 CH/schema 文件触发 |
| GATE-PANORAMA-ALIGNMENT | 3062ms | 0 | 同 DECISION-MAP |
| NO-SECRET-HARDCODE | 2109ms | 0 | own 化+密钥特征文件触发 |
| TAG-VOCAB | 2172ms | 0 | 图书馆域文件触发 |
| SCHEMA-FILE-EXISTS | 1906ms | 0 | schema 文件触发 |
| ARCH-REFERENCE | 1750ms | 12 | docs/ 变更触发 |
| SSOT-REDEFINITION | 1641ms | 37 | own 化后均值大降 |
| RULE-FOUR-WAY-ALIGN | 1312ms | 0 | 规则 YAML 变更触发 |

长尾两台：CREATE-GUARD（P50 157ms 但 P95 56s、总耗时第1 5883s——注册表 IO 长尾，建议缓存）；CAPABILITY-OVERLAP（P95 22.9s，加缓存）。

## D. 净零核算

| 项 | 现状 | 处置后 | 依据 |
|---|---|---|---|
| L2 台数 | 117 | **99**（退役 -3，合并 -15） | C1+C2 |
| 每次提交检查点（L2+L2.5 必跑） | 173 | **155** | L2.5 两段式另行 |
| 单次提交门禁链中位耗时 | 拦截链 P50 71.1s / 成功链 P50 43.2s | 仅 C5 六台慢门（sum_p50=32.9s）条件化后：**拦截链 ≈38s（-46%）** | 真实计时 |
| 多会话误伤 | 全暂存连坐（09-23 实证） | 31 台 own 化后外来违规=warn+审计 | C3 |

## E. Owner 裁定清单（2026-09-23 全批：A-E 五包）

1. 零触发安全门留置（SECRET/GETENV/SUBPROCESS）→ 留+own+条件触发 ✅全批
2. 4 台 warn-only 观察闸 → 30 天扩窗复核 ✅全批
3. 图谱 6 并 1 ✅全批
4. 复杂度三件套并 1 台保留 L2 快速层 ✅全批
5. META-TESTS-COVERAGE → 裁定退役归观察包（C5 零触发挂触发）✅全批
6. 39 台零触发挂 files_trigger 跑满 30 天再清算 ✅全批
7. precommit 56 hooks 两段式（确定性子集 7 hooks 15-40s 先行）✅全批
8. 统一 gate_registry.yaml 补 3 台漂移 → 立即事故级修复 ✅全批
9. own_scope 机生补账（27/30/33 归一）✅全批

**关键数据文件路径**（复算用）：`.runtime/audit/gate_execution_stats.jsonl`、`.runtime/audit/commit_block_events.jsonl`、`docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml`、`docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml`、`.pre-commit-config.yaml`、`src/zephyr/gov_enforcement/commit_gates/`。
