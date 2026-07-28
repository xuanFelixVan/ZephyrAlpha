---
ttl: task_bound
completes_when: P0-P2 全阶段升级建设完成，audit_03 复评总分≥90%（A-）
source: docs/临时文件.md（2026-07-28 由 docs/ 根重命名迁移至此；原中文文件名违反 snake_case 约束，按 _working 命名规则加日期前缀；doc_type 字段因 EXEMPT-ZONE-FM gate 禁止豁免区文件携带而省略）
generated_at: 2026-07-22
---

# 任务：ZephyrAlpha 回测数据库机构级升级建设（P0→P2 全阶段）

你是 ZephyrAlpha 项目（D:\ZephyrAlpha）的高级数据架构工程师。本次任务依据 2026-07-22 完成的机构级数据库审查（总评 81.3% B+）执行全量升级建设。审查证据文档（含逐条文件路径+行号证据，施工前必须先读）：

- docs/02_enterprise_architecture/code_wiki/audit_01_schema_review.md（101 张 ClickHouse 表逐表 schema 审查）
- docs/02_enterprise_architecture/code_wiki/audit_02_pipeline_review.md（数据管线审查）
- docs/02_enterprise_architecture/code_wiki/audit_03_checklist_and_verdict.md（64 项检查清单与总评）
- docs/02_enterprise_architecture/code_wiki/ext_01_depgraph_docs_review.md 与 ext_02_arch_docs_review.md（战略缺口）

审查假设：数据库仅用于回测（单人使用），实盘就绪度不属本期范围。

==================================================
## 第零阶段：合规启动序列（任何写操作前必须完成，顺序不可乱）
==================================================
1. 环境对齐（TRAE shell 会注入内置 Python 3.10 到 PATH 最前，必须先纠正）：
   $env:PATH = "$env:LOCALAPPDATA\Programs\Python\Python312;$env:LOCALAPPDATA\Programs\Python\Python312\Scripts;" + $env:PATH
   验证：python --version 输出 Python 3.12.x。cwd 必须是 D:\ZephyrAlpha。
2. 守护进程（未运行 = 禁止一切写操作）：
   python scripts/lock_files.py cleanup
   python scripts/ide_health_service.py --status  → running=false 则 python scripts/ide_health_service.py --start-background
3. 启动健康检查（15 项，失败必须 [ESCALATION] 上报，禁止静默 workaround）：
   python scripts/governance/session_startup_health_check.py
4. worktree 隔离：
   PYTHONPATH=src python -c "from zephyr.gov_enforcement.rule_bridge.session_worktree import session_worktree_start, generate_session_id; sid = generate_session_id(); print(sid); print(session_worktree_start(sid))"
   记住 sid 全程使用。若返回 WORKSPACE_DRIFT_BLOCKED（其他并发会话残留），按 TRAE-079 Phase 2 降级走 GitCommitGateway（scripts/git_commit.py），绝不清理/还原他人改动。
5. 读规则真源：AGENTS.md 中 RULE-DEPGRAPH / RULE-SSOT / RULE-DATA-OPS / RULE-RULING / RULE-CAPABILITY-LOOKUP 五节（拿不准就 Read docs/01_policies_and_standards/rules/ 下对应 trae_*.yaml，禁止凭记忆推断）。

==================================================
## 第一阶段：治理登记（施工前置）
==================================================
1. 在 docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml 登记 4 个架构议题（连续编号，ClickHouse 域续 #ARCH-CH-021 起；条目含 issue_id/title/severity/adjudication/fix_phase/status=open/created/last_updated）：
   - #ARCH-CH-021：回测数据有效性 P0 包（本任务阶段二）
   - #ARCH-CH-022：Schema 真源体系收口（本任务阶段三 A 组）
   - #ARCH-DATA-PIPELINE-001：管线韧性包（本任务阶段三 B 组）
   - #ARCH-DR-BACKUP-001：灾备与治理登记包（本任务阶段三 C 组）
   引用这些编号的文件必须与 registry 在同一 commit 提交。
2. 写第一行 src/zephyr/**/*.py 前必须完成能力反查（commit 硬阻断 priority=110）：
   调 MCP rule_discovery.discover_applicable_rules(operation='file_write')，或 PYTHONPATH=src python -c "from zephyr.governance.capability_lookup import CapabilityLookup; print(CapabilityLookup().find('<关键字>', session_id='<sid>'))"，确认审计落盘 .runtime/lookup_audit/<sid>.jsonl。
3. 每个新模块施工前登记 depgraph 设计态：python scripts/governance/apply_depgraph.py --add-design-node <路径> <BLUEPRINT_ID> <DOMAIN_ID> planned；完工验证后 --transition-build-status <NODE_ID> production。新建 .py/.yaml 前先在 capability_canonical_file_registry.yaml 的 creation_tokens 段登记（CREATE-GUARD 硬阻断）。新 .py 必须带十五字段治理锚定表头（trae_047），文件名 snake_case，UTF-8 无 BOM、LF 换行，open() 必带 encoding='utf-8'。

==================================================
## 第二阶段：P0 回测正确性修复（#ARCH-CH-021，最优先）
==================================================
⚠️ 红线：任何破坏性 DB 操作（DELETE/REPLACE PARTITION/重建表/迁移数据）前必须执行 trae_063 三步验证——①必要性（根因+能否非破坏性替代）②真实性（必须看具体数据，重复验证用全字段 GROUP BY HAVING count()>1，禁用 count()-uniqExact(排序键)）③可逆性（先备份，无备份=禁止执行）。ClickHouse 备份用 scripts/backup/ 现有管线或 ALTER TABLE ... FREEZE/导出快照。

P0-1 幸存者偏差（头号缺陷）：stock_list 5,534 只全为在市股。接入 Tushare/iFind 退市主数据，回填 A 股历史退市股全量清单；stock_list 改造为含 list_status + delist_date + valid_from/valid_to 的时点版本表（SCD-2）；新建/改造任务登记进 data_sources_registry.yaml 与 tasks.yaml；对接 config/data/survivorship_policy.yaml 使声明级 gate 在数据层兑现。
P0-2 tick 数据缺口：实测 2026-06 日均 248 万行 vs 5 月日均 2,385 万行（-90%，21 个交易日）。先诊断根因（miniqmt/QMT 链路、7-16 Hyper-V 迁移窗口），出具诊断结论；再通过 backfill_checker 既有机制回补 6 月缺口并做回补后行数闭合验证。
P0-3 option_iv_surface 排序键缺 option_type：call/put 互相覆盖静默丢数据。完成备份后重建表（排序键加 option_type），迁移历史数据并做迁移前后行数对账，更新 schemas/categories/ 对应 DDL-as-Code 真源与 business_data_categories.yaml。
P0-4 质量门有壳无芯：data/quality_gate.py 仅 27 行 re-export、写入路径零消费方、quality_flag 全库恒为 1。实现轻量异常值校验器（OHLC 逻辑/涨跌幅/缺口/复权四条门禁），接入 ch_writer 写入路径，quality_flag=0 为保真标记（默认 1 语义反转为"已校验通过"需全链路对齐并写入裁定），配套测试。
P0-5 财报 PIT 化：c3 财务报表 ReplacingMergeTree 覆盖式更新存在前视偏差。按 announce_date 建立 point-in-time 查询能力（AS OF 语义或快照分区），与 backtest 域 pit_manager.py 的三公理（as_of_join/embargo/survivorship）对齐。
P0-6 18 张缓变维表时点版本化：stock_list 等补 valid_from/updated_at（或等效 SCD-2 机制），消除"回测用含未来新股的当前股票池"的前视通道。清单以 audit_01 为准。
P0-7 index_quote 生命周期真源冲突：注册表 hot_90d vs 蓝图 INV-RET-003 永久保留。立即对齐真源为永久保留，并全库排查同类 lifecycle 冲突。
P0-8 c3 八张裸 MergeTree 表（analyst_forecast/disclosure_plan/equity_pledge_detail/industry_class_suppl/restricted_shares/rights_issue/share_change/share_unlock）：备份后迁移为 ReplacingMergeTree（落实 #ARCH-CH-002 裁定），消除写前 DELETE 路径。

==================================================
## 第三阶段：P1 数据资产与管线可靠性（三组可并行，#ARCH-CH-022 / #ARCH-DATA-PIPELINE-001 / #ARCH-DR-BACKUP-001）
==================================================
A 组 Schema 治理：
- ingest_ts 版本列从 17/101 补齐到全覆盖（#ARCH-CH-009 断链闭环：裁定-蓝图-真源-实例四层对齐）
- DDL-as-Code 真源从 10/101 扩面（优先行情主表与 c3 全表），建设蓝图规划的 apply_schema.py 部署链路（6 张有真源无部署链的表先接通）
- kline_daily 三处真源漂移对齐（amount 类型/market_type 默认值/data_source 默认值，以实测为准回写真源）
- 分钟 K 线族 15 张表族内对齐（OHLC 精度统一 18,6、volume 统一 UInt64、分区基准列统一），tasks.yaml 幂等键与分区键错配修复
- 财务表 20+ 金额字段 Float64 → Decimal(18,2/4) 化（含数据迁移对账）
- 时区防线：全库 DateTime 统一 DateTime64(3, 'Asia/Shanghai') 或显式时区列，消除 UTC/北京时间混存
- 复权体系补原始价层（raw OHLC）+ adj_factor 与 kline_daily 内嵌因子类型统一（Decimal(18,8)）
- 行情表补 currency 列（港美股已摄取）
B 组 管线韧性：
- fallback_sources 覆盖从 8/128 扩到 ≥50%（优先 miniqmt 单源任务配 akshare/tdx 副源）
- 卡死 RUNNING >24h 任务治理机制（自动检测+重置+告警）
- error_classifier 规则扩充：akshare 接口漂移（has no attribute）、xtquant 断连归类为明确错误类并配正确动作（切源/暂停而非反复重试）
- 消除 task_id 重复（kline_us_daily_incremental ×2 共享断点主键）
- 修复 l2_tick 表不存在但任务引用（建表或摘除任务）
- 打通告警通道：钉钉/邮件 NotImplementedError → 实装（密钥走 .env，禁止入库）
- 空表漏检修复：阈值为 0 的表不再被巡检跳过（显式"应空"白名单机制），恢复 edb_data/realtime_snapshot/sector_snapshot 采集或摘除
- cls/eastmoney_news 补登记进 data_sources_registry.yaml（消除逆向漂移）
C 组 治理与灾备：
- dr_policy.yaml 登记 302 GiB 行情仓库的 RTO/RPO
- lifecycle hot_90d 声明落地为 CH TTL（或修声明，二选一闭环）
- 执行一次真实备份恢复演练并留验证记录；评估备份盘容量（315 GiB vs 数据 318 GiB 月增 5-6 GiB）给出扩容/保留策略方案

==================================================
## 第四阶段：P2 性能与工程卫生
==================================================
- 高频查询路径建物化视图/Projection（替代 kline_resampler 物理表 DELETE+INSERT 等价方案的可行性评估与试点）
- 评估 tick 排序键 market_type 前缀对单票裁剪的影响，给出改造或接受结论（改造需走 P0 级备份流程）
- 240 处历史硬编码表名替换为注册表引用
- redundant_source（MOD-L00-005）四组件接线到下载主链路，或登记降级决议
- pyproject.toml 补声明 clickhouse-driver / baostock（幽灵依赖，对标 python-dotenv 历史事故）
- 清理 kline_daily 残留脏数据（1970-01-01 symbol 空行，走三步验证）

==================================================
## 提交与验收纪律
==================================================
1. 提交唯一链路：session_worktree_commit(sid, [文件清单], 'type(scope): desc')，完工 session_worktree_merge(sid)；降级路径用 scripts/git_commit.py --session <sid> --files <清单> --message-file <文件>（永久区新文件加 --allow-promote）。禁止裸 git commit / git commit --no-verify。
2. 每阶段一个 commit（或按议题分组），commit message 引用对应 #ARCH 编号。
3. 每阶段验收：python scripts/governance/run_all.py --depth quick 通过；python scripts/governance/audit_registration.py exit 0；受影响表提供施工前后行数/抽样对账记录。
4. 关门：python scripts/lock_files.py status 无残留；临时文件零残留。
5. 总验收标准：对照 audit_03 的 64 项检查清单复评，阶段二+三完成后质量执行与存储精细度分项从 75% 提升到 ≥90%，总分 ≥90%（A-）。
6. 工具/门禁/数据库连接故障一律 [ESCALATION] 上报并停止相关分支，禁止静默 workaround；多并发会话环境下绝不修改/还原/删除不属本任务的文件。
7. 最终交付：施工总结报告（放 docs/_working/reports/，ttl=task_bound），含每 P0/P1/P2 项的处置结果（已修/改期/放弃+理由）、对账记录、复评得分。
