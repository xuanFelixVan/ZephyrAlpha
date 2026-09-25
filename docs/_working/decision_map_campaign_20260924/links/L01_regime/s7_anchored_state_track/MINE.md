---
ttl: task_bound
title: L01-S7 子模块挖矿簿 · 锚定态双轨（regime_state_anchored 四档波动）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-A
status: MINE 完成（含对 SKEL 两项状态改判）
---

# L01 · S7 锚定态双轨

**① 职责一句话**：用零拟合的 vol_pct 结构阈值给大盘打"波动风险四档"，作为 HMM 概率轨之外的第二真值轴（结构性免疫 label switching）。

**② 现状实测**

| 项 | 实测 |
|---|---|
| 代码 | `src/zephyr/regime/core/anchored_state_machine.py` 204 行，MATURITY=**design**（头注 :8），INVARIANTS 头注 :9=四态固定阈值 0.30/0.60/0.80（裁定编号 229，ruling_registry 已登记） |
| 任务 | `tasks.yaml:647 anchored_state_build`（schedule=daily_kline，trading_day_only） |
| DDL | `schemas/categories/backtest/backtest_regime_state_anchored.py`（59 行，头标 `[AI_AUTONOMY] human_only`） |
| 表实测 | `c1_backtest.regime_state_anchored`＝**2,239 行 / 2,239 唯一日 / 2017-07-11→2026-09-24**（本册 CH 只读探针；单行每日、无双写） |
| 消费 | `pf_alloc/allocation_inputs.py:612-700`（锚定总暴露熔断 cap，AGG 分家：仓位数字仍归 L1）+ `internal_compute_provider.py` capability 路由 + `sector_state_pipeline` 读 dominant |
| **改判 1** | SKEL 记"schema 缺 `SQL_LATEST_ANCHORED_STATE` = allocation_inputs 活体不可导入"——**本册实测：该缺陷已由"L01-C01 本地定义修法"处置**，`allocation_inputs.py:633` 现自带该 SQL 常量（注释 :624-632 明写"schema 件头标 human_only 禁改…待解除后迁移"），且 `python -c "import zephyr.pf_alloc.allocation_inputs"` 实测 **OK** |
| **改判 2** | 同次 import 实测：`from schemas.categories.backtest.backtest_regime_state_anchored import SQL_LATEST_ANCHORED_STATE` 仍 **ImportError** → 原验收判据（"schema 件补符号 + git show dev 视角可导入"）**未达成**，实际走的是本地常量旁路 |
| 测试面 | 相关测试经 allocation 侧覆盖（本册未单测 cap 分支，属 VERIFY 车道） |

**③ 六向台账**

| 向 | 发现 |
|---|---|
| ①上游 | 内部：kline_index 000300 收盘（load_close，start 2016-06-01 留热身）。外部：阈值分档=非参数风险分层的通行做法（波动率目标族两源，见 S5 册 §③⑤ 引文，本册标沿用不重复入图） |
| ②下游 | 内部：cap（只减不加）+ 板块层 dominant 轴 + 双轨对拍件。外部：已查无（查法：双轨并行的外部惯例检索未见"阈值态与 HMM 态并行"成例，本仓属自洽设计） |
| ③算法 | 内部：hv20 + 250 日滚动分位，全 rolling PIT。外部：CUSUM/BOCPD 可作阈值稳健性巡检候选（SKEL §14.2 已收录 ruptures/bocd，沿用不重复） |
| ④后端 | 内部：①**真源位置违规风险**——SQL 常量落在消费件内而非 DDL-as-Code 件（schema 件 human_only 是唯一阻力，需 Owner 解除）②MATURITY=design 与"在产任务 + 2,239 日真值"不符 |
| ⑤前端 | 内部：无独立呈现（经 panel 人工面）。外部：已查无 |
| ⑥数据字段 | 内部：close/vol_pct/ma20/60/120/data_source 齐；质量画像=2,239 日连续、无缺日迹象（实测行数=唯一日数） |

**④ 缺口清单**

| 编号 | 内容 | 册内出处 |
|---|---|---|
| L01-C01（在册） | schema 补符号随车修 | SKEL §12；本册实测=以本地常量旁路达成"能跑"、未达成判据 |
| LK-L01-2（在册） | schema 缺符号导致导入断裂 | 本册改判为"已旁路，断裂点在 schema 侧" |
| L01-C04 步 5 | 锚定表 rN 双词表语义待裁（HMM 七态 vs 波动四档同名 rN，附录 C） | 附录 C 在册 |
| L01-S7-G1 | 本地 SQL 常量=第二真源隐患（去重口径与 alloc_shrinkage_daily 同族件并存两份） | 册内未见 |
| L01-S7-G2 | MATURITY=design 但已承担生产熔断 cap 输入=成熟度与职责不符 | 册内未见 |

**⑤ 自审闸三态裁定**

| 缺口 | 裁定 | 理由 |
|---|---|---|
| L01-C01 | 施工（P0，判据不变） | 需 Owner 解除该 schema 件 human_only（AI 自治门位）后迁移符号；旁路只是止血，终局要"读 SQL 只看 DDL 件" |
| LK-L01-2 | 挂起（随 C01 销口） | 阻塞条件=同一门位 |
| L01-C04 步 5 | 挂起排期（Owner 语义裁定门位） | 词表裁定不是 AI 可自裁项；解锁=裁定登记 |
| L01-S7-G1 | 施工（随 C01 同批） | 两处同义 SQL=未来改动必漏一处；净零（迁移即删本地块，注释已预告） |
| L01-S7-G2 | 施工（P3 登记面） | 成熟度字段失真会让自动编排错判可用级别；改动零代码 |

**⑥ 挖矿日志**

| 轮 | 矿脉 | 判定 | noise 归因 |
|---|---|---|---|
| R1 | 内部：活体 import 双向实测（消费件可导入 / schema 符号仍缺） | signal（**对 SKEL 两项改判**） | — |
| R2 | 内部：CH 探针 2,239 行=2,239 日 | signal | — |
| R3 | 外部：阈值分档惯例 | noise | 归因=沿用既有引文，无新增量 → 已查无（新料） |

**本册封矿判据**：六向封口 + 两项对上游叙述的改判留证 → **子模块封矿**。
