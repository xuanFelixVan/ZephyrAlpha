---
ttl: task_bound
title: L01-S3 子模块挖矿簿 · overlay 供数件家族（Wyckoff/LPPL/合成VIX/演化/波动双件/筹码/指数传感器）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-A
status: MINE 完成（八件全实测，三态裁定含内收申报）
---

# L01 · S3 overlay 供数件家族

**① 职责一句话**：给 S2 的 8 转换通路提供"结构性事件原料"（恐慌指数、收集-派发 FSM、赶顶、压缩突破、风格演化、筹码结构、指数强弱）的八个独立打分件。

**② 现状实测**（行数=本册 `wc -l` 实测；引用计数=本册全仓 grep `src/ scripts/` 实测，排除自身与 `features/__init__.py`）

| 件（src/zephyr/regime/） | 行数 | 声明 MATURITY | 仓内被引 | 生产触发面 |
|---|---|---|---|---|
| `features/wyckoff_engine.py` | 476 | production | 6（含 overlay_features / overlay_signals_builder / validation/wyckoff_walkforward / **pf_core/strategies/daban_sleeve_strategy.py** / **signal_ashare/bottom_confirmation_entry.py**） | 随 S2 日级；另有打板策略侧引用 |
| `features/synthetic_vix.py` | 228 | production | 6（market_features/overlay_features/institutional_regime_scorer/overlay_signals_builder/**data/implementations/miniqmt_provider.py**） | 随 S2 日级 |
| `volatility_regime_alerter.py` | 223 | production（:7） | 3 | **CONSUMERS 自注"运行时装配批接线"=未接**（:5）；GARCH 自研复用 MOD-RK-26、禁引 arch 库（:8 INVARIANTS） |
| `volatility_squeeze_breakout.py` | 317 | production（:7） | 3 | 同上——契约在、装配批未落 |
| `features/lppl_detector.py` | 186 | design | **0** | 无 |
| `features/evolution_signals.py` | 190 | design | **0**（三函数未入 _TRANSITION_DIMS，:39 自注同证） | 无 |
| `features/chip_distribution_engine.py` | 464 | 打回 trial（裁定编号 257④，ruling_registry 已登记） | 0（仅 `features/__init__.py`、`shared/utils/market_units.py`） | 无（真实数据伪分布案底在头注） |
| `features/index_sensor.py` | 135 | design | 0（仅 `features/__init__.py`） | 无（TDM-E-L1-S1 节点所指件本身未接电） |

测试面（实测在册）：`tests/regime/test_wyckoff_engine.py`、`test_synthetic_vix.py`、`test_synthetic_vix_iv_path.py`、`test_volatility_regime_alerter.py`、`test_volatility_squeeze_breakout.py`、`test_chip_distribution_engine.py`、`test_index_sensor.py`——**八件全部有测试**，测试覆盖 ≠ 生产消费，本册区分记录。

**③ 六向台账**

| 向 | 发现 |
|---|---|
| ①上游 | 内部：kline_index 收盘/高低、成交额、option_iv_surface（取数面在册但 D4 未明）、指数估值、板块与连板截面（经 S2 传入）。外部：合成 VIX 的业界替代口径=已实现波动率分位 + 期权 IV（A 股仅有 50ETF/300/500 期权链，覆盖指数有限）——本册以"期权 IV 曲面在 A 股指数层覆盖不全"为结论登记，**外部单源未足两源，标待验证不入图**（查法：本轮未做 IV 口径定向检索，列为下轮长尾） |
| ②下游 | 内部：唯一活跃下游=S2 转换评分；Wyckoff 另被打板 sleeve 与底部确认进场引用（跨环节边，L06/L04 侧登记）。外部：已查无（查法：以"wyckoff phase detection consumers risk overlay"检索，未得一线机构件） |
| ③算法 | 内部：FSM 五阶段 + walk-forward（`validation/wyckoff_walkforward.py` 901 行，MATURITY=validation）；LPPL 自研 186 行。外部：LPPLS 有成熟开源实现可直接替换自研（Boulder Investment Technologies `lppls`，GitHub 2020-04，https://github.com/Boulder-Investment-Technologies/lppls ；R 实现 https://github.com/sabato96/lppls ）+ 学术口径（Sornette 系两百年实证，Physica A 2016-09，https://www.sciencedirect.com/science/article/abs/pii/S0378437116301017 ）→ **两源跨验通过**：自研件属"可用但非最优"，候选换轨登记 |
| ④后端 | 内部：两件 volatility（alerter/squeeze）契约齐、MATURITY=production 但**装配批未落地**——文档态与运行态不符（属"叙述与现状脱节"类，只登记不改判据）。外部：ruptures（BSD-2，离线变点）与 bocd（MIT）已在 SKEL §14.2 收录，本册标沿用不重复 |
| ⑤前端 | 内部：无呈现面（八件全为中间评分件）。外部：已查无（查法：呈现惯例并入 S10 面板册，本层无独立诉求） |
| ⑥数据字段 | 内部：option_iv_surface（D4）、布林带宽分位、RV_5d/RV_20d、250 日分位、KDJ 顶背离——字段在；质量画像=option_iv_surface 表实测在库但取数面未见消费（S4 册探针同证）。外部：已查无 |

**④ 缺口清单**

| 编号 | 内容 | 册内出处 |
|---|---|---|
| D4 | 期权 IV 曲面口径未明 | 需求册沿用 |
| L01-S3-G1 | 零消费件四只（lppl_detector / evolution_signals / chip_distribution_engine / index_sensor）——挂测试但无生产消费者 | 册内未见 |
| L01-S3-G2 | MATURITY=production 却未装配的漂移两件（volatility_regime_alerter / volatility_squeeze_breakout） | 册内未见 |
| L01-S3-G3 | LPPLS 自研件与开源成熟实现并存，未做换轨评估（净零候选） | 册内未见 |

**⑤ 自审闸三态裁定**

| 缺口 | 裁定 | 理由 |
|---|---|---|
| D4 | 挂起排期 | 解锁条件=期权 IV 数据源账号/API（Owner 终局四事之一），非 AI 可自解 |
| L01-S3-G1 | 施工（内收申报） | 终局判据明确：零触发零消费→退役（宪法 §4.2）；chip 已打回 trial 同批复核；**反驳者一问**：①"留着以后接"——以后=无解锁条件的挂起，账本已两次证明会腐烂（真实，但不构成保留理由，走档案化不删除）②"测试成本为零"——测试面是维护面非资产（真实）③"evolution 三维是长尾矿"——若真要，走新卡预注册而非休眠件（成立）→ 裁定=申报退役/档案化，不新建 |
| L01-S3-G2 | 施工（P2，随 S2-C01 装配批） | 两件事消灭的是"人工通读头注才知道没接"这一环节；MATURITY 字段与运行态一致是终局自动编排的前提 |
| L01-S3-G3 | 挂起排期 | 终局要最优内核，但换轨属"在错误层位提前重做"——解锁条件=S2 阈值账本落地（S2 册 G1）后按统一账本比较两者触发质量，再裁 |

**⑥ 挖矿日志**

| 轮 | 矿脉 | 判定 | noise 归因 |
|---|---|---|---|
| R1 | 内部：八件引用计数 + MATURITY 头注实录 | signal（四件零消费量化实证，纠正 SKEL"未接"散文为可核对数字） | — |
| R2 | 内部：测试面对表 | signal（八件全有测试，测试≠消费定性） | — |
| R3 | 外部：LPPLS 开源+学术两源 | signal | — |
| R4 | 外部：合成 VIX / A 股 IV 口径 | noise | 归因=**来源贫矿**（A 股指数期权 IV 公开方法论少，检索命中多为行情广告文）→ 已查无记档，列下轮定向长尾 |
| R5 | 外部：Wyckoff 量化消费的机构实践 | noise | 归因=**查询词不当**（英文 wyckoff 命中散户教程为主）→ 降优先级，改由打板侧（L04/L06 车道）挖 |

**本册封矿判据**：八件逐一实测封口，六向含"已查无+查法"，未挖长尾仅剩"IV 口径外部方法论定向检索"一条（已记 noise 归因 + 下轮线索）→ **子模块封矿**。
