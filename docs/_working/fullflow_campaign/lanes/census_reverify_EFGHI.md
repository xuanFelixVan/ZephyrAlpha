---
ttl: task_bound
completes_when: 总包据本件把 E/F/G/H/I 五族 30 条的四态判并入普查可信分母，且 01_break_census.md 记载数字按本件 §5 完成更正
---

# 断点普查复测 · E/F/G/H/I 五族 30 条（普查复测车道 st-ff-rv3-20260918）

产出者=`st-ff-rv3-20260918`（派工=总包 `st-fullflow-20260918`）
被复测对象=`skeleton/01_break_census.md` E 族 12 + F 族 8 + G 族 3 + H 族 5 + I 族 2 = **30 条**
本件性质=**只做复测与四态判定，零施工**（未改 `src/**`/`scripts/**`/config/注册表；未取裁定号；未建任务条目；未碰 `ruling_registry.yaml`）。

> **本件论域声明（R-024C 口径）**
> 论域 = 普查 E/F/G/H/I 五族 30 条，每条**重跑其"证据"列原始命令**。
> 论域外：A/B/C/D/J 族（55 条）+ z-verifier3 已亲验的 5 条（BRK-001/048/049/050/051）不在本件。
> 本件**不说"全绿"**；未跑条目在 §6 显式列明，绝不折入"仍成立"。

**依据等级图例**：`亲验`=本车道亲自复跑原始命令 / `转报`=引他腿产物未复跑 / `推断`=未取证。

**四态判据（本车道口径，先声明防再次口径不符）**：
`仍成立`=违规对象复跑后仍在（**数字漂移不改判，单列 §2/§5 更正**）；
`已闭合`=违规对象消失且能指到 commit 或磁盘件；
`归属错`=对象在但挂错环节/族；`口径不符`=普查与本车道用了不同分母/不同判据，数字不可直接比；
`未可判`=判据不足（本件 0 条）。

---

## 1. 四态计数（总数 = 30，无缺件）

| 四态 | 条数 | 条目 |
|---|---|---|
| **仍成立** | **22** | BRK-056/057/058/059/060/061/062/063/064/065/067 ｜ 069/070/071/072/073 ｜ 076/077 ｜ 079/083 ｜ 084/085 |
| **已闭合** | **4** | BRK-066（真闸落地）｜ BRK-074 · BRK-075（双口径+映射表治本）｜ BRK-078（保命轨最小实体） |
| **口径不符** | **4** | BRK-068（普查自身 15 vs 其列举 16）｜ BRK-080/081/082（域论域三套分母） |
| 归属错 | 0 | — |
| 未可判 | 0 | — |
| **合计** | **30** | — |

**给总包的可信分母结论**：本车道 30 条**全部亲验**（含原始 `.runtime/tmp/ff-mine0/` 三件探针重跑）。
加上 z-verifier3 已亲验的 5 条（BRK-001/048/049/050/051），全役目前**被独立复跑过的 = 35 / 85**，
**剩余未复测 = 50 条**（A 族 19 − 已验 1 = 18、B 族 7、C 族 20、D 族 9 中已验 4 = 5、J 族盲区）。
→ "还剩多少断点"自此**有分母**，且分母本身仍带 50 条未复测的已知欠账（不是零）。

---

## 2. 逐条明细（实测值 vs 普查记载）

### E 族 · 死管线/退役未清（12 条）

| BRK | 普查记载 | 本车道实测（命令） | 差 | 四态 | 依据 |
|---|---|---|---|---|---|
| 056 | nodes: generated 8711 / production 2800 / stable 316 / **deprecated 93** / planned 68 / testing 7 | `dg_agg.py` 重跑 → generated 8711 / production **2804** / stable 316 / **deprecated 93** / planned **90** / testing **8** | deprecated **93 未变**（断点核心）；总节点 11995→**12022** | 仍成立 | 亲验 |
| 057 | planned 68 + testing 7 = **75** | planned **90** + testing **8** = **98** | **+23**（悬挂面扩大，非闭合） | 仍成立（数字须更正 75→98） | 亲验 |
| 058 | `dataflow_jobs` **196 行**中 121 行 module_placeholder（61.7%）；真实 job 75 行，production/stable=**0** | 实测 `dataflow_jobs`=**204 行**；module_placeholder=**129**（63.2%）；`job` 仍 planned 51 + generated 24 = **75，production/stable=0**；但 module_placeholder production **9→14** | 总行数 +8；**headline"真实 job 零生产态"成立** | 仍成立（须更正 196→204 / 121→129） | 亲验 |
| 059 | `dataflow_runs`/`dataflow_datasets_metadata`/`dataflow_jobs_metadata` 三表 **0 行** | `rv_tables.py` → **0 / 0 / 0** | 无 | 仍成立（逐项精确） | 亲验 |
| 060 | `interface_contracts` **5 行** | 实测 **5 行**（另注：`contracts` 表 = 66 行，系**不同表**，普查未混用，本车道亦不混用） | 无 | 仍成立（唯"全项目 3477 个模块"分母本车道未复算） | 亲验 |
| 061 | `dataflow_datasets` 76 行 = planned 51 + generated 25，production=**0** | 实测 planned 51 + generated 25 = **76，production 0** | 无 | 仍成立（逐项精确） | 亲验 |
| 062 | 已建产物存在 **19/22**，3 件缺失 | `panorama_registry.md` 表头实测仍为 **19/22** | 无 | 仍成立 | 亲验 |
| 063 | 已建 22 / 待建 16 / 总 38 / 覆盖率 57.9% | 实测 **22 / 16 / 38 / 57.9%** | 无 | 仍成立（四项精确） | 亲验 |
| 064 | GOM-L3 disconnected 4 项；KS×5 仅 2 活链、CB×9 仅 4 活链 | GOM-L3 disconnected **仍 4 项**、同一 KS×5/CB×9 文字；**重复实现未删**；`\.respond(` 生产调用点实测 **0**（唯一命中 `killswitch_response_levels.py:126` 是文档串示例，参数 `"a"`/`"..."`） | 无（**部分缓解**：`7b451b7f76` 已注册 MOD-AU-004→route_incident 唯一入口，GOMAP 自记"记黄"） | 仍成立 | 亲验 |
| 065 | GOM-L0 "双轨并存 process_pool/process_lifecycle_gateway"，mounts 8 | GOM-L0 disconnected **仍 1 项**同文字，mounts **8** | 无 | 仍成立（精确） | 亲验 |
| **066** | GOM-L2 "系统级看护空白：无人看护全系统提交内存水位" | **已补真闸**（证据见 §5）：GOMAP GOM-L2 文字自记"已补真闸（2026-09-18 wiresafe BRK-066）"；`process_reaper --status` 实测输出 `watermark={'ram_total_gb': 63.85, 'ram_avail_gb': 32.32, 'ram_used_pct': 49.4, 'commit_total_gb': 95.85, 'commit_used_gb': 39.31, 'commit_pct': 41.01, 'cpu_pct': 44.9, 'degraded': False}`——**硬编码 12.5%/OK 假通道已被实探替换** | — | **已闭合** | 亲验 |
| 067 | `kline_sector_880_incremental` + `kline_sector_incremental` 同档并发争 tqcenter 单例 | 两任务**均在** `tasks.yaml`，`schedule` **同为 `daily_kline`**；`known_data_gaps.yaml` id=`kline_sector_concept_shrinking` gap_type=`universe_shrinking` status=`mitigated` 原文在册（gaps 总数 44→**45**） | 无 | 仍成立 | 亲验 |

### F 族 · 无锚点环节 BM-INV-001（8 条）

| BRK | 普查记载 | 本车道实测 | 差 | 四态 | 依据 |
|---|---|---|---|---|---|
| **068** | "无锚点环节（**15 件**·全项目最大簇）…研究孵化 34 环节中 15 件（**44%**）"——但其**同行列举的 step_id 恰为 16 个** | `dg_bm.py` 重跑 → `research_incubation` no_anchor=**16** / 34 = **47%**（列举与实测都是 16） | **普查自身标题数 ≠ 其列举 ≠ 实测**（15 vs 16） | **口径不符**（对象成立，计数记载错） | 亲验 |
| 069 | 4 件：BM-BT-05-H-A/B/C/D 偏差归因四件套 | no_anchor(backtest_validation)=**4**，四个 step_id **逐一吻合** | 无 | 仍成立 | 亲验 |
| 070 | 3 件：BM-BUY-06 真缺 + BM-BUY-05/14 退役占位 | buy_flow no_anchor=**3**，三 id 逐一吻合（BM-BUY-05/14 名仍为"编号退役占位（历史断档，禁止复用）"） | 无 | 仍成立 | 亲验 |
| 071 | 2 件：BM-MT-03 AutoML、BM-MT-04 因子发现 | model_training no_anchor=**2**，两 id 吻合 | 无 | 仍成立 | 亲验 |
| 072 | 1 件：BM-RC-12 极端事件与黑天鹅 | risk_control no_anchor=**1** = BM-RC-12（50 环节中唯一） | 无 | 仍成立 | 亲验 |
| 073 | BM-SEL-20 前缀 BM-SEL（选股）却挂 `position_management` → 双重违例 | 实测 `['BM-SEL-20','多策略交叉投票','position_management']` —— **前缀/阶段错位仍在**，且仍零锚点 | 无 | 仍成立 | 亲验 |
| **074** | "文档 5 vs 真源 27，**漂移 22 件（5.4 倍）**→ 生成器未重跑，最重要健康指标被低估" | `battle_map_panorama.md:23-26` 现**并列两行**：`无锚点环节·有效态口径（BM-INV-001 违例面…）=5` **与** `无锚点环节·裸表口径（steps LEFT JOIN anchors 零命中…）=27`，另起 `口径差异解释 … 差 22 件，**非数据缺失**`；§41「状态口径映射表 / State-Caliber Mapping（生成器现算，禁手工对齐）」正文写"（全流通战役普查 **BRK-074/BRK-075 治本**）…普查把 5 与 27 相减，报成 5.4 倍产物漂移，实为**口径未标注**" | 5.4 倍"漂移"这一**命题本身被生成器否证** | **已闭合** | 亲验 |
| **075** | "两套口径**无映射表** → 无法机械判'运营态'到底几个" | 同文档 §41 现给**三套**口径映射表并逐态列实测分布：① step 五态 design 157/production 151/deprecated 20/candidate 8/missing 5；② anchor `status_snapshot` 八值 production 200/planned 164/stable 147/generated 39/deferred 16/candidate 11/NULL 10/design 1；③ depgraph `build_status` 现值 production 312/generated 155/stable 67/—28/planned 20/deprecated 6；并自证"②③合计=588 与锚点总数同行互验" | 映射表已从"无"到"有"（且升为三套） | **已闭合** | 亲验 |

**F 族补充实测（普查未记载的新事实，交总包）**：`battle_map_domain_policy.yaml` 的
`acknowledged_orphans.steps` 现已把无锚点环节**正式登记为待接线孤儿**，分 3 组共 **34 个 step_id**
（high 28 / low 3 / low 3）。与本车道 DB 实测 27 件裸表零锚点做差集：

- **登记未覆盖 5 件**：`BM-BT-05-H-A / -B / -C / -D`（**= BRK-069 整条偏差归因四件套，完全未登记**）+ `BM-RES-11-A`。
- **登记却已非零锚点 12 件**（清单滞后于 DB，即这 12 件已挂上锚点）：
  `BM-MT-02 / BM-MT-05 / BM-MT-05-A / BM-RC-12-B / BM-RC-12-C / BM-RES-05 / BM-RES-08 / BM-RES-09 / BM-RES-10 / BM-RES-11 / BM-SIM-01 / BM-SIM-08`。

→ 结论：**F 族"补齐锚点"这条闭合路径尚未走完**（0 件因此改判"已闭合"）；
且新登记册自身已漂移（漏 5、多 12），须按 DB 现算重生，不可手改。

### G 族 · 横切机制未落地（3 条）

| BRK | 普查记载 | 本车道实测 | 差 | 四态 | 依据 |
|---|---|---|---|---|---|
| 076 | 横切类别数=17，mermaid 尾行 `class CC_01..CC_17 design`（17 全 design，production=0） | `battle_map_12_cross_cutting.md:23` 横切类别数 **17** ✓；`:68` **仍为** `class CC_01,…,CC_17 design`（17 全 design） | 无 | 仍成立（精确） | 亲验 |
| 077 | CC_06 四模式开关未建（状态 design） | `:68` 含 CC_06 design ✓；在 `ex_core`/`simulation`/`backtest` 三域 grep `shadow`+`mode` 实测 **0 命中**（无四模式开关实体） | 无 | 仍成立 | 亲验 |
| **078** | CC_07 应急保命轨"有登记、有优先级、**零节点**"；`decision_nodes` 213 行全 planned → 该轨无任何落地节点 | **实体已落地**：`config/emergency_track.yaml`（84 行，把 `activation_condition` 翻译成判据）+ `src/zephyr/governance/resilience_governance/emergency_track_guardian.py`（**624 行**）+ `process_reaper._run_safety_wires()` **真调** `run_emergency_track_check()` + `tests/governance/resilience/test_emergency_track_guardian.py`（301 行）；`--status` 实测 `emergency_track_state=normal confirmations=0 breaches=1`。 commit `7b451b7f76`。**残留**：`:68` CC_07 仍 design、`decision_nodes` 实测仍 **planned 213（100%）** | 判据两真源（图/决策节点表）滞后于代码 | **已闭合（最小实体级）**，附派生件滞后告警 | 亲验 |

### H 族 · 域注册表一致性（5 条）

先立**论域事实**（这是本族四条里三条判"口径不符"的根因）：

| 域论域 | 实测基数 | 出处 |
|---|---|---|
| `architecture_model/index.yaml` §domains | **74**（无 D_TEST；末次语义变更 09-13，非今日） | 亲验 |
| depgraph `nodes` DISTINCT `domain_id` | **73**（零节点域不会出现于此） | 亲验 |
| 普查所用"**75** 域" | = index.yaml 74 **+ D_TEST**；而 `D_TEST` **只**出现在 `project_handbook/05_trading_domains.md:142` 与 `domain_responsibility_market…`/`domain_responsibility_layer_mapping.yaml`，**不在 index.yaml** | 亲验（差集实测：census75 − index74 = `['D_TEST']`，反向空集） |

| BRK | 普查记载 | 本车道实测 | 差 | 四态 | 依据 |
|---|---|---|---|---|---|
| 079 | `stock_selection.allowed` 含 `D_SIGNAL`，75 域中无之 → 幻影域 | 实测 `D_SIGNAL` **仍在** `stock_selection.allowed`；nodes 中 0 个 `D_SIGNAL`；不在 index.yaml 74 域内；`nodes WHERE domain_id='D_SIGNAL'` = **0** | 无 | 仍成立（精确） | 亲验 |
| 080 | "11 阶段 allowed 并集 42 域；depgraph 域中从未被任何 flow_stage 允许 = **34**" | 并集 **42 ✓ 精确**；never-allowed 按论域三值：**32**（nodes 论域）/ **33**（index.yaml 论域）/ **34**（index74+D_TEST，即普查论域） | 普查 **34 未声明论域**，同数不同物 | **口径不符**（分母未声明；结论方向仍成立） | 亲验 |
| 081 | business 38 + tool 19 = 57；未分类 **19** 域；注 `D_PLAN` 未分类却出现在 `position_management.allowed` | business **38 ✓** + tool **19 ✓** = 57；未分类 **17**（nodes 论域）/ 18（index 论域）/ 19（普查论域）；`D_PLAN in position_management.allowed` = **True**（分类册与白名单册自相矛盾**仍成立**） | 同 080 根因 | **口径不符**（D_PLAN 子命题=仍成立） | 亲验 |
| 082 | FDR distinct **68**；FDR 有 depgraph 无 = **4**（四 *_legacy）；depgraph 有 FDR 无 = **11** | FDR distinct **68 ✓ 精确**；FDR−depgraph = **5**（`D_EXECUTION/D_ORDER/D_PORTFOLIO/D_SIGLEGACY/D_SIGNAL`）；depgraph−FDR = **10**（D_TEST 因零节点不入 nodes 集） | 4→5、11→10，**全部由零节点域 D_SIGLEGACY/D_TEST 造成**，与 079/083 同源 | **口径不符**（两册不同步的结论仍成立） | 亲验 |
| 083 | `D_SIGLEGACY`=0 节点、`D_TEST`=0 节点、`_domain_red_blue_validator` 目录 0 篇 .md | DB 实测 `domain_id=D_SIGLEGACY` → **0 节点**、`D_TEST` → **0 节点**；handbook `:141/:142` 两行原文均在（HEAD 与工作树一致）；该目录 `*.md` 计数 = **0**（仅存 `algo_flow/` 子目录） | 无 | 仍成立（三项精确） | 亲验 |

### I 族 · 治理/注册表（2 条）

| BRK | 普查记载 | 本车道实测 | 差 | 四态 | 依据 |
|---|---|---|---|---|---|
| 084 | ROOR `summary`={total_registries 73, fully_scanned 19, pending 5, broken 1, by_tier 11/28/34}；而各 tier 实际 registries 长度 **12/28/34 = 74**（tier_0 漂 1） | `summary` **六字段逐项精确复现**（73/19/5/1 + by_tier 11/28/34）；`tiers[*].registries` 实长度 = **12 / 28 / 34**，合计 **74** | **无——漂移 1 仍在** | 仍成立（含"计数漂移 1"这一子命题精确复现） | 亲验 |
| 085 | `acknowledged_orphans.modules` 实测"≥9 件…该 list 未全量读完（输出截断），FF-14 子挖矿须先取全量条数" | 全量读完 = **恰好 9 件**（与普查已读出的 9 件同名，无第 10 件）；另该键的姊妹键 `.steps` 存在且含 3 组 34 个 step_id（普查未记载，见 F 族补充实测） | 不确定性**消解为 9** | 仍成立（普查疑点由本车道关闭） | 亲验 |

---

## 3. 六向台账重生成后的新分布（★ 本役最大量级的实测变化）

**执行**：`python scripts/automation/flowthrough_verifier.py --all`，尺子=HEAD 内 `1162a40d35`（含 `e154da27ac` 论域补口）。
**先读 argparse 真接口再跑**（红线要求）：`--all` 无 `--apply/--mirror` 类写生产语义，写盘目标实测仅
`OUT_DIR=docs/_working/fullflow_campaign/skeleton/`（两件台账）+ `TMP_DIR=.runtime/tmp/ff-verifier/`。
**旧 392KB 台账已备份**至 `.runtime/tmp/st-ff-rv3-20260918/`（md5 `38f24981…`/`40bd8e2d…`），
且两件台账**本就跟踪在 HEAD**（`63802383af`），重生成不致丢证。
**论域硬断言 `universe_guard_payload()`（11 必备字段）本次未崩**，退出码 0，两件均落盘。

| 口径 | 旧台账（19:36，`generated_at 11:36:03Z`） | **新台账（21:24，`13:24:01Z`）** |
|---|---|---|
| 行数 | 18（FF-01..FF-17 + COVERAGE-DIFF） | 18（同） |
| **全 18 行汇总** | **红 13 / 黄 5 / 绿 0** | **红 16 / 黄 2 / 绿 0** |
| FF-01..FF-17 | 红 13 / 黄 4 / 绿 0 | 红 16 / 黄 1 / 绿 0 |
| 转黄项 | FF-05 / FF-11 / FF-14 / FF-17 / COVERAGE-DIFF | FF-14 / COVERAGE-DIFF |

（"17 环节"与"18 行"是同一台账的两个分母：COVERAGE-DIFF `kind=meta` 非环节。
z-verifier3 的"红13/黄5"取全 18 行，与本件 FF-only"红13/黄4"不矛盾，仅分母差 1，**已在 §4 单列以免再次口径不符**。）

**逐向差分（这才是"差多少"的真答案）**：

| 向 | 旧 | 新 | 定性 |
|---|---|---|---|
| ①入口有料 | 绿6 / 黄2 / 红7 / 不可测2 | **红15 / 不可测2** | ⚠️**本次不可用**——见下"①向被 ClickHouse 超时污染" |
| ②转化能跑 | 红5 / 黄-门位8 / 黄1 / 不可测1 / 绿2 | **逐项完全相同** | 真无变化（崩点仍存，见 §7） |
| ③出口有货 | 绿9 / 不可测8 | **逐项完全相同** | 真无变化 |
| ④下游能取 | 绿16 / 红1 | **逐项完全相同** | 真无变化 |
| ⑤哨兵在岗 | 绿11 / 红4 / 不可测2 | **红7 / 黄8 / 不可测2（绿=0）** | ✅**真实口径变化**，与 z-verifier3 预判方向一致 |
| ⑥失败会响 | 黄17 | **红16 / 不可测1** | ⚠️**纯尺子改严**，非代码退化（见下） |

### 3.1 ①向被 ClickHouse 超时污染（**必须带这个限定词引用新数**）

新台账 ①向 15 个"红"**全部**由 `broken_hop` 驱动，而其 evidence 写的是 `=-1行`
（查询失败哨兵值），**不是 `0行`（真表空）**：

- 新台账 `broken_hop` 条目合计 **30 处**，全部 evidence 为 `=-1行`；旧台账同类仅 **2 处**。
- 运行日志实测 `CH query 失败(TCP+HTTP 均失败)` + `HTTP query 失败: timed out` **12 次**，
  并带 ClickHouse 线程栈；失败对象含 `SELECT count() FROM c1_market.tick_data FINAL`、
  `SELECT max(toString(trade_date)) FROM c1_market.tick_data FINAL`。
- 同一张表两版对照：`c1_backtest.strategy_screen` 旧=`1306行`（真值）→ 新=`-1行`（没测到）；
  `c1_backtest.crisis_gate_log` 旧=`0行`（真表空）→ 新=`-1行`（没测到）。

→ **①向新分布不得读作"15 环节入口都没料"**。本车道判：**CH 侧不可用（`tick_data FINAL` 重查超时）所致，须 CH 健康后重跑**。
→ **顺带交回一条尺子缺陷**：`①`把"查询失败(`-1`)"与"真断链"同码进 `broken_hop` 判红，
**测不到与真坏不可分**——这正是宪法 §9/R-024 要防的"把没扫到读成扫了且为零"的反向变体（把没测到读成测出红）。建议总包裁：`-1` 应判`不可测`而非`红`。

### 3.2 ⑥向变红是尺子口径变严，不是代码退化

FF-01 ⑥向 `silent_except_count` 旧=**324**、新=**324**（一模一样），`silent_sites` 前 20 条同；
但 verdict 由 `黄` → `红`。新版记录新增字段 `pattern_counts / files_scanned / dynamic_injection / verdict_reason`，
verdict_reason 实测：`检出 324 处 AST 级静默放行 / 五模式合计 34 处命中`
（`pattern_counts = {silent_except_pass 24, debug_then_proceed 0, always_true_gate 0, fail_open_default 10, latch_before_deliver 0}`）。
旧版记录**无 `pattern_counts`**。→ **⑥的红全部来自判据换轨（引入五模式），输入未动**。

### 3.3 ⑤向绿→0：z-verifier3 结论方向对，机理需收窄（本车道修正其表述）

`sentinel_verdict()` 现行实现（HEAD `1162a40d35`）确有 `if blind: return "黄"` 于 `return "绿"` 之前。
但对**旧台账**逐条按现行函数回放（注意机读键名是 `allow_empty_blind`，非 `blind`——本车道首跑亦踩此键名坑）：

| 旧台账 ⑤=绿的 11 环节 | 其 `allow_empty_blind` | 现行代码回放 |
|---|---|---|
| FF-01 / 02 / 03 / 04 / 06 | **1**（`c1_market.market_convertible_bond_clause` allow_empty=true） | **黄 ⇒ 与记载互斥** |
| FF-05 / 07 / 09 / 11 / 12 / 15 | **0** | **绿 ⇒ 自洽** |

→ **精确结论**：旧台账 17 环节中**恰 5 环节**⑤=绿在现行代码下不可能产生，其余 6 个绿合法。
→ **更硬的自证矛盾**（不依赖"代码不可能"）：旧台账 FF-01 ⑤记录**同一行内** evidence 已写
`有阈值行 40 表 / allow_empty 白名单 1 表（**白名单不判绿**） / breach 实跑=True 违规=0`，
而其 `verdict` 字段却是 **`绿`**——**该行自己反驳自己**，无需引代码即证伪。
→ 本车道判 z-verifier3 的"先 `--all` 重生成再引用"硬指令**成立且已执行**；
但其"代码不可能出绿 ⇒ 两件台账为已知失真产物"的**全称式机理应收窄为"5/11 绿不可复现 + 行内自相矛盾"**，
否则会把 6 个合法绿一并误判为伪造（总包引用时若按"全失真"处置，会低估旧台账里 ②③④ 向的可信度——
而 ②③④ 三向新账与旧账**逐项相同**，恰说明旧账多数非编造）。

---

## 4. GOMAP / ROOR 实测计数 vs 普查记载（★ 总包预期"大概率已漂"，实测**未漂**）

| 件 | 普查记载 | 本车道实测（原始命令重跑） | 判 |
|---|---|---|---|
| `config/governance_operations_map.yaml` §counts（BRK-001/002） | `{total_modules 416, wired 244, wired_dynamic 6, wired_by_header 71, suspect_orphans 95}` | `yaml.safe_load(...)['counts']` → **`{'total_modules': 416, 'wired': 244, 'wired_dynamic': 6, 'wired_by_header': 71, 'suspect_orphans': 95}`** | **五字段逐项完全一致，未漂** |
| GOMAP §pipeline 各层 disconnected/mounts | L0 disconnected（双轨并存）+ mounts 8；L2 系统级看护空白；L3 disconnected 4 项 | L0 disconnected **1** / mounts **8**；L2 disconnected **2**（含已闭合的 BRK-066 项）/ mounts **6**；L3 disconnected **4** / mounts **8**；L1/L4 各 1（已删项）、L5/L6 各 0 | 结构一致；**L2 内容已实质变更**（见 §5） |
| `docs/registry_of_registries.yaml` §summary（BRK-084） | `{total_tiers 3, total_registries 73, fully_scanned 19, pending_scan 5, broken 1, by_tier 11/28/34}` | 六字段**逐项精确复现**；`tiers` 实为 `d['tiers']`（3 个 dict，键 `registries`），实长 **12/28/34 = 74** | **summary 未漂；tier_0 漂移 1 仍在**（BRK-084 的漂移子命题精确成立） |

→ **今日多车道落地并未推动这两个 headline 计数**（它们由 GOMAP/ROOR 自身的生成器口径决定，
今日落地件未触发这两个重生器）。这与派工预期相反，已单列 §8 推翻前提。

---

## 5. 判"已闭合"的 4 条 · commit / 磁盘件证据

`git merge-base --is-ancestor` 实测 `7b451b7f76` **是 HEAD 祖先**（已进版本保护）。

| BRK | commit 证据 | 磁盘件证据 |
|---|---|---|
| **066** 系统级内存水位无看护 | `7b451b7f76` `feat(wiresafe): 保命链接线批1——…全系统内存水位真闸(BRK-066)…`；`git log -S"ALERT-SYS-003" -- config/alert_rules.yaml` **唯一命中该 commit** | `git show --stat` ：`config/alert_rules.yaml +38`、`capacity_assurance/host_resource_governor.py **+289**`、`trading/process_reaper.py +45`、`tests/autonomy/test_system_watermark_gate.py +152`。实探证据：`process_reaper.py:1064` `from …host_resource_governor import check_system_watermark` → `:1068` 赋值 → `:1095-1100` 进 `--status` 输出；`--status` **亲跑**实测真值（RAM/commit/CPU 三面非硬编码）；`grep 12.5` 实测该值现仅存于**历史缺陷说明注释**（`:12 [INVARIANTS] 探针必须是实探——禁硬编码读数（历史缺陷：probe() 曾恒返 12.5%/OK 的假通道）`） |
| **078** 应急保命轨零节点 | 同 `7b451b7f76`（标题即含"应急保命轨最小实体(BRK-078)"）；施工包 `lanes/wiresafe_BRK-078_construction_pack.md` 同批入库 | `config/emergency_track.yaml`（84 行，新建）+ `src/zephyr/governance/resilience_governance/emergency_track_guardian.py`（**624 行**）+ `tests/governance/resilience/test_emergency_track_guardian.py`（301 行）+ `process_reaper.py:1055` 真调 `run_emergency_track_check()`；`--status` 实测 `emergency_track_state=normal … breaches=1`。**残留（不算重开）**：`battle_map_12_cross_cutting.md:68` CC_07 仍 `design`、`decision_nodes` 仍 planned 213 → 派生件待重生 |
| **074** 无锚点文档 5 vs 真源 27 | **无 commit 可用**——`battle_map/*.md` 已被 `326952a276 chore(git): 派生文档移出 git 跟踪——100 文件 git rm --cached` 移出跟踪，现命中 `.gitignore:562` | 磁盘件：`docs/02/…/battle_map/battle_map_panorama.md:23-26` 双口径两行 + `:41` 「状态口径映射表（生成器现算，禁手工对齐）」+ `:43` 正文点名"BRK-074/BRK-075 治本" | 
| **075** 两套口径无映射表 | 同上（无 commit，派生件不入库） | 同文档 `:45-51` 三套口径映射表 + "②③合计=588 与锚点总数互验"自核行 |

⚠️ **须总包裁的副作用**：BRK-074/075 的治本**只存在于磁盘**，其载体文档**已被 gitignore**，
即"最重要健康指标"的修正**无版本保护、不可 `git log -S` 取证**（本车道只能给文件行号）。
按宪法 §9.5（静态清单禁手工维护）该件是生成器产出，可重生；但"改态不可取证"这一性质本身是验收风险。

---

## 6. 未跑条目 + 原因

本件 **30 条全部亲验，无未跑条目**。以下三项**主动未做**（非遗漏，均因红线/预算）：

1. **未复算 BRK-060 的"全项目 3477 个模块"分母**。原因：3477 属"模块数"口径，
   与本件实测的 `nodes`=12022（节点数）不同物；要判须先定"模块"口径真源，属总包裁定，不宜由复测车道自定。
   → 该条 headline（interface_contracts=5）已亲验成立，仅分母待裁。
2. **未跑 `generate_project_depgraph.py --force` 后重算 E 族 depgraph 类条目**。
   原因：本车道只读施工；且 nodes 11995→12022 / edges 22805→22843 实测表明**今日已有他腿刷新**，
   再 force 一遍会与在途车道抢写。→ E 族 056/057/058/061 的漂移数字引自**当前快照**，非本车道改动。
3. **未对 CH 做健康修复或改判 ①向**。原因：修 CH/改尺子均为施工，越红线。
   → ①向已按 §3.1 如实标注"本次不可用"，未拿污染数去判任何 BRK。

---

## 7. ★ 第 11 族顺手项：②入口"import 期即崩"冒烟复测（只读）

**(a) 本车道切片涉及的 7 个模块 `python -c "import <mod>"` 冒烟：全 7 件 IMPORT-OK，无一崩。**
`host_resource_governor` / `emergency_track_guardian` / `last_resort_watchdog` /
`kill_switch_orchestrator` / `trading.process_reaper` + z-verifier3 点名的 `alt_data.cohort_daily_ledger`、`data.ch_parts_monitor`。

**(b) 推翻/收窄"②入口 import 期即崩"这一族名（重要）**：
`cohort_daily_ledger` 与 `ch_parts_monitor` **作为包 import 时不崩**（本车道实测），
但**作为脚本直跑**（`python src\zephyr\alt_data\cohort_daily_ledger.py`）时崩（新台账 21:24 仍记 rc=1）。
机理已定位：`cohort_daily_ledger.py:60` 写 `from schemas.categories.cohort_daily_ledger import …`，
而 `schemas` 实测解析到**仓库根** `D:\ZephyrAlpha\schemas\__init__.py`（`src/schemas` 与 `src/zephyr/alt_data/schemas` **均不存在**）。
→ 该绝对 import **只在仓库根位于 `sys.path` 时成立**；脚本直跑时 `sys.path[0]` 被换成文件自身目录 ⇒ 必崩。
→ **建议族名定性为「②入口以脚本方式直跑即崩（sys.path[0] 依赖的真绝对 import）」**，而非"import 期即崩"：
差别的实质是——若按"import 即崩"去修，会误判"此模块无人可用"；实为"经包路径可用、经脚本入口不可用"，
处方应是改 import 为 `zephyr.alt_data.…` 或补 `schemas` 的正确挂接，**不是**下线该模块。
`ModuleNotFoundError`/`calendar.day_abbr`/`pandas._pandas_datetime_CAPI`/`email.utils._has_surrogates`
**四式崩法同根**：脚本入口直跑时 `sys.path[0]` 指向模块自身目录，从而**同名局部件遮蔽 stdlib/三方包**
（`calendar.py`/`pandas`/`email` 类阴影）+ 仓库根包失联。这是**一类**系统性缺陷，不是三个孤立崩点。

**(c) 本车道新增一条 z-verifier3 未记载的崩点（同族第 4 件）**：
新台账 FF-02/FF-04 ②向实测 `src/zephyr/data/quality_sentinel.py` → rc=1，
`ImportError: cannot import name '_has_surrogates' from partially initialized module 'email.utils' (circular import)`。
→ **`quality_sentinel` 是哨兵本体**（⑤向真跑依赖它，`run_sentinel_live()` 内 `from zephyr.data import quality_sentinel`），
它以脚本入口方式崩虽不必然影响包内 import 路径，但意味着**⑤向真跑的可信度与 ②向崩族同源**。
→ 该件应并入 V3-N02 族（总包转正时建议：一 BRK 四症状，含 quality_sentinel）。

---

## 8. R-018 高风险判断表（本车道自评）

| # | 判断 | 等级 | 若错会怎样 | Max 验真命令 |
|---|---|---|---|---|
| J1 | 六向新分布 **红16/黄2/绿0**，其中 **①向 15 红被 CH 超时污染、⑥向 16 红纯尺子改严** | **高** | 总包若把"红16"当真实退化上报 Owner，会误判战役夜间施工把系统做坏了（实际代码侧 ②③④ 零变化） | `python -c "import yaml;d=yaml.safe_load(open('docs/_working/fullflow_campaign/skeleton/04_sixway_machine_ledger.yaml',encoding='utf-8'));print([(s['stage_id'],s['sixway']['①入口有料'].get('broken_hop')) for s in d['stages'] if s['stage_id'].startswith('FF')])"` → 应见 30 处 `-1行`；并 `grep -c "CH query 失败" .runtime/tmp/st-ff-rv3-20260918/verifier_all.log` → 12 |
| J2 | **BRK-066/078 判已闭合**（非"仍成立"） | **高** | 若"最小实体级"不等于普查要的"该轨落地"，则战役会少一项高危待办（应急轨仍只有 guardian 一条腿，CC_07 图上仍 design、decision_nodes 仍 0 落地） | `git show --stat 7b451b7f76` + `python -m zephyr.trading.process_reaper --status`（看 `safety_wires:` 行）+ `grep -n "class CC_" docs/02_enterprise_architecture/07_trading_decision_architecture/battle_map/battle_map_12_cross_cutting.md`（CC_07 是否仍 design） |
| J3 | **BRK-074/075 判已闭合**，且**普查的"5.4 倍漂移"命题本身被否证**（是口径未标注，不是产物漂移） | **高** | 若总包继续按"生成器未重跑致 5.4 倍低估"处置，会去重跑一个本来正确的生成器，并可能反过来把已标注的双口径"改回"单口径——即**用假病灶真治** | `sed -n '19,51p' docs/02_enterprise_architecture/07_trading_decision_architecture/battle_map/battle_map_panorama.md`（看 5/27 两行 + 映射表 + 点名 BRK-074/075） |
| J4 | **GOMAP counts 与 ROOR summary 今日未漂**（416/244/6/71/95 与 73/19/5/1 逐项精确） | **中** | 总包若据此等"已更新"的数字去写交付报告，会引用一个它预期已变但实际未变的数（危害有限，但"以为会漂"的推理链需断掉） | `python -c "import yaml;print(yaml.safe_load(open('config/governance_operations_map.yaml',encoding='utf-8'))['counts']);print(yaml.safe_load(open('docs/registry_of_registries.yaml',encoding='utf-8'))['summary'])"` |
| J5 | **H 族 080/081/082 三条的"漂移"全是零节点域（D_SIGLEGACY/D_TEST）造成的论域未声明**，非今日改动 | **中** | 若判为三条独立"口径不符"去分别修，会漏掉唯一真修法（给 battle_map 域对账**钉死一个论域定义**），三数仍会下次再漂 | `python .runtime/tmp/st-ff-rv3-20260918/rv_h_index.py`（三套分母 32/33/34 同屏输出）+ `python -c "import yaml;print(len(yaml.safe_load(open('architecture_model/index.yaml',encoding='utf-8'))['domains']))"` → 74 |
| J6 | **BRK-068 普查计数错（15 vs 16）** | **低** | 研究孵化无锚点簇被少算 1 件，占比 44%→47%，影响"最大簇"排序叙述 | `python .runtime/tmp/st-ff-rv3-20260918/dg_bm.py`（数 research_incubation 行=16） |
| J7 | 第 11 族应定名为「脚本入口直跑即崩（sys.path[0] 依赖）」，且**含 quality_sentinel 共 4 件**而非 2 件 | **中** | 若按"import 即崩"处置，会误下线两个其实经包路径可用的模块；漏 `quality_sentinel` 则 ⑤向真跑的可信度隐患继续隐身 | `python -c "import zephyr.alt_data.cohort_daily_ledger,zephyr.data.ch_parts_monitor,zephyr.data.quality_sentinel;print('PKG-IMPORT-OK')"` 对照 `python src/zephyr/alt_data/cohort_daily_ledger.py` |
| J8 | **本车道未复测任何 A/B/C/D/J 族条目**，全役可信分母 35/85 | **高** | 若把本件当成"85 条已复测完"，Owner 的"万无一失、没有任何遗漏"验收会建立在一个 50 条未复测的分母上 | `grep -c "^| BRK-" docs/_working/fullflow_campaign/skeleton/01_break_census.md` → 85，与本件 §1 的 30 + verifier3 的 5 对账 |

---

## 9. ★ 本车道推翻总包/前腿前提（单列）

| # | 被推翻的前提（出处） | 实测 | 性质 |
|---|---|---|---|
| P1 | 派工 §1："**今日多车道落地，这两个数（GOMAP counts / ROOR）大概率已漂**" | **未漂**。GOMAP 五字段、ROOR 六字段**逐项精确等于普查记载** | 预期落空（非事实错误，但引用该预期会误导）——今日落地件未触发这两个 headline 的重生 |
| P2 | 派工 §1 / 总包活单："**#ARCH-338 / #ARCH-339 / #ARCH-343 三条的 headline 计数待更正（`ruling_registry.yaml`…）**" | **这三条不在 `ruling_registry.yaml` 里**。该册实测 `entries`=158 条、`ruling_id` 最大数字号 = 裁定号 339，**裁定号 343 不存在**（此号从未登记）（#341/#342/#344 亦不存在）。`#ARCH-338..356` 是 **z-arch 案卷系列**，载体=`lanes/arch_338_356_dossiers.md`，与裁定号是两套编号 | **编号体系混用**。更正动作应落在 arch 案卷件；若去 `ruling_registry.yaml` 找 #343 会一无所获。本车道已在 §10 按案卷件交回实测值 |
| P3 | z-verifier3（派工 §1 引）："台账记 FF-01 ⑤=绿，但 `sentinel_verdict()`…**代码不可能出绿**"，并据此判两件台账为"已知失真产物" | 机理**偏宽**：旧台账 ⑤=绿 共 11 环节，其中 **blind=0 的 6 个（FF-05/07/09/11/12/15）在现行代码下仍判绿、合法可复现**；仅 **blind=1 的 5 个（FF-01/02/03/04/06）互斥**。另：机读键名是 `allow_empty_blind` 不是 `blind`（本车道首跑亦踩） | 结论方向成立、**外延须收窄**。附带交回一条**更强且无需引代码的证据**：旧台账 FF-01 ⑤ 行内 evidence 自写"白名单不判绿"而 verdict=`绿`，**该行自我反驳** |
| P4 | 派工 §1："六向台账机读件…实测 **17 环节** 红13/黄5/绿0" | 17 与 18 是两个分母：台账实 **18 行** = FF-01..FF-17（17 环节）+ `COVERAGE-DIFF`(`kind=meta`)。"红13/黄5"= 全 18 行口径；FF-only 是**红13/黄4** | 口径补充（不是错，但引用须带分母，否则下次又漂 1） |
| P5 | 普查 F 族隐含前提：无锚点环节"尚无承载/未被登记" | `battle_map_domain_policy.yaml.acknowledged_orphans.steps` **已登记 34 个 step_id**；但对 DB 实测 27 件**漏 5 件**（含 BRK-069 全部四件套 BM-BT-05-H-A/B/C/D）且**多 12 件已非零锚点** | 新事实：登记册自身已双向漂移。F 族未因此闭合，但"闭合路径=补挂锚点"已部分启动，普查须记这一状态 |

---

## 10. 交回总包的实测值（**不动 `ruling_registry.yaml`**）

**(a) `#ARCH-338/339/343` headline 计数（案卷件 `lanes/arch_338_356_dossiers.md`）**

| 案卷 | headline 现文 | 本车道实测 | 可否直接更正 |
|---|---|---|---|
| **#ARCH-343** | "pf_alloc 整域…（**7 件仅 W03 真接线**）" | 独立重测 in-pkg 非 test importer：**W01=2、W02=0、W03=5、W04=4、W05=5、W06=0、W07=0** ⇒ 有 importer 的是 **W01/W03/W04/W05 = 4 件**，零 importer 的孤儿 = **W02/W06/W07 = 3 件**。**与案卷 §105-106 的逐件数字 100% 复现** | ✅ 可直接更正为"7 件中 3 件零 importer（W02/W06/W07）；'仅 W03 真接线'在 import 层不成立"。**但**案卷自注：in-pkg importer ≠ 生产 orchestrator 可达，终判属 z-land3 DFS，本车道未做 |
| **#ARCH-338** | "执行域孤儿族…（OrderExecutionSaga/ExecutionEngine/ex_sor/order_splitter/process_fill **零生产接线**）"，案卷自评"核心成立，但 headline 口径需修（**3/5 子项**）" | 本车道**未做代码级可达性 DFS**（越只读边界且属 z-land3 落地权） | ❌ 不交实测值，维持案卷自评。**建议总包别把 338 的更正挂在本车道** |
| **#ARCH-339** | "风控孤儿闸族产而不消（K03 StopGate/K06/K09/K07）"，案卷自评"StopGate 归因需重分类"（`auto_runtime_core.py:137 self._stop_gate = StopGate()` **在生产核心被实例化**） | 本车道**未复跑 K03/K06/K09/K07 调用点** | ❌ 不交实测值（同上） |

**(b) 若"338/339/343"实指 `裁定#338/#339`（`ruling_registry.yaml`）**——本车道顺手实测两处可直接核的 headline：

| 裁定 | headline 现文 | 实测 | 建议 |
|---|---|---|---|
| `裁定#339` | "miniQMT 9/18 退役，**tasks.yaml 63 任务 source=miniqmt**" | `tasks.yaml` 现 **264 任务**，其中 `source=miniqmt` = **57**（akshare 98 / akshare_alt 36 / internal 19 / tushare 12 / tqcenter 5 / tdx 5 / tickflow 4） | **63 → 57**（−6）。注：任务总数已 262→264（与 z-verifier3 对 BRK-050 的 +2 复测一致），故 63 也可能是切换前真值被在途改表推动；**须总包裁定 57 是否=已接管进度**，本车道不推断 |
| `裁定#338` | "GT-6 **348 条** HIGH 落点债"、"重复 TTL 头 **106/200** 抽样" | 未复测（HIGH 落点债须跑落点校验器，属施工面；本车道未起任何写路径校验器） | 留待下一轮 |

---

## 11. 修正建议（**不改 `01_break_census.md` 原件**）

**须更正数字（对象不变，仅记载值）**：
1. `BRK-057` 75 → **98**（planned 90 + testing 8）。
2. `BRK-058` 196 行/121 行/61.7% → **204 行 / 129 行 / 63.2%**；headline"真实 job production/stable=0"**保持**。
3. `BRK-056/060/061` 等引 depgraph 快照者，须加**快照时刻标注**（本车道实测 nodes **12022**、edges **22843**，普查时 11995/22805；不标注则每次对账都判成"漂移"）。
4. `BRK-068` 标题与影响句 **15 件 / 44% → 16 件 / 47%**（普查同行列举已是 16）。

**须改判**：
5. `BRK-066`、`BRK-078` → **已闭合（附残留）**，引 commit `7b451b7f76`；`BRK-078` 残留=CC_07 图态与 decision_nodes 待重生。
6. `BRK-074`、`BRK-075` → **已闭合**，且**撤下"5.4 倍产物漂移"这一表述**（真源文档已点名 BRK-074/075 治本并给出三套口径映射表）；同时登记"治本件已被 gitignore、不可 commit 取证"为独立风险项。
7. `BRK-080/081/082` → 由"仍成立"改"**口径不符**"，并**合并为一条**（同一根因：域对账未钉论域 + 零节点域 D_SIGLEGACY/D_TEST）；真修法=给 battle_map 域对账声明单一论域，而非三处分别修数。
8. `BRK-064` → 保持"仍成立"，但补记：唯一入口链已注册（MOD-AU-004→route_incident），**而生产侧 `respond()` 调用点实测仍 0**，GOMAP 自记"记黄"，重复实现"净删候选只登记不删"。
9. `BRK-085` → 把"≥9 / 输出截断 / 须先取全量条数"改为**确定值 9**；并新增子项：`.steps` 键（3 组 34 id）与本车道差集（漏 5 多 12）。

**须新增（普查装不下的）**：
10. 第 11 族定名建议：「**②入口以脚本方式直跑即崩（sys.path[0] 依赖的真绝对 import / 同名件遮蔽 stdlib）**」，
    成员 4 件：`cohort_daily_ledger`(schemas)、`ch_parts_monitor`(calendar & pandas 两式)、`quality_sentinel`(email.utils)。
    本车道已证：**包 import 全通过**，故该族**不得**据"import 即崩"下线模块。
11. 尺子缺陷 1 条（非 BRK，属工具侧）：①向 `-1行`（查询失败）与真断链同码判红，"测不到"与"测出坏"不可分；建议改判`不可测`。

---

## 12. 交付与取证件清单（本车道产物，全在临时区或本件）

| 件 | 用途 | 是否入库 |
|---|---|---|
| `docs/_working/fullflow_campaign/lanes/census_reverify_EFGHI.md` | **本件（成品）** | 本车道 `git add`，提交经总包/队列 |
| `.runtime/tmp/st-ff-rv3-20260918/agg.json` `bm_steps.json` `census_db.json` | 三探针重跑实测 | 临时件，不入库 |
| `.runtime/tmp/st-ff-rv3-20260918/rv_tables.py` `.py` `h_family.json` `h_index_universe.json` | E/F/H 族专用只读探针 | 临时件，不入库 |
| `.runtime/tmp/st-ff-rv3-20260918/04_sixway_ledger.md` + `04_sixway_machine_ledger.yaml` | **旧 392KB 台账备份**（md5 `40bd8e2d…` / `38f24981…`） | 临时件，不入库 |
| `.runtime/tmp/st-ff-rv3-20260918/verifier_all.log` | 尺子 `--all` 全量运行日志（含 12 次 CH 失败原文） | 临时件，不入库 |

**红线自查**：未改 `src/**`、`scripts/**`、config、任何注册表；未碰 `ruling_registry.yaml`；
未取裁定号、未建任务条目；未提交 `04_sixway_ledger.md`/`.yaml`（遵 z-verifier3 硬指令，入库与否由总包裁）；
未跑任何带 `--apply/--mirror` 的生成器（跑前已 `--help` 读 argparse 真接口）；
DB 全程经 `get_depgraph_pg_connection(read_only=True)`，禁裸 duckdb；
`.runtime/tmp/ff-mine0/` 原件**未被覆写**（本车道用路径改写副本，改前改后 md5 留档：
`dg_agg.py ce8e6f7d…`/`dg_bm.py d7464b61…`/`dg_census.py 87cf4d41…`、
`agg.json eca0f73c…`/`bm_steps.json fa1de224…`/`census_db.json a2cc7b3a…`）；
无破坏性 git；项目根零临时文件。

**入库状态（须总包处置）**：本件 `git add` 已完成（`git ls-files --cached` 可证，暂存态 `A`），
但 `git_commit.py --session st-ff-rv3-20260918 --files <本件> --enqueue --allow-non-worktree`
**在锁外预检被 `[SESSION-REQUIRED]` 阻断**——本复测车道从派工到执行未走 `session_worktree_start`，
session 未注册。本车道**未伪造逃生通道**（`allow_overlap` 会在 message 打 `[GW:<sid>:overlap]` 审计标记，
属治理副作用，越"只读复测"边界；且此刻 index 内叠着 22–29 件**他会话 staged 文件**，
正是宪法 §2.5/§3 所述 FOREIGN_CHANGE 连坐窗口），故按红线停手如实上报。
→ **总包二选一**：① 为本车道补注册后由队列落地（`commit_queue.py` 正门，serializer worktree 干净暂存区）；
② 由总包以自家 session 直接吸收本件入库。message 稿留档
`.runtime/tmp/st-ff-rv3-20260918/commit_msg.txt`（失败保留，可直接重跑同一命令）。
**风险提示**：本件目前仅"已暂存"未"已提交"——若后续他车道 `git stash`，暂存态成品有被卷入的前科（R-042）。
