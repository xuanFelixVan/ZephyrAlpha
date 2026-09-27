---
ttl: task_bound
title: "F11 TDM 交叉轴挂接——13 轴表驱动×dataset 值域×口径漂移终结复飞案卷"
session: zc-l01-20260927
---

# F11 TDM 交叉轴挂接（复飞案卷）

> 前序：M1 册 05_tdm_crossaxis.md+补挖波 10_f11_xref_counting_drift.md（口径考古终结）；本卷=当日代码实测复核+勘误传递。

## 一、六向台账（本日实核）

| 向 | 内容与实证 |
|---|---|
| 上游 | CH/PG 实体库+catalogs/ 各域 registry YAML+PG ig_chain 生成源（chain_registry 873 条机生，本日 grep 实数 873 ✓） |
| 下游 | decision_map.py R26-R45 门禁校验器；TDM 画布（M6）；alignment_checklist 对齐键；data_asset_registry 295 datasets（本日实数 ✓）为 data_refs 值域 |
| 自动触发 | chain_registry=生成器机生（generate_chain_registry.py，禁手改，decision_map.py:115-117 注）；对齐=align_all.py 单入口；R99 文件缺失即 error（:955-959） |
| 真源注册表 | 轴表驱动真源=decision_map.py:100-118 `_XREF_SPECS`（**本日 sed+grep 复核 13 轴**）+_XREF_MAX :119-133；19 文件全家福（6 核心+13 轴）catalogs/ 在盘 |
| 门禁质量尺 | R99 真源缺失=error（禁假阴性）；轴值域校验+超容量粒度门禁；ALGO-NOTE-SYNC；新库挂接义务=_XREF_SPECS 表 §4 |
| 运行状态 | **绿（代码）红（文本）**：代码 13 轴 19 文件自洽运转；宪法 AGENTS.md §8 与 agent_constitution_l0.md:119 双副本仍写"16 表"（R-M1-05 修宪证据包已交付未落地） |

## 二、子模块三级枚举

1. 轴注册表 13 件（10 册全表：PAT R26/SEAT R27/MAC R28/CYC R29/UNI R30/CST R31/EVT R32/RLM R33/PFM R34/BMK R35/THD R36/ML R38/CHN R45+容量上限）
2. 六核心注册表：data_asset（295）/strategy/factor/execution_algo/technical_indicator/decision_algo
3. 挂接校验：decision_map.py :713 _check_xref_libraries（轴存在性+容量表驱动）+:955 R99 循环
4. 产业链轴：chain_registry.yaml（873，机生禁手改）+generate_chain_registry.py（真源 PG ig_chain）
5. 相邻账：L00 §二 B-8 判 REG-DATAFLOW-001 数据资产册（15517 行）并入 F11——本卷登记：并入后 data_asset_registry 与数据资产册双册关系待收敛（同域重复簇嫌疑，内收判据 w5_1 条 3）

## 三、接线四态独立复核

- 总册：built（口径漂移：宪法称 16 表/代码 13 轴）/P1/D11。独立复核：**built 成立+漂移定性精确**（10 册考古：16=R99 文件数 09-07 时点冻结，13=现行轴数，错在 09-12 换版量纲"个"→"表"）。
- 本日新增实测：chain_registry 873 ✓（与骨架一致，无漂移）；data_asset_registry 295 ✓；_XREF_SPECS 13 ✓——三数全对上，代码面零漂移。
- 勘误⑯：总册 F11 真源列写"decision_map.py:100（_XREF_SPECS 13 轴）"正确；但 05 册 §三记 catalogs/ 存在 alert_threshold_registry.yaml.tmp.21732.* CAS 残留件——本日未复扫（热文件卫生账挂 06 册 manifest），列入待裁节不判缺失。

## 四、缺口清单

| # | 缺口 | 处置 | 级 |
|---|---|---|---|
| X1 | 宪法"16 表"双副本漂移 | 施工：等长替换"业务资产库 13 轴表驱动挂 TDM 交叉轴（_XREF_SPECS，R99 全家福 19 注册表）"——提请总筹走宪法替换通道（10 册 T1'/T1'' 证据包版） | P1 |
| X2 | 品类↔dataset↔data_refs 三层覆盖率无对账器（挂接义务凭人记） | 施工：align_all 加覆盖率报告（先 WARN） | P1 |
| X3 | _XREF_SPECS/_XREF_MAX 两表可合一 | 施工：容量并入 spec 元组（少一处漂移面） | P2 |
| X4 | 数据资产册并入后的双册收敛 | 挂起+解锁=裁-5 改写授权+内收判据评审 | P2 |
| X5 | CAS 残留件（alert_threshold_registry.tmp） | 施工：热文件卫生清扫批（只清 tmp 残件不动正身） | P2 |

## 五、自审闸三态

挖干可施工（05/10 册+本日三数实测复核）；X2/X3/X5 可施工；X1=总筹宪法通道；X4 挂起裁-5。总册判定沿用处已注明。

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
sed -n '100,118p' src/zephyr/trading/decision_map.py | grep -c '("'    # 13
grep -c "^- {chain_id" docs/01_policies_and_standards/_registry/catalogs/chain_registry.yaml   # 873
grep -c "dataset_id:" docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml   # 295
ls docs/01_policies_and_standards/_registry/catalogs/ | grep -cE "pattern|seat|macro_indicator|regime_cycle|universe|cost_model|event_calendar|risk_limit|portfolio_model|benchmark|alert_threshold|model_registry|chain_registry|data_asset"   # 全家福
grep -n "16 表" AGENTS.md   # 漂移文本仍在
```
