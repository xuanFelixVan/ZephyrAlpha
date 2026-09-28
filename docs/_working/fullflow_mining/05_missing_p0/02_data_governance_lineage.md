---
ttl: task_bound
volume: 02_data_governance_lineage
session: st-ailayer-final-20260924
creation_token: fullflow-p0-data-gov-lineage-20260926
---

# 02 · 数据资产·血缘·字段字典治理环节（P0，二验成立，**部分挖干**）

> 成立来源＝对账表 **D-3（代码域 `data_governance`）＋ B-8（REG-DATAFLOW-001 数据资产登记表）＋ B-7（REG-FLD-001 字段字典）**，三行同一治理对象族（数据资产元数据与血缘）→ 按宪法 §4.2 并为**一个**新环节。
> 二验结论：F01–F122 无此环节（F 册 `grep -w data_governance`＝0、`grep lineage`＝0、`grep 字典`＝0、`grep 数据资产`＝0）；**ROOR 全文亦零命中 `data_governance`/`lineage`**＝该 3,046 行本体域连注册表归属都没登记。
> 六向中"自动化触发"一向**实测无自主运行证据**（见 §二），故本册判 **部分挖干**，不算完。

## 一、环节定义与边界

- **做什么**：①维护数据资产 SSoT 三实体台账（sources/datasets/jobs，对标 OpenLineage；实测 `data_asset_registry.yaml` **15,517 行**、ROOR 记 entry_count=342、owned_by=governance）；②维护字段字典（`field_dictionary.yaml` **8,280 行 / 7,628 键**）；③产出与消费列级/记录级血缘（`src/zephyr/data_governance/`：`column_lineage_analyzer`、`column_lineage_tracker`、`record_lineage_tracker`、`static_lineage_analyzer`、`runtime_lineage_collector`、`lineage_parser`、`lineage_change_detector`、`ml_lineage_tracker`、`openlineage_exporter`）；④元数据与 schema 登记（`core/metadata_registry.py`、`core/schema_registry.py`）；⑤资产自动发现（`asset_auto_discovery.py`）；⑥血缘变更检测→下游报警。
- **不做什么**：不做采集与落库（F01/F04/F06/F08）、不做数据判重审计（F05）、不做 TDM 交叉轴挂接（F11）、不做血缘的**可视化渲染**（F113"图谱/血缘/瀑布五视图"是**消费端**，本环节是**本体**）。
- **边界冲突（必须登记的病灶）**：实测存在**两个同名包**——`src/zephyr/data_governance/`（21 py，本体）与 `src/zephyr/governance/data_governance/`（含 `akshare_provider.py`、`ch_tick_provider.py`，是 provider 适配）。同词不同指，对账表 V-6。新环节立项时必须择一为真源并给另一条退役/改道登记（**只登记不改动**，遵更正5）。

## 二、六向台账

| 向 | 内容与实测证据 | 是否挖干 |
|---|---|---|
| 上游输入 | ①代码面：全仓 `.py` 与 CH/PG/DuckDB 表结构（被 `static_lineage_analyzer.py`/`lineage_parser.py` 解析）；②外部 provider：`src/zephyr/governance/data_governance/{akshare_provider,ch_tick_provider}.py`；③采集与落库环节的产物＝F01/F04/F06/F08（F 册 :26/:29/:31/:33）；④`market_data_aggregates.py` 派生聚合输入 | ✅ |
| 下游消费 | ①包外真实 import 实测 2 件：`src/zephyr/data/data_service.py`、`src/zephyr/alt_data/alt_data_catalog.py`（`grep -rln "zephyr\.data_governance"` 去自身后）；②字符串级依赖（跨域引用 `data_governance`）实测 8 件：另加 `backtest/core/data_handler.py`、`backtest/core/tick_replay.py`、`ex_core/open_order_resolver.py`、`frontend/dashboard/components/order_book.py` 等；③治理侧：`scripts/governance/d5_architecture/checkers/check_registry_code_anchor.py`、`check_registry_code_fingerprint.py` 读两张台账做代码锚校验；④`generate_registry_master_index.py`、`align_all.py` 消费 `field_dictionary` | ✅ |
| 自动化触发 | 实测**只有提交/审计链上的被动件**：`scripts/governance/d3_metadata/generate_data_asset_coverage.py`（生成器，存在但未证自触发）、`check_registry_consistency.py`、`commit_queue.py` 内含 lineage 字面；**无 sch_* 计划任务、无事件驱动 reconciler、无 AutoRuntime 节律挂载**证据（`grep lineage` 在 `gate_registry.yaml`＝0 命中；无任何门禁以 lineage 为对象）。→ **本向缺一**：该环节"自动触发/自动运行"两要素（宪法 §9.3 永久系统四要素）无实证 | ❌ **待挖** |
| 真源与注册表 | ROOR `REG-DATAFLOW-001` @`docs/registry_of_registries.yaml:669`（name=数据资产登记表、maintenance=**manual**、entry_count=342、status=active、description=「数据资产唯一真源（SSoT）三实体 sources/datasets/jobs」、owned_by=governance）；ROOR `REG-FLD-001` @`:680`；**ROOR 内零命中 `data_governance`/`lineage`**（实测）＝血缘本体无注册表条目；F 体系真源＝**无** | ✅（含 V-7 断链证据） |
| 门禁与质量尺 | ①`tests/data_governance/` 实测 7 件（test_asset_auto_discovery / test_column_lineage_analyzer / test_column_lineage_tracker / test_lineage_change_detector / test_lineage_parser / test_lineage_tracker / test_market_data_aggregates）；②锚校验尺：`check_registry_code_anchor.py`、`check_registry_code_fingerprint.py`（两册→代码指纹对账）；③一致性尺：`check_registry_consistency.py`；④**提交门禁零覆盖**（gate_registry 无 DATA-ASSET/LINEAGE 门，实测 0 命中）＝尺子在但无硬拦 | ✅ |
| 当前运行状态 | **黄**：本体在盘（21 py / 3,046 行，`__init__` 头注 `[MATURITY] production`、`[STARTUP] imported`）、测试在盘、两张大台账 active（15,517/8,280 行）；**但三处黄转红风险**：①ROOR 记 maintenance=manual 而 `generate_data_asset_coverage.py` 生成器存在＝手工/机生口径冲突（违宪法 §9.5"条目清单必生成器产出"）；②血缘无门禁、无自动触发＝环节不闭环；③包 `__init__` 头注 `[BLUEPRINT] MOD-DATA_GOV | (pending)`、`[TESTS]` 空＝蓝图与测试指针未填 | ✅（判黄） |

**挖干判据自查**：六向中五向有 file:line 或可复跑命令实测，**"自动化触发"一向证据为负**（不是没找，是找遍 gate_registry/计划任务/reconciler 面均无）→ 本册判**部分挖干**，不算完；缺什么已在该向写明。

## 三、子模块清单（ls＋grep＋注册表交叉实测）

`src/zephyr/data_governance/` 实测 21 py（其中 14 非 `__init__`）/3,046 行；一级子包 `api/ core/ infrastructure/ models/ services/ _extensions/`：

| # | 子件（相对 `src/zephyr/data_governance/`） | 行数面 | 角色 | 状态 |
|---|---|---|---|---|
| 3.1 | `core/column_lineage_analyzer.py`、`column_lineage_tracker.py` | 列级血缘双件（analyzer＋tracker） | 本体 | 测试在盘（黄：双件职责重叠未判） |
| 3.2 | `core/lineage_parser.py`、`core/lineage_tracker.py` | 解析＋总跟踪 | 本体 | 绿（各有测试） |
| 3.3 | `core/record_lineage_tracker.py`、`core/static_lineage_analyzer.py`、`core/runtime_lineage_collector.py` | 记录级／静态／运行时三路血缘 | 本体 | 黄（运行时采集是否有触发未证） |
| 3.4 | `core/metadata_registry.py`、`core/schema_registry.py` | 元数据与 schema 登记 | 本体 | 黄（与 B-7 字段字典、F06 CH DDL 的派生方向未定） |
| 3.5 | `asset_auto_discovery.py` | 资产自动发现（喂 15,517 行台账） | 生产端 | 黄（触发方式未证＝§二 自动化触发向） |
| 3.6 | `lineage_change_detector.py` | 血缘变更检测 | 报警端 | 黄（下游消费者未实测到） |
| 3.7 | `openlineage_exporter.py` | 对外 OpenLineage 导出 | 出口 | 黄（是否有消费端未证） |
| 3.8 | `ml_lineage_tracker.py` | ML 血缘（对账表 D-6/D-7 的交叉面） | 跨界 | 黄 |
| 3.9 | `market_data_aggregates.py` | 行情聚合（与 D-5 `market_data` 包双真源嫌疑） | 跨界 | 待裁 |
| 3.10 | 台账件：`data_asset_registry.yaml`（15,517 行）、`field_dictionary.yaml`（8,280 行/7,628 键） | 数据面 | 真源 | active（ROOR 在案） |
| 3.11 | 治理侧生成/校验：`scripts/governance/d3_metadata/generate_data_asset_coverage.py`、`check_registry_consistency.py`、`d5_architecture/checkers/check_registry_code_{anchor,fingerprint}.py` | 尺子 | 外围 | 在盘 |
| 3.12 | 同名异物包 `src/zephyr/governance/data_governance/`（akshare_provider/ch_tick_provider 等） | 干扰面 | 待裁定归属 | 红（V-6） |

## 四、堵点与病灶

| # | 现象 | 根因 | 修法草案 | 工作量 | 本车道可修 |
|---|---|---|---|---|---|
| 1 | 3,046 行本体域在 ROOR 零登记，与被它治理的两张大册之间无"生产者→注册表"关系 | 域未编目（对账表 V-7/V-9：能力卡 0 命中、模块翻译登记 0 命中） | 新环节行＋ROOR 补条目（`physical_path` 指包、`generator` 指生成器）＋能力卡补建 | 1 施工袋 | 否（ROOR 热册，车道禁改） |
| 2 | 无自动触发＝环节非"永久系统"（宪法 §9.3 四要素缺二） | 血缘只在按需调用路径上 | 事件触发方案（表结构变更/新表登记→reconciler），**禁 cron/Timer/sleep-loop** | 1–2 施工袋 | 否 |
| 3 | 血缘/字段/资产三面无任何提交门禁 | 治理面尺子只在审计链跑 | 新增 own-scope 门（staged 数据类文件变更时验台账同步），或明确"全仓扫描"理由登记（宪法 §3.3） | 1 施工袋 | 否 |
| 4 | `maintenance: manual` 与生成器并存＝手工台账必漂移（宪法 §9.5） | 生成器上线后 ROOR 口径未刷新 | 刷新 ROOR 口径＋计数改派生字段（§4.3） | 小 | 否 |
| 5 | 双同名包（3.12） | 历史域拆分未收口 | 先登记"同词不同指"，归属待裁（**只登记不改动**） | 中 | 否 |
| 6 | 环节无 F 位 | 122 不完备 | F 册新增行（建议 A/K 交界，占位编号交总筹） | 文档 | 否 |

## 五、内收与合并机会

1. **同真源可派生→必并**：B-7（字段字典）＋B-8（数据资产台账）＋D-3（血缘本体）并为本 1 环；若 F 册按上棒方案各开一行＝造 3 条假环节（终数因此虚高，见对账表 §三）。
2. **与 B-9 的关系**：上棒 P0①"DB schema 迁移"若将来立成环节，其 schema 版本真源应与本环节 `core/schema_registry.py` 同一对象→**必并**（现判该 P0 不成立，见对账表 B-9 行）。
3. **与 F113 的关系**：血缘**渲染**归 F113（消费端），本环节归本体→**跨域不同对象→不并**，但要建立"本体→视图"的引用（F113 真源字段现只写渲染器 5 件，无血缘来源锚点）。
4. **与 F05/F06/F01 的关系**：判重审计、CH DDL、采集调度各自保留环节；本环节只提供资产/schema/字段的登记真源，禁止把三者的业务动作迁入（否则 F 册出现语义黑洞）。
5. 候选并入项（可选，省 1 环）：D-4 `data_security`（脱敏/访问审计 724 行）与本环节同为"数据面治理"，但**语义不同对象**（安全 vs 元数据）；默认不并，若总筹按窄口径可并成"数据治理与安全"1 环。

## 六、自审闸三态

**部分挖干**（不满足封矿判据）：六向中 5 向有实证，**"自动化触发"向实测为零证据**（已给出检索面：`gate_registry.yaml` 无 lineage/DATA-ASSET 条目、无计划任务、无 reconciler 挂载）→ 缺的就是这一向，列 §二 该行。
可派施工范围：ROOR 补登记＋事件触发设计＋own-scope 门（三条均须另开工单，本车道零施工）。
**待挖**：①14 个实体件→F01/F05/F06/F08/F11/F113 的逐件归属表（判"环内缺口 vs 环缺位"的最终依据）；②`src/zephyr/governance/data_governance/` 与本体包的件级差异；③血缘是否被 AutoRuntime 任一 job 消费（`data/capability_cards` 0 命中，需查 trading_contracts/job 清单）。
**待裁**：P-4（双同名包归属）、P-5（market_data_aggregates 与 `market_data` 包双真源）→ 见 `pending_rulings.md`。

## 七、复核命令

```bash
cd /d/ZephyrAlpha/.worktrees/st-ailayer-final-20260924
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$PATH"; python --version
S=docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md
# 1 环节无位（预期四项皆 0）
grep -c -w data_governance $S; grep -c lineage $S; grep -c 字典 $S; grep -c 数据资产 $S
# 2 本体域规模（预期 14 非 init / 3,046 行）
find src/zephyr/data_governance -name "*.py" ! -name __init__.py | grep -v __pycache__ | wc -l
find src/zephyr/data_governance -name "*.py" ! -name __init__.py | grep -v __pycache__ | xargs wc -l | tail -1
# 3 ROOR 零登记（预期 0 命中）＝V-7 断链
grep -rn "data_governance\|lineage" docs/registry_of_registries.yaml | wc -l
grep -n "registry_id: REG-DATAFLOW-001" -A10 docs/registry_of_registries.yaml | cut -c1-150
grep -n "registry_id: REG-FLD-001" -A9 docs/registry_of_registries.yaml | cut -c1-140
# 4 两张台账规模（预期 15,517 / 8,280 行）
wc -l docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml docs/01_policies_and_standards/_registry/catalogs/field_dictionary.yaml
# 5 真实 import 消费方（预期包外 2 件）
grep -rln "zephyr\.data_governance" src/zephyr scripts | grep -v __pycache__ | grep -v "^src/zephyr/data_governance"
# 6 自动化触发向＝负证据复跑（预期全 0）
grep -c -i "lineage\|DATA-ASSET" docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml
# 7 测试与尺子在盘（预期 7 件）
ls tests/data_governance/*.py | grep -v __init__ | wc -l
ls scripts/governance/d3_metadata/generate_data_asset_coverage.py scripts/governance/d5_architecture/checkers/check_registry_code_fingerprint.py
# 8 双同名包（V-6，预期两包并存）
ls -d src/zephyr/data_governance src/zephyr/governance/data_governance
# 9 包头注口径（预期 MATURITY production / BLUEPRINT (pending) / TESTS 空）
sed -n '1,16p' src/zephyr/data_governance/__init__.py | cut -c1-120
```
