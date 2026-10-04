---
ttl: task_bound
completes_when: 车道H 执行完毕+终验后转归档
title: F8 138 待裁·总筹家族处置表（Owner 已批代执 2026-10-04）
---

# F8 家族处置表（总筹裁定，车道H 照表执行）

> 授权链：Owner"手刹件全批"+「F8 按我出的家族表代执」。判据：内容是否仍被引用/是否可再生/是否成套。
> 执行纪律：每批前 claim；测试族先跑测试全绿才提交；数据产物只 unstage 不删盘面文件。

| 家族 | 台数 | 处置 | 依据 |
|------|------|------|------|
| 回测 artifacts_v2 | 11 | **unstage（留盘面）** | 裁定#479 已禁入 .gitignore；可再生运行结果 |
| 战役文档族（fullscore_night 8+night_totalflow 7+circulation 5+deadletter_cure 4+branch_zero 3+disk_reorg 3+pipeline-research 1） | 31 | **提交** | 病历本素材（F4 挂载引用面），历史保全零风险 |
| 散件 docs/03_modules blueprint.md | ≈12 | **提交** | 模块头 [BLUEPRINT] 引用路径，缺席=REFERENCE-INTEGRITY 隐患 |
| 数据安全 wiring（config+src+3tests） | 5 | **跑 3 测试→绿则提交** | 成套源码 |
| SLA 预测（src+test） | 2 | **跑测试→绿则提交** | 成对 |
| 注册册计数对账（src+test） | 2 | **跑测试→绿则提交** | 成对 |
| 宏观 sensor（config+src） | 2 | **提交** | 挂 config/macro_indicator_series_map 语义 |
| 期权日统计（schema+script） | 2 | **提交** | schema 类目+脚本 |
| metaq 283问 scripts | 2 | **提交** | dead-archive 处方点名要它们（q-chainpile 袋） |
| wave1a 交付卡 scripts | 2 | **提交** | 在册工具 |
| algo_flow 桥接 yaml ×2、E4 考试、两融回填、sector_line/、T0 n_trial 测试、L5 日闸测试 | 6 | **提交**（测试件先跑） | 各有在册引用 |
| T0 条件矩阵 csv、metaq .rda ×2 | 3 | **提交** | 研究登记数据对（.matrix.json 已在 HEAD） |
| morning_digest、rolling_archive_state、_cache parquet、promotion_advisories/、statreplay_baseline/ | 5 | **留置不动** | 机生运行产物/缓存，数据区原生 |
| 剩余散件（ensure_ai_wrapper 等 4 台 fresh 待裁+未列散件） | — | **留待 Owner** | 内容 HEAD 独有且意图不明（覆盖度 58% 等），不代裁 |
| 索引态残迹 3 台 | 3 | **git add 复位** | HEAD 已含等值，index 缺席 |

执行批次序：B 战役文档 → C blueprints → D 测试族（wiring→SLA→reconciler→其余）→ E 数据产物 unstage → F 索引态复位 → G 数据登记件。每批独立提交（--enqueue），批名前缀 [F8家族处置批X]。
