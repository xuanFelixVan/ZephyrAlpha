---
ttl: task_bound
title: L02-B 子模块挖矿簿 · 情绪全史回放线（emotion_index_replay）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-A
status: MINE 完成（对 SKEL L02-C01 现状改判）
---

# L02 · B 全史回放线

**① 职责一句话**：用冻结公式把 emotion_index 从"逐日攒"改成"全历史一次回放"，补齐 close_final 深史供考试与 GPU 条件包使用。

**② 现状实测（本册 2026-09-26 复核）**

| 项 | SKEL（09-25 记） | 本册实测 |
|---|---|---|
| 代码件 | 滞 `.aidrafts/st-emoreplay-20260923/`，主区无 | **`src/zephyr/alt_data/emotion_index_replay.py` 已在主区**（头注 MATURITY=experimental，TESTS 指 `tests/alt_data/test_emotion_index_replay.py`，两件均存在）；`git status --porcelain` 实测=**`??` 未跟踪**（盘上有了，未进 HEAD） |
| DDL source 列 | 待补 | **已在 HEAD**（`market_emotion_index.py:42`） |
| 文档五件 | 滞 .aidrafts | `docs/_working/emotion_line/{history_replay_report_v1.md, gpu_emotion_condition_matrix_v1.csv, gpu_emotion_condition_matrix_v1.meta.yaml, gpu_emotion_condition_cells_v1.csv}` 实测已在盘且为 **`A ` 已暂存态** |
| 数据面 | 8,596 行 replay | CH 实测：close_final replay 8,596 行（1991-06-10→2026-08-31）+ live 18 行（2026-09-01→09-24）→ **接缝在 08-31/09-01，中间 09-01 前无空洞但 08-31→09-01 恰为 1 交易日界**（SKEL 未记的具体接缝位置，本册补） |
| 悬空引用 | 34_d_backtest.md:3043 与 t0_condition_matrix_v1.meta.yaml:138 引"主区无此件" | 随文档件已暂存而**消除**（登记销口） |

**③ 六向台账**

| 向 | 发现 |
|---|---|
| ①上游 | 内部：五表全史；同公式零复制（import builder）。外部：已查无（一次性批作业无外部惯例） |
| ②下游 | 内部：GPU 情绪条件矩阵输入包（8,613×24 列）、D2 双轴重考（NO_MAP）、t0 E4 复跑、condition_package 冻结消费。外部：已查无 |
| ③算法 | 内部：切片缓存 reader（纯 GROUP BY 形状白名单，JOIN 形状直通真查询防窗界伪影）。外部：已查无（工程技巧，无方法论对应） |
| ④后端 | 内部：**唯一残差=两件代码未进 HEAD**（`??` 态）——即 L02-C01 从"复职批五类交付"缩为"两文件随车提交 + 撞键纪律复核"；回放只写活管道不存在的键（ORDER BY 不含 source 的覆盖风险已在头注 INVARIANTS 自证） |
| ⑤前端 | 内部：无。外部：已查无 |
| ⑥数据字段 | 内部：1991-2018 段为 ~237 只 stub 宇宙分位（跨 2019 断崖不可比，输入包带 universe_honest_ok 列）→ **质量画像已内建诚实标记**，Owner 呈批项 P-2（stub 段去留）仍未裁 |

**④ 缺口清单**：L02-C01（在册，本册缩范围）；呈批项 P-2/P-5（在册）；**L02-B-G1 回放线与活管道 source 列去重语义仅靠约定（无机械守卫）**——册内未见。

**⑤ 三态裁定**：C01=**施工 P0**（现仅"把两文件交落地车道"，零设计）；P-2/P-5=挂起（Owner 门位）；G1=**施工 P2**（加一条"同 (trade_date,stage) 不得同时存在 live/replay 两行"的对拍 SQL 进既有测试，净零）。

**⑥ 挖矿日志**：R1 内部：文件+git 态三方实测→signal（**改判：代码面已落盘、文档面已暂存，缺口从"复职五类"缩为"两文件提交"**）；R2 内部：CH 接缝探针→signal；R3 外部：回放/回填方法论→noise，归因=方向本就无矿。

**封矿判据**：六向封口 + 现状改判留证 → **子模块封矿**。
