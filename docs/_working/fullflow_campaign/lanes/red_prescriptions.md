---
ttl: task_bound
completes_when: 红队攻击面全部处置（攻破项派工落地或明确判定防线成立）
---

# 红队战记 + 处方（st-ff-red-20260918 · 全流通战役 §6 红蓝对抗）

> 口径（裁定#325）：本轮攻击 7 靶，**未破 3 面**（防线成立），**攻破 4 处**（全部只出处方，
> 因缺陷落点全在他人独占/禁写域），**未打完 2 面**（如实列，不混写"攻不动"）。
> 一切以实测为准；总包 §6.6 已证其任务书含 4 处引用失实，本文对每条都自己跑过。
> 复现脚本：`.runtime/tmp/ff-red/r1_batch_id_probe.py`、`r1_probe2.py`、`r2_slippage_null_probe.py`、
> `r3_mutate.py`、`r4_final.py`、`r4_v2.py`（scratch worktree=`.worktrees/ff-red`，已 remove）。

## 1. 逐靶结论表

| 靶 | 攻了什么 | 打前实测 | 打后实测 | 结论 |
|---|---|---|---|---|
| **R1** 幂等键 | 复跑测试真身 + **signal_batch_id 稳定性命门** + 跨进程 TOCTOU | `tests/ex_core/test_miniqmt_broker.py`+`test_order_idempotency_persistence.py` = **25 passed / 1 xfailed**（z-land2 报的 4 failed 不复现，已被 `9e16e884af` 以 tmp_path 隔离治本，非降级：xfail 1 例是 xtquant mock 不全的旧钉） | 崩溃重启硬判据成立（P5：`order_stock` 增量 0 次；P5b PROCESSING 态 Fail-Closed 拦下）；TOCTOU 有兜底（P6：6 进程并发 claim→1 OK/5 FAIL，落库 1 行，PRIMARY KEY 生效）；**但批次判别符在生产恒为空**（P1：`begin_signal_batch` 在 src/ **零调用者**）+ 键含墙钟日（P3）+ 同日二次合法意图被吞（P4） | **攻破→只出处方 P-R1-1/2**（落点 `ex_core`/`shared/infra`=z-land3 独占） |
| **R2** 滑点 NULL | 端到端重放 R-014 真单 + 契约双向探针 | 零成交撤单 `build_execution_report` → **`slippage_bps = -10000.0`（BUY）/ +10000.0（SELL）仍在产出**；`validate_execution_report(-10000.0)` **通过**；`validate(None)` 拒（ZA-SH-0054） | 同前，未变 | **攻破→处方 P-R2-1**（R-014 裁定的置 NULL **完全未落地**，第 9 笔只对齐了 DB 列类型） |
| **R3** 加严真加严 | **独立重做两个变异**（read_bytes/write_bytes，禁 checkout）+ escalation_sink 读者 | M1 基线 34 passed；M2 基线 24 passed | M1（还原 `.get(key,{})`）→ **4 failed**；M2（还原恒真门 `ok=True`）→ **2 failed`；两件均 `sha 一致=True` 按字节还原 | **变异面未破（能红证据独立复现成立）**；但**整件零生产消费者**→处方 P-R3-1 |
| **R4** 换行保真 | 造 CRLF 件跑 `--apply` + 跑第二遍 + 追 31 件下落 | `scripts/compute_signals.py` 改 CRLF 213 行、重复 TTL 2 处 | `--apply` 后 **CRLF 211 行全保留、LF-only 0 行**；第二遍 `duplicate_injected_block_files=0 / applied=0` = **真幂等**；但 `git diff --numstat` = **`+0 -2` 而非判据写的 `+0 -1`** | **未破（工具真保真真幂等）**；总包 R-008 判据不完整→见 §3 |
| **R5** 告警链 | 闩修法落地面 + webhook 去重键 + OpsAlertFeed 读者 + `LEVEL_CRITICAL` 绕行 | `src/zephyr/data/scheduler.py:686 _deliver_alert_with_latch` **在 HEAD**（`:795` 用返回值置闩=修法确已落地） | **`src/zephyr/data/alert_webhook_dispatch.py` 不在 HEAD、不在工作区**，仅存于 `.runtime/tmp/ff_quarantine/untracked_snapshot/`（36,284B）；全仓 `import alert_webhook_dispatch` = **0** | **攻破（缺件未落地）→处方 P-R5-1**；四道防误触发反向变异**未打**（时间预算） |
| **R6** 克隆合并 | clone_guard 清零 + 六族行为等价 + 白名单撤销复核 | 未跑 | **未打**（见 §6） | **未打**（原因：轮数预算，非"攻不动"） |
| **R7** 门禁绕过 / 未鉴权资金面 | 造违规批预跑真门；面板 API 鉴权现状 | 未跑 | **未打**（见 §6） | **未打** |

## 2. 攻破清单（全部只出处方——落点均在我禁写域）

### P-R1-1 ★命门：`signal_batch_id` 在生产恒为空串 ⇒ 幂等键退化，同时漏拦与误吞
- **落点**：`src/zephyr/ex_core/order_manager.py:175`（`self._signal_batch_id: str = ""`）、`:236`（唯一写方 `begin_signal_batch`）、`:266-273`（键派生）
- **攻击步骤**：`git grep -n begin_signal_batch -- src/zephyr scripts` ⇒ src/ 内**只有定义、零调用**（探针 P1 实测 `生产开批点数=0`）；生产两个建单点 `trading_session.py:885`、`order_execution_saga.py:604` 都不开批。
- **复现命令**：`python .runtime/tmp/ff-red/r1_batch_id_probe.py`
- **实测后果（两条相反方向的失效，同一根因）**：
  1. **误吞合法单（P4）**：键退化为 `sha256(strategy|symbol|UTC日|""|side)` ⇒ 同日同标的同方向**第二笔合法意图**（金字塔加仓 / 撤单后重下 / 风控要求重报）被静默短路，`submit_order` 返回**上一笔的 broker_order_id**，`order_manager.submit_order` 又把它写进新单（`order.broker_order_id = broker_order_id`）⇒ **两笔本地单共享一个券商号** + `_declaration_guard.record_submit()` 计入未发生的申报 + `_emit_order_event` 发出幻影 SUBMITTED 事件。实测：`第1笔→9001 / 第2笔→9001，order_stock 总调用=1 次`。
  2. **漏拦二次发单（P3）**：`trade_date` 取 `now_utc().date()`（墙钟 UTC 日）而非**信号所属交易日** ⇒ 同一笔信号跨 UTC 日界重放得**新键**。实测 `key_before=11b00558…` vs `key_after=b3e7fe2f…` ⇒ 不相同 ⇒ 可二次发单。夜间挂起次日晨补跑积压信号、夜盘品种（21:00 CST 起=次日 UTC）都在此窗口。
- **对总包那句"确定性键等于随机键"的精确化**：不是随机，而是**与被标识对象无关**——键是"何时重放"+"意图形状"的函数，不是"哪一批信号"的函数。三件套里唯一真正的批次判别符从未被上游喂值，故 R-L3 的实质覆盖面仅限"同一 UTC 日内、同形状意图恰好相同"这一狭窄情形。**此项修复未虚设（同日重放与 PROCESSING 崩溃态都真拦住了），但也未达成"同信号重放"的原始判据。**
- **建议改法**：①键的 `trade_date` 必须来自**信号携带的交易日**，`_resolve_trade_date()` 的 `now_utc()` 兜底改为 Fail-Closed（无交易日上下文即拒绝确定性键并告警，而不是猜一个）；②在信号→建单的装配批强制 `begin_signal_batch`，批次号由信号内容摘要派生（禁 uuid/时间戳）；③若短期无法喂批次号，则**必须把"同日同形状第二笔"从"返回旧单"改为"拒绝并告警"**，否则丢单无声。
- **能红测试设计**：`test_signal_batch_id_absent_in_production_wiring`——用 `ast` 扫 `src/zephyr/**` 断言存在 ≥1 个 `begin_signal_batch` 调用点（当前即红，钉住"未接线"不被当成已修复）；`test_key_independent_of_wall_clock`——冻结墙钟在 UTC 23:59 与次日 00:01 各派生一次同信号键，断言相等；`test_second_legitimate_intent_not_swallowed`——同 strategy/symbol/side/日 两笔不同 order_id，断言 `order_stock` 被调 2 次或抛显式重复意图异常（当前两者皆不满足=红）。

### P-R1-2 键的兜底路径可被"未开批"静默走通
- **落点**：`order_manager.py:266`（`signal_batch_id=self._signal_batch_id` 无校验）
- 与 P-R1-1 同批处置：开批状态应是**发单前置不变量**而非可选上下文。

### P-R2-1 ★零成交仍产出 `-10000.0`：R-014 裁定未落地，交工报告称"已收口"名不副实
- **落点**：`src/zephyr/ex_core/execution_report.py:52-60`（`_signed_slippage_bps` 无 `actual_qty==0` / `avg<=0` 判据）；`src/zephyr/ex_core/execution_report_producer.py:344`（`avg_fill_price=avg_price or _ZERO` 把 None 折成 0 喂给它）、`:414`（`f"{float(value):.6f}"` ⇒ 永不出 NULL）
- **攻击步骤/复现**：`python .runtime/tmp/ff-red/r2_slippage_null_probe.py`
- **实测**：零成交 BUY @4.07 ⇒ `slippage_bps=-10000.0`（下游按"正=不利"读作**满分执行**）；SELL ⇒ `+10000.0`。契约校验器放行 -10000.0、拒绝 None。
- **性质**：`8b12ffa789`（第 9 笔）只把 ClickHouse 列对齐为 `Nullable(Float64)`（**让 NULL 存得下**），`175f837e89` 落的生产者**没有任何一处写 NULL**。R-014 裁定"改判为无有效执行样本、滑点置 NULL、撤单/FILLED 分开计数"三项里只有"分开计数"落了（`producer.py:264` 的 `emitted_filled/emitted_unfilled`），且它**与置 NULL 无关**—— poison 数字照样落库。⇒ **本战役最"安静"的那类病在当前 HEAD 仍活跃**：每笔撤单持续向 TCA/FF-02/FF-06 回流一张乐观票。
- **建议改法**（三件必须同批，缺一即契约方读不回）：①`_signed_slippage_bps` 增 `if actual_qty <= 0 or avg_fill_price <= 0: return None` 并把返回类型改 `float | None`；②`shared/contracts/execution_report.py:57` `slippage_bps: float` → `float | None`，`execution_report_contract.py:164-167` 允许 None（保留"数值时必须有限"）；③`cross_layer_contracts.yaml:806` `type: float, required: true` → `Optional[float]/false`（**=已递 Owner/Max 的 CTR-P1-007 申请单，须与①②同一时序**）；④`producer.py:414` 零成交分支写 `\N`/空 cell 使列落 NULL。
- **能红测试设计**：`test_zero_fill_has_no_slippage`——`actual_quantity=0` 断言 `slippage_bps is None` 且 TSV 该行第 N 列为 NULL 字面量；把 `_signed_slippage_bps` 改回旧算法必红（前手声称的"NULL 测试钉"经 z-drift 与本车道两次独立 grep 均为**不存在**，故此钉须新建，不得沿用）。
- **同型点扫描结果**：见 `lanes/red_zero_vs_none.md`。

### P-R3-1 加严件所在模块零生产消费者 ⇒ 加严在生产路径上永不生效
- **落点**：`src/zephyr/position/position_reconciler.py:123`（`handle_execution_report`）、`:74`（`escalation_sink`）
- **实测（grep，不信注释）**：`handle_execution_report` 在 src/ **零调用者**（仅 tests）；`PositionReconciler(` 的 4 个构造点（`ex_core/position_reconciler.py:110`、`ex_core/risk_layer_orchestrator.py:466`、`trading/recon_runner.py:433`、`scripts/start_paper_session.py:465`）**全是同名不同类**（它们的关键字是 `system_source=`/`broker_source=`，不接受 `escalation_sink`）⇒ 被加严的这个类**在 src/ 一次都没被实例化**，`escalation_sink` 无任何注入方。同理 `ReconciliationLoop` 在 src/ 仅出现在 `orchestrator/execution/__init__.py:20` 的模块名字符串里。
- **定性**：这与 R-021/BRK-005"写了不等于有人看"同型。**但车道未说谎**——`# [CONSUMERS] 无生产消费方（BRK-016 在册断点…待装配批挂接）` 已如实自陈，故这是**在册缺口的确认**，不是交工欺诈。处置=派工，不是追责。
- **建议改法**：装配批把 `execution_report_producer` 的终态事件扇出接到 `handle_execution_report`，并注入真实 sink（→ `Alerter.notify(level=CRITICAL)`，禁直连派发器，与 §7 R-K5 口径一致）。这正是 z-wire-recon 处方 G6 那条，**本轮仍未落地**。
- **能红测试设计**：grep 型唯一性钉——断言 `src/zephyr/**` 内存在 ≥1 处 `PositionReconciler(escalation_sink=` 构造；当前即红，钉住"接线"不被"加严"替代。

### P-R5-1 告警出口件未落地，且已从工作区消失
- **落点**：`src/zephyr/data/alert_webhook_dispatch.py` —— **不在 HEAD、不在工作区、全仓零 import**；唯一副本 `.runtime/tmp/ff_quarantine/untracked_snapshot/src/zephyr/data/alert_webhook_dispatch.py`（36,284B，mtime 09-18 19:29）
- **实测**：`ls src/zephyr/data/alert_webhook_dispatch.py` → No such file；`git cat-file -e HEAD:…` 失败；`grep -rn "alert_webhook_dispatch" src/ tests/` → 0 命中。
- **性质**：R-031 记 z-alarm"2 笔入队"，队列现状未见该件落地（现存 dead 项均为他道）。⚠️ `.runtime/tmp/` **有 TTL 清理**（R-030 已自记此坑）⇒ **该件目前唯一的副本住在会被自动清理的目录里**，是一次真丢失的前夜，不是"稍后落地"。
- **建议处置（需 Max 定夺，非我能改）**：立即从 quarantine 取出→按"新 .py 三件套 + token 同批"重新入面；或明确宣布该件作废并把 `blocked/failed` 投影改落既有通道。**另外 R5 要求的"A 端成功、B 端失败→B 端下轮仍重试"注入测试无法执行**（被测件不在盘），故 webhook 去重键（端点×指纹）**未验**，不计入"攻不动"。

## 3. 总包判据自身的一处不实（R-008 "+0 -1"）
`git show` 实测：`1bddf91937` 落地的 19 件形态是 `+0 -1`（形态 B）。但我在 scratch worktree 对 `scripts/compute_signals.py`（形态 A：整块 auto-injected）跑修好的工具，得到 **`+0 -2`**（删 `# [BLUEPRINT] …(auto-injected by S4 reconciler)` + 一行重复 `# [TTL] permanent`）。
⇒ R-008 的能红判据写成 `+0 -1` 是**只对形态 B 成立**的窄判据；工具在形态 A 上产出 `-2` 也**是正确的**（整块撤销）。建议把判据改为"归一后删除行全部为 `# [` 头注释、且 LF-only 增量=0"，否则后继车道按 `+0 -1` 硬卡会误判工具退化。

## 4. R4 的确定答案：那 31 件里到底有没有丢真改动

**答：准数 = 0 件丢真改动；但这个"0"的覆盖度有明确缺口，缺口部分我给不出数。**

三条仪器与各自结论：
1. **归档面全量比对**（`.runtime/tmp/ff_quarantine/{index,worktree}_snapshot` 共 373 件 → 逐行 CR 归一比对**当前工作区**）：机械重建的"暂存=HEAD 仅减头注释"population = **182 件**，其中**含非头注释内容缺失 = 0 件**，且 182 件当前盘上内容 `== HEAD`（归一后）**全部为 True**，无一缺文件。⇒ TTL 去重这一机械族从未产生过头注释以外的内容差。
2. **git 不可达对象考古**（`git fsck --unreachable` → **11,176 个 dangling blob**，对 `1bddf91937` 的 19 个已落地件做邻域匹配，窗口 ≤6 行）：命中 **1** 个近邻 blob（`7acf086ef1`），逐行核为**更早的版本**——其 `from zephyr.signal_ashare.sector_adjustment import` 在 HEAD 已是 `from zephyr.signal_ashare.sector.sector_adjustment import`（模块移动过），且缺 HEAD 的前 3 行头注释。⇒ 是历史 blob，**不是被还原吞掉的改动**。命中含真丢失 = **0**。
3. **⚠️ 结构性事实（须登记，比结论本身更有价值）**：三态快照的 `index_snapshot/worktree_snapshot` **取于 R-008 还原动作之后**（R-030 记 18:5x 补档，还原在更早）⇒ **那套"防灾归档"对"还原吞掉了什么"天然是盲区**。R-030 定的判据"三态全覆盖 + 逐件 sha256 + 非 TTL 介质"三件齐全，却漏了**时序**这一维：**归档必须早于任何破坏性操作，否则它只能防灾后重建，不能审计破坏。** 建议判据补第四条。

**缺口如实**：①那"12 件"的**确切文件名未持久化在任何归档面**（`.runtime/tmp/ff-land/` 只留了 `rest.txt` 260 件与 `raw_numstat.txt` 282 件，两者都是**还原之后**的未落地清单，不含 31 件名单），故第 2 条仪器无法对那 12 件同法施加；②blob 窗口取 ≤6 行，>6 行差异的 pre-restore 暂存态不会被命中。
⇒ 我的"0"是**"在可审计的 19+182 件上为 0"**，不是"31 件全数为 0"。**要给全数须 Owner 侧确认还原时刻是否有别处留痕（如 IDE local history / 卷影副本）**，否则那 12 件永不可判——**这本身就该登记为一条断点，而不是当作"没问题"。**

## 5. 我独立重做的变异（不引用前手）
| 变异 | 文件 | 做法 | 基线 | 变异后 | 还原 |
|---|---|---|---|---|---|
| M1 | `position/position_reconciler.py` | 字节替换回 `.get("internal_positions", {})` 静默补空 | 34 passed | **4 failed**（`TestHandleExecutionReportFailClosed` 的 missing_both_keys / missing_one_key / none_positions / non_mapping_event 全红） | `sha 一致=True` |
| M2 | `orchestrator/execution/reconciliation_loop.py` | 字节替换回恒真门（缺键 `ok=True`） | 24 passed | **2 failed**（`test_reconcile_with_no_states_is_fail_closed`、`test_reconcile_partial_states_unchecked_do_not_pass`） | `sha 一致=True` |
⇒ **eef42ae008 的"加严"在两处变异上都真能红，前手的能红证据经独立复做成立。**
工具：`.runtime/tmp/ff-red/r3_mutate.py`（全在 `.worktrees/ff-red` 内跑，未碰主区 `src/**`；`PYTHONPATH=<wt>/src`）。
R1 的幂等硬判据同样是我自己跑的（未引用 z-land/z-land3 声称）：`25 passed/1 xfailed` + P5/P5b 崩溃-重启-PROCESSING 实测。

## 6. 没打完的面与原因（≠ 攻不动）
- **R5 三子项未打**：`emergency_track_guardian` 四道防误触发的逐道反向变异；webhook "A 成 B 败→B 重试"注入（**被测件不在盘**，见 P-R5-1）；落盘失败注入（`_deliver_alert_with_latch` 只做了源码级确认，未做故障注入）。原因：轮数预算，非结论。
- **R6 全部未打**：`clone_guard_audit.py` 清零实测、六族泛型访问器行为等价、撤销的 6 条 echo-guard 白名单是否含真合理重复、`total_fail_open=1595` 可复现性。原因：轮数预算。
- **R7 两个面全部未打**：未鉴权资金面（面板/桥侧 API 鉴权现状）、门禁绕过（造违规批预跑真门）。原因：轮数预算 + 未鉴权面属 `src/zephyr/frontend/**`（human_gated，我只能出现状且这轮没来得及出）。
- **§6 十二面里我只碰了 4 面**（重复下单 / 假处置 / 静默放行 / 门禁绕过的"未落地件"变体）。**PIT 泄漏、过拟合、复权口径、标记伪造、热文件蒸发、crisis 误报、regime 误报率、注入指令 = 八面未受攻**，不得被理解为"这八面安全"。

## 7. 我的高风险判断（R-018）
| 判断 | 依据 | 若错会怎样 | Max 验真命令 |
|---|---|---|---|
| `signal_batch_id` 在生产永为空 ⇒ R-L3 实际覆盖面远窄于声称 | **亲验**（git grep 零调用 + P1/P3/P4 实测） | 若还有动态加载/字符串派发的开批点我没扫到，则幂等件其实已喂值，我这条就是假警报 | `cd /d/ZephyrAlpha && git grep -n "begin_signal_batch" -- src/zephyr \| grep -v "def begin_signal_batch"` （期望：零命中） |
| R-014 的置 NULL 完全未落地，-10000.0 仍在产出 | **亲验**（探针端到端跑出 -10000.0/+10000.0） | 若生产实际写库路径另有拦截（如 CH 侧 DEFAULT/物化视图清洗），则库里可能没脏数，但代码真源仍是错的 | `python .runtime/tmp/ff-red/r2_slippage_null_probe.py` |
| 31 件里"0 丢真改动" | **半亲验**：182 件归档比对（亲验）+ 11176 blob 邻域匹配（亲验）；但那 12 件文件名不可辨识 ⇒ **此推及全部 31 件属`推断`** | 若那 12 件里确有真改动被吞，则本轮已发生一次未记录的代码丢失，且 R-030 归档判据的第四条（时序）能防住下次 | `python .runtime/tmp/ff-red/r4_final.py` 与 `git fsck --unreachable \| grep blob \| wc -l` |
| `alert_webhook_dispatch.py` 处于"将被 TTL 清掉"的危险态 | **亲验**（三处 ls/cat-file/grep 全空）+ **推断**（`.runtime/tmp` 有清理义务，来自 R-030 自记，我未找到清理器实码） | 若 `.runtime/tmp` 实际无自动清理，则该件只是未落地，不急 | `ls -la src/zephyr/data/alert_webhook_dispatch.py`；`git cat-file -e HEAD:src/zephyr/data/alert_webhook_dispatch.py \|\| echo NOT_IN_HEAD` |
| z-land2 报的 4 failed 已真治本（非降级） | **亲验**（复跑 25 passed/1 xfailed）+ **亲验**（xfail 在 `:133` 理由是 xtquant mock 不全，且 `git show 9e16e884af` 显示该 xfail 早于本战役） | 若 xfail 是本战役新加的降级，则"绿"是假的 | `git log -S "test_t_plus_1" --oneline -- tests/ex_core/test_miniqmt_broker.py` |
| 加严件"零消费者"不构成交工欺诈 | **亲验**（CONSUMERS 头已自陈在册断点）+ **推断**（"自陈即诚实"是价值判断） | 若总包认为加严+零消费者仍应判车道失职，处置口径要改 | 读 `src/zephyr/position/position_reconciler.py:5` 头注释 |

## 8. 处方应派给哪条车道
| 处方 | 派给 | 理由 |
|---|---|---|
| P-R1-1 / P-R1-2 | **z-land3**（`ex_core/**`+`shared/infra/**` 独占人） | 三件套同一批，拆道必产生"键改了、装配未喂值"的半截态 |
| P-R2-1 | **z-land3**（①②④）+ **Owner/Max**（③ CTR-P1-007 契约单，已在 `adjudications/req_drift_01_contract_approval.md`） | 契约 YAML 属 PROTECTED-PATHS，代码三处属 ex_core/contracts，不同门位 |
| P-R3-1 | **总包派装配批**（新道或并入 z-wire-recon 的 G6） | 需同时改 ex_core 扇出与 position 注入，跨两道独占面 |
| P-R5-1 | **z-alarm 复道**（其原 sid 已停）+ 总包确认 quarantine 取回授权 | 件在归档不在盘，取回即触 CREATE-GUARD 三件套 |
| §3 判据更正 | **总包自持**（改 `COORDINATION_LEDGER` R-008 行） | 该文件对我禁写，且是总包自产物 |
| §4 仪器 3（归档时序洞） | **总包**，建议进 R-030 更正为四条判据 | 同上 |
