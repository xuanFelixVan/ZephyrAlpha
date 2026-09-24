---
ttl: task_bound
completes_when: 11 工单全部施工闭环+队列九批全落+终局行生效后随包归档
title: 新总包车道交接书——283 问战役施工阶段全权指令（一键复制版）
owner: ZephyrAlpha-Owner
session: st-metaq-20260923
date: 2026-09-24
---

# 新总包车道交接书（Owner 已批全部裁定，本件=开工令+全量上下文）

## §0 一句话使命

283 问考试战役的"考"已 100% 完成（PG 在库），你接手的是"施工闭环"阶段：按 Owner 已批的六裁定，把 11 张工单（WO-001~011）全部施工闭环，让 45 个 fail 转绿或妥善退役、96 个 insufficient 的复考前置全部建成，最终交付"数据→因子→状态→决策"全链路可运行状态。

## §1 项目背景（30 秒）

ZephyrAlpha=D:\ZephyrAlpha，A 股量化，100% AI 开发。PG 库 depgraph 的 meta_question schema 三表=全项目"数据→因子→状态→决策"链路的验收判据（283 问）。st-metaq-20260923 班已把 283 问全部考出结论：pass 142 / fail 45（30 因子无预测力退役+15 基建缺口）/ insufficient 96（复考前置未满足）。Owner 已批全部六项裁定（见 §3），你按批件施工即可，无需再等裁定。

## §2 必读文件（按序）

1. `docs/_working/meta_question_answers/02_final_ledger.md` — 端到端总账（三态计数/验证链/心跳流/死因链全录）
2. `docs/_working/meta_question_answers/01_phase2_plan.md` — 96 insufficient 三分诊（A28 数据回补清单/B37 建设载体清单/C31 案由）
3. `docs/_working/meta_question_answers/gaps/WORKORDER_MASTER.md` — 11 张工单总册（每单：缺口/配套/evidence/工作量/验收判据/门位）
4. `docs/_working/meta_question_answers/gaps/FAIL_CLOSURE_LEDGER.md` — 45 fail 闭环台账
5. `docs/_working/meta_question_answers/gaps/RETIREMENT_REGISTER.md` — 30 问退役登记（禁翻案铁律）
6. `docs/_working/meta_question_answers/ANSWER_CONTRACT.md` — 答题纪律（红线浓缩）
7. 源线谱册：`docs/_working/chain_piling_campaign/02_source_line_registry.md`（29 线三档）
8. AGENTS.md（宪法 L0）

## §3 Owner 已批六裁定（2026-09-24 晨，对话在案）

1. **复权口径**：raw×adj_factor 为真源，重算 kline_daily_hfq 712 万行（WO-004）
2. **板块主从**：TQCENTER 行情口径为主、知识图谱为从，按代码路由建映射册（WO-005）
3. **CKG 降级**：一致率 1.23%≪70% 触发题面自带降级条款，CKG 降为结构先验（WO-007 并案 0065）
4. **io_edge DDL**：选旁挂映射册（不动原表），153 部门映射排产（WO-007）
5. **产品边阈值**：30%→5%（机械天花板实证），留同义词册升级口（WO-008）
6. **campaign regime**：95（WO-003 监控器占位转正；持续入题后可改常态带）
7. **WO-010**：DS 册一行已批落地（q-0035 在队）

## §4 施工任务清单（15 分包建议编制）

| # | 工单 | 内容 | 量级 | 依赖 |
|---|------|------|------|------|
| 1 | WO-011 | tushare money_flow 回补 2021-01~2025-09（560-600 万行，解 A06 族 6 问复考） | M | 无 |
| 2 | WO-004 | 复权链重算（raw×adj_factor 真源，重建 hfq 712 万行） | L | 无 |
| 3 | WO-007 | io_edge 旁挂册+153 部门映射+CKG 降级执行 | L | 无 |
| 4 | WO-006 | ig_node_company 三源补挂+2,225 节点收敛 | L | 无 |
| 5 | WO-005 | 节点↔板块 symbol 路由映射册 | M | 无 |
| 6 | WO-009 | 质押事件版本载体 DDL+11.3 万回填 | L | 无 |
| 7 | WO-008 | 产品同义词册（阈值已裁 5%） | M | WO-007 |
| 8 | WO-001 | registry.py 降级桩换真检（依赖 0004 批落 HEAD） | S | 0004 |
| 9 | WO-002 收口 | 对账器进排班例行化（回放/接线已建成） | S | 0004/0006 |
| 10 | WO-003 | 持续入题机制（监控器已建成 q-0007） | M | 无 |
| 11 | WO-010 ✓ | 已落地（q-0035） | - | - |
| 12 | A 类回补 | 01_phase2_plan 数据清单#2-4（IO 表落库等） | M-L | 无 |
| 13 | B 类载体 | 01_phase2_plan 建设清单（writeback API/E1C 台账/宏数 vintage） | L | 无 |
| 14 | 队列死信值守 | 九批在队（0020-0033），死则按台账配方修投 | 值守 | 无 |
| 15 | docs 增量批 | 后续产生的新文件按 token 先行批+内容批投递 | 值守 | 0010 已落 |

## §5 关键路径速查

- PG 只读：`from zephyr.governance.depgraph_schema import get_depgraph_pg_connection`（默认 read_only=True）
- CH 只读：`DatabaseService().get_clickhouse_conn(role="reader")`（execute 无 cursor；库前缀 c1_market/c3_fundamental/c1_backtest）
- PG 写（depgraph 架构数据）：`get_depgraph_pg_connection(read_only=False)`（仅架构数据合法）
- 提交正门：`python scripts/git_commit.py --session <sid> --files <逗号清单> --enqueue --allow-non-worktree --allow-multi-domain --allow-overlap`
- token 登记：`python scripts/governance/d3_metadata/batch_creation_tokens.py --prefix <目录> --created-by <sid> --capability <名> --merge-evaluation "<一句话>"`（注意目录级前缀会卷入全目录文件，窄前缀或外科插入）
- 翻译登记：`python scripts/governance/d3_metadata/add_module_translation.py --path <py> --domain D_* --name-zh <中文名> --plain-zh <大白话>`
- 队列状态：`python scripts/commit_queue.py status`
- 冷启动 PATH：`export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:/c/Users/fanzi/AppData/Local/Programs/Python/Python312/Scripts:$PATH"`

## §6 已知雷区（前车之鉴，必读）

1. **capability 册拉锯**：docs/01.../capability_canonical_file_registry.yaml 被多包整文件重写，token 条目分钟级被抹——注册后立即投递，或线级外科插入（禁 yaml round-trip 重排=防批量删除门）。
2. **翻译册拉锯**：module_translation_registry.yaml 同病——add_module_translation 幂等可重跑。
3. **json 禁入 docs/_working**：目录契约白名单 [.md,.csv,.yaml,.html]——交付件一律 .yaml（json→yaml 先例 G6）。
4. **FOLDER-CAPACITY**：单目录 ≤40 文件——大批拆分片子目录。
5. **CREATE-GUARD 读主树册**（非批快照）——token 注册后立即投递压窗口；热册清场则每轮重注册。
6. **283 问铁律**：PIT 切点 2025-09-09；no_alpha 禁翻案；fail 两类区分写进作业簿；挖矿 SOP 先行（六向台账+三态裁定封矿后才施工）。
7. ** Background shell cwd 漂移**：后台命令用绝对路径或显式 cd。

## §7 验收判据（收官标准）

- 11 工单全部施工闭环或 Owner 批准的替代处置
- 45 fail：infra 15 问复考全 pass 或妥善处置；no_alpha 30 维持退役
- 96 insufficient：A 类回补完成后复考出 outcome；B 类载体建成；C 类案由归档
- 九批队列全落 HEAD；终局行生效（a1_chainpile_ledger）
- 全链路红蓝对抗一轮+连续两轮零
- GitCommitGateway 正门全量落地+临时文件清零

## §8 红线（违反即返工）

PG 只写 meta_question schema（五列+exam_result/audit）；禁裸 SQL 写业务库；禁裸 duckdb/psycopg2；实盘四禁；git 只走 GitCommitGateway；挖矿 SOP 先行（六向台账+三态裁定封矿前禁施工代码）；30 问退役禁翻案（增补令#5）。
