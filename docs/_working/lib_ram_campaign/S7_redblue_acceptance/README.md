---
ttl: task_bound
title: S7 红蓝验收设计 · 图书馆内存常驻缓存战役（只设计不落码：五条红 + 三条蓝 + 夹具隔离纪律 + 断言位）
created: 2026-09-29
sid: st-libram-s4s7-20260929
status: 设计定稿（自审=未干，B3 尺子基线阻塞见 §5）
---

# S7 红蓝验收设计（不落码）

**验收对象**=Owner 定版规格的四条硬约束（世代原子交换 / 读时版本比对+single-flight / 快照留 2 份轮转 / 常驻层条件与内存硬顶）。
**设计纪律**：每条给「夹具怎么搭 → 判据 → 失败即红的断言位」三件套；
红=必须拦住，蓝=必须零改动仍绿。**任何夹具禁写 `data/` 业务目录与生产快照目录**（根宪法 §9.4/§9.6）。

体例循 `docs/_working/fms_overhaul/00_orchestration.md` §四（六向台账 + 自审闸三态）。

## ① 真源（判据从哪来，不许自造）

| 判据 | 真源位 |
|------|--------|
| 至多 2 世代、峰值 ≈200MB、代码常量封死、无逐条淘汰 | Owner 定版规格 §1（战役任务书）；实现常量位由 S2 定 |
| 刷新=读时版本号比对 + single-flight，全链禁 cron/Timer/sleep-loop | Owner §2 + 根宪法 §9.3（`AGENTS.md` §9 条目 3） |
| 磁盘只留 2 份、新快照落盘成功才删上上代 | Owner §3 + S3 §4.3 七步崩溃安全序（提交点①②） |
| `--max-memory-mb 512` 硬顶 + 并入 reaper RAM 水位 | Owner §4 + S5 §⑤（reaper `_DANGEROUS_MEM_GB`/keep 语义） |
| 版本水位口径 `max(event_id)` | S1 案 B（现值 [读档，转引 S3 §3.1] 2,231,744；行数量级 44,963 转引 S3 §4.1） |

## ② 写者（谁产夹具数据）

- **PG 侧**：红队需"能改库但不 bump 版本"的能力 → 夹具自带**私有 PG 不可行**（禁测连生产库，根宪法 §9.6 测试隔离），
  故红队数据面一律走**注入缝**：复用现成 DI 模式
  （`library_regen_reconciler.make_library_regen_reconciler(gateway)` 接受 `project_root` 注入，
  `src/zephyr/library/library_regen_reconciler.py:99-107` + 夹具先例 `tests/library/test_library_regen_reconciler.py:38-41`）
  与 fake-conn 模式（`tests/library/test_lookup_tombstone.py:4` 自述"零 DB 依赖：fake conn/cursor 记录参数，CLI 走 monkeypatch lookup_assets"）。
- **磁盘侧**：`tmp_path` 作快照根（覆盖 S3 判家 `data/library_snapshots/` 的路径参数），
  文件名携版本（S3 §4.2 命名 `lib_snapshot.v<ledger_version>.<ext>`）→ 损坏/截断/轮转全部可在纯文件层造假，零 PG 依赖。

## ③ 消费者（这套验收谁跑）

| 消费方 | 挂法 |
|--------|------|
| pytest（施工批自测） | 新目录 `tests/library/test_ledger_cache_*.py`（红蓝各成文件，命名循 `tests/library/` 现风格；被测件=**`src/zephyr/library/ledger_cache.py`**，与 S2 §4.2 同调） |
| 提交门 | 不新增门（净零 §⑥）：靠 S4 §③C 既有门禁消费面回归（B2）兜 |
| 既有两把尺 | `check_library_tri_consistency.py`（三层断言，`:7` 纯只读、exit 0/1/2 语义 `:13`）+ `regen_clean_check.py`（`--check/--staged/--pairs`，`:30-32`）——见 B3 |

## ④ 红队夹具总则（每条红都适用的公共约束）

1. 每夹具**独立 tmp_path**，禁共享生产 `data/`、`docs/library/`、`.runtime/` 根（根宪法 §9.4）。
2. **fake 世代戳发生器**：`VersionWatermark` 桩（返回可控 `ledger_version`），禁在测试里 `datetime.now()`/`time.time()`
   （根宪法 §1 规则 10 RULE-SCHEMA-TZ：生成器禁裸时间；测试同样守此例以免污染基线）。
3. 并发用 `threading.Barrier` + `ThreadPoolExecutor`，**不用 sleep 等时序**（sleep-loop 是宪法红线，测试里用 sleep 会造出假绿/假红）。
4. 内存上界断言用 `resource`/`psutil` 读 RSS 的**相对增量**（`psutil` 在本仓可用，先例
   `src/zephyr/trading/process_reaper.py:392,428` 用 `proc.memory_info().rss`），禁绝对值断言（机器相关=抖动红）。
5. 每条红**必须能在未实现版本上先跑出红**（真红可复现原则）：施工前先落"预期 FAIL"的 xfail 记录，
   实现后转 PASS 并删 xfail——防"写了个永真断言当验收"。

## ⑤ 红队用例（5 条）

### R-1 版本号跳变 × 并发查询 → single-flight 只放 1 个加载

- **夹具**：tmp 快照根预置 v1 代；`VersionWatermark` 桩初值 v1，在 `Barrier(N)` 全部线程就位后翻 v2；
  加载器桩 `loader()` 内用 `counter`（`itertools.count` + 锁）记录进入次数；N=16。
- **判据**：版本跳变后，**恰 1 个**线程执行真实加载，其余 15 个等待并复用同一次结果；
  等待者不得回退直连 PG（否则 single-flight 失效退化为惊群）。
- **失败即红的断言位**：
  - `assert load_counter == 1`（>1 即红：single-flight 破防）；
  - `assert len({id(served_generation)}) == 1`（结果对象同一实例，防"各装各的"）；
  - `assert max_concurrent_generations <= 2`（任意时刻存活世代 ≤2：服务代+加载代，Owner §1）——
    实现侧要求缓存对象暴露 `live_generations()` 观测口，**无观测口即判红**（缺可测性也是红）。

### R-2 快照文件损坏/截断 → 必须回落 PG 且报红

- **夹具**：tmp 内按 S3 §4.2 生成合法 v 代文件 + manifest；然后三型破坏各一例：
  (a) 尾部截断 1 字节；(b) 中间随机字节改写（校验和必失配）；(c) **manifest 指向不存在的文件名**（半提交态，S3 §4.3 崩溃窗口③）。
- **判据**：读侧行为=**拒绝使用快照 + 回落 PG 真源 + 显式报红**（三件事缺一即红），
  绝不"静默降级为部分行集"（部分行集=假真源，最坏结局）。
- **失败即红的断言位**：
  - `assert result.source == "pg"` 且 `assert result.degraded is True`（回落但**必须自报**）；
  - `assert snapshot_load_error is not None`（有异常对象，不许吞——对照现网 fail-open 前科
    `capability_lookup.py:292-294` 探针失败静默 return None，缓存层不得继承这种"吞"）；
  - (c) 型：`assert served_generation is None`（半提交态下不得认任何代）。

### R-3 超内存上界 → 拒绝加载新代，不得 OOM

- **夹具**：把世代上限常量注入为**极小值**（如 4 行/2MB，走 DI 缝而非改生产常量），加载器喂 5 行伪代；
  同时在测试进程内 `psutil.Process().memory_info().rss` 取基线。
- **判据**：**新代加载前**先估体积（行数 × 平均行字节 or 序列化长度）→ 超限则放弃换代、
  保留旧服务代、返回明确的 `refused` 语义；旧代继续服务（RCU：不交换=无影响）。
- **失败即红的断言位**：
  - `assert served_generation.version == old_version`（旧代未被撕）；
  - `assert outcome == "refused_over_cap"`（不许返回部分行集、不许抛未捕获异常）；
  - `assert rss_delta_mb < cap * 1.2`（RSS 相对增量封顶，防"估算通过但实测爆炸"）；
  - `assert peak_live_generations <= 2`（Owner §1 峰值≈200MB 的代码封死条款在此被机器检验）。

### R-4 写侧脏读：改库不 bump 版本 → 读侧必须能证明"读到旧代"可发现

这是**规格自身最尖锐的一条**（读时版本比对的逻辑盲区）：
`lib_events` 只追加留痕经 `Librarian.act`（`governance/migrations/add_library_successor_of.py:26` 写明写入路径唯一=`Librarian.act`），
但**裸 SQL 直写 `lib_assets`** 不产生 event → `max(event_id)` 不变 → 版本比对永远判"无需刷新"。
真实先例即 S6 §④1 的裁-07 事故（三轮全量 ingest 悄悄清零 68 资产的供数轴，靠事后 `count` 对账才发现）。

- **夹具**：桩世代 v1（含 asset X，`status=active`）；"库变"桩直接把 X 改成 `deceased` 而**不动 event 水位**；
  断"读侧拿不到 PG 真相，只能自证"。
- **判据（分两层，别混）**：
  - L1 **可归因**（必须绿）：每条返回行/结果对象携 `generation`/`ledger_version` 标签，
    读侧 API 暴露 `served_generation` 与 `stamp_checked_at_watermark`——
    即使内容陈旧，**"这是第几代"必须永远为真且可打印**。
  - L2 **可发现**（弱保证，须显式声明）：提供**廉价判别子**（`row_count` + `sha256(有序主键串)`，
    S3 §4.2 manifest 已含 `row_count/sha256` 字段）随版本比对一并抽样核；判别子不一致=报红并强制换代。
    设计红线：**不得把 L2 说成 L1 的替代**，也不得承诺"零漏检"（裸写不 bump 版本时唯一可靠防线是写侧纪律）。
- **失败即红的断言位**：
  - `assert all(r.get("generation") for r in rows)`（无代标签=红，这是最便宜的防线）；
  - `assert rows_come_from_single_generation(rows)`（**禁跨代混行**：一次响应内行必须同代，混代=最恶心的静默错）；
  - 判别子路径：`assert probe_mismatch_triggers_rebuild is True`（sha/row_count 失配却没触发换代=红）；
  - 写侧校验对照：`ingest_with_shrink_guard` 型对账（`library_regen_reconciler.py:62-98`）在夹具里**必须读到 PG 现值**，
    若把它改接缓存层，断言 `counter()` 返回值来自 fake PG 而非缓存（**S4 §⑤"写侧校验禁读缓存"的机器锁**）。

### R-5 PG 断连时缓存复用不得伪装成真源

- **夹具**：`get_depgraph_pg_connection` monkeypatch 成抛 `psycopg2.OperationalError`
  （连接口即 `lookup.py:35,116`；另一条 `--feeds` 口 `lookup.py:247` **两条都要单独测**，
  这是 S4 §③A A3 点名的第二连接路径）。
- **判据**：PG 不可达时，缓存/快照**可以**继续供读（可用性收益，S3 §3.3 明写"PG down 兜底"），
  但每次响应必须带 `authoritative=False` + 陈旧度（`served_generation.version` vs 最后成功核到的水位）；
  人类可读输出（CLI）必须显式打印降级横幅，**禁与正常命中同形**。
- **失败即红的断言位**：
  - `assert result.authoritative is False`（伪装真源=红，本条是本战役对"报假平安"零容忍的核心）；
  - `assert "stale" in cli_stdout.lower() or result.degraded_reason`（CLI 面必须可见；
    对照现契约 `lookup.py:13` [ERROR_CONTRACT] "DB 异常原样上抛；CLI 无结果返回 1"——
    改造后**语义变更须同步该头部**，否则头部与实现背离即判红（这是可机检的文档-代码同代断言））；
  - `assert exit_code != 0 or degraded_flag_set`（不许"静默返回 0 + 空结果"糊过去）。

## ⑥ 蓝队用例（3 条，必须零改动仍绿）

### B-1 正常查询命中

- 夹具：真实小代数据注入 tmp；首次装载→同版本再查→跨版本查询三段。
- 判据：同版本期间**零 PG 查询、零磁盘快照 IO**；结果与直连 PG 的基线**逐行同序同字段**
  （序敏感参照既有尺 `check_library_tri_consistency.py` 断言 1 "rows[:_DISPLAY_CAP] 逐行 (asset_id,kind,status,home) 与总账复核（序敏感）"）。
- 断言位：`assert pg_query_count == 0`（第二次查询）；`assert cached_rows == pg_rows`（含 `lookup.py:132-142`
  的逐深度轮转合并语义、`:288-293` 的墓碑升级提示行为不变）；别名展开路径 `lookup.py:81-98` 结果与 `--no-alias` 对照不变。

### B-2 门禁消费面回归零改动

- 夹具：**不新建测试**，直接跑 S4 §③C 清单的既有测试群
  （`tests/governance/test_capability_library_dedup.py`——其 `:21` 自述"monkeypatch lookup_assets + tmp_path 审计目录，零真实 PG 依赖"；
  `tests/governance/commit_gates/test_capability_lookup_audit_log.py:83-89,159-201`；
  `tests/governance/rule_bridge/test_ssot_gate.py:121-148`；
  `tests/gov_enforcement/test_library_blood_flesh_gate.py`、`tests/capability/test_capability_lookup.py`）。
- 判据：**这些测试文件一行不改全绿** = 门禁消费面契约未破；且 `git diff --stat` 对上述路径为空。
- 断言位：`git diff --name-only` ∩ S4 §③C 清单 = ∅（改动即红，说明读侧改型污染了门禁面）；
  探针 fail-open 语义保持：`assert _library_dedup_probe(boom_pg) is None`（不得抛，`capability_lookup.py:292-294`）。

### B-3 两套既有尺仍绿（**当前阻塞，不得当作已定基线**）

- 夹具：`python scripts/governance/generators/check_library_tri_consistency.py`（不带 `--skip-regen`，
  让它自带 regen-clean 子步：子进程再生成 + `git diff --exit-code docs/library/`，`:11` INVARIANTS 实证）
  + `python scripts/governance/generators/regen_clean_check.py --check`（`:30`）。
- 判据：tri 尺 `exit 0`（`:13` 语义：0=三层一致 / 1=有漂移 / 2=总账不可达）；regen-clean 零脏。
- **阻塞取证（本会话实测，见 S6 §⑤b）**：`check_library_tri_consistency.py` 处于
  index 已 `D` + 盘上 untracked 重建态（`git ls-files --error-unmatch` 判 NO），
  `regen_clean_check.py` 处于 `M ` staged 已改态 → **两把尺自己都在别人手里**，
  现在跑出来的绿/红都不是本战役可归因的基线。
  → 处置：B3 施工前必须先做"尺子基线快照"（记录两尺当前 exit code + 盘上/HEAD 行数差），
  本战役只要求**不使情况变差**（棘轮判据，`00_orchestration.md` §二.1），不要求绝对绿。
- 断言位：`assert exit_code_before == exit_code_after or (before!=0 and after==0)`（只许变好，变差即红）。

### 蓝队附加不变量（低成本高价值）

- `assert lookup_cli_latency_p50 < baseline`（基线 = S5 §① 实测 2570ms；缓存改造对 CLI 形态收益上限 ≈4% 是 [亲验] 已知事实，
  **禁止用"CLI 快了几倍"当蓝侧指标**，那是假绿；常驻化后另立 <10ms 口径，见 S5 结论 B）。
- `assert release_called and close_called is False`（`depgraph_schema.py:1625-1628` 文档串要求 pooled 连接走
  `release_depgraph_pg_connection()`，现 `lookup.py:144` 用 `conn.close()`——改造顺带纠正，属净收益非必需）。

## ⑦ 净零方案

1. **不新建红蓝基建**：夹具全部复用仓内既有三模式（`tmp_path` 注入 / fake conn 记录参数 / monkeypatch 模块函数），
   先例即 §② 引的四个测试文件；禁引入 pytest-timeout/flaky/wrapper 类新插件（新依赖=净增）。
2. **不新增验收门**：红蓝用例是测试不是 gate；新门须声明替代旧门（根宪法 §4.1 + `registry_mass_deletion_gate.py:8` 净删风险），
   成本不划算，且 B2 的意义正是"门禁面不加不减"。
3. **被测件名与 S2 同调**：红蓝夹具一律指向 **`src/zephyr/library/ledger_cache.py`**（S2 §4.2 实现位 `:120`、
   常量位 `_MAX_GENERATIONS=2` `:145`）；S7 不得引入第二个模块名（两名并存=第二真源，违净零）。
4. **簿内不留第二真源**：S7 只写"怎么验"，规格数值（200MB/512MB/2 代/版本口径）一律指回 S1/S2/S3/S5，
   不复制数字（防 `00_orchestration.md` §4.3 记过的"文档自相矛盾=事故"）。
   **注意 S2 §50 已给出体积实测**（单代 tracemalloc current 36.5MB / peak 41.3MB，2 代 ≈73-83MB），
   S7 R-3 的 cap 断言应引用该实测而非自造估算。
5. **测试件三件套**（施工批仪式）：新 `tests/library/test_ledger_cache_*.py` 须带
   `[A_test]/[BLUEPRINT]/[MODULE]` 头部（先例 `tests/library/test_library_regen_reconciler.py:1-11`）；
   creation_token 对 tests/ 豁免（根宪法 §1 CREATE-GUARD 括注），**大白话简介亦不罚 tests/**
   [亲验 `src/zephyr/governance/audit/translation_coverage_reconciler.py:108,131`——
   "tests/ 路径段（is_test_exempt 单一真源，含 scripts/tests/）"为排除项]，
   脚本真身=`scripts/governance/d3_metadata/add_module_translation.py`（tracked）。

## ⑧ 自审闸三态

**状态：`未干`（五条红 + 三条蓝的设计与断言位已可直接落码；两处硬缺口使 B 侧基线未定档）**

已干：
- 红 5 条全部给到夹具/判据/断言位三件套，且**每条都锚在真实代码位或真实事故先例**上
  （R-4 锚裁-07 缩水闸 `library_regen_reconciler.py:62-98`；R-5 锚两条独立连接口 `lookup.py:116,247` + ERROR_CONTRACT `:13`；
  R-2 锚"探针静默 fail-open"前科 `capability_lookup.py:292-294`）；
- 规格盲区的处理有明确立场：R-4 拆 L1（可归因，硬要求）/L2（可发现，弱保证并禁止夸大），
  避免验收时拿"发现不了裸写"判成实现失败——**这是本战役最可能被误判红的一条**；
- 蓝侧 B-2 用"既有测试文件零改动 + git diff 交集为空"当机检断言，比"我测过了"可核；
- 假绿防线显式写入（禁用 CLI 延迟当蓝侧指标、禁绝对值 RSS 断言、禁用 sleep 造时序、真红可复现先 xfail）。

缺口（据此不可判"挖干"）：
1. **B3 基线未定档**（§⑥ B-3 已给处置方案=棘轮式"不使变差"，但需总筹认这一判据降级是否可接受；
   两把尺目前在 st-p1b/FMS B4 手里，见 S6 §⑤b 表行 2 与 §②盘面块）。
2. **single-flight 的可观测口未定规格（跨簿接口缺，优先级最高）**：R-1/R-3 依赖缓存件暴露
   `live_generations()` / `served_generation` / `load_counter` 三个读口；
   复读 S2 §4.2（`S2_librarian_cache/README.md:117-145`）后确认 S2 只承诺
   `_GUARD = threading.Lock()` 单飞锁 + `_current` 模块内唯一 rebind + `_MAX_GENERATIONS: Final[int] = 2` 常量，
   **未规划任何测试观测口**（S2 全文 grep `观测|metrics|可测` 零命中 [亲验]）。
   → 二选一交总筹：(a) S2 加 3 个只读诊断口（改动小、验收可机检）；(b) R-1/R-3 降级为
   "黑盒间接断言"（用 PG 连接计数代理 single-flight 次数）——**精度显著变差**，且 `max_live_generations`
   将彻底不可检（Owner §1 的"至多 2 世代"失去机器守卫，只剩常量声明）。
3. ~~tests/ 是否需大白话简介~~ **已闭**（§⑦5：`translation_coverage_reconciler.py:108,131` 明列 tests/ 路径段为排除项）。
4. **内存估算口径未定**：R-3 的"加载前估体积"用行数还是序列化字节长未定；
   但 S2 已给实测锚（单代 current 36.5MB / peak 41.3MB，`S2:50`）→ 建议判据改为
   **以代数为主（`live_generations <= 2`）+ RSS 相对增量为辅**，cap×1.2 系数仍是 [推断] 待施工标定。
5. **[未跑] 现有测试基线**：本会话未实跑 `tests/library/` 与 B-2 清单（工具预算优先给了延迟实测与盘面取证），
   故"改造前这些测试是绿的"这一前提目前为 [读档]（来自各文件 [TESTS] 头部），非 [亲验]。施工批须先跑一次记基线。
   补一条已闭的旁证：S5 §结论 B' 实测**同进程现读 PG 单次 121.8-271.7ms**，
   说明 B-1 "同版本期零 PG 查询"这一断言在改造前必然 FAIL（=真红可复现，符合 §④5 原则）。

受阻：无（设计簿无阻塞；缺口 1/2 属跨簿接口，非环境阻塞）。
