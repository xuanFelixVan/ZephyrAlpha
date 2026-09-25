---
ttl: task_bound
lane: M1 数据链
segment: D11 TDM 交叉轴挂接 + D12 产业链图谱数据面
mined_at: 2026-09-25
session: st-commitspeed-tbl-20260924
---

# 05_tdm_crossaxis — TDM 交叉轴作业簿（D11/D12）

## 一、环节定义与边界

一句话：把数据资产（dataset）与 13 条业务库交叉轴挂到 TDM 决策地图节点上，新库/新表有挂接义务；873 条产业链图谱经生成器入值域。
- **供料方**：data_asset_registry（295 datasets）← business_data_categories（338 品类）← CH 实表（252）；chain_registry ← PG ig_chain 族（机生）。
- **消费方**：decision_map.py 校验器（R26-R45 门禁）、TDM 前端画布（M6）、alignment_checklist 对齐键。

## 二、六向台账

| 向 | 内容与实证 |
|---|---|
| 上游输入 | CH/PG 实体库（03 册）+ 各域 registry YAML（catalogs/ 实列 20 件）+ PG ig_chain 生成源 |
| 下游消费 | decision_map.py:955（六核心注册表+13 轴文件缺失即 R99 error）；:713 _check_xref_libraries（轴存在性+容量表驱动）；TDM 画布/晨报消费 |
| 自动化触发 | chain_registry.yaml=**生成器机生**（scripts/governance/generate_chain_registry.py，生成物禁手改，decision_map.py:115-117 注）；文件重命名后 generate_project_depgraph.py --force（宪法 §9.10）；对齐=align_all.py 单入口（宪法 §8） |
| 真源与注册表 | 轴定义表驱动真源=src/zephyr/trading/decision_map.py:100-118 `_XREF_SPECS` **13 轴**：PAT 形态/SEAT 席位/MAC 宏观指标/CYC 周期/UNI 宇宙/CST 成本模型/EVT 事件日历/RLM 风险限额/PFM 组合模型/BMK 基准/THD 告警阈值（R26-R36）+ML 模型（R38，D38 补挂）+CHN 传导链（R45，v2.0 扩容）；容量上限表=_XREF_MAX :119-133；dataset 值域=data_asset_registry.yaml（**295 dataset_id** grep 实数）；产业链=chain_registry.yaml（873 条口径见骨架册 D12） |
| 门禁与质量尺 | R99 注册表真源缺失=error（:957-959 禁假阴性）；轴引用值域校验+超容量=粒度门禁；ALGO-NOTE-SYNC/链值域封闭（chain 机生禁手改）；业务资产库新库/新表挂接义务=AGENTS.md §8 + _XREF_SPECS 表驱动"新增库只需加一行"（:99 注） |
| 当前运行状态 | **绿**。catalogs/ 实列：13 轴注册表文件全部在盘（含 data_asset/strategy/factor/execution_algo/technical_indicator/decision_algo 六核心=19 文件全家福）；未发现轴文件缺失（R99 前提满足）。**数量口径账**：AGENTS.md §8 与骨架册 D11 均写"业务资产库 **16 表**挂交叉轴"，而 _XREF_SPECS 实为 **13 轴**、decision_map 全家福注册表为 **19 件**——L0 宪法表述与代码漂移（入 pending_rulings，建议改宪法为"13 轴表驱动"或口径注明） |

## 三、子模块清单（轴注册表逐条，catalogs/ 实列交叉 decision_map.py:102-117）

| 轴 | 注册表文件 | 门禁码 | 容量上限 |
|---|---|---|---|
| 形态库 PAT | chart_pattern_registry.yaml | R26 | 12 |
| 席位库 SEAT | seat_registry.yaml | R27 | 8 |
| 宏观指标库 MAC | macro_indicator_registry.yaml | R28 | 12 |
| 周期库 CYC | regime_cycle_registry.yaml | R29 | 8 |
| 宇宙库 UNI | universe_registry.yaml | R30 | 4 |
| 成本模型库 CST | cost_model_registry.yaml | R31 | 4 |
| 事件日历库 EVT | event_calendar_registry.yaml | R32 | 8 |
| 风险限额库 RLM | risk_limit_registry.yaml | R33 | 12 |
| 组合模型库 PFM | portfolio_model_registry.yaml | R34 | 4 |
| 基准库 BMK | benchmark_registry.yaml | R35 | 4 |
| 告警阈值库 THD | alert_threshold_registry.yaml | R36 | 8 |
| 模型库 ML | model_registry.yaml | R38 | 4 |
| 传导链库 CHN | chain_registry.yaml（机生） | R45 | 8 |
| 数据资产（data_refs） | data_asset_registry.yaml（295 datasets） | V 校验族 | _MAX_DATA_REFS=8/节点 |
| 产业链图谱 D12 | chain_registry.yaml 同源；data_audit_sop/industry_chain_data_audit_policy=审计修复循环 | — | — |

旁证：catalogs/ 目录现存 `alert_threshold_registry.yaml.tmp.21732.70ad97c19748` CAS 残留件（safe_write 中断残迹）——热文件卫生见 06 册 manifest。

## 四、堵点与病灶

| # | 现象 | 根因 | 修法草案 | 工作量 | 本车道可修 |
|---|---|---|---|---|---|
| T1 | "16 表"口径漂移：宪法 L0 §8/骨架册 D11 写 16，代码实为 13 轴（+6 核心注册表=19 文件；#ARCH-351 另有"哨兵 16 表"旧口径混淆源） | 宪法换版（#ARCH-310 R3）时数量未随 _XREF_SPECS 扩容（R38/R45 两次加轴）同步 | 宪法等长替换一行："业务资产库 13 轴表驱动挂 TDM 交叉轴"（或口径注明基准日期+指向代码真源） | 0.1 天 | 是（提请总筹走宪法替换通道） |
| T2 | 新表挂接义务无机械化检查：business_data_categories 新增品类后，data_asset_registry datasets 与 TDM data_refs 是否跟进全凭人记 | 挂接义务无对账器 | align_all 或新对账步骤加"品类↔dataset↔data_refs 三层覆盖率"报告（先WARN） | 1 天 | 是 |
| T3 | 病灶闭环核验：①"75 库盘点唯一真缺口"=ML 库→D38 补挂**已闭环**（:113-114 注）；②传导链轴 v2.0 吸收对齐 583/873 禁重画**已闭环**（:115-117）；③R21 死锁残留（旧连字符正则与缓存一致性互斥）→2026-09-16 复核班放宽**已闭环**（:95 注） | — | — | — | — |

## 五、提速与合并机会

1. _XREF_SPECS 与 _XREF_MAX 两表可合一（容量并入 spec 元组）——少一处漂移面。
2. chain_registry 机生模式（生成器+禁手改）是全注册表族的标杆：data_asset_registry 295 datasets 中"表级品类镜像"部分可改由 business_data_categories 派生生成，消双层手维。

## 六、自审闸三态

**挖干可施工**（T2 对账器可施工；T1 宪法措辞=总筹通道）。D12 产业链图谱数据面（873 条）真源与审计 SOP 已锚定；图谱内容质量挖掘归 M8/数据审计专项，不在本册重复。

## 七、复核命令

```bash
sed -n '100,133p' src/zephyr/trading/decision_map.py          # 13 轴+容量表
ls docs/01_policies_and_standards/_registry/catalogs/ | grep -E "pattern|seat|macro_indicator|regime_cycle|universe|cost_model|event_calendar|risk_limit|portfolio_model|benchmark|alert_threshold|model_registry|chain_registry|data_asset"  # 轴文件全家福
grep -c "dataset_id:" docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml  # 295
grep -n "16 表" AGENTS.md docs/_working/fullflow_mining/00_skeleton_fullflow.md  # 口径漂移证据
sed -n '953,960p' src/zephyr/trading/decision_map.py          # R99 真源缺失=error
```
