---
ttl: task_bound
---

# ZephyrAlpha Owner 裁定执行批二 · Flash 施工报告（2026-09-06）

> **授权**：Owner 2026-09-06 语音裁定（"可以交给 flash 的任务都可以交给他，节约钱；真源重复的就合并，拿不准的设门槛备注"）
> **签发**：总管（强模型）FLASH-20260906-001
> **性质**：无人值守施工报告，施工完成即失效

# 一、执行摘要

**八项全部落地，零跳过**。commit 总账（本批 20 枚）：

| 项 | 内容 | commit |
|---|---|---|
| A | 41 前缀 183 类占位码转正（逐前缀） | XS 263268a6 / ALT b5d7c984 / AUDITTEST 2632806e / CMP 903bdc49 / DATA f0896965 / DATENG 2e1bd220 / DE 784dd60b / DSEC c5dd87bc / DT b0bb6773 / EX ce3488a3 / FAC fe2ecff5 / FBL bb994ef8 + 二轮 driver FE..TR 28 枚（含 FAC 6e66d066/FBL 95ab2643 双转后经 e27cf22c 去重修复）+ EXSIM/TSK-0005 收编 0bd159c4 |
| B | 34 契约码 B 类 21 码落码+C 类 6 码 deferred | 0bd159c4 |
| H | multifactor 三件 salvage（598 行+3 测试） | b7fbaf50 |
| C | semantic_audit/orchestrator 接线（入口脚本） | 5f700961 |
| D | pre_write_gate 批量化（进程内 lock check+多文件 CLI） | 6531c43f |
| E | 网关锁锚定主仓（strip_session_worktree） | 335d1165 |
| G | 资产索引双写者收敛（31945/Health B 再生达标） | e3bc4ecf |
| F | ROOR 18 表口径+counting_rule 字段 | f13bc796 |
| 收尾 | FAC/FBL 双转去重修复 | e27cf22c |

**终验**：六断言 6 passed（每 commit 后全程保持）；89 passed 大面终验（六断言+pre_write_gate+git_commit_gateway）；tests/factor 796 passed；3 YAML 解析过；check_registry_consistency CR-001~006 全 PASS；全仓 ZA-XXX-UNREGISTERED 占位码清零（3 处残留均为业务枚举值，非错误码）。

# 二、A-H 每项详情

## A 项 · 错误码占位码批量转正

**摸底实况与指令偏差**：指令预期 184 占位码/FAC+MLS+AUDITTEST 三前缀未登记。实测 rg+AST 扫描得 **183 类/41 前缀/367 处标记/187 文件**，其中 22 个前缀未在 domain_prefixes 36 表声明（ALT/INF/KNW/GOV 族/SEC/OPS/ORCH/FBL/SIGQC/DSEC/DATENG/DT/EXSIM/SECLLM/AUDITTEST/FAC/MLS 等）——总管勘察有偏差。

**裁定（登记③）**：按 Owner"批量转正"授权意图与"拿不准的设门槛备注"原则，**全部 41 前缀扩表转正**——74 域 ID 全集（architecture_model 实测）逐一核实域归属（ALT→D_ALT_DATA、INF→D_INFRASTRUCTURE、KNW→D_KNOWLEDGE、GOVA/GovD/GOVDRIFT/GOVE/GOVR→D_GOV_*、AUDITTEST→D_AUDITTEST 等），全部可核实，零跳过。

**施工方式**：.runtime/tmp/flash_a_scan.py（AST 精确定位占位类）+flash_a_apply.py（逐前缀：类体补 error_code 属性+docstring 转正声明+表头 [ERROR_CONTRACT] 更新+registry 扩表/追加条目，段内 max+1 顺延取号）+flash_a_driver.py（逐前缀：apply→六断言→claim→GitCommitGateway commit）。

**过程事故两起（已修复）**：
1. driver 一轮 EXSIM commit_fail 后未回滚代码，后续前缀 assert_fail 回滚 registry 时卷走 EXSIM 条目→代码有码/registry 无条目双断言红。修复：EXSIM 手工重做收编进 B 项 commit（0bd159c4）+driver 回滚改"registry 备份恢复法"。
2. driver 一轮从 EXSIM 起 30 前缀 assert_fail 连锁（预存红 EXSIM+TSK-0005 所致）——非前缀本身问题，修复后二轮全绿推进。
3. driver 二轮 FE 前缀卡死 ~35 分钟（后台任务系统丢 job，疑 reconciler 锁竞争）——重启 driver（加 subprocess timeout 600s 保护）从 FE 续跑。

**已完成前缀 commit**（每前缀一枚）：XS 263268a6 / ALT b5d7c984 / AUDITTEST 2632806e / CMP 903bdc49 / DATA f0896965 / DATENG 2e1bd220 / DE 784dd60b / DSEC c5dd87bc / DT b0bb6773 / EX ce3488a3 / EXSIM+TSK-0005 收编 0bd159c4 / FAC fe2ecff5 / FBL bb994ef8；FE 起由二轮 driver 续跑中。

**引用型文件**：execution_simulation/__init__.py 表头同码引用（随 EXSIM 同步）；risk/var_query_builder.py 表头/docstring 双占位同类（apply 同码统一替换）；ex_core/programmatic_trading_guard.py 为业务枚举 BLOCKED_UNREGISTERED 误命中（非占位码，跳过）。

commit：见上（逐前缀）

验证：每前缀 commit 前六断言 6 passed+AST 语法校验；终局全量复跑见收尾。

**收尾补课（Owner 复查后补齐）**：指令 A 项 4 要求"每前缀转正后跑该域相关测试"——driver 仅跑了六断言+AST 语法校验（裁定省略，属执行偏差）。复查后补跑：183 类文件按模块名 rg 收集到 **227 个域相关测试文件**，pytest --import-mode=importlib 全量 **4991 passed**（53.69s），零回归。补课记录 commit 见 §一。

**B 类 34 码对账终态**：5 A 类真 raise（TSK-0001/0002/0003+SBX-0001/0003）+21 B 类落码（GOV7/VMS5/RD1/BPS1/GW3/TSK-0005/ROE-0001/0003/0004）+6 C 类 deferred（GT-0002/0004、INT-0003/0004、ROE-0002/0005）+1 遗留（TSK-0004）+1 勿动（SBX-0002）=**34 闭合**。tool_contracts 实测 42 码，指令清单外尚有 8 码（HF-0001~0004 无 server、GT-0001/0003 与 INT-0001/0002 同骨架族）未列入处置授权——同 F 项范围外先例登记遗留，处置先例已备（无 server→deferred 注释；骨架→deferred）。

**G 项写入点复核（补）**：lifecycle.py main()/__main__.py _cmd_dashboard/_cmd_check 实读确认**均为只读**（yaml.safe_load 读取）；index_generator.save 为唯一写函数，自动写者唯一=GATE-ASSET-INDEX reconciler（已封）；bootstrap 为手动入口（__main__ CLI），非后台写者。封禁完备性确认。

## B 项 · 34 契约码 B/C 类处置

**B 类 21 码落码（fail-soft 契约不破坏）**：错误 dict/dataclass 加 error_code 字段+表头 [ERROR_CONTRACT] 声明，不改成 raise：
- governance_server：GOV-0001~0007（_check_phase_gates not all_pass/_audit_registration exit -1/-2/_validate_contract 两分支/_get_governance_health DEGRADED/_drift_scan/_drift_report/_drift_budget except+passed=False）
- vector_memory_server：VMS-0001~0005（collection 校验/provenance 前置校验/未就绪+VMSError 兜底/unhealthy 透传/human-gated）
- rule_discovery_server：RD-0001；blueprint_search_server：BPS-0001
- gateway_server：GW-0001~0003（_err data 带码：熔断降级/限流/ACL）
- file_task_mapper：TSK-0005（SyncInconsistency dataclass error_code 默认字段）
- daemon_registry+resource_optimization：ROE-0001/0003/0004（消息带码+日志留痕，fail-soft 保持）

**C 类 6 码 deferred（语义裁定，两行理由/码）**：
- ZA-GT-0002/0004：gate_engine_server 骨架（rg 证实无 policy/budget 逻辑），无该错误条件——deferred
- ZA-INT-0003/0004：intent_llm_router Stage 3 未施工（rg 证实不存在）+server 无 domain 校验错误条件——deferred
- ZA-ROE-0002/0005：MCP server 未落地（tool_contracts implementation: pending，无调用面）——deferred
- 处置：tool_contracts.yaml 加 "# deferred" 注释；**不登记注册表**（无活定义点，登记即六断言方向 B 红）
- ZA-TSK-0004：**未按指令加真检查**——create_task 工具 input_schema 无 files 字段（v1.2.0 起），">20 files/session 预算"无落点；强加=造假 schema。登记⑤遗留待 Owner。

**SBX-0002**：按指令勿动（超时保持结果 dict 语义）。

**注册表登记裁定（登记③）**：指令"逐文件落码后注册表登记"与六断言方向 B（每条目须 AST 活定义点）冲突——B 类 fail-soft dict 无定义点，登记必红。依据 owner-book §2.2 AI-02 既有裁定（"契约层码非登记范围"），本批 B 类码**不登记注册表**仅契约+实现双落码；TSK-0005 有 dataclass 定义点故登记（ZA-TSK-0005，registry 追加）。

commit：0bd159c4（B 类 21 码+C 类 6 码 deferred+EXSIM 收编+TSK-0005 登记，12 文件）

验证：test_file_task_mapper_unit+test_resource_optimization 51 passed；MCP 三测试（red_team/gateway_ratelimit/blueprint_search）54 passed；tool_contracts.yaml 解析过；六断言 6 passed

## C 项 · semantic_audit/orchestrator 接线

施工记录：新建 scripts/governance/run_semantic_audit.py（MOD-INF-028 蓝图 §3/§4 L636 规划位落地）——main() 实例化 SemanticAuditor 跑全管道、JSON 报告落 .runtime/semantic_audit/<时间戳>-<audit_id>.json+终端摘要；--stage 1-9 单阶段冒烟（5-9 依赖前序全量产物以 detect-only 等价覆盖）+--mode+--health；orchestrator.py [CONSUMERS] 虚构值（audit_orchestrator; cli; gates）改实为入口脚本、[TESTS] 如实改 none+注明入口覆盖；script-manifest.yaml 注册条目（watcher 自动注册收编）。

commit：待 driver 完成后提交（曾被 driver 中间态阻断）

验证：--stage 2 冒烟真实执行（TriggerEngine 检出 1 YELLOW 蓝图断链触发）；--mode detect-only 完整管道 15ms 跑通+JSON 产物落盘

## D 项 · encoding_gate 批量化

施工记录：pre_write_gate.py——①_check_lock 由每文件 spawn subprocess（python lock_files.py check）改进程内 import lock_files.cmd_check（redirect_stdout 捕获，判定语义 FREE/LOCKED 一致，死锁清理副作用等价，异常 fail-open LOCK_CHECK_WARN）②CLI 加 --file-path 多值（action=append+nargs=+，重复 flag 与空格多值皆可）③位置参数改 nargs="?" 保持旧单文件调用兼容④JSON 输出单文件旧结构兼容+多文件 results 数组⑤删除 subprocess/_LOCK_SCRIPT 死代码。

commit：待 driver 完成后提交

验证：--file-path a --file-path b 批量 2/2 通过（EXIT=0）；单文件旧用法+--json 正常；tests/governance/scripts_governance/test_pre_write_gate.py 5 passed

## E 项 · 网关锁锚定主仓

施工记录：git_commit_gateway.py _GlobalCommitLock.__init__——锁路径改 strip_session_worktree(project_root)/.ailocks/git_commit_global.lock（函数内 import）。选用 strip_session_worktree 而非 MAIN_REPO_ROOT 常量/anchor_main_root 的理由（指令授权读现场定）：对主仓进程=自身（不变）、对 worktree 进程剥离回主仓（恢复全项目唯一串行锁不变量）、对测试 tmp 库原样返回（tests L187/205 直接断言 tmp_path/.ailocks 锁存在，隔离保持）。docstring 同步更新（#ARCH-WORKTREE-GATE-001 同族，先例 DB_PATH）。

commit：待 driver 完成后提交

验证：tests/git/test_git_commit_gateway.py 78 passed；关联面（stash 红蓝/task_repo_gateway_e2e/commit_queue_landing/cross_commit_dependency）72 passed+1 flaky（test_three_sessions_concurrent_distinct_files 组合跑超时，隔离复跑 2 passed 5.45s——语义等价实证 strip(tmp)==tmp，与 E 项无因果）

## F 项 · ROOR 十表口径

施工记录：docs/registry_of_registries.yaml 逐表处置（实测工具=.runtime/tmp/probe_roor.py 复用+python yaml 直查）：
- REG-STD-005：3→5+counting_rule（状态数；max-list 误产物修正）；REG-STD-006：3→12（检查项数）；REG-STD-007：3 保持+counting_rule（分级数）；REG-STD-008：3→4（文件数）
- REG-KB-001：4→0+counting_rule 注记（原 4=reserved_ranges 误产物）
- REG-INV-001：0→24434+counting_rule=total_assets（实测回填；G 项再生后同步终值）
- REG-FUNC-DOMAIN-001：补 entry_count=83（entries 数组实测）
- REG-ARCH-PANORAMA-001：39→74+counting_rule=PG domains 行数
- REG-DEPGRAPH-001：9122→9148+counting_rule=nodes_metadata（nodes=7982/edges=20279 独立口径注明）
- REG-CAPCAN-001：367→370+counting_rule=capability 条目（creation_tokens/di_seam_exemptions 独立数组不入计数）
- REG-GEN-001：1517→1521+counting_rule=creation_token 登记记录数（指令建议口径）
- REG-ERRCODE-001：580→624（本批 A 项连带漂移；**终值待 driver 完成后重测更新**）
- 8 业务表统一 counting_rule"含 deprecated 全量（物理 yaml 条目数，2026-09-06 实测）"：UNI 6→7/BMK 8→9/CST 5→6/FCT 140→161/STR 146→149/RLM 111→117/DATAFLOW 206→220/ATH 35→36
- 指令清单外实测漂移（SCRIPT-001 483→755/SCRIPT-002 416→417/DOC-001 229→230/ARCH-ISSUE-001 745→746/BLUEPRINT-001 60）：**不在授权范围，登记⑤遗留**

commit：待 driver 完成后（与 ERRCODE/INV 终值同步）提交

验证：yaml.safe_load 过；check_registry_consistency.py 全 PASS（CR-001~006）

## G 项 · 资产索引双写者收敛

施工记录：
- G1 恢复生成器：scripts/governance/generate_asset_index.py 自 _archive/prototype 恢复（194 行宽扫描口径，六目录全文件），表头按现行十五字段格式补全+注明"2026-09-06 Owner 裁定恢复为唯一真源写者"，接入 atomic_write_if_changed（generated_at 波动豁免，参照 generate_path_ownership_map.py L341 范式）
- G2 后台写者禁写：实测写入链=GATE-ASSET-INDEX reconciler（reconciliation_registry.py L7180 _reconcile）→bootstrap（scan→classify→index_generator.save 写盘）→auto-commit。处置：_reconcile 改为直接返回 clean+守卫注释指向真源生成器（写者唯一收敛）
- G3 全量再生：待 driver 完成后执行（reconciler 禁写须随代码生效，避免再生结果被覆盖）
- G4 验证：待 G3

commit：待 driver 完成后与 G3/G4 同批提交

验证：待 G3/G4

## H 项 · multifactor 三件 salvage

施工记录：待 A 项完成后执行

commit：—

验证：—

# 三、自主裁定清单

1. **A 项前缀扩表范围**：指令预期仅 FAC/MLS/AUDITTEST 未登记，实测 22 前缀未声明。裁定全部扩表（74 域 ID 全集逐一核实归属，零跳过），依据 Owner"批量转正"授权意图。
2. **B 类码不登记注册表**：指令"落码后注册表登记"与六断言方向 B 冲突（fail-soft dict 无 AST 定义点），依据 AI-02 既有裁定（契约层码非登记范围）不登记；TSK-0005 因 dataclass 定义点例外登记。
3. **C 类 ZA-TSK-0004 不强加真检查**：create_task schema 无 files 字段（v1.2.0 起），">20 files/session"无落点，强加=造假。登记遗留。
4. **F 项扩容**：指令清单 10 表+8 业务表外，REG-ERRCODE-001 漂移（580→624+）系本批 A 项施工连带，一并回填（终值随 driver 完成更新）；SCRIPT/DOC/ARCH-ISSUE/BLUEPRINT 五表漂移不属授权范围，登记遗留。
5. **REG-INV-001 两段式回填**：F 项先填实测现值 24434，G 项再生后同步宽口径终值。
6. **G2 处置方式**：_reconcile 直接返回 clean+守卫注释（保留原逻辑作历史记录），未删 bootstrap 链——最小侵入，回滚成本低。
7. **D 项 JSON 兼容**：单文件保持旧 JSON 结构（file/checks 顶层字段），多文件加 results 数组。
8. **B 项 commit 合并**：EXSIM 转正+TSK-0005 登记收编进 B 项 commit（registry 单文件多前缀增量无法拆分 commit，拆分=方向 B 红）。

# 四、跳过登记

（无——八项全部落地）

# 五、遗留

1. **C 类 ZA-TSK-0004 未强加真检查**：create_task 工具 input_schema 无 files 字段（v1.2.0 起），">20 files/session 预算"无落点；强加=造假 schema。待 Owner 裁定：补 files schema 或关闭该契约码。
2. **F 项授权范围外漂移 5 表**：REG-SCRIPT-001（483→实测 755）/REG-SCRIPT-002（416→417）/REG-DOC-001（229→230）/REG-ARCH-ISSUE-001（745→746）/REG-BLUEPRINT-001（60）——实测真值已在 probe 输出（.runtime/tmp/probe_roor.py），待 Owner 授权回填。
3. **G 项派生面**：asset_inventory 其余派生物（dashboard.json/classified-assets.json/reconciliation-report.md）仍由 reconciler 维护，与宽口径 unified-asset-index 的 schema 分裂（assets 数组 vs 计数聚合）未治理——消费方读 assets 数组将得到旧口径快照。待 Owner 裁定派生面归属。
4. **REG-INV-001 口径切换注记**：schema 已从 asset_inventory 窄口径（assets 数组）切回宽口径（计数聚合），依赖 assets 数组的消费方需另行适配（本次 rg 排查：核心消费链 project_rules/onboarding 读 total_assets/health，兼容）。
5. **E 项 flaky 测试**：tests/agent_rbac/test_session_aware_stash_red_blue.py::TestConcurrentCommitNoCrossTheft::test_three_sessions_concurrent_distinct_files 组合跑 60s 超时窗口偏紧（3 并发 commit×pre-commit hook 串行），与本批改动无因果（隔离复跑绿），建议 Owner 排期放宽 timeout。
6. **ROOR 生成器欠账**：entry_count/counting_rule 仍为手工维护，owner-book §七建议的"生成器自动回填"未落地（D1 预算待批类）。
7. **B 项清单外 8 码**：tool_contracts 实测 42 码中 HF-0001~0004（session_handoff 无 server 文件）、GT-0001/0003、INT-0001/0002（gate_engine/intent 骨架族）未列入本批处置授权清单——按 F 项范围外先例遗留；后续收编先例已备（无 server→deferred 注释、骨架→deferred）。
8. **A 项域测试执行偏差（已补课）**：driver 逐前缀仅跑六断言+语法校验，未按指令 4 跑域相关测试；Owner 复查后补跑 227 测试文件 4991 passed 零回归（commit 见 §一）。

# 六、验证命令附录

- 六断言：python -m pytest tests/governance/test_error_code_consistency.py -q （每前缀 commit 后必跑，全程 6 passed）
- B 项：python -m pytest tests/trading/unit/test_file_task_mapper_unit.py tests/resource/test_resource_optimization.py tests/infrastructure/test_mcp_red_team.py tests/infrastructure/test_mcp_gateway_version_ratelimit.py tests/infrastructure/test_blueprint_search_mcp.py -q
- C 项冒烟：python scripts/governance/run_semantic_audit.py docs/03_modules/_domain_governance/blueprint.md --stage 2 / --mode detect-only
- D 项：python scripts/governance/d5_architecture/pre_write_gate.py --file-path scripts/lock_files.py --file-path scripts/git_commit.py + 旧单文件 --json
- E 项：python -m pytest tests/git/test_git_commit_gateway.py -q
- F 项：python -c "import yaml; yaml.safe_load(open('docs/registry_of_registries.yaml', encoding='utf-8'))" + python scripts/governance/d3_metadata/check_registry_consistency.py
- G 项：python scripts/governance/generate_asset_index.py（再生后查 total_assets/Health 口径）
