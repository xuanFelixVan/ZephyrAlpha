---
module_id: AUTONOMOUS_GOVERNANCE_RUN_QUEUE_001
version: 1.0.17
status: Active
created_date: 2026-04-11
last_updated: '2026-04-13'
owner: 仓库 Owner / 文档负责人
responsibility:
  - 跨 Cursor 会话的治理任务顺序、当前指针与锚点指令真源
standard_type: 运行队列
applicable_scope: 全仓文件治理接力；与 REPO_WIDE 并列，执行时以本文件「下一步」优先
---

# 自主接力 — 治理运行队列

> **用途**：用户发送多轮「继续未完成的工作」时，**每一轮新对话**先读本页 **「当前指针」** 与 **「下一步」**，避免重复扫全仓或偏离底线。  
> **不能承诺**：单次 AI 对话连续执行 9 小时；**能承诺**：仓库内留有**固定顺序**与**可更新指针**，使多会话逼近同一目标。  
> **真源并列**：[全仓库文件治理任务清单](./REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md)（未勾项）、[会话交接（阶段 A/B）](./GLOBAL_FILE_GOVERNANCE_SESSION_HANDOFF.md)、[治理工具总索引](./GOVERNANCE_TOOLS_INDEX.md)。

---

## 1. 当前指针（每轮对话结束更新）

| 字段 | 填写 |
|------|------|
| **UTC 时间** | `2026-04-13T02:30:00Z` |
| **上轮 commit** | `84bfd625` |
| **next_queue_id** | **B-02** |
| **本轮建议前缀**（§7） | `docs/09_AUDIT/REPORTS` · `docs/05_IMPLEMENTATION/04_OPERATIONS`；或 `docs/09_AUDIT/STATE` 续批 |
| **notes** | **B-02 · `09_AUDIT/STATE` 批次 3**：[`docs/09_AUDIT/INDEX.md`](../../../09_AUDIT/INDEX.md) 在 REPORTS 与 04_OPERATIONS 之间增 **STATE 子域**表（`STATE/INDEX`、分组索引、`INDEX_HEALTH_20260413`、`overnight_runs/INDEX`），并注明与 REPORTS 的 `20260412` 健康度文件分日期勿混读。L1 **判定无效=0**。运行队列 **v1.0.17**。 |
| **stuck** | **无**（若有 **[STUCK]**，见下节并在 `notes` 写明细） |

> 更新规则：完成一个队列子项或推进一批 §7.2 后，**至少**更新 `last_commit` 与 `next_queue_id`。

### [STUCK] 标注（防 L1 / Git 修复死循环）

若**同一任务**（例如：`sentinel_l1` 判无效反复修仍 >0；或 merge/rebase 冲突连续 3 轮仍无法干净收尾）已 **连续失败 3 次**：

1. **本对话内停止**再对该任务做链式自动修复。  
2. 在 **「当前指针」→ `notes`** 追加一行，格式：  
   `[STUCK] queue_id=… 原因一句话；末次现象（如 L1 无效链数 / 冲突文件路径）；建议 Owner：…`  
3. 若卡住的是 **Phase B 某前缀**，在 **§4 前缀表**对应行状态列改为 **`[STUCK]`**（保留原 `[ ]` 语义：未完成，但明示暂停），并在同一格或 `notes` 写 UTC 日期。  
4. 将 **next_queue_id** 改为**下一可执行项**（如跳过该前缀、先做下一前缀或 B-03）。  
5. **commit** 对本文件的指针/STUCK 更新（仅当工作区允许；若仓库处于冲突中则先让用户解决再提交）。

---

## 2. 锚点指令（每约 15 轮用户消息插入一条，或新开对话时先扫一眼）

**锚点 A — 真源**  
`ZephyrAlpha 根目录。先打开 AUTONOMOUS_GOVERNANCE_RUN_QUEUE.md 当前指针，再执行 next_queue_id。权威：REPO_WIDE 未勾项、GOVERNANCE_TOOLS_INDEX。D 类合稿须 Owner，禁止擅自合并蓝图正文。`

**锚点 B — Git / L1**  
`先 git status；只 add 本任务文件；中文 commit。改文档后 python scripts/governance/sentinel_l1_governance_scan.py 判定无效=0。git ls-files 统计用 core.quotePath=false。`

**锚点 C — 交接**  
`回复中文、术语英文。结尾列出：改动文件、commit、建议下一 next_queue_id；勿假设下一轮读过本轮。`

---

## 3. 每轮必做（Phase A · 纪律）

- [ ] `git status` 看清无关改动，**勿误提交**  
- [ ] 只 `git add` 本任务路径  
- [ ] 改 `docs/` 或路径后：L1 **判定无效 0**；若同目标已失败 3 次 → **按 §1 [STUCK] 停止并跳过**  
- [ ] 更新本节上方 **「当前指针」**（同一次 PR / commit 可合并进本文件）

---

## 4. 任务顺序（按依赖；与 REPO_WIDE 对齐）

### Phase B — §7.1 / §7.2 深度尽治（主队列）

机器/AI **可**做：单前缀一批内的摆放核对、导航补链、断链修、rollup 复跑、小步 commit。  
**勿**在无人裁决时批量删 `06_ARCHIVE` 或合并 D 类蓝图正文。

- [x] **B-01** 已读 [`REPO_DIRECTORY_ROLLUP_20260411.md`](../../../09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_20260411.md) 与 [`.json`](../../../09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_20260411.json)（2026-04-11）  
- [ ] **B-02** 对下表 **自顶向下**每次选 **1 个前缀**（或拆子目录），按 REPO_WIDE **§7.2** 模板执行一批后打勾并 commit  
- [x] **B-03** 批次间 `python scripts/governance/export_repo_directory_rollup.py --date YYYYMMDD` 并提交（作证据）（2026-04-13：`20260413` 快照已提交）  
- [ ] **B-04** REPO_WIDE **§7.3** 总勾或登记**书面例外**（须 Owner）

#### `docs/` 深度 3 前缀队列表（条数以最新 rollup 为准；当前快照见 `REPO_DIRECTORY_ROLLUP_20260413.json` · 前 40 占位）

| 状态 | 条数 | 前缀 |
|------|-----:|------|
| [ ] | 499 | `docs/09_AUDIT/REPORTS` |
| [ ] | 406 | `docs/05_IMPLEMENTATION/04_OPERATIONS` |
| [ ] | 382 | `docs/09_AUDIT/STATE` |
| [ ] | 273 | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS` |
| [ ] | 218 | `docs/06_ARCHIVE/20260404_audit_reports_archive` |
| [ ] | 97 | `docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS` |
| [ ] | 83 | `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE` |
| [ ] | 62 | `docs/05_IMPLEMENTATION/07_OPERATIONS` |
| [ ] | 54 | `docs/09_ARCHIVE/duplicates` |
| [ ] | 51 | `docs/06_ARCHIVE/20260408_double_yaml_dryrun_sample` |
| [ ] | 40 | `docs/01_FRAMEWORK/LAYER4_ML` |
| [ ] | 40 | `docs/06_ARCHIVE/20260407_old_layer_audit_reports` |
| [ ] | 33 | `docs/09_AUDIT/STANDARDS` |
| [ ] | 23 | `docs/06_ARCHIVE/20260407_p1_cleanup_archive` |
| [ ] | 21 | `docs/05_IMPLEMENTATION/02_DEVELOPMENT` |
| [ ] | 20 | `docs/06_ARCHIVE/architecture_v4` |
| [ ] | 20 | `docs/06_ARCHIVE/main` |
| [ ] | 19 | `docs/09_RESEARCH_INNOVATION/maintenance_records` |
| [ ] | 18 | `docs/06_ARCHIVE/20260406_encoding_issues_archive` |
| [ ] | 16 | `docs/03_TRADING_TACTICS/01_STRATEGY_FRAMEWORK` |
| [ ] | 16 | `docs/09_AUDIT/TEMPLATES` |
| [ ] | 15 | `docs/03_TRADING_TACTICS/04_YOUZI_STRATEGIES` |
| [ ] | 13 | `docs/04_EXECUTION/07_LIVE_STREAM` |
| [ ] | 11 | `docs/06_ARCHIVE/temp_pending` |
| [ ] | 10 | `docs/09_AUDIT/PROCEDURES` |
| [ ] | 7 | `docs/03_TRADING_TACTICS/99_ARCHIVE` |
| [ ] | 7 | `docs/05_IMPLEMENTATION/01_QUICKSTART` |
| [ ] | 7 | `docs/06_ARCHIVE/20260404_market_participant_consolidation` |
| [ ] | 7 | `docs/09_RESEARCH_INNOVATION/_archive` |
| [ ] | 6 | `docs/04_EXECUTION/03_MONITORING` |
| [ ] | 6 | `docs/05_IMPLEMENTATION/03_DEPLOYMENT` |
| [ ] | 6 | `docs/06_ARCHIVE/duplicate_documents` |
| [ ] | 6 | `docs/09_AUDIT/AUTOMATION` |
| [ ] | 6 | `docs/09_AUDIT/CONFIG` |
| [ ] | 5 | `docs/06_ARCHIVE/20260405_economic_regime_cleanup` |
| [ ] | 5 | `docs/06_ARCHIVE/factor-library` |
| [ ] | 5 | `docs/07_RESEARCH/02_EXPLORATORY_ANALYSIS` |
| [ ] | 5 | `docs/10_GOVERNANCE_COMPLIANCE/KNOWLEDGE_BASE` |
| [ ] | 5 | `docs/11_STRATEGIC_DECISION/archive` |
| [ ] | 4 | `docs/00_RESOURCES/04_PLATFORM_DOCS` |

> 余下前缀见 JSON 全量；本表仅占位前 40，**完成一行请在表内改 `[x]`** 并视需要扩展更多行。

### Phase C — REPO_WIDE 其它未勾（机器边界内）

- [ ] **C-01** [REPO_WIDE §3.6](./REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) **D**：仅当 Owner 已裁决 — AI 可改链、stub、登记 [D_CLASS_CONSOLIDATION_PENDING_REVIEW_REGISTER](./D_CLASS_CONSOLIDATION_PENDING_REVIEW_REGISTER.md)  
- [ ] **C-02** [REPO_WIDE P4](./REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) 可选 `MODULE_PANORAMA_*` 脚本（§2.4）— 单独小 PR  
- [ ] **C-03** 合并相关 PR 附「替换范围 + 验证脚本列表」（流程纪律，见 REPO_WIDE §3.6）

### Phase D — 完成判据

- [ ] **D-01** REPO_WIDE **P5 + §7.3** 可勾或已登记例外  
- [ ] **D-02** 办公室 [README](./README.md) 与 [STATE INDEX](../../../09_AUDIT/STATE/INDEX.md) 仍链到本队列（维护者自检）

---

## 5. 版本记录

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.5 | 2026-04-14 | **B-02 · `04_OPERATIONS` 批次 1**：新增 `README`、补 `INDEX` 导航与实施层 `INDEX` 链 |
| 1.0.4 | 2026-04-14 | **B-02 批次 6**：`INDEX_GROUPED_REPORTS_20260408` 对齐 rollup 口径并补导航链 |
| 1.0.3 | 2026-04-14 | **B-02 批次 5**：REPORTS `README`/`INDEX` 与 `REPO_DIRECTORY_ROLLUP_20260413` 互链并声明手工统计非 Git 真源 |
| 1.0.2 | 2026-04-13 | 指针 notes 记录 **B-03**：`REPO_DIRECTORY_ROLLUP_20260413`；§4 前缀表条数与快照对齐（REPORTS 499、STATE 382、`06_CONSTRUCTION_DOCS` 273） |
| 1.0.1 | 2026-04-11 | 增 **[STUCK]** 防死循环：连续失败 3 次停止、标注指针与前缀表、跳下一项；与 AGENTS / Cursor rule 互指 |
| 1.0.0 | 2026-04-11 | 首版：指针表、锚点 A/B/C、§7 深度 3 前 40 前缀、Phase B～D |

---

## 相关链接

- [项目根 AGENTS.md](../../../../AGENTS.md)  
- [Cursor 规则](../../../../.cursor/rules/zephyr-governance-agent.mdc)  
