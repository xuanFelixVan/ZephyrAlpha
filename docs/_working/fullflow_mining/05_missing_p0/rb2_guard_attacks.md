---
ttl: task_bound
volume: rb2_guard_attacks
session: st-ailayer-final-20260924
creation_token: rb2-guard-attacks-wave2-20260926
---

# RB-2 红队案卷：波2 执法件"装饰化 / 说谎"攻击实录

> 车道＝RB-2 红队；任务＝想办法让本轮新建执法件变成装饰或说谎，不是确认它们能用。
> 作业规范=`92_chief_command_wave2.md`；设计意图与门位边界=`94_chief_rulings_wave2.md`。
> 靶件全部在 worktree `D:\ZephyrAlpha\.worktrees\st-ailayer-final-20260924`。
> 脚本＝`D:\ZephyrAlpha\.runtime\tmp\redblue_wave2\rb2\`（5 支：cleaning_weight_tombstone / confirm_vocab / 2b_fixups / secret_cage_tombstone / mutability_probe）＋同目录 `results_t127.json` `results_t34.json` `results_t34b.json` `results_t567.json` `results_mutability.json` 为原始输出。
> 纪律执行：零提交、零入队、零 claim、零生产写路径；**所有被测文件测后逐字节还原并自证 sha256**（见 §九）。
> 假绿防线：worktree 裸 `python` 会导到主区包（`D:\ZephyrAlpha\src`），故每支脚本首行强制 `sys.path.insert(0, <worktree>/src)` 并 `assert WT in zephyr.__file__` 才继续。

## 〇、结论速览（七面 × 六件）

| 靶件 | 面 A 谁调它 | 定性 |
|---|---|---|
| 1 `weight_ssot` + `auto_mount` | 唯一调用点 `auto_mount.py:1085`，且在 `if not args.apply: return`（:1078）之后 | **半装饰**：只在 `--apply` 写图前自证；生效面（pf_alloc）与提交面**零拦点**；第二头探测器只有测试调用 |
| 2 `cleaning_rules_hosting` + `config/cleaning_rules.yaml` + `supply_sentinel` | 真链路 `supply_sentinel.py:541 → scheduler.py:238-251`（L13 排班）→ **会跑** | **真接线但结论无人消费**；三把静默闸（enabled / disabled_flag / cadence）皆可 `ok=True` 不跑 |
| 3 `confirm_gate` | 零生产调用（`api_server:4606` 仍返回 `ok:false not_wired`，诚实） | **装饰（待接线，如实登记）**；但并发/半写缺陷已实测坐实，接线即出事 |
| 4 `market_state` + 册 + `state_vocab_registry_gate` | 门由 `in_process_gate_registry.yaml:646` 驱动（真挂载） | ** warn 出厂下只有一件事会硬拦＝册读不到**；值级锁定三态可绕；同名册漂移可整体归零 |
| 5 `ai_secret_exposure`（＋ tombstone） | `combined_deny_patterns`/`screen_session_env*`/`assert_key_not_forbidden` 全仓零生产调用；连 `screen_session_env` 本身也无启动器调用 | **装饰**；现网 forbidden=0；头注 ERROR_CONTRACT 与实现不符（说谎） |
| 6 `price_cage` 两腿 | 两腿真调（`miniqmt:874`、`qmt_file_bridge:563`）；`attach_cage_quote_source` **零挂载** | 判定面**拦住**（480 组输入逐字段零差异）；供数面**半装饰**（端口开了没插头）＋一个危险组合（见 §六.5） |
| 7 `tombstone_ttl_proposer` | CLI 手跑；全仓无宿主调用 | 装饰（提案器，风险面低）；但"ttl_windows=0 当班可清"与"缺 since=零动量"两条会让清单说谎 |

Top4 严重缺陷（会不会造成假绿/漏拦/误拦）：
① **靶 4 同名册 schema 漂移＝值级锁定静默归零**（主区已存在另一车道 09-22 版同名同 registry_id 的 `state_vocabulary_registry.yaml`，无 `official_ontology` 段 → `_load_registry` 回 `error=""` 且锁定表为空；实测官方类加第八态照样 passed=True）⇒ **假绿**，且合并时未跟踪文件会撞车。
② **靶 3 confirm_gate 三颗并发/半写雷**（同单并发 4 次 → 4 条事件 4 个回执；快照写失败后重试被"幂等命中"掩盖成半写永不自愈；`orders.jsonl` 畸形行被下一次 upsert 静默抹掉＝审计销毁器）⇒ 现在因零调用点不咬人，**一接线就咬资金面**，且配对测试全为顺序单线程、抓不到。
③ **靶 6 cage 的 Owner 一行里埋着反向地雷**（`attach_cage_quote_source` 零挂载＋生产下单链不喂基准价 ⇒ 两腿恒 UNKNOWN；此时翻 `unknown_reject` ＝连续竞价限价单 100% 拒单；模块只登记了"需时段豁免判别器"，没登记"需先挂供数源"）⇒ 不造成漏拦，造成**全量误拦**。
④ **靶 5 契约说谎**：头注承诺"册里无 `ai_exposure` 标注 ⇒ 抛 `AiExposureError`"，实测不抛——而现网真册正是"106 条、0 条标注"；叠加"零生产调用点"，本件写的是插座不是护栏。


## 一、面 A：谁调它＋能否改变行为

1. **weight_ssot**：`git grep` 全仓（排除 docs/_working）→ 除自身与 `auto_mount.py` 外零引用；`src/zephyr/pf_alloc/**`（被声明为唯一生效作者）**一次都不 import 这把尺**；`gate_registry.yaml`/生成器/CI 面零引用 ⇒ **平时提交生效面没有拦点**，只有人手动跑 `auto_mount --apply` 才咬。第二头探测器 `discover_weight_writers` 的调用点只有 `tests/backtest/test_weight_ssot_single_authority.py:160,172` ⇒ "野生写手"只在跑测试时暴露。
   补刀（数据流层面拆分也是纸面的）：`allocation_request()` 打的 `binding=nomination/authority=auto_mount/effective=False` 标记**没有任何下游读者**——`rebalance_proposal()` 只把它塞进打印用的 dict（`auto_mount.py:1011`），而 pf_alloc 用的是自家的 `StrategyAllocationRequest`（`src/zephyr/pf_alloc/core/multi_strategy_capital_allocator.py:115`），从不接 auto_mount 的行。故头注那句"任何把本件行当生效值落库的接法都要先过 `assert_nomination_not_binding`"= **对一条不存在的接法做的承诺**（无门禁保证将来也不能绕过）。
2. **cleaning 托管腿**：真实排班链成立（`scheduler.py:238-251` 事件触发调 `run_supply_sentinel`，后者 :541 调托管腿）。但 `scheduler` 返回 `{"data_supply_sentinel": bool(result.get("ok"))}`，读的是**断供腿**的 ok；`summary["cleaning_gate"]["ok"]` 不进任何排班判定 ⇒ 本腿 `ok=False`（承载册坏了 / 全表降级 / 命中脏数据）时**排班面仍报绿**，只有 Alerter 一条出声通道。这正是 92/94 册点名的"接线≠生效"最后一里。
   运行时实况（同分钟实测，非记忆）：主区确有一个 `-m zephyr.data.scheduler` 常驻进程在跑（L13 槽位 cron `50 6 * * *`），但托管腿代码此刻**只在 worktree、未合并** ⇒ 今天不会跑，落地后才会真跑（`D:\ZephyrAlpha\data\cleaning_gate` 目前不存在，符合预期）。附带一条册面漂移：`config/schedule.yaml:231` 的 `data_supply_sentinel` 描述只写了 quality_sentinel 托管，**没写新增的清洗第二段** ⇒ 只读排班册的人/普查器看不出这条腿现在还跑清洗（`cleaning_rules_hosting.py [CONSUMERS]` 写了，册没写）。
3. **confirm_gate**：宣称消费者 `api_server POST /api/schedulegate-confirm` 仍是"诚实拒执行"占位（路由体不含 ConfirmGate）⇒ 前端按钮现在点了不产生任何写入（没吹牛，但本窗判定面未经受真实流量）。
4. **state_vocab 门**：唯一真实触发面＝GitCommitGateway in-process（`in_process_gate_registry.yaml:646` + `gate_registry.yaml:1311`，priority=135）⇒ 真挂载；但出厂 `STATE_VOCAB_GATE_MODE="warn"` ⇒ 除"册不可读"外一律放行。
5. **ai_secret_exposure**：见 §七。
6. **price_cage**：两腿都真调，且 `execution_engine → order_manager.submit_order(order_id, broker_id)` 不喂基准价（HEAD 病根原样在），故**现状两腿仍恒 UNKNOWN**，只是改后会打一条 WARNING。
7. **tombstone**：`main()` CLI；无月度体检器调用（`gen_ai_layer_monthly_checkup.py` 未引用），归档件是一份 `records_scanned:0 / data_source.status: ok` 的清单，而 worktree 无 `data/governance.db` ⇒ **"0 条墓碑"当前不可复核**。

## 二、面 B：fail-open 后门（异常注入）

| # | 注入 | 靶件 | 结果 |
|---|---|---|---|
| 1 | 承载册文件不存在 | 2 | **拦住** `ok=False, config_error=承载册缺失` |
| 2 | 坏 YAML | 2 | **拦住** |
| 3 | wiring 键名拼错（`cadence_dayz`） | 2 | **拦住**（未知键=配置错，附 legal 清单） |
| 4 | `tables: []` / 某表 `rules` 空 | 2 | **拦住**（"有表无尺=假覆盖"） |
| 5 | `cadence_days: true`（布尔投毒）/ `0` | 2 | **拦住** |
| 6 | 表名塞 `WHERE 1=1 UNION SELECT…` | 2 | **拦住**（标识符白名单） |
| 7 | `host_schedule` 与实调方不符 | 2 | **拦住**（防"册里挂了宿主却没接"） |
| 8 | CH 全表不可达 | 2 | **拦住** `all_degraded=True → ok=False` |
| 9 | **两表之一查询恒失败** | 2 | **绕过**：`ok=True`（alerts=1）。口径只惩罚"全表 degraded"，**再加一张表就能把失明表稀释成绿** |
| 10 | **查询返 0 行**（表空 / `date_col` 口径错） | 2 | **绕过**：`ok=True` 且**零告警**，被当"已巡检且干净" |
| 11 | `disabled_flag` 文件存在 | 2 | **绕过**：`ok=True, skipped=master_switch_off`，**零告警零审计**（一个 `data/runtime/*.disabled` 空文件＝永久静默本腿） |
| 12 | `wiring.enabled: false` | 2 | 同 11 |
| 13 | 节奏闸第二次触发 | 2 | **绕过**：`ok=True skipped=cadence_7d_last_...`；状态真源＝`report_dir` 里文件名前 10 字符 ⇒ **任何人写一份当天命名的 JSON 即可让本腿未来 7 天不跑**（投毒面，无校验） |
| 14 | 承载册非法 UTF-8 字节 | 2 | 抛 `UnicodeDecodeError`（非声明的 `CleaningGateConfigError`）；宿主 catch-all 兜住 ⇒ 不 fail-open，但 CLI `main()` 只 catch 声明错型 ⇒ 运维手跑裸 traceback。**契约口径不符** |
| 15 | 中央册缺失 / 坏 YAML / 顶层非映射 | 4 | **拦住（硬阻断）**——本轮唯一真硬牙；范围与袋序风险见 §五末段 |
| 16 | 中央册存在但**无 `official_ontology` 段**（换 schema） | 4 | **绕过且静默**：`error=""`、`value_locks={}` ⇒ 值级锁定整体归零，见 §五.4 |
| 17 | 空册（`classes: []` `vocabularies: []`） | 4 | **拦住**（未登记即记违规）——warn 态下只是"全仓都违规"，不阻断 |
| 18 | `ai_exposure` 字段未出现在任何条目 | 5 | **绕过**：不抛错（头注说明会抛 → 说谎，见 §七.2） |
| 19 | `secrets: []` / 条目全是标量 | 5 | **绕过**：`forbidden=()` 无错（"整册被清空＝无人被禁"） |
| 20 | 缺 `criteria.tombstone` 段 | 7 | **拦住**（ValueError 透传） |
| 21 | 旗标层 `is_enabled` 抛错 | 6 | 静默回落 OFF（有 `logger.warning`，不报红）——方向安全，但"enforce 被旗标层故障关掉"无红信号 |
| 22 | `confirm` 的 journal `emit` 抛 OSError | 3 | **拦住**：上抛，决策账不存在、快照未改 ⇒ 头注"emit 失败上抛不假持久化"**成立** |
| 23 | `emit` 成功但快照 `upsert` 抛错 → 重试 | 3 | **绕过**：重试返回 `ok=True idempotent=True`，而 `orders.jsonl` 永缺 `owner_decision` ⇒ "不假持久化"只在 emit 那一路成立，**append/upsert 这一路仍会假持久化**（§四.2） |

## 三、面 C：豁免与逃生通道能否被静默拉满

1. **noqa 逃生压过官方值级锁定**（靶 4，高）：`_class_has_noqa` 的检查在值锁定**之前**（gate 源码 :286 `continue` 早于 :288 `locked = ...`），故在官方本体类体内加一行 `# noqa: STATE-VOCAB-REGISTRY  例行自证` 即可让该类**整体免检**（含新造第八态）。实测：`passed=True`。且配对测试 `test_noqa_escape_hatch_still_works_for_value_lock` 把这条逃生**当特性钉绿**。noqa 的本意是"启发式误报白名单"，而官方本体的值级锁定不是启发式误判，不该适用逃生。
2. **门内自述文案教的 noqa 形态无效**（靶 4，低但难堪）：detail 文本让用户写 `# noqa 标记（STATE-VOCAB-REGISTRY） <原因>`，而 `_make_noqa_pattern` 认的是 `#\s*noqa:\s*<gate_id>\s{2,}(\S.*)$`。实测按文案写 → `passed=False`（没豁免）。反向说谎：用户以为已经免检。
3. **cleaning 腿三把静默闸**（靶 2，中）：`enabled:false` / `disabled_flag` 存在 / 节奏闸命中 ⇒ 全部 `ok=True` 且**零告警**，退出码 0。停用不留痕、不通知，与 INVARIANTS 里"绝不静默当已巡检"的强度不符（那条只覆盖了配置错路径）。
4. **weight_ssot 的判据＝自家文件里的三张声明表**（靶 1，中-高）：`WEIGHT_PRODUCERS` / `PRODUCER_FIELDS` / `PRODUCER_PATH_KEYS` 改一行即改判据，而这三个 dict 不受任何门禁保护（`assert_producer_writes_nomination` 正是拿它们自证）。改 `PRODUCER_FIELDS["auto_mount"]=EFFECTIVE_FIELD` 会被拒（拦住了），但改 `PRODUCER_PATH_KEYS["pf_alloc"]=("src/zephyr/zzz/",)` 之后，真正的 pf_alloc 写点集体掉出 census、`auto_mount` 成唯一观察者 ⇒ `single_effective_path=False` 会拒（这条路 fail-closed），**反向不 fail**：把 `auto_mount` 的键改成它自己文件的别名，就能让自己从 census 里隐身，同时它的写点也消失 ⇒ 看起来"没人写权重"＝放行。**未登记作者一律 `classify_path→None→不参与判定`（weight_ssot.py:273 注释自认）**，这是最大的结构性逃生。
5. **confirm 的 `allow_amend` 与 `actor` 都由请求体给**（靶 3，中）：`decide_from_payload` 无鉴权、`actor` 自由填；实测决策账里 `actor=['zhangsan','lisi','wangwu']`。接线后任何能 POST 者可自助改判＋伪造审计主体。
6. **host-mismatch 校验方向正确**（靶 2）：`host_schedule` 声明与实调不符 → `ok=False`（不是"降级继续跑"），这面没找到可拉满的逃生。

## 四、面 D：幂等与并发（confirm_gate 为主）

1. **同一 confirm 并发 4 次 → 双写坐实**（高）：实测 `confirm_decisions.jsonl=4 行`、`pending_events.jsonl=4 条事件`、4 个不同 `receipt_id`。直接违反头注「幂等=同单同判再请求返回原回执**零新事件零重写**」。根因＝读(`history`)→判(`evaluate_confirm`)→写(`_append`/`upsert`) 三步无锁、无 CAS；顺序请求才幂等。后果（接线后）：下游 `order_daemon` 收到 N 条 `order_confirmed_due` ⇒ 重复派工＝资金面。
2. **半写＋幂等命中＝假持久化换了条路**（高）：见 §二.23。最小修法＝决策账与快照写用同一 CAS 序（先 `upsert` 后 `_append`，或把 `receipt_id` 写进快照做对账；重试时若快照缺 `owner_decision` 而决策账有 decided 行 ⇒ 必须判"半写待补"而非幂等命中）。
3. **`OrderFileStore.upsert` 整档重写并发丢单**（高）：8 线程各 upsert 一个新单，最终只有 2 个落地，且抛 `PermissionError`（Windows `os.replace` 撞打开的句柄）。根因＝读-改-写全档无锁，tmp 文件名固定（`orders.jsonl.tmp` 所有人共用）。与宪法硬规则 13 的精神冲突：这条写路径**没有**走 `safe_write_text`（同项目 quality_sentinel/cleaning 腿都用了）。
4. **fail-open 读 + 整档重写＝审计销毁器**（高）：`load_orders` 对畸形行只 `skipped_lines+=1` 并 warn（声明为"search_orders 同款 fail-open 读"），但 `upsert` 用 `load_orders()` 的结果**重写整档** ⇒ 任何一行损坏（半截写/人为截断）在**下一次任意 upsert 时被永久抹掉**。实测：`ORD-VICTIM` 行从 3 行变 2 行，同时 `decide` 返回 `ok=True`。这与 INVARIANTS「改判留痕不删（旧行永在）」正面冲突——事件账/决策账是 append-only，但工单快照的 `audit_log` 不是。
5. **提名/生效写路径 TOCTOU**（靶 1，未证成缺陷）：`alloc_authority_guard()` → `safe_write_text(MAP_YAML, after, expected_base_sha256=sha(before))`。census 与写盘之间确有时间窗，但 CAS 期望基线锁住了被改文件本体，且 `not r.written → RuntimeError` ⇒ 该处**没有可乘之机**（如实记"攻击未得手"）。
6. **tombstone 提案器重跑稳定性**（靶 7，拦住）：输入乱序两次 `build_proposal` 逐字节相同（`candidates` 显式按 `switch_id` 排序、tag 用 set 后 sorted）；无 `datetime.now()`；`as_of` 必填。

## 五、面 E：值级 vs 名级（state_vocab 新加的值级锁定实测）

| 攻击 | 结果 | 机制 |
|---|---|---|
| 官方类 `MacroRegime` 内新增第八态 `R13`（模拟 block 态） | **拦住** | `value_locks[类名]` 逐值比对，detail 点名 R13 |
| 别处新文件造同名 `class MacroRegime` 塞 `R9/R13` | **拦住** | 同上（值锁定按类名生效，不要求路径） |
| **换个类名**（`MacroRegimeOfficial`）＋ 同样错值，文件仍是 `market_state.py` | **绕过（passed=True，detail 空）** | 双重：① `value_locks.get(node.name)` 按**类名**查 ⇒ 改名即脱锁；② 册里 `official_ontology.physical_location` 是**纯路径串**，`_is_registered` 的模块路径分支命中即整文件放行 ⇒ 官方本体所在文件成了文件级白名单（正是 YAML 注释 :85-87 自称"登记粒度保持在类/符号级而非文件级"想避免的事，官方段自己破了自己的口径） |
| 造不含 state/phase/regime/emotion/mode 关键词的类（`class SixGrid: A="CAPITULATION" B="IGNITION" C="RECHARGING"`） | **绕过** | 连"词表类"都不认定 ⇒ 词表扩段零成本 |
| 取值写成小写 / 计算式（`A = "r1"`、`X = f(r)`） | **绕过** | `_is_upper_string_literal` 只认全大写字符串字面量 |
| 类体只留 2 个全大写赋值 | **绕过** | `< _MIN_UPPER_ASSIGNMENTS=3` 不识别（可"删一个成员"退到门槛下） |
| 官方类体内加一行 `# noqa: STATE-VOCAB-REGISTRY  <原因>` | **绕过**（见 §三.1） | 逃生通道在值锁定之前短路 |
| **同一段代码，判据换成主区在册的另一版同名册**（`D:\ZephyrAlpha\...\state_vocabulary_registry.yaml`，2026-09-22 他道产出，无 `official_ontology`） | **绕过且静默** | `_load_registry` 返回 `error=""`、`value_locks={}`（实测登记字符串 298 个、锁定表 0 个）⇒ 值级锁定**整体归零**，门仍"绿"。两版同名同 `registry_id`（REG-STATE-VOCAB-001）＝双真源，且 worktree 版仍是未跟踪文件，合并时会 `untracked working tree files would be overwritten` 撞车 |

**结论（实测给判）**：新加的值级锁定**有牙但不是钢牙**——它把"名级"缺陷修成"名级+值级双按名索引"，凡改名、凡不在关键词表、凡非全大写字面量、凡一行 noqa，判据即失效，且**册换 schema 时静默归零而非报红**。warn 出厂态下它今天**拦不下任何东西**（实测 warn 态新造第六段 `passed=True`）。最小修法（按性价比排序）：① `_load_registry` 增加"册必须含 `official_ontology.classes[4]` 且 `values_locked` 全真"的结构自检，缺即报红（与"册不可读"同级，堵住本节最后一行）；② `value_locks` 查表键从"类名"改为"类名 + `official_ontology.classes[].target` 的模块路径"，只有**两者都命中**才认定"这就是官方本体"，从而取消 `physical_location` 带来的文件级白名单；③ 值锁定路径不吃 noqa（noqa 只豁免"启发式未登记"，不豁免"官方在册值被改"）。

**硬阻断的范围与名册口径（两条附带发现）**：

* "册不可读=报红"确实会**连坐**，但范围由名册触发面决定：`in_process_gate_registry.yaml:646-655` 的 `files_trigger: ["src/", ".py"]` ⇒ 只打含 `.py`/`src/` 的提交，不是字面全仓。真正的风险是**袋序**：本门的 YAML（`catalogs/state_vocabulary_registry.yaml`）与 `src/zephyr/shared/vocab/**` 在 worktree 里仍是**未跟踪**状态，而 gate 本体已是 `M`（改后未 add）——只要"码先册后"分两袋落地，中间窗口里所有含 .py 的提交都会被"判据本体不可用"挡死。修法＝**门禁代码＋它读的册同袋原子投**（本项目已有同族教训）。
* 同一条名册的 `register_line` 注释**仍写着"注册表缺失 fail-open"**（2026-09-22 的原契约），与本轮改后的 fail-closed 相反 ⇒ 判据改了、机读名册的自述没改＝**名册说谎**（车道禁触 `catalogs/**` 热册，须由总筹在同一袋里改这一行注释）。


## 六、面 F＋靶 6：price_cage 的"逐字节不变"断言成不成立

1. **miniqmt 腿：成立**。用 HEAD 版 `_apply_price_cage_locked` 判定段逐行复刻，与新 `decide_cage_for_limit_order` 做笛卡尔对照：BUY/SELL × 4 个价位 × 4 种 order_book（None / 空档 / 正常对手方价 / 全 0 价）× 3 种 prev_close × 5 个板块码（600000/300750/688981/832000/999999）= **480 组**，比较 `(status, base_price, upper_bound, lower_bound, clamped_price, was_clamped)` 六元组 ⇒ **差异 0**，且 `reject` 恒 False、`supplied` 恒 False。旗标出厂读数确认 OFF。
2. **文件桥腿：不成立（有语义可见的增量）**。改前该腿对 UNKNOWN **完全静默**，改后新增 `elif UNKNOWN: logger.warning(UNKNOWN_WARNING_TEMPLATE)` ⇒ 多一条 WARNING（外加 `supplied` 日志）。`price_cage` 头注（:292）自己承认"两旗标全 OFF 时除 UNKNOWN 必打告警外零语义变化"，但 `miniqmt` 侧头注写的是"本段行为与改前逐字节一致"⇒ **两条腿的口径不同，文档没统一**。资金语义无变化，日志量有变化 ⇒ 定级低-中；最小修法＝把"逐字节"改成"判定逐字段一致；UNKNOWN 告警为新增（文件桥腿）"。
3. **旋钮是真咬合的**（不是第二枚装饰）：运行时注册旗标后 → UNKNOWN+`reject=True`、供数 → `CLAMPED`+`supplied=True`。
4. **两键在 `config/flags.yaml` 未登记** ⇒ `is_enabled(key, default=False)` 恒 False（安全方向）；Owner 要开必须新增 `flags: {ex_core_price_cage_unknown_reject: {enabled: true, description: …}}`（标量值会被 loader `continue` 跳过）。这不是缺陷，但要写进"Owner 一行"里，否则 Owner 写 `key: true` 会得到"我翻了但没生效"。
5. **危险组合（必须进 94 册 Owner 一行）**：`attach_cage_quote_source` 在 `src/scripts/tools` **零挂载点**（只有定义＋文档注），生产下单链 `execution_engine.py:306/329/342/452 → order_manager.submit_order(order.order_id, broker_id)` 不喂 `order_book`/`prev_close` ⇒ 现状两腿恒 UNKNOWN。此时若 Owner 先翻 `unknown_reject` 而供数未接，**两腿连续竞价限价单 100% 被拒**（实测无 quote 即 `reject=True`）。`price_cage` §案 BF-6 注记了"需时段豁免判别器"，**没记"需先挂供数源"** ⇒ 前置条件清单不完整，是本轮最像"事故说明书"的一条。定级高（不是假绿，是反向误拦地雷）。
6. **靶 5 的"只扩不缩"名实不符**：见 §七。

## 七、面 F：ai_secret_exposure 的"只扩不缩"与契约说谎

1. **只扩不缩只对硬编码基线成立**：`combined = tuple(DENY_ENV_PATTERNS) + 册面 forbidden`。改 YAML 把某键从 `forbidden` 撤掉 ⇒ 拦截面立刻缩回基线，实测 `4 条 → 3 条(=基线)`，**零拒绝、零留痕、零报红**；"整册为空 / `secrets: []` / 条目全非映射"同样静默得到"无人被禁"。也就是说：INVARIANTS 里"只扩大拦截面、绝不缩小"防的是"有人改基线"（基线在 `negative_list.py`，另有门禁管），而**新字段自己的缩减完全无保护**——这正是本件存在的理由被反向消解。最小修法＝把"曾出现过的 forbidden 键集"落一份 append-only 台账（事件账/`OBJ_S` 变更账），`load_ai_exposure_report` 发现**撤章**即抛 `AiExposureError` 或在 report 里给 `removals` 非空即 fail-closed。
2. **ERROR_CONTRACT 与实现不符（说谎，高）**：头注写「文件缺失/**`AI_EXPOSURE_FIELD` 未出现在任何条目** → `AiExposureError`（真源不可用不得假装"无人被禁"）」。实测：一个 `secrets` 两条、**都不带** `ai_exposure` 的册 → 不抛错，`marked_entries=0`，`combined==baseline`。而**现网真册恰好就是这个状态**（`config/secret_registry.yaml`：`total=106, marked=0, forbidden=()`）⇒ 承诺的 fail-closed 分支不存在，且它描述的正是今天的生产态。
3. **两个读端打架**：`registry_deny_patterns` 把键名当 fnmatch 模式交给 `screen_session_env`（实测 `key: "QMT_R**_*"` 会拦 `QMT_R**_TOKEN`，`allowed=False denied_keys=(...) leak_suspected=True`），而 `assert_key_not_forbidden` 用 `name in set(forbidden_keys)` **精确匹配** ⇒ 同一个"盖章"条目，筛查面拒绝、读取面放行。接线后必出"一处拒一处放"，且后者是被绕过的那条。最小修法＝两读端共用一个 matcher（或强制键名必须是字面量：含 `*?[` 即配置错）。
4. **非法字节**：抛 `UnicodeDecodeError`（未落到声明的 `AiExposureError`）——方向 fail-closed，但错型不在契约里，调用方按契约捕错会漏。
5. **面 A 定性**：`combined_deny_patterns` / `screen_session_env_with_registry` / `assert_key_not_forbidden` 在 `src/scripts/tools` **零生产调用**；连 `screen_session_env` 本体也没有启动器调用者（与 94 册 §三"AI-4 R-1/R-2 写了不读，随点火批"一致）。⇒ 本件目前是"执法面 + 可证伪测试"的**预置插座**，不是护栏；任何文档若把它记成"AI 密钥面已防护"即为假绿。

## 八、面 G：配对测试判别力（改一行破坏被测件 → 测试是否变红）

> 方法：备份字节 → 单行变异（每例挑最承重的那一行判定）→ 跑该件配对测试 → **立刻还原并校验 sha256**。
> 原始输出 `results_mutability.json`；先跑 7 个配对文件的**未变异基线（CONTROL）**，全部真绿且**有例数**（防"no tests ran 也算绿"）。

| 配对测试（CONTROL 基线） | 变异（改一行） | 变红？ |
|---|---|---|
| `tests/backtest/test_weight_ssot_single_authority.py`（17 passed） | `assert_nomination_not_binding` 里 `if binding == BINDING_EFFECTIVE:` → `if False:`（提名越权不拒） | **是**（1 failed） |
| `tests/zephyr/data/test_cleaning_rules_hosting.py`（28 passed） | `_reject_unknown_keys` 的 `if unknown:` → `if False:`（未知键静默接受） | **是**（2 failed） |
| 同上 | `_parse_positive_int` 的 `if value < 1:` → `< 0:`（0 放行=静默空转） | **是**（2 failed） |
| `tests/ai_layer/scheduling/test_confirm_gate.py`（21 passed） | `if verdict["kind"] == "idempotent_hit":` → `if False:`（幂等短路失效） | **是**（1 failed） |
| 同上 | `_aware` 的 naive 拒收改为 `return moment` | **是**（1 failed） |
| `tests/gov_enforcement/test_state_vocab_registry_gate.py`（19 passed） | `if locked is not None:` → `if False:`（值级锁定关闭） | **是**（2 failed） |
| 同上 | `if registry_error:` → `if False:`（册不可用退回 fail-open） | **是**（4 failed） |
| `tests/ai_layer/redline/test_ai_secret_exposure.py`（7 passed） | `baseline = tuple(DENY_ENV_PATTERNS)` → `tuple()`（并集丢基线＝缩面） | **是**（2 failed） |
| 同上 | 词表外值不再按 forbidden 处置 | **是**（1 failed） |
| `tests/ex_core/test_price_cage_bf6_wiring.py`（16 passed） | `_flag_on` 恒 `return True`（旗标当班即 ON） | **是**（6 failed） |
| `tests/ai_layer/switch_engine/test_tombstone_ttl_proposer.py`（11 passed） | `if record.state != "tombstone":` → `if False:`（非墓碑行也进净删提案） | **是**（1 failed） |

**结论：本面全部拦住，未发现恒绿测试**（11/11 变异被抓，7 个配对文件基线 119 例全绿且非空跑）。本轮纪律里的"恒绿无配对测试＝疑似判据失效"在**这六件的新配对测试上不成立**——这是好消息，如实记。

但配对测试的**覆盖盲区**与我实测到的缺陷是同一批（变异打不到＝测试不涉及）：

1. `test_confirm_gate.py` 21 例**全是顺序单线程** ⇒ §四.1 并发双写、§四.3 整档重写丢单、§四.4 审计行被抹，三颗都没有配对测试（我变异幂等分支它才红，说明它只测了"第二次调用"而不是"两次同时调用"）。
2. `test_price_cage_bf6_wiring.py` 16 例钉住了"旗标 OFF 零变化"，但**没有一例测"供数端口是否真被挂载"** ⇒ §一.6 的"零挂载"逃过配对测试（这正是本项目"接了插座没接线"的经典形态）。
3. `test_state_vocab_registry_gate.py` 19 例把"noqa 逃生对值级锁定仍有效"**当特性钉绿**（`test_noqa_escape_hatch_still_works_for_value_lock`）⇒ 我的 §三.1 绕过在测试眼里是预期行为。
4. `test_ai_secret_exposure.py` 7 例全用 tmp 册 ⇒ 现网真册 `marked=0`（字段零使用）这一事实**不在任何断言里**，头注契约（§七.2）说谎不被测。
5. `test_cleaning_rules_hosting.py` 28 例覆盖 fail-closed 九面（做得最扎实），但 `ok=True` 的三条静默闸（§三.3）与"两表之一 degraded 仍 ok=True"（§二.9）**无断言**。

## 九、盘面自证（零污染）

* 变异探针前后各跑一次逐文件 sha256 比对：`sha_before.json`（15 个靶件文件，含 `config/cleaning_rules.yaml`/两条 broker 腿/册/包 `__init__`）vs 结束时同集合 ⇒ **漂移=无**（脚本输出"漂移: 无（全部与基线一致）"，`results_mutability.json` 每例 `sha复原: True`）。
* 全部攻击写盘只落 `D:\ZephyrAlpha\.runtime\tmp\redblue_wave2\rb2\`（含 `work_t1/2/3/4/5/6/7` 假仓根与假册），未写 `data/`、未写 `.runtime` 根、项目根零临时文件。
* CH/PG：全程只用注入式 `Exec` 假执行器；对生产库**零连接**（`t_real_db_readonly` 因 worktree 无 `data/governance.db` 而短路，未回落到主区库写路径）。
* 未执行任何 `git add` / `commit` / `enqueue` / `claim` / `release`。工作树**内容面**零污染：15 个靶件文件（含两条 broker 腿、`config/cleaning_rules.yaml`、中央册、`shared/vocab/**`）sha256 全绿、漂移计数 0。
* 如实记一条盘面异动（**非本车道所为**）：收口时 `git status` 由开工时的 141 行变为 157 行，原因是他道/总筹在本窗口内批量 `git add`（`catalogs/state_vocabulary_registry.yaml`、`src/zephyr/shared/vocab/*` 等由 `??` 变 `A`）。本道产物 `05_missing_p0/rb2_guard_attacks.md` 与红队同伴的 `rb1_meter_attacks.md` 仍是未跟踪态，**归属清楚**，请总筹按 §车道作业规范第 2 条补 creation_token 后统一落地。
* 方法自审（诚实披露）：单行变异需要真实模块路径生效，因此存在 **10–30 秒的跨进程可观察窗口**；实测期间他道确有 pytest 在跑（`tests/pf_alloc`、`tests/ --collect-only` 等）。若他道在该窗口内跑全量并偶发见红，应以此段解释并复跑，**不要当成新缺陷立案**。下一轮红队建议改用"整包副本 + sys.path 指向副本"的变异法，消掉这个窗口。

## 十、最小修法清单（按门位属性分堆，逐条可粘给施工车道）

**A. 车道今夜可做（不触门位，纯本件＋自家测试）**

| # | 靶件 | 一行修法 | 消掉的红队结论 |
|---|---|---|---|
| A1 | 2 cleaning | `ok` 计算加"任一表 degraded ⇒ ok=False"（或 `degraded_tables>0` 单独出声＋计数进结论）；0 行样本另记"无对象"而非"干净" | §二.9 / §二.10 |
| A2 | 2 cleaning | 三条静默闸（`enabled:false`/`disabled_flag`/节奏跳过）各打一条 `LEVEL_WARN` 并写进报告 JSON（现在只 `log.info`＋零告警） | §三.3 |
| A3 | 3 confirm | `decide` 全程加进程内文件锁（`state_dir/confirm.lock`）；或把 `OrderFileStore.upsert` 改走 `safe_write_text`（CAS），并在 `decide` 里先比对"快照是否真含本次 `owner_decision`"再回幂等命中 | §四.1/.2/.3 |
| A4 | 3 confirm | `load_orders` 检出畸形行时**原样保留该行**（把无法解析的行按原文回写），或拒绝 upsert 并报红 | §四.4 审计销毁器 |
| A5 | 4 vocab | 值锁定分支不再前置 noqa（`locked is not None` 时绕过 noqa）；detail 文案里的中文 noqa 形态改成正则真认的 ASCII 形态 | §三.1 / §三.2 |
| A6 | 5 secret | 把 `ERROR_CONTRACT` 与实际实现对齐：要么补"册内无任何 `ai_exposure` 标注 ⇒ 抛错"，要么把头注那句删掉并在 report 里给 `field_unused: true`；`assert_key_not_forbidden` 与 `registry_deny_patterns` 共用同一 matcher | §七.2 / §七.3 |
| A7 | 7 tombstone | `policy_from_criteria` 校验 `ttl_windows >= 1`（对齐 cleaning 腿"整数键须 ≥1"口径）；`_revival_momentum` 对"有迁移但缺时间戳"记 `indeterminate` 而不是当零动量 | §七末段 T7 两条绕过 |
| A8 | 6 cage | `miniqmt` 腿头注"逐字节一致"改成"判定逐字段一致；文件桥腿新增 UNKNOWN 告警"（两腿口径统一） | §六.2 |

**B. 总筹单点（热册/接线一行，禁车道自触）**

| # | 内容 |
|---|---|
| B1 | `in_process_gate_registry.yaml` 的 STATE-VOCAB-REGISTRY `register_line` 注释仍写"注册表缺失 fail-open"——与改后代码相反，须同袋改这一行 |
| B2 | **门禁代码与 `catalogs/state_vocabulary_registry.yaml`、`src/zephyr/shared/vocab/**` 同袋原子投**（现在 YAML 未跟踪、gate 已 M） |
| B3 | 主区已存在的另一版同名 `state_vocabulary_registry.yaml`（2026-09-22 他道产出，无 `official_ontology`）＝**同路径双真源**，须先定谁是真源再落本波版本（合并时会 `untracked would be overwritten` 撞车） |
| B4 | `config/schedule.yaml` 的 `data_supply_sentinel` 描述补"新增托管第二段=cleaning_rules（判据=config/cleaning_rules.yaml，7 天节奏闸，停用=data/runtime/cleaning_gate.disabled）" |
| B5 | confirm_gate 的"待接线一行"（api_server 路由体改调 `ConfirmGate().decide_from_payload`）**建议在 A3/A4/A5 落地之前不要接**——现在接＝把双写＋丢单＋审计销毁三颗雷直接放到 Owner 点按钮的路径上 |
| B6 | weight_ssot 的生效面拦点：要么给 `pf_alloc` 落一次 `assert_nomination_not_binding`（运行时），要么把 `discover_weight_writers` 从测试提为提交面/巡检面（否则"第二头"只能等跑测试才现形） |

**C. 确属 Owner 的一行（本案卷新增，建议并进 94 册 §二 BF-6 行）**

* **`ex_core_price_cage_unknown_reject` 的启用前置条件必须补第二条**：现有注记只写"需时段豁免判别器"；实测**供数端口 `attach_cage_quote_source` 全仓零挂载、生产下单链 `order_manager.submit_order(order_id, broker_id)` 不喂基准价 ⇒ 两腿恒 UNKNOWN**，此时翻 enforce 旗标＝**连续竞价限价单 100% 拒单**（纸面/实盘两腿同）。次序铁律：**先挂供数源并验"供数后不再 UNKNOWN"，再谈翻 enforce**——与 94 册"BF-5 供数先于 BF-1/BF-2/BF-8"同构。
* 另记一条旗标操作口径：两枚 cage 旗标目前**未在 `config/flags.yaml` 登记**，Owner 开须写成 `key: {enabled: true, description: …}` 映射形态（标量 `key: true` 会被 `load_flags_from_yaml` 静默 `continue` 跳过＝翻了没生效）。

