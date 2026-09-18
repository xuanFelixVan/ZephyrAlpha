---
ttl: task_bound
completes_when: 全流通战役收官且最终交付报告落盘
---

# 静默失效模式扫查（车道 st-ff-silent-20260918）· 五模式普查与收口

> 触发实例 = R-023 的 `scheduler.py` CH 探活告警「先置闩再投递 + except pass」。
> 本车道查的是它的**可泛化缺陷类**：*在投递之前就把"已处理"标志置上*，及其四个同族。
> 分工边界：z-failopen 已改 7 处"告警/熔断自身被吞"（`lanes/failopen_triage.md` §3），
> 本车道只管"闩 / 标志位 / 恒真返回 / DEBUG 放行 / 预设失败类别"，**未重复改它那 7 处**。

## 0. 口径声明（先读这节，否则数字会骗人）

| 项 | 值 |
|---|---|
| 扫描根 | `src/zephyr/**` + `scripts/**` |
| 排除面 | `.aidrafts/`、`.worktrees/`、`__pycache__`、`data/c4_pdf_cache/` |
| 实扫 .py 文件数（grep 口径） | **4657** |
| AST 口径 | 同一文件集逐个 `ast.parse`（SyntaxError 跳过并计数） |
| 扫描器 | `.runtime/tmp/ff-silent/silent_scan.py`（本车道临时件，未入库） |
| 原始命中 JSON | `.runtime/tmp/ff-silent/scans/scan_all.json` |

**判读纪律**（承 R-019/R-023：命中数本身无意义，普查既可能漏计也可能放大）：
每个模式两个口径都给，差值必须解释，真病例一律附逐条人工判读理由。

---

## 1. P1 闩前置（latch-before-delivery）—— 本车道主案

### 判据（AST 严判）
同一函数体内，**闩类写入**（①对名字命中 `alerted|latch|seen|dedup|already|warned|notified|last_*|_ts|_stamp|flag|acknowledged|suppressed|reported` 的目标赋值；②对该类容器的 `.add()/.update()/.setdefault()/.append()` 原地变更）
行号 **早于** 投递调用（`notify|send|dispatch|publish|deliver|alert|escalat|emit|post_|trigger`），
且该投递的**返回值未被消费**（不是赋值右侧、不在 if/test、不在 return/bool 表达式里）。
附加标注：投递是否被 `try` 包裹、handler 是否重置闩、handler 是否只有 `pass`。

### 命中数
| 口径 | 数 | 差值解释 |
|---|---|---|
| grep 启发式（行首闩赋值 `= True|time.|now_utc|datetime|monotonic` + 其后 30 行内出现投递调用） | **4** | **严重漏计**：grep 只认"赋常量 True"一种形态，漏掉 `dict[key]=…`、`set.add()`、`tuple 解包赋值`、"写入已落盘的状态文件即视为置闩"等形态 |
| AST 严判（原始） | **78** | 含同一 (file,func,latch) 的重复计数 |
| AST 严判（按 file+func+latch 去重） | **61 组** | **判读基数**。其中 24 组投递被 try 包裹 → 逐行读码；具名 `alerted/last_pressure_level/_dedup_state` 的另 8 组亦逐行读码 |

### 真病例（3 处，全部已收口）

| # | file:line | 改前（缺陷） | 改后 | 危害 |
|---|---|---|---|---|
| F1 | `src/zephyr/data/source_health_check.py:107-119` | `alerter.notify(...)` **返回值被丢弃**，随后无条件 `alerted = True`，且该闩在 `:120-128` **写进 `_STREAKS_PATH` 持久化 JSON** | `delivered = alerter.notify(...)` → `alerted = bool(delivered)`；未落盘走 `log.error` 明说"保留未告警态，下一轮重试" | **比触发实例更严重**：scheduler 那例只在**进程余生**内静默，本例把"已告警"**落盘** → 数据源连续 N 天异常的告警一旦未写盘，**跨进程重启永久静默**，除非人工改 JSON |
| F2 | `src/zephyr/data_eng/data_anomaly_alerter.py:373 + 397-413` | 路由之前先 `self._dedup_state[key] = (now_ts, new_count)` 推进合并窗戳；`_alert_sink` 抛异常时戳已吃掉 → 合并窗内后续同键信号全被 `merged → continue` 抑制 | 改为"送达成功或有意跳过才推进戳"：`silenced/merged` 分支内写戳；sink 异常分支 `continue` 不写；try 成功后写 | 数据异常告警器（四路检测的出口）**首条未送达即静默整个合并窗**（默认 3600s） |
| F3 | `src/zephyr/trading/resource_optimization.py:537-552` | `engine.last_pressure_level = snap.pressure` 在 `bus.emit(...)` **之前**；except 只打 `logger.warning("suppressed error in resource_optimization")` | 档位只在 emit 成功后推进；失败分支打真实类型名 + `exc_info` 后 `return`（保留旧档位=下轮重试） | 自愈回路的资源压力事件：emit 失败 → 同一压力档位在进程余生不再外发（去抖闩吃掉重试） |

顺手同治（属 P5 纪律，随 F1/F2/F3 一并落）：`source_health_check.py:130`、`data_anomaly_alerter.py:413`、`resource_optimization.py:551` 三处兜底日志改为
`%s: %s + type(e).__name__` + `exc_info=True`，不再丢类型。

### 假阳与排除理由（61 组中余下 58 组）

| 类别 | 代表 | 排除理由 |
|---|---|---|
| **计算型判定标志**（不是"已处理"闩） | `data_eng/incremental_update_engine.py:156`、`pf_core/core/rebalance_cost_analyzer.py:227`、`gov_drift/agent_stability_index.py:242` | 形如 `alerted = deviation > tolerance`——语义是"**该不该告警**"，写在投递之前是正确的。**但**该字段随结果对象返回：若下游把它读成"**已**告警"就是语义漂移 → 已作为观察项写进 `silent_prescriptions.md` §P1-b（未改） |
| 事件性质标志 | `plan_engine/overnight_boundary_reviser.py:502/505/513` | `flags['high_impact_event_night']=True` 是日历事实位，不是投递回执 |
| 数据变量误命中闩词表 | `data/scheduler.py:1692 task_start_ts`、`commit_belt_daemon.py:154 oldest_ts`、`scripts/ops/ch_health_probe.py:123 max_ts`、`catchup_guard.py:197/221`、`rollback_executor.py:452 already_committed` | 名字命中 `last_/_ts` 但语义是业务量（最早时间戳/最大时间戳/已提交集），无"已处理"含义 |
| 已由 z-failopen 收口 | `data/scheduler.py` 的 CH 探活闩与 DDL 去重戳 | 它的成品；我只读不改 |
| **正确的防吞设计（阴性证据）** | `gov_enforcement/rule_bridge/worktree_drift_watchdog.py:1149-1248` | 注释明载「不更新 files_state/alerted——daemon 下轮仍按全状态告警，**防吞**」：投递失败时**故意不推进去重**。这是 P1 的正解样板，说明该模式在本仓已有先例认知，缺的是**机械复检** |

---

## 2. P2 恒真 / 硬编码返回（R-021 同族）

### 判据
- **P2a**：函数 `docstring` 声明某数据来源（psutil/redis/clickhouse/duckdb/SELECT/requests/subprocess/os.environ…）而函数体**未引用**该来源，且所有 return 都是常量/常量元组。
- **P2b**：函数体有效语句只有 1 条 `return <字面量>`（零 Name load）。
- **P2c**：`.get(key, True)` / `.get(key, "OK"|"normal"|"healthy"|"PASS")` 默认值恒真的查表判定。

### 命中数
| 口径 | 数 | 差值解释 |
|---|---|---|
| grep 启发式（`.get(x, True)` + 整行 `return True|0.0|"healthy"|"OK"`） | **1797** | **放大**：grep 不知函数是否只有这一条语句、更不知该返回值是否被当"健康/放行判定"消费 |
| AST P2a | 35 | **全 FP**——我的 used_names 未纳入**函数体内 `import x` 的局部导入名**（例：`health_check()` 文档写"尝试 import requests"，函数体确实用了局部 import）。判据须补这条，已写进 gate 提案 |
| AST P2b | **158** | 真判据基数（整函数只有常量 return） |
| AST P2c | 89 | 未逐个判读（见"未达成"）；z-wire-recon 已在 `reconciliation_loop.py` 抓到一例 |

### 真病例（恒真返回族，6 处深读确认）

| file:line | 恒真物 | 是否被当判定消费 | 处置 |
|---|---|---|---|
| `src/zephyr/trading/boot_hooks.py:132-135` | `def _boot_hooks_health_check() -> str: return "healthy"` | **是**——它被 `register_system_health("boot_hooks", …)` 注册进 HealthDiscovery，成为一条**永不失效的活体探针** | 处方 P2-R1（需先定义"boot_hooks 健康"的真实判据，属语义取舍，不在我 lane 自裁） |
| `src/zephyr/gov_enforcement/rule_enforcement/secrets_guard.py:28` | `check_env() -> True`（RULE-SECRETS"三道 gate"之一） | 未见调用方 | 处方 P2-R2（**恒真安全闸**，即便零调用也不该以"能力"面目留在册） |
| `src/zephyr/infrastructure/rollback/temporal_context_adapter.py:149` | `_verify_hmac() -> True`（HMAC 校验永不失败）+ 同文件 `:56`、`:153` **明文硬编码密钥** `b"ZephyrAlpha-TOTP-Secret-v1"` / `b"ZephyrAlpha-HMAC-TimeProof-v1"` | 类内 `_generate_totp` 用同一常量 | 处方 P2-R3（**双病例**：恒真校验 + 裸密钥，触 RULE-SECRETS；密钥我不动，交 Owner/Max） |
| `src/zephyr/orchestrator/lifecycle/system_transfer.py:29` | `verify_health_after_transfer() -> True` | BRK-003 整族零消费 | 处方 P2-R4（与"蓝图承诺 vs 代码实体"族合并） |
| `src/zephyr/gov_audit/corporate_actions.py:97` | `verify(sample_count=10) -> True`（复权因子校验永不失败） | 未见 src 内调用方 | 处方 P2-R5（**钱路径语义**：复权口径验收的红蓝攻击面正对着它） |
| `src/zephyr/feedback_loop/detectors/drift/concept_drift.py:34` | `check(...) -> 0.0`（概念漂移恒零） | feedback_loop 半族零入度（BRK-011） | 处方 P2-R6 |

另：**LSG 安全层桩群**——`security/llm_defense/llm_security/layers/{l0,l1,l2a,l3,l4,l6,l8}*.py` 与 `self_protection/l7_validation.py` 共 **30+** 个
`validate/check_*/verify_* -> True` 常量返回（P2b 口径）。这不是"一个 bug"而是"一层的默认实现是放行"。
**普查 §J 第 1 条"恒真门禁未系统扫"在此得到实证。** 本车道不改（属安全架构级取舍 + 注册表净删风险），
整体登记为处方 P2-R7，建议 Max 用 `is_fail_closed()` 反向断言逐层钉。

### 与本车道分工的收口判定
按"只收口钱/决策/告警/熔断/自愈路径"的规则：以上 P2 真病例**全部落在他人独占文件或需语义裁定**
（boot_hooks 属"该断言什么"的设计问题；LSG 属安全层承诺问题；alt_data/risk 属禁写区）→ **0 处自改，7 条处方**。

---

## 3. P3 只写不读（BRK-005 型）

### 判据
`self.<attr>` 在 `src/zephyr`+`scripts` 内**只有 Store、没有任何 Attribute Load**，且 attr 名命中告警/状态/心跳/裁决语义词表。

### ⚠️ 口径事故与纠正（本车道自曝，R-019 同型）
第一版扫描器把 reads 表的键写成 `"attr:"+name`，而判读时拿**裸名**比对 →
**每一次查找都必然落空 → 所有写方都被误判为"只写不读"**。AST 首版给出的 **448** 这个数**作废**。
实测证据：`_alert_sink` 被判为只写不读，但全仓 `self._alert_sink` 的 Load 有 **59** 处
（首处 `src/zephyr/alt_data/alt_source_health_manager.py:205`）。
已修口径（`("attr:"+attr) in acc.reads`）后重跑：**23 件**（`scans/scan_p3.json`）。

| 口径 | 数 | 说明 |
|---|---|---|
| AST 首版（**判据自身有缺陷，作废**） | ~~448~~ | 键前缀比对错 → 全判只写 |
| AST 修口径后 | **23** | 语义词表过滤后，其中**告警/自愈语义命名 9 件** |
| grep（名字级） | 不可用 | 见下"方法学结论"：名字级反查在本模式上必然失真 |

### P3 的 9 件语义命名写方（23 件之内）逐条判读

| attr | 首个写方 | 判读 | 处置 |
|---|---|---|---|
| `owner_alerted` | `feedback_loop/detectors/correlation/external_validation_checkpoint.py:107`（`_escalate()` 里置 True） | **真病例**：升级路径上"已通知 Owner"这位**全仓零读方**；`get_pending_escalations()` 读的是 log 里的 `acknowledged`，不是它 → 该位是纯装饰（BRK-005 同型，且它在**保命升级**路径上） | 处方 SILENT-P3-R1（未改：要么被消费、要么删；删除触字段净删，需 Max 判） |
| `_hk_stale_warned`、`_threshold_ledger_warned` | `regime/overlay_signals_builder.py:663 / :237` | **待判**：warn-once 闩无读方 → 无法审计"是否已提醒过"，也无法做恢复消警。需按类逐条读码确认是否经 `__dict__`/序列化间接读 | 处方 SILENT-P3-R2 |
| `last_trip_callback_error` | `data/source_circuit_breaker.py:87` | **z-failopen 本轮新增的可观测字段，当前全仓零读方**（写方 2 处）→ 属"写进对象但没人看"的**新欠账**，不是旧病 | 处方 SILENT-P3-R3（转报 z-failopen/Max：建议进熔断状态快照或 `/health` 投影） |
| `source_state`、`target_state` | `shared/lifecycle/state_machine.py:96/83` | 疑为 dataclass/协议字段，经构造或序列化消费 → **假阳**（我的判据不认 dataclass 字段声明与跨模块 kwargs 传参） | 排除（附理由） |
| `error_contract`、`error_id` | `shared/contracts/ctr002_producer_validator.py:83`、`shared/contracts/core/enforcer.py:113` | 同上，契约字段经 `model_dump`/异常消息间接消费 | 排除 |
| `total_warnings` | `gov_drift/brain_integration.py:174` | 计数聚合位；无读方=不外报 → 弱病例（同 P3-R2 族） | 处方 SILENT-P3-R2 |

**结论**：P3 修口径后 23 件，深读 9 件语义件 → **真病例 1（`owner_alerted`）+ 待判 4 + 假阳 4**。
P3 未穷尽（23 件里的 14 件非语义命名未逐条读），如实登记交 Max。

### 方法学结论（这条比数字值钱：它是总包 §1 第④向判据缺陷的机械证据）
我做了一次**全仓名字级提及**交叉核对（121254 个文件，含 .py/.yaml/.md/.json/.ps1/.sql/.html）：
**448 个"只写不读"属性名，零提及者 = 0**——即每一个都在别处出现过。
原因：同名**局部变量**（`alerted = ...`）、别类的同名属性、文档散文都会命中 `git grep`。
→ **验收规范 §1 第④向"用 `git grep` 引用面判下游能取"会把"只写不读"判成已接通**（复查清单 §0.2 已登记该缺陷待 Max 改），
本车道给出可执行的替代判据：**符号级**（AST `(class, attr)` 二元组 + 同类约束），名字级只能当粗筛。

### 处置
未收敛（逐条判读 448→修后基数需按 (class,attr) 二元组重做，超本车道预算）。
已交 Max 波次，登记于 `silent_prescriptions.md` §P3。本车道**不声称 P3 已普查完毕**。

---

## 4. P4 DEBUG 级放行（普查 §J 第 2 条明载"本轮未扫"，本车道补扫）

### 判据
- **P4a**：`except` handler 的全部语句只由 `*.debug(...)`（+ 可选 pass/continue）组成 → 真失败只留 DEBUG 痕。
- **P4b**：`if <失败判定>: logger.debug(...)` 之后继续执行/返回成功。

### 命中数
| 口径 | 数 | 差值解释 |
|---|---|---|
| grep 启发式（except 次行的 `log.debug(`） | **207** | 只看次行 → 漏 handler 内跨行/多语句形态；且不知 handler 是否**还有**别的可见日志 |
| AST 严判 | **238**（P4a 228 + P4b 10） | 差值 +31 = grep 次行口径漏计（与 z-failopen 对 `except…pass` 的 144→261 同一病因：**次行偏移启发式不完备**） |

### 热路径筛后 64 处（`src/zephyr/{data,trading,data_eng,strategy_pipeline,ex_core,plan_engine,pf_core}**`）中的真病例

| # | file:line | 改前 | 改后 |
|---|---|---|---|
| F4a | `src/zephyr/trading/health_monitor.py:239` | `logger.debug("longevity probe registration failed", exc_info=True)` | `logger.warning("longevity probe 注册失败（看护探针数少于预期，健康视图偏乐观）: %s: %s", type(...), ..., exc_info=True)` |
| F4b | `src/zephyr/trading/health_monitor.py:269`（原 `# 5.12.1 修复：原 except: pass` 只做到 DEBUG） | 同上 | 同上（注释如实记"DEBUG 在生产日志档位下不可见 = 哨兵自身失明无人知晓"） |
| F5 | `src/zephyr/strategy_pipeline/daily_decision_orchestrator.py:475` | `log.debug("[DAILY-DECISION] 告警通道不可达", exc_info=True)` —— **拍板链的告警通道自己断了，只留 DEBUG 痕** | `log.error("[DAILY-DECISION] 告警通道不可达，本条播报未送达（level=%s）: %s: %s", level, type(alert_exc).__name__, alert_exc, exc_info=True)` |

**为何 F4 是真病例**：`register_probe` 失败意味着**看护列表变短**，而 `HealthMonitor` 的聚合健康视图
不会因此报"缺探针"——它只会少一个键。这正是 §1 第⑥向的反面："看起来有监控，实际监控项已静默蒸发"。

### 假阳/未改（登记）
- `data/implementations/akshare_provider.py` 约 25 处 `self._log.debug(f'…失败: {e}')`（**instL 独占文件**）→ 处方 P4-R1。
  判读：多数是"逐 symbol 循环内的降级"，升 WARNING 会产生海量噪音 → 属"需要按类聚合后再升可见性"的改法，不该机械改。
- `strategy_pipeline/pipeline_events.py:193/235/562/929`（`alerter 不可达`/`receipt 落盘失败`/`audit marker 写入失败`）→ **residG 独占** → 处方 P4-R2（**其中 `alerter 不可达` 与 F5 是同一条链的两端**：orchestrator 侧我已升 ERROR，pipeline_events 侧仍是 DEBUG）。
- `data/scheduler.py:563/1532`、`data/tick_subscriber.py:522/552/667` → z-failopen 独占面 → 处方 P4-R3。
- `trading/boot_hooks.py:281/296/313/340/512/522/539/587` **8 处治理钩子**（`rbac_kill_switch_check`/`rbac_kill_switch`/`escalation_check`/`timeout_check`/`budget_delta`/`triple_align_event`/`skill.freshness_critical`）hook 自身异常只留 DEBUG → 处方 P4-R4（**保命轨钩子静默失败是本模式里最贵的一类**）。

---

## 5. P5 兜底日志预设失败类别（#ARCH-327 教训族）

### 判据
`except <宽类型>` handler 内的日志调用：正文含预设性词（超时/不可达/拒绝/refused/deadlock/锁不可得/导致/权限/不存在…），
且**既无 `type(exc).__name__` 也无 `exc_info`** → 一旦异常类型与措辞不符即误导归因。

### 命中数
| 口径 | 数 | 差值解释 |
|---|---|---|
| grep 启发式（except 次行含预设词） | **108** | 放大：多数写法其实带了 `exc_info=True` 或 `type(...)` |
| AST 严判（**首版有 FP**） | 28 | 首版只 `unparse` 关键字**值**，把 `exc_info=True` 读成 `True` → 误判"无 exc_info"。改为关键字名+值后 → **19** |
| AST 严判（修口径后） | **19** | 真基数 |

### 判读与处置
19 条中：
- **已随本车道收口 3 条**（F1/F2/F3 的 handler 顺手补真实类型名，不再单列）。
- **判为无需改 6 条**：措辞与真实异常面基本同形且信息量足（如 `gov_enforcement/rule_bridge/session_worktree.py:5907` 的 `(TimeoutExpired, OSError)` **窄类型** + 明写两种可能 → 预设面已被 except 类型锁死）；`position_adjudication_center.py:222`、`timeout_guard.py:165` 等已带 `exc_info=True`（我的判据里 exc_info 合格即不入 19，这几条是按词表二次筛除）。
- **处方 10 条**：`data/ch_writer.py:511`、`data/implementations/{eia,fred,qweather,miniqmt}_provider.py`（4 条"网络不可达/权限"式措辞，宽 `except Exception` 且不预设类型名）、`gov_audit/delegation_bridge.py:83`、`governance/resilience_governance/f5_*.py`（2 条）、`shared/infra/process_incubator.py:394/412`（"concurrent writer" 式归因，实际异常类型未验）、`risk/paper_hedge_leg.py:419`（z-land2 独占）、`commit_queue.py:1594`。
  → 全表见 `silent_prescriptions.md` §P5。

---

## 6. 收口与证据总账

| 项 | 值 |
|---|---|
| 实改文件 | 5（F1/F2/F3/F4a/F4b/F5 六处收口点，分布在 5 个文件） |
| 新增测试 | `tests/zephyr/data/test_silent_latch_before_delivery.py`，12 条 |
| 本轮该套件检出 | **12 件通过，且已被证明能红**（变异证据见下） |
| 回归 | `tests/data/test_source_health_check.py` + `tests/zephyr/data/test_data_anomaly_alerter.py` + `tests/resource/{test_resource_optimization,test_engine_resource_optimization,test_self_healing}.py` + `tests/governance/ops/test_health_monitor.py` + 新钉 = **184 件通过** |
| **因加严转红的既有测试** | **0 条** |
| 纯处方（不动手只登记） | P1-b 观察项 3 + P2 处方 7 + P4 处方 4（含 ~36 处逐条点名） + P5 处方 10 |
| 能红证据 | `.runtime/tmp/ff-silent/red_proof.py` → `red_proof.txt` |

### 能红证据（按字节还原，禁 `git checkout`）
`red_proof.py` 对 5 个源文件逐个 `read_bytes()` → 反替换 → `write_bytes()` 还原为**改前实现**，跑对应测试：

| 还原的文件 | 还原后测试结果 | 重放补丁后 |
|---|---|---|
| `data/source_health_check.py` | **2 failed**, 1 passed, 9 deselected | 3 passed |
| `data_eng/data_anomaly_alerter.py` | **2 failed**, 1 passed, 9 deselected | 3 passed |
| `trading/resource_optimization.py` | **2 failed**, 1 passed, 9 deselected | 3 passed |
| `trading/health_monitor.py` | **1 failed**, 11 deselected | 1 passed |
| `strategy_pipeline/daily_decision_orchestrator.py` | **1 failed**, 11 deselected | 1 passed |

每组"1 passed"是**正向对照**（如 F1 的"真落盘才置闩"、F3 的"成功送达后仍去重"）——
它们在新旧实现下都该绿，用来证明我没有把测试写成"只测失败方向"。

### 不 mock 防线自身
- F1 用**真 `Alerter`**（把 `_DEFAULT_FAILURES_DIR` 指到"父段是普通文件"的路径 → 真 `NotADirectoryError` → 真返回 False），
  断言的是**落盘后重读的 streaks JSON**里 `alerted` 的值，不是内存对象；
- F2 用**真 `DataAnomalyAlerter.evaluate`**，故障=sink 第一次真抛 `OSError`；
- F3 用**真 `_ExternalNotifier.emit_pressure_event`**，故障=event bus 真抛 `ConnectionError`；
- F4 用**真 `HealthMonitor.register_shared_monitoring_probes`**，故障=`register_probe` 真抛 `LookupError`；
- F5 用**真 `ddo._alert`**，故障=注入的 alert_fn 真抛 `ConnectionError`（`_alert` 本身未被 mock）。

---

## 7. 未达成（如实列）

1. **P2c（89 处默认恒真查表）未逐个判读**——需要逐个追它的消费点是否当"健康判定"用，预算内只做到了"P2b 深读 6 + LSG 群"。
2. **P3 未收敛**——首版口径有缺陷（已自曝并修），修后基数的逐条判读交 Max；本车道不声称该模式普查完毕。
3. **`daily_decision_orchestrator` 无既有测试文件**：我想跑它的回归，`find tests -name "*daily_decision*"` 返回空 →
   **该模块（含拍板链告警面）此前测试覆盖为 0**。附带自曝：我因 glob 展开为空，误跑了一次
   `python -m pytest <空参数>`（≈全量收集），结果 `26 skipped, 105 collection errors, 0 tests run, 21min`——
   未执行任何测试体、未写 `data/`，但这违反"禁 `pytest tests/` 全量"的操作纪律，记在这里。
4. P4 处方里的 `boot_hooks` 8 处保命钩子 DEBUG 放行**未改**：改法应是"钩子失败计入 boot 健康位"，
   与处方 P2-R1（boot_hooks 恒返 healthy）是同一枚硬币的两面 → 必须一起裁，单独改日志等级会造出"看得见失败但没人判"的半吊子。
5. 门禁候选提案已出，但**未落地任何 gate**（提案需 Max 批 + 宪法 §4.1 的"替代对象"需其确认）。
