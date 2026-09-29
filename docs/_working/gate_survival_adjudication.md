---
created: 2026-09-29
ttl: task_bound
title: 提交链路全组件存留裁定与提速方案（挖矿交接版）
session: st-gate-rationalize-20260929
deliverable_to: 施工对话（ 门禁/提交链提速施工班）
---

# 提交链路全组件存留裁定与提速方案（挖矿交接版）

> **本文是什么**：对提交链路上**每一个吃时间的组件**（183 条门禁注册 + 69 个 hook + ~20 个非门禁组件）逐台给出「功能一句话 + 实测数字 + 存留裁定」。本会话只调查不施工；施工按 §8 包执行，Owner 门位项见 §9。
>
> **数据窗口与真源**：定量数据 = `.runtime/audit/gate_execution_stats.jsonl`（9/15–9/29，2185 条门禁链）+ `.runtime/audit/commit_block_events.jsonl`（9/13 起）+ `.runtime/audit/precommit_channel_stats.jsonl`（9/24 起，141 次）；语义证据 = 三册（`docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml` 183 条 / `catalogs/in_process_gate_registry.yaml` 名册 104 条 / `.pre-commit-config.yaml` 69 条）+ 逐台源码 docstring。分析脚本（只读，可复跑）：`.runtime/tmp/commit_speed_audit/{analyze,gate_stats}.py`（tmp 区 24h TTL，方法见 §10 可重建）。
>
> **裁定代号**：【保留】【优化：处方】【执行退役】=判据由宿主/对侧承载、停掉双跑，非净删【退役候选】=Owner 门位（§5.2 注册表净删）【账实对齐】【已合并·锚保留】。

---

## §1 执行摘要

**底数**：统一册 183 条 = 99 台 in-process L2 + 56 hook + 28 manual（其中 27 已 deprecated）；运行时名册 104 条、4 台 enabled=false、实跑 n_specs=100；hook 配置 69 条，实跑 pre-commit 阶段 57 台。窗口内 in-process 链累计 147,412s（2185 链，含 9/21–25 恶化期）；hook 通道 p50 44.3s / p90 157s / max 1784s。

**六个结构性发现（此前审计未点透的）**：

1. **DOC-HEADER-SUITE 与 7 个子台每笔双跑**（簇1）：聚合门已顺序调用全部 7 个子判据，但 7 个子台仍在名册单独 enabled 各跑一遍。**名册置 enabled=false 即回收 ~2–5s+/笔，判据零变化**。
2. **6 对同脚本双层门**：ID-UNIQUENESS / TTL-METADATA / ENCODING-SAFETY / DIRECTORY-CONTRACT / PURE-SHIM / BLUEPRINT-NODE-ID-HARDCODE 的 L1 是 subprocess 调 hook 同一脚本的 thin wrapper。9/19 起 gateway 通道本就全量跑 hook 套件（`gate_precommit_run` flag），这 6 对在 gateway 路径=纯双跑。裸 commit 面已被 gate-commit-gw（always_run 硬阻断）整体封死，「hook 兜裸面」论据不成立。**通道内 SKIP 5 个 hook twin 即单层化**。
3. **hook 通道仍在全局锁内 + 绿件双跑**：通道执行点在 `_commit_locked` step 5.5（git_commit_gateway.py:3439）；两段式 Phase-A 快段子集 + Phase-B 全通道，绿件多付一次快段调用（代码注释自认）。hook p50 44.3s 中快段占 38.4s（87%）——**大头不是慢尾 20 台，是快段 36 台的数量×单价**。
4. **簇2 系统性重复扫描**：~25–30 台门禁各自独立跑 `git diff --cached --name-only` + 逐文件 added 行 + `ast.parse`，无跨门共享（`_diff_helpers.py:280-341`）。S1 own-tree 视图（7.1× 读面收益已验收）与 preflight 内容哈希缓存**都已建成但 flag 出厂 OFF**。
5. **每笔提交的固定杂税**（非门禁）：integrity 基线刷新 mean 46.1s/落地件（snapshot flag 未翻转）、reference-transaction 守卫 1.25s/落地件、post-commit 每笔 spawn Qoder Electron（零遥测）、bottleneck 横幅整读 jsonl ×2、tracked 快照 4 个 git 子进程、DEPGRAPH-FRESHNESS 整读依赖图 JSON 只为取一个时间戳。
6. **账实不符一批**：4 台名册 disabled 但统一册 active（GATE-VOCAB / PERMANENT-SYSTEM-TRIGGER / CAPABILITY-OVERLAP / ALGO-FLOW-LINK）；6 台 MANUAL_GATES 墓碑与运行时 active 并存；3 个实跑 hook 从未登记进统一册；2 个 hook 触发面已死、1 个模块路径坏死、1 个自认 SKIP 骨架。

**预期收益排序（P0 全落≈单笔省 50–90s，落地件另省 ~47s）**：hook 单趟化+通道 SKIP（-40s 量级）＞ DOC-HEADER 子台执行退役（-2–5s+）＞ integrity snapshot 旗（-40s/落地件）＞ ref-transaction 收窄（-1.25s/落地件）＞ S1/缓存 flag 开启（簇2 面上 7.1×）。

---

## §2 现状底数（三册对账）

| 册 | 条数 | 实况 |
|---|---|---|
| gate_registry.yaml（统一册，机生，PS-REG-014） | 183（active 156 / deprecated 27） | 生成器三源合并：pre-commit + commit_gates/*.py + MANUAL_GATES；**不驱动运行时，只读派生** |
| in_process_gate_registry.yaml（运行时名册） | 104（enabled 100） | 由 gate_auto_registrar 动态 import 注册；enabled=false×4：CAPABILITY-OVERLAP(:85)、GATE-VOCAB(:203)、PERMANENT-TRIGGER(:241)、ALGO-FLOW-LINK(:348) |
| .pre-commit-config.yaml | 69 条 | 实跑 pre-commit 阶段 57 + manual 8 + post-commit 3 + commit-msg 1；全 `repo: local` + `language: system`=每台独立 python 子进程串行 |
| 未登记 | 3 hook | gate-detect-git-dangerous / gate-detect-shell-dangerous / gate-detect-permanent-deletion 实跑但统一册无条目 |
| 口径债 | 6 条 | 注册表把 manual 阶段 6 台（gate-arch/naming-audit/frontmatter-audit/bp-place/dedup/drift）计为 enforcement_channel=pre-commit，「56」对不齐任何单一执行面（实跑 57） |

---

## §3 裁定框架

宪法 §4.2 内收判据：同真源可派生→必并｜零触发零消费→退役｜同域重复簇→收敛唯一｜跨域不同对象→不并。叠加：

- **判据层 vs 执行层分离**：本方案绝大多数收益在执行层（停双跑/共享扫描/条件化/出锁），**不删任何检查判据**——判据退役一律列【退役候选】走 Owner 门位，与 9/24 战役「不删门禁，只合并/降档/diff 化」红线一致。
- **阻断实证即价值**：窗口内阻断数（blocks）是该门「真拦到过东西」的硬证据；0 阻断×高成本×warn-only 是优化/退役的最强组合证据。
- 双通道（L1 in-process + L2 hook）**保留双轨登记**（防 --no-verify 有意绕过仍有一层），但同一通道内不双跑。

---

## §4 in-process L2 门禁逐台裁定（99 台 + 名册 4 disabled + manual 28）

实测列：`累计s`=窗口累计耗时；`阻断`=commit_block_events 记录的拦截次数。窗口跨 9/23–25 合并批，deprecated 行数字为合并前历史。

### §4.1 大头门（累计 >800s，18 台）——逐台详裁

| gate | 功能一句话 | 累计s | 阻断 | 裁定 |
|---|---|---|---|---|
| CREATE-GUARD | 新建 .py/非rules .yaml 须有 creation_token（p50 219ms 已被缓存修好，p90 仍 55s=缓存 miss 尾） | 20868 | 100 | 【保留】+【优化】跨进程持久缓存预热/注册表分片，砍 p90 尾；阻断第 1 名=价值实证 |
| BLUEPRINT-HEADER | [A_module]格式+BP↔AM双拼写（聚合 2 子判据） | 7659 | 5 | 【执行退役】standalone 条目由 DOC-HEADER-SUITE 承载；宿主内 2 遍同源扫描并 1 遍 |
| CAPABILITY-OVERLAP | CapabilityLookup 提示+CloneGuard 语义克隆 | 7619 | 40 | 【账实对齐】名册已 disabled（运行时零执法），统一册改 disabled；CloneGuard 写时检查（check_before_write）仍在，有补偿。复启用与否 Owner 裁 |
| REGISTRY-MASS-DELETION | 登记表净删/条目蒸发阻断 | 6420 | 13 | 【保留】（净删防护，宪法§5.2 底座）+【优化】簇4 共享 parse；单次 19.5s 尖峰治本 |
| GIT-CALL-BUDGET | git 调用预算 warn（为统计自己再跑一遍 git） | 5594 | 0 | 【优化】改读 check_all 已有 _stat_ms 记账，删自扫 git；0 阻断 warn-only |
| CH-BATCH-SIZE | CH 批量写入防回退 | 5586 | 11 | 【保留】+【优化】簇2 共享 diff 视图（S1/preflight flag） |
| CH-VERSION-COL | CH version 列语义误用 | 5574 | 0 | 【保留】+【优化】已触发式（454 skip）；进一步收窄触发面 |
| RECONCILER-HEALTH | reconciler 健康度 | 5057 | 0 | 【优化】改读健康快照缓存，不做每笔 DB 查询；0 阻断 |
| BLUEPRINT-FORMAT | [BLUEPRINT] module_id 格式 | 4530 | 100 | 【执行退役】standalone 由 SUITE 承载（阻断数随宿主延续） |
| MUTABLE-CONST-WITHOUT-FINAL | 可变常量缺 Final | 4500 | 79 | 【保留】（阻断第 3）+【优化】簇2 |
| GATE-ERRCODE-CONSISTENCY | error_code 注册表↔代码对账 | 4305 | 23 | 【保留】+【优化】p50 5.5s 全仓唯一扫描台收窄；hook twin 改 baseline-aware（存量连坐缺陷） |
| GATE-DOMAIN-FK | [DOMAIN] 头域外键校验 | 4123 | 1 | 【保留】+【优化】簇2/4；1 阻断 4123s 性价比低，触发面已收窄再观察 |
| SSOT-REDEFINITION | SSoT 符号重复定义 | 3288 | 48 | 【保留】+【优化】簇4 共享 parse |
| NO-SECRET-HARDCODE | 密钥硬编码 | 3101 | 0 | 【保留】（安全红线）+【优化】已触发式（510 skip） |
| GATE-PANORAMA-ALIGNMENT | 三图对齐（已并入 MAP-ALIGNMENT） | 2489 | 0 | 【已合并·锚保留】 |
| COMPLEXITY-GUARD | 高复杂度+GodClass+长参数三合一 | 2366 | 34 | 【保留】+【优化】p90 18.4s 尾：AST 结果缓存 |
| NO-IMPORT-SIDE-EFFECT | 模块级副作用 | 2205 | 27 | 【保留】+【优化】簇2 |
| CONSUMERS-ACCURACY | CONSUMERS 字段准确性 warn | 2199 | 0 | 【优化】簇4 共享 parse；warn-only 0 阻断，降频到触发式 |

### §4.2 中尾部 active 门（累计 <2000s，按簇批量裁定）

**簇2 成员（共享 git diff+AST 重复扫描，统一处方=开 S1 own-tree 视图 + preflight 缓存 flag，一次施工全体受益）**：

| gate | 功能 | 累计s | 阻断 | 裁定 |
|---|---|---|---|---|
| ARCH-REFERENCE | #ARCH 悬空引用（已并入 REFERENCE-INTEGRITY） | 1993 | 12 | 【已合并·锚保留】 |
| DEPGRAPH-ENFORCEMENT | planned流转/新文件登记/改名同步/写路径 四合一 | 1484 | 6 | 【保留】+【优化】内部 4 子扫描各自跑 git diff → 并 1 遍；DB 连接合 1 |
| BLUEPRINT-AMODULE-CROSS-CHECK | BP↔AM 双拼写（墓碑） | 1441 | 1 | 【已合并·锚保留】 |
| DEPGRAPH-WRITE-PATH | 写权限白名单（墓碑） | 1434 | 1 | 【已合并·锚保留】 |
| BLUEPRINT-AMODULE-CONSISTENCY | [A_module] 格式（墓碑） | 1402 | 0 | 【已合并·锚保留】 |
| GATE-BATTLE-MAP-ALIGNMENT | 作战地图（墓碑） | 1397 | 1 | 【已合并·锚保留】 |
| FILE-PLACEMENT-TTL | ttl↔放置区一致 | 1376 | 14 | 【执行退役】→ SUITE |
| FILE-COPY | 新增 .py 克隆检测 | 1322 | 7 | 【保留】（RULE-CLONEGUARD 底座） |
| RELATIVE-PATH-LITERAL | 相对路径字面量 | 1291 | 0 | 【保留】+簇2 处方 |
| TRANSLATION-COVERAGE | 新 .py 大白话简介覆盖 | 1290 | 24 | 【保留】 |
| IMPORT-INTEGRITY | 悬空 import | 1261 | 13 | 【保留】+簇2 |
| NO-DOMAIN-NAME-ZH-DIRECT-ACCESS | DOMAIN_NAME_ZH 直访 | 1260 | 0 | 【保留】+簇2 |
| REGISTRY-YAML-PARSE | 热注册表 parse+重复根键 | 1221 | 5 | 【保留】+【优化】簇4（cap registry 一次 parse 多路用） |
| CH-FINAL-GATE | ch_writer.query() 直调阻断 | 1101 | 4 | 【保留】+簇2 |
| TABLE-NAME-REGISTRY | 表名硬编码绕真源 | 1093 | 23 | 【保留】+簇2/4 |
| REFERENCE-INTEGRITY | #ARCH/#裁定/AGENTS§ 悬空引用三合一 | 1043 | 8 | 【保留】 |
| DECISION-MAP | 决策图（墓碑） | 932 | 5 | 【已合并·锚保留】 |
| MODULE-ID-CONSISTENCY | module_id 三轨一致+跨文件唯一 | 926 | 6 | 【执行退役】→ SUITE +【优化】git grep 全仓改 staged 面 |
| DOC-HEADER-SUITE | 文档头七判据聚合门（簇1 宿主） | 891 | 3 | 【保留】（承载 7 子台后单趟） |
| TAG-VOCAB | 标签词表一致 | 863 | 0 | 【保留】+簇4 |
| BLOOD-FLESH | 图书馆藏书血肉一致 | 820 | 0 | 【保留】+簇4 |
| MSG-STYLE | 错误消息风格 | 806 | 2 | 【保留】+簇2 |
| NO-LONG-PARAM-LIST | 长参数（墓碑） | 955 | 37 | 【已合并·锚保留】 |
| TTL-METADATA | ttl/doc_type 元数据 | 2105 | 35 | 【执行退役】→ SUITE；hook twin（gate-frontmatter）通道 SKIP |
| ALGO-NOTE-SYNC | 算法锚与简介同步 | 619 | 55 | 【保留】 |
| ZEPHYR-ENV-DIRECT-ACCESS | ZEPHYR_ENV 直访 | 686 | 0 | 【保留】+簇2 |
| NO-BARE-GETENV | 裸 getenv 读密钥 | 674 | 0 | 【保留】+簇2 |
| RULE-FOUR-WAY-ALIGN | 规则四方对齐 | 650 | 0 | 【保留】（触发式） |
| TEST-SOURCE-CONSISTENCY | 测试-源码符号一致 | 627 | 15 | 【保留】+簇2 |
| ALGO-FLOW-LINK | ALGO_FLOW 锚链接 | 579 | 29 | 【账实对齐】名册 disabled 但统一册 active 且历史阻断 29——与 hook gate-algo-flow-marker（管标记存在性）分工不同。建议：要么复启用、要么确认 hook 层接管后统一册改 disabled。Owner 裁 |
| MAP-ALIGNMENT | 六图对齐聚合门 | 566 | 3 | 【保留】 |
| FUNCTION-DUP | 重复函数实现 | 530 | 18 | 【保留】 |
| NO-BARE-SQL | 裸 SQL 字面量 | 516 | 30 | 【保留】+簇2 |
| UNSAFE-DICT-SPREAD | `**data` 展开 warn | 492 | 0 | 【保留】（触发式）+簇2 |
| ORPHAN-MODULE | 孤儿模块 | 486 | 19 | 【保留】+与 GATE-17 双通道登记注记 |
| DATETIME-NOW-FORBIDDEN | datetime.now 禁令 | 448 | 7 | 【保留】（宪法§10 RULE-SCHEMA-TZ 底座）+簇2 |
| OPEN-WITHOUT-WITH | open 不在 with | 445 | 1 | 【保留】+簇2 |
| RULING-REFERENCE | 裁定悬空引用（墓碑） | 445 | 6 | 【已合并·锚保留】 |
| PURE-SHIM | 纯 re-export shim | 433 | 0 | 【保留】（L1 own-scope 归因优）+hook twin 通道 SKIP |
| ASYNCIO-RUN-IN-CONTEXT | 异步上下文误用 | 415 | 0 | 【保留】+簇2 |
| TEST-RESIDUE-SSOT | 测试残留前缀 | 363 | 0 | 【保留】+簇2 |
| FRONTEND-MAP | 前端图（墓碑） | 312 | 13 | 【已合并·锚保留】 |
| DIRECTORY-CONTRACT | 目录契约 DCR-001~007 | 278 | 22 | 【保留】（L1 消息感知版）+hook twin 通道 SKIP |
| PURE-ASSERTION | 纯陈述原则 | 272 | 5 | 【保留】+簇2 |
| MSG-EXPOSURE | 错误消息泄敏 | 261 | 6 | 【保留】+簇2 |
| PERMANENT-SYSTEM-TRIGGER | 时间触发/永久manual无订阅 二合一 | 253 | 9 | 【账实对齐】名册 disabled；永久系统四要素是宪法§9.3 红线，禁令不应无执法——建议复启用或明示由哪层承接，Owner 裁 |
| UNDEFINED-NAME | F821 未定义符号 | 252 | 6 | 【保留】+簇2；⊃SCRIPTS-IMPORT-INTEGRITY |
| BLUEPRINT-NODE-ID-HARDCODE | node_id/edge_id 硬编码 | 241 | 0 | 【保留】+hook twin（gate-doc-node-id）通道 SKIP |
| DOC-REF-BROKEN | 新 .md 相对链接断裂 | 207 | 0 | 【执行退役】→ SUITE |
| VOCAB-HARDCODE | 词表硬编码（墓碑） | 203 | 16 | 【已合并·锚保留】 |
| NOQA-VALIDATION | 自定义 noqa 合规 | 167 | 8 | 【保留】+簇2 |
| EXEMPT-ZONE-FM | 豁免区 frontmatter | 166 | 14 | 【执行退役】→ SUITE |
| ENCODING-SAFETY | 编码安全（BOM/mojibake） | 151 | 3 | 【保留】（L1 版）+hook twin（gate-encoding-safety）通道 SKIP |
| EMPTY-HANDLER | 空 handler | 149 | 0 | 【保留】+簇2 |
| FRONTEND-TRUTH-SOURCE | 前端真源接通 | 144 | 0 | 【保留】 |
| DERIVED-FILE-DELETION-PROTECTION | 派生文件删除保护 | 143 | 0 | 【保留】 |
| NO-HIGH-COMPLEXITY | 高复杂度（墓碑） | 143 | 25 | 【已合并·锚保留】 |
| REGISTRY-CODE-ANCHOR | 业务注册表代码锚 | 134 | 6 | 【保留】 |
| DEPGRAPH-FRESHNESS | depgraph 新鲜度 | 132 | 0 | 【优化】现在整读+json.loads 全项目依赖图只为取 saved_at → 流式只读 _meta（几十行改动） |
| MANUAL-ONLY-PERMANENT / PERM-TRIGGER | 墓碑 | 131/129 | 26/21 | 【已合并·锚保留】 |
| BARE-SUBPROCESS | 裸 subprocess | 123 | 2 | 【保留】+簇2 |
| SNAPSHOT-DRIFT | 违规快照漂移 | 123 | 0 | 【保留】 |
| CAP-CONSISTENCY | Provider 路由-meta 一致 | 119 | 4 | 【保留】+簇4 |
| DERIVATION-ANNOTATION | 派生声明真实性 | 109 | 0 | 【保留】 |
| SECRET-REGISTRY-CONSISTENCY | .env.example↔secret_registry 对齐 | 106 | 3 | 【保留】 |
| MCP-VERSION-FIELD | MCP version 字段 | 101 | 0 | 【保留】 |
| NO-GOD-CLASS | GodClass（墓碑） | 101 | 0 | 【已合并·锚保留】 |
| STATE-VOCAB-REGISTRY | 状态词表一致 | 99 | 0 | 【保留】+簇4 |
| SCRIPTS-IMPORT-INTEGRITY | scripts 用 _shared.constants 未 import | 86 | 0 | 【退役候选】违规集 ⊂ UNDEFINED-NAME（F821 覆盖同域）；残余价值=高精度报错文案。并入 UNDEFINED-NAME 报错分支或转 warn。Owner 裁 |
| STASH-ACCUMULATION | stash 堆积阈值 | 78 | 0 | 【保留】（防 stash 吞写事故复发） |
| VOCAB-CHAIN | SSoT 词表路径（墓碑） | 76 | 10 | 【已合并·锚保留】 |
| NEW-FILE-DEPGRAPH-ENFORCEMENT | 新文件 depgraph（墓碑） | 75 | 15 | 【已合并·锚保留】 |
| BUSINESS-REGISTRY | 业务资产库入库 | 71 | 2 | 【保留】 |
| RENAME-DEPGRAPH-SYNC | 改名 depgraph 同步（墓碑） | 58 | 14 | 【已合并·锚保留】（宪法§9.10 判据由 DEPGRAPH-ENFORCEMENT 承载） |
| HOT-FILE-BASE-FRESHNESS | 热文件 base 新鲜度 | 57 | 48 | 【保留】（防 CAS 拉锯） |
| FMS-HYGIENE | FMS 引用卫生 | 53 | 0 | 【保留】 |
| DANGLING-REFERENCE | AGENTS§ 悬空（墓碑） | 42 | 14 | 【已合并·锚保留】 |
| NO-UPWARD-IMPORT | shared 向上依赖 | 41 | 0 | 【保留】+簇2 |
| COMMIT-SCOPE | 提交边界域一致 | 36 | 35 | 【保留】 |
| RULE-EXECUTION-PAIRING | 规则-执行配对 | 21 | 0 | 【保留】（触发式） |
| PROTECTED-PATHS | 受保护路径（L1 消息感知+审批三通道） | 17 | 13 | 【保留】 |
| HELD-OVERLAP | 搭便车冲突 | 15 | 62 | 【保留】 |
| CLAIM-REQUIRED | claim 前置 | 13 | 58 | 【保留】 |
| RESOURCE-SCHEDULE | 排班冲突 | 12 | 2 | 【保留】（触发式） |
| LIBRARY-COVERAGE / DATA-TASK-COMPLETENESS / ISSUE-RESOLVED-INTEGRITY | 已退役三台 | 7/3/0 | 0 | 【已合并·锚保留】（9/23 审计裁定退役，维持） |
| RULING-COMMIT-VERIFIED | 「已完成」commit hash 真实性 | 6 | 1 | 【保留】 |
| SCHEMA-FILE-EXISTS | schema_file 悬空 | 4 | 0 | 【保留】（触发式）+簇4 |
| FOLDER-CAPACITY-HARD-LIMIT | 目录容量硬上限 | 3 | 18 | 【保留】 |
| SPLIT-COORDINATION | 拆分×编辑协议 | 2 | 3 | 【保留】 |
| R5-DIGIT-SUFFIX | R5 数字后缀目录 | 2 | 0 | 【保留】 |
| ID-UNIQUENESS | hook id 唯一性（=hook 同脚本 thin wrapper） | 1 | 0 | 【保留】L1 +hook twin（gate-id-uniq）通道 SKIP |
| CAPABILITY-LOOKUP-REQUIRED | 能力反查强制 | 1 | 13 | 【保留】 |
| INDUSTRY-CHAIN-MAP / FACTORY-MAP | 墓碑 | 1/0 | 0 | 【已合并·锚保留】 |
| GATE-PRECOMMIT-OFFLINE | pre-commit 配置离线可跑 | 1 | 0 | 【保留】（触发式） |
| SESSION-REQUIRED | session 注册强制 | 0 | 17 | 【保留】 |
| RECONCILER-FILE-OPS | reconciler 文件操作 | 0 | 0 | 【保留】 |
| FORGED-GW-MARKER | [GW:] 伪造检测 | 0 | 6 | 【保留】（宪法§9.8 底座） |
| META-TESTS-COVERAGE | commit_gates 改动须带测试 | 0 | 0 | 【保留】 |
| WORKTREE-REQUIRED | worktree 隔离强制 | 0 | 83 | 【保留】（宪法 RULE-WORKTREE 底座） |
| COMMIT-CRITICAL-SECTION-LOCK | 全局锁机制实名登记（非钩子） | 0 | 0 | 【保留】（登记项） |
| GATE-VOCAB | 词表硬编码+SSoT路径 二合一 | — | — | 【账实对齐】名册 disabled 但 hook gate-vocab（--ci）仍执法同域词表检查——执法未断，L1 复启用与否 Owner 裁；统一册 active 改一致 |
| ALGO-FLOW-LINK | （已列） | | | 见 §4.2 |
| CAPABILITY-OVERLAP | （已列 §4.1） | | | |

### §4.3 manual 28 台

24+3 台为 deprecated 墓碑（§4.2 已逐台标注【已合并·锚保留】）；BLUEPRINT-FORMAT 墓碑与运行时 enabled 单跑并存的矛盾随 §4.1 执行退役消除；COMMIT-CRITICAL-SECTION-LOCK 唯一 active（登记项，保留）。**统一册生成器 seen_gate_ids 去重导致 6 台墓碑落册失败**（generate_gate_registry.py:143-158）→ 施工时修生成器让墓碑语义正确落册（登记债，§7）。

---

## §5 hook 通道逐台裁定（69 条）

### §5.1 通道结构性裁定（先于逐台）

1. **通道出锁**：通道执行点 `_commit_locked` step 5.5（git_commit_gateway.py:3439）在全局锁内——p50 44.3s 的通道把所有人挡在门外。处方=通道移到锁外+锁内复核 staged 指纹（9/24 方案 B1，仍未落）。
2. **单趟化**：Phase-A 快段子集+Phase-B 全通道两段式，绿件双付快段（gateway:3597-3635 注释自认）。处方=单趟全通道（own-scope 临时索引已解决连坐，Phase-A 存在理由消失）或 Phase-B 跳过 Phase-A 已过台。
3. **通道 SKIP 扩容**：`_PRECOMMIT_CHANNEL_SKIP_HOOKS`（:432）现有 3 台，追加 5 台 hook twin：gate-id-uniq / gate-frontmatter / gate-encoding-safety / gate-directory-contract / gate-doc-node-id（同脚本 L1 已跑且带 own/foreign 归因）。gate-ssot-code 第三段 pure_shim 同理但它是三脚本链，需链内跳过或整链保持。
4. **慢尾 20 台逐台处方**见下表；快段 36 台靠单趟化+SKIP 吃到收益，不逐台动。

### §5.2 pre-commit 阶段 57 台

| hook | 功能 | 模式 | 裁定 |
|---|---|---|---|
| gate-test | pytest --collect-only 全树 3720 测试文件+结构检查 | 硬 | 【优化】P0：改 staged 测试文件收集（判据保留：测试可导入性）；全树收集移 CI/夜检。9/24 R1 点名最大单项 |
| gate-21-manifest-drift | 所有生成器 --check 全量漂移 | 硬 | 【优化】触发式：仅 manifest/catalogs/generators 本身变更时全量，否则跳过 |
| gate-zr-zero-residue | 零残留 ZR-001~009 | 硬 | 【优化】全仓 scan() → staged 面 |
| gate-ssot-code | SSoT 三合一（pure_shim 段全量扫 src） | 硬 | 【优化】pure_shim 段 own-scope 化；与 L1 PURE-SHIM 单层化（§5.1.3） |
| gate-triple-align | 蓝图↔代码↔依赖图对齐 | 硬 | 【优化】触发式（blueprint/depgraph 变更才跑全图） |
| gate-schema-truth | DDL 真源 vs ClickHouse 对账 101 表 | 硬 | 【优化】CH 不可达已 exit 0；加结果缓存 TTL（schema 对账无需每笔联网） |
| gate-script-q | 脚本八维质量+_shared 重定义 | 硬 | 【优化】--scripts-dir 全扫 → staged 面 |
| gate-c2 | 契约漂移+物理路径+schema 健康 | 硬 | 【优化】自扫 → 触发式 |
| gate-mcp-contract-consistency | tool_contracts↔register_tool | 硬 | 【优化】自扫 → 触发式（integration/mcp 变更时） |
| gate-16-architecture-compliance | VR-008/009/011 架构合规 | 硬 | 【优化】docs/01 自扫 → staged 面 |
| gate-12-blueprint-provenance | 蓝图 Provenance 三件套 | 硬 | 【优化】目标目录自扫 → staged 面 |
| gate-reg-bl | 注册审计基线差分 | 硬 | 【保留】（已 incremental+baseline-aware） |
| gate-errcode-consistency | error_code 双向对账 | 硬 | 【优化】hook 版跑整 pytest 含存量违规（连坐缺陷）→ baseline-aware（L1 已是） |
| gate-vocab | 词表硬编码+派生一致 | 硬 | 【保留】（L1 GATE-VOCAB disabled 后它是唯一词表执法层；复启用 L1 则二选一） |
| gate-17-orphan-py | 根目录孤儿 .py | 硬 | 【保留】+【优化】曾误连坐 vendor/_working（排除目录复核） |
| gate-naming | 命名增量守门 | 硬 | 【保留】 |
| gate-algo-flow-marker | ALGO_FLOW 标记存在性 | 硬 | 【保留】（与 L1 ALGO-FLOW-LINK 互补） |
| gate-pytest-config-drift | pyproject↔py.ini 对齐 | 硬 | 【保留】（触发式 2 文件） |
| gate-rules-integrity | 规则文件 golden hash | 硬 | 【保留】（C 层兜底，A 层在 gateway 内） |
| check-merge-conflict-marker | 冲突标记 | 硬 | 【保留】 |
| detect-private-key-local | 私钥检测 | 硬 | 【保留】 |
| gate-protected-paths | 受保护路径（Layer2） | 硬 | 【保留】登记（通道已 SKIP 防误杀审批写入；裸面由 gate-commit-gw 覆盖）→【退役候选】随 gate-commit-gw 保留决策一并裁 |
| gate-worktree-required | worktree 软门禁 Layer2 | warn→硬 | 【保留】登记（同上，通道已 SKIP） |
| gate-commit-gw | 裸 commit 恒阻断 | 硬 | 【保留】（它是「裸面已被封死」论据的承重墙） |
| ruff / ruff-format | lint+format | 硬 | 【保留】 |
| gate-src-no-data / gate-no-tests-unit / gate-no-commit-derived | 路径禁令三条 | 硬 | 【保留】 |
| gate-directory-contract | 目录契约 Layer2 | 硬 | 通道 SKIP（§5.1.3），裸面登记保留 |
| gate-encoding-safety | 编码安全 Layer2 | 硬 | 通道 SKIP，裸面登记保留 |
| gate-frontmatter | frontmatter 增量 | 硬 | 通道 SKIP（L1 SUITE 承载），裸面登记保留 |
| gate-id-uniq | hook id 唯一 | 硬 | 通道 SKIP（配置变更时 L1 ID-UNIQUENESS 承载），裸面登记保留 |
| gate-doc-node-id | node_id 硬编码 Layer2 | 硬 | 通道 SKIP（L1 承载），裸面登记保留 |
| gate-symbol-convention | symbol 列约定 lint | 硬 | 【保留】 |
| gate-return-contract | TypedDict 禁键访问 | 硬 | 【保留】 |
| gate-worktree-ops-telemetry | 擦除操作遥测 | 硬/warn | 【保留】 |
| gate-adm-manifest-admission | Manifest 准入 | 硬 | 【保留】 |
| gate-codegen-idempotent | 生成器幂等 | 硬 | 【保留】（触发式） |
| gate-canonical-yaml-drift | canonical YAML 5 断言 | 硬 | 【保留】（触发式） |
| gate-debt-bridge | 5.96 维度架构债 | 硬 | 【保留】（--staged 已亚秒） |
| gate-any-abuse | 裸 Any 滥用 | 硬 | 【保留】（--staged） |
| gate-20-llm-security-gateway | 裸调 LLM AST 扫描 | 硬 | 【保留】（宪法§9.2 底座，--staged） |
| gate-generator-no-realtime-time | 生成器禁 datetime.now | 硬 | 【保留】（触发面窄） |
| gate-vms-ssot | VMS 真源双检测 | 硬 | 【优化】governance 分支触发面已死 → 收缩为 integration 单分支 |
| gate-detect-git-dangerous / shell-dangerous / permanent-deletion | 危险命令/永久删文本检测 | 硬 | 【保留】+【账实对齐】补登记进统一册（实跑却无条目） |
| **gate-14-authority-registry** | 权限注册表自校验 | 硬 | 【退役候选】触发正则指向不存在的 .md（真身是下划线 .yaml），自注册以来零执行。修正则或退役，Owner 裁 |
| **gate-13-blueprint-overlap** | 蓝图草稿重叠 | 硬 | 【退役候选】触发目录 0 个 tracked 文件，永不触发 |
| **gate-drift-light-scan** | 行为漂移 LIGHT | warn | 【退役候选】entry 模块路径坏死（zephyr.behavioral_auditor 不存在）+warn-only 无人消费 |
| **gate-22-load-path-integrity** | AI 加载路径完整性 | warn | 【退役候选】自认 SKIP 骨架（config :28），零判定产出 |
| gate-algo-quality | 算法糊弄 6 类 pattern | warn | 【优化】全仓扫描观察期——核实 30 天转硬判据是否到期：到期转 --ci 或退役，不悬置 |
| gate-silent-degradation | 降级无日志 | warn | 【优化】观察期清障：转硬或退役，不悬置 |
| gate-nested-flat-prefix | 目录平铺容量 | warn | 【优化】同上（全扫 ROOTS 收窄 staged） |
| gate-module-lifecycle-transition | 生命周期枚举 | warn | 【优化】32 项存量未清——清存量后转硬或退役 |
| gate-node-label-quality | 节点简介质量 | warn | 【优化】触发目录仅剩 1 个 tracked .md，触达趋零：随域文档重建决策一并裁 |

### §5.3 manual / post-commit / commit-msg（12 条）

| hook | 功能 | 裁定 |
|---|---|---|
| commit-msg-conventional | Conventional Commits 校验 | 【保留】 |
| handoff-log-generate / handoff-log-post-commit | 交接日志 | 【保留】 |
| retire-tmp-artifacts-post-commit | tmp TTL 退役 | 【保留】 |
| gateway-post-commit-ritual | rules/contracts 批次重钉 | 【保留】 |
| gate-arch / gate-naming-audit / gate-frontmatter-audit / gate-bp-place / gate-dedup / gate-drift（manual 段 6 台+sync-audit） | 全仓审计类手动台 | 【保留】（manual 不占提交时间）+【账实对齐】统一册 channel 口径修正 |
| gate-arch（19 项检查五合一） | 架构门禁手动全检 | 【保留】 |

---

## §6 非门禁链路组件裁定（每笔提交都在付钱的）

| 组件 | 功能/现状 | 成本特征 | 裁定 |
|---|---|---|---|
| `_GlobalCommitLock` 锁范围 | 整条门禁链+pre-commit 通道+git commit+post-commit 钩链全在锁内（TRAE-079 防拆分设计） | 通道 p50 44.3s 全部排他 | 【优化】P1：通道出锁+锁内 staged 指纹复核；gate→stage→commit 原子性不受损（通道只是校验） |
| 锁等待盲轮询 | 0.1s 间隔 O_EXCL+整读锁文件 | 竞争时 10 次/s | 【优化】P2 指数退避 |
| integrity 基线刷新 | 每落地件同步跑 validate_rules_integrity --register | mean 46.1s/max 301s | 【优化】P0：翻转出厂 flag `ZEPHYR_INTEGRITY_BASELINE=snapshot`（按 HEAD 派生省 40-46s/件）——flag 翻转 Owner 门位 |
| reference-transaction guard | 任意 ref 事务审查 dev 前进 | 1.25s/次×每落地件 | 【优化】P1：收窄为仅 refs/heads/dev 前进时全检，其余早退 |
| post-commit YAML regen | diff+双读 generator_registry+TTL 锁+条件 spawn 再生 | 同步段 0.1-1s；扇出 11-131s | 【优化】P1：TTL 去重静默丢 75% 合格触发+在陈旧 worktree 干负收益活——改事件触发（§9.3 红线本来就要求 reconciler 事件化） |
| post-commit guard | 非 GW 提交检测：17 处 git/shell+全册 grep | 秒级候选 | 【保留】+【优化】P2 报告 grep 加缓存 |
| **post-commit Qoder tracker** | 每笔 spawn Electron/node（E:/Qoder…exe） | UNKNOWN（零遥测=缺陷本体） | 【退役候选】P1：每笔提交拉起 IDE 进程无观测无消费方——Owner 确认后移除或改 env 门控 |
| post-checkout 链 | lfs+guard+Qoder，每落地件 reset --hard 触发 | UNKNOWN | 【优化】随 Qoder 裁定一并处理 |
| pg_probe 前置探针 | TCP 5432 探测 | PG 离线时 1s/笔 | 【优化】P2：结果缓存 60s |
| bottleneck 横幅 | 整读 commit_block_events.jsonl 逐行 parse，×2/笔 | 随账本线性涨 | 【优化】P2：尾读 N 行/按 ts 二分 |
| tracked 区快照 | gate 链前后各 2 个 git diff 子进程取指纹 | 4 git/笔 | 【优化】P1：并 1 组复用 |
| `_snapshot_worktree_status` | 每笔成功跑全量 git status+append | 秒级（Windows） | 【优化】P2：异步化+jsonl 轮转（该册曾 449 万行） |
| SessionRegistry | 每次变更整表读+美化写+os.replace；claim/release 各 1-2 次 | O(会话×文件) 整表重写；与 30s 心跳互踩（WinError5 退避） | 【优化】P1：增量/分片写 |
| scripts/lock_files.py | 全局 Mutex+整表 RMW+fsync | 批量版已优化 | 【保留】 |
| claim 快照 | claim 1 写+release 1 删+adopt append | 小 | 【保留】 |
| safe_write_text CAS | 双读双哈希+回读复核+审计 append | 落在热文件写者头上 | 【保留】（宪法§1.13 底座） |
| 遥测写放大 | 每笔成功 append 5-10 个 jsonl，无 fsync 无轮转 | 单次小；账本无限涨拖慢整读者 | 【优化】P2：统一轮转/尺寸上限策略 |
| stats_lock 停世界 | 落地记账段持 4 工共享锁做全 pending 扫描+fsync 重写 | 144ms/次×完全串行（D1 实测） | 【优化】P1：D1 手术单已立档（commit_speedup_campaign），按单施工 |
| reconcile 扇出 auto-commit | 每笔成功 spawn ~40 reconciler+批量 auto-commit **重入全局锁** | 与前台提交互抢锁（放大环） | 【优化】P1：auto-commit 错峰/低优先级通道 |
| 主区收敛 `_converge_main_workspace` | 逐路径 blob 比对快进 | med 0s / max 1887s；~630s/件仍不可归因 | 【优化】P1：A2 装表续作（八相位分段已有）把 630s 归因坐实后定向治 |
| DEPGRAPH-FRESHNESS 扫描本体 | reconciler 异步重建，门只读缓存 | 门侧整读大 JSON | 【优化】P0：流式读 _meta（几行改动） |
| 队列 serializer | worktree 同步+预暂存 | 归入 630s UNKNOWN 段 | 随装表归因后裁 |

---

## §7 账实不符与登记债清单（施工时顺手清）

1. 4 台名册 disabled × 统一册 active：GATE-VOCAB / PERMANENT-SYSTEM-TRIGGER / CAPABILITY-OVERLAP / ALGO-FLOW-LINK（in_process_gate_registry.yaml:203/:241/:85/:348）。
2. 6 台 MANUAL_GATES 墓碑落册失败（生成器 seen_gate_ids 去重，generate_gate_registry.py:143-158）：TTL-METADATA/FILE-PLACEMENT-TTL/EXEMPT-ZONE-FM/DOC-REF-BROKEN/MODULE-ID-CONSISTENCY/BLUEPRINT-HEADER 的墓碑语义未落统一册。
3. BLUEPRINT-FORMAT 墓碑已落册但运行体仍在名册单跑（名册:366）——随 §4.1 执行退役消除。
4. 3 个实跑 hook 未登记：gate-detect-git-dangerous / gate-detect-shell-dangerous / gate-detect-permanent-deletion。
5. 注册表 enforcement_channel 口径：manual 6 台计成 pre-commit，56 对不齐实跑 57。
6. gate-14-authority-registry 的死正则（连字符 .md vs 真身下划线 .yaml）同时写进了统一册 :147。

---

## §8 施工包建议（按收益/风险排序；全部不动判据，只动执行结构）

**P0（半天量级，单笔提交立省 50–90s）**
1. 名册 7 子台 enabled=false（DOC-HEADER-SUITE 承载）——判据零变化。
2. `_PRECOMMIT_CHANNEL_SKIP_HOOKS` +5 hook twin（§5.1.3）。
3. hook 通道单趟化（拆 Phase-A/B 或 Phase-B 跳过已过台）。
4. flag 翻转（Owner）：ZEPHYR_INTEGRITY_BASELINE=snapshot → -40s/落地件。
5. DEPGRAPH-FRESHNESS 流式读 _meta。
6. reference-transaction guard 收窄 dev-forward。
7. gate-vms-ssot 触发面收缩；gate-14/13/drift-light/load-path 四死件呈 Owner 退役。

**P1（1–2 天）**
8. hook 通道出锁（staged 指纹回锁复核）。
9. S1 own-tree 视图 + gate_cache_preflight 缓存 flag 开启（簇2 一拖 ~25-30 台，读面 7.1× 已验收）。
10. gate-test 改 staged 收集。
11. 簇4 注册表 parse 共享（_capability_registry_io 扩展）。
12. DEPGRAPH-ENFORCEMENT 内部 4 扫并 1；BLUEPRINT-HEADER 内部 2 扫并 1。
13. GIT-CALL-BUDGET 改读 _stat_ms；RECONCILER-HEALTH 改读健康快照。
14. integrity/converge/落地八相位装表续作（630s UNKNOWN 归因）；stats_lock D1 手术。
15. SessionRegistry 增量写；post-commit regen 事件化修复 75% 丢弃+负收益工。
16. tracked 快照 4→1；Qoder tracker 呈 Owner 处置。
17. §7 登记债六项清理（含生成器墓碑修复）。

**P2（择机）**
18. 盲轮询退避、pg_probe 缓存、bottleneck 横幅尾读、遥测轮转策略、worktree_status_snapshots 轮转、reconcile auto-commit 错峰、SCRIPTS-IMPORT-INTEGRITY 并入 UNDEFINED-NAME（Owner）。

**验收**：每包落袋后跑 `.runtime/tmp/commit_speed_audit/gate_stats.py`（重建法 §10）对比逐台累计；单笔墙钟以 done 队列项 created→landed p50 为准（基线：9/26-27 为 94-148s，目标 <60s；单文件提交目标对齐战役 G1）。

---

## §9 Owner 门位清单（宪法 §5.2，本方案不代行）

> **批复留痕（2026-09-30）**：Owner 对本节五项口头批准（"全部批准，你现在就开工"）。按宪法 §9.11，口头指令不构成门禁豁免——净删/翻转的机械效力以本批 commit 留痕为凭。执行中两处按盘面在案证据修正，见 §11。

1. **注册表净删**：4 个死 hook（gate-14-authority-registry / gate-13-blueprint-overlap / gate-drift-light-scan / gate-22-load-path-integrity）+ warn-only 观察群清障（algo-quality/silent-degradation/nested-flat-prefix/module-lifecycle-transition/node-label-quality 五台转硬或退役）。
2. **flag 出厂翻转**：ZEPHYR_INTEGRITY_BASELINE=snapshot；S1 own-tree flag；gate_cache_preflight 两 flag。
3. **disabled 台去向**：GATE-VOCAB（hook 层在执法，L1 复启用或正式单层化）、PERMANENT-SYSTEM-TRIGGER（宪法红线不应无执法，建议复启用）、CAPABILITY-OVERLAP（CloneGuard 写时检查补偿，建议维持 disabled）、ALGO-FLOW-LINK（与 hook 互补，建议复启用或明示 hook 承接）。
4. **Qoder tracker 移除**（post-commit/post-checkout 每笔 spawn Electron）。
5. SCRIPTS-IMPORT-INTEGRITY 退役/并入。

## §10 与既有裁定的衔接（防重复施工）+ 复核工具

- 已执行勿重做：9/23 审计 117→99（退役 3 台/合并 15→7 簇）、C5 六慢门条件化、pkg8 文档头七台合一（聚合门已建，**缺的只是子台名册下线**）、S1 own-tree 验收（7.1×）、簇1 缓存（CREATE-GUARD p50 4.1→0.7s）、B4 排队 FIFO（倒挂 56%→0）、Rx-2 锁等待落账、A1/A2 precommit/落地装表。
- 本方案不推翻任何既有判据；与 15_gate_chain.md §E「6 对双层有意」的衔接：双层**登记**保留（防 --no-verify 语境），同通道**执行**单层化。
- 复核脚本（tmp 区 24h TTL，方法如下可 30 行重建）：读 gate_execution_stats.jsonl 聚 `ms/reused` 字段得逐台 runs/p50/p90/累计/触发跳过；读 commit_block_events.jsonl 聚 gate_id 得阻断数；读 precommit_channel_stats.jsonl 聚 total_ms/fast_subset_ms 得通道分布。注册表语义真源=三册+commit_gates/*.py docstring。

---

## §11 执行留痕（2026-09-30 第一波·st-gate-rationalize-20260929）

**已落（本会话直接施工，Owner 批复见 §9）**：

1. 名册 8 台 enabled=false（CAS safe_write）：7 子台执行退役（TTL-METADATA/FILE-PLACEMENT-TTL/EXEMPT-ZONE-FM/MODULE-ID-CONSISTENCY/DOC-REF-BROKEN/BLUEPRINT-FORMAT/BLUEPRINT-HEADER——安全实证=9/26 遥测 256 链中 SUITE 与 TTL 同起同落 160=160、SUITE 运行时 7 子台全数在内）+ SCRIPTS-IMPORT-INTEGRITY 退役（违规集⊂UNDEFINED-NAME）。
2. `_PRECOMMIT_CHANNEL_SKIP_HOOKS` +5 hook twin（gate-id-uniq/gate-frontmatter/gate-encoding-safety/gate-directory-contract/gate-doc-node-id）。
3. DEPGRAPH-FRESHNESS 流式读：头部 4KB 正则提取 saved_at，失配回落全量 parse；测试 +3（快路径不走 json.loads 红证/头损仍过/字段后置回落）共 30 绿。
4. .pre-commit-config.yaml：4 死 hook 退役（各留墓碑注释）+ gate-vms-ssot 触发面收缩 integration 单分支 + gate-node-label-quality 退役（触发面仅 1 tracked 文件）。64 hook id 唯一性过、yaml parse 过。
5. Qoder AI tracker 两处（post-commit/post-checkout）注释封存（非删除，可逆）。

**证据驱动的修正（原方案两处建议作废）**：

- §9.3「复启用 PERMANENT-SYSTEM-TRIGGER/ALGO-FLOW-LINK」**否决**——名册在案留痕均为 Owner 批准的临时禁用且恢复条件未满足（PERMANENT: "api_server 既有代码时间模式非本批引入"；ALGO-FLOW-LINK: "八卡在批内，worktree sync 后恢复"；GATE-VOCAB: "187 件落地后恢复"）。维持 disabled，账实对齐改由统一册侧承载（第二波）。
- §8.6「reference-transaction guard 收窄」**取消**——实读源码确认 M3/T6（st-commitspeed-tbl-20260924）已做非 dev 早退（:133-135）与零子进程根发现，本项已是现状，不动红队加固过的安全脚本。

**第二波待办（撞车/前置未满足，按占用方释放后进）**：

- flag 三翻转（config/flags.yaml 与 commit_queue_landing.py 被他会话占用中）。
- 生成器登记债全项（gate_registry.yaml 被占用；改生成器不重生成=manifest-drift 自爆，必须码+重生成同批）。
- 单趟化 Phase-A/B（9% 首过率下 Phase-A 对红件净省，需与出锁一起重设计，勿单独拆）。
- hook 通道出锁、S1/缓存 flag 开启、簇4 parse 共享、D1 手术、装表续作（P1 原案不变）。
- warn-only 观察群 4 台（algo-quality/silent-degradation/nested-flat-prefix/module-lifecycle-transition）转硬前置=存量清零，需清障专项，本批未动。
