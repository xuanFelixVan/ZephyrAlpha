---
campaign: matrix-20261006
lane: S-direction-survey
status: final
ttl: task_bound
created: 2026-10-06
---

# direction_survey_v1 — 因子册 direction 标签全册勘察（P1-8 只读调查，2026-10-06）

> 真源：`docs/01_policies_and_standards/_registry/catalogs/factor_registry.yaml`（175 条）× B 道实测 `docs/_working/fexam/codesym_factor_exam_v1.yaml`（31 条）。结构化同源册：`direction_survey_v1.yaml`。
> 硬纪律：翻案候选**只列候选禁下结论**，翻案必须走 P1-4 式事前假设流程；本册零改源册。

## 一、direction 覆盖率总表

| 口径 | 数值 |
|---|---|
| 总条目 | 175 |
| 已填 | 156（89.1%） |
| 空 | **19**（10.9%） |
| neutral / short / long | 98 / 29 / 29 |
| both / 其他值 | 0 |

- 空 19 条按 class：quality 6、expectations 6、momentum 4、intraday 2、value 1。
- **病呈片状非孤例但非全册**：ICBATCH 代码锚批 5 条（MOM-029/030、QUAL-002、INTRADAY-029/030）+ 基本面粉批 14 条（FQ×6、GR×2、EXP×6）。
- caveat：registry 头注自述 neutral 为 v2.0 默认**占位**，98 条 neutral 含占位存量——已填≠已裁定，真实裁定率或低于 89.1%。

## 二、交叉分析（空 direction × B 道实测）

考池=registry 全部 code_symbol 非空 31 条；19 条空 direction 中 **18 条有码锚、全部入考且全部实测**（MOM-030 无码锚未入考）。实测册 direction_declared 与 registry direction 逐条一致（0 错位）——**MOM-029 根因归因成立，且同病 17 条**。

| class | 空 n | 入考=实测 | verdict | h5 IC 负 | h5 IC 正 | 补向可过线 |
|---|---|---|---|---|---|---|
| momentum | 4 | 3 | rework 2 / retire 1 | 1（MOM-029） | 2 | **1** |
| quality | 6 | 6 | rework 4 / retire 2 | 1（FQ-003） | 5 | 0 |
| expectations | 6 | 6 | rework 6 | 1（EXP-005） | 5 | 0 |
| intraday | 2 | 2 | rework 2 | 2 | 0 | 0 |
| value | 1 | 1 | rework 1 | 0 | 1 | 0 |

### 翻案候选清单（只列候选、禁下结论）

| factor_id | 现值 | 补向 | h5 holdout 补向后 | 三线判定 | caveat |
|---|---|---|---|---|---|
| FCT-MOM-029 20日动量（代码锚） | 空 | **short** | ic 0.0517 / icir 0.310 / retain 0.593 | 三线全过，**icir 擦线（+0.010）** | 三窗 IC 全负号一致、is_ref 同号更负；但 h1 icir 翻后 0.226<0.3 不达（仅 headline 窗过）。**须走 P1-4 事前假设流程** |

其余 17 条实测空 direction 条目补 short/long **均不可过线**：|IC|<0.02（基本面/预期族）或面板退化/覆盖<60%（EXP 族）——翻转不改量级，病不在 direction。

## 三、regime_valid / regime_invalid / entry_role 顺带体检

| 字段 | 已填/总 | 覆盖率 | 备注 |
|---|---|---|---|
| regime_valid | 44/175 | 25.1% | high_vol 25、low_vol 16、panic 8、ranging 5、euphoria 4、trend_down 3、trend_up 3；liquidity 27/37、momentum 26/33、sentiment 19/24、technical 16/29 全空 |
| regime_invalid | **0/175** | **0%** | 头注"翻译拆解因子必须填"强制项**零执行** |
| entry_role | 175/175 | 100% | ranking 157、timing 12、filter 1、**词表外值 factor×5**（恰为 ICBATCH 批，头注默认=ranking，疑漂移） |

- 空 direction 19 条的 regime_valid/regime_invalid 亦全部为空（gap 连片，宜同一工单并补）。
- 另察：factor_class 实际词表溢出头注十类（expectations/knowledge_only/data_asset/risk_rule/technical_indicator）；FCT-QUAL-002 前缀 QUAL 但 class=value。

## 四、补全工单（19 条全列；suggest=候选值非终值，写入仍须工单评审）

### A 栏：能从 code 语义/卡面 hypothesis 客观推导（17 条）

| # | factor_id | 建议 | 依据 | 旗 |
|---|---|---|---|---|
| 1 | FCT-MOM-029 | long | code 原样返回 pct_change(20) 无取负，动量惯例多头 | **conflict**：vs B 道实测反转 short 候选，须 Owner 裁定+翻案走 P1-4 |
| 2 | FCT-MOM-030 | long | 卡面§F8.46"涨速前10=最早买入信号" | |
| 3 | FCT-QUAL-002 | long | code value_signal=1/PE，高=便宜多头惯例 | |
| 4 | FCT-FQ-001 | long | 公式自带负号 -(应计)/TA，Sloan 方向内嵌 | |
| 5 | FCT-FQ-002 | long | 转化效率高=质量好 | |
| 6 | FCT-FQ-003 | long | Novy-Marx 2013 多头口径（deprecated 低优先） | |
| 7 | FCT-FQ-004 | long | ΔROEq 改善=高分 | |
| 8 | FCT-GR-001 | long | 营收成长多头（RevSUE） | |
| 9 | FCT-GR-002 | long | 盈利二阶导为正 | |
| 10 | FCT-FQ-005 | long | 公式自带负号，质量差减分 | |
| 11 | FCT-FQ-006 | long | F-Score 高分多头 | |
| 12 | FCT-EXP-001 | long | EP 高=便宜（华泰多头口径） | |
| 13 | FCT-EXP-002 | long | 上调修正漂移（Gleason & Lee 2003） | |
| 14 | FCT-EXP-003 | long | 上调占比高多头 | |
| 15 | FCT-EXP-004 | long | 异常覆盖度多头（Lee & So 2017） | |
| 16 | FCT-EXP-005 | **short** | 卡面假设：高分歧→未来收益偏低（Diether 2002），反向消费 | |
| 17 | FCT-EXP-006 | long | 评级上调动量多头 | |

### B 栏：必须 Owner 定（2 条）

| # | factor_id | 事由 |
|---|---|---|
| 1 | FCT-INTRADAY-029 盘中VWAP | code 自述"供信号/风控作为基准价读取"，非方向 alpha（ic5=-0.0201、|icir|5=0.09 量级不足）；填 neutral 还是另立 baseline 语义须 Owner 定 |
| 2 | FCT-INTRADAY-030 盘中收盘价 | 同上（基准价件，ic5=-0.0276）；direction 语义须 Owner 定 |

**工单计数：A 栏 17（含 conflict 升级 1：MOM-029）＋B 栏 2 ＝ 19 全覆盖。**

