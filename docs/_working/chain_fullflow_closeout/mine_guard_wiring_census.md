---
ttl: task_bound
---
# M5 广度普查案卷：「声称已防护」接线真实性总表（全量版）

> 班次：全流通战役挖矿班 M5（只挖矿、只写案卷、不施工）。判据沿用上一班两问：**谁调它 + 它能否改变行为**。
> 机生总表=`.runtime/tmp/mine_dossiers_20260926/wiring_table.md`；再生成脚本=`gen_wiring_census.py`（含归因分类 `classification.json`）；原始引用图=`census_raw.json`。本卷人工改判优先于机判初判，逐条标注。

## 1. 分母与取数命令（实测，非记忆）

| 类 | 分母 | 取数命令 |
|---|---|---|
| A 宪法硬规则+补充铁律 | 13（§1 表含热文件行）+4 补充=17 件 | AGENTS.md §1 逐条誊录（本卷 §2A） |
| B 门禁名册 | gate_registry.yaml(dev) 181 条 = `total_gates` 字段 181（一致）；active 169（pre-commit 55 / commit-gate 113 / manual 1）；deprecated 12（含 redirect 锚点） | `git show dev:docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml > .runtime/tmp/gate_registry_dev.yaml` |
| B' commit-gate 装载真源 | in_process_gate_registry.yaml 103 条（enabled 96 / disabled 7；`total_gates` 字段=102 与条目数 103 差 1=字段漂移） | `docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml`；装载链=`git_commit_gateway.py:1033 auto_register_gates()`（YAML 动态 import+register，fail-closed 裁定#351 系） |
| C 运行时守护/治理桥 | 28 件符号清单（硬编码于生成脚本 GUARDS，可扩） | `python .runtime/tmp/mine_dossiers_20260926/gen_wiring_census.py` |
| D 计划任务 | Zephyr 系任务 49 个（GBK 解码 CSV 实测） | `python -c "subprocess.run(['schtasks.exe','/query','/fo','CSV'])...decode('gbk')"`（只读；任何 schtasks 写操作=Owner 门） |

## 2A. 宪法 17 条→执法件映射（每条给"能否变红"证据）

| 规则 | 执法件 | 装载 | 变红证据 | 态 |
|---|---|---|---|---|
| 1 RULE-ENV | 无机械执法（程序性） | — | — | 设计即知识-only |
| 2 RULE-GUARDIAN | `ZephyrAlpha_ProcessReaper` 计划任务 + reaper 模块（13 引用） | 任务实存 | `tests/.../test_process_reaper*`（7 测试文件） | 真执法（任务侧）；台账快照缺陷沿上班案 |
| 3 RULE-WORKTREE | GATE-WORKTREE-REQUIRED(pre-commit 实钩)+WORKTREE-REQUIRED(in-proc) | √ | 有配对（不在 46 缺测清单） | 真执法 |
| 4 RULE-DEPGRAPH | DEPGRAPH-ENFORCEMENT 宿主（吸收 DEPGRAPH-WRITE-PATH/NEW-FILE-DEPGRAPH-ENFORCEMENT/RENAME-DEPGRAPH-SYNC 子目） | √(宿主 enabled) | 宿主装载 fail-closed 测试（test_gate_auto_registrar 有 raises 断言） | 真执法(聚合)；子目名册仍单列 active=虚报面（登记） |
| 5 RULE-REGISTRY | REGISTRY-* 门（manifest 装载） | √ | 部分在 46 缺测清单 | 混合 |
| 6 RULE-SSOT | GATE-SSOT-CODE / SSOT-REDEFINITION | √ | **GATE-SSOT-CODE 零配对测试** | 疑似判据失效 |
| 7 RULE-DATA-OPS | check_tick_duplication.py（工具非门） | 有调用方 | **零配对测试** | 疑似判据失效 |
| 8 RULE-RULING | RULING-COMMIT-VERIFIED(装载√)；RULING-REFERENCE=agg-sub@REFERENCE-INTEGRITY(宿主√) | √ | RULING-REFERENCE 零配对（在 46 清单） | 半接线嫌疑（宿主是否代证未核） |
| 9 RULE-CAPABILITY-LOOKUP | CAPABILITY-LOOKUP-REQUIRED | √ | 不在 46 清单 | 真执法 |
| 10 RULE-SCHEMA-TZ | GATE-GEN-NO-REALTIME-TIME / DATETIME-NOW-FORBIDDEN(redirect→DEPGRAPH-ENFORCEMENT) | √/聚合 | **GATE-GEN-NO-REALTIME-TIME 零配对** | 疑似判据失效 |
| 11 RULE-SECRETS | NO-SECRET-HARDCODE+bare_getenv_gate+secrets 族（102 引用/33 测试） | √ | 有 | 真执法 |
| 12 RULE-GIT-SAFE | detect_git_dangerous(pre-commit √)+git_safety_wrapper | √ | 有配对 | 真执法 |
| 13 热文件 safe_write_text | 78 处 src/scripts 引用+12 测试 | √ | 调用面实测 | 真执法 |
| 补1 RULE-CLONEGUARD | clone_guard 族（23 引用/13 测试）+clone_guard_audit | √ | 有 | 真执法 |
| 补2 TRANSLATION-COVERAGE | 同名门（manifest √） | √ | 不在 46 清单 | 真执法 |
| 补3 RULE-WORKSPACE-WIP | classify_workspace_wip（有调用方） | 工具 | 零/少配对（未在 46 清单按 gate_id 计） | 真执法嫌疑待抽 |
| 补4 CREATE-GUARD | create_guard.py（creation_token 16 引用/8 测试） | √ | 有 | 真执法 |

## 2B. 四态机判总表（B 类 169 active gates）

机判规则（`gen_wiring_census.py` v3）：装载=pre-commit→脚本 basename 实现在 `.pre-commit-config.yaml`（69 hooks）；commit-gate→in_process 名册 enabled 且 module_path 文件存在+factory AST 验证；配对测试=tests/ 提及 gate_id。

| 态（终判=机判+人工归因） | 件数 | 说明 |
|---|---|---|
| 真执法(初判：装载√+配对测试) | 104 | 机判，未逐件过反事实闸（见四闸④） |
| 真执法(聚合宿主回填，人工改判) | 13 | 22 未装载件中的 agg-sub：挂 REFERENCE-INTEGRITY/BLUEPRINT-HEADER/MAP-ALIGNMENT/DEPGRAPH-ENFORCEMENT/COMPLEXITY-GUARD 五宿主（宿主均 enabled、子目缺失 fail-closed 呈报，`panorama_alignment_gate.py:303-314`）；名册仍单列 active=归属虚报面登记 |
| 疑似判据失效(装载√无配对测试) | 43 | 清单=census_raw.json `gates_no_test_pair`；**不判可删**（Owner 令：只合并/降档/diff 化） |
| 装饰 | 9 | 4 停用链（ALGO-FLOW-LINK/CAPABILITY-OVERLAP/PERMANENT-SYSTEM-TRIGGER + 其子目 MANUAL-ONLY-PERMANENT、VOCAB-CHAIN@停用宿主 vocab_hardcode_gate*）+ 4 悬空（COMMIT-CRITICAL-SECTION-LOCK/GATE-ZR/GATE-DRIFT/GATE-ERRCODE 无钩子无启动器承接）*GATE-ERRCODE 有 validate_config_integrity.py 文本提及，降格半接线见下 |
| 半接线 | 2 | GATE-ERRCODE（仅单一脚本顺带调）；VOCAB-CHAIN（in-process 宿主停用、pre-commit 同族 hook `check_vocab_hardcode.py` 在——两面对账待施工班核） |

C 类 28 件：**装饰 2**（`alert_aggregator` 零调用方仅 1 测试自引用=同型复发确认；`session_env_guard` 仅 `redline/__init__.py` noqa 静态 import，`screen_session_env/filter_env` 全仓零调用=上班"装饰"结论在 dev 面复测成立，import 出现≠接线）；**疑似判据失效 3**（`check_tick_duplication`/`batched_auto_committer`/`session_claim` 有调用方零测试）；其余 23 件调用方>0（kill_switch 54 引用/47 测试、LSG、gateway、lock_files 等=真执法面）。
D 类：reaper/belt/watchdog/drift-watchdog/deadman/CHHealthProbe/DataScheduler 任务实存（ProcessReaper EXISTS）；heartbeat_daemon **无对应计划任务**，调用面=session_concurrency/session_worktree=会话拉起型 → 队列/会话一停即饿死=**半接线**（与任务书示例同型）。

## 3. 新发现装饰件清单（按危害排序，均双证）

1. **PERMANENT-SYSTEM-TRIGGER 停用 + 名册虚报 active（高：宪法 §9.3 事件触发红线无执法）**——gate_registry active ↔ manifest `enabled: false`；且 `PERM-TRIGGER`(deprecated)→redirect→此停用件；子目 MANUAL-ONLY-PERMANENT 随之悬空。复现：`grep -B2 -A6 "gate_id: PERMANENT-SYSTEM-TRIGGER" docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml` + 生成脚本 CLASS 行。
2. **GATE-VOCAB in-process 宿主停用（高：词表恒绿面）**——`vocab_hardcode_gate` manifest enabled=false；名册 GATE-VOCAB 走 pre-commit hook（该面在），但 VOCAB-CHAIN(commit-gate 面) 指向停用宿主=半接线；两面是否等价未证。
3. **ALGO-FLOW-LINK / CAPABILITY-OVERLAP claim-active-but-disabled（中：名册=归属账本失真）**——同上复现法；合计 3+1 件 active/disabled 漂移=「数据假绿」类（一切读名册算覆盖率的下游被喂假数）。
4. **COMMIT-CRITICAL-SECTION-LOCK（中：门禁空转）**——唯一 active manual gate：entry 指向 gateway 文件但 gateway 内无该 gate_id 字符串；全仓唯一引用=生成器自身（名册自指）。声称执法"提交临界区锁"，无任何运行时检查以该名变红。
5. **GATE-ZR / GATE-DRIFT（中）**——channel=pre-commit 但不在 69 hooks；behavioral_auditor 模块实存（20 src 引用）但无人以 GATE-DRIFT 身份调度=判据存在、门禁不存在。
6. **session_env_guard / alert_aggregator（沿上班，本轮复测确认）**——判据两问全过：前者"能改变行为"（有测试证明 filter_env 可拒）但"谁调它"断链；后者两问全断。
7. **check_tick_duplication 零配对测试（RULE-DATA-OPS 判重唯一指定工具）**——破坏性 DB 三步验证第二步的尺无红证。

## 4. 逐类实测记录（勾选=已做）

- [x] B/B'：装载双轨机判（52/55 pre-commit 实钩；98/113 manifest 装载；103/96 名册/enabled）。
- [x] redirect_to 12 条全量核验：**全部 status=deprecated**（诚实锚点，非虚报）——初稿"PERM-TRIGGER 两级断链"已修正为"目标件停用"单点缺陷（§3.1）。
- [x] 聚合宿主 5 个逐一 enabled 验证 + 子目 fail-closed 语义读码。
- [x] D 类计划任务 49 个全名单实测（含 ProcessReaper 实存）。
- [x] A 类 17 条映射表（§2A），4 条落"疑似判据失效/半接线"。
- [x] 判别力抽验：`tests/governance/test_gate_replay_harness.py`（自述"恒绿尺=无效尺"，构造两树仅差一行验 added_lines 精确捕获+注入噪声验漂移=红样现成基座）；`test_gate_auto_registrar.py`（invalid yaml/non-dict/缺 factory 均 raises=装载 fail-closed 有红证）。
- [ ] 43 无配对 gate 的逐件红样构造（挂起，复用 replay harness 台）。
- [ ] C 类 23 件逐件"返回值是否进分支"读码（本轮按引用数初判）。

## 5. 六向寻路台账

- ①名册→代码：装载真源=in_process 名册+pre-commit 钩子**双轨**，两轨与 gate_registry 三份账可漂移（实测漂移 3 停用虚报+in_process 自身 total_gates 字段 102≠103）。发现。
- ②代码→行为：`commit_gates/__init__.py:28-34` 自述静态 import 仅为 ORPHAN-MODULE 反孤儿合规**不代表注册**→"文件被 import/引用"是假接线信号（session_env_guard 实证）；注册只认 manifest+enabled。发现（判据修正已入生成器口径）。
- ③外部对照（URL+发布方+年份，≥2 源）：
  - [Practical Mutation Testing at Scale: A view from Google](https://www.computer.org/csdl/journal/ts/2022/10/09524503/1wpqGmxSESI)（IEEE Trans. on Software Engineering / Google，2022）——用变异测试度量"测试能否抓到植入缺陷"=本卷"配对测试还须有判别力"的同行方法；本仓 replay harness 红证构造即其抽样式等价。
  - [Security Fundamentals Part 1: Fail Open vs. Fail Closed](https://community.opentext.com/cybersec/b/cybersecurity-blog/posts/security-fundamentals-part-1-fail-open-vs-fail-closed)（OpenText 安全博客，2014）——控制失效必须默认拒绝；对照发现：装载面本仓已 fail-closed（裁定#351 系），但**名册面漂移（active/disabled 不同步）是 fail-open 的**——建议项入 §8。
- ④事故向：上班 9 装饰件复测——alert_aggregator 仍零调用（同型复发）、session_env_guard 补了"装饰 import"新形态；无新翻案。发现。
- ⑤运行态向：计划任务/会话拉起/事件驱动三态分账（§2B D 类）；heartbeat=会话依赖饿死形态确认。发现。
- ⑥字段向：可机判字段=`status/entry/source/own_scope/files_trigger/redirect_to`×`enabled/module_path/factory_function`；**缺**：配对测试指针、最近一次变红时间、聚合父-子目系（本次靠 regex 反推）——三字段补齐即可全名册机判+判别力下界。发现。

## 6. 挖矿日志

| 轮 | 矿脉 | 定性 | 产出 | 复现 |
|---|---|---|---|---|
| R1 | dev 名册 | signal | 181/169/通道分布 | §1 命令 |
| R2 | 全仓索引 | signal | 9018 文件引用图（首版 per-gate walk 超时=noise：改单趟） | 生成脚本 |
| R3 | 装载双轨 | signal | 52/55、98/113、103/96 | 同上 |
| R4 | manifest→代码 AST | signal | 首跑"95 broken"=路径拼接 bug（noise，当场证伪），纠偏后 0 broken | 同上 |
| R5 | redirect/聚合链 | signal | 12 redirect 全 deprecated（初判"两级断链"过头，已改判）；5 宿主聚合+2 停用宿主 | classification.json |
| R6 | 22 未装载归因 | signal | 13 agg-sub/3 disabled/4 悬空 | 同上 |
| R7 | 守护件调用面 | signal | alert_aggregator/session_env_guard 装饰复确认；heartbeat 会话依赖 | census_raw.json |
| R8 | schtasks | signal | 前两轮 grep 零匹配=**GBK 编码假红**（noise，归因留痕）；解码后 49 任务、ProcessReaper 实存 | §1-D 命令 |
| R9 | 外部对照 | signal | 两源入账（§5③） | WebSearch |

## 7. 防噪音四闸过闸记录

1. 复测闸：R4 假警报、R8 编码假红当场证伪后才落结论；R5 初判过头当场降级改判。✅
2. 双证闸：装饰判定均给"名册条目+装载真源"两点；单证项一律标"嫌疑/待核"（VOCAB-CHAIN、GATE-ERRCODE）。✅
3. 工具自证闸：全部计数来自 `gen_wiring_census.py` 产物；`wiring_table.md`/`classification.json` 机生勿手改。✅
4. 反事实闸：仅 §4 抽验两点过了"判据恒真测试还红吗"（replay harness 正反两判、registrar raises 族）；其余 147 件未过闸→真执法只标"初判"，不写"已证有效"。✅（口径已声明）

## 8. 挖后自审闸（三态裁定；量尺=终局全貌：Owner 只做账号注册/API 申请/充值/策略转正审批）

施工向（判"新增须声明替代"，全资产净零）：
1. **名册三账一致性机判**（gate_registry.active ↔ in_process.enabled ↔ .pre-commit hooks 差集即红，含 total_gates 字段自洽）——施工；净零声明=并入 `generate_gate_registry.py` 校验段，不新增脚本/不新增门（替代现人工周审计动作）。
2. 名册增 `test_pair/last_red/parent_gate` 三字段（⑥缺口）——施工（生成器侧：tests 反查+replay 台回写）；替代=§5⑥手工 regex 反推。
3. 43+3 无配对件红样采集——挂起排期；解锁条件=日班排 20 门抽样过 replay harness（Owner 醒后批带宽）。
4. 3 停用虚报+4 悬空件处置——挂起；解锁条件=Owner 门（合并/降档/diff 化选项，夜间不退役）。
5. 全量逐门反事实测试台常跑——**方案封矿**；反驳者一问："169 门×构造样的一次成本 vs 抽样 20 门的覆盖率下界，差多少？"答：边际收益低且违 §4.1 净零（无替代声明）→封（非以"规模小/频次低"封）。

待 Owner 门位登记项（只登记）：①PERMANENT-SYSTEM-TRIGGER/GATE-VOCAB(in-proc)/ALGO-FLOW-LINK/CAPABILITY-OVERLAP 四停用是否有意，或名册改 status；②COMMIT-CRITICAL-SECTION-LOCK、GATE-ZR、GATE-DRIFT 三悬空件的合并/降档方向；③heartbeat_daemon 是否需要非会话期兜底触发（注意：看门狗自动恢复一事 Owner 已判"不必保护"，本条仅登记 daemon，不重提案）。

## 9. 长尾矿脉清单（未扫到，明示）

- pc 69 hooks ↔ 名册 181 反向差集的精确清单（本轮 regex 混入描述文本噪音，需严格字段化重跑）；粗查候选：retire_tmp_artifacts、detect_direct_llm_calls、validate_commit_message、auto_handoff_log、scan_debt、serve_docs 等 6-10 个"有钩子无名册"件。
- C 类逐件"返回值进分支"读码（23 件只做了引用计数）。
- 5 宿主聚合子目与子目原测试的配对迁移（DECISION-MAP 等有 tests/trading/test_decision_map.py，其余未逐一对账）。
- A 类"半接线嫌疑"3 件的深挖（registry 族、workspace-wip 工具面）。
- risk_tier_registry 人机门位执法面、SECRETS 三道 gate 逐道、前端 app_panel"绿"的供数真实性——零覆盖。
- 一次性任务（C4Exam_Full0916 等 N/A 态）清理=Owner 门（schtasks 写禁）。
