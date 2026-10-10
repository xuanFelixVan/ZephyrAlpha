---
ttl: task_bound
title: 过夜总令挖矿车道共用作业簿（st-nightmine-20261010）
created: "2026-10-10"
sid: st-nightmine-20261010
family_id: NIGHTMINE-CAMPAIGN
---

# 共用作业簿（每车道开工前必读，禁凭记忆）

工作根=工棚 `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010`（一切读写以此为前缀）。
名册真源=`docs/_working/nightmine_campaign/00_lane_roster.yaml`（186 节点×车道×现存卡态，机生）。

## 一、你的产出只有两类（越界即连坐他人袋）

1. 本车道挖矿台账：`docs/_working/nightmine_campaign/L<n>_ledger.md`（逐节点可复核）。
2. 新考试卡 YAML：`docs/03_modules/_domain_backtest/exam_cards/<flow>/<layer>/<node_id>__<family>__NN_<中文名>.yaml`。

**禁止**：改 TDM/注册表/分数册/git 操作/commit/跑生成器删除他人件；改他人车道目录；写 `.runtime` 根；
在项目根落临时件（临时件走 `.runtime/tmp/st-nightmine-20261010/`）。
**禁止**手改 `*__<family>.yaml` 骨架件（generated: true 受保护件）——新卡一律另建新文件。

## 二、卡可运行判据（不可运行的卡=废卡）

执行器 `scripts/backtest/fexam/calibration_exam.py:run_card` 机械读取以下字段，缺一即 RuntimeError：

- `status: preregistered`（empty=未冻结禁考；冻结=看数前把假设/窗口/分桶/门柱写死，事后挪门柱=作废 G4-5）
- `signal_kind: panel | series`（panel=逐符号宽表；series=日度单序列，广度/结果面用 series）
- `pillars_numeric:`（机判面，必填数值）：`mono_spearman_min` / `ic_mean_min` / `ic_ir_min` /
  `regime_same_sign: true` / `oos_same_sign: true`
- `window.in_sample` + `window.oos`（两列表日期）+ `window.regimes`（牛/熊跨度串）
- `buckets`（分桶型与最小样本）+ `pillars`（文字判据，与 numeric 面同口径）+ `target.primary/secondary`
- `lineage.confidence_writeback: TDM.nodes.<node_id>.confidence`
- 不得带 `generated: true`；须带 `preregistered_by: st-nightmine-20261010-L<n>` + `preregistered_at: '2026-10-10'`
- **新增必填面（本战役立法：卡的取数接线声明）** `data_binding:` 段——把这张卡将来怎么取数写死，供考试车道接线：
  - `signal_table`（CH 表全名，经 TableRegistry 在册）/ `signal_column` / `signal_derivation`（一句话算法）
  - `target_source`（`kline_index 000300 close→next_day_return` 之类）
  - `data_window_evidence`（实测该表覆盖窗+行数，命令原文）

模板真源=`docs/03_modules/_domain_backtest/exam_cards/entry_flow/L1/TDM-E-L1-S2__calibration__02_涨停家数.yaml`
（照该件字段序与写法，把 `data_binding` 段补上）。

## 三、每节点六向作业（mining_sop v1.7.0 §2，逐向留痕：发现或"已查无"）

| 向 | 本域落地动作 |
|----|-------------|
| ①上游 | 读 TDM 节点 `data_refs`/`factor_refs`/`algo_note_zh`/`decision_question` 全文→每个判据性陈述=一张卡候选（一句假设一个可判数值面） |
| ②下游 | `git grep -ln <node_id>` 反查消费方，判该环输出该考"喂给谁的效果" |
| ③算法 | 同族先例卡对照（`exam_cards/` 内 grep 近亲）+ 机构三件套（响应曲线/时滞/条件稳定性）；外部引用须 URL+发布方+年份，禁凭记忆 |
| ④后端 | 该环代码现状（`module_ref`/`module_mounts` 指向件）——缺实现不阻卡，卡标 `blocked_on_impl` 注明缺什么 |
| ⑤呈现 | 只登记不施工（一句话） |
| ⑥数据 | 逐字段核 CH 可得性＋质量画像（覆盖窗/行数/断供史）；**断供不弃卡**→`status: blocked_on_data` 并写死缺哪张表哪一段 |

**念想引擎（可选，本车道 ≤8 次调用）**：经 LSG 云 qwen 生成补充假说，卡内标 `origin: llm_qwen`。
调用形：`from zephyr.security.llm_defense.llm_security.gateway import ...`——先 `git grep -n "provider='qwen'"` 找真用法再调，失败即弃该向（记"受阻"不算查无）。

**枯竭判据（§3 结构判据，禁降格）**：本节点六向全部"已查无/已入卡"＋无未挖长尾 ⇒ `mined_out`。
禁以"挖了两轮没新东西/时间不够/节点太多"封矿；候选多=富矿不是停止判据。

## 四、数据可得性探针（命令原文，禁裸 duckdb）

```
cd D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010
python -c "
import sys; sys.path.insert(0,'scripts/backtest')
from fexam.ch_data import ch_query_df, table_columns, T_KLINE_DAILY_HFQ
df=ch_query_df('SELECT min(trade_date), max(trade_date), count() FROM c1_market.kline_index WHERE symbol=\'000300\'')
print(df)
"
```
空结果≠无数据：先看是否抛错/rc，`ch_query` 出错可能返回空串（在册事故案）。日期必加引号，聚合表读须 `FINAL`。
断言"X 不存在/未做"前 MUST 跑 `python -m zephyr.library.lookup state "<关键词>"`（trae_065 v1.1.0 铁律），
把输出摘录进卡的 `data_window_evidence` 或台账。

## 五、台账格式（逐节点一行，机读优先）

```
| node_id | 六向结论(每向一句) | 新卡数 | 族分布 | mined_out? | blocked 原因 |
```
车道收尾 MUST 写：本车道节点总数/已挖数/新卡总数/族分布/未挖长尾清单（明列）/交叉复挖建议（20% 节点名单）。
