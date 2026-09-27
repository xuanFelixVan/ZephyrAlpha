---
ttl: task_bound
completes_when: "波10 底数复核机读表+G-A 接线件与消费面反查证据+G-B/G-C 缺口案卷三件随袋落地"
---

# 波 10 施工案卷 · 底数复核 / G-A 接线 / G-B·G-C 缺口（W-117 终审版）

- turn_budget: 派单口径=8 次调用内出骨架（本队第 11 次调用落骨架、第 12–17 次生成并跑通底数件与接线件、第 18–22 次定点补数）；单块调研 ≤6 次；后期只落盘。全程零 commit/零 add/零 enqueue/零点火。
- verified（本袋实测，命令见 evidence_ref）:
  - `src/zephyr/signal_ashare/` 实存 .py = **154**（其中 `strategy_signal/` 子簇 **19**，其余簇 **135**）；案卷"62 模块"口径**不可复现**（见 §1.4 数字更正）。
  - 三簇**全部 154/154 在 HEAD**（`git ls-tree -r HEAD` 命中，分支 `session/st-final-build-20260926`）。
  - 生产路径消费（运行时 import 闭包判定）：簇 core **21/135 接**、簇 chain **2/19 接** → 两簇合计 **23 件真在生产路径**。
  - 蜡烛目录三面一致：**在册 83 行**（chart_pattern_registry `pattern_id: "PAT-CANDLE-*"` 去重=83、行数=83）｜**talib CDL 实枚举=61**｜**scanner 源码静态 id 字面量=23**（PAT-CANDLE-001 + 062..083=16 手写+6 Bulkowski）→ 61 动态 + 22 手写 = **83 成立**。
  - 冻结件 diff：`config/search_space_prereg.yaml`/`exam_scale_cost_gate.yaml`/`config/flags.yaml` **全部 clean_diff_zero**（本袋未改一字）。
  - G-A.2 接线件离线红证五条全红（见 §2.4 读数）。
- assumed（未实测，禁作判据）:
  - `scripts/script-manifest.yaml` 在册行仍写"共 77 条 PAT-CANDLE 目录"（=2026-09-15 增补前口径），本队**未改热册**，仅登记更正。
  - `pattern_event_job` 内部以 `subprocess` 外调（实现在 `zephyr.data.implementations.internal_compute_provider` 委托链上）：import 闭包=可达，**实际执行态未运行验证**（禁据本表宣称"已跑通"）。
  - "62" 可能出自某注册表口径；本袋在 `module_translation_registry.yaml` 实测 `MOD-SIG-*` 去重=**38**、`module_id: MOD-SIG-` 行=16，两者均≠62 → 未检索到可复现 62 的机械口径。
- input_set_disjoint_with: 波 2 车道树；波 3–6（治理/灾备/数据链）；本袋写入面仅 `scripts/governance/wave10/` + `scripts/signals/` + `docs/_working/total_command_closeout/wave10/`；未触碰 `docs/01_policies_and_standards/**`、`config/**`、任何阈值/断言/skip/xfail、任何 prereg。
- evidence_ref.cmd:
  - `find src/zephyr/signal_ashare -name "*.py" -not -path "*__pycache__*" | wc -l` → 154
  - `find src/zephyr/signal_ashare/strategy_signal -name "*.py" -not -path "*__pycache__*" | wc -l` → 19
  - `python scripts/governance/wave10/wave10_asset_base_audit.py` → 机读表 `docs/_working/total_command_closeout/wave10/wave10_asset_base_audit.yaml`（簇×三列+逐件 verdict+蜡烛三面+冻结 diff）
  - `python scripts/signals/chart_condition_package.py --selfcheck`（离线构造数据红证，零库零点火）
  - 消费面反查（人工复核用）：`git grep -ln "candlestick_scanner\|unified_pattern_engine\|pattern_event_store" -- src scripts`

---

## §1 底数复核（三簇 × 三列，机读表=`wave10_asset_base_audit.yaml`）

在册判据（本袋执行口径）：**装饰性接线一律判未接** —— 仅 `TYPE_CHECKING` 边 / 仅簇内互引 / 仅被包 `__init__` re-export / 仅脚本或测试消费，均不算接。生产闭包=自 `zephyr.trading|zephyr.data|zephyr.frontend|zephyr.orchestrator|zephyr.runtime` + 具名跑批入口（`scripts.backtest.factory_grid_executor`、`scripts.backtest.f06_e4_wfa_exam`、`scripts.compute_signals`）沿**运行时** import 边可达集（实测闭包含 1,308 模块，全仓扫 4,908 模块）。

### 1.1 簇汇总表

| 簇 | 范围 | 实存模块数 | 在 HEAD | 生产路径消费（真接） | 未接细分 |
|---|---|---|---|---|---|
| C1 图形核簇 | `zephyr.signal_ashare.*`（除 strategy_signal） | **135** | 135/135 | **21** | off_prod_path 46 ｜ orphan 68 |
| C2 形态链路簇 | `zephyr.signal_ashare.strategy_signal.*` | **19** | 19/19 | **2** | off_prod_path 13 ｜ orphan 4 |
| C3 蜡烛目录 | REG-PAT-001 `PAT-CANDLE-001..083` | **83**（在册行数=去重数=83） | 在册件在 HEAD（本袋未逐行核） | 实现主体 `candlestick_scanner` 判 **NOT_CONSUMED_off_prod_path**（唯一入边=包 `__init__`） | — |
| C4 本袋新建 | `scripts/signals/*` + `scripts/governance/wave10/*` | 2 | 0/2（禁 commit，未入库） | 0（import 可达面待总包排产同批） | orphan 2 |

### 1.2 C2 关键件 verdict（"缺口是接线不是建库"的实测支撑）

- 真在生产路径的 2 件：`pattern_event_job`、`strategy_decay_certifier`（入边=`zephyr.data.implementations.internal_compute_provider` 委托 `run_incremental`/`run_win_rate_materialize`/`run_weight_sync`/`run_evidence_certify`）。
- 判未接但被簇内互引拖着的（典型装饰性接线）：`candlestick_scanner`、`pattern_event_store`、`unified_pattern_engine`、`pattern_win_rate_provider`、`pattern_to_signal_mapper`、`pattern_signal_runtime`、`series_transform`、`signal_factory`、`signal_weight_adjuster`、`pattern_evidence_certifier`、`pattern_lifecycle`、`strategy_vote_integrator`、`dual_engine_fusion_decision_engine` —— 入边全部来自 `zephyr.signal_ashare/__init__`、`strategy_signal/__init__` 或同簇互引，闭包无生产根。
- 真孤立（零入边）：`strategy_signal`（包本体）、`pattern_match_strategy_library`、`strategy_cross_vote_funnel`、`strategy_matrix_3d`（18 格三维矩阵＝**零消费**，与案卷"18 格矩阵"叙述同物，但按 §4 内收判据属"零触发零消费"候选）。

### 1.3 G-B/G-C 锚点件 verdict（本袋实测，逐件）

| 锚点件 | 实存 | verdict |
|---|---|---|
| `trendline_sr_detector` | 在 | NOT_CONSUMED_off_prod_path（唯一入边=`strategy_signal.unified_pattern_engine`，该入边自身未接） |
| `chanlun_structure` | 在 | NOT_CONSUMED_off_prod_path（同上） |
| `false_breakout_trap_detector` | 在 | NOT_CONSUMED_off_prod_path（入边=`zephyr.signal_ashare/__init__`） |
| `auction_microstructure_analyzer` | 在 | NOT_CONSUMED_off_prod_path |
| `limit_up/`（9 .py） | 在 | 6 件 orphan（含 `limit_up_followthrough`/`seat_pattern_analyzer`/`war_pool_generator`/`lhb_premium_analyzer`/`limit_up_reason_attribution`/包本体）；3 件 off_prod_path（`limit_up_ecosystem_leadership`/`limit_up_potential_scorer`/`youzi_relay_emotion_engine`） |
| `candlestick_scanner` | 在 | NOT_CONSUMED_off_prod_path |

三件的 `[CONSUMERS]` 头注本身即写"（候选：…叠加层/门槛）"，MATURITY=testing —— 与机械判定一致，非推断。

### 1.4 数字更正项（案卷/在册 ↔ 实测，本队不改热册，仅登记）

1. ext_01/ext_02"62 模块" → 实测 154 文件（135+19）；未检索到可复现 62 的机械口径 → **案卷数字按不可复现处理**。
2. `scripts/script-manifest.yaml` "CDL 61 + extras 16（共 77 条）" → 现态 extras=22（16+6 Bulkowski）、目录=83 → 在册行漂移（更正须走热册批次，非本包）。
3. ext_01 G-B.2 "几何形态族现全缺位（83 条全是蜡烛形态）" → **半对半错**：`chart_pattern_registry.yaml` 在册非蜡烛族 = `chart_pattern` 81 行 / `trendline_channel` 13 行 / `support_resistance` 10 行 / `structure` 59 行（PAT-STRUCT-* 46 去重）/ `chanlun` 15 行 / `fibonacci` 18 行（registry `entry_count: 287`）。缺的是**实现钩子与接线**（每个非蜡烛 id 前缀在 `src`+`scripts` 仅 1 个文件命中），不是目录行 → **G-B.2 施工面必须改为"在册 81 chart_pattern 行的实现落地+接线"，禁再新增重复目录行**（AGENTS §4 全资产净零/内收铁律；§14 裁定口径）。
4. 本袋未发现任何"在册判据阈值"需改；红证自检全部离线构造数据。

---

## §2 G-A 接线（已落两件 + 消费面反查证据）

立法（写进两件头注 INVARIANTS 首条）：**图形信号只作考试条件轴，禁作独立信号**（Marshall 2006 证伪基线，出处=`final_review_chartlib/dossier_academic_papers.md` §1.1，本袋 grep 命中）。

### 2.1 G-A.1 盘点/底数件（生成器，非静态清单）

- `scripts/governance/wave10/wave10_asset_base_audit.py` → 输出 `docs/_working/total_command_closeout/wave10/wave10_asset_base_audit.yaml`。
- 出口判据对齐：逐件 `path`+`in_head`（HEAD 命中即 `git ls-tree` 实测）、`verdict`+四类消费者清单（即"消费面反查证据"）、蜡烛目录三面对账、`frozen_files_diff`。不落库/未接件**单独成列**（`NOT_CONSUMED_*` 三档 + orphan），无漏登。

### 2.2 G-A.2 图形条件包（新建，同族复用不造第二套轴）

- `scripts/signals/chart_condition_package.py`：三轴胞 `cell_id = c<图形标签>|g<灰度档>|s<状态档>`；灰度/状态一律**消费** `zephyr.backtest.regime_validation.condition_package` 产物（`ConditionPack.frame`），本件禁重算禁扩窗；地板 `_CELL_FLOOR_DAYS` 由该件 import（**唯一真源，禁自带数值**）；未达地板 → `cell_id=None` 下沉 conditional-free。
- 图形标签口径封闭可复算：单日事件按 `direction` 归一（bull/bear/neutral 三集，未知字面量即抛），bull>bear→`bull`、bear>bull→`bear`、相等且>0→`mixed`、无事件→`no_event`；中性计数单列不入方向比较（沿用胜率 NULL 语义）。
- 事件输入契约=`market_pattern_event` 的 `INSERT_COLUMNS`（`schemas/categories/market/market_pattern_event.py` 实测列集：event_id/pattern_id/pattern_class/direction/confidence/timeframe/symbol/anchor_trade_date/confirmed_at/name/key_points/regime_tag/scan_run_id/data_source）；**本件零写库**，写入仍归 `pattern_event_store` 单一写者（波 10 红线 3）。

### 2.3 G-A.3 胜率接线（零 schema 改动）

- `cell_win_rate(provider, cell_id=…, pattern_id, timeframe, direction, fwd_window, baseline=False)` → 注入式调 `pattern_win_rate_provider.get(...)` / `get_baseline(...)`，把图形条件胞 id 作 `regime_tag` 传入（schema 已预留 timeframe+regime_tag，实测确认）；`__baseline__` 对照行由 `get_baseline` 既有路径给出。
- 契约保持：查无/样本不足 → **None**（红证 4）；数值类型校验禁"字符串按下标取值"（W-180 红线口径）。
- 未改 `pattern_win_rate_provider.py` 一字（避免 MODIFY-GUARD/阈值面）。

### 2.4 G-A.4 接入点声明 + 红证读数（本袋实跑输出）

- 声明：图形条件轴=**新预注册族**（G-D.1 `config/chart_resonance_prereg.yaml`，本袋**未建**，须走 creation_token + 总包排产），不进 T1/T2 冻结轴。实测 `git diff HEAD -- config/search_space_prereg.yaml`/`exam_scale_cost_gate.yaml`/`config/flags.yaml` = 空（audit yaml `frozen_files_diff: clean_diff_zero`）。
- `python scripts/signals/chart_condition_package.py --selfcheck` 读数（构造数据 120 交易日，零库零点火）：
  - `cells_recomputable: OK cells=6 eligible=2`
  - `red_lookahead_event: OK(前视事件 5 行：confirmed_at 晚于 anchor_trade_date…)`
  - `red_wrong_state_label: OK(状态字面量越界 ['涨停板状态']…)`
  - `red_standalone_signal_usage: OK(图形条件轴产物含独立信号列 ['signal']——违反立法…)`
  - `red_none_not_zero: OK`
  - `red_floor_gate: OK(eligible=2 insufficient=3)`（10 日薄样本判 INSUFFICIENT-N，不当独立样本）

### 2.5 本袋接线的诚实边界

接线件当前 verdict=`NOT_CONSUMED_orphan`（audit yaml C4 行）：**已交付 importable 接线面与红证，未接进任何跑批入口**（禁点火=本包硬约束；G-D 逐格引擎未建、prereg 未建、`factory_grid_executor` 未改）。G-D 消费面落地与 promote 到 `src/zephyr/backtest/regime_validation/` 同批义务（模块号登记、翻译登记、depgraph 节点、creation_token）列入 §5 待排。

---

## §3 G-B 缺口案卷（趋势线通道／几何形态族／A 股事件轴）——只出方案不出码

### G-B.1 趋势线/通道

- 已有：`trendline_sr_detector`＝分形极值(±k 满窗)＋价位聚类(容差%=强度)＋两同向极值连线，支撑/压力取现价上下最近位；`false_breakout_trap_detector`＝N=3 日回落封闭规则＋诱多三特征 40/35/25；两者**均在 HEAD、均未接**（§1.3）。
- 缺：①多触点拟合（枢轴穷举；RANSAC 弃用＝终审裁定，出处 ext_02 G-B.1；备选 Hough，出处 `dossier_github_ecosystem.md` §五）②上下轨通道 + 平行容差 ③通道↔假突破的在册接线（现两件互不成轴）④反弹次数加权 + 时间衰减（Chung & Bellotti 两规律，arXiv:2101.07410，出处 `dossier_academic_papers.md`）。
- 最小施工面：新件 `scripts/signals/trendline_channel_v2.py`（多触点+上下轨+衰减评分，旧单线输出作 legacy 对照列）；**不改** `trendline_sr_detector` 现有聚类容差（阈值面）；通道标签以 `chart_label` 新枚举值接入 §2.2 三轴包（`c<trend_dn_upper>` 之类），事件落库仍走 `pattern_event_store.build_event_rows`；红证三例=通道判定/假突破/衰减加权 + 新旧对拍 + Owner"15 分钟下降通道上沿"构造数据用例。
- 前视注入位：**G-B.1-A** 枢轴"满窗"右侧确认——极值须右侧 k 根才可知，若把线有效性起点记为枢轴当日即前视（应记确认日收盘）；**G-B.1-B** 聚类容差/ATR 归一若用全样本统计＝未来函数（须滚动窗）；**G-B.1-C** 假突破 N=3 日"已决"判定天然滞后 3 日，未决 pending 若被当结论消费即前视。

### G-B.2 几何形态族

- 已有：在册 `chart_pattern` 81 行 + `trendline_channel` 13 行 + `support_resistance` 10 行（`chart_pattern_registry.yaml`，`entry_count: 287`）；实现主体仅蜡烛（`candlestick_scanner`）；非蜡烛 id 前缀在 src+scripts 各仅 1 文件命中（承载件未定名，待总包核）。
- 缺：头肩(正/反)/双顶双底/三角×3/楔形×2/旗/通道(复用 G-B.1)/杯柄的**枢轴序列+几何容差实现**与 `unified_pattern_engine` 注册面。
- 最小施工面：**先在既有 81 在册行内挑 ~15 族落地**（ext_01"新增 ~15 形态族"须按净零口径改为"实现+接线在册既有行"；确无对应行才新增，且新增须声明替代/合并旧条目）；几何件独立于蜡烛簇（域不相交），落库走既有事件契约；罕见形态单列（Bulkowski 口径，出处 `dossier_academic_papers.md`/`dossier_institution_practice.md` 命中）。
- 前视注入位：**G-B.2-A** 形态"完成日"口径——颈线/形态右端确认前若把形态起点日记为事件锚点即前视（`confirmed_at` 必须=右端 bar 收盘，沿用 store 头注 PIT 铁律）；**G-B.2-B** ATR 归一容差的全样本分母；**G-B.2-C** 枢轴序列若用未来重标（rebalance）回溯改写历史极值。

### G-B.3 A 股事件轴

- 已有：`limit_up/` 9 件（6 件零入边 orphan）、`auction_microstructure_analyzer`、`chanlun_structure`（PAT-CLL 15 行在册承载）。
- 缺：把上述产物**显式化为事件轴**并登记进底数表（封板/炸板/busted pattern/缠论买卖点，每轴三字段：预期方向/证据出处/持有期口径）；证据命中：Jiang & Li 2026 SSRN 6955939（`dossier_academic_papers.md` §6.5 命中）、Bulkowski busted（同卷 §1.4 命中）、中泰缠论（§6.1 命中，**只作入考资格不作统计豁免**）。
- 最小施工面：一个 `chart_condition_package` 的事件源适配层（把 limit_up/chanlun 产物映射为 `_EVENT_REQUIRED_COLUMNS` 契约），不新增判据、不改任何模块阈值；缠论分型**复用** `chanlun_structure`（禁造第二套极值算法，与 G-C.2 同条铁律）。
- 前视注入位：**G-B.3-A** 封板/炸板状态在盘中未定而收盘后才可判，若用日内某刻状态即前视（须 anchor=收盘）；**G-B.3-B** `limit_up_followthrough` 类"后续走势"字段天然含未来数据，禁作条件轴输入（只可作结果侧标签）。

---

## §4 G-C 缺口案卷（多周期共振引擎）——只出方案不出码

- 已有：日频两轴条件包（`condition_package`，生产可达）＋本袋三轴图形条件包；蜡烛事件锚点口径 `confirmed_at=bar 收盘（仅已完成 bar）`（scanner 头注实测）。
- 缺（四条）：
  1. **G-C.1 跨周期 PIT 数据层**：全仓无 `merge_asof(direction="backward")` 的高/低周期贴列件（分钟数据另受 G-E 阻塞）。施工面=一个纯函数层：基础周期=参与周期最低档（freqtrade @informative 律，出处 `dossier_github_ecosystem.md` §四命中）。
  2. **G-C.2 摆动结构双峰检测**：LH/HL 链 + "两次不过前高"（ATR 容差）。施工面=在 `chanlun_structure` 分型之上做摆动高点链，**禁造第二套极值算法**；红证=单调递增序列判双顶必红。
  3. **G-C.3 共振条件对定义器**：首批 `15M 触及下降通道上沿 AND 1M 双峰不过前高 → 预警`，四字段登记进底数表（事件 id/两腿定义/确认时点/失效条件）。
  4. **G-C.4 lead-lag 观察轨**：滞后相关矩阵 + FDR + 分窗稳定性（Curme 2015 / Fang 2025，出处 `dossier_academic_papers.md` §3.1/§3.3 命中）；结论无论正负入负结果台账口径。
- **前视风险注入位（点明 6 处，逐条带红证设计）**：
  - **L1** `merge_asof` 边界：高周期 bar 收盘时刻 == 低周期行时刻时，`allow_exact_matches` 默认 True → 同刻可见"刚收盘"值，实为 T+0 信息泄漏；红证=注入该 bar 的未来 OHLC 必红。
  - **L2** 高周期列 partial bar：未收盘的高周期 bar 参与贴列（聚合窗右端未闭）＝直接前视；必须只贴 `is_closed=True` 的高周期行。
  - **L3** 误用 `merge`/`join` 或 `method="nearest"/"forward"` 替 backward（forward fill 会向过去填未来值）。
  - **L4** 基础周期取高档（如以 15M 为基）→ 1M 信息被下采样掩盖，事件确认时点前移。
  - **L5** 双峰检测极值标记日=枢轴当日而非右侧确认日（G-B.1-A 同源）；`confirmed_at` 必须=确认 bar 收盘。
  - **L6** 逐格收益窗（G-D.2）以信号日收盘价为起点＝同 bar 成交前视；沿用案卷 §七已标注的 alphalens `shift(1)` 陷阱口径（`dossier_github_ecosystem.md` 命中）。
- 本袋**未写任何会真跑矩阵的代码入口**；G-D 只能 READY_NOT_FIRED（本包范围外，未触碰）。

---

## §5 红线自查 / 未落项

- 零 commit、零 add、零 enqueue、零点火、零删除、零 DDL/UPDATE/DELETE；无任何数据库访问（两件均注入式输入，底数件纯 AST+git 只读）。
- 未改：`config/search_space_prereg.yaml`、`exam_scale_cost_gate.yaml`、`config/flags.yaml`、任何阈值/断言/skip/xfail、`docs/01_policies_and_standards/**`、`strategy_signal/*` 任何件、`condition_package.py`。
- 外部引用全部经本仓案卷 grep 命中才落笔（arXiv:2101.07410 / SSRN 6955939 / Marshall 2006 / Curme 2015 / Fang 2025 / Bulkowski / freqtrade / pytrendline·Hough / zig-zag·HHMM / alphalens shift(1)）；**未检索到**：可复现"62 模块"的机械口径（见 §1.4）。
- 待排（禁自赋裁定号，只列项）：①新 .py 的 creation_token / 翻译登记 / depgraph 节点（须热册批次，本包无权）②接线件 promote 至 `src/zephyr/backtest/regime_validation/` 的同批义务 ③`chart_resonance_prereg.yaml`（G-D.1）与逐格引擎（G-D.2）④§1.4 三条数字更正入册 ⑤在册非蜡烛形态 id 的实现承载件定名（本袋仅计数未逐行核）。
- 观察（非本袋所有，按"他会话在途违规不代修"上报不动手）：索引中已存在 `docs/_working/total_command_closeout/wave1b/dead_letter_census.py`、`wave2/lane_inventory.py` 两个 `docs/_working/` 下 .py（DIRECTORY-CONTRACT DCR-005 面），状态 AD，本袋未删除未改动。
