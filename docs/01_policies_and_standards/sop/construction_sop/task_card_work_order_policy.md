---
ttl: permanent
doc_type: policy
rule_form: procedural
verifiability: manual
title: 任务卡工单制政策 v1.0——施工必开卡/两轮预审验收/闸消费/图书馆预留/豁免判据
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-10-04
topic: construction_sop
---

# 任务卡工单制政策 v1.0（真源）

> **一句话**：Owner 已批任务卡转正为 AI 层标准工单系统（2026-10-04，分两步：先施工必开卡三接口，图书馆入口绑定第二步）——施工必开卡、验收走 TaskRepository 两轮预审+verify 证据核销、发车类闸消费 verified 状态。
> **定位**：construction_sop 家族新册，与 [construction_workflow_policy.md](construction_workflow_policy.md)（15 步闭环编排真源）互补——本册只立"卡"的法：何时开、怎么验、谁能消费、何时豁免；编排内容不复制。
> **净零声明**：正典资产净增 1 册；对价=收编散落于车道任务书/会话收尾惯例中的"建卡/验收"口头约定为成文法，不新增并行真源。接口②自动化实体=scripts/governance/card_review_automation.py（本册锚定，非第二实现）。

## 0. 真源与术语

- 任务卡=TaskCard，真源 `src/zephyr/governance/persistence/task_repo.py`（10 态状态机；一切读写经其公共 API，禁裸 SQL/裸 UPDATE）。
- 建卡正门=`create_and_ready()`（无依赖卡直达 READY）；有依赖走 `create()`+依赖解析器。
- 预审=`batch_review()`（7 维度，记录持久化 task_reviews 表）；审查状态=`get_review_status()`（review_complete=连续 2 轮 0 问题，对齐 CIRCULAR_ACCEPTANCE_ROUNDS）。
- 核销=`verify()`（置 verification_status=verified 的唯一合法生产路径，前置=审查完成）；发车=`transition(COMPLETED)`（G7 评估）。

## 1. 施工必开卡（接口①）

1. **开工即建**：施工车道会话注册后、首行业务代码前，须持本车道 active 卡（status ∈ READY/IN_PROGRESS 且 session_id=本 sid）。
2. **本版生效形态**：车道首提交前必持 active 卡；提交信息/会话汇报引用所持 task_id 供核对。机械拦截（提交闸读卡）待 GitCommitGateway 窗口，届时另行登记 gate，不在本版范围。
3. **接口①待 rule_bridge 窗口**：session_worktree_start 联动为 keyword-only opt-in（默认关、零行为变化），因该文件 [STABILITY] evolving 且热面（启动主路径），本版不动代码，留如下 diff 方案（约 18 行）待窗口实施：

```python
# (a) session_worktree.py 签名 keyword-only 参数区追加 1 行：
    require_active_card: bool = False,
# (b) body 在 sid 计算后、并发阻断前插入（fail-open 对标 _print_startup_error_patterns）：
    if require_active_card:
        try:
            from zephyr.governance.persistence.task_repo import TaskRepository
            with TaskRepository(enable_gate=False) as _repo:
                _has_card = _repo.count_by_status_and_session_any_active(sid)
            if not _has_card:
                return {"ok": False, "session_id": sid, "worktree_path": "", "branch": "",
                        "registered": False, "created": False, "error": "ACTIVE_CARD_REQUIRED",
                        "detail": "任务卡工单制政策 §1：开工必开卡——先 create_and_ready 再 start"}
        except Exception as _card_err:  # fail-open：检测失败不阻断启动
            logger.warning("[start] active-card check failed: %s", _card_err)
# (c) task_repo.py 增只读 helper count_by_status_and_session_any_active(sid)
#     （复用 SQL_SELECT_TASKS_ACTIVE_BY_SESSION_SORTED 语义，过滤 READY/IN_PROGRESS）；
# (d) 同步 session_worktree.py [DEPENDENCIES]/INVARIANTS 头 + tests/ mock 双依赖测试。
```

   - 注意：TaskRepository 延迟 import（防启动路径拖库）；count helper 放 task_repo 而非 rule_bridge 内联 SQL（禁裸 SQL 红线）。

## 2. 验收=两轮预审+证据核销（接口②，已落地）

1. **两轮预审自动化**：收尾先跑 `python scripts/governance/card_review_automation.py --task-id <卡> [--session-id <sid>]`——自动跑 2 轮 batch_review（轮内出 issue 即提前停，连续零问题计数被打断后空跑无意义；轮间隔 --interval-seconds 可配），出具 verify 就绪度报告（schema=card_review_automation/v1，--json 机器可读；rc 0=就绪/已盖章，1=未就绪，2=卡不存在/用法错）。
2. **人工/车道确认后才核销**：报告 verify_ready=true → 车道确认后调 `TaskRepository.verify(task_id, session_id=sid)`。**自动化恒不代盖章**（工具 stamped 字段恒 False，任何路径不调 verify）——预审可机械化，核销责任在人/车道。
3. **禁裸 UPDATE**：verification_status/construction_status 只能经 verify() 置位；绕过=私改真源，按门禁违规处置。审查证据以 task_reviews 表为准，可追溯。
4. **建卡质量前置**：description 须含 根因/治根/施工步骤/验收标准 结构词且 ≥100 字（solution_completeness 维度机械校验）——防建卡即死锁（D-SIGNAL 臆造 post_sync 命令死锁 20 卡事故在案）。

## 3. 闸消费（接口③，现状确认）

1. **G7 Task Delivery Gate**（`src/zephyr/gov_enforcement/rule_enforcement/task/g7_orc_gate_engine.yaml`，check G7-ORC-VERIFICATION，severity=error）已在 transition(COMPLETED) 时消费 `verification_status==verified`——"发车类闸消费 verified 状态"的现状实证（Owner 引 T2 先例即此型）；本版无需新增闸。
2. 后续发车类闸（提交队列落地闸/发布闸等）需要收尾证据时，一律消费卡状态（verified / review_complete），禁自建平行验收通道；新增消费闸须登记 rule_enforcement_registry 并按宪法 §3 声明 own-scope 或全仓扫描理由。

## 4. 图书馆绑定（第二步预留，本版只立法不实施）

1. 施工产物入馆（docs/library 收录）凭卡溯源：入库申请须引用 task_id，且该卡处于已核销链上（verification_status=verified，或 VERIFIED 终态）。
2. 本版不改动 library 入口代码与 INDEX 生成器；实施载体（library.lookup 入参校验或收录 gate）留第二步，经 Owner 门位批复后另立 diff，届时以本节为立法依据。

## 5. 豁免判据（全或无，禁部分豁免）

同时满足以下全部判据的任务可免开卡：

1. 纯只读探针：零写操作（不落任何仓库文件/DB/注册表；.runtime/tmp/ 临时脚本按宪法生命周期隔离不算写）；或改动仅限 tests/（测试隔离红线本就禁写生产路径）；
2. 会话生命周期 ≤ 单轮问答，不产生提交。

豁免决定在会话汇报中一句话声明命中判据即可，不建登记册（静态清单禁手工维护）；写操作、提交、注册表变更三者任一出现即失格，回 §1 开卡。

## 6. 版本记录

- v1.0.0（2026-10-04）：首版立法（Owner 批复转正）。接口②落地（card_review_automation.py+tests 10 用例全绿+临时库端到端冒烟）；接口①给 diff 待 rule_bridge 窗口；接口③现状确认（G7 先例）；图书馆绑定第二步预留。
