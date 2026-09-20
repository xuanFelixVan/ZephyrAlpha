---
ttl: task_bound
title: ENV1 清洁零风险三类·逐件三层判决挖矿作业簿（挖矿不执行）
owner: ZephyrAlpha-Owner
session: st-cleanexam-20260918/A
date: 2026-09-18
status: mining_complete
---

# ENV1 清洁零风险三类 · 挖矿作业簿

> **授权**：ruling_registry #清洁执行（2026-09-18，active）——Owner 附条件批准删除三类零风险件；条件=逐件三层调查全过才删，任一层不过即保留留档。本作业簿只挖矿判决，**未执行任何删除/DROP**。
> **基线**：`docs/_working/sharpe2_prep/c_audit/2026-09-17-cleanliness-audit.md`（fe8fce25b7）。**判据**：①真安全（不破坏链路）②真无人用（rg 全根目录+双真源 yaml）③真无价值（count()/哈希/正本比对）。
> **产物**：`verdict_tables.csv`（10 表逐件）｜`verdict_files.csv`（129 行逐件）｜`execution_plan.md`（只设计不执行）。

## 0. 挖矿日志

| 轮 | 矿脉 | 判定 | 关键产出 |
|---|---|---|---|
| R1 | 10 空壳表行数复验（CH 只读经 DatabaseService） | signal | 10/10 count()=0、0 字节、c1_market、ReplacingMergeTree——基线准确 |
| R2 | 10 表引用面 rg（src/scripts/config/docs/data/tests/.trae + 补盲 schemas/tools/meta/models/acceptance/architecture_model/runtime/vendor/_journals/_diag） | signal | 仅 3 类命中：审计文档、data_inventory.md（机生盘点）、finish_p0_1.py（4 表）；schemas/ 全目录零 tzbak 登记；script-manifest 仅注册条目；无 tasks.yaml/调度引用 |
| R3 | finish_p0_1.py 定性 | signal | STARTUP=manual、CONSUMERS=Owner/施工会话手动（2026-09-14 行情修复批）、INVARIANTS 自载"备份表清理恒 mutations_sync=1"——0 行=修复链已消费完毕；repair_kline_tz_monthly.py `--bak-suffix` 为创建侧参数。非活链路 |
| R4 | CAS tmp 全量重扫+全量正本比对（125 件，超抽样 20 件要求） | signal | 124 件 glob（114 catalogs 含 _archive 1 件、7 config、4 data）+1 件 heartbeat 特判；**123 正本较新+1 逐字节相同+0 件 tmp 较新**（heartbeat 例外见 R5）；总量 22.1 MB；较基线 110 件净增 15/天 |
| R5 | 特殊写者逐一核验（metrics.py:221 / watchdog.py:53 / governance_watchdog.py:110 / crisis_gate pid 风格） | signal | metrics.prom 正本活跃（03:24 刚写）；watchdog 只读固定名正本；heartbeat tmp 较正本新 16 分钟但为**临时态心跳**（正本 09-06 已停跳 12 天、对端过期阈值 1800s、内容=时间戳）→零价值可删；`data/runtime/tmp_protocol_head.md` 为 find 误匹配（task_bound 协议文档）→排除 |
| R6 | db bak 字节级复验（md5+sha256+cmp） | **signal（基线证伪）** | b/c 同尺寸 29,282,304（基线误写 28,282,304）但 **md5 不同**，cmp 差 **14,239 字节**——非逐字节重复；首份 bak_20260909 亦三不相同。"纯重复"前提不成立 |
| R7 | 裁定登记反查 | signal | ruling_registry #清洁执行（2026-09-18）条件明载"纯重复三选一"——前提被 R6 证伪，按裁定自身条款"任一层不过即保留留档"改判 |

**noise/受阻轮：无**（本轮全内部反查，未出网，无 429）。

## 1. 三类判决总览（逐件明细见两个 CSV）

| 子类 | 可删 | 保留 | 需再证 | 说明 |
|---|---|---|---|---|
| (1) 空壳 CH 表 | **10/10** | 0 | 0 | 三层全过；回滚 DDL 已快照 |
| (2) CAS tmp | **125/125** | 0 | 0 | 124 glob 全量比对 + 1 heartbeat 特判；另有 1 件排除（非残留）；全量 22.1 MB |
| (3) db bak b/c | 0 | **2** | 0 | **基线"纯重复"被字节级复验证伪**，按裁定条款保留留档 |

## 2. 六向台账

- **①上游**：基线审计 §1.3/§2.1 + ruling #清洁执行（2026-09-18）——授权与条件已核（R7）。
- **②下游（消费方反查）**：10 表——0 活消费（4 表仅历史 manual 修复件引用，R2/R3）；tmp——0 消费（mkstemp 随机名不可被引用；`*.yaml` glob 不匹配点前缀；metrics/watchdog/crisis_gate 写者只读正本，逐一经代码行号核验）；bak——0 程序消费（ruling/审计/机生全项目树引用=文书非消费）。
- **③算法/机制**：CAS 语义真源 `src/zephyr/shared/io/file_utils.py`——atomic_write 异常路径**有** unlink，故 catalogs 残留=进程被硬杀绕过清理；`src/zephyr/data/metrics.py` flush 异常路径**无** unlink=实锤泄漏通道（治本长尾 L2）。验证机制=count()（CH）+md5/sha256/cmp（字节）+mtime 次序（时序）+git check-ignore（追踪面）四重交叉。
- **④后端**：回写生成器 `scripts/ch/_data_inventory.py`（manual 只读盘点）；既有清理件 `scripts/ops/cleanup_runtime_tmp_residue.py`（scope=.runtime/tmp 测试残留，**不含**本批三处，扩 scope 候选=L3）；`finish_p0_1.py`/`repair_kline_tz_monthly.py` 标注"勿再跑"。
- **⑤前端**：查无（零 UI 关联，不登记）。
- **⑥数据字段**：CH system.tables+count() 逐表实查 10/10；字节级三重（md5/sha256/cmp -l=14,239）；tmp mtime 全量 125/125。

**防噪音四闸自检**：来源可溯（基线文件+裁定编号+代码行号逐条）✓；交叉验证（CH 复验+双哈希算法+rg 两轮含补盲目录）✓；A 股适配（不适用——仓内卫生域）✓；可回测/数据可得（不适用，以"行数实查=0"替代价值判据）✓。

## 3. 执行链五环（设计，详见 execution_plan.md）

复核（执行日 count()/mtime/增量重扫）→ 冻结清单（精确路径白名单+排除清单，禁通配）→ 执行（SHOW CREATE 快照→逐表 DROP；tmp 10 分钟 mtime 守卫+tar 暂存→按名删除）→ 验证（system.tables 查无+tmp 复扫+git status 零漂移）→ 回写（data_inventory 再生+本簿收口+长尾登记）。**bak b/c 不入执行清单。**

## 4. 挖后自审闸

- **北极星**：把"Owner 逐件人工考证垃圾件"变成机器逐件三层判决+可一键执行的清单——消灭 Owner 逐件考证的人工环节，且全部可自动化（执行链五环全脚本化路径）。
- **过度工程三问**：①收益实算=22.1 MB tmp+10 空表+判决留档，决赛前安静期宣示性清理，成本一次会话；②已有产物覆盖=否——基线只定性未逐件三层，本簿补齐判决层；③成本实算=挖矿 1 会话已沉没，执行 1 会话内。
- **反驳者一问（对删除计划列最强三条再驳回）**：a)"tmp 或有未落盘写"→全量比对 0 件 tmp 较正本新+执行环 3 仍设 10 分钟守卫；b)"空表或被未来脚本用"→26 根目录零引用+DDL 快照秒回滚；c)"删除动作自身风险"→回滚件三套（DDL/tar/全 gitignored 不触追踪树）+裁决条件化。
- **三态裁定**：**施工**（=执行计划就绪，按 ruling 条件进入执行；挖掘本身封矿）。分域：类 1 清理封矿；类 2 清理封矿+治本挂起（L1/L2/L3 长尾）；类 3 **方案封矿**（判决=保留，非删除候选，留档即交付）。

## 5. 与基线的偏差（诚实记录）

1. **bak b/c"纯重复/同字节"证伪**：实际尺寸 29,282,304（基线写 28,282,304 系笔误）；md5/sha256 全不同；cmp 实差 14,239 字节（同日 15:59/16:13 两个不同快照）。基线"疑似"二字保留了一半诚实，本次定量坐实"非重复"。
2. **tmp 规模漂移**：110→125（+15/天）；新增 pid 风格残留 `config/crisis_gate.yaml.24676.tmp`（今日 02:17）——泄漏不止 safe_write_text 一条通道。
3. **finish_p0_1.py 引用为基线未列事实**：4 张 tzbak 表引用面非绝对零，定性=历史一次性 manual 修复件后可删。
4. **heartbeat tmp 较正本新 16 分钟**：基线笼统"低风险"，本次给出机制级定性（临时态、正本停跳 12 天）仍判可删。
5. 空壳 10 张行数、git 追踪树 0 件——与基线一致（基线准确处如实确认）。

## 6. 长尾矿脉（未挖，登记续挖）

- **L1**：atomic_write 异常清理被进程硬杀绕过——治本方向=注册表写者侧启动清扫或 CAS tmp 周期 reconciler（事件触发，红线：禁 cron/sleep-loop）。
- **L2**：`src/zephyr/data/metrics.py` flush except 路径补 unlink（一行级修复，src 域施工件）。
- **L3**：`cleanup_runtime_tmp_residue.py` 扩 scope 至 catalogs/config/data 三处（复用其 PID+TTL 双判定骨架）。
- **L4**：pid 风格写者（crisis_gate/watchdog_state）源头定位与统一收敛到 atomic_write 真源。

## 7. 范围外保持原状（防越界）

中风险 8 件（§2.2 六表+§1.2 forensic/backup db bak，其中 auction_book_limit_bak 需 Owner 先裁定唯一副本存废）、疑似死配置 4 件（考证清单已转 Owner）、`docs/_working` TTL 316 件、`.runtime/sessions` 111 过期候选、`integrator_progress.db.bak_20260909` 首份与 20260916 系备份——**本役一律不动**。

## 8. 留痕

- CH 只读经 `DatabaseService().get_clickhouse_conn()`；DDL 快照=`.runtime/tmp/env1_rollback_ddl.sql`（10/10 捕获，执行时应转存 staging）。
- 逐件证据机器生成：`verdict_files.csv`（129 行=125 可删+2 保留+1 范围外+1 排除）、`verdict_tables.csv`（10 行全可删）。
- 新建文件 CREATE-GUARD/registry 登记义务留作战役收口统一办理（本代理红线禁写注册表）。
