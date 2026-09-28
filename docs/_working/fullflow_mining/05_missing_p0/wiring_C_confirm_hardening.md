---
ttl: task_bound
volume: wiring_C_confirm_hardening
session: st-ailayer-final-20260924
creation_token: w6c-confirm-gate-three-mines-hardening-20260926
---

# W6-C · confirm_gate 三雷加固 + 接线前置钉死（红队案卷 rb2 §四/§十 落地车道）

> 靶件=`src/zephyr/ai_layer/scheduling/confirm_gate.py`＋配对测试`tests/ai_layer/scheduling/test_confirm_gate.py`。
> 零提交零入队。禁触件本报告只引用不修改。案卷真源=`rb2_guard_attacks.md` §四（幂等与并发）＋§十 A3/A4/B5。

## 一、三颗雷：修前现象（红队实测）／修后机理／红测结论

### 雷 1 并发不幂等（案卷 §四.1，原评级=高）

- **修前现象**：同一单并发 4 次 confirm ⇒ `confirm_decisions.jsonl` 4 行 decided＋
  `pending_events.jsonl` 4 条 `order_confirmed_due`＋4 个不同 `receipt_id`。
  根因=`history()` 读 → `evaluate_confirm` 判 → `_append`/`upsert` 写 三步之间零互斥，
  幂等只依据"上一次读到什么"，故只有顺序请求才幂等。头注自述"重放返回原回执、零新事件"在并发下为假。
  接线后果=下游 `order_daemon` 收 N 条确认事件 ⇒ 重复派工（资金面）。
- **修后机理**：`ConfirmGate._gate_lock()`＝**单一临界区包住整个 decide**（读判三写全在锁内）。
  锁=本仓既有 OS 字节排他锁先例的复刻（`gov_audit/writer.py::_cross_process_append_lock`
  Windows `msvcrt.locking(LK_LOCK)` / POSIX `fcntl.flock(LOCK_EX)`，句柄即锁生命周期，
  进程被杀自动释放、无 stale 残留），再叠一层同 `state_dir` 的进程内 `threading.RLock`
  （msvcrt 同进程多线程同 fd 语义不保证，双保险而非二选一）。锁文件
  `orders.jsonl.gate.lock` 只创建永不删除（删＝拆散互斥域，同先例口径）。
  **不是"加锁重试到不冲突"**：临界区内部零重试、零轮询；第 2..N 个请求拿锁后读到的是
  已落定的 decided 行＋快照回执，走 `idempotent_hit` 直接返回原回执，不产生任何新写。
  写前判存（`_landing_present` 三处实读）作为第二道防线，锁失效时也只补齐不重复。
- **红测结论（收紧）**：`test_concurrent_same_request_is_idempotent` 线程数 **12**
  （严于案卷的 4，覆盖 Windows `os.replace` 撞句柄窗口）⇒
  决策账 decided 行数 **=1**、事件账 `order_confirmed_due` 条数 **=1**、
  12 份回执的 `receipt_id` **同一枚**、`orders.jsonl` 该单 `audit_log` 长度 **=1+1**。
  顺序重放（旧测）仍绿：`test_idempotent_replay_no_duplicate_event`。

### 雷 2 半写假持久化（案卷 §四.2 / §二.23，原评级=高）

- **修前现象**：`emit`＋`_append` 成功、`upsert`（工单快照）抛错这一路：当次把半截状态
  当成功返回，且重试被"幂等命中"掩盖 ⇒ `orders.jsonl` 永缺 `owner_decision`，
  "绝不假持久化"只在 emit 那一路成立。
- **修后机理**：**写前意图账（WAL）＋按落点实读对账**。
  ① `decide` 在锁内先物化本次 `receipt_id`，写
  `.runtime/ai_scheduling/confirm_intents/<receipt_id>.json`（含 order_id/decision/
  receipt_id/decided_at/待写事件与快照全量载荷）；② 依次落 ①事件账 ②决策账 ③工单快照，
  快照行新增 `owner_receipt_id`（对账锚，案卷 §四.2 建议的"把 receipt_id 写进快照"）；
  ③ 三处都实读到才删意图行。任一步抛错 ⇒ 上抛 `ConfirmPersistError`
  （带 `stage`/`order_id`/`receipt_id`），意图行**留在盘上=未持久化凭据**，
  绝不返回 `ok=True`。下次任何对同单的 `decide`（或直调 `reconcile()`）先跑
  `_recover_locked`：按落点实读补齐缺腿（同一 `receipt_id`、同一 `decided_at`，
  故事件/决策行不新增），补齐后才进入判定 ⇒ 自愈且幂等。
  幂等命中额外要求**快照真带该回执**（`idempotent_hit` 缺 `owner_receipt_id` ⇒ 判
  `persist_failed:orders_snapshot` 报红，堵住案卷点名的"半写被当成幂等命中"）。
  意图文件删失败留下的 stale 意图无害（重放按落点实读=零操作）。
- **红测结论（收紧）**：`test_second_write_failure_reports_and_self_heals`
  打桩让第二写（决策账 append）失败 ⇒ 断言 `ConfirmPersistError` 上抛、
  `exc.stage == "decisions"`、回执已定形且落盘意图文件在场、
  返回面**从未出现 ok=True**；撤桩后重跑同一请求 ⇒ 自愈成功且
  decided 行数 **=1**、事件条数 **=1**、`receipt_id` 与失败那次**同一枚**。
  第三写失败同测（`stage == "orders"`，另断言事件/决策账已在场但快照缺 ⇒
  自愈后快照 `owner_receipt_id` 落定）。

### 雷 3 审计销毁器（案卷 §四.4，原评级=高）

- **修前现象**：`load_orders` 对畸形行只 `skipped_lines+=1` 并 warn（fail-open 读），
  而 `upsert` 用 `load_orders()` 的结果**重写整档** ⇒ 任意一次无关 upsert 永久抹掉
  损坏行。实测 `ORD-VICTIM` 从 3 行变 2 行，同时 `decide` 返回 `ok=True`＝历史被销毁。
  另 §四.3：8 线程各 upsert 新单只剩 2 个落地（读-改-写全档无锁＋固定 tmp 名共用）。
- **修后机理（`OrderFileStore` 读侧防御，见 §三"为什么不算越界"）**：
  ① 快照写改成**按行外科式改写**（`_rewrite_locked`）：原文件逐行按序保留，
  命中 `order_id` 的那行原地替换，无命中才尾部追加——畸形行/非 dict 行/未知行
  **一律原文回写**，路径上不存在"整档重建"；② 固定 tmp 名改 `<pid>-<uuid>` 唯一名＋
  `os.replace` 前置 `flush+fsync`（治 §四.3 的 `PermissionError` 与丢单）；
  ③ 写前/写后各做一次**行集指纹比对**（`_row_census`：可解析行的 `order_id` 集合＋
  不可解析行的原文集合），`_assert_no_loss` 判定"丢失集非空 ⇒ 抛错且不落盘（写前）／
  落盘后立即复读，丢则上抛"，任何重写路径可证明零行丢失；④ 畸形行除原文保留外，
  另落 `.runtime/ai_scheduling/orders_quarantine.jsonl` 留痕（行号＋sha256＋原文＋原因），
  并 `log.error` 出声；⑤ 同 `order_id` 多行＝并发/upsert 异常史 ⇒ 只替换首行、
  其余原样保留＋留痕报红，不静默合档。
- **红测结论（收紧）**：`test_malformed_line_survives_unrelated_upsert`
  塞一枚畸形行（`"{ this is not json"`）＋两枚好单，对**另一枚**单做 upsert ⇒
  断言坏行原文**逐字节仍在盘上**、行数不降（3→3）、
  `orders_quarantine.jsonl` 有该行的留痕记录、`caplog` 有 ERROR 出声；
  `test_upsert_never_drops_rows_under_concurrency` 16 线程各 upsert 一枚新单 ⇒
  16 枚全部在场（原实测 8→2）。原"畸形行跳过计数"测保留但改成
  **同时断言原行仍在**（旧测只断"跳过"＝销毁的共犯口径）。

## 二、另两处如实处置（今夜不修完，留可执行结论）

### 处置 1：`allow_amend` / `actor` 由请求体自填、零鉴权（案卷 §三.5，中）

**代码未改，且不造假鉴权函数充数**——`decide_from_payload` 仍照 body 取
`actor`/`allow_amend`。接线前必须接会话鉴权真源，判据与接线点如下（可执行清单）：

- 接线点（唯一）：`src/zephyr/frontend/dashboard/api_server.py`
  的 `POST /api/schedulegate-confirm` 路由体（现为诚实拒执行 `not_wired` 占位）。
  本件属禁触热件且在别的会话视野内，**本车道未碰**。
- 接线判据（三条全满足才准接，缺一即不接）：
  1. **actor 不得来自 body**：路由体从服务侧会话上下文取
     （仓内既有真源＝`zephyr.gov_enforcement.rule_bridge.git_commit_gateway` 的会话身份链，
     以及 `zephyr.security.access_control` 域），把 body 的 `actor` 字段
     **丢弃或只接受与已认证身份相等的值**（不等 ⇒ 拒并落 `actor_spoof_refused` 审计）。
     判据测试口径＝"body 里写 `zhangsan` 而会话身份是别的 ⇒ 决策账 `actor` 落已认证身份"。
  2. **allow_amend 不得来自 body**：改判＝推翻既有 Owner 判，属 Owner 门位动作，
     须经认证通道（裁定登记或正式门位），不接受匿名 POST 自填 True。
     现状 body 直填即"谁都能自称改判"（案卷 §三.5 实测 `actor=['zhangsan','lisi','wangwu']`）。
  3. **确认语义的写权限**：只有 `owner_gate=true` 骨架级单可被本门判，且调用方须具备
     Owner 侧身份（`risk_tier_registry.yaml` 的 high 域 human_gate 同口径）。
- 待裁项（转 `pending_rulings.md`／总筹）：**"会话鉴权真源是哪一件"**——候选＝
  gateway 会话身份 vs `security.access_control` vs 仪表盘自有 session。
  本车道不自裁、不新造第四套身份件。案卷 §十 B5 的"建议 A3/A4/A5 落地前不要接"
  中，本车道已完成 A3（雷 1+雷 2 的锁与 CAS 序）／A4（雷 3 的畸形行保留），
  **鉴权仍缺 ⇒ 接线前置三件只满足两件**（见处置 2）。

### 处置 2：本件今日仍是**装饰件**（案卷 §〇/§一 判=装饰）

**如实登记：`confirm_gate.py` 今日未接线，零生产调用点，Owner 点前端按钮不产生任何写入。**
本车道修的是"接线即出事故"的三颗雷，**不等于本件已生效**。

- 接线前置三件（缺一不得接线，接了就是把雷放到 Owner 按钮路径上）：
  1. **鉴权源**——见处置 1 三条判据，**未满足**（本车道未做，也不许造假的）。
  2. **并发串化**——**已满足**（雷 1 的单一临界区锁＋写前判存）。
  3. **`OrderFileStore` 归档语义确认**——**代码侧已加固**（雷 3 的零丢失证明＋quarantine），
     但**语义待确认**：生产真源目标是 PG `ai_scheduling.ai_work_order`（C2 DDL 已在册），
     文件快照究竟是"过渡落点"还是"长期真源"未裁；若最终是 PG，则本件的
     `orders.jsonl` 写腿要退役为投影，接线点选择完全不同 ⇒ 须先定这个再谈接线。
- 交付叙述红线：**任何汇报把 `/api/schedulegate-confirm` 说成"已生效/已闭环"=失实**。
  本件三态＝**代码完工、接线待前置**。

## 三、改动面与"读侧防御为什么不算越界"

- 改动文件（本车道全部）：
  - `src/zephyr/ai_layer/scheduling/confirm_gate.py`（雷 1/2/3 加固＋头注契约同步）
  - `tests/ai_layer/scheduling/test_confirm_gate.py`（配对测试，全部收紧）
  - 本记录册
- `OrderFileStore` 的读侧防御为何不算越界：它是 **confirm_gate.py 文件内的类**，
  雷 3 的靶点就写在这段代码里（`upsert` 用 `load_orders()` 结果重写整档），
  不改它无法修这颗雷；生产路径归属上 `orders.jsonl` 与本件同属
  `.runtime/ai_scheduling/` 落点域，未跨模块、未碰任何禁触件。
  对外唯一可见面变化＝`load_orders` 仍返回"可解析 dict 行"（`search_orders.py` 等
  读端语义零变），新增的是 `malformed_lines`/quarantine 留痕与写侧零丢失保证；
  既有公开签名（`get`/`upsert`/`load_orders`、`decide`/`decide_from_payload`、
  `evaluate_confirm`）**全部保持向后兼容**（`evaluate_confirm` 是纯函数，签名与判定
  口径一字未动，半写判据落在编排层不污染纯函数面）。
- 未做（如实）：未新增 gate、未改判据阈值、未碰 `config/flags.yaml`、
  未碰 `api_server.py`、未自赋裁定号、未写 Owner 署名。

## 四、待登项（交总筹单点，本车道零提交零入队）

1. **depgraph 设计节点**：`confirm_gate` 的 `[DEPENDENCIES]` 新增
   `zephyr.shared.io.file_utils`? — **否**（本车道刻意不引 `safe_write_text`，
   见 §五.2 理由），依赖面零新增；新增产物路径声明：
   `.runtime/ai_scheduling/confirm_intents/*.json`（WAL 意图账，可删可重放）、
   `.runtime/ai_scheduling/orders_quarantine.jsonl`（畸形行留痕，append-only）、
   `.runtime/ai_scheduling/orders.jsonl.gate.lock`（锁文件，只创建永不删除）。
2. **translation / creation_token 登记**：本记录册（新 .md）＋无新 .py 模块。
3. **接线一行**：仍**不建议接**（前置三件里鉴权源未落、归档语义未裁）。
   案卷 §十 B5 的"不接"结论在本车道加固后**仍然成立**，只是原因从"三颗雷"收窄为"两颗"。
4. **待裁两案（可原样粘进共享 `pending_rulings.md` 表；本车道未自行改他人 in-flight 件，
   该册现为 `AM` 态属 05 挖矿车道，故只在此备行）**：

   | # | 问题 | 已试路径（实测） | 选项 | 建议 | 门位属性 |
   |---|---|---|---|---|---|
   | C-1 | `confirm_gate` 的会话鉴权真源是哪一件（`actor`/`allow_amend` 现由请求体自填＝零鉴权）？ | 读 `decide_from_payload` 与 api_server `not_wired` 占位；候选=git_commit_gateway 会话身份链 / `security.access_control` 域 / 仪表盘自有 session；本车道**刻意未造**假鉴权件 | a 接 gateway 会话身份／b 接 access_control／c 仪表盘自有 session 升为真源 | **a＋三条判据齐才接**（见 §二处置 1）；body 的 `actor` 只接受与已认证身份相等值，不等即拒并落 `actor_spoof_refused`；`allow_amend` 一律不来自 body | Owner 门（high，改判＝推翻既有 Owner 判） |
   | C-2 | `orders.jsonl` 文件快照是过渡落点还是长期真源（生产真源目标声明=PG `ai_scheduling.ai_work_order`，C2 DDL 已在册但 sink 未接）？ | 读 `OrderFileStore` 头注自述＋`order_daemon` 无 PG sink；本车道已把文件侧写成零丢失＋quarantine 语义（雷 3），但**语义归属未裁** | a 文件=过渡、PG 为真源（本件写腿退役为投影）／b 文件=长期真源（PG 只做镜像）／c 先补件级比对再定 | **c→a**：接线点形态由这个答案决定，未定之前 `confirm_gate` 保持装饰态＝不接 | 治理门（medium） |

5. **后续工单（非今夜）**：`confirm_intents/` 与 `orders_quarantine.jsonl` 的
   容量治理（现设计=完成即删/留痕 append-only，零轮询零定时器，
   清理入口应挂在既有 reconciler 的事件沿上，禁新建 cron）。

## 五、自证与复核

### 实测结果（2026-09-26 本车道落盘后复跑，非记忆）

| 项 | 实测 |
|---|---|
| 环境自证 | `python -c "import zephyr; print(zephyr.__file__)"` ⇒ `D:\ZephyrAlpha\.worktrees\st-ailayer-final-20260924\src\zephyr\__init__.py`（Python 3.12.8，落本 worktree 非主区） |
| 配对测试规模 | `tests/ai_layer/scheduling/test_confirm_gate.py` **30 测全绿**（修前 19 测 → 净增 11 条红测，零删除零放宽） |
| 本域全量 | `tests/ai_layer/scheduling` **134 collected，exit=0**；连跑 3 轮 exit 全 0（并发测无抖动） |
| `ruff check` 两文件 | `All checks passed`（仅剩仓内既有 `# noqa: SLF001——`/`import-integrity` 形态的 warning，属他人既有行，未做整档格式化连坐） |
| 零生产写 | `.runtime/ai_scheduling/` 在 worktree 与主区**均不存在**（本车道未建）；pytest 临时根=`.runtime/tmp/pytest_*`；`data/` 零写入 |
| 全域 `tests/ai_layer` | exit=1，**4 条红全在 `tests/ai_layer/redline/test_ai_secret_exposure.py`** ⇒ 归属 W6-H 在途（`ai_secret_exposure.py` 与其测试同为 `AM` 态，且 `wiring_H_honest_status.md` 未跟踪），属本车道禁触件，**未代修、未改动**（宪法 §3.4 owner 责任制） |

### 判别力自证（变异法：证明新测能红，不是自我安慰的绿）

用 `.runtime/tmp/w6c_red_check.py` 在内存里把新实现退回各雷的修前形态（不改被测件、不落盘），
跑配对测试 ⇒ **必须变红**：

| 变异（模拟修前） | 变红的测 | 结论 |
|---|---|---|
| `gate_lock_for` → 空上下文（雷 1 无互斥） | `test_concurrent_same_request_is_idempotent` | 实测拿掉闸后 12 线程造出**多枚回执**且 `persist_failed:orders` 上抛 ⇒ 闸是承重的，测有牙 |
| `_write_intent` → 空操作（雷 2 无写前凭据） | `test_second_write_failure_*` / `test_third_write_failure_*` / `test_reconcile_heals_*`（3 条全红） | 意图账是自愈的唯一凭据 |
| `upsert` → 旧"整档重建"（雷 3 销毁器） | `test_malformed_line_survives_unrelated_upsert` / `test_upsert_keeps_duplicate_order_id_rows` / `test_upsert_never_drops_rows_under_concurrency`（3 条全红） | 畸形行被抹/重复行被合档/并发丢单三种事故均可被现测抓到 |

**变异自证反哺出的一处弱敏点（已收紧）**：首轮 `nointent` 变异**没能**打红
`test_third_write_failure_reports_and_self_heals`（该测复跑走"改判"路径，绕开了意图账依赖），
故补断言"同判复跑必须先靠意图账自愈返回原回执 + 意图文件必须在盘"⇒ 二轮变异 3 条全红。

### 环境自证

- 环境自证：cwd=worktree＋`PYTHONPATH=$PWD/src`，`python -c "import zephyr; print(zephyr.__file__)"`
  必须落在 `D:\ZephyrAlpha\.worktrees\st-ailayer-final-20260924\src\zephyr\__init__.py`
  （主区裸 python 导包＝假绿源，本车道已实测排除）。

- 两条实施期取舍（如实披露）：
  1. 意图账目录名 `confirm_intents/` 而非 `.tmp`——`.runtime` 卫生口径下它是**语义状态**
     不是临时输出，故落 `state_dir` 内（与 `orders.jsonl` 同域），不进 `.runtime` 根。
  2. **未采用 `safe_write_text`**（案卷 §十 A3 的"或"分支）：它是热文件 CAS 件，
     每次调用向 `repo_root/.runtime` 直写 `safe_write.jsonl` 审计行，
     而本件测试必须全 `tmp_path`（宪法 §9.6 测试禁写生产路径），
     用 `repo_root=tmp_path` 改写审计锚又会把审计甩出真源域；
     雷 3 的实质是"**零行丢失**"而非"整档内容 CAS"，
     故改为自带行集指纹比对（`_row_census`+`_assert_no_loss`）＋唯一 tmp 名＋fsync，
     并把雷 1 的互斥做成 OS 字节锁（跨进程真互斥）。**这条与案卷建议的偏差请总筹复核。**

### 复核命令（可直接粘）

```bash
cd "D:/ZephyrAlpha/.worktrees/st-ailayer-final-20260924"
export PYTHONPATH="$PWD/src"      # PowerShell: $env:PYTHONPATH="$PWD\src"
python -c "import zephyr; print(zephyr.__file__)"   # 必须落在本 worktree
python -m pytest tests/ai_layer/scheduling -p no:cacheprovider -c py.ini -q --timeout=300 \
  -k "confirm_gate or concurrent or persist or malformed or quarantine"
python -m pytest tests/ai_layer/scheduling -p no:cacheprovider -c py.ini -q --timeout=300  # 全量配对面
# 判别力自证（把新实现退回修前形态，期望对应测变红）：
python .runtime/tmp/w6c_red_check.py nolock && echo UNEXPECTED_GREEN
```

## 六、本车道文件清单（交总筹统一补 creation_token／翻译登记后落地，零提交零入队）

| 路径（worktree 内相对） | 态 | 说明 |
|---|---|---|
| `src/zephyr/ai_layer/scheduling/confirm_gate.py` | 修改（HEAD 有基线） | 三雷加固＋头注契约同步（[INVARIANTS]/[ERROR_CONTRACT]/[TESTS]/[CONSUMERS] 四段改到与实现一致） |
| `tests/ai_layer/scheduling/test_confirm_gate.py` | 修改 | 19 测 → 30 测；旧 `test_order_store_skips_malformed_lines` 由"只断跳过"**收紧**为"同时断原行逐字节留盘" |
| `docs/_working/fullflow_mining/05_missing_p0/wiring_C_confirm_hardening.md` | 新增（本件） | 车道记录册＝三雷修法＋接线前置＋两处如实处置 |
| `.runtime/tmp/w6c_red_check.py` | 新增（临时件，TTL 区） | 判别力变异自证脚本；**非交付物**，可随 `.runtime/tmp` 清理 |

### 三态结论

**代码完工、接线待前置**（不是"完工"，也不是"待挖"）：

- 三颗雷＝修完且红测有牙（并发/半写/审计销毁各有专属红测＋变异自证）；
- 未接线状态如实保留（api_server 未碰、`not_wired` 占位仍在，Owner 点按钮零写入）；
- 待裁两项转 `pending_rulings.md` 口径：①会话鉴权真源是哪一件；②`orders.jsonl` 是过渡落点
  还是长期真源（决定接线点形态）。

