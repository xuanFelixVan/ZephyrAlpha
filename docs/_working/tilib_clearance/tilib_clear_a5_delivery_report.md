---
ttl: task_bound
session: st-tilib-clear-20260920
title: 技术指标库清欠班交付报告（分包A·34指标三件套清零）
---

# a5 交付报告（2026-09-20 · tilib 清欠班 · 分包A）

> 终极目标：technical_indicator_registry.yaml 102→≥136 条，34 指标三件套（代码+测试+注册表）全清。
> **结论：达成。136 条在 HEAD（020728598c），全库测试 1070 passed，红蓝对抗 ALL PASS。**

## 1. 终极目标逐条对账

| 目标项 | 目标 | 实测 | 判定 |
|---|---|---|---|
| 注册表条目 | 102→≥136 | **136**（v1.4.0，entry_count=136，yaml 解析实测） | ✅ |
| 三件套 | 每指标=代码+≥4测试+注册表条目 | 34/34 齐（模块级类+测试类+IND-* 条目） | ✅ |
| 测试 | 目录全绿 | **1070 passed/5 skipped ×2 轮**（基线 762，+308） | ✅ |
| 注册表↔代码一致性 | module_id 与文件头 [BLUEPRINT] 一致 | 探针 mismatches=NONE（含治愈 9 条历史 stale） | ✅ |
| Registry↔DDL↔INSERT_COLUMNS↔运行时 | 列集全等 | **198×4 全等**（四方探针） | ✅ |
| CH 宽表 | 新列就绪供夜跑回填 | 36 列 ALTER landed 36/36，物理列 207 | ✅ |
| 无遗留无待裁 | 台账销行+停手项留痕 | 裁①..⑨ 全落台账；登记债 2 条（见 §5） | ✅ |

## 2. 交付物清单（三个 HEAD 提交）

| commit | 内容 |
|---|---|
| **7c7396cc69** | 波1+波2：+31 指标/32 列（M-L1 自适应均线族 7+M-L2 价格变换 4+M-L3 统计回归 4+M-L5 社区热门 16） |
| **020728598c** | 波3：+3 指标/4 列（M-L6 学术滤波器族 SUPERSMOOTHER/HIGHPASS/PTREND，TASC 2024-09） |
| 20b2e4e3bb | 探针副产物（2 个注册表 yaml 先行落地，内容与 7c7396cc69 完全一致，无害留痕） |

文件构成（每波）：族文件 6（trend/statistics/volatility/momentum/volume/cycle）+测试 7+schema+注册表+capability 册+16 号 memo v1.7.0/1.8.0/1.9.0+战役文档（a1 台账/a2 施工卡/a3 挖矿报告）。

## 3. 数值正确性证据链（证据等级[亲验]）

- **MAMA/FAMA**：与 talib.MAMA 逐位一致（偏差 0.0，测试种子+红蓝新随机种子双验证）
- **回归四件/价格变换/TRIMA**：talib 对照 1e-12~逐位级
- **TEMA/T3**：与 talib 第 100 根起 rtol=1e-6（SMA 种子预热差异按 MAMA 豁免口径，指数衰减实测 2.9e-11@150）
- **无 TA-Lib 对应的 19 件**（JMA/FRAMA/VIDYA/EBSW/INERTIA/QSTICK/RMI/PFE/FOSC/CTI/VHF/ER/WAD/VO/MARKETFI/ZSCORE/SS/HP/PTREND）：独立路径复算双实现互证+手工微样本写死值+性质测试（常数恒等/正弦衰减/值域）
- **红蓝对抗（独立探针，种子 20260920≠测试种子）**：PIT 零未来行（shift(-n)/bfill 扫描空）+ 新数据 talib 复验 12 项全过 + 递推类常数恒等 5 项全过 + 三方复账 4 项全过 + 弱断言扫描零命中。初判 2 FAIL（jma/frama 常数恒等）经定性均为探针自身疏漏（未排预热 NaN/未同改 H/L），实现复验正确。

## 4. 同义剔除与挖矿增量（34 账目口径）

- 批4 清单 34 项 − **3 项同义剔除**（裁①/⑦：LINEARREG_BAR=既有 linearreg、PSL=既有 PSY、MSW=既有 ht_sine）= 31 项
- \+ **波3 学术新挖 3 项**（SUPERSMOOTHER/HIGHPASS/PTREND，TASC 2024-09 Precision Trend 正主+论文原生组件）= **34 项施工** ✓
- 登记后续（不施工）：Griffiths 预测器+Instantaneous Frequency（TASC 2025-01）、Continuation Index（TASC 2025-09）——公式源未镜像，a3 挖矿报告 §2 立卡待令

## 5. 未达成项与原因（禁虚报，逐条）

| 项 | 状态 | 原因与建议 |
|---|---|---|
| 波4 stretch：stock_daily_basic 数据批 | **未启动** | ①性质=stretch（前波全绿才开的可选项）；②全市场 AKShare 换手率采集 2021 起≈5000 标的×1200 交易日，需小时级网络窗口+批9 配方（交接包 §3 现成：DDL-as-Code→provider→tasks.yaml→回填验收 000852 100%）；③本班收官判据（红蓝+交付）已达成，收尾时段强行开工长数据批违背质量门节奏。**建议：下一夜班窗口按交接包 §3 配方直接开工，验收口径不变。** |
| 登记债① | 留痕 | reversal.py 行1 [BLUEPRINT] 计数散文 stale（元数据债，非本班破损） |
| 登记债② | 留痕 | maxexec q-0040 死信（ALGO-FLOW-LINK 断锚 decisiongraph_adapter.yaml）——他会话在途违规，按 §3.4 不代修 |

## 6. 提交通道连环死因记录（q-0001..q-0005 全死信，勿 requeue，维护班可清账）

R5-DIGIT-SUFFIX（目录 _20260920）→CREATE-GUARD（新 .md 缺 token）→EXEMPT-ZONE-FM（生成 index.md 带 doc_type）→GATE-NAMING N-16（基名撞 final3_campaign）→#341 新钩子 ruff/ruff-format。五连治愈配方全部留痕台账裁⑤/⑥/⑧/⑨；CREATE-GUARD token 共 6 条（r1×3+r2×3）已登记 capability 册顶级 creation_tokens 节。

## 7. 运维终态

- CH 宽表：36 新列全就位（探针 landed 36/36），夜跑 02:30 tilib_indicator_backfill_nightly 将自动回填新列历史；宽表当日零 INSERT 遵守（ALTER=元数据操作，批6/批8 配方）
- D-15 三态核实：17 文件 HEAD/index/worktree 全一致（回退炸弹已拆除：index 旧 blob 经 git reset 消弹，capability 册以 HEAD 超集收敛磁盘）
- 台账：docs/_working/tilib_clearance/tilib_clear_a1_ledger.md（canonical 名，断点续班凭指令+a1 即续）
- 死会话遗物：st-dataqa-20260920 已由 reaper 冷启动自动回收（与本班无关）
