---
ttl: task_bound
completes_when: 孤儿分诊战役终裁落地（chief 终审+处置执行）后本册随 30/31 号转归档
title: 孤儿分诊证据包：小簇合并册 misc_general（15 簇 27 台）
owner: st-orphtriage-20261004
---

# 41 号·小簇合并册：misc_general（15 簇 27 台）

> 宇宙口径=裁定#481；数据真源=30_attribution_table.yaml；处置=建议非终裁。
>
> 合并初判汇总：dispute=1，mount=26

### 簇 scripts.__init__.py（1 台；初判 mount=1）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `scripts/__init__.py` | （无文档头，按文件名语义：__init__） | 2026-06-21（105天） | in=1/out=0·wired | **mount**→chief 判（域 __init__.py 无预设映射）（活线在身未挂线） |

### 簇 scripts.ch（4 台；初判 mount=4）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `scripts/ch/apply_pattern_certification_ddl.py` | market_pattern_certification 建表 DDL 部署 + 验证脚本（MOD-SIG-148 W-CB）。 | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 ch 无预设映射）（活线在身未挂线） |
| `scripts/ch/apply_pattern_event_ddl.py` | market_pattern_event 建表 DDL 部署 + 验证脚本（MOD-SIG-145 W1）。 | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 ch 无预设映射）（活线在身未挂线） |
| `scripts/ch/apply_pattern_win_rate_ddl.py` | market_pattern_win_rate 建表 DDL 部署 + 验证脚本（MOD-SIG-145 W3）。 | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 ch 无预设映射）（活线在身未挂线） |
| `scripts/ch/apply_signal_history_ddl.py` | market_signal_history 建表 DDL 部署 + 验证脚本（#BT-PIPELINE-001 阶段三）。 | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 ch 无预设映射）（活线在身未挂线） |

### 簇 scripts.check_naming_convention.py（1 台；初判 mount=1）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `scripts/check_naming_convention.py` | （无文档头，按文件名语义：check_naming_convention） | 2026-08-03（62天） | in=1/out=0·wired | **mount**→chief 判（域 check_naming_convention.py 无预设映射）（活线在身未挂线） |

### 簇 scripts.clone_guard_audit.py（1 台；初判 mount=1）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `scripts/clone_guard_audit.py` | CloneGuard L2 周期审计触发脚本（事件驱动，非 cron）。 | 2026-08-21（44天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 clone_guard_audit.py 无预设映射）（活线在身未挂线） |

### 簇 scripts.compute_signals.py（1 台；初判 mount=1）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `scripts/compute_signals.py` | 日频因子信号计算器（管道 B，#BT-PIPELINE-001 阶段三）。 | 2026-09-02（32天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 compute_signals.py 无预设映射）（活线在身未挂线） |

### 簇 scripts.estimate_pit_backfill_cost.py（1 台；初判 mount=1）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `scripts/estimate_pit_backfill_cost.py` | estimate_pit_backfill_cost.py — llm_premarket_analysis PIT 回填成本 dry-run 估算（44号 §9.14） | 2026-09-02（32天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 estimate_pit_backfill_cost.py 无预设映射）（活线在身未挂线） |

### 簇 scripts.industry_graph（10 台；初判 mount=10）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `scripts/industry_graph/execute_r1_chain_plans.py` | R1 链级治理方案执行器（Owner 2026-09-08 预审批准的四方案，链级处置）。 | 2026-09-18（16天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 industry_graph 无预设映射）（活线在身未挂线） |
| `scripts/industry_graph/fix_s6_s7_nodes.py` | S6 tier 方案落地 + S7 后缀名剥离合并治理脚本。 | 2026-09-18（16天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 industry_graph 无预设映射）（活线在身未挂线） |
| `scripts/industry_graph/migrate_roles.py` | S10 role 归一治理脚本（Owner 2026-09-09 五值裁定：龙头/核心/主要/参与/提及）。 | 2026-09-18（16天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 industry_graph 无预设映射）（活线在身未挂线） |
| `scripts/industry_graph/migrate_tier_to_function_role.py` | tier 职能化迁移治理脚本（Owner 2026-09-09 v0.4 裁定）。 | 2026-09-18（16天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 industry_graph 无预设映射）（活线在身未挂线） |
| `scripts/industry_graph/quality_fix_p0.py` | Phase2 P0 污染源清除治理脚本（SOP §12.3 优先级1，SOP v1.5.0）。 | 2026-09-18（16天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 industry_graph 无预设映射）（活线在身未挂线） |
| `scripts/industry_graph/quality_fix_p2.py` | P2 合规修复 + P1 尾项综合治理脚本（子命令，全幂等）:: | 2026-09-18（16天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 industry_graph 无预设映射）（活线在身未挂线） |
| `scripts/industry_graph/ths_equity_hk_refill.py` | hk_stock_list 在库真源的名称精确匹配(禁凭记忆/禁模糊 LIKE); 同名多 code 命中>1 留缺口 | 2026-09-14（20天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 industry_graph 无预设映射）（活线在身未挂线） |
| `scripts/industry_graph/ths_equity_import.py` | THS 被投清单导入 ig_equity_edge（Owner 2026-09-09 裁定执行）。 | 2026-09-18（16天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 industry_graph 无预设映射）（活线在身未挂线） |
| `scripts/industry_graph/ths_import.py` | ths_import.py — R3b 宽度铺面施工件(SOP §6 第3轮 R3b,夜班指令书第1优先)。 | 2026-09-11（23天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 industry_graph 无预设映射）（活线在身未挂线） |
| `scripts/industry_graph/vocab_loader.py` | 产业链图谱词表加载器（字段字典单一真源的消费入口，Owner 2026-09-10 方案 A）。 | 2026-09-19（15天） | in=4/out=0·wired | **mount**→chief 判（域 industry_graph 无预设映射）（活线在身未挂线） |

### 簇 scripts.ml（1 台；初判 mount=1）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `scripts/ml/run_sft_train.py` | run_sft_train.py — P1-E3 Phase 4: 执行 LoRA SFT 训练 + F1 评估。 | 2026-08-24（41天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 ml 无预设映射）（活线在身未挂线） |

### 簇 scripts.post_checkout_guard.py（1 台；初判 mount=1）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `scripts/post_checkout_guard.py` | Post-checkout Guard — 事后检测 checkout 是否覆盖了其他 session 的文件锁。 | 2026-09-29（5天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 post_checkout_guard.py 无预设映射）（活线在身未挂线） |

### 簇 scripts.print_exam_summary.py（1 台；初判 dispute=1）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `scripts/print_exam_summary.py` | 输出所有模型考试成绩清单（中文版） | 2026-08-21（44天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 44 天内有 commit（活着但零线零引）；①mount→chief 判（域 print_exam_summary.py 无预设映射） ②retire→Owner 门位） |

### 簇 scripts.scan_forward_days.py（1 台；初判 mount=1）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `scripts/scan_forward_days.py` | scan_forward_days.py — P2-E8: forward_days 参数扫描（13 号 §4.2）。 | 2026-08-21（44天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 scan_forward_days.py 无预设映射）（活线在身未挂线） |

### 簇 scripts.serve_docs.py（1 台；初判 mount=1）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `scripts/serve_docs.py` | 本地文档服务：按需重生成派生架构文档 + 启动 HTTP 服务器浏览。 | 2026-09-07（27天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 serve_docs.py 无预设映射）（活线在身未挂线） |

### 簇 scripts.setup_dev_env.py（1 台；初判 mount=1）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `scripts/setup_dev_env.py` | 开发环境一次性初始化（裁定 #ARCH-PYTHON-SITECUSTOMIZE）。 | 2026-07-23（73天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 setup_dev_env.py 无预设映射）（活线在身未挂线） |

### 簇 scripts.setup_git_guard_aliases.py（1 台；初判 mount=1）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `scripts/setup_git_guard_aliases.py` | Setup/Remove Git Aliases for Git Guard — 自动化集成入口。 | 2026-08-21（44天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 setup_git_guard_aliases.py 无预设映射）（活线在身未挂线） |

### 簇 scripts.verify_sentiment_hidden_driver.py（1 台；初判 mount=1）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `scripts/verify_sentiment_hidden_driver.py` | 情绪周期"隐形驱动"验证脚本（28 号 memo §3.7.4，G07 施工前必做）。 | 2026-09-13（21天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 verify_sentiment_hidden_driver.py 无预设映射）（活线在身未挂线） |
