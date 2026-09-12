---
module_id: SOP-CONSTITUTION-L0
doc_type: policy
doc_type_note: L0 候选宪法（#ARCH-310 R3）。切换验收通过后替换 AGENTS.md 正文，本文件转为真源。
ttl: permanent
title: ZephyrAlpha AI Agent 宪法 L0（≤300 行硬规则+索引）
version: 0.1.0-draft
status: candidate
cutover_plan: 见文末 §切换程序；索引卡真源=capability_cards/ L0-L3 渐进披露体系
---

# ZephyrAlpha — AI Agent 宪法 L0

> 本文件是唯一必读宪法。目标长度 ≤300 行（#ARCH-310 R3：规范总量与执行率负相关，
> 上下文是硬预算）。每个硬规则一行陈述+真源指针；细节按需检索，不预载。

## 0. 冷启动序列（按序执行，缺一不可）

1. **RULE-ENV**：`$env:PATH = "$env:LOCALAPPDATA\Programs\Python\Python312;...Scripts;" + $env:PATH`，
   验证 `python --version` = 3.12.x（TRAE 注入 3.10 会崩 `datetime.UTC`）。
2. **RULE-GUARDIAN**：`python scripts/lock_files.py cleanup && python -m zephyr.trading.process_reaper --status`。
   计划任务不存在 = 禁止任何写操作。长批任务先登记 `data/runtime/process_reaper_keep.txt` 防误杀(每行一个 cmdline 子串)。
3. **RULE-WORKTREE**：`session_worktree_start`（或按既定裁定降级走 `scripts/git_commit.py` 正门）。
   提交必经 GitCommitGateway / git_commit.py，禁止裸 `git commit`。
4. **RULE-CAPABILITY-LOOKUP**：写第一行业务代码前调
   `capability_lookup.find(<kw>, session_id=<sid>)` 或 MCP `rule_discovery`（写审计）。
5. **RULE-DEPGRAPH**：施工前 `apply_depgraph.py --add-design-node` 登记；文件重命名后
   `generate_project_depgraph.py --force`。
6. **RULE-REGISTRY**：查注册表先读 `docs/registry_of_registries.yaml`（ROOR，勿背数）。
7. **RULE-SSOT**：写数据前判真源方向——规则数据改 YAML 同步 DB；架构数据 apply_*.py 直写 DB。

## 1. 十二条硬规则（违反即硬阻断，无直觉例外）

| # | 规则 | 一行陈述 | 真源 |
|---|------|---------|------|
| 1 | RULE-ENV | Python 3.12 PATH 修正在任何 python 调用之前 | AGENTS.md §RULE-ENV（切换后=本文） |
| 2 | RULE-GUARDIAN | reaper 计划任务存活是写操作前提 | scripts/register_process_reaper_task.ps1 |
| 3 | RULE-WORKTREE | 隔离施工/正门提交，HELD-OVERLAP 不硬闯 | docs/.../policies/parallel_session_coordination_policy.md |
| 4 | RULE-DEPGRAPH | 先登记后施工；HIGH drift pre-merge 阻断 | trae_080_panorama_alignment.yaml |
| 5 | RULE-REGISTRY | 注册表发现唯一直 ROOR；数量勿写死 | docs/registry_of_registries.yaml |
| 6 | RULE-SSOT | 规则=YAML、架构=DB，机械判定禁止凭记忆 | trae_062_ssot_classification.yaml |
| 7 | RULE-DATA-OPS | 破坏性 DB 操作三步验证（必要性/真实性/可逆性） | trae_063_data_ops_discipline.yaml |
| 8 | RULE-RULING | 裁定#NNN 必须先登记 ruling_registry，同 commit 原子 | ruling_registry.yaml |
| 9 | RULE-CAPABILITY-LOOKUP | 施工前能力反查留审计；逃生走 [no-lookup:<白名单 reason>] | trae_065/trae_077 |
| 10 | RULE-SCHEMA-TZ | DateTime64(3)+显式时区；生成器禁 datetime.now()/time.time() | trae_065 时区批/AGENTS §11.1.1 |
| 11 | RULE-SECRETS | 密钥走 secrets.py，禁裸 getenv/硬编码（三道 gate） | SECRETS.md |
| 12 | RULE-GIT-SAFE | 危险 git 命令清单禁用；每轮修改即 git add；改前 claim | scripts/git_safety_wrapper.ps1 |
| 13 | 热文件写入 | 注册表/宪法/tracker 等热文件必用 `safe_write_text`（CAS 防并发覆盖，`src/zephyr/shared/io/file_utils.py`），禁裸 Edit/Write 后不复核；写后进程外核实 | file_utils.py |

补充铁律（同硬阻断级）：RULE-CLONEGUARD（extract 级克隆无逃生）；新建 .py 模块须登记大白话简介（`add_module_translation.py`，TRANSLATION-COVERAGE gate 拦截）；
RULE-WORKSPACE-WIP（脏文件先跑 classify_workspace_wip.py，禁肉眼判罚）；
CREATE-GUARD（新建 .py/.yaml/.md 等 7 格式须登记 creation_token，tests/ 豁免）。

## 2. 并发与提交（#ARCH-310 R1：队列是正门）

1. **提交一律走 `scripts/git_commit.py`**：`--session <sid> --files <清单>`。
2. **锁忙不要空转**：LOCK_TIMEOUT 自动改道入队（flag commit_queue_interactive）；
   需要同步语义时 `--no-auto-enqueue` 显式退出。
3. **失败重试带 `--adopt-prior-work`**（失败提交的 finally 释放 claim 但文件保持
   staged，不带 adopt 的重新 claim 会把 staged 差异判外来——FOREIGN_CHANGE 恶性循环）。
4. **gate+自家测试同批是合法的**：COMMIT_SCOPE 误判时用 `--allow-multi-domain`（留痕）。
5. **commit 后必做**：`git log -1 --name-only` 核实真实归属（暂存区可能吸收他会话内容）。
6. **多会话并发窗口**：优先 `--enqueue` 走队列（serializer worktree 干净暂存区，
   结构性免疫连坐）；直连与队列不要混抢。
7. 死会话 stale claim 挡道：`gateway.release_files('<死sid>', files)` 精准释放后重 claim。

## 3. 作用域与连坐（#ARCH-310 R2）

1. 内容扫描型 gate 默认 own-diff 作用域（`_diff_helpers._build_own_scope` 模式）；
   外来 staged 违规=warn+审计（`_audit_foreign_staged`），不阻断无辜提交人。
2. own_scope 标记见 `gate_registry.yaml` 的 `own_scope` 字段（机生，勿手改）。
3. 新 gate 必须 own-scope 或登记"全仓扫描"理由（结构校验型按 perf 方案 §2.6 分级）。
4. 他会话在途违规不代修：owner 责任制，等待其落地或按 WIP 判读铁律处置。

## 4. 规范预算与退役（#ARCH-310 R4）

1. 规范总量净零增长：新增规则/gate 须声明替代或合并的旧条目。
2. 退役审计：基于 reconcile_execution_log 触发率，季度执行（gate 触发率持续近零→降级/退役）。
3. 文档纪律：计数用字段（`total_gates`/`total_registries`）不写死在散文；
   文档矛盾=事故（对齐清单/perf plan 自相矛盾案例在案）。

## 5. 人机门位（#ARCH-310 R5）

1. 门位注册表：`risk_tier_registry.yaml`（域→tier→human_gate；未列出域默认 low）。
2. high 域门位：production 流转 / 注册表净删 / flag 出厂翻转 / 资金破坏性操作 → Owner。
3. medium/low 全自动；门禁强度由 gate 体系独立保证，分级不放松 gate。

## 6. 上下文预算（#ARCH-310 约束②）

1. 本宪法 ≤300 行是硬上限；新增内容必须等长替换。
2. 细节检索序：capability_cards/（L0-L3 渐进披露）→ docs/01.../rules/*.yaml →
   capability_canonical_file_registry.yaml → Grep 符号发现。
3. 会话内不复制大段规则进上下文；引用真源路径+锚点。

## 7. 核心系统速查（细节按需检索）

| 系统 | 入口 |
|------|------|
| AutoRuntime Core | `python -m zephyr.trading` |
| GitCommitGateway | `zephyr.gov_enforcement.rule_bridge.git_commit_gateway`（唯一合法 commit 入口） |
| 提交队列 | `scripts/commit_queue.py`（enqueue/status/drain/requeue；drain=真落地） |
| DatabaseService | `zephyr.infrastructure.database_service`（唯一真源，禁裸 duckdb） |
| LSG | `zephyr.security.llm_defense.llm_security.gateway`（所有 LLM 调用必经） |
| CapabilityLookup | `zephyr.governance.capability_lookup` |
| KillSwitch | `zephyr.security.access_control.kill_switch` |
| 数据集成器 | `python -m zephyr.data`（7 子命令） |
| 仪表盘 | `src/zephyr/frontend/dashboard/app_panel.py` |

## 8. 词汇与对齐

- 八图对齐：`alignment_checklist.md`（对齐键=module_id/step_id；`align_all.py` 单入口）。
- 业务资产库 16 表挂 TDM 交叉轴（`_XREF_SPECS` 表驱动）；新库/新图挂接义务见该表 §4。
- 术语三层：terminology_glossary.yaml（术语）/ functional_domain_registry.yaml（域）/
  module_translation_registry.yaml（模块）——生成器输出经 loader，禁硬编码翻译。

## 切换程序（本文件转正流程）

1. 本文件通过红蓝对抗 + 新会话冷启动烟囱测试（新 session 只读本文件完成一次真实
   小型施工，全 gate 通过）。
2. AGENTS.md 正文替换为本文件 + 一节"历史规则索引"（指向 rules/*.yaml 原文，
   零内容删除只重排）。
3. 回滚=git revert 单 commit。
4. 完成定义：连续两个新会话冷启动施工零宪法相关阻断。
