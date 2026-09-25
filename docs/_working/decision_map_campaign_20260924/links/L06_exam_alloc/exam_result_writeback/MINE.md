---
ttl: task_bound
doc_type: log
title: L06-子模块 考试结果回写面（exam_result 双 outcome 语义 / 唯一合法写口 / 三态桶消费）挖干
created: 2026-09-25
sid: st-qmine-20260925
lane: L06_exam_alloc
status: SEALED-CORE（①②③④⑤⑥全填；六向内部反查全、③向外部双源齐；DB 行数实测=受阻/11号文已实证 exam_result=0，见挖矿日志 R3）
skeleton_source: ../SKEL.md（八子块）；../../09_link_skeletons.md 环节6；判据 ../../17_quantified_acceptance.md §一
doc_role: L06 挖矿子模块 MINE（本目录=新切子块，非 SKEL 八块号复用）
---

# 子模块 · 考试结果回写面（exam_result writeback）

> 本块 = 任务令点名的**本环节最大一块**：`meta_question_exam_result` 的列 `outcome` 是生命周期态，
> 裁决结论在 `conclusion` JSONB 的 `outcome` 键（11 规范键之一）；只写列不写 JSONB 键 ⇒ 考试结果静默掉出三态桶。

## ① 职责一句话
把"一场考试的裁决"机械落进 `exam_result` 追加账并驱动 `meta_question` 主表生命周期，
保证**列态（answered/reexam/suspended）与 JSONB 裁决（pass/fail/insufficient）双写不缺键**，
让下游"三态桶"验收能读出该问到底被裁成什么。

## ② 现状实测（代码 file:line + 表字段实测）

### 表结构与字段
- DDL 真源：`scripts/governance/apply_meta_question_ddl.py:147-166`，表 `meta_question.meta_question_exam_result`。
  - `conclusion JSONB`（:151）、`confidence JSONB`（:152）、`data_window JSONB`（:153）、`pit_assertion`（:154）、
    **`outcome TEXT NOT NULL CHECK (outcome IN (<生命周期词表>))`**（:155）、`recorded_by`、`created_at`；
    自增主键 `id`（序列 `meta_question_exam_result_id_seq`，GRANT :213），索引 `(q_id, created_at)`（:166）。
  - 头注 :15/:34 明示"考试记账独立表（30§C R3：**主表零增量**）"——即考试结果不写回主表列，只在独立追加表 + 主表 `status`/`last_exam` 乐观锁推进。
- 词表：`outcome` 列取值来自 `load_vocabulary_values("meta_question_outcomes_vocabulary.yaml")`
  （`exam_ops.py:102`；`apply_meta_question_ddl.py:65`），与 `OUTCOME_FROM_STATUSES` 键集一致 =
  **{answered, reexam, suspended}**（生命周期三态，`exam_ops.py:136-140`）。
- **11 规范键**（`conclusion` JSONB 必备键，唯一枚举位 `writeback.py:505-517`）：
  `outcome`（裁决 pass/fail/insufficient）、`conclusion`（文本）、`evidence`（list）、`fail_type`、
  `confidence`、`data_window`、`exam_ref`、`pit_assertion`、`three_check`、`notes`、`threshold`。
  注释铁律（:501-503）：*"规范键 `outcome` 是裁决，与 `exam_result.outcome` 列（生命周期）语义不同；
  全仓读出一律按 `conclusion->>'outcome'` 取裁决，缺它会让问题掉出三态桶"*。

### 两条写路径（一条合法、一条可绕过）
1. **唯一合法入口** `ExamLoopWriteback.writeback`（`src/zephyr/governance/meta_question/exam_loop/writeback.py:147`）：
   鉴权→六查→降级→双时戳→矛盾检测→乐观锁写单事务（INVARIANTS :8-18）。`conclusion` 经
   `_conclusion_block`（:497-527）组装 ⇒ 结构上保证 11 键齐全。
2. **低层 Mixin** `MetaQuestionExamMixin.record_exam_result`（`exam_ops.py:411-477`，`MetaQuestionRegistry` 继承暴露）：
   直接 `_as_json(result.get("conclusion"))`（:440）把调用方给的 `conclusion` **原样落库**，
   **不校验也不注入内层 `outcome` 键** ⇒ 任何走此公共方法的调用方若 `conclusion` 缺内层 `outcome`，
   列态仍合法但裁决读不出 = **静默掉桶旁路**（本块核心漏洞①）。

### 生产触发面（有无）
- **代码在、零生产样本**：治理级考试循环 283 问全 `registered`、`answered=0`、`exam_result=0 行`
  （`11_integrated_backtest_audit.md §5.3`，PQ-0051-0058；L05/L06 SKEL 亦引 = IBT-E01）。
- 触发面 = 手工 CLI：`scripts/governance/meta_question/wo_b1_examloop/run_exam_loop.py`（落账出口）、
  `check_exam_loop.py`（判据复考）——无计划任务/事件触发常驻（writeback.py `[STARTUP] manual` :6、`[MATURITY] new` :7）。
- **镜像旁路实证**：YAML 考试答案已产出为文件镜像 `docs/_working/meta_question_answers/results/b1/PQ-0004.yaml`、
  `.../b2/PQ-0095..0108.yaml`，但表内 `exam_result=0` ⇒ 答案出在文件、未回写进表（本块漏洞②：
  "有结论 ≠ 进了三态桶"，回写闭环未收口）。

### 数据新鲜度
- 追加表 `created_at` = 落库时点；当前表无行 ⇒ 无可测起止。镜像文件批次 = 2026-09（b1/b2 两批）。
- 待复核：只读连库数 `meta_question.meta_question_exam_result` 行数与 `conclusion->>'outcome'` 非空率（本块 ② 实测补洞，见日志 R3；DB 忙则记受阻）。

## ③ 六向台账（每向内部反查 + 全网搜索双动作）

| 向 | 内部反查发现 | 全网外部反查 |
|---|---|---|
| ①上游 | 写入口载荷契约=13§1（writeback.py:31-57 docstring 示例）：调用方须给 `outcome`(列态)+`verdict`/`conclusion_outcome`(裁决)+六查原料。裁决键取 `payload.get("verdict") or payload.get("conclusion_outcome") or ""`（:507）——**二者皆缺则裁决键写空串**，A1 六查不查此键（`_check_a1` 只验 `conclusion_value`+`conclusion_dir`，:595-601）⇒ 核心漏洞③：合法入口自身也能产出"列填了、裁决空"的行 | 待外部反查（挖矿日志 R2）：业界 append-only/双时态事实表"生命周期态列 vs 业务结论分离"的命名/校验惯例 |
| ②下游 | **读端已定位**（R2 收口，非 SQL `->>` 而是 Python dict 取键）：闭环台账 `scripts/governance/meta_question/build_closure_ledger.py` 以 `select distinct on (q_id) q_id, conclusion ... from meta_question_exam_result`（:55-56）取最新行，`concl.get("outcome")`/`fail_type`（:94-95）入表；`outcome_dist` 按 pass/fail/insufficient 三态计数（:276-277）、`open_q`=fail|insufficient（:273）；水位 `max(created_at),count(*)`（:59/:81）。**掉桶守卫=红蓝尺** `redblue_metaq_suite.py`：R2 结论形态尺 `ruler_r2_conclusion_shape`（:160-167）验 11 键齐 + 裁决键 ∈ {pass,fail,insufficient}（非法即报"裁决值非法"，fail 缺 fail_type 即报）；R4 三态守恒尺（:231-236）逐问最新行三态和须=问总数，否则列"掉出三态桶"问。⚠ 关键 nuance：守卫在**审计/红蓝侧**（本块只读不碰，属 LANE-RB 收口面），**写路径自身无此兜底** ⇒ 漏洞③ 仍可在落库瞬间成立、只在事后巡检暴露 | 三态分桶（pass/fail/insufficient）下游消费模式外部佐证（并入 ③ 向引文） |
| ③算法/机制 | 追加更正不 UPDATE/DELETE：全 SQL 仅 `INSERT` 追加（`_SQL_INSERT_EXAM_RESULT` exam_ops.py:246-250）+ 主表乐观锁 `UPDATE ... WHERE version=?`（:234-237）；追加表**无 UPDATE/DELETE 语句**（grep 实证）⇒ 修历史只能追加新行，符合任务令"禁 UPDATE/DELETE"。三取二仲裁=同 `plan_version` 多条 `conclusion` 多数裁定（`arbitration.resolve_majority`，writeback.py:239/245-248）。`build_closure_ledger` 用 `distinct on (q_id) ... order by created_at desc`=事件溯源"取快照=最新事件折叠"标准读法 | **≥2 源**：① Microsoft Azure Architecture Center "Event Sourcing Pattern"（learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing，微软，2026 更新）——append-only 不可变事件流、更正以新事件追加而非改写；② CODE Magazine "Event Sourcing and CQRS with Marten"（codemag.com/Article/2209071，2025-12）——同一事实现存于追加事件序列、state 由事件重放折叠。**A 股适配闸=NA**（治理元数据面，非行情信号） |
| ④后端 | 冻结件旁路守卫：`writeback.py:19 [MODIFY-GUARD]` 指向 `13_exam_backfill_loop_design.md §1/§2/§33`；契约变更须先改设计稿。`record_exam_result` 无同类守卫 ⇒ 绕过面缺"改前 claim/契约钉"（漏洞①后端侧）。异常族 `QuestionValidationError`/`VersionConflictError`（exam_ops.py:146-161）fail-closed 上抛（:20-21） | 待外部反查：双写口（canonical builder + raw DAO）漂移的防护惯例（schema-on-write vs schema-on-read） |
| ⑤前端 | `meta_question_answers` 台账镜像文件是"人读面"（YAML casefile）；`exam_result` 表无看板前端消费证据（grep 前端无 exam_result 引用，登记边界）。呈现=只登记不施工（挖矿 SOP §2⑤） | 已查无：前端无 `exam_result` 三态桶可视化；如需上板应并入环节 9 复盘（L09），本块不越界 |
| ⑥数据字段 | 11 规范键逐键核对：裁决 `outcome` 键**无 DB 约束**（CHECK 只钉列 `outcome` :155，JSONB 内键不校验）⇒ schema-on-read，缺键静默。`data_window` 双时戳 `fetch_ts`/`decision_ts`（A5 :658-671）、`confidence` 块含 `level/ci_lo/ci_hi`（:529-540）。"字段在 ≠ 可得"：列在、CHECK 在，但内层键可得性取决于调用方 | 待外部反查：JSONB/宽表内层键无约束时的下游"缺键即掉桶"事故范式（数据契约 data-contract testing） |

## ④ 缺口清单（沿用编号 + 新续编，注明册内是否见）

| 编号 | 缺口 | 册内可见性 | 判据/落点 |
|---|---|---|---|
| IBT-E01 | 治理级考试循环零生产样本（283 问 exam_result=0 行） | SKEL §L06-C ⑤/§8 C07 在 | 回写闭环须以 run_exam_loop 打样 ≥1 批，验收=`exam_result` 表行数>0 且 `conclusion->>'outcome'` 非空率=100% |
| **L06-C11（新，册内未见）** | **`record_exam_result` 公共旁路绕过 `_conclusion_block`**：写手 `conclusion` 缺内层 `outcome` ⇒ 列合法、裁决读不出（漏洞①） | 本块新立 | 治理=要么下线该公共方法/降为私有，要么在其入口加"内层 outcome ∈ {pass,fail,insufficient}" 硬拦；改前 claim + 契约钉 |
| **L06-C12（新，册内未见）** | **合法入口 `_conclusion_block:507` 允许裁决键空串**：payload 无 `verdict`/`conclusion_outcome` 时写 `""`，且 A1 六查不覆盖此键（漏洞③） | 本块新立 | 施工=在 `_check_a1` 增"裁决键非空且属枚举"，或 `_conclusion_block` 缺键即抛（fail-closed）；属判据面则须走裁定通道（本块只登记"谁该改=writeback 契约件维护者"，不动手） |
| **L06-C13（新，册内未见）** | **写时无兜底、检测滞后到红蓝巡检**：读端已定位（`build_closure_ledger.py` + `redblue_metaq_suite.py` R2/R4 尺），但掉桶检测发生在事后审计，写路径落库瞬间即使命中空/非法裁决键也不拦（漏洞③ 与漏洞① 的暴露点=巡检而非写口） | 本块新立（R2 修正原"读端未证"） | 判据=写口 fail-closed 与巡检尺双闸；⚠ 施工涉 `redblue_metaq_suite.py`/`build_closure_ledger.py` 属 LANE-RB 收口面，**本块只登记边界、不改其尺**；写口侧加拦=writeback 维护者，走裁定通道 |
| LK-08（在） | PBO/CPCV 逐格报告入考试验收链：裁决键的 pass/fail 若不含多重检验则三态桶判据不完整（与 17 §一 多重检验正式判据挂接） | SKEL §L06-B/C 在 | 冻结件侧（prereg/考尺），本块仅登记消费面缺口，不改判据 |

## ⑤ 自审闸三态裁定（mining_sop_policy §6，量尺=终局全貌）

**主判据（是否消灭人工参与）**：回写闭环是"考试结论→上岗/退役/三态验收"的唯一机械咽喉；终局全貌里
治理级考试循环必须无人值守自动产出可读裁决 ⇒ 该面**终局有位置且消灭人工**，**不得封矿**。

- **裁定=施工（部分）+ 挂起排期（部分）**：
  - **施工**：L06-C11（旁路收口/加内层 outcome 硬拦）——纯代码防御，不触判据，可进施工闭环。
  - **挂起排期（解锁条件）**：
    - L06-C12（合法入口空串）——涉**判据契约面**，须裁定通道；解锁条件=Owner/契约件维护者裁"六查是否纳入裁决键校验"。
    - IBT-E01（打样回写）——解锁条件=治理级考卷 exam_plan 结构化冻结 + GPU 成绩单口径件（L06 他块）就绪；现状 283 问全 registered 属原料未齐，非"规模小"（禁以此封矿）。
    - L06-C13（读端确认）——解锁条件=②向 dict-access grep + 状态带脚本消费核实完成（本块 ②/③ 轮续挖）。
- **不封矿声明**：矿脉未枯——漏洞①②③三点为结构判据级发现，读端定位与 DB 行数实测两项长尾未清（见日志 R2/R3 pending）。

## ⑥ 挖矿日志（mining_sop §7）

| 轮 | 矿脉 | 动作 | 判定 | 归因 |
|---|---|---|---|---|
| R1 | 写路径 + DDL + 11 键 + 生命周期列 | 内部反查：读 writeback.py / exam_ops.py 全文、apply_meta_question_ddl.py DDL、grep SQL 消费 | **signal**（3 结构级漏洞 + 追加不改语义实证 + 镜像旁路） | — |
| R2 | ②下游读端 + ③机制外部 | 内部：grep `conclusion`/`outcome` 于 scripts/governance/meta_question（定位 build_closure_ledger / redblue_metaq_suite 两读端+守卫尺）；外部：WebSearch event-sourcing append-only（Microsoft Azure + CODE Magazine 两源） | **signal**（读端坐实=非虚挂；守卫在巡检侧、写口无兜底=nuance） | — |
| R3 | 表行数/`conclusion->>'outcome'` 非空率 DB 实测 | 只读 database_service 查 `count(*)` + 三态分布 | **受阻/未跑**（GPU 忙期，避免连库；行数结论以 `build_closure_ledger.py:59` 水位 SQL 为可执行入口，11 号文 §5.3 已实证 exam_result=0 行/283 问全 registered） | 归因=并发车道禁 DB 重查，非查无；后续批 D 收口时随巡检补测 |

> noise 归因：本轮无 noise（首落即 3 项结构发现）。A 股适配闸：本块为治理元数据回写、非行情信号，T+1/涨跌停无涉，过闸=NA（不适用，如实注）。
