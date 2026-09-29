---
created: 2026-09-30
ttl: task_bound
title: 提交链路全流通作战·E3 L2 门禁链（in-process）
session: st-gate-rationalize-20260929
---

# E3 L2 门禁链（in-process）挖矿册

> 环节定义：`_commit_locked` 锁内门禁链段——从 `GitCommitGateway.__init__` 经
> `gate_auto_registrar.auto_register_gates` 装载，到 `CommitGateRegistry.check_all`
> 按 priority 升序逐台执行的全过程（不含 pre-commit hook 通道=E4、不含锁外前置=E2）。
> **逐台裁定真源 = `docs/_working/gate_survival_adjudication.md` §4**（99 台 in-process
> + 4 disabled + manual 28 逐台裁定）——本册只放指针不复刻全表；与该册冲突处以该册为准，
> 但该册 §11 之后的 Owner 新令（裁定#431）已在册面生效，本文以盘面实态记录并注明。

## §0 自审闸三态

**【挖干】**（六向齐、逐件有锚；三处口径差异如实声明见下）。

- 逐台级功能/耗时/阻断数字**不在本册复刻**（真源=裁定册 §4.1/§4.2 逐台表，本会话已逐行核对结构一致）；
- 三处声明：①统一册条数种子说 183，盘面实测 **178**（9/30 晨退役 5 hook 后重生成，
  `gate_registry.yaml` generated_at=2026-09-29T21:14:42Z 即北京时间 9/30 05:14）；②种子说
  4 台 disabled，盘面实测该 4 台已 **enabled=true**（裁定#431 第①项 2026-09-30 翻回，
  ruling_registry.yaml:5989-5996；本条为裁定册 §11"维持 disabled"之后的 Owner 新令，
  名册行内注记自证"覆盖名册在案旧否决注记"）；③九簇之"297ms 三疑点已并"在盘面
  （docs/ 全树 grep）未定位到独立真源锚，按种子口径收录并标注待核。

## §1 组件全清单（11 件 + 九大重叠簇）

| # | 组件 | 实态（file:line） |
|---|------|------------------|
| 1 | 统一册 gate_registry.yaml | **178 条**=active 151（commit-gate 99 / pre-commit 51 / manual 1）+deprecated 27（全 manual 墓碑）；`generated_by: scripts/governance/generators/generate_gate_registry.py`、maintenance: auto；**不驱动运行时，只读派生**（PS-REG-014，裁定册 §2）。退役 5 hook（gate-14/13/drift-light/22/node-label）已不在册（逐 id 复核 False） |
| 2 | 运行时名册 in_process_gate_registry.yaml | `total_gates: 104`（:40）＝**enabled 96 + enabled:false 8**（yaml.safe_load 实数）；8 台=TTL-METADATA(:97-102)/FILE-PLACEMENT-TTL(:103-108)/EXEMPT-ZONE-FM(:229-234)/MODULE-ID-CONSISTENCY(:235-240)/DOC-REF-BROKEN(:265-270)/BLUEPRINT-FORMAT(:366-371)/BLUEPRINT-HEADER(:379-384) 七子台执行退役 + SCRIPTS-IMPORT-INTEGRITY(:411-417) 退役（违规集⊂UNDEFINED-NAME）——各条目行内注记"2026-09-30 Owner 批"指向裁定册 §4.1/4.2 |
| 3 | 4 台裁定#431 翻回条目 | CAPABILITY-OVERLAP(:85-90)/GATE-VOCAB(:203-208)/PERMANENT-SYSTEM-TRIGGER(:241-246)/ALGO-FLOW-LINK(:348-352) 均 `enabled: true`，行内注记"Owner 2026-09-30 批复翻回（裁定#431 第①项）"并各载恢复前置达成事实（echo-guard 撞号治愈/187 件落地/worktree sync） |
| 4 | gate_auto_registrar.py | `auto_register_gates`(:262)：从名册 YAML 动态 import+register（REGISTRY_REL_PATH=:90 指向名册路径）；**fail-closed（裁定#351）**：任一 enabled gate 装载失败/装载数对账不符→`GateAutoRegistrationError` 阻断提交（模块头 INVARIANTS :8、ERROR_CONTRACT :13）；enabled=false 跳过；files_trigger 注入校验 fail-closed（QMine M5 矿②） |
| 5 | CommitGateRegistry.check_all | commit_gate_registry.py:392 起：priority 升序逐台；`files_trigger` P5 条件触发未命中记 `trigger_skip`（:452-461）；`skip_gates`（worktree 隔离跳过集合，单一真源=session_worktree._WORKTREE_SKIP_GATES，:462-473）；preflight 结果复用（:491-497）；P2⑧ 缓存查/存（:444-452,:478-490）；S1 分道 15 台名单门改发本体 gateway（:413-434,:498-505）；单 gate 异常降级 fail-closed 不阻断后续 |
| 6 | DOC-HEADER-SUITE 聚合门（簇1 宿主） | blueprint_format_gate.py:204-260；`_DOC_HEADER_SUITE_SUBS`(:220-229) 七判据数据（源台 gate_id/模块/判定体/原 priority）；`_union_check` 逐子判定体独立判定、违规带 `[源台名]` 前缀聚合呈现、任一失败即阻断、判据零退役；priority=77；模块双重身份（BLUEPRINT-FORMAT 薄工厂 :193-197 保留出名册供历史引用） |
| 7 | gate_cache_preflight.py（P2⑧ 缓存+P2⑦ 预跑基座） | `CONTENT_SCAN_CACHE_WHITELIST` 15 台（:102-122，实测 top15：复用面 10+耗时面 5）；缓存键六元组 gate_id×own_scope×own 内容 sha×spec_sha×manifest×flags_mtime（:329-332，T7/B2 改键——旧键含 HEAD/write-tree 是"87 命中/24h"病根，:20-23）；只缓存 passed=True、TTL 600s（:132）；`GATE_INPUT_MANIFEST` 现空置（:129）；P2⑦ `Fingerprint`（write-tree/HEAD/flags_mtime，:164-201）服务锁外预跑+锁内 F′==F 采信 |
| 8 | S1 不可变树视图 CommitTreeView | flag `git_operations.immutable_tree: true`（config/flags.yaml:52）**已实弹生效**——翻转 commit ed935c29af（2026-09-27，Owner 09-26 批，selfcheck 100 笔/1522 文件 byte_mismatch=0）；`_immutable_tree_enabled` 直读 YAML（git_commit_gateway.py:220-236）；`_build_own_tree_view` 构造视图（:3108-3144，base_rev=门禁时刻 HEAD 修正 off-by-one、fail-safe 回退本体）；`_check_gates_with_drift_watch` :3213-3222 注入 check_all；`_diff_helpers.py` 四入口代理（docstring :31-36；`_own_tree_view` 分派原语 :239-259；`_read_staged_file` :262-277；`_get_staged_py_files` :280+）；15 台 SHARED_INDEX_WITHOUT_OWN_SCOPE 故意读全索引不分道 |
| 9 | 三个 flag（均 ON，production） | `gate_result_cache: true`（flags.yaml:99-102，2026-09-12 Owner 批转正）；`gate_preflight: true`（:104-107，同批转正）；`gate_precommit_run: true`（:109-112，裁定#341 方案②）——种子所谓"出厂 OFF 待翻转"三件已全部完成翻转 |
| 10 | 遥测面 | `.runtime/audit/gate_execution_stats.jsonl`（逐台 ms/reused/trigger_skip，`_stat_ms` 记账经 check_all 各分道写入）；`.runtime/audit/commit_block_events.jsonl`（阻断事件，阈值化只记异常，git_commit_gateway.py:1963-1975） |
| 11 | 逐台裁定指针 | `docs/_working/gate_survival_adjudication.md`：§4.1 大头门 18 台逐台详裁（:62-83）、§4.2 中尾按簇批量裁定（:85-193）、§4.3 manual 28（:195-197）、§5 hook 通道（:201-276）、§6 非门禁组件（:280-305）、§7 账实不符六项（:309-316）、§8 施工包（:320-346）、§9 Owner 门位+批复留痕（:350-358）、§10 防重复施工（:360-364）、§11 执行留痕（:368-389） |

### 九大重叠簇（完整列出；与裁定册冲突处按裁定册并注明）

| 簇 | 内容 | 状态（file:line） |
|----|------|------------------|
| 簇1 | SUITE 七子台双跑（DOC-HEADER-SUITE 聚合门已顺序调 7 子判据，7 个 standalone 条目曾各跑一遍） | **已执行退役**（2026-09-30，名册 7 条 enabled=false CAS 落盘，commit 03ce599b85①；安全实证=9/26 遥测 256 链 SUITE:TTL 同起同落 160=160，裁定册 §11.1） |
| 簇2 | diff+AST 系统性重复扫描 ~25-30 台各自独立跑 `git diff --cached --name-only`+逐文件 added 行+ast.parse 无共享（裁定册 §1.4，_diff_helpers.py） | 处方=**S1 视图+preflight 缓存，两 flag 均已 ON 实弹**（flags.yaml:52/:99-107；ed935c29af；~72 台一次改指输入源不再读共享暂存区，git_commit_gateway.py:3200-3212 注释） |
| 簇3 | depgraph 复合：DEPGRAPH-ENFORCEMENT 内部 4 子扫描各跑 git diff+DB 连接 | 并 1 待施工（A2 包，裁定册 §8.12）；同族 DEPGRAPH-FRESHNESS 流式读 _meta **已落**（头部 4KB 正则提取 saved_at 失配回落全量，裁定册 §11.3） |
| 簇4 | 注册表 YAML 读取共享缺位：capability 册被 ≥4 台独立 parse（REGISTRY-MASS-DELETION/REGISTRY-YAML-PARSE/SSOT-REDEFINITION/CONSUMERS-ACCURACY 等，裁定册 §4.1/4.2 逐台"簇4 共享 parse"批注） | 待施工（A4 包=parse 共享 `_capability_registry_io` 扩展，裁定册 §8.11） |
| 簇5 | 机制门（登记型，非内容扫描）：COMMIT-CRITICAL-SECTION-LOCK 全局锁实名登记等 | 【保留】登记项（裁定册 §4.2 末行；统一册 manual/active 唯一 1 台） |
| 簇6 | 6 对同脚本双层门：ID-UNIQUENESS/TTL-METADATA/ENCODING-SAFETY/DIRECTORY-CONTRACT/PURE-SHIM/BLUEPRINT-NODE-ID-HARDCODE 的 L1=subprocess 调 hook 同一脚本 thin wrapper（裁定册 §1.2） | 通道 SKIP 已落 5 对（gate-id-uniq/frontmatter/encoding-safety/directory-contract/doc-node-id 入 `_PRECOMMIT_CHANNEL_SKIP_HOOKS`，git_commit_gateway.py:464-473）；PURE-SHIM↔gate-ssot-code 一对**未跳**（三脚本链需链内跳过，裁定册 §5.1.3） |
| 簇7 | 已合并墓碑：统一册 deprecated 27（全 manual 段）；裁定册 §4.2【已合并·锚保留】逐台在案 | 墓碑语义落册债未清（生成器 seen_gate_ids 去重致 6 台 in-process 墓碑落册失败，generate_gate_registry.py:143-158，裁定册 §7.2——现行统一册 178 条中无此 6 台墓碑条目） |
| 簇8 | "297ms 三疑点已并" | **种子口径，盘面未定位独立真源锚**（docs/ 全树 grep 无"三疑点"/"297ms"独立载体；疑似裁定分析会话口头台账）——按种子收录，移交复核（§4） |
| 簇9 | registry 系三台互补（跨域不同对象→不并）：REGISTRY-MASS-DELETION 净删防护（裁定册 :69）/REGISTRY-YAML-PARSE 结构硬化（:103）/REGISTRY-CODE-ANCHOR 代码锚（:148） | 【保留】三台各守一面，维持互补不合并 |

## §2 六向台账

| 组件 | 上游触发源 | 下游消费方 | 输入面 | 输出面 | 真源锚 | 耗时账 |
|------|-----------|-----------|--------|--------|--------|--------|
| 名册 YAML | 人工/施工批编辑（CAS safe_write） | gate_auto_registrar 装载 | gates 列表（gate_id/module_path/factory/enabled/files_trigger） | 装载失败抛错阻断 | in_process_gate_registry.yaml:40 | 装载一次性（__init__） |
| auto_register_gates | GitCommitGateway.__init__ | CommitGateRegistry.register | 名册 YAML+commit_gates/*.py | 已注册 GateSpec 集（96 台） | gate_auto_registrar.py:262-330 | 每进程 1 次 import 面 |
| check_all | _check_gates_with_drift_watch（:3213） | 阻断裁决→commit 结果 | files 清单+gateway（或视图）+preflight_results+skip_gates | list[GateResult]（逐台 passed/detail） | commit_gate_registry.py:392-510 | 窗口累计 147,412s/2185 链（裁定册 §1，含恶化期） |
| 簇2 扫描门（~25-30 台） | check_all 逐台分发 | 各台 GateResult | S1 ON=两棵不可变树（HEAD/index 树）；OFF=共享暂存区（现状 ON） | own 违规集/ warn | _diff_helpers.py:31-36 | S1 读面收益 7.1× 已验收（裁定册 §10）；缓存命中台 0ms 记账（cache_hit） |
| P2⑧ 缓存 | check_all 白名单台 | 命中台跳现算 | 键=六元组内容哈希 | .runtime/gate_cache/*.json | gate_cache_preflight.py:295-333 | TTL 10min；命中省整台现算 |
| P2⑦ 预跑 | gateway.commit 拿锁前 | 拿锁后 F′==F 采信 | write-tree/HEAD/flags mtime | Fingerprint+预跑结果表 | gate_cache_preflight.py:164-201 | 锁内只跑信号型+其余台 |
| S1 视图 | flags.immutable_tree ON | 72 台门输入源 | base_rev=HEAD+staged_tree=write-tree | 视图替身（map git 命令改指两树） | git_commit_gateway.py:3108-3144 | 树内外来 staged 恒 0（结构保证，:3119-3120） |
| SUITE 宿主 | 名册 enabled 台 | 阻断聚合消息 | staged .py added 行+docs 面 | 7 判据聚合失败串 | blueprint_format_gate.py:204-260 | 单趟替代 8 趟（省 ~2-5s+/笔，裁定册 §11.1） |
| 遥测 jsonl | _stat_ms/阻断事件 | gate_stats 复核脚本/commit_perf_report | 逐台 GateResult | jsonl 行 | git_commit_gateway.py:1940-1961 | 只记异常（阈值化）防爆炸 |

## §3 缺陷与已修

**已修（本环节，2026-09-30 前后落地）**：

1. 簇1 七子台+SCRIPTS-IMPORT-INTEGRITY 共 8 台执行退役——名册 enabled=false CAS 落盘（03ce599b85①；名册 :102/:108/:234/:240/:270/:371/:384/:417 行内注记）。
2. 账实对齐闭环：裁定册 §7.1"4 台名册 disabled×统一册 active"矛盾——以裁定#431 翻回名册侧终局（两侧现均 active/enabled，名册 :90/:208/:246/:352；**本条为裁定册 §11"维持 disabled"记载之后的新令，以裁定册 RULE-RULING 真源 ruling_registry.yaml:5989-5996 为准**）。
3. BLUEPRINT-FORMAT 墓碑/运行时单跑并存矛盾（裁定册 §7.3）——随执行退役消除（名册 :371）。
4. DEPGRAPH-FRESHNESS 整读 10.6MB 依赖图→流式读 _meta 头部 4KB（03ce599b85③，测试 +3 共 30 绿）。
5. S1 视图+双缓存 flag 全部 ON 实弹（ed935c29af + flags.yaml:99-107；簇2 处方到位）。
6. T7/B2 缓存键改内容哈希，治"87 命中/24h"并发作废病根（gate_cache_preflight.py:18-23，红证 tests/git/test_gate_cache_key_isolation.py）。

**在案缺陷/债（未清）**：

1. 统一册生成器墓碑落册失败（generate_gate_registry.py:143-158 seen_gate_ids 去重）——in-process 6 台墓碑语义不在统一册；修复须"改生成器+重生成同批"否则 manifest-drift 自爆（裁定册 §11 第二波）。
2. 3 个实跑 hook（gate-detect-git-dangerous/shell-dangerous/permanent-deletion）统一册仍无条目（本册逐 id 复核 False；裁定册 §7.4 债仍开）。
3. enforcement_channel 口径债仍开：GATE-ARCH 实为 manual 段 hook 却计 pre-commit channel（统一册实测 pre-commit 51=真实 50+GATE-ARCH 1；对照 .pre-commit-config.yaml manual 段 7 台实测），裁定册 §7.5。
4. 簇4 parse 共享、簇3 DEPGRAPH-ENFORCEMENT 4 扫并 1 未施工（A2/A4 包）。
5. 簇8"297ms 三疑点"无盘面真源锚（本册 §1 簇表第 8 行）——需原分析会话补锚或除名。
6. 裁定册 §7.6 "gate-14 死正则写进统一册 :147"——已随该条目退役出册自然消失（复核 False），债面关闭。

## §4 待办移交

| 项 | 内容 | 认领 |
|----|------|------|
| T-E3-1 | A2：DEPGRAPH-ENFORCEMENT 内部 4 子扫描并 1（裁定册 §8.12） | st-gate-rationalize A 段 |
| T-E3-2 | A4：簇4 注册表 parse 共享（_capability_registry_io 扩展，§8.11） | 同上 |
| T-E3-3 | 生成器登记债全项（墓碑落册修复+重生成同批；gate_registry.yaml 第二波） | st-gate-rationalize B 段 |
| T-E3-4 | 补登 3 个 gate-detect-* hook 进统一册 | 随 T-E3-3 同批 |
| T-E3-5 | 簇8"297ms 三疑点"补锚或除名（找原分析会话/分析脚本 .runtime/tmp/commit_speed_audit 重建） | 总包 C 段交叉验证 |
| T-E3-6 | BLUEPRINT-HEADER 内部 2 扫并 1（宿主已退役 standalone，聚合门内部同源并扫，§8.12 后半） | A3 包 |
| T-E3-7 | E9 册衔接：immutable_tree/两缓存 flag 的遥测实证（cache_hit/preflight_reused/trigger_skip 分道计数抽取）由 e09_telemetry_flags.md 承载 | M-E9 |
