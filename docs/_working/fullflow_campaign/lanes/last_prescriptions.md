---
ttl: task_bound
completeness_note: 只收本车道亲手复跑过、能给现场证据的条目
completes_when: 最后一条收口红判读被总包采纳或转裁定，且两轮逐目录回归结论入册
---

# 收口第二班 · 处方与登记（车道 `st-ff-last-20260918`）

> 接班 `close1_prescriptions.md`（它把 round1 的 3 条红修到 round2 只剩 1 条）。
> 表述纪律（#325）：不写"全绿/零问题已达成"，只写"本轮检出 N 件通过且已被证明能红"。

## 1. 判读结论：最后一条红 = 假设甲（危机闸正确拦单被测试当成失败），乙/丙均被实测否证

红件：`tests/backtest/test_sim_paper_ledger.py::test_replay_pipeline_consistent`
（`assert res["rows"] and res["events"]` ⇒ rows=53 非空、events=[]）。

探针 `.runtime/tmp/st-ff-last-20260918/probe_ab.py`（六种模式，全部只读，零生产写），
结果表（`real` 口径 = 当前工作区；含 pf_alloc 在途未提交件，见 Q-3）：

| 模式 | 做法 | rows | events | blocked_days | 结论 |
|---|---|---|---|---|---|
| `real` | 现读 CH 真链 | 53 | **0** | `['2026-07-17']` | 现场复现总包 00:5x 单跑 |
| `prewo2a` | 载 `e1a975b158^` 版 `sim_paper_ledger.py` 跑同一窗口 | 53 | **2** | 无该键 | 行为改变边界=WO-2a 那一笔 |
| `fake_normal` | 注入 resolver 恒返 normal(p_r10=0.02) | 53 | **2** | `[]` | 放行腿=一进一出（07-17 入 / 08-13 强平），权益 1,000,000→1,073,747.03 |
| `fake_crisis` | 注入 resolver 恒返 crisis(p_r10=0.60,dominant=r10) | 53 | **0** | `['2026-07-17']` | 与 `real` 逐项同形 ⇒ 甲成立且只有这一个变量在起作用 |
| `blockimport` | 装拦截器：任何 import `zephyr.regime.core.regime_detector` 即抛 | 53 | 0 | `['2026-07-17']` | `regime_detector_import_attempts=[]` ⇒ 该模块**根本不在这条链上** |
| `oldregime` | 把 `eb9e18f846^`（R-055a 之前）版 regime_detector 预置进 sys.modules 再跑 | 53 | 0 | `['2026-07-17']` | 与 `real` 逐字节同结果 ⇒ **乙否证**（前手"换回 HEAD 版同样失败"的结论方向对、归因错） |

- **甲（成立）**：危机闸 L3 拦掉了窗口内唯一 panic 信号日 2026-07-17 的入场。
  拦截机制落地于 `e1a975b158`（WO-2a，**2026-09-18 02:40:45**），比 `eb9e18f846`（R-055a，23:25:26）早 **20h45m**。
- **乙（否证，两条独立路数）**：
  ① 代码面：`blockimport` + `oldregime` 如上——R-055a 改的 `regime_detector.py` 在回放全程既不被 import、
     换旧版也不改变结果；`resolve_crisis_state` 走的是 `allocation_inputs.load_regime_input`
     的 **PIT 读已落库快照**（`c1_backtest.regime_snapshot_history`），R-055a 改的是快照**生产者**不是读者。
  ② 数据面（本车道自跑 DatabaseService，只读）：2026-07-17 那行判据 `dominant='r10' / p_r10=0.600 /
     run_id=VAL-P0-20260916-230726 / ingest_ts=2026-09-16 15:08:06 UTC`——**比 R-055a 落地早两天**；
     再早一版（2026-09-12 07:41 ingest）同样 `r10/0.600`。窗口内 `dominant='r10'` 的快照共 71 行。
     ⇒ 拦单事实与今晚的加严无关，且不是单日噪声。
- **丙（作为根因否证，作为缺陷成立）**：见 §2。

## 2. L-1 `crisis_gate.py` 留痕日期类型缺陷（真缺陷，独立于本测试成立）——**只出补丁未落地，原因见 Q-3**

- **根因**：`log_crisis_gate_row` 把 `validate_date_literal(trade_date)` 的返回值（**`str` 'YYYY-MM-DD'**，
  它是给 SQL 模板做字面量插值用的）直接塞进行元组第 2 位，而该列 DDL 是 `trade_date Date`
  （`schemas/categories/crisis_gate_log.py:48`）。ClickHouse 客户端在**本地序列化**时对 Date 列取
  `value.year` ⇒ `AttributeError: 'str' object has no attribute 'year'`，被函数内
  `except Exception` 兜住、只留一条 warning。
- **真实驱动路径最小复现**（`Client('127.0.0.1').connection.context` + `columns.service.write_column`，
  不连服务端、零写入）：
  ```
  '2026-07-17'            -> AttributeError: 'str' object has no attribute 'year'
  datetime.date(...)      -> serialize OK
  datetime.datetime(... tz=UTC) -> serialize OK
  ```
- **补丁（一行，已验可用）**：行元组里 `day` → `date.fromisoformat(day)`
  （`day` 仍是已校验字面量，SQL 读路径的字符串口径不受影响）。
  验核：加载打过补丁的模块副本 → `row slot 类型 = [datetime, date, str, float, str, str, str, str]`，
  Date 列序列化通过（后续报错是我假 writer 的 BytesIO 缺 `write_strings`，与缺陷无关，
  同一 harness 下 `'2026-07-17'` 直接死在 Date 列）。
- **它不是 events=[] 的根因**：`fixcheck` 模式把留痕换成"修好的实现"再跑真链 ⇒
  `rows=53 / events=0 / blocked=['2026-07-17']`，与 `real` 完全一致（拦单发生在日循环内、留痕在循环外且返回值被丢弃）。
- **补丁件**：`.runtime/tmp/st-ff-last-20260918/backup/crisis_gate_proposed_datefix.py`（同步冷库）。

## 3. L-2 本车道对 `test_sim_paper_ledger.py` 的处置（**零断言删除**，断言 3→14 条）

原 `test_replay_pipeline_consistent` 一次现读 CH，把"账实一致"与"当日 regime 快照不是危机态"两件事
捆成一条断言。捆在**放行日**能跑，捆在**危机日**必然红——后者正是 WO-2a 想要的行为。
故：把判据拆开显式化，**不放宽任何阈值、不给危机闸加默认放行、不 xfail、不把 events 从断言里摘掉**。

| 用例 | 钉住什么 | 变异能红（`mutate.py`，按字节改+还原，sha256 复验一致） |
|---|---|---|
| `test_replay_pipeline_consistent`（改夹具不改语义） | 放行日 rows>=52 / 2 事件 / 进出台日与行动序 / 权益>初始 / 零拦单 | MT4 强平日 `>=`→`>HOLD_N+1` ⇒ 本件红 |
| `test_replay_crisis_day_blocks_entry_with_trace`（新腿） | 危机日 0 事件 + 当日 signal=cash + note 留痕 + 权益不动 | MT1 危机分支改 fail-open ⇒ 本件红；MT2 抹掉 note ⇒ 本件与第 4 件同时红 |
| `test_replay_crisis_resolver_error_fails_closed`（新腿） | resolver 抛异常 ⇒ fail-closed 拦单且 note 记 `resolver_error` | MT3 该 except 腿改 return False ⇒ 本件红 |
| `test_replay_live_chain_never_swallows_tradesilently`（新腿，仍现读 CH） | 真链禁"既无成交又无拦截留痕"的静默空转；拦单日集合==留痕日集合；被拦日不得出事件 | MT2 ⇒ 本件红（审计缺口被抓） |

- 对"是不是把尺子掰弯"的回答：原断言的**意图**是"管线不许空转"。新第 4 件把这条意图保留成
  `events 非空 ∨ 拦单留痕非空` + 集合一致性，**比原来的 `assert res["rows"] and res["events"]` 更严**
  （原式在"全被拦但留痕"下会红——即把正确行为判为失败；新式在"全被拦且零留痕"下才红）。
  原式的三处具体期望（rows>=52 / 2 事件 / 权益>初始）一条不少地搬到了放行日腿里，覆盖面净增 3 件。

## 4. 登记（不属本车道写域 / 需总包或 Owner）

### Q-1 ★★★ 沿 close1 P-9 的 index 回退快照——**本车道 01:2x 独立复测：仍未清、且比 P-9 记录更宽**
实测（`git show :<f> | wc -l` vs `git show HEAD:<f> | wc -l` vs index 内 `R-055` 出现次数）：

| 文件 | index 行数 | HEAD 行数 | index 内 R-055 |
|---|---|---|---|
| `tests/backtest/test_rb_stats_validator_teeth.py` | **不在 index** | 307 | — （净删 `307/-0`） |
| `tests/backtest/test_overfitting_detector.py` | 246 | 313 | 0 |
| `scripts/backtest/f06_e4_wfa_exam.py` | 529 | 643 | 0 |
| `src/zephyr/backtest/core/overfitting_detector.py` | 439 | 490 | 0 |

`git diff --cached --numstat` 按删除列排序，P-9 未列的**新增两件**：
`src/zephyr/data/implementations/akshare_alt_provider.py`（**186 删 / 0 增**）、
`tests/zephyr/data/test_silent_latch_before_delivery.py`（265 删 / 0 增）。
`.ailocks/registry.json` 的 `locks` 此刻 **0 条** ⇒ 这批 staged 字节无在活 owner。
本车道一律未动（外来条目 owner 责任制）。

### Q-2 ★ 缺陷告警文案的**归因是假的**：`crisis_gate_log` 表其实存在
`crisis_gate.py:402` 的 warning 写"表可能未注册 DDL，由总统筹 apply"。实测
`EXISTS TABLE c1_backtest.crisis_gate_log = 1`、`system.tables` 里就在。
⇒ 真正的病是日期类型（§2），**总包不需要为这条红去跑任何 DDL**。
文案在缺陷未修时会持续把施工者往"建表"方向带（与本役"归因错误"家族同根：close1 P-1 是第二例）。
处方：修 §2 的同时把该 warning 文案改成"按异常类型分档（序列化错≠表缺失）"。

### Q-3 ★ 本车道**让路**未落地的一条：`src/zephyr/pf_alloc/**` 工作区有非本车道在途改动
任务书 §3 授权我改 `crisis_gate.py` 的留痕日期缺陷，但 §5 的并发条优先：
`crisis_gate.py` / `allocation_inputs.py` / `allocation_orchestrator.py` 三件工作区相对 HEAD
**已有 +89/-16 的未提交改动**，内容自陈为红队车道 `st-ff-rb-safe-20260918`（攻面一①③⑤：
`data_degraded` 退化外显 + 旁路无痕加严）——**它已阵亡（R-053/R-058）未交工**。
`git add` 该文件会把它的整批在途工作署到我名下，故本车道只交补丁件不落地。
⇒ 请总包二选一：① 按 R-049/R-053"救回≠可落"流程复跑 rb-safe 那批并同批带上 §2 一行；
   ② 或按其归属单独成批。
旁证：`scripts/backtest/f06_e4_wfa_exam.py` 旁躺着 `*.tmp.19900.1789737759293`（safe_write_text 崩溃残留），
属同一在途现象，本车道未清（禁 rm 于并发窗口）。

### Q-4 告警外发 fail-closed 在测试期刷屏（**正常工作，登记噪音**）
每次模拟盘回放遇危机日 ⇒ `alerter` CRITICAL + `alert_webhook_dispatch`
`action=blocked reason=enabled=false endpoints=[]` 各一条。`0808dd8757` 行为符合"缺省不外发但必须出声"。
登记点：① 测试里未抑制该出声，长跑日志会被它污染（本车道 `-q --tb=line` 下仍进 stdout）；
② 若 Owner 要"真出声"需给 `config/alert_webhook.yaml` 端点——那属人类门位（tier=human，台账 A 类）。

### Q-5 提交前进程内门禁预跑器仍在 TTL 目录
`.runtime/tmp/ff-recon/backup_prerun/gate_prerun.py`（97 行 / 113 GateSpec）。
总包 R-069b 已裁"必须入库"，本车道实测它仍在 `docs/registry_of_registries.yaml` 与 HEAD 皆不可见的位置。
本车道用它做提交前预跑（见 §6 提交记录）。

### Q-6 沿 P-6/P-7/P-8 的三条（本车道 round1 未复现，如实记"本轮未触发"而非"已消失"）
- P-6 MSG-STYLE 子串自豁免：脚本 basetemp 已哈希命名 ⇒ 两轮 0 触发；**门禁源码那处 `in "commit_gates/"` 仍在**（收紧处方归总包）。
- P-7 `test_key_hierarchy` key_id 随机含 `dek`：两轮未触发（≈1.1e-4/次量级，不指望它消失）。
- P-8 `test_errcode_consistency_gate::test_current_repo_is_clean` 观测面=live index：两轮未触发，
  但 Q-1 那批 staged 回退快照还在 index 上 ⇒ 它随时可能被再次连坐。

### Q-7 ★★★ `batch_creation_tokens.py` 的"纯插入"会**吃掉锚点之后、段尾之前的既有 token 条目**（本车道实弹抓到并已原位修复）
- 现场（01:3x）：`python scripts/governance/d3_metadata/batch_creation_tokens.py --prefix
  docs/_working/fullflow_campaign/lanes/last_prescriptions.md --created-by st-ff-last-20260918
  --capability fullflow-last` 报 `落盘: True (CAS attempt 1) / 已插入 1 条（锚点 capability: fullflow-close1）`，
  但落盘结果把前一条 **`file: docs/_working/2026-09-18-gate-identity-root-fix-plan.md`
  （created_by=st-ruledisp-20260918，2026-09-19 01:12:48 刚进 HEAD）**整条 4 行删除**（净 -4/+0）。
- 后果：`REGISTRY-MASS-DELETION` 在本车道提交前预跑里当场硬拦（`8083 -> 8082，条目身份消失 1 条`）⇒
  **如果我不跑进程内预跑（`run_gate_chain.py` 预跑不到它），这 4 行会在我的提交里静默蒸发**，
  而该册是唯一真源的 CREATE-GUARD 凭据面 ⇒ 那条车道的新建件从此"无 token"，下次触碰即死信。
  这正是台账 R-063"热册条目被外来非 CAS 写蒸发"家族的**又一例，且肇事者是官方登记工具本身**。
- 机制定位（未改工具，属他道写域）：`insert_block()` 的注释与 `_MODIFY_GUARD` 都自陈"纯插入"，
  实现在**锚点不是段内真正最后一条**时会把"锚点行之后到段尾（`di_seam_exemptions:`）之前"的内容整体替换掉；
  其写后自检 `_self_check` 只查"我的条目在不在/是否落进段外死区"，**不查"别人的条目有没有少"** ⇒ 漏网。
- 处方（择一，交工具 owner/总包）：① 自检补一条"段内条目数与身份集合只增不减"（把 REGISTRY-MASS-DELETION
  的判据前移到写侧，与 R-063 治本同方向）；② 或锚点强制取段内**最后一条** `capability` 行并断言其后仅剩段尾键。
- 本车道处置：已按 A 型（盘上比 HEAD 旧）正解恢复——用 `safe_write_text`（CAS）把文件重写为
  `HEAD 字节 + 我的 4 行纯插入（插在 gate_identity_root_fix 之后）`，
  复验 `git diff HEAD --numstat` = **4/0**、`grep -c gate-identity-root-fix-plan` = 2（原样在位）、
  预跑 REGISTRY-MASS-DELETION 由 FAIL → PASS。**未使用任何破坏性 git 命令**。

### Q-8 ★ 该登记册此刻正被两条他道并发追加（01:12:04 `dd39de9b6c`、01:3x `85cd86f522`），
本车道因此在同一份册上吃了两次"基线过期"：第一次是工具吃掉外来条目（Q-7），
第二次是**外部自动 `git add` 把修复前的坏快照推进了 index**（`git diff --cached --numstat` 显示 `0 4`），
第三次是修复后的基线又被 `858cd…` 的新条目越过（staged 变 `4 4`）。
⇒ 可复用判据（进手册 §4 候选）：**热册入批必须"以当下 HEAD 重建 + `git add` + 立刻复查
`git diff --cached --numstat` 必须是 `N/0` 纯插入"**，且 `git add` 之后 HEAD 再动就要重来一遍；
只看工作区 diff 会被 index 面背刺（门读的是 index）。本车道未动任何外来 staged 条目。

## 5. 两轮逐目录回归（本车道自己重跑，未引用任何前手数字）
见 `round1.jsonl` / `round2.jsonl`（`.runtime/tmp/st-ff-last-20260918/`，同步冷库
`G:/zephyr_cold/st-ff-last-20260918/`）。脚本 `.runtime/tmp/ff-recon/loopcheck.py`（`--lane fflast`）。

### 5.0 脚本自证（第 1 轮前）
| 步 | 结果 |
|---|---|
| `--only ai_layer` | rc=0，12 collected / 12 passed / 2.6s |
| `--only d3_metadata`（tmp_path 重灾区再证） | rc=0，190 collected / 190 passed / 15.2s |

### 5.1 第 1 轮（起算 HEAD=34c2728580；跑时 pf_alloc 三件为他道在途未提交字节，见 Q-3）
| 目录 | rc | collected | passed | failed | error | skip+xfail | 耗时(s) |
|---|---|---|---|---|---|---|---|
| `tests/regime` | 0 | 1036 | 1036 | 0 | 0 | 0 | 44.1 |
| `tests/backtest` | 0 | 1836 | 1836 | 0 | 0 | 0 | 249.1 |
| `tests/governance/commit_gates` | 0 | 2584 | 2584 | 0 | 0 | 0 | 80.0 |
| `tests/plan_engine` | 0 | 732 | 732 | 0 | 0 | 0 | 12.2 |
| `tests/ex_core` | 0 | 1304 | 1303 | 0 | 0 | 1 | 25.3 |
| `tests/pf_alloc` | 0 | 401 | 401 | 0 | 0 | 0 | 22.0 |
| `tests/security` | 0 | 177 | 175 | 0 | 0 | 2 | 9.5 |
| `tests/model` | 0 | 883 | 882 | 0 | 0 | 1 | 11.9 |
| `tests/data` | 0 | 566 | 566 | 0 | 0 | 1 | 28.6 |
| `tests/strategy_factory` | 0 | 55 | 55 | 0 | 0 | 0 | 3.8 |
| `tests/ai_layer` | 0 | 12 | 12 | 0 | 0 | 0 | 2.6 |
| `tests/risk` | 0 | 1857 | 1857 | 0 | 0 | 1 | 71.1 |
| `tests/automation` | 0 | 375 | 349 | 0 | 0 | 26 | 67.4 |
| `tests/governance/d3_metadata` | 0 | 190 | 190 | 0 | 0 | 0 | 16.0 |
| `tests/strategy_pipeline` | 0 | 155 | 155 | 0 | 0 | 0 | 19.3 |
| `tests/governance/test_shared_yaml_utils_reexport.py` | 0 | 66 | 48 | 0 | 0 | 18 | 5.6 |
| **合计(16)** | **全 rc=0** | **12229** | **12181** | **0** | **0** | **50** | **668** |

### 5.2 第 2 轮（同脚本同清单同 `--lane fflast`；起算 HEAD=34c2728580，跑至 01:24:44 期间他道落 1 笔 dd39de9b6c，只含 1 个 .md + 登记册 4 行，不涉任何测试目录）
| 目录 | rc | collected | passed | failed | error | skip+xfail | 耗时(s) |
|---|---|---|---|---|---|---|---|
| `tests/regime` | 0 | 1036 | 1036 | 0 | 0 | 0 | 66.6 |
| `tests/backtest` | 0 | 1836 | 1836 | 0 | 0 | 0 | 275.2 |
| `tests/governance/commit_gates` | 0 | 2584 | 2584 | 0 | 0 | 0 | 107.6 |
| `tests/plan_engine` | 0 | 732 | 732 | 0 | 0 | 0 | 15.0 |
| `tests/ex_core` | 0 | 1304 | 1303 | 0 | 0 | 1 | 26.7 |
| `tests/pf_alloc` | 0 | 401 | 401 | 0 | 0 | 0 | 22.7 |
| `tests/security` | 0 | 177 | 175 | 0 | 0 | 2 | 10.1 |
| `tests/model` | 0 | 883 | 882 | 0 | 0 | 1 | 13.6 |
| `tests/data` | 0 | 566 | 566 | 0 | 0 | 1 | 29.6 |
| `tests/strategy_factory` | 0 | 55 | 55 | 0 | 0 | 0 | 4.3 |
| `tests/ai_layer` | 0 | 12 | 12 | 0 | 0 | 0 | 2.9 |
| `tests/risk` | 0 | 1857 | 1857 | 0 | 0 | 1 | 74.9 |
| `tests/automation` | 0 | 375 | 349 | 0 | 0 | 26 | 69.9 |
| `tests/governance/d3_metadata` | 0 | 190 | 190 | 0 | 0 | 0 | 17.1 |
| `tests/strategy_pipeline` | 0 | 155 | 155 | 0 | 0 | 0 | 21.8 |
| `tests/governance/test_shared_yaml_utils_reexport.py` | 0 | 66 | 48 | 0 | 0 | 18 | 6.0 |
| **合计(16)** | **全 rc=0** | **12229** | **12181** | **0** | **0** | **50** | **764** |

### 5.3 达标判定（按 #325 表述纪律）
- 两轮各 16 目录、同脚本、同清单、同 `--lane fflast`、同 basetemp 命名空间；
  两轮 **rc∉{0,5} 的目录数=0**、**failed=0**、**error=0**、collected 两轮同为 12229（=close1 round2 的 1833/12226
  口径加本车道新增 3 件测试）。skip/xfail 构成两轮逐目录一致（automation 26、shared_yaml 18、security 2、
  ex_core/model/data 各 1、risk 与 data 各含 1 件"收集期 skip"与 collected 口径重叠）。
- **连续两轮"该 16 目录套件本轮检出 12181 件通过、0 失败 0 错误"已达成**，且这些通过不是空断言：
  本车道自家 4 件回放守卫由 MT1-MT4 四个变异分别证明能红（`mutate.py`，按字节改+还原+sha256 复验）；
  脚本自身先经"已知绿套件不产假红"自证（§5.0）。
- 未做的口径：本表只覆盖 16 个被役改过的目录，不等于 `tests/` 全量（宪法 §6 与手册 §6：
  单进程 `pytest tests/` 必然收集失败）。

## 6. 提交记录（本车道共 1 笔，≤2 笔授权内）
- 批 1 入队 `q-20260919-st-ff-last-20260918-0001` → **`state=done` / landed=`cbddfa2a2b16fcffcb8ef7bc106a85142f93dc03`**。
  归属核实 `git log -1 --name-only cbddfa2a2b` = **恰好 3 件、零外来吸收**：
  `tests/backtest/test_sim_paper_ledger.py`(+90/-13)、
  `docs/_working/fullflow_campaign/lanes/last_prescriptions.md`(新 228 行)、
  `capability_canonical_file_registry.yaml`(+4/-0 纯插入 token)。
- 提交前预跑：`.runtime/tmp/st-ff-last-20260918/gate_prerun.py`（113 GateSpec，进程内门）
  → 第 1 次 1 条硬阻断（REGISTRY-MASS-DELETION，即 Q-7）→ 修复后 **0 硬阻断 / 0 环境信号 / 0 gate 异常**。
  这条预跑**就是 Q-7 不被静默吞掉的唯一原因**（`run_gate_chain.py` 预跑不到进程内门）。
- 落地后复验：`pytest tests/backtest/test_sim_paper_ledger.py` **13 passed**（HEAD=cbddfa2a2b 字节）；
  claim 已全部 release（`--release-only` released=3，`.ailocks/locks`=0）。
- 轮数纪律：本车道交工时约第 6x 轮（≤110 轮门槛内），未攒批——测试件写完即 `git add`、判清即入队。
