---
ttl: task_bound
title: ADJ 案卷·t0 甲位三版本分叉（auto_mount.py 写回准否）
---

# ADJ · t0 甲位三版本分叉

> 车道=LANE-ADJ（裁定材料汇编，不出裁定）。所有字节/行数/闸态均为本班 2026-09-25 21:10-21:50 亲测，标注"实测"处可复算。

## ① 一句话问的是什么

`scripts/backtest/auto_mount.py` 盘上存在三个字节版本，0033 终批（含六段相位全史）卡在"写回哪一版"这一句话上——问的是：**允许把 worktree 那版（含 D-3 双写去重治本）写回主区/落 HEAD 吗**。

## ② 现状实测

### 2.1 三分叉实物（实测 sha256 前 12 + 字节）

| 版本 | 路径 | 盘上字节 | LF 归一后字节 | 归一 sha | 行数 | ruff format | ruff check |
|---|---|---|---|---|---|---|---|
| V1 主区=HEAD | `scripts/backtest/auto_mount.py`（git status clean，实测） | 61,143 | 61,143（本就 LF） | `7316d34b0bd7` | 1,046 | **FAIL** | **FAIL** |
| V2 worktree | `.worktrees/st-t0-matrix-20260924/scripts/backtest/auto_mount.py` | 64,573（CRLF×1,199） | **63,374** | `e4dc2de62355` | 1,200 | **PASS** | **PASS** |
| V3 0033 在册 blob | `.runtime/commit_queue/blobs/f436d2b981b4…`（bag `files[].blob_sha256` 自校通过，实测） | 64,581（CRLF×1,200） | 63,381 | `07cb0777c8e7` | 1,201 | **FAIL** | PASS |

补充实测：`.runtime/tmp/st_t0_monitor/fixed/auto_mount.py` 与 V2 **逐字节相同**（`a021f3765e58`）。ruff 判定统一用根 `pyproject.toml [tool.ruff]`（line-length=120）跑，命令：`ruff format --check --config pyproject.toml <path>` / `ruff check --config pyproject.toml <path>`。

### 2.2 "63,374B 版本盘面不存在"这句话被实测证伪（关键）

- 台账 Round 45 记：三版本 = 主区 61,143B / worktree 64,573B / 0033 袋 64,581B，"甲位所述 63374B 恰差 7B 版本盘面不存在"（`docs/_working/cmd_ledger/overnight_decisions_20260924.md:170`，引自此文未复测其结论）。
- 本班实测：**63,374B 正是 V2 的 LF 归一尺寸**，且其归一 sha `e4dc2de62355` 与 t0 班 LEDGER D-51 自报"治本件 sha"**逐字吻合**（`docs/_working/t0_matrix/LEDGER.md:714`，引自该文）。
- 7B 差 = V3→V2 之间那条长字符串的折行（V3 归一 63,381 − V2 归一 63,374 = 7，实测）。
- 结论：**Round 45 拿"归一口径的 63,374"去对"盘上原始口径的 61,143/64,573/64,581"，是量具口径错配，不是版本失踪**。治本件在盘（=V2 本体）。

### 2.3 V1→V2 到底差什么（实测 diff，非格式部分三条）

`diff` V1/V2 归一文本共 3 类改动，前一类纯格式，后两类是真语义：

1. 纯 ruff format 重排（多行字典/括号折行、`"pd.DataFrame"` 去引号 UP037）——零语义。
2. `auto_mount.py:195` 裸 SQL 提为模块级常量 `_SQL_SNAPSHOT_DOMINANT`（V1 无此常量，实测 `git show HEAD:… | grep -c _SQL_SNAPSHOT_DOMINANT` = 0）——治 0020 袋死因 NO-BARE-SQL。
3. `auto_mount.py:284` 签名由 `load_phase_panel(end=None)` 扩为 `load_phase_panel(end=None, start=IS_WIN_START)`，并新增 **快照表同日双写去重 + dominant 分歧 fail-closed**（V1 `has_duplicates` 出现次数=0，V2=1，实测）。V2 注释自陈缺陷"当下就在发生"：2020+ 的 1,631 个 trade_date 中 1,624 个有 2 行（引自 V2 注释，本班未复测该 1,624/1,631）。

### 2.4 0033 批为什么被挡（实测死因，与文档记载不同）

- 袋：`.runtime/commit_queue/dead/q-20260924-st-t0-matrix-20260924-0033.json`，created 2026-09-24T10:11:08+08:00，**files=35 件（全部 action=modify）**，dead_at 未见同文件字段=见 dead_reason。
- **真死因（实测 dead_reason 原文）**：`门禁 CAPABILITY-OVERLAP 阻断: CloneGuard 检测到 extract 级代码克隆`——`scripts/audit/t0_gpu_condition_pack.py:_reg` 与 `scripts/governance/meta_question/build_closure_ledger.py:68 _connect` 相似度 100%（structural）、与 `…/wo008/generate_product_synonym_register.py:189 _pg` 相似度 100%。**不是 ruff-format**。
- 克隆是**存量对、非本批引入**（实测）：HEAD 版 `t0_gpu_condition_pack.py:97 _reg` 与袋内版**逐字节相同**（HEAD 该件 1,017 行，袋内 1,108 行，差异 105 行在别处）；HEAD 里 `_reg()` 早已随 96870e1fd3 落库。即"文件随批修改而暴露既有同构对"——正是 `echo-guard.yml` 已 acknowledged 82 对里的既有先例形态（实测 acknowledged 段 82 条，其中 0 条覆盖 t0_gpu_condition_pack）。
- **甲位不是形式问题，是硬依赖**（实测）：袋内 `scripts/audit/t0_six_phase_materialize.py:46 import auto_mount as am`、`:56 panel = am.load_phase_panel(start=start)`；而 HEAD 版签名无 `start` 形参 → 对 HEAD 直跑必 TypeError。六段全史就是它产的。

### 2.5 0033 批内容物实测（文档"20 件"计数漂移）

- 19 号文 B6 行写"0033 批 20 件"（引自该文，未复测）。实测袋内 **35 件**：docs/_working/t0_matrix/** 24 件、scripts/audit/ 6 件、scripts/backtest/auto_mount.py 1 件、tests/audit/ 4 件。
- 落地进度实测：35 件中 **2 件在册字节与 HEAD 已逐位相同**（幂等），**12 件 HEAD 已有但字节不同**（真增量），**21 件 HEAD 查无此路径**（新件）。
- 六段全史本体实测（从袋内 blob 直读）：`six_phase_history_v1.csv` 92,451B / 1,817 行 / **1,816 数据行**，列 `trade_date,dominant,six_phase,routed,leg_macro,leg_euphoria,leg_distribution,preempt,closed_book_ok,phase_version`，首 2019-04-01 末 2026-09-21；配套 meta 自述 `rows: 1816 / rows_routed: 1054`。与文档 09 号文所述 1,816/1,054 一致（本次为实测）。
- 主区盘上 `docs/_working/t0_matrix/six_phase_history_v1.csv` **不存在**（实测），HEAD 亦无（实测）→ 全史目前只活在队列 blob 里。
- 真源方向风险：该 CSV 的 meta `truth_source.mapping` 明文指向 `scripts/backtest/auto_mount.py（R2SIX + phase_overlay + resolve_six_phase）`——**产物真源就是甲位争的那个文件**。

## ③ 可选路径

**路径 A：甲位=放行 V2 写回（V3 弃用，重投按 V2 字节重捕）**
- 动作：V2 覆盖主区 → 35 件按当前盘重捕新袋 → 另步在 `echo-guard.yml` acknowledged 段登记 2 对（`_reg↔_connect`、`_reg↔_pg`）→ 重投。
- 代价：一次全量重捕（禁 `--from-bag`，会用旧快照）；`echo-guard.yml` 是热文件，须 `safe_write_text` CAS。
- 不可逆点：V2 的去重+fail-closed 一改，**六段面板的日/行计数口径即刻变化**；已按旧口径产出的任何下游（P1 条件表/相位统计）与全史之间出现口径断层，须重算才能对齐（C2 栏"历史重算"项即为此设）。

**路径 B：甲位=放行 V3 写回（在册字节原样落）**
- 代价：V3 对 `ruff format --check` FAIL（实测）→ 同批必须带格式修复，落回 V2；且 V3 归一尺寸 63,381 与文档钉死口径差 7B，等于重新制造一次分叉。
- 不可逆点：无（但走不通）。

**路径 C：甲位=不写回，改物化件适配 HEAD 签名**
- 动作：`t0_six_phase_materialize.py` 改为不调 `start=`（或在 HEAD 版只加 `start` 形参不加去重）。
- 代价：**明知 D-3 双写缺陷在 HEAD 存续**，全史与下游面板的行/日计数继续翻倍虚高（V2 注释口径）；等于把治本债再挂一期，且后续每批都要重演同一次分叉确认。
- 不可逆点：期间产出的所有按日聚合结果（30 日样本地板、判窗）都是脏数，事后要作废重算——**这是三条里唯一会让研究段数据整体报废的选项**。

## ④ 专业对照（外部论据，URL+发布方+年份）

1. **派生产物必须与其生成代码同版可追**：FDA 21 CFR Part 11 与 EMA Annex 11 对"记录派生（derived record）"要求生成逻辑与数据同期受版本控制、可重审；Good Automated Manufacturing Practice（ISPE GAMP 5, 2008, 2nd ed. 2022 复审）把"重新生成能力"列为验证证据要件。→ 落 1,816 行全史而不落产它的 `auto_mount.py` 版本 = 违反派生数据可重生成原则。
   - https://www.ispe.org/publications/guides/gamp-5 （ISPE，2008/2022）
   - https://www.ema.europa.eu/en/documents/scientific-guideline/guideline-computerised-systems-annex-11-rev1_en.pdf （EMA，2011）
2. **数据版本化/可重现实务**：DAG（data version control）在量化与科学计算侧的标准动机即"代码与数据快照同版本绑定，否则结果不可复现"；相关开源先例：lakeFS（Treeverse，2020-，Apache-2.0/MIT 双件）、DVC（Iterative，2017-，Apache-2.0）、Pachyderm（2014-，Apache-2.0）。
   - https://docs.lakefs.io/understand/why.html （LakeFS 官方文档，2024）
   - https://dvc.org/doc/user-guide/experiment-management/reproducing-experiments （DVC 官方文档，2024）
   - 检索日期 2026-09-25；两源独立（一份是虚拟文件系统厂商文档，一份是开源工具官方文档）。

（本项专业对照的落点是"版本绑定"这一条纪律，非阈值或方法论主张。）

## ⑤ 风险（做错的最坏情形）

- **资金安全：零直接暴露**。实测编排/执行面无一消费该 CSV 做下单；`GRADUATED_PACKAGES: Final[frozenset[str]] = frozenset()`（`src/zephyr/strategy_pipeline/daily_decision_orchestrator.py:121`，实测）→ 结构性不产实盘单（裁定#305 安全态）。风险全在**研究可信度面**。
- 选 C 的最坏情形：六段相位下游（P1 条件概率表、做T相位匹配矩阵、上岗规则原料）系统性建立在双写虚高的日计数上，**30 日样本地板被虚假满足**→ 不合格策略被判合格进入候选池 → 若未来某天毕业集非空，等于用脏样本骗过毕业门。这是本项唯一带资金尾部风险的形态。
- 选 A 的最坏情形：口径断层期（旧脏数结论与新全史并存）若未标注即引用，出现同指标两值互相打脸；文档纪律上 17 号文有"占位口径结论标注+重算"槽（引自 19 号文 C2，未复测）。
- 流程风险：绕 CloneGuard 用 `ZEPHYR_PROTECTED_PATHS_BYPASS`/noqa 类硬闯=把"存量同构对"洗成"本批新克隆"，下次同类批必再死。

## ⑥ 解锁依赖（还缺什么）

1. `echo-guard.yml` acknowledged 新增 2 对（`t0_gpu_condition_pack.py:_reg` ↔ `build_closure_ledger.py:_connect`、↔ `wo008/generate_product_synonym_register.py:_pg`），须带理由+会话号，且该册是热文件走 CAS。**登记前，任何版本都过不了 PROTECTED 之外的这道闸**。
2. 重捕工具与 35 件当前盘字节的一致性核验（0033 的在册 blob 对 V3，不是 V2；重投须重捕，不能 `--from-bag`）。
3. 重算清单：哪些下游已按未去重口径出过结论（P1 表 v1 469 板块版 / 做T相位矩阵 / 六段锚定表）——**本班未盘，缺一份消费面点名表**。
4. `tests/audit/test_t0_six_phase_materialize.py`（袋内新件，21 件 HEAD 查无者之一）落地后才能真正跑通去重回归。

## ⑦ 一句话推荐（推荐待总筹拍）

推荐 **A（放行 V2 写回）**，但**批准即附两条硬前置**：随批登记 `echo-guard.yml` 两条 acknowledged（否则仍死），并同步开"脏口径下游点名+重算"工作项（否则 A 只解字节分叉、不解结论分叉）——理由：C 会让研究段数据整体报废，B 走不通，A 的代价只是标注工作。
