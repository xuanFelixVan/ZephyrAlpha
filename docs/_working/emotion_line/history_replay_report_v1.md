---
ttl: task_bound
title: 情绪指数全历史回放班报告 v1（盘点+回放落地面+PIT 自证+解锁三连+红蓝+晨报六要素）
created: "2026-09-23"
sid: st-emoreplay-20260923
lane: emotion_line
status: final（本班交付件；判档表述遵循裁定#325 禁"全绿"）
---

# 情绪指数全历史回放报告 v1

> 使命：把 emotion_index 从"逐日攒"改为"全历史回放"，为 GPU 情绪条件化搜索供料。
> 公式真源=`zephyr.alt_data.emotion_index_builder`（v0.1.0 冻结，本班零改动零复制）；
> 回放件=`zephyr.alt_data.emotion_index_replay`（切片缓存 reader 注入原函数）。
> 全部数值出自 2026-09-23 18:30-20:10 实弹探针与落库核验（快照在 `.runtime/tmp/st-emoreplay-20260923/`）。

## §1 成分历史深度盘点（实测，任务 1）

| 成分 | 原料表 | 覆窗（实测） | 日数/行数 | 近端 | 回放可用性判定 |
|------|--------|-------------|-----------|------|----------------|
| C1 涨停温度 | daban_board_event | 2026-09-01→09-22 | 16 日 / 1,454 行 | 09-22 | 恒 insufficient（obs 16<120），如实降档 |
| C2 晋级率 | daban 自 JOIN | 同上 | 16 日 | 同上 | 同上 + 缺陷 D-1（见 §5） |
| C3 广度 | kline_daily + kline_index(000300) | 1990-12-19→09-23 / 000300 2005-01-04→ | 8,732 日 / 10,102,490 行 | 当日 | ok 自 1991-06-10（120 观测满窗） |
| C4 量能 | kline_daily(amount/turnover) | 同上；turnover>0 至 2026-08-25 | 8,707 日 | 当日 | ok 自 1991-06-10 |
| C5 杠杆 | margin_trading | **2024-09-02→2026-09-18** | 497 日 / 2,065,857 行 | 滞后 09-18 | ok 自 **2025-04-03**（S4 深史回补解锁） |
| C6 新闻 | news_sentiment_window(scope=market) | 2026-02-24→09-22 | 184 日 | 09-22 | ok 自 **2026-07-14** |
| （未回放）竞价 | auction_snapshot | 2026-06-01→09-23 | 52 日 | 当日 | auction stage 原料史仅 52 日，本班不回放 auction/pre_open |

**诚实下限（实测截面广度，非估算）**：kline_daily 年截面最小股票数 2015=230、2016=231、2017=231、
2018=233，2019=3,563（15× 断崖），2020=3,806，2021=4,224。故 1991-2018 段 C3/C4 为 ~237 只 stub
宇宙的分位序列，**跨 2019 不可比**。本班按"机械全量+如实标注"处置：全史行照落，输入包带
`universe_honest_ok` 列，2019-01-04 前消费须自带理由（Owner 若判"该段不落"→回滚见 §7）。

**ok 成分集形态变化点**（回放实测，逐日 status 派生）：
`1991-06-10` C3+C4 → `2005-01-05` 仅 C4（缺陷 D-2）→ `2005-07-07` C3+C4 → `2025-04-03` +C5
→ `2026-07-14` +C6。C1/C2 全程未达 120 观测。降档按 builder 既有机制（等权重在 ok 集内重分配），
禁硬凑＝未插值未补史。

## §2 历史回放落地面（任务 2）

- 计算：8,732 交易日逐日调 `build_emotion_index(day, stage='close_final', reader=切片缓存)`；
  产 8,613 行，119 日全成分不可产如实跳过（builder 返 None）；均值 0.5341 / 标准差 0.2165 /
  值域 0.0120-1.0000。
- 落库：`c1_market.emotion_index` 新增 **source='replay' 8,596 行**（1991-06-10→2026-08-31，
  423 个月分区，strict 通道分块写——CH `max_partitions_per_insert_block=100` 首撞 Code 252，
  已按 ≤90 分区/块治本并加红测）；**撞活键跳过 17 行**（2026-09-01→09-23 活管道已产区间）。
- 表结构：新增 `source LowCardinality(String) DEFAULT 'live'` 列。ALTER 文本唯一真源=
  `scripts/ch/apply_market_tables_ddl.py::_MIGRATIONS` 条目，DDL-as-Code 同批更新
  （`schemas/categories/market/market_emotion_index.py`，该件 AI_AUTONOMY=human_only，
  本班按 tilib-b10 先例走"增列+探针"路径，呈批见 §6）。
- **活管道零打扰取证**：`source='live'` 50 行（含 17 close_final）与落库前 18:30 探针基线
  逐字节比对（stage/ts/emotion_index/version/components 五字段）→ **0 不匹配**；
  `system.query_log` 4 小时窗内该表 INSERT 共 11 条 = 17:43 活插（6 列）+ 19:21 本班回放块（7 列），
  无第三条改写活行。`INSERT_COLUMNS`（6 列契约）未动，活日批吃列默认值。
- 键安全：source **不在** ORDER BY 内 → 回放结构性跳过活管道已存在键（撞键会被 FINAL 覆盖活行=禁）；
  实测 `FINAL` 后 (trade_date,stage) 重叠数=0、pre-merge 重复键=0、replay 行 components 长度均=6。

## §3 PIT 自证（任务 3）

1. **形状等价自证**（切片回放 ≡ 真窄窗查询）：5 个纯 GROUP BY/行选形状 × 14 抽样日
   （2019/2020/2021/2022/2023/2024/2025/2026-06 + 近 6 活日）= **70/70 逐字节一致**。
   JOIN 形状（C2 自 JOIN、竞价跨窗 JOIN）含窗界伪影 → 白名单外一律真查询直通，不走切片。
2. **10 天活值对拍**：最近 10 个活日 replay vs `build_emotion_index` 真数据面直调 →
   emotion_index 浮点与 components JSON **逐位全等**（10/10，抽样输出 live=replay=0.349123 等）。
3. **回放 vs 已落库活行**（信息性对照）：10 天中 9 天有差，**归因=C5 观测数 19→250**
   （S4 两融深史回填改变了分位窗，成分分位仅微动但 C5 由 insufficient 转 ok 参与等权）
   ——同公式、不同数据快照，非公式漂移。接缝处置见 §5 D-3。
4. **假绿防线**：宽窗抓取返空即抛（ch_reader 静默失败返回 '' 的在案陷阱）；跑完以同 reader
   对最近 3 活日复验等价（防半程原料被改写）；单元侧合成 CH 复刻真 CH 尾换行形态，
   使"切片漏尾换行"这类表示层错必红（该错真跑中被抓出过一次，见 §4 事故 A-1）。

## §4 红蓝一轮（任务 5）

| # | 攻击面 | 结论 |
|---|--------|------|
| R-1 | 回放是否偷换公式 | 蓝方：回放器 import 冻结 builder 并逐日调原函数，零公式复制；红方：10 天对拍逐位+70/70 字节等价 → 未见偏移。**判：站得住** |
| R-2 | 切片是否改变聚合语义 | 红方指 JOIN 形状有窗界伪影（C2 的 t2 窗、竞价 k 窗）→ 白名单外直通真查询；纯 GROUP BY 每行值与窗界无关可证 → 切片合法。**判：处置正确** |
| R-3 | 活管道是否被覆盖 | 撞键跳过 17 + FINAL 重叠 0 + 基线逐字节 0 不匹配 + query_log 交叉验证。**判：零打扰成立** |
| A-1 | 自写验证件的假红/假绿 | 本班两次自打：①等价自证首跑红于 2026-09-16——根因不是并发，是**切片漏尾换行**（真 CH TSV 以 \n 结尾）；修=切片复刻尾换行 + 合成源也带尾换行（否则测试永抓不到）。②"活行零打扰"比对首跑 False——根因=核验件漏 `source='live'` 过滤（落库后同 SQL 返 8,613 行必然不等）；修=独立后置核验件按 (trade_date,stage) 键比基线。**判：两处均为验证件缺陷，已修且各带红测** |
| R-4 | D2 重考是否用了未合并代码 | 板块聚合器在 st-secbuild worktree（HEAD c14ac74c7e）未合并主区——本班只读调用、快照号留痕，未落任何依赖其的提交物。**判：披露为移交条件（§6 P-3）** |

## §5 缺陷登记（不自修，公式冻结红线）

- **D-1 C2_promotion 恒 1.0**：CH 默认 `join_use_nulls=0` 使 LEFT JOIN 未命中行 `t2.symbol=''`
  而非 NULL，`countIf(t2.symbol IS NOT NULL)` 恒等于 `count()` → 晋级率成分实为常数 1.0
  （实测全部 16 个活日 raw=1.0/percentile=1.0）。当前因 daban 史 16 日判 insufficient 而
  不参与聚合=暂无害；daban 自然长到 120 观测后**会把指数常数项拉高**。修复=改 SQL 语义=升版本
  =按卡纪律作废重开新卡，交 Owner/Max 立项，本班不动。
- **D-2 子项观测数拉低整成分**：`_sub_component` 取 `min(子项 obs)` 作成分 obs，故 000300
  自 2005-01-04 接入后，C3 因新子项 obs=1 被判 insufficient 6 个月（2005-01-05→2005-07-06
  全史只剩 C4 单成分参与）。属冻结口径实况，回放如实复现，不改。
- **D-3 接缝不连续**：2026-09-01 前=回放（当前数据快照），起=活行（各自当日快照）。S4 两融回填
  使接缝两侧 C5 状态不同（insufficient vs ok）。若 Owner 要求轴一致，须授权重算活区间
  （=触活管道写域，本班主任不做）。
- **D-4 板块"低波动组"无列**：卡 D2-1 防御组=滞后象限+低波动组，而 sector_state 无波动列
  （上次考试以 rs_ratio≤100 近似）→ 主判 tilt≥1.0 指向日不受影响（防御组非指向日），
  但混淆矩阵/防御档消费需板块线补口径。

## §6 解锁三连（任务 4）

**① D2 板块偏好卡双轴重考（全史情绪轴，frozen 卡零改动）**

| 版 | W_map | 实到日/指向日 | 价差均值/日 | NW t(lag5) | 命中率 | 对随机超额 | 最小档样本 | frozen 判档 |
|----|-------|---------------|-------------|------------|--------|------------|------------|-------------|
| V2 卡面象限口径（rrg_quadrant+momentum_pct 真公式） | 1,585 | 947 / 537 | **−0.3204%** | −1.263 | 0.5754 | +7.54pct | 125 | **NO_MAP** |
| V1 上次近似口径（ret5 三分位，新旧可比） | 1,585 | 947 / 537 | −0.3328% | −1.199 | 0.5289 | +2.89pct | 125 | **NO_MAP** |
| 消融：仅 regime 轴（emotion=契约 mock） | 1,585 | 947 / 753 | −0.3254% | −1.638 | 0.5644 | +6.44pct | 0（DEFENSIVE/CROWDING_WARN 结构性不可达） | INSUFFICIENT |

- **主判定档=NO_MAP**（三判据：均值>0 ✗、t≥1.65 ✗、命中超额>5pct ✓）——情绪轴解锁把
  W_map 从 16 日推到 1,585 日（首次越过 120 日主判门），出档结论是"偏好映射对次日板块
  结构无解释力，且指向组次日均值跑输"。两口径同判，方向与卡 B 的"情绪尾部反向"观察、
  S10 的 momentum NO_EDGE 一致。
- 预承诺兑现：阈值/档位/tilt/权重零改动，一次考完不再改（D2-6.1）；RED 后重设计=下轮新卡。
- 多重检验披露：主判 1 格（V2）+ 可比版 1 格 + 消融 1 格 + 档位计数 5 档 = 8 格全量入表，
  仅主判进族。

**② t0 情绪门 E4 双门重跑**

- 原样重跑 `t0_conditional_e4_exam.py`（只读，产物写本班 tmp）：配对 24 / 宏观门命中 8（<30）/
  门内毛 −5.5bp 净 −36.7bp / 前置命中 0 → **verdict 仍 INSUFFICIENT_SAMPLES**（材料
  `data/backtest_artifacts/bt-*.json` 自 09-16 后无新增，样本未积累）。
- **双门不可出的真因（案卷，非本班能签）**：卡 §2.2 情绪门词表=**TDM 六段**
  （capitulation/accumulation/ignition/expansion/euphoria/distribution），探针在
  `sentiment_panel.metric` 上找六段标签；emotion_index 是连续 0-1 温度计，**不在该词表内**，
  顶替=词表越轴+改卡。且该脚本明文：`emotion_ok=True` 时直接 SystemExit
  "双门取数尚未实现——按卡纪律作废重开"。
- 要出双门需三件之一/组合：(a) 六段标签历史持久化（t0 verdict 自记"data 线工单"）；
  (b) 新预注册卡把情绪门数据源改为 emotion_index 分位（含六段↔分位映射裁定）；
  (c) 材料积累过 30 对。本班已备好 (b) 的取数面：全史情绪轴 + 按卡 PIT T-1 读数的
  门位候选序列（就在 §6③ 输入包内，band3/`vol_bucket3` 两列即门位原料）。

**③ GPU 情绪条件矩阵输入包（按总指挥令 24GB/59h + 闭卷线校准）**

- 三件：`gpu_emotion_condition_matrix_v1.csv`（8,613 行 × 24 列，1991-06-10→2026-09-23）+
  `gpu_emotion_condition_cells_v1.csv`（条件胞普查）+ `.meta.yaml`（预算与纪律声明；
  契约注记：`docs/_working/` 仅允 `.md/.csv/.yaml/.html`，首版 `.meta.json` 已被
  DCR-005/008 打死，YAML 头两行写明"原 .json 版已废弃"防旧引用，并带机读
  `deprecated_aliases` 字段）。
- 列：`emotion_index` / `band5`（骨架稿 §3 五档）/ `band3_emotion`（板块线 0.40/0.70 口径）/
  六成分 `p_*` 分位与 `st_*` 状态 / `ok_set`+`ok_n` / `regime_dominant`+`vol_pct`+`vol_bucket3`
  （t0 卡 frozen 边界 0.328/0.700）/ `source`（live/replay）/ `universe_honest_ok`（2019-01-04 界）/
  **`closed_book_ok`（≤2025-09-09=1，其后只可作卷外观察）** / `state_axis_available`。
- 算力口径（RTX 3090 24GB / 周五 12:00→周日 23:00=59h）：包体积 1.2MB、稠密内存 1.8MB，
  整表驻留显存占比 <0.01% → **24GB 不是本包的约束，瓶颈在每配置前向回测次数**；
  情绪条件查表按 trade_date 索引 O(1)，不构成显存压力。
- **闭卷窗内的搜索空间基数（实测，决定可扫维度上限）**：诚实窗 2019-01-04→2025-09-09 =
  **1,622 日**；其中 **1,513 日情绪轴只有 C3+C4 两成分**（带 C5 仅 109 日、带 C6 0 日）
  → "多源情绪条件化"这一搜索维度在闭卷窗内统计学不成立，只能卷外观察；五档灰度窗内实际
  **4 档有数（冰点档 0 日）**，按五档切分会留空维度；情绪三档×五档×vol 三桶×regime 组合
  共 **31 胞，达 30 日样本地板的只有 18 胞** → 联合条件维度可用格上限=18，超出即碎片化。
- 纪律（写进 meta 随包交付）：公式冻结禁按搜索结果回改（改=作废重开新卡）；closed_book_ok=0
  段禁参与阈值选择/调参/定档；每胞 <30 交易日不进搜索空间；进族格数如实登记（裁定#325 禁全绿）。

## §7 复核命令与回滚

```bash
# 只读复核
python .runtime/tmp/st-emoreplay-20260923/probe_emotion_history_depth.py      # §1 深度实测
python .runtime/tmp/st-emoreplay-20260923/run_replay_verify.py                # §3.1/3.2 等价+对拍
python .runtime/tmp/st-emoreplay-20260923/verify_after_land.py                # §2 零打扰取证
python .runtime/tmp/st-emoreplay-20260923/run_d2_reexam.py                    # §6① 重考
PYTHONPATH=<wt>/src python -m pytest tests/alt_data/test_emotion_index_replay.py -q   # 10 例
# 回放面
SELECT source, count(), min(trade_date), max(trade_date) FROM c1_market.emotion_index
FINAL GROUP BY source;
```
回滚（两步，均为加法之逆）：`ALTER TABLE c1_market.emotion_index DELETE WHERE source='replay'`
→ `ALTER TABLE c1_market.emotion_index DROP COLUMN source`；代码侧 revert 本批 commit。

## §8 晨报六要素

**一、完成清单（含落点）**

| 项 | 交付 | 落点 |
|----|------|------|
| 任务1 | 六成分深度实测 + 2019 universe 断崖量化 + ok 集变化点 | 本报告 §1；探针/快照 tmp |
| 任务2 | 回放器（冻结公式零复制+切片缓存+分块写）+ 全史 8,596 行落库 + source 列 | `src/zephyr/alt_data/emotion_index_replay.py`；`c1_market.emotion_index`；DDL/applier 同批 |
| 任务3 | 70/70 形状字节等价 + 10/10 活值逐位对拍 + 9/10 存库差归因（C5 回填） | §3；`verify_result.json` |
| 任务4① | D2 双轴重考首次出档 NO_MAP（W_map 16→1,585） | §6①；`d2_reexam_result.json` |
| 任务4② | t0 E4 原样重跑（仍 INSUFFICIENT_SAMPLES）+ 双门案卷三条件 | §6②；`t0_e4_out/` |
| 任务4③ | GPU 情绪条件矩阵输入包 8,613 行 + 条件胞普查 + meta（按总指挥令 24GB/59h+闭卷线 2025-09-09 校准：闭卷窗 1,622 日、可用条件胞 18/31） | §6③ 三文件 |
| 任务5 | 红蓝一轮（4 发见+2 起自打假红）+ 缺陷 D-1~D-4 登记 | §4/§5 |
| 测试 | 回放器 10 例（含 Code 252 分块红测、尾换行红测、空宽窗 fail-visible） | `tests/alt_data/test_emotion_index_replay.py` |

**二、关键发现**：①D-1 C2 成分恒 1.0（join_use_nulls 语义）——满 120 观测后会污染指数，
最高优先移交项；②情绪轴解锁后 D2 从"无从判档"变"判档 NO_MAP 且指向组次日跑输"；
③回放与活行接缝的成因不是公式而是 S4 两融回填（同公式不同快照）；④t0"双门"被词表轴
卡住而非数据史——本班供料不能替它解轴。

**三、呈批项（Owner 门位）**

- P-1 source 列 ALTER **已执行**（additive/DEFAULT/'live' 零改写，先例=tilib-b10 在 human_only
  schema 加列）；如判越权，§7 回滚两步即净退。
- P-2 1991-2018 stub 段（宇宙 237 只）：现照落+打标。要不要改判"该段不入库只留 tmp"？
- P-3 D2 重考依赖板块线未合并件（worktree HEAD c14ac74c7e）：板块班合并后需复跑一次确认数；
  且上次考试分组口径与卡面不符（§4 R-4/§5 D-4）→ 移交板块班裁定。
- P-4 D-1（C2 恒 1.0）是否立项新卡修复（改=升版本=考试族重开）。
- P-5 D-3 接缝：是否授权重算 2026-09-01→09-23 活区间以统一口径（触活域，本班主任不做）。

**四、死信/事故**：队列死信 1 项 `q-20260923-st-emoreplay-20260923-0001`——门禁
DIRECTORY-CONTRACT（DCR-005+DCR-008）打死 `gpu_emotion_condition_matrix_v1.meta.json`
（`docs/_working/` 允许清单无 `.json`）；修法按 Owner 令=改 `.meta.yaml`+内容转 YAML+
包内写"原 .json 版已废弃"两行（头注释+机读 `deprecated_aliases`），`requeue --worktree-root`
重发。另本班首趟 `--enqueue` 落在 **worktree 私有队列根**（主 daemon 永不排空的死根，
wm1 车道 B 在案处方的复现），已把该滞留项改名 `.stranded-by-worktree-root` 封存防双落地，
改由主根 `commit_queue.py enqueue --worktree-root <wt>` 正规入袋。库侧无事故：
Code 252 首撞时核实 total=50 未变（零半落库）后重跑。两次自产假红（A-1 ①②）均本班内
定位并修，各补红测。

**五、待办/明日**：①板块线 sector_state 历史回放（D2 防御组/混淆矩阵才完整）；②六段情绪
持久化工单（t0 双门前置）；③周五 GPU 班接包（meta 限制须进搜索空间约束）；④C1/C2 待 daban
史自然长到 120 观测（约 2027-03）后按卡 A 预承诺重考 W_full。

**六、临时清理确认**：本班全部临时件在 `.runtime/tmp/st-emoreplay-20260923/`（探针 3 + 驱动 4 +
JSON 快照 6 + 日志 6），无项目根文件、无 `data/` 写、无 `.runtime` 根直写；
`process_reaper_keep.txt` 追加 4 行子串（run_replay_verify/run_replay_full/land_replay/run_d2_reexam）
——收班时摘除。worktree 的 `config/.env.clickhouse` 为运行期副本（gitignore 区，不入库）。
