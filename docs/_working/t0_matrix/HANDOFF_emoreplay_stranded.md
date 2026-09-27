---
ttl: task_bound
title: 移交包 · st-emoreplay-20260923 滞留交付件（本包不代接，附完整判据与闸位）
sid: st-t0-matrix-20260924
created: "2026-09-24"
lane: t0_matrix
status: handoff-open
---

# 移交：emoreplay 班滞留交付件（为什么不在本包落地）

## 1. 事实基线（本班实测，非引用）

- 产线 `c1_market.emotion_index`：**8,647 行** = `source='replay'` **8,596 行**（1991-06-10→2026-08-31）
  + `live` 51 行；`stage` 仅 `close_final/pre_open/auction`（日内阶段，**非六段相位**）。
- **可复现性已独立证明**（本班子代理取证，21 个跨 1991→2026 抽样日）：用 **HEAD 内**
  `zephyr.alt_data.emotion_index_builder` 以真 reader 只读复算，**21/21 与库内存储值逐位一致**
  （delta=0.000000000，components JSON 全等）；库完整性：重复键 0、live∩replay 键重叠 0、
  close_final 行数=kline_daily 日历日数（**缺失日 0**）。
  ⇒ **"库跑在代码前面"的真实缺口不是公式**（公式在 HEAD），**而是批驱动件与 DDL-as-code**：
  HEAD 内 `scripts/ch/apply_market_tables_ddl.py` 对 `emotion_index` 引用数=**0**，
  `schemas/categories/market/market_emotion_index.py` 无 `source` 列。
- 已知缺陷确认：`C2_promotion` 在 17 条 live close_final 行上 `raw_value` min=max=1.0
  （`uniqExact=1`，status=insufficient）=CH `join_use_nulls` 伪值；8,596 条 replay 行为 `missing`
  故当前**惰性无害**，daban 史达 120 观测后会抬升温度计（现 16 日）。

## 2. 滞留件清单（原址 + 字节）

| 文件 | 字节 | 状态 |
|---|---|---|
| `.aidrafts/st-emoreplay-20260923/src/zephyr/alt_data/emotion_index_replay.py` | 17,795/405 行 | 干净，可落地 |
| `…/tests/alt_data/test_emotion_index_replay.py` | 10,565/271 行 | **10 passed 42.54s**（本班实跑，无生产写入） |
| `…/schemas/categories/market/market_emotion_index.py` | 3,262/61 行 | **闸位：`AI_AUTONOMY=human_only`** |
| `…/scripts/ch/apply_market_tables_ddl.py` | 68,473/1,329 行 | **主区 DIRTY（他会话持有）** |
| `…/docs/_working/emotion_line/history_replay_report_v1.md` | 18,374/217 行 | 干净（status: final） |
| `…/docs/_working/emotion_line/gpu_emotion_condition_matrix_v1.{csv,meta.yaml}` + `cells_v1.csv` | 1,203,923 / 3,285 / 790 | 干净 |
| `…/docs/_working/emotion_line/index.md` | 1,951 | **与主区生成器产物撞车**，禁随批 |
| 两份热册（capability_canonical_file 2.4MB / module_translation 3.4MB） | — | **禁整册快照覆写**（会驱逐主区 147/8 个键） |
| `.runtime/tmp/st-emoreplay-20260923/*.py` 7 个驱动件 | ~44KB | **24h TTL 临期**，本班已保全（见 §4） |

## 3. 为什么本包不落地（三条硬规则，非嫌麻烦）

1. **AGENTS §5 人机门位**：`market_emotion_index.py` 头部明文 `AI_AUTONOMY=human_only` ⇒ 该文件
   的改动须 Owner 签。绕开它=违宪。
2. **AGENTS §1 规则 3 + §3.4**：`apply_market_tables_ddl.py` 在主区被**另一活跃会话持有为脏**，
   HELD-OVERLAP 不硬闯、他会话在途不代修。
3. **AGENTS §2 队列教训复用**：该班死信根因（`q-…-0001` DIRECTORY-CONTRACT `.json`、
   `q-…-0002` TRANSLATION-COVERAGE）是**整册快照覆写热册**所致，不是内容缺陷；
   正确修法=对当前主区重跑 `add_module_translation.py` 与 creation-token 写手，
   而非带快照——这属于原班（或接管班）的施工，不是接线。

## 4. 本班已做的唯一动作：防灭失保全（非破坏、可逆）

驱动件住在 `.runtime/tmp/`（AGENTS §9.4 临时区，24h TTL，mtime 2026-09-23 18:24–20:40
⇒ 约 2026-09-24 晚被清）。这批脚本是 8,596 行产线数据的**唯一批驱动面**，灭失即"判据灭失"病根第三次复发。

- 动作：7 件逐字节复制到 `.aidrafts/st-emoreplay-20260923/scripts/emoreplay_drivers_preserved/`，
  附 `README_PRESERVED.md`；**sha256 全 7 件已核全等**。未删原址、未动主区、未改内容。
- 撤销方式：删该目录即可（无其他副作用）。

## 5. 接管班落地配方（按序，每条可机械校验）

1. 先与 `apply_market_tables_ddl.py` 的持有会话对齐，把 `_ALL_DDL` 注册 + `source` 列 ALTER
   落进**同一文件态**（否则 HEAD 无表可 ALTER，即 §1 的引用数=0 问题）。
2. `market_emotion_index.py` 走 Owner 签（human_only）；`source` 列位置与产线不同（产线
   `ingest_ts→source`，DDL-as-code `source→ingest_ts`）经核**良性**（`verify_schema_truth.py` 按名比对、
   INSERT 用显式列名），但须在批文里留痕免得下次又查一遍。
3. 修三件小硬伤（同批）：`_live_close_final_keys` 只按 `stage` 过滤未带 `source='live'`
   （⇒ 重跑静默 written=0 而非刷新）；窄窗常量 `590` 字面量改 import builder `_window_start`；
   `verify_slice_equivalence`/`pit_live_value_check` 空样例时返回字面 `True` ⇒ 必须改为抛错
   （**假绿结构性来源**，本班红蓝口径要的就是这一条）。
4. 补 `python -m zephyr.alt_data.emotion_index_replay` 的 `__main__` 入口（头注声明了但不存在），
   或把保全的 3 个驱动件正式升进 `scripts/` 并改 `sys.path` 指向主仓。
5. 热册用生成器重跑入册，禁整册覆写；`emotion_line/index.md` 移出批次、merge 后重生成。

## 6. 与本包（做T 矩阵重考）的关系

本包的六段相位真源**不依赖**上述任何未落地块：`six_phase_history_v1.csv` 的宏观腿走
`c1_backtest.regime_snapshot_history`、微观腿走广度指数，映射件 `auto_mount.py` 全在 HEAD。
唯一依赖产线的是 GPU 输入包里的**连续温度计列**（`emotion_index`/`band5`/`ok_n`），
其公式已在 HEAD 且 21/21 复算一致 ⇒ 本包结论有效性不受本移交项阻塞。
