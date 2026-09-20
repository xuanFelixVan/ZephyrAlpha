---
title: "终极图书馆 · 总目类目表 v1（清单的清单）"
ttl: task_bound
completes_when: 十维度全量盘点完成且每维度"有清单件或立缺口"二选一；随总攻验收转正
date: "2026-09-21"
owner: "ZephyrAlpha-Owner"
session: "st-ulib-20260921"
---

# 总目类目表 v1 —— 清单的清单（图书馆地图的地图）

> **Owner 令（2026-09-21）**：图书馆包含的不只是管线和资产——门禁、git 提交通路上的一切设备、制度、规则，**整个项目所有方方面面**都要有清单。本件=全项目清单维度的总清，挖干判据=每一维度"有清单件"或"立缺口"二选一，无第三态。
> 状态标记：✅=已有清单件/真源（可直收）；⬜=缺清单（今夜总攻立）；🔁=已有但存在已立档漂移。

## A 制度类（→制度馆）

| # | 类目 | 清单件/真源 | 状态 |
|---|---|---|---|
| A1 | 宪法 | AGENTS.md（L0，≤300 行）+ agent_constitution_legacy_v1.md（归档全文） | ✅ |
| A2 | 规则 | docs/01_policies_and_standards/rules/trae_*.yaml **86 件**+rule_catalog+rule_ai_perception_index | ✅ |
| A3 | 裁定 | ruling_registry.yaml（#1..#384+，同 commit 原子登记制） | ✅ |
| A4 | 架构议题 | architecture_issue_registry.yaml（#ARCH-XXX **761 条**） | ✅ |
| A5 | 人机门位 | risk_tier_registry.yaml（域→tier→human_gate） | ✅ |
| A6 | 标准 | MTH-001..013+quality_standard.md+graph_quality_standard.md | ✅ |
| A7 | 政策/流程 | policies/（并行协调政策§10、67 号冲突三分法、施工 workflow、挖矿 SOP、数据源 onboarding）+SOP 九族 | ✅ |
| A8 | 冻结契约 | freeze_manifest.yaml（**38 条**跨层契约） | ✅ |
| A9 | 错误码 | error_code_registry.yaml（**788 条** ZA-XX-NNNN） | ✅ |
| A10 | 词汇 | 术语三层（terminology/functional_domain 83 域/module_translation）+field_dictionary **257**+target_layer_vocabulary | ✅ |

## B 门禁与提交链设备（→闸门馆，Owner 点名"git 路上所有设备"）

| # | 设备 | 清单件/真源 | 状态 |
|---|---|---|---|
| B1 | pre-commit 门禁 | .pre-commit-config.yaml（**55 hooks**） | ✅ |
| B2 | in-process 门禁 | in_process_gate_registry.yaml（**113**，SSoT）+commit_gates/*.py GateSpec | ✅ |
| B3 | 会话/管线门禁 | rule_enforcement/_registry.yaml（**91** G1..G_FWD_REF，独立家族） | ✅ |
| B4 | 门禁聚合视图 | gate_registry.yaml（170，generate_gate_registry 三源生成，reconciler 830 重生成） | ✅🔁（169≠170+PG 289 已立档） |
| B5 | fail-open 放行点 | fail_open_register.yaml（**1,635 点/272 文件**，纯派生） | ✅ |
| B6 | noqa 豁免 | catalogs 版 28 marker+config/governance 版 92 file | ✅🔁（同名异构已立档） |
| B7 | tracked 写白名单 | gate_tracked_write_allowlist.yaml（11，A/B/C 三类） | ✅ |
| B8 | 提交网关 | scripts/git_commit.py（唯一合法入口：串行锁+stash 隔离+GW 标记+15 逃生旗） | ✅ 源码即真源 |
| B9 | 提交队列 | scripts/commit_queue.py+serializer+死信台账（done 1,056/dead 95/快照袋） | ✅ |
| B10 | 锁与 claim | scripts/lock_files.py+.ailocks/（claim/SALVAGE/TTL 30min） | ✅ |
| B11 | 会话注册与心跳 | SessionRegistry+heartbeat（claim_file 自动注册+活性窗） | ✅ |
| B12 | worktree 工棚 | scripts/session_worktree.py（create/exec/merge/abort）+.worktrees/ | ✅ |
| B13 | 提交后守卫 | POST-COMMIT-GUARD+post_commit_guard.sh（[GW:] 伪造回滚） | ✅ |
| B14 | 对账 reconcilers | d8_doc_sync 六 reconciler+priority 编制（如 830）+reconcile_generators 26 条 | ✅ |
| B15 | 写入 CAS | safe_write_text/atomic_write（热文件 CAS+审计 jsonl） | ✅ |
| B16 | 设备总台账 | **无**——B1..B15 散在源码与 config，无一页总目录 | ⬜→今夜 D7 建台账 |

## C 安全设备（→闸门馆）

| # | 设备 | 清单件/真源 | 状态 |
|---|---|---|---|
| C1 | LLM 安全网关 | LSGSecurityGateway+config（裸调被 GATE-20+运行时拦截器双捕） | ✅ 文件在/⬜ 无独立清单页 |
| C2 | KillSwitch | zephyr.security.access_control.kill_switch | ✅ 文件在/⬜ 同上 |
| C3 | 红蓝对抗 | REG-RB-001（**24 场景**）+REG-RB-002（**44 条款**） | ✅ |
| C4 | 密钥治理 | secrets.py 三道 gate+SECRETS.md+SECRET-REGISTRY-DRIFT 检测（REDIS 三键缺失已报） | 🔁 检测报缺已立档 |

## D 代码资产（→代码馆）

| # | 类目 | 清单件 | 状态 |
|---|---|---|---|
| D1 | 模块/文件依赖 | depgraph PG **12,107 节点/23,686 边**（module 3,854/test 3,551/config 3,503/script 1,088/blueprint 101） | ✅🔁（ROOR 旧数 9,148 已立档） |
| D2 | 脚本 | script-manifest **991**+governance 子集 **434** | ✅ |
| D3 | 蓝图 | PG blueprint_links 101+蓝图体系（w14 口径 542） | ✅ |
| D4 | 模块 ID/修复器/模式库 | module_id_registry 74/fixer_map 11/pattern_index 15 | ✅ |
| D5 | schema/迁移 | schemas/categories 树+migrations | ✅ |

## E 数据与量化资产（→数据馆）

| # | 类目 | 清单件 | 状态 |
|---|---|---|---|
| E1 | CH 表/源/通道/质量 | data_asset_registry（OpenLineage 式）+data_sources_registry+known_data_gaps+哨兵 yaml；**CH 246 表行数/新鲜度=待采集** | ✅ 仓内/⬜ CH 采集器（今夜 B2） |
| E2 | 因子/策略/指标/形态 | factor 175/strategy 161/indicator 138/pattern 254/DAL | ✅ |
| E3 | 风控/组合/模型/实验 | risk_limit 117/portfolio_model 8/model 8/experiment/backtest_backlog 135 | ✅ |
| E4 | 交易基础数据 | universe 6/benchmark 9/cost/seats 15/event 12/macro 15/cycle 12/compliance 6/execution_algo 6 | ✅ |
| E5 | 字段字典 | field_dictionary 257（PIT/复权口径） | ✅ |

## F 管线与决策（→管线馆）

| # | 类目 | 清单件 | 状态 |
|---|---|---|---|
| F1 | 决策图 | TDM yaml 138/194+PG decisiongraph 213/211+decision_tracks | ✅🔁（两图口径未声明已立档） |
| F2 | 作战地图 | battle_map PG 341 步/114 边 | ✅ |
| F3 | 数据血缘 | dataflow PG 1,757 jobs/76 datasets/90 edges | ✅ |
| F4 | 蓝图路由/生产图/GOM | blueprint_routing 19/strategy_production_map/governance_operations_map | ✅ |
| F5 | 调度与排班 | tasks.yaml+排班三表一入口+skeleton_health 电表（138 节点接电态） | ✅ |
| F6 | 资源画像 | resource_profile_registry 74 实体（=计划任务中央登记候选） | ✅ |

## G 运行时设备（→管线馆）

| # | 设备 | 清单件 | 状态 |
|---|---|---|---|
| G1 | MCP | tool_contracts 12 server/64 tools（契约 SSoT）+config/mcp.json 12 注册+ACL 三角色 | ✅🔁（文件系统 19 server vs 契约 12 双向漂移已立档） |
| G2 | 模型路由/嵌入 | model_routing_policy+embedding_model_registry 4 | ✅ |
| G3 | 守护/看门狗 | daemon_registry 能力卡+qmt_watchdog+bdpan_tick_watch | ✅ 卡在/⬜ 台账页待建 |
| G4 | 服务 | services_registry（api 8890/serve_docs 8765/dashboard） | ✅ |
| G5 | 计划任务 | 系统侧 44+1 实测+21 个 register_*.ps1+4 OneShot 残留+3 手工+Startup .lnk | ⬜ 台账层（今夜 D5，resource_profile 收编） |

## H 文档与知识（→文档馆）

| # | 类目 | 清单件 | 状态 |
|---|---|---|---|
| H1 | docs 手写文档 | directory_registry 88+rule_catalog 256+d1 index 族 | ✅ |
| H2 | 全景图 | 十图口径（align_all）+graph_quality_standard | ✅ |
| H3 | SOP | 九族（backtest/construction/data_audit/data_ops/governance/mining/ops/review/tdm） | ✅ |
| H4 | 任务卡/验收证据 | recovered_task_cards 11 卡+acceptance/ 9 件 | ✅/⬜ acceptance 无清单 |
| H5 | 能力卡（渐进披露） | capability_cards **33**（REG-SKILL-001，ROOR 旧记 22 已立档） | ✅ |
| H6 | 语义知识库 | vector_memory 8 collections（decisions/code_context/lessons/knowledge/rules/blueprints/session_snapshots/execution_traces） | ✅ |

## I 基建与备份（→基建与备份馆）

| # | 类目 | 清单件 | 状态 |
|---|---|---|---|
| I1 | 基础设施 | infrastructure_registry 9 组件+services 部署形态 | ✅ |
| I2 | 备份链 | backup.ps1 六阶段+backup_config+asset_inventory（E: 117.6G 冷归档唯一副本在册） | ✅/⬜ F→G 镜像与 restore 演练缺（已呈批） |
| I3 | 盘与冷储 | D 系统/E 冷储/F zephyr_cold/G 9 万研报/bdpan（3.19 亿行回补在册） | ✅ 登记/⬜ 实盘核对 |
| I4 | 数据库实例 | PG depgraph 73 表+CH 246 表+DuckDB（DatabaseService） | ✅/⬜ 实例级台账待建 |
| I5 | 杂项资产 | models/ 69+vendor/ 138+tools/ 937 | ⬜ 白名单外补录（血肉矿） |

## J 运行时态与审计（→运行时区，半开：台账型入馆，堆积型只计指标）

| # | 类目 | 清单件 | 状态 |
|---|---|---|---|
| J1 | 活性台账 | data/runtime/ 6 json（strategy_decay/indicator_usage/factor/pattern_lifecycle/strategy_registry_snapshot 等，实时刷新） | ✅ |
| J2 | 资源采样 | logs/resource_samples 11 jsonl | ✅ |
| J3 | 审计流 | governance.db+reconcile_execution_log+lookup_audit 305+hook_tracked_drift.jsonl+safe_write 审计 | ✅ |
| J4 | 告警 | alert_threshold_registry 36+workspace_alerts+alert_webhook_trail | ✅ |
| J5 | 堆积型 | commit_queue 3.7G/52k 文件、tmp 5.5 万文件、gate_cache 7.5k | ✅ 只计指标不建清单 |

## §2 缺口汇总（⬜ 共 9 处，全部落今夜总攻）

| 缺口 | 落点 |
|---|---|
| B16 提交链设备总台账 | 今夜 D7 闸门链馆 |
| C1/C2 LSG/KillSwitch 清单页 | D7 顺带 |
| E1 CH 采集器 | B2 包 |
| G5 计划任务台账页（含 OneShot/手工/Startup） | D5 包 |
| I2 F→G 镜像+restore 演练 | 已呈 Owner 批（备份馆授权项） |
| I3 盘实核对 | D6 包 |
| I4 实例级台账 | D2/D6 包 |
| H4 acceptance 清单 | 血肉矿 |
| I5 白名单外补录 | 血肉矿 |

## §3 挖干判定（本件自身）

十维度 A-J 全量过堂：**有清单件 51 类，立缺口 9 类（全部有落点），无"未知类目"残留**。此后新增类目=增枝，须过停止判据三问并在本件补行留痕。
