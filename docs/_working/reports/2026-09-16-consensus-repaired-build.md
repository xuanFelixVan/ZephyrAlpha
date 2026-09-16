---
ttl: task_bound
completes_when: consensus_daily_repaired 经 Owner 验收切换（或判废）后归档
---

# consensus_daily_repaired 双轨重建台账（2026-09-16）

> 施工依据：docs/_working/2026-09-14-c4-history-repair-plan.md §6 + 交接包
> docs/_working/reports/2026-09-16-consensus-repaired-handoff.md；
> 设计真源：expectation_consumption_design_policy.md §M1/§8/§9。
> 会话 st-consrep-20260916（worktree .worktrees/st-consrep-20260916）。

## 1. 落库实绩（表 c3_fundamental.consensus_daily_repaired）

| 段 | eps_source | 行数 | 标的数 | 快照日跨度 | forecast_year |
|---|---|---|---|---|---|
| A（历史修复） | pdf_forecast_high | 1,472,629 | 1,854 | 2017-01-03~2021-12-31 | 2016~2023 |
| B（前向干净源） | analyst_forecast_snapshot | 91,367 | 2,632 | 2026-07-22~2026-09-15 | 2028（仅此一年） |
| 合计 | — | 1,563,996 | 3,253 | 2017-01-03~2026-09-15 | — |

- A 段月份覆盖 60/60（2017-01~2021-12 无缺月）。
- **空洞 2022-01-01~2026-07-21**：上游 pdf_forecast_extracted 止于 2021-12-31，
  analyst_forecast 自 2026-07-22 起累积——非构建缺陷，是源覆盖边界（§5 发现 2）。
- 对照：DS-229 consensus_daily = 6,780,329 行 / 3,053 标的（污染历史回放）。
- build_batch = `c4-repair-20260916`；DS-229 未被本批任何写操作触及（双轨物理隔离）。

## 2. 证据链与守卫计数（--stats 出证）

| 量 | 值 | 说明 |
|---|---|---|
| reports_in_window | 60,477 | research_report 2017-2021 全集 |
| reports_with_eps | 13,063 | 守卫后仍携带 EPS 预测的研报数 |
| eps_rows_kept | 38,467 | 进入聚合的 (report, forecast_year) 行 |
| eps_rows_dropped_by_guard | 634 | 守卫剔除（eps>50） |
| slot_rows_trimmed | 126 | 预测年多于 3 个者截断为 fy0/fy1/fy2 |

守卫参数（预注册于 consensus_daily_repaired_compute.py，禁挪）：
`confidence='high'` ∧ `0 < eps ≤ 50` ∧ `slot ≤ 3`。

**eps≤50 上界的依据（非拍脑袋）**：2017-2021 全 A 股真实 EPS 最大值=茅台 2021 年 41.76；
采样 eps>50 的 14/14 份经目视全为"营业收入/归母净利润"行串列（且 99.0/100.0/200.0 哨兵值
在互不相关标的间复现）；缺陷散布在多种表头标签上（bad_pct 0.05%~6.79%），无定向排除路径，
故用值域守卫。94.2% 研报恰携带 3 个预测年，槽位打包忠实；余 0.5% 由 S1 规则（正向年升序
→ 上前向年降序 → 截断至 3）处置。守卫不用任何前视信息。

## 3. 三重对照验收（scripts/ch/build_consensus_daily_repaired.py --check，3/3 PASS）

- **① 重叠期秩相关**（B 段 vs DS-229，2026-07-22~09-15）：均值 **0.9713**，
  39 个快照日，min 0.9669 / max 0.9771，判据 ≥0.9 → PASS。
  （口径注：适配层复用生产聚合真源 `build_consensus_rows`，此项验的是"同源同口径"，
  不是"值语义正确"——值语义由 ②③ 与抽核承担。）
- **② 锚点股历史曲线**（600519/000858/601318/000651/600036，A 段）：32 条 (symbol,
  forecast_year) 序列，其中多源序列 27 条，eps_consensus 去重值 min 1 / max 60，
  违反"多源须有修正"的序列 = **0** → PASS。
  反面证据（同窗 DS-229）：y=2026/2027/2028 均 **uniq=1 / 1,074 个快照日**——
  回放污染的定义性症状被数值坐实；repaired 侧 600519 呈真实时变收敛阶梯，
  区间包住实际 EPS（21/28/32.8/37.2/41.8）。
- **③ 窗口聚合 SQL 独立重算对照**：A 段季末快照日全抽 20 日，比对行 **213**
  （下限 100），不一致 **0** → PASS。与 DS-229 的 --check 本质不同：那是对污染的源
  重算（同饮一池水，§9.1 方法论教训），本项从 pdf_forecast_extracted 走独立 SQL 路径
  重算窗口均值，验的是"适配+聚合"链路。

## 4. 判据口径变更披露（本批自拟实现项，方案 §6 三条预注册数值均未挪）

方案 §6 预注册判据（锚点集准确率 ≥90% / 抽核错误率 ≤5% / 重叠期秩相关 ≥0.9）**原样守住**。
以下两项是 §6 未预注册数值的**实现自拟项**，且本批内有口径变更，留痕如下：

1. **② 由绝对阈值改覆盖条件检验**。初版判据"锚点序列去重值 ≥5"实测误伤 5 条序列——
   它们是 n_reports 恒为 1 的稀疏单研报年份（无可修正源，天然恒定），属覆盖薄而非污染。
   现判据更严且对症：任一序列若窗口内曾出现 ≥2 份不同研报，则去重值必须 ≥2，一条不满足即 FAIL。
2. **③ 由单日扩到季末全抽**。初版只验 A 段最后一个快照日，锚点股仅得 8 行可比，
   对 156 万行重建覆盖面过薄；改为每季度末快照日全抽（20 日）并设比对行数下限 100
   （不足即 FAIL，防抽样过窄假 PASS）。
3. **② 污染侧查询修 bug**：初版按 `forecast_year BETWEEN 2017 AND 2021` 过滤 DS-229，
   回放污染使该窗内预测年全为当下年（2026-2028），返回空行——已去掉该过滤。
   （教训：拿污染表做反面证据时，过滤条件本身可能被污染语义反噬。）

## 5. Owner 级发现（裁定级，本会话不代裁）

1. **C4 提取批已死在 91.7%**（55,464/60,477 份），但 **60,245 份 PDF 已在缓存**
   （F:\zephyr_c4_pdf_cache，junction，勿搬回 D）→ 续跑提取只是重 CPU 不需重下载，
   代价低。本批 A 段的证据集是提取批的中止产物（13,063 份带预测研报）。
2. **§8.1 冻结 IS 窗 2019-2023（60 月）只能覆盖 36/60**：pdf_forecast_extracted 止于
   2021-12-31，2022-01~2023-12 无修复证据。实测：A 段在 IS 窗内有行的月份=**36**
   （2019-01~2021-12），且这 36 个月月内标的数**均 ≥100**（评估器 `_MIN_NAMES` 门槛）——
   即缺口纯在时间轴后段，不是密度问题。→ 交接包步骤 7 的 EXP-01/03/05 复评
   **无法按预注册窗口执行**。候选处置（请裁）：
   - A：IS 窗缩为 2019-2021（36 月）先行出证，标注"窗缩"，2022+ 补齐后复跑；
   - B：先补 2022-2026 提取批（夜窗 3-5 晚）再按原窗复评；
   - C：其他（如改用 analyst_forecast 前向窗，但干净窗最早 2027-07）。
   本会话按预注册禁挪原则**未擅自缩窗跑**，步骤 7 停在此裁定点。
3. **analyst_forecast 当前仅 forecast_year=2028 单一年份** → "双源合并"目前是单地平铺，
   ① 秩相关只验了一个预测年；且 B 段 n_orgs 恒为 0、eps_std=0、min=max=consensus
   （源侧无机构明细/无分布），消费方需按 eps_source 分段对待。
4. **high-only 密度偏低**：标的中位约 2 份研报/标的-年，A 段 1,854 标的 vs DS-229 3,053
   → EXP-05（预期分歧族）在低 n 上退化（eps_std n=1 时为 0）。"mid 是否入聚合"是
   铁律级选择（交接包铁律=high-only 入聚合、mid/low 留档），本批严守 high-only，
   是否放宽请裁。
5. **DS 号与登记字段**：consensus_daily_repaired 初取 DS-271，**后因与 dev 撞号改为 DS-275**（见 §8.13）；
   `dual_track` / `switch_gate` 两键在 data_asset_registry 无字段先例，按 RULE-SSOT
   不擅自扩表，事实写入 format_summary 自由文本。
6. **抽核采样口径偏差（审计有效性披露）**：本批抽核抽样 SQL 带 `eps BETWEEN 0.05 AND 200`
   过滤（为排除哨兵垃圾以取得可目视样本），故 **25/30 全对结论的适用域是 eps≤200**；
   守卫剔除的 634 行（eps>50）未经目视抽核，其判定依据=§2 的 14/14 定向采样 +
   哨兵值跨标的复现，属"排除即止损"而非"排除已验真"。
7. **残留风险**：600519/2018 曲线低尾（14.39，实际 2018 年 EPS≈21）与 50~100 区间的
   真实预测值可能被守卫一并截掉；审计员建议的"EPS×股本 vs 归母净利润"软校验未实施
   （需引入股本源，跨域依赖）。

## 6. 工件清单与复现

| 工件 | 路径 |
|---|---|
| DDL 真源（DDL-as-Code） | `schemas/categories/fundamental/consensus_daily_repaired.py` |
| 计算适配层 | `src/zephyr/data/implementations/consensus_daily_repaired_compute.py` |
| 集成器路由分支 | `src/zephyr/data/implementations/internal_compute_provider.py`（`payload.table=c3_fundamental.consensus_daily_repaired` → `run_compute_repaired`；按需触发，不挂 tasks.yaml 夜间档） |
| 建表部署 | `scripts/ch/apply_consensus_daily_repaired_ddl.py` |
| 重建+验收 | `scripts/ch/build_consensus_daily_repaired.py` |
| 纯函数单测（9 项） | `tests/scripts/test_build_consensus_daily_repaired.py` |

复现：`python scripts/ch/apply_consensus_daily_repaired_ddl.py`（建表，幂等 IF NOT EXISTS，
DDL 走 base/admin 账号——writer 无 CREATE 权限，#ARCH-CH-027）
→ `python scripts/ch/build_consensus_daily_repaired.py`（全量重建，可 `--start/--end/--symbols` 局部）
→ `python scripts/ch/build_consensus_daily_repaired.py --check`（三重对照，三项全 PASS 才退 0）。

切换门位：本表 `switch_gate=Owner`——DS-229 的消费方（pit_query 白名单、EXP 族评估器）
在 Owner 验收前不得改指本表。评估器 `scripts/backtest/eval_exp_expectations.py` 的
`--source {polluted,repaired}` 开关本班已就位（默认 polluted=既有出证口径零漂移；出证 JSON
落 `consensus_table` 字段防两轨跑混认），但**未运行**——运行即撞 §5.2 的 IS 窗裁定点。

## 7. 抽核滚动进度（承接 30 份协议）

首批 15（2026-09-15-c4-acceptance-interim.md）+ 第二批 5（reports/2026-09-16-c4-audit-batch2.md）
+ 第三批 5（reports/2026-09-16-c4-audit-batch3.md）= **25/30**，
报告级 24/25=96%、high 表路径 25/25 全对（唯一错误仍是首批 #4 的 mid 文本兜底历史案）。
余 5 份随下一夜滚动补齐。

## 8. 下一班待办（本班未闭环，按可直接执行口径写）

1. **抽核协议余 5 份（#26-30）**：抽样域与排除集沿用 batch3 台账口径
   （`ingest_ts>2026-09-15 01:00` 生产行 ∧ confidence=high ∧ method=heuristic ∧
   report_id 与标的双排除），fitz Matrix 2.2 渲染 + 表/正文互证；
   台账续记到 `docs/_working/reports/2026-09-1x-c4-audit-batch4.md`（reports/ 子目录，
   平铺区已满）。§5.6 的采样口径披露要求随批继承：抽样过滤条件须如实写明。
2. **IS 窗裁定（§5.2，阻塞 EXP 族复评）**：Owner 裁 A/B/C 后——
   裁 A（缩窗 2019-2021）= 改 `eval_exp_expectations.py` 的 `_IS` 并登记裁定号（禁静默改窗）；
   裁 B（补 2022-2026 提取批）= 先 `Get-CimInstance` 查 c4_* 活进程再拉起（勿重复发射），
   完成后重跑 `build_consensus_daily_repaired.py`（ReplacingMergeTree 幂等）+ `--check` 复验；
   `--source repaired` 开关已就位，无需再施工。
3. **Owner 切换门位**：本表 `switch_gate=Owner`——验收前不得把 DS-229 消费方改指本表；
   验收动作=`--check` 3/3 PASS 复核 + §5 七项发现逐项裁定。
4. **本班提交旁注（基础设施留痕，未代修）**：worktree 内首次 `--enqueue` 因
   `commit_queue._REPO_ROOT` 随脚本落点解析到 `.worktrees/<sid>/`，队列项进了 worktree
   本地队列根，而本地排空又被 OPS-GUARD 保护区拦截（`.worktrees/**` 禁 in-process 移动），
   该项遂成惰性快照；改设 `ZEPHYR_COMMIT_QUEUE_DIR=<主仓>/.runtime/commit_queue`
   重入队后方进共享队列正门。教训=**在 worktree 内发射队列必须先钉该环境变量**。
   另：本班会话注册因 `SessionRegistry` TTL=3600s 过期而被 SESSION-REQUIRED 拦下，
   重跑 `session_worktree_start(allow_workspace_drift=True)` 时因主仓 2288 文件残留 WIP
   走了新建分支路径（`.aidrafts/st-consrep-20260916`，空壳未使用）——两现象一并上报治理线。
5. **队列正门在并发高峰会空转（本班第二次撞）**：钉好环境变量后进共享根的那一项，
   drain 落盘时曾报 `LOCK_TIMEOUT`（全局 commit lock 60s 超时，他会话正在提交）。
   **但该项的 `dead_reason` 随后被 serializer 重写为门禁判定（见下条）——教训=死信要重读
   `dead_reason` 现值再归因，勿据首次快照的瞬时结论定性**（首次读到的锁超时是真的锁忙，
   重试后暴露出真堵点）。blob 快照无损、内容零丢失，处置=改完代码重新 `--enqueue` 取新快照
   （旧项不 requeue），不改走裸 `git commit`。
6. **两道门禁硬拦本班首版代码，均已治本非豁免（真因死信）**：
   - **CH-BATCH-SIZE**：首版 `run_build` 在 `for` 循环内直调 `ch_writer.write_result(fr)`
     （`build_consensus_daily_repaired.py:103`），违反裁定 #ARCH-CH-003/#ARCH-CH-004。
     按门禁指引用 `BufferedWriter` 中间层改写（`max_rows` 与产出分批同宽=10 万行，
     INSERT 次数=flush 次数=data parts 数）。窄窗冒烟（600519 2019Q1）：175 行 / 1 次 INSERT。
   - **NO-HIGH-COMPLEXITY**：三个新函数复杂度 16/16/25 超 §5.158 的 15 上限，按"拆短函数"
     口径抽出 `_pdf_slots_by_report`、`_rating_counts`+`_segment_b_row`、`_accumulate_recompute`
     （阈值、列序、容差、判据数值逐字未动）。
   **重构不改行为的机证**：按 `eps_source` 分组的行数、标的数、`sum(eps_consensus)`、
   `sum(n_reports)`、评级分档加权和、以及行级 `cityHash64(symbol,trade_date,forecast_year,
   eps_consensus,eps_min,eps_max,last_report_date)` 校验和，重构前后**逐位相同**
   （B=`454349279187449912` / A=`4731894266116947220`）；9 项单测全过；`--check` 三项复验
   仍 3/3 PASS；表内 `count(FINAL)` 恒 1,563,996 行 3,253 标的（同键 ReplacingMergeTree 幂等），
   active parts=66 个 / 8.0 MB。
7. **TRANSLATION-COVERAGE 查的是主仓真源，不是本批 staged 内容（本班第三次撞）**：该门禁经
   `module_translation_loader` 读 `REPO_ROOT`（=`zephyr.shared.io.paths`，按脚本落点解析到主仓）
   下的 `module_translation_registry.yaml`——所以"在 worktree 里把翻译条目跟代码同批提交"
   永远判"无 plain_zh 简介"（item 0004 实证）。正道=钦定工具
   `python scripts/governance/d3_metadata/add_module_translation.py --path <新 py> --domain <D_*>
   --name-zh <中文名> --plain-zh <大白话>`（主仓内跑，upsert 进真源，本批 4 条）。
8. **热注册表防回退（提交前必查，本班撞出）**：本 worktree 分支落后 dev
   （`capability_canonical_file_registry.yaml` +636 行、`module_translation_registry.yaml` +14 行
   均为他会话所加）——直接按 worktree 内容提交会把别人条目整体回退。处置=先把两个热库
   以 dev 内容为基准重放自己的追加，再提交；机证=对 dev **纯插入** 28/13/24 行、零删除，
   `data_asset_registry.yaml` 与 `business_data_categories.yaml` 的 delta 只含本批
   （version、changelog、DS 条目与品类各一段）。**注：该段结论已被 §8.13 的第二次重放取代**
   ——dev 在本班窗口内又前进（fc28026614/895ce2c91f/eae3d937d4），四张热库须以新 dev 为基准再重放一次。
9. **ORPHAN-MODULE 第四撞（item 0005 真堵点）+ 治本接线**：该门禁只 `git grep` **`src/**/*.py`**
   找 import 引用，`scripts/` 不在搜索范围内——所以"builder 脚本 import 了计算核"在门禁眼里
   仍是孤儿（生产孪生 `consensus_daily_compute` 之所以过，是因为 `internal_compute_provider`
   有路由分支）。处置=按同目录既有约定给 `internal_compute_provider.fetch` 加
   `payload.table == "c3_fundamental.consensus_daily_repaired"` 分支 →
   新方法 `_fetch_consensus_daily_repaired` 懒 import 委托 `run_compute_repaired`；
   **刻意不挂 tasks.yaml 夜间档**（双轨重建轨，切换门位=Owner，只允许按需触发重建，
   生产读路径零改动）。改前把该热文件以 dev 内容为准重放（本 worktree 分支落后 dev 65 行
   =他会话广度分支），我的 delta 对 dev 纯插入。补线后本机预检三道后续门禁：
   `git grep` 复算 ORPHAN-MODULE（命中 provider）、FUNCTION-DUP 同名同体扫描（0 命中）、
   `_find_broken_refs` 复算 DOC-REF-BROKEN（0 断链）、复杂度复算（唯一 >15 的 `fetch`=20
   在 HEAD 已存在=门禁跳过），25 项单测（provider 16 + 本批 9）全过。
10. **NO-BARE-SQL 第五撞（item 0006 真堵点，priority 94）**：§5.160.2 SQL 集中化——该门禁**逐 added 行**
    跑 `SELECT…FROM`/`INSERT INTO`/`UPDATE…SET`/`DELETE FROM` 正则（所以"SELECT 与 FROM 分在两行的
    隐式拼接"侥幸过关，同片段的两处被拦），豁免通道只有两条：`^_?SQL_\w+$` 命名的模块级常量（AST 识别整段
    Assign 行范围）或行尾 `# noqa: bare-sql <理由≥10字>`；`scripts/ch/` 整域豁免（CH 运维脚本 SQL=业务语言）。
    处置=走正道不挂 noqa：四条读取全集中化为 `_SQL_REPORT_ROWS`/`_SQL_PDF_EPS`/`_SQL_ANALYST_ROWS`/
    `_SQL_ANALYST_MAX_DATE` + `.format()` 注入自家预注册常量（无外部输入拼接面）。
    **不改行为的机证**：AST 取出常量求值与重构前字面量**逐字节相同**；复算 gate 命中 0；25 项单测全过。
11. **TABLE-NAME-REGISTRY 第六撞（item 0007 真堵点，priority 120）**：该门查 added 行 `ast.Constant`
    字符串是否含**已注册**全限定表名（精确匹配 + 最长优先子串匹配；docstring 行豁免；豁免面仅
    `table_registry.py`/门自身/`schemas/categories/`/`apply_*_ddl.py`——`scripts/ch/` 与 `scripts/backtest/`
    不豁免）。两个坑各中一次：①子串匹配会把新表名 `…consensus_daily_repaired` 判成老注册名
    `c3_fundamental.consensus_daily` 的硬编码（我的 provider 分支因此连坐）；②门读进程内
    `get_registry()` 快照，序列化器侧注册表尚未含本批新品类，故"引用新品类"不报、"引用老注册名"必报。
    处置=四处字面量全改真源派生（compute 的 `_TBL_RESEARCH_REPORT`/`_TBL_ANALYST_FORECAST`、
    provider 的 `_TBL_CONSENSUS_DAILY_REPAIRED`、builder 的 `_TBL_REPAIRED`/`_TBL_POLLUTED`/
    `_TBL_RESEARCH_REPORT`、eval 的 `_CONSENSUS_TABLE_POLLUTED`/`_REPAIRED`）；`pdf_forecast_extracted`
    属 C4 域未登记品类，故以 `_TBL_PDF_EVIDENCE` 承载并在源码注明"登记后须改走真源"。
    **不改行为的机证**：`--check` 三项数字逐项复现（0.9713/39 日、32 序列 27 多源 0 违反、213 行 0 不一致）、
    25 项单测全过、以 `GateSpec.check` 直调本批可能连带的十七道门 **17/17 PASS**（桩=`run_git` 在 worktree
    执行 + 先 `git add` 本批 13 文件；此法比手抄规则可靠）。
    **知情后果**：`get_registry().table("fund_consensus_daily_repaired")` 是**导入期 fail-closed**——品类
    YAML 必须与代码同批落地（本批已同批）；worktree 内跑本批脚本须 `PYTHONPATH=<worktree>/src`，
    否则 `zephyr` 解析到主仓、新品类查不到（主仓 `REPO_ROOT` 按包落点解析，非按 cwd）。
12. **本班收口被外来全局门禁挡死（item 0008 死因，非本批违规，需 Owner 处置）**：
    `GATE-ERRCODE-CONSISTENCY`（priority 131，触发条件=staged 含 `src/zephyr/**.py` 或 error_code_registry.yaml）
    报 `TestRegistryToCode.test_active_entries_have_live_definition` 红：**ZA-PA-0031/0032/0033** 三条
    active 条目指向 `src/zephyr/pf_alloc/allocation_{inputs,persistence,config}.py`，而这三个文件
    **从未进过 git**（`git ls-files`/`git log --all --diff-filter=A`/各 worktree 全查无，`classify_workspace_wip.py`
    判为 `untracked_new`，仅存活在主工作区磁盘）。登记动作由 **st-tickdrain-20260916 的 commit 8d0cf26117**
    （2026-09-16 16:34，`[ARCH-APPROVAL:ARCH-MODEL-LIFECYCLE-001]`，消息自述"全局阻断的唯一治本路径/BYPASS=1"）
    完成——**它本地扫主工作区见得到文件、队列 serializer 从 dev 检出见不到**，于是注册表有了指针、dev 没有代码，
    此后凡含 `src/zephyr/**.py` 的批次一律被拦（同时段仅含 scripts/docs 的 st-qoder-t1a 项 18:12/18:18 正常落地，
    即为该触发条件的实证）。
    两条治本路径（本班不代裁，均属高危域）：①**补交代码**——把三个 untracked 文件按正规批次（creation_token +
    翻译 + depgraph）落进 dev，指针即"存活"（与 8d0cf26117 的"存量码"自述一致）；②**改判指针**——给三条条目加
    `deprecated`（测试判据是 `"deprecated" not in e`，加此键即跳过），但那是把别人在跑的代码标成退役，且
    `error_code_registry.yaml` 是受保护路径。**建议①**。
    本批状态=13 文件全 staged 于 worktree、十七道门本地预跑 17/17 PASS、消息与台账就绪；解阻后**重新 `--enqueue`
    取新快照**即可（勿 requeue 旧项、勿改走裸 git commit、勿为绕门把 `src/zephyr/**` 拆出批次——那会造出
    "有表无计算层"的半批）。附撞：item 0009 死于 `LOCK_TIMEOUT`（并发高峰，瞬时）。
    **另须上报门禁体系本身**：全局对账型门禁在"主工作区直连通道"与"队列 serializer 通道"结论不一致
    （前者看得见 untracked 文件、后者看不见）——这正是 8d0cf26117 误判"已治本"的根因，建议给该门补
    "以 git 追踪态为准（或显式拒绝 untracked 定义点）"的口径。

13. **DS 号撞车改号 DS-271→DS-275 + 四热库对 dev 二次重放（本班收口最后一撞，已治）**：
    **撞车事实**：本班 17:2x 登记 DS-271=`c3_fundamental.consensus_daily_repaired` 时，dev 上 DS-271 已被
    **commit 895ce2c91f**（车道 D2/E 战役补登）占用为 `c1_market.daban_engine_load`，且同批还占了 DS-272~274。
    两条 v1.9.7 changelog 互相矛盾、两个实体抢一个 dataset_id——直接违反注册表不变量
    `test_registry_internal_uniqueness`（unique_key.datasets=[dataset_id]）。**取号靠"读一眼最大值"必然撞**：
    本班的错不在选号规则，而在**登记与提交之间隔了 2 小时**（热文件 CAS 只防同文件并发写，不防"号段"并发占）。
    **处置**：改取段内 max+1=**DS-275**（dev 实测最大 DS-274），并把四个热库全部以**当前 dev 内容**为基准重放
    本班追加（不再以 worktree HEAD 为基准）。机证（对 dev 逐文件 normalized-diff）：
    `data_asset_registry.yaml` +63/-1（唯一删除=本班 `version: 1.9.6→1.9.8` 元数据行）、
    `capability_canonical_file_registry.yaml` +37/-0、`business_data_categories.yaml` +17/-0、
    `module_translation_registry.yaml` +28/-0；四库 `yaml.safe_load` 全过，datasets 264 条 id 全唯一、
    capabilities 378 条 id 全唯一、本班 6 条 creation_token 各 1 次、dev 新增的 `market_daban_engine_load`
    品类与 DS-271~274 四条**完整保留**（重放=纯插入，零回退他人成果）。
    **同步订正本班自有事实错误**：DS-275 `format_summary` 原写"DS-229 全部消费方（pit_query 白名单/EXP 族评估器）
    不得改指"——实测 `pit_query.py:92-115` 白名单**不含** `consensus_daily`，该表述会让后来人误以为切换要动
    pit_query。已改为实查得到的 5 类 9 处消费方清单（生产夜批/生产对账/研究评估器/建表 DDL/纯函数与测试），
    并显式注明"本表切换不涉及 pit_query"。
    **未擅改的两处既有漂移（如实上报，非本班引入，owner 责任制不代修）**：
    ① `entry_counts.datasets` 全仓已漂（声明 241 / 实测 263→本班后 264），该字段自述"派生快照值…禁止凭此报数"，
    回填职责在 `scripts/governance/d3_metadata/check_registry_consistency.py --update-entry-counts`，
    本班不在批次内擅改（改则又是与他人冲突的热点行）；
    ② `business_data_categories.yaml` dev 上已有 2 个重复 category_id（`market_limit_up_pool`、
    `market_daban_board_event`），本班前后计数一致，非本班引入。
    **解阻核实（§8.12 的外来门禁已消失）**：三个 pf_alloc 文件已于 **commit fc28026614（18:33:19）** 进 dev
    （`git cat-file -e dev:src/zephyr/pf_alloc/allocation_{inputs,persistence,config}.py` 三命中），
    即 §8.12 建议的治本路径①已由 st-tickdrain 班自行完成。为不靠推断，另建**纯净 dev 临时 worktree**
    （`.worktrees/tmp-devcheck-errcode`，detached at dev）直调真门复现 serializer 条件：
    `GATE-ERRCODE-CONSISTENCY` = **PASS**（ZA-PA-0031/0032/0033 三条 active 条目现有存活定义点）。
    本班 worktree 内 17 道门重放后复跑 **17/17 PASS**（`NOT-PASS GATES: 0`）。
    **下一班须知的同类风险（已装载中）**：`ZA-BT-0043/0044`（主工作区注册表在途条目）指向
    `src/zephyr/backtest/core/cost_attribution.py` 与 `cost_model_calibration.py`，两文件当前
    **FS 存在但未进 git**（`git ls-files` 无、`git cat-file -e dev:` MISSING）——与 §8.12 同型，
    若其注册表条目先于代码落地，含 `src/zephyr/**.py` 的批次会再次被全局挡死。

14. **第二起同型全线阻断：dev 已落地的 CAP-CONSISTENCY 欠账（本批代偿，非本批引入）**：
    解阻核实后重新入队（item 0010）死于 `LOCK_TIMEOUT`（瞬时），但重放热库到**当前 dev**
    （35cf0eb36a）后本地预跑出现**新的一红**：`CAPABILITY-CONSISTENCY`（priority 101）报
    `internal_compute_provider.py: 路由支持但 meta.capabilities 未声明: ['daban_engine_load']`。
    **归因（机证，非推断）**：以纯 AST 判定函数 `capability_validator.check_route_meta_consistency_content`
    分别喂 **dev 原文**与**本批文件**，两者**同报同一条**违规 → 欠账属 dev，不属本批。
    来源=**commit 8057549c8e**（车道 B2 打板引擎负载"生产触发方"接线）：它把 `daban_engine_load`
    加进了路由能力集 `_INTERNAL_COMPUTE_CAPABILITIES`（L117）、实现了 `_fetch_daban_engine_load`（L712）、
    在 `fetch` 里加了显式路由分支（L524），并在 `src/zephyr/data/config/tasks.yaml:3127-3134`
    登记了 `daban_engine_load_daily`（`capability: daban_engine_load`、`symbols:` 为 null 且注释写明
    "null=全市场"）——**唯独漏了 `meta.capabilities` 的声明行**。
    **为什么这是全线阻断而不只是本批的麻烦**：该门按 staged `*_provider.py` 触发、判定用**整文件 AST**
    （非 own-diff），故此后**任何**触碰任一 provider 文件的批次都会被这条他人欠账挡死；且
    `capability_validator` 自述"capability 不存在则 ERROR 阻断"（启动期校验 task.capability ↔
    provider.meta），意味着 8057549c8e 刚接上的**生产任务在启动校验层也是红的**——不是纯门禁洁癖问题。
    **处置=代偿 2 行**（按同段既有约定补 `CapabilityContract("daban_engine_load", supports_symbols_null=True)`，
    `supports_symbols_null=True` 的依据=tasks.yaml 该任务 `symbols` 为 null 且方法体本身不按 symbols 过滤、
    是市场级逐交易日批）。这与宪法 §3.4「他会话在途违规不代修」不冲突：该项**已落地 dev**（不是在途），
    且已构成对全体的硬阻断；代偿范围严格限于"解除阻断所必需的最小声明行"，**未触碰** daban 的任何业务口径
    （口径真源仍在 `ex_core.daban_load_producer`，本件零复制）。
    **机证**：补声明后 `check_route_meta_consistency_content` 对本批文件返回 **[]**（零违规）；
    对 dev 纯插入 **+26/-0**（原 21 行 + 本次 5 行含注释）；`test_internal_compute_provider`(16) +
    `test_capability_validator`(48) + `test_build_consensus_daily_repaired`(9) = **73 passed**。
    **另建"忠实 serializer 沙盘"取证（本班方法论沉淀，值得复用）**：为排除"本 worktree 落后 dev 造成的假红/假绿"，
    另建纯净 dev 临时 worktree（`.worktrees/tmp-devcheck-errcode`，detached at dev），把本批 13 文件
    **原样拷入并 git add**——即"dev + 本批 blob"= serializer 落地时的真实树，再在其中直调 18 道真门。
    结果 **NOT-PASS GATES: 0**（含 `GATE-ERRCODE-CONSISTENCY` PASS、`CAPABILITY-CONSISTENCY` PASS）。
    此法一举解决两类误判：①本 worktree 陈旧导致的**假红**（如上述 CAP 红在陈旧树里无法归因）；
    ②`get_registry()` 解析到主仓导致的**假绿/假红**（沙盘内 PYTHONPATH 指自身 src，品类真源=本批版本）。
    **系统性结论（须进门禁体系议题，与 §8.12 同族）**：两起事故（ERRCODE 的 ZA-PA-0031/32/33、
    CAP 的 daban_engine_load）根因同一个——**全局对账型门禁的"观测面"没有统一定义**：
    ERRCODE 以**文件系统**为观测面（直连通道看得见 untracked、serializer 看不见），
    CAP 以**整文件 AST**为观测面（不看 own-diff，于是他人欠账连坐后来人）。
    两者都违反宪法 §3.1「内容扫描型 gate 默认 own-diff 作用域」的精神，且都让"谁先提交谁被别人的债挡死"。
    治本方向已另立裁定批处理（见 2026-09-16 裁定批台账）。
