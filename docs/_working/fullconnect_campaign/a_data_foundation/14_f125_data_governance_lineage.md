---
ttl: task_bound
title: "F125 data_governance 数据治理本体（血缘/元数据/schema 注册）复飞案卷"
session: st-c7-mine-20260927
---

# F125 data_governance 数据治理本体（A·K 交界，主归 A 段，P0，骨架态=unmined(new id)）

> 立卷依据：`00_skeleton_verified.md` §二 D-03 行——"`data_governance`（21 py）→ F125（P0，A/K 交界，数据治理本体）"。包内件数经本卷实核=21（§六 P1），与骨架口径逐字吻合。
> **本卷首要结论（红）**：该包在 HEAD 上有 21 件实现 + 15 件测试，但**生产面零 import**（AST 全仓判定，§六 W1 输出 PROD=0），全部跨包引用只存在于注释与测试里。按本仓四态口径=**装饰**，不得因"件数多/测试全绿/在册"判已接线。

## 一、六向台账（2026-09-27 实证，基准=HEAD 3b4b1f86a1）

| 向 | 实测证据 |
|---|---|
| 实现件 | `src/zephyr/data_governance/`（21 .py 在 HEAD，§六 P1 计数）：血缘族 `core/lineage_tracker.py`+`core/column_lineage_analyzer.py`+`core/record_lineage_tracker.py`+`core/runtime_lineage_collector.py`+`core/static_lineage_analyzer.py`+`core/lineage_parser.py`+`column_lineage_tracker.py`+`lineage_change_detector.py`+`ml_lineage_tracker.py`+`openlineage_exporter.py`；注册族 `core/metadata_registry.py`+`core/schema_registry.py`+`asset_auto_discovery.py`；投影族 `market_data_aggregates.py`；骨架目录 `api/ services/ models/ infrastructure/ _extensions/` 五只 `__init__.py` 空层。M1 台账 dir3=`dirs_in_head {src/zephyr/data_governance: 16}`（16 为非 `__init__` 件口径，两口径差 5 恰等于骨架目录占位件数，§六 P1/P2 并列可复算）。 |
| 在册态 | 三层术语册全覆盖：`module_translation_registry.yaml` 命中 **34** 处、`candidate_module_registry.yaml` 命中 **33** 处（§六 R1 两条 grep 计数，路径前缀口径 `zephyr.data_governance`/`zephyr/data_governance`）。契约层在册：`.importlinter:29` 列 `zephyr.data_governance` 为受契约约束层；`architecture_model/contracts/error_code_registry.yaml:3025/3030/3035…` 逐模块登错误码（`module: zephyr.data_governance.asset_auto_discovery` 等）。⇒ **在册态=绿**，且是本环节四态里唯一确证通的面向。 |
| 消费者 | **生产消费者=0（AST 实测）**。跨包出现的全部三处均为非代码引用，逐条否证：<br>①`src/zephyr/data/data_service.py:4` `[DEPENDENCIES] … zephyr.data_governance.core.lineage_tracker …`——头部声明，但该文件 AST 内**无对应 import**（§六 W1/W2），且 :29 自述"后端全部注入式（… lineage_tracker …）"＝注入而非导入；<br>②`src/zephyr/alt_data/alt_data_catalog.py:4` `[DEPENDENCIES] 无（… 血缘语义参照 zephyr.data_governance.core.lineage_tracker）`——自述"参照"，:25 亦仅散文；<br>③`src/zephyr/infrastructure/asset_inventory/__init__.py:175` 注释原文="`zephyr.data_governance.asset_inventory 不存在（Test-Path=False，复制残留）`"——**在册名指向一个包内不存在的模块**，是自我否证。测试消费者=15 件（§六 T1）。M1 台账 dir4 的 symbol_evidence 只到 `AssetType`/`ColumnLineageError` 两族，且 `AssetType used by src/zephyr/knowledge/research_catalog.py` 未经 import 面复核，本卷不采信（§六 C2 复核口径）。 |
| 测试 | 15 件测试文件命中本包（§六 T1），代表锚点：`tests/data_governance/test_column_lineage_analyzer.py:28-29`、`tests/data_governance/test_openlineage_exporter.py:29`、`tests/data_governance/test_schema_registry.py:20`。M1 台账 dir5.files 只列 5 件（采集截断），实测宽于机采。测试全绿不等于接线：测试是**唯一**消费者时，绿只证明件自洽。 |
| 自动化触发 | **零**。dir6 六向机采 wide=false/narrow=false；本卷补人工检索亦零命中：`git grep -ln "data_governance" HEAD -- '*.ps1' 'config/*' 'scripts/*.py'` 的生产触发腿不存在（§六 A1）。血缘变更检测器 `lineage_change_detector.py` 名字暗示常驻，实为按需调用件、无排班、无事件源挂载。 |
| 真源方向 | 架构数据=DB（depgraph）：本包模块身份应经 `apply_depgraph.py --add-design-node` 登记，落库由 `generate_project_depgraph.py` 采集；血缘语义真源归属**未定**——`core/lineage_tracker.py`（代码实现）、`ml_lineage_tracker.py`、`column_lineage_tracker.py`、`openlineage_exporter.py`（导出）与 depgraph `edges` 表之间无派生关系声明。规则数据侧无 YAML 册对应本环节。⇒ RULE-SSOT 判定悬空，是 P0 记账项（§四 缺 2）。 |
| 门禁与质量尺 | 契约面在：`.importlinter` 层约束 + `error_code_registry.yaml` 错误码在册；故"包不能反向依赖上层"这类边界有尺。业务效果面**无尺**：不存在任何 gate 检查"血缘边是否真被写入"（§六 G1）。这正是本环节从"在册"滑向"装饰"而无人报警的原因。 |
| 运行状态 | **红（装饰态确认）**：实现全在盘、测试全在跑、注册全在册，运行链路零通。 |

## 二、子模块三级枚举（21 件逐件，按族收敛）

1. **血缘族（10 件）**
   - 二级=核心引擎：`core/lineage_tracker.py`（有向图实现基座）
   - 三级=按粒度切：列级 `core/column_lineage_analyzer.py` / `column_lineage_tracker.py`；记录级 `core/record_lineage_tracker.py`；ML 资产级 `ml_lineage_tracker.py`
   - 三级=按获取方式切：静态解析 `core/static_lineage_analyzer.py` + `core/lineage_parser.py`；运行时采集 `core/runtime_lineage_collector.py`；变更检测 `lineage_change_detector.py`；对外导出 `openlineage_exporter.py`（OpenLineage 标准）
2. **注册族（3 件）**：`core/metadata_registry.py`（元数据）｜`core/schema_registry.py`（schema）｜`asset_auto_discovery.py`（资产自动发现）
3. **投影族（1 件）**：`market_data_aggregates.py`
4. **骨架占位族（5 件 `__init__.py` + 包 `__init__.py`）**：`api/`、`services/`、`models/`、`infrastructure/`、`_extensions/` —— 五层目录只有 `__init__.py`，无实现件（§六 P3 可复算：这五层非 `__init__` 件数=0）。⇒ 该包是按分层模板建的骨架，实际件全落在根层与 `core/`。
5. **对外接缝（非本包件，但属本环节枚举义务）**：`src/zephyr/alt_data/alt_data_catalog.py:126` `lineage_sink: Callable[[str,str,str], None] | None = None`、:263-264 未注入即 `raise AltDataCatalogError("lineage_sink 未注入（血缘强制回调登记，禁止旁路）")`。

## 三、接线四态独立复核

**判定=装饰（非半接线）**，判据链三条，缺一不立：

1. **生产 import 面**：AST 全仓扫描（§六 W1）把 `zephyr.data_governance*` 的 import 节点按 PROD/TEST/TYPE_CHECKING 三态归类，结果 **PROD=0 / TEST=18 条 import 语句（分布 15 文件）/ TC=0**。零 PROD import 是"装饰"的硬前提，本环节满足。
2. **注入接缝无供方（本仓最常见假绿形态，专门测）**：`alt_data_catalog` 的血缘是**依赖注入**式接缝，不看 import 看谁传参。实测 `lineage_sink` 的**非测试供给方=0**（§六 W3）：全仓仅 `tests/alt_data/test_alt_data_catalog.py:200` 与 `tests/ml_train/test_research_data_manager.py:128` 两处用 lambda 传入。**决定性补强**：生产装配点 `src/zephyr/alt_data/alt_source_bootstrap.py:258` 实写 `catalog = AltDataCatalog(clock=clock, fts_connection=fts_connection)`——**未传 lineage_sink**，取默认 `None`（:126 形参默认值），于是 :263-264 的 Fail-Closed 分支成为该装配路径下挂血缘的唯一出口。⇒ 本环节的血缘能力在真实装配里是"接了口但没人插"，生产血缘边写入量=0。两种情形下 F125 对真实数据链路的贡献都是**零**：走挂血缘即抛、不走则永不抛——这正是"守卫/接缝存在但无供给方喂它 = 装饰"的教科书实例。
3. **在册态不能救场**：34 处翻译册命中 + 33 处候选册命中 + `.importlinter` + 错误码在册，全部是登记面；`asset_inventory/__init__.py:175` 更证明登记面会指向不存在的模块（`data_governance.asset_inventory` 包内查无）。⇒ 名册计数与运行连通性无因果，本卷按 §三.1/.2 定罪，不按名册免罪。
4. **半接线为什么不成立**：半接线要求"部分腿通"。本包四条外联可能性中，注入腿（无供方）、注释腿（非代码）、名册腿（登记面）、错误码腿（自我声明）**均不构成运行时通路**，故无"部分通"可言。
5. **同批横向对照**（防以偏概全）：同夜实测 ml_train PROD=5 条真 import、nlp PROD=9 条、infra_ops PROD=1 条——证明本仓存在真被消费的包，F125 的 PROD=0 是**该包自身缺陷**而非扫描口径失效。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | 生产零消费：21 件包整体为装饰态，血缘能力未接入任何真实数据链路 | 施工（二选一，须总筹定方向）：A=把 `core/lineage_tracker` 作为 `lineage_sink` 供方接入 `alt_data_catalog` 与 `data_service` 的构造点并补红样；B=本环节转挂起，登记为"未接线待排期"，禁在施工波中被当作已有能力引用 | P0 |
| 2 | 真源方向未定：血缘语义究竟以 `lineage_tracker.py` 代码、`openlineage_exporter` 导出件、还是 depgraph `edges` 表为真源，无声明 | 挂起：属 RULE-SSOT 判定面，须立法件定档后回填本卷；挖矿道不自裁真源 | P0 |
| 3 | `infrastructure/asset_inventory/__init__.py:175` 记录的"复制残留"死名（指向不存在的 `data_governance.asset_inventory`）仍在权威链上 | 施工：清死名并核 `candidate_module_registry.yaml`（33 处命中内）是否含同名条目；禁手工点删热册（根宪法 §1.13） | P1 |
| 4 | 五个分层目录（api/services/models/infrastructure/_extensions）零实现件＝纯骨架 | 挂起：净零判据（根宪法 §4.2）下是否收敛由治理侧定；本卷只登记"骨架层无件"事实 | P2 |
| 5 | 无"血缘边是否真写入"的效果尺（§六 G1），导致本环节红态长期不可见 | 施工：新增效果型判据（读侧计数），落点须 own-scope（根宪法 §3.3），禁全仓扫描 | P1 |
| 6 | depgraph 是否已收录本包 21 件，本卷未连库实测（PG 直连凭据未取） | 挂起：与 F07 卷缺 1 同因（凭据通道），复跑命令见 §六 D1 | P1 |

## 五、自审闸三态

**未干（但主结论已定）。** 已定且可复算的：生产零 import、注入无供方、在册态三层计数、21 件三级枚举、五骨架目录零实现——这五项足以支撑"装饰/P0 红"的判读并可直接转工单。未干的原因：①`core/lineage_parser.py` 的 SQL 解析覆盖面（能吃哪些方言、能吃几张真实表）未测，那是"若接线则能力多大"的定量前提；②`openlineage_exporter.py` 的输出契约是否与 OpenLineage 官方 schema 对齐未核；③缺 6 的 depgraph 在册面未实测。⇒ 本卷交"红线 + 未干"，不盖挖干章。

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
cd /d/ZephyrAlpha
# P1 包件数（期望 21）
git ls-tree -r --name-only HEAD src/zephyr/data_governance | wc -l
# P2 非 __init__ 件数（期望 16，对齐 M1 dir3 口径）
git ls-tree -r --name-only HEAD src/zephyr/data_governance | grep -v "__init__.py" | wc -l
# P3 五个骨架目录零实现自证（期望全 0）
for d in api services models infrastructure _extensions; do echo "$d=$(git ls-tree -r --name-only HEAD src/zephyr/data_governance/$d | grep -vc '__init__.py')"; done
# W1 决定性测量：PROD / TEST / TYPE_CHECKING 三态 import 计数（期望 PROD=0）
python -c "
import ast,subprocess,collections
f=collections.Counter()
files={l.split(':',1)[1] for l in subprocess.run(['git','grep','-l','zephyr.data_governance','HEAD','--','*.py'],capture_output=True,text=True,encoding='utf-8').stdout.split()}
for p in sorted(files):
    if p.startswith('src/zephyr/data_governance/'): continue
    s=subprocess.run(['git','show','HEAD:'+p],capture_output=True,text=True,encoding='utf-8',errors='replace').stdout
    if not s.strip(): continue
    try: t=ast.parse(s)
    except Exception: continue
    tc={n.lineno for i in ast.walk(t) if isinstance(i,ast.If) and 'TYPE_CHECKING' in ast.dump(i.test) for n in ast.walk(i) if isinstance(n,(ast.Import,ast.ImportFrom))}
    for n in ast.walk(t):
        ms=[n.module] if isinstance(n,ast.ImportFrom) and n.module else ([a.name for a in n.names] if isinstance(n,ast.Import) else [])
        for m in ms:
            if m.startswith('zephyr.data_governance'):
                k='TC' if n.lineno in tc else ('TEST' if p.startswith('tests/') else 'PROD')
                f[k]+=1; print(k,p+':'+str(n.lineno),m)
print('SUMMARY',dict(f))"
# W2 注释腿否证（[DEPENDENCIES] 声明但无 import）
grep -n "\[DEPENDENCIES\]" src/zephyr/data/data_service.py | head -1
git grep -n "^from zephyr.data_governance\|^import zephyr.data_governance" HEAD -- 'src/zephyr/data/data_service.py' 'src/zephyr/alt_data/alt_data_catalog.py' | wc -l
# W3 注入接缝供方实测（期望：排除 alt_data_catalog 自身后命中数=0）
git grep -n "lineage_sink *=\|lineage_sink=" HEAD -- '*.py' ':!tests/*' ':!src/zephyr/alt_data/alt_data_catalog.py' | wc -l
git grep -n "AltDataCatalog(" HEAD -- '*.py' ':!tests/*' | head
# C2 symbol 腿复核（M1 报的 AssetType 消费是否经 import）
git grep -n "AssetType" HEAD -- src/zephyr/knowledge/research_catalog.py | head -3
# T1 测试文件数（期望 15）
git grep -l "zephyr\.data_governance" HEAD -- 'tests/*' | wc -l
# R1 在册态三层
grep -c "zephyr[./]data_governance" docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml
grep -c "zephyr[./]data_governance" docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml
grep -n "zephyr.data_governance" .importlinter
grep -n "zephyr.data_governance" architecture_model/contracts/error_code_registry.yaml | head -3
# D1 死名在册（期望：该模块文件不存在）
git cat-file -e HEAD:src/zephyr/data_governance/asset_inventory.py 2>/dev/null && echo UNEXPECTED || echo DEADNAME
sed -n '175p' src/zephyr/infrastructure/asset_inventory/__init__.py
# A1 触发面（期望零命中）
git grep -ln "data_governance" HEAD -- '*.ps1' 'config/*' | head
# G1 效果尺缺位（期望零命中）
grep -in "lineage" docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml | head
```
