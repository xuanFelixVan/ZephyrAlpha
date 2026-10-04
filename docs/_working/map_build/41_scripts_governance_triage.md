---
ttl: task_bound
completes_when: 孤儿分诊战役终裁落地（chief 终审+处置执行）后本册随 30/31 号转归档
title: 孤儿分诊证据包：scripts.governance（42 台）
owner: st-orphtriage-20261004
---

# 41 号·分诊证据包：scripts.governance（42 台）

> 宇宙口径=裁定#481；数据真源=30_attribution_table.yaml（join checker 机生）；处置=证据班建议，终裁归 GLM-5.3 chief，退役执行归 Owner 门位。
>
> tier 分布：suspect_orphan=7，wired=11，wired_by_header=24；初判汇总：dispute=7，mount=35

## 逐台证据（四字段+初判）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `scripts/governance/_shared/registry_batch_edit.py` | registry_batch_edit re-export 壳——真源单一（scripts/governance/registry_batch_edit.py）。 | 2026-09-13（21天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 21 天内有 commit（活着但零线零引）；①mount→GOMAP（治理/安全域） ②retire→Owner 门位） |
| `scripts/governance/_tasks/__init__.py` | （无文档头，按文件名语义：__init__） | 2026-07-02（94天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 94 天内有 commit（活着但零线零引）；①mount→GOMAP（治理/安全域） ②retire→Owner 门位） |
| `scripts/governance/d11_compliance/__init__.py` | （无文档头，按文件名语义：__init__） | 2026-06-21（105天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 105 天内有 commit（活着但零线零引）；①mount→GOMAP（治理/安全域） ②retire→Owner 门位） |
| `scripts/governance/fullflow/__init__.py` | fullflow/ — 全流通战役机生尺（静态清单/对账表自动生成器） | 2026-09-28（6天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 6 天内有 commit（活着但零线零引）；①mount→GOMAP（治理/安全域） ②retire→Owner 门位） |
| `scripts/governance/query_candidate_registry.py` | 候选模块登记表查询工具。 | 2026-08-20（45天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 45 天内有 commit（活着但零线零引）；①mount→GOMAP（治理/安全域） ②retire→Owner 门位） |
| `scripts/governance/scan_offrepo_assets.py` | 仓外资产扫描器（Off-repo Asset Scanner） | 2026-09-18（16天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 16 天内有 commit（活着但零线零引）；①mount→GOMAP（治理/安全域） ②retire→Owner 门位） |
| `scripts/governance/vms/__init__.py` | （无文档头，按文件名语义：__init__） | 2026-07-02（94天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 94 天内有 commit（活着但零线零引）；①mount→GOMAP（治理/安全域） ②retire→Owner 门位） |
| `scripts/governance/__init__.py` | （无文档头，按文件名语义：__init__） | 2026-06-21（105天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `scripts/governance/_shared/__init__.py` | （无文档头，按文件名语义：__init__） | 2026-06-21（105天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `scripts/governance/_shared/algo_flow_applier.py` | algo_flow_applier.py — ALGO_FLOW 校准标记集中应用器（半自动落地步骤③配套）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `scripts/governance/_shared/algo_flow_drafter.py` | algo_flow_drafter.py — ALGO_FLOW 草稿生成器（半自动落地步骤①）。 | 2026-08-20（45天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `scripts/governance/_shared/algo_flow_validate_marker.py` | algo_flow_validate_marker.py — ALGO_FLOW 校准标记质量校验器。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `scripts/governance/_shared/code_algorithm_extractor.py` | code_algorithm_extractor.py — 模块核心算法提取器（派生逻辑真源）。 | 2026-09-17（17天） | in=5/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `scripts/governance/_shared/frontmatter.py` | 文件头部格式解析 SSoT（Single Source of Truth） | 2026-08-20（45天） | in=5/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `scripts/governance/audit_return_contract_usage.py` | audit_return_contract_usage.py — 返回契约 ok 键调用方审计（P2-5，2026-07-19） | 2026-08-20（45天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `scripts/governance/blob_gc.py` | blob_gc.py — blobs 内容寻址存储的归档式 GC（QMine M4 承重件；默认 dry-run，归档不删除）。 | 2026-09-25（9天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `scripts/governance/check_meta_question_batch.py` | check_w6_batch — W6 问题批次 JSON 纯读校验（统计+违规清单，rc 0/1）。 | untracked（未入库） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `scripts/governance/chief_lease.py` | chief_lease.py — 总指挥租约仲裁器（裁定#415 机械化，2026-09-28） | 2026-09-29（5天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `scripts/governance/commit_derived_sync.py` | 派生残留一键收口（2026-09-07 triage 根治配套）——治"每次都处理了，每次又都会再次出现"。 | 2026-09-30（4天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `scripts/governance/d11_compliance/check_generator_no_realtime_time.py` | 门禁：生成器禁止使用实时时间源（datetime.now / time.time / datetime.today）。 | 2026-09-22（12天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `scripts/governance/d11_compliance/check_no_commit_derived.py` | 门禁：阻断对派生产物（已离库的生成器输出）的 git add。 | 2026-09-19（15天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `scripts/governance/d11_compliance/validate_blueprint_overlap.py` | Module docstring — see module-level docstring for details. | 2026-08-18（47天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `scripts/governance/d5_architecture/panorama_common.py` | panorama_common.py — 全景投票共享工具（ARCH-056 引擎加固） | 2026-08-20（45天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `scripts/governance/d5_architecture/validators/validate_authority_registry.py` | Module docstring — see module-level docstring for details. | 2026-08-18（47天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `scripts/governance/data_supply/__init__.py` | Wave-3 data-supply rulers (3.2 false-green cross-check / 3.3 supply conservation / W-102). | 2026-09-29（5天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `scripts/governance/fullflow/generate_fullflow_crosscheck.py` | 全流通五向对账生成器（机生，宪法 §9.5"静态清单禁手工维护"的落地尺）。 | 2026-09-28（6天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `scripts/governance/generate_governance_map.py` | generate_governance_map.py — 治理运行地图(GOMAP-001)骨架生成器。 | 2026-10-04（0天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `scripts/governance/generators/library_hygiene.py` | library_hygiene.py — 图书馆月度卫生命令（ulib3 T9）：一条命令出候选清单，Owner 月批。 | 2026-09-29（5天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `scripts/governance/git_hooks/__init__.py` | git_hooks 包标记——post_commit_regen_yaml 等 git hook 脚本的 Python 包入口。 | 2026-08-17（48天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `scripts/governance/git_hooks/post_commit_regen_yaml.py` | post_commit_regen_yaml.py — post-commit YAML 变更触发器（治本缺口#3） | 2026-09-24（10天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `scripts/governance/meta_question/wo006/apply_node_bindings.py` | WO-006 挂接写入器——读候选旁挂册 → 三验证 → 分片走 ingest 唯一合法通道纯 INSERT。 | 2026-09-26（8天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `scripts/governance/meta_question/wo006/emit_case_file.py` | WO-006 案卷装配器——从六份旁挂册现读数字，产出 build/WO-006.yaml。 | 2026-09-26（8天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `scripts/governance/meta_question/wo006/generate_merged_node_convergence.py` | WO-006 合并节点收敛册生成器——2,225 个"已并入"节点以指向式表达，零物理删除。 | 2026-09-26（8天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `scripts/governance/meta_question/wo006/generate_micro_chain_retirement_nominations.py` | WO-006 零覆盖微链退役**提名**册生成器（≤2 活跃节点且活跃口径零覆盖的链）。 | 2026-09-26（8天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `scripts/governance/meta_question/wo006/recompute_pq0064.py` | WO-006 PQ-0064 判据复算（施工前/施工后同口径两次）+ 转 pass 路径诊断。 | 2026-09-26（8天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `scripts/governance/meta_question/wo_b2_e1c/apply_e1c_ledgers.py` | 部署/同步/核验 metaq_e1c 台账（组合空间预注册三件套 + 考尺快照 + 合并闸运行账）。 | 2026-09-26（8天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `scripts/governance/qcure_offset_report.py` | qcure_offset_report.py — 死信×预检对消周报生成器（QCure 观测线验收承重件，生产数据只读）。 | 2026-09-25（9天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `scripts/governance/run_silent_failure_regression.py` | run_silent_failure_regression.py — silent-failure 回归套件一键执行入口（P3-2，2026-07-19） | 2026-08-20（45天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `scripts/governance/shared/frontmatter.py` | 公共模块别名（R5 公共化）— 从 _shared.frontmatter 重新导出。 | 2026-08-18（47天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `scripts/governance/standards/standards_lib.py` | standards_lib — 考纲标准库加载器+修标重考历史工具（骨架 v1.1 §8）。 | 2026-09-18（16天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `scripts/governance/wave1a/cross_session_view.py` | cross_session_view.py — 交接视图（1A.6）：一条命令出跨会话状态视图。 | untracked（未入库） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `scripts/governance/wave1a/verified_promotion_check.py` | VERIFIED 升态校验器（wave1a）——升 VERIFIED 前置三判据。 | 2026-09-30（4天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
