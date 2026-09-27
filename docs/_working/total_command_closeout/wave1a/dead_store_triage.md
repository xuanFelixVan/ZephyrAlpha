---
ttl: task_bound
completes_when: "波 1A.5 死库普查四列表 + W-180.1 严格读接口（query_rows/count_strict）+ W-180.2 静态尺 + W-180.4 ch_probe 四件齐，两把红证测试跑成且可复算"
---

# 波 1A 施工案卷 · 死库普查（1A.5）+ CH 读数通道治本（W-180.1/.2/.4）

> 车道：`D:\ZephyrAlpha\.aidrafts\st-final-build-20260926`（HEAD=`5701fb99c8`，分支 `session/st-final-build-20260926`，**未提交**）
> 性质：施工执行件登记卷。**本队不裁定、不改规则册、不 commit、不 enqueue**；热册补丁只以 ```diff 文本待总包执行（§6）。
> 输入真源：`10_wave_plan.md` 1A.5 行 / `02_field_corrections_and_new_cases.md` X-53 / `dossier_B_backup_and_cold_storage.md` G-9 / 桌面终审卷 `03_排期完整性审计与分类视图.md` §七·§7.3 / 码内 `ch_reader.py`·`ch_writer.py`·`database_service.py`。

## 0. 案卷头四字段

- **turn_budget**：自设 40 次工具调用。实际：读输入 6 · 盘面普查/尺迭代 14 · 建接口 8 · 探针 3 · 红证 4 · 落盘 5 ≈ **40（压线，未超）**。超支处置预案（后期禁新调研只落盘）已执行：§3/§5 的进一步存量清算**未开工**，列为总包待办（§8）。
- **verified（本车道实测，全部命令原文见 §7）**
  1. 盘面 0 字节 `.db` **7 个**（`data/` 三层内实读，C1）：`data/zalpha_metadata.db`、`data/depgraph.db`、`data/databases/{depgraph.db, integrator_progress.db, progress.db, scheduler_progress.db}`、`data/runtime/progress.db`。**波 1A.5 原文列的 4 个之外，自查新增 3 个**（`data/depgraph.db`、`data/runtime/progress.db`，及"同名两处 depgraph.db 重复立案"这一形状）。
  2. 活替代实测（C2）：`data/integrator_progress.db`=37,003,264 B（mtime 09-26 20:15，**仍在写**）、`data/databases/governance.db`=203,804,672 B、`data/integrator_jobs.db`=57,344 B。
  3. fail-silent 病在码实证（C3）：`ch_writer.query()` TCP 失败→降级 HTTP→HTTP 失败→`log.error` + **`return ""`**；**空结果集同样 `return ""`** ⇒ 失败/真空在返回面上不可分；`ch_reader.count()` 对 `""`/非数字 `return 0`（`int(result.strip() or 0)` + `except ValueError: return 0`）。头注即在册契约：`[ERROR_CONTRACT] query失败->返回空字符串(同ch_writer); count失败->返回0`。
  4. 全仓 grep `query_strict|strict_query|query_rows|count_strict` 开工前**零命中**（终审卷 §7.2 L2 判断成立）；但存在**半个**既有严格入口：`ch_writer.get_client_strict()`（`ch_writer.py:217`，TCP 不可用即抛 RuntimeError），被 `scripts/backtest/*` 等 12+ 处自助使用——只严格在"取连接"一环，不覆盖结果形状与 HTTP 降级面。
  5. `DatabaseService`（`infrastructure/database_service.py`，399 行）实测是**连接工厂 + health_check**，无 `query()/count()` 门面 ⇒ 严格读接口按内收原则落在数据读取层 `zephyr.data.ch_reader`（复用 `ch_writer` 传输层，零新增连接层）。
  6. 严格接口 + 探针 + 尺 + 普查器四件落地，**24 条测试全绿**（§4）；尺对 HEAD 树 129 个候选文件**零命中**、对 canary 输入**必红**。
- **assumed（未实测，总包落地时须复核）**
  1. `trae_034` 3 处 `data/zalpha_metadata.db` 的行号以总包现读为准（本队只读定位，§6 补丁按读到的原文给）。
  2. `data/backups/zalpha_metadata_*_pre_close.db` 6+ 份备份内容未逐份打开（1A.5 指其可作取证源）。
  3. depgraph 真源是否已全量迁 Postgres：`DatabaseService.get_depgraph_conn()` 签名返回 `psycopg2.extensions.connection`（码面即证），但 `scripts/governance/d5_architecture/analyze_change_impact.py` 仍持 `depgraph.db` 字符串——**本队只报引用面，迁移事实由总包核**。
  4. W-34 空壳表清单是否真被 `count()` 的 fail-silent 污染：§5 只给复测配方，未实跑（实跑归总包在落地面统一做）。
- **input_set_disjoint_with**
  - 本队**未碰**（亦禁他人误以为本队碰过）：`docs/01_policies_and_standards/**`（规则册 trae_034/063 等热册，总包集中改）、`config/flags.yaml`、`data/**`（只读盘面）、阈值/断言/skip/xfail、任何进程与容器、任何 CH/PG 写路径、任何删除动作、git 提交面。
  - 本队独占写集（车道内）：`src/zephyr/data/ch_reader.py`（**只追加新符号**，`query/count/query_table/inject_final` 行为与签名一字未动）、`src/zephyr/data/ch_writer.py`（追加 `ClickHouseQueryError/parse_tsv_rows/query_strict/last_transport` + 头注契约行，`query()` 本体未动）、`scripts/governance/wave1a/store_liveness_probe.py`、`scripts/governance/wave1a/ch_read_shape_ruler.py`、`scripts/governance/data_supply/ch_probe.py（注：施工方案原指 `scripts/data/`，实测该目录被 .gitignore 第 603 行整体排除，故改道）`、`tests/governance/test_wave1a_{strict_read_canary,query_shape_ruler}.py`、本卷 + 两份机生产物 `wave1a/store_liveness_census.{md,jsonl}`、`wave1a/read_shape_violations.{md,jsonl}`。
  - 与 1A.1 建卡车道（同目录 `scripts/governance/wave1a/build_delivery_cards.py` 已存在）：读集相交于 `zalpha_metadata.db` 字面，写集不相交；本队普查器把它当普通消费者计数（自引用亦计数，见 §1 注）。
  - 与 W-34 空壳表车道：本队只出配方不实跑 ⇒ 无读集冲突。
- **evidence_ref.cmd**：§7 命令台账 C1..C13（原文可复算）；机生表＝§1（census）与 §3（尺）；红证原文＝§4。

---

## 1. A · 死库普查四列表（生成器产出，禁手改）

尺：`scripts/governance/wave1a/store_liveness_probe.py`（只读，不连任何 DB，不 import zephyr）。
四列＝**字节数 / 被多少 .py 引用（其中带路径真指针数）/ 有无活替代 / 消费者数**，另附规则册指向数与三态处置建议。
"消费者"＝提及行 ±8 行内出现真实读写动作（`duckdb.connect|sqlite3.connect|psycopg2.connect|get_*_conn|.execute(|.query(|.count(|read_sql|to_sql|cursor(`）的 .py 文件；"被提到"≠"被用"，死指针正藏在这差里。
"共现后继"＝与本库**同行**被点名的其他 `.db`（声明面证据，如 `registry_adapter.py:37` 写"SqliteAdapter 读取 governance.db（zalpha_metadata.db）"）。

**生成器原文（`docs/_working/total_command_closeout/wave1a/store_liveness_census.md`，机生禁手改）**

<!-- 本表由 scripts/governance/wave1a/store_liveness_probe.py 机生，禁手改（重跑覆盖） -->
<!-- generated_at=2026-09-26 20:36:49 -->

| 库（rel path） | 字节数 | mtime | .py 引用数（带路径真指针数） | 真实消费者数 | 规则册指向数 | 规则册样例 | 活替代（同 stem 最大件） | 共现后继（同行点名） | 三态建议 | 判据 |
|---|---|---|---|---|---|---|---|---|---|---|
| `data/databases/depgraph.db` | 0 | 2026-07-20 09:26 | 31（11） | 4 | 0 | 无 | 无 | `governance.db` | **repoint** | 4 个真实消费者 + 存在活替代/共现后继 `governance.db` ⇒ 改指活库 |
| `data/databases/integrator_progress.db` | 0 | 2026-07-24 02:38 | 1（0） | 1 | 0 | 无 | data/integrator_progress.db (37,003,264B @2026-09-26 20:15) | 无 | **repoint** | 1 个真实消费者 + 存在活替代/共现后继 `data/integrator_progress.db` ⇒ 改指活库 |
| `data/databases/progress.db` | 0 | 2026-07-24 14:03 | 1（0） | 1 | 0 | 无 | 无 | `integrator_progress.db` | **repoint** | 1 个真实消费者 + 存在活替代/共现后继 `integrator_progress.db` ⇒ 改指活库 |
| `data/databases/scheduler_progress.db` | 0 | 2026-08-14 07:15 | 0（0） | 0 | 0 | 无 | 无 | 无 | **retire** | 零消费者 + 零规则指向（声明面与消费面双空）⇒ 内收判据'零触发零消费→退役' |
| `data/depgraph.db` | 0 | 2026-08-04 00:59 | 31（0） | 4 | 0 | 无 | 无 | `governance.db` | **repoint** | 4 个真实消费者 + 存在活替代/共现后继 `governance.db` ⇒ 改指活库 |
| `data/runtime/progress.db` | 0 | 2026-09-15 23:50 | 1（0） | 1 | 0 | 无 | 无 | `integrator_progress.db` | **repoint** | 1 个真实消费者 + 存在活替代/共现后继 `integrator_progress.db` ⇒ 改指活库 |
| `data/zalpha_metadata.db` | 0 | 2026-09-10 00:44 | 5（1） | 1 | 1 | trae_034_task_card_standard.yaml | 无 | `governance.db` | **repoint** | 1 个真实消费者 + 存在活替代/共现后继 `governance.db` ⇒ 改指活库；规则册亦指向本库 ⇒ 规则与代码同批 |

合计可疑库 7 个；其中 0 字节 7 个。


> 注 1（尺口径告警，供总包判读）：`consumer_files_sample` 里 `scripts/_archive/**` 占多数——depgraph.db 的 4 个消费者中 **3 个在 `_archive/`（归档件）**，活件仅 `scripts/governance/d5_architecture/analyze_change_impact.py`；`zalpha_metadata.db` 的引用里含本队普查器自身与 1A.1 的 `build_delivery_cards.py`（新写件，非存量）。**尺不替人裁"归档件算不算消费者"**，两态都摆在 jsonl 里（`consumer_files_sample`）供逐条归属——这正是 1A.5 出口判据"34 处 depgraph.db 引用逐条有归属"要的东西。
> 注 2：波 1A.5 原文记 depgraph.db "被 34 个 .py 引用"；本尺现读 **31 个 .py（其中 11 个带路径真指针）**，`git grep` 对 HEAD 提交面独立复核＝**30**（差的 1 个是车道内新写件 `store_liveness_probe.py` 自身的字面提及，未入 HEAD）。与原文 34 的差异＝口径差（本尺只算 .py、只算含 `depgraph.db` 字面者；原文疑含 .md/.yaml 或旧盘面）。**以尺现读为准逐条复核，勿照抄 34**（X 册"三套旧数并存"教训）。

### 1.1 逐库判词（三态建议：复活 / 改指活库 / 退役；**建议非裁定**）

| 库 | 建议 | 一句话判据（消费者数 / 活替代 / 规则指向） |
|---|---|---|
| `data/zalpha_metadata.db` | **改指活库（必与规则同批）** | 1 个活消费者（`validators/validate_cross_references.py:225`）+ trae_034 明文 3 处指向 + 码内注释自证后继＝`data/databases/governance.db`（203 MB，今日仍在写）；`_archive/one_off/phase_a_backup.py` 属归档面。**补丁见 §6** |
| `data/databases/depgraph.db` | **改指活库 → 实为跨后端，须总包裁** | 31 .py 引用（HEAD 面 30）/ 4 消费者（3 在 `_archive`）/ 无同 stem 文件级活替代，但 `DatabaseService.get_depgraph_conn()` 已返回 psycopg2 连接 ⇒ 真源疑已迁 Postgres；共现点名 `governance.db` |
| `data/depgraph.db` | **退役（与上一条合并立案）** | 与 `data/databases/depgraph.db` 同名同 0 字节＝**一对象两名重复立案**（内收铁律"同域重复簇→收敛唯一"）；0 个带路径真指针指向本路径 |
| `data/databases/integrator_progress.db` | **改指活库** | 唯一消费者 `src/zephyr/data/progress_store.py`，其默认路径实为 `data/integrator_progress.db`（37 MB，09-26 20:15 在写）⇒ 死文件只是历史路径残迹 |
| `data/databases/progress.db` | **改指活库** | 同上单消费者 + 共现后继 `integrator_progress.db` |
| `data/runtime/progress.db` | **改指活库**（禁向 `.runtime` 根直写，本件即 9.4 卫生红线现证） | 同上单消费者 + 共现后继 `integrator_progress.db` |
| `data/databases/scheduler_progress.db` | **退役** | 0 引用、0 消费者、0 规则指向 ⇒ 内收判据"零触发零消费→退役"；**本队不删**（禁删除动作），列退役清单待总包按 #311/#328 条件通道走三层调查 |

**净零/内收对价**：本包净增脚本 3（普查尺 / 形状尺 / 探针）+ 测试 2 文件；对价＝① 形状尺即 W-180.2 未来 gate 的判据函数原型，升 gate 后不另立扫描器；② 普查器替代 1A.5 手工 0 字节库清单（散文清单必然漂移，宪法 9.5）；③ 严格读通道承接 `get_client_strict()` 的脚本层自助通道（退役候选，见 §2）。

---

## 2. B · 严格读接口（W-180.1）——落点与内收声明

**落点（两文件，非新建模块）**：
- `src/zephyr/data/ch_writer.py`：新增 `ClickHouseQueryError`（异常，带 `sql` + `attempts=[(tcp|http|engine_probe|contract, 原因)]`）、`parse_tsv_rows(text)`、`query_strict(sql, timeout) -> list[tuple]`、`last_transport() -> "tcp"|"http"|""`。
- `src/zephyr/data/ch_reader.py`：新增 `query_rows(sql, timeout) -> list[tuple]`、`count_strict(table, where, timeout) -> int`、`query_rows_table(...) -> list[tuple]`、`inject_final_strict(sql)`、`_final_suffix_strict(table)`；转发别名 `ClickHouseQueryError`。

**契约（失败必抛，两态可分）**：
| 通道 | 查询失败 | 真空 0 行 | 结果形状异常 | 引擎探测失败（FINAL 注不上） |
|---|---|---|---|---|
| 旧 `query()/count()`（行为一字未改） | `""` / `0` | `""` / `0`（**不可分**） | 静默 | 静默不注入 |
| 新 `query_rows()/count_strict()` | **raise** | `[]` / `0`（确证的真空） | **raise** | **raise** |

`query_strict` 只接受只读语句前缀（`SELECT/WITH/SHOW/DESCRIBE/DESC/EXPLAIN`），否则 `raise`——判据通道结构性不可能写 CH（对齐本包"禁对 ClickHouse 做任何写操作"硬禁）。

**内收声明（"替代/合并了哪个旧入口"）**：
1. **未新建连接层**：`query_strict` 复用 `get_client()` / `get_http_host()` / `_ch_lock` / `_ch_http_headers()` 及既有自愈钩子（`_invalidate_tcp_client` / `_invalidate_http_host` / `_note_http_failure` / `_reset_http_fail_streak`）——同一传输层，只换错误契约（W-180.1 规格原文）。
2. **合并对象**：`ch_writer.get_client_strict()`（`ch_writer.py:217`）+ `scripts/backtest/*` 等 12+ 处"自助严格"（取连接判 None → 自己 `client.execute` → 自己拼行）⇒ 今后这类读一律走 `query_rows/count_strict`；本队**未删** `get_client_strict`（禁删除动作），登记为**退役候选**交总包在 W-180.3 存量清算批里一并处理。
3. **正门归属**：`DatabaseService` 实测无查询门面（连接工厂），严格读正门因此落在 `zephyr.data.ch_reader`（数据读取层，裁决 #ARCH-CH-007 的既有真源），不在 `infrastructure/database_service` 里另造第二个读接口。
4. **红线（W-180 追加，本包已工具化可查）**：判据类读数（清单 / 尺 / 案卷 / 呈裁证据）必须 `query_rows` / `count_strict` / `ch_probe` **三选一**；用 `ch_reader.query()` 字符串直取或不查失败态的 `count()` ＝违规（§3 的尺即为此而设）。
5. 头注同步：两文件 `[ERROR_CONTRACT]` / `[INVARIANTS]` / `[CONSUMERS]` 已改，禁留"名册说抛、码里返回空"这种声明-强制脱钩。

---

## 3. C · 静态扫描尺与违规清单（W-180.2，**尺能红**）

尺：`scripts/governance/wave1a/ch_read_shape_ruler.py`（默认扫 **HEAD 树**，`git grep` 预筛 + 一次 `git cat-file --batch` 批读；`--files` 供增量/canary）。
三类模式：`S1_DIRECT_SUBSCRIPT`（`….query(...)[0]`／`[0][0]`）、`S2_FOR_IN_CALL`（`for x in ….query(...)`）、`S3_VAR_SUBSCRIPT` / `S3_VAR_FOR_IN`（`tsv = ….query(...)` 后数字下标或直接 for-in）。分级：`JUDGMENT`（判据路径，硬红）/ `NON_JUDGMENT`（软红）/ `EXEMPT`（测试、`_archive`、严格通道实现本体）。

**生成器原文（`docs/_working/total_command_closeout/wave1a/read_shape_violations.md`，机生禁手改）**

<!-- 本表由 scripts/governance/wave1a/ch_read_shape_ruler.py 机生，禁手改（重跑覆盖） -->
<!-- source=git HEAD tree scanned_files=129 unreadable=0 generated_at=0 findings -->

扫描面：`git HEAD tree`，129 个 .py 文件；命中 0 处（判据路径 0、非判据路径 0、豁免面 0）。

| 分级 | 文件 | 行 | 模式 | 命中原文 | 建议补丁位置 |
|---|---|---|---|---|---|

补丁口径统一＝把字符串读接口换成立即可用的严格通道：`ch_reader.query_rows()` / `count_strict()` / `query_rows_table()`（W-180.1），判据类一次性读数走 `scripts/governance/data_supply/ch_probe.py（注：施工方案原指 `scripts/data/`，实测该目录被 .gitignore 第 603 行整体排除，故改道）`（W-180.4）。


**判读**：
- HEAD 树候选面 129 个 .py（提到 `ch_reader|ch_writer|reader|writer` 的 `query(`/`query_table(`），**命中 0** ⇒ 存量生产调用点无需批量改（与终审卷 §7.2 L1"仓内 12+ 消费文件多数正确（变量名多叫 tsv）"一致）。**本队因此未改任何生产调用点**（硬禁：只列清单与建议补丁位置，禁批量改）。
- 误报治理是这把尺能不能用的关键，三条实测（C8）：① `tsv.strip().splitlines()` / `.split("\n")` 的**按行迭代＝正确用法不报**；② `isinstance(result, (list, tuple))` 分流后再 for-in 不报（`generate_data_inventory.py:267` 首跑被误报，加守卫后消除）；③ 严格通道 `query_rows(...)[0][0]` 合法不报（返回的确实是行元组）。
- 已知盲区（列给总包，不属本包范围）：a) 跨文件别名导入（`from … import query as q`）；b) f-string 拼出的 SQL 文本无法静态判形；c) `count()` 消费点的"判据类"识别属 W-180.3 存量污染清算，本尺不吞（需人工分级，配方见 §5）。
- 建议补丁位置（若今后命中）：统一换成 §2 严格通道，一次性判据读数改 `scripts/governance/data_supply/ch_probe.py（注：施工方案原指 `scripts/data/`，实测该目录被 .gitignore 第 603 行整体排除，故改道）`。

---

## 4. 红证（两把 canary，实测原文）

```
$ PYTHONPATH=src python -m pytest tests/governance/test_wave1a_strict_read_canary.py \
    tests/governance/test_wave1a_query_shape_ruler.py -q
tests\governance\test_wave1a_strict_read_canary.py ..............        [ 58%]
tests\governance\test_wave1a_query_shape_ruler.py ..........             [100%]
======================== 24 passed in 91.28s (0:01:31) ========================
```

- **红证一（"query 抛错"必红）**：`test_wave1a_strict_read_canary.py`——monkeypatch 把 TCP client 置 None、HTTP host 置 ""（人为造查询抛错），断言 `query_rows`/`count_strict` **必抛** 且 `attempts` 含 tcp+http 两条；把 `query_strict` 的 `raise` 删掉即红（出口判据"红证=去掉 raise 必红"）。同文件另证旧通道同刻返回 `""`（在册病基线，禁改），并断言"真空 0 行 ⇒ 返回 int 0 而不抛"两态可分、非只读语句必抛、`parse_tsv_rows` 与 `splitlines()+split('\t')` 对拍（5 组参数含空串/纯换行/含空字段）。
- **红证二（"按下标取值"必红）**：`test_wave1a_query_shape_ruler.py`——把 §7.1 的 P1/P2 病样本作输入（`ch_reader.query(sql)[0][0]`、`for row in ch_reader.query(...)`、`tsv = ch_reader.query(sql)` + `tsv[0][0]` / `for line in tsv`），断言尺必出对应 kind 且分级 `JUDGMENT`；CLI `main()` 退出码断言 **==1（红）**；反向 3 组正确用法断言零命中；再跑一遍 HEAD 树基线可复算。

---

## 5. D/E · 探针与 W-34 空壳表 strict 复测配方（**只出配方，不实跑**）

### 5.1 探针 `scripts/governance/data_supply/ch_probe.py（注：施工方案原指 `scripts/data/`，实测该目录被 .gitignore 第 603 行整体排除，故改道）`（W-180.4）

一次探测一行 JSONL：`ts_utc / sql_raw / sql_executed(FINAL 注入后) / transport(tcp|http|none) / elapsed_ms / rows / first_row_sample / outcome(ok|empty|fail) / error.attempts / channel`。产物落 `.runtime/tmp/ch_probe/ch_probe_<UTCstamp>.jsonl`（TTL 纪律，禁写生产路径）。**失败显式报红**：`outcome=fail` + stderr `[RED]` + 退出码 2，绝不降级成"空表"。

车道内实跑证据（C9，车道无 `config/.env.clickhouse` ⇒ 必然失败，正是"失败必报红不静默"的现证）：
```
$ PYTHONPATH=src python scripts/governance/data_supply/ch_probe.py（注：施工方案原指 `scripts/data/`，实测该目录被 .gitignore 第 603 行整体排除，故改道） --sql "SELECT count() FROM system.tables WHERE database = 'c1_market'"
[PROBE] 产物=...\.runtime\tmp\ch_probe\ch_probe_20260926T124616Z.jsonl 共 1 次：ok=0 empty(真空,已确证)=0 fail(失败,已报红)=1
[RED] 探测失败（禁降级为无数据）: ... -> {'type': 'ClickHouseQueryError', 'attempts': [['tcp','client 不可用（配置缺失或处于冷却期）'], ['http','host 不可用（配置缺失或处于冷却期）']]}
exit=2
```
> 落地面（主区有 CH 配置）才出真实读数；三个病样本复核（P1 行数≠1、P2 给真实值、P3 给"失败+传输路径"）由总包在落地窗口跑，本队不实跑。

### 5.2 W-34 空壳表 strict 复测取数配方（交总包在落地面统一执行）

**安全边界（先读后动，本包全程只读）**：ClickHouse 有 0 字节破损件事故史 ⇒ **禁 `mv` / `DETACH` / `RELOAD` / 重启服务，禁动任何容器与 `/var/lib/clickhouse` 元数据目录，禁任何写操作**；本配方三步全是 `SELECT`。

```bash
# 步骤 1｜取表宇宙（严格通道，勿用旧 query() 字符串直取）：库.表 + 引擎 + 字节数
python scripts/governance/data_supply/ch_probe.py（注：施工方案原指 `scripts/data/`，实测该目录被 .gitignore 第 603 行整体排除，故改道） --sql \
  "SELECT database, name, engine, total_rows FROM system.tables WHERE database NOT IN ('system','INFORMATION_SCHEMA')" \
  --out-dir .runtime/tmp/ch_probe
# 步骤 2｜对旧 W-34 空壳表清单逐表 strict 复测（真空 vs 失败两态分离）
python scripts/governance/data_supply/ch_probe.py（注：施工方案原指 `scripts/data/`，实测该目录被 .gitignore 第 603 行整体排除，故改道） --count c1_market.<table>          # outcome=empty + rows=1 才是"确证空壳"
# 批量（每行一条 SQL，# 注释）
python scripts/governance/data_supply/ch_probe.py（注：施工方案原指 `scripts/data/`，实测该目录被 .gitignore 第 603 行整体排除，故改道） --file docs/_working/total_command_closeout/wave1a/w34_recheck.sql
```
判读口径（写进复测表）：
- `outcome=empty` **且** `transport∈{tcp,http}` **且** `first_row_sample=[0]` ⇒ 真·空壳（可进 #311/#328 条件通道，逐件三层调查）。
- `outcome=fail` ⇒ **读数作废、不得计入空壳**（这类正是历史上被 `count()` 读成 0 的污染面）；换时段/换传输重探，仍失败则登记为"不可判"而非"空壳"。
- 逐表须留：strict 读数 / 传输路径 / UTC 时间戳 / JSONL 产物路径（与旧清单 diff 逐行说明差异＝W-180.3 出口判据）。
- 代码侧同批改造（W-180.3 存量污染清算）：凡判据路径调 `ch_reader.count(` 者逐个改 `count_strict()` 或加显式失败分支——本队未改（禁批量改生产调用点），清单由尺与 grep 现算：`git grep -n "ch_reader\.count(" HEAD -- src scripts tools`。

---

## 6. 待总包执行的热册补丁文本（本队禁改 `docs/01_policies_and_standards/**`，仅出 ```diff）

**必须"规则与代码同批"**：trae_034 明文指向 0 字节的 `data/zalpha_metadata.db`；活库是 `data/databases/governance.db`（1A.5 实测 203 MB、今日仍在写，`task_repo.py` 的 `DB_PATH` 亦此）。**禁止只改规则或只改代码**（留死指针＝1A.5 点名病灶）。

补丁 1｜规则册（3 处，行号为 2026-09-26 车道现读）
```diff
--- a/docs/01_policies_and_standards/rules/trae_034_task_card_standard.yaml
+++ b/docs/01_policies_and_standards/rules/trae_034_task_card_standard.yaml
@@ -37,7 +37,7 @@
     conditions: []
     actions:
     - type: mandatory
-      step: 唯一创建入口为TaskRepository.create()写入SQLite(data/zalpha_metadata.db)
+      step: 唯一创建入口为TaskRepository.create()写入SQLite(data/databases/governance.db)
     - type: mandatory
       step: .md文件为伴读副本，不作为创建入口
@@ -209,7 +209,7 @@
     - type: pre_condition
-      check: 阶段一建卡完成——按task_001_template/task_001_fields/task_001_granularity建卡，所有任务卡已写入SQLite(data/zalpha_metadata.db)
+      check: 阶段一建卡完成——按task_001_template/task_001_fields/task_001_granularity建卡，所有任务卡已写入SQLite(data/databases/governance.db)
       pass: 进入阶段二批量审查
@@ -557,7 +557,7 @@
     steps:
     - order: 1
-      action: 调用TaskRepository.create()写入SQLite(data/zalpha_metadata.db)
+      action: 调用TaskRepository.create()写入SQLite(data/databases/governance.db)
       pre_condition: 任务卡数据准备完毕
```

补丁 2｜代码侧同批（唯一活消费者，去掉死指针读路径）
```diff
--- a/scripts/governance/d5_architecture/validators/validate_cross_references.py
+++ b/scripts/governance/d5_architecture/validators/validate_cross_references.py
@@ -222,7 +222,8 @@
-    db_path = REPO_ROOT / "data" / "zalpha_metadata.db"
+    # 波 1A.5：zalpha_metadata.db 实测 0 字节（死指针），活库=governance.db；
+    # 与 rules/trae_034_task_card_standard.yaml 同批改，禁单侧改。
+    db_path = REPO_ROOT / "data" / "databases" / "governance.db"
```
（`src/zephyr/infrastructure/asset_inventory/registry_adapter.py:37` 仅注释提及，无功能指针，批注可择机顺手改。）

补丁 3｜depgraph 指针簇（30 处 .py / 11 处带路径真指针）——**本队不给 sed 式批量 diff**：
先由总包裁"真源是否已全量迁 Postgres（`DatabaseService.get_depgraph_conn()` 返 psycopg2）"，再按 `store_liveness_census.jsonl` 的 `ref_files_sample`/`consumer_files_sample` 逐条归属（3/4 消费者在 `scripts/_archive/**` ⇒ 建议整簇按"归档件不改、活件改指"处理）；两处分身 `data/depgraph.db` 与 `data/databases/depgraph.db` 须收敛为一（内收"同域重复簇→收敛唯一"），**退役动作走 #311/#328 条件通道，本包零删除**。

---

## 7. 命令台账（原文可复算）

| # | 命令原文 | 用途 | 输出锚 |
|---|---|---|---|
| C1 | `find D:/ZephyrAlpha/data -maxdepth 3 -name "*.db" -size 0` | 盘面 0 字节库普查（7 个） | §0 verified-1 |
| C2 | `ls -la D:/ZephyrAlpha/data/databases` / `ls -la D:/ZephyrAlpha/data/*.db` | 活库字节与 mtime 实测 | §0 verified-2 |
| C3 | `grep -rn "def query\b\|def count\b\|ch_writer\|get_clickhouse_conn" src/zephyr/infrastructure/ src/zephyr/data/` | fail-silent 契约定位（`ch_reader.py:13`、`ch_writer.query` 双失败 `return ""`） | §0 verified-3 |
| C4 | `python scripts/governance/wave1a/store_liveness_probe.py --root . --live-root D:/ZephyrAlpha --out-md docs/_working/total_command_closeout/wave1a/store_liveness_census.md --out-jsonl docs/_working/total_command_closeout/wave1a/store_liveness_census.jsonl` | 四列普查表（尺能红：仍有 0 字节库 ⇒ 退出码 1） | §1 表 |
| C5 | `git grep -rl "depgraph\.db" --include=*.py src scripts tools \| wc -l` | 独立复核尺口径（HEAD 面=30；尺现读 31＝多出的是车道内新写件自引用；波 1A.5 原记 34 属旧口径） | §1 注 2 |
| C6 | `git grep -rn "zalpha_metadata" docs/01_policies_and_standards/rules` | trae_034 三处死指针定位（行 40/212/560） | §6 补丁 1 |
| C7 | `python scripts/governance/wave1a/ch_read_shape_ruler.py --root . --out-md …/read_shape_violations.md --out-jsonl …/read_shape_violations.jsonl` | HEAD 树形状尺（129 候选 / 0 命中 / 退出码 0） | §3 表 |
| C8 | 同上 `--files <canary>` | 误报治理复算（splitlines/isinstance/query_rows 三组不报） | §3 判读 |
| C9 | `PYTHONPATH=src python scripts/governance/data_supply/ch_probe.py（注：施工方案原指 `scripts/data/`，实测该目录被 .gitignore 第 603 行整体排除，故改道） --sql "SELECT count() FROM system.tables WHERE database = 'c1_market'"` | 探针失败显式报红实跑（车道无 CH 配置，exit=2） | §5.1 |
| C10 | `PYTHONPATH=src python scripts/governance/data_supply/ch_probe.py（注：施工方案原指 `scripts/data/`，实测该目录被 .gitignore 第 603 行整体排除，故改道） --count c1_market.kline_daily` | count 通道（outcome=fail，未降级为空壳） | §5.1 |
| C11 | `PYTHONPATH=src python -m pytest tests/governance/test_wave1a_strict_read_canary.py tests/governance/test_wave1a_query_shape_ruler.py -q` | 两把红证（24 passed） | §4 |
| C12 | `git show HEAD:src/zephyr/data/ch_writer.py \| grep -n -A 22 "def get_client_strict"` | 既有"半个严格入口"取证（合并对象） | §0 verified-4、§2 内收-2 |
| C13 | `git rev-parse --short HEAD` | 案卷基线（`5701fb99c8`） | 卷首 |

---

## 8. 遗留与待总包（本队未做，勿误判为已做）

1. **CREATE-GUARD / 翻译登记**：本包新建 5 个 .py（含 2 个测试，tests 豁免），非测试 3 件须登记 creation_token + `add_module_translation.py` 大白话简介 + `apply_depgraph.py --add-design-node`；本队未跑（改热册/注册表属总包集中动作）。
2. **W-180.2 升 gate**：本尺是判据函数原型（`scan_text()` 可直接 import），升 gate 须登记 own_scope 与 files_trigger（禁 `files_trigger=''` 全链跑，1A.3 现案）。
3. **W-180.3 存量污染清算**：`ch_reader.count(` 消费点判据分级 + `get_client_strict()` 自助通道退役，逐件走 §5.2/§2 内收-2 口径。
4. **W-180.5 审计读数复核**：G 册与终审卷直读结论按 §5.1 通道复核（本队未碰任何册面读数）。
5. **0 字节库的删除/退役动作**：本包零删除；`scheduler_progress.db` 等退役须走 #311/#328 逐件三层调查。
6. 普查尺口径两处可再收紧（列备，未做）：把 `scripts/_archive/**` 引用单列一栏计数；对 `.bak`/备份层（`data/backups/zalpha_metadata_*_pre_close.db`）加取证只读索引。
