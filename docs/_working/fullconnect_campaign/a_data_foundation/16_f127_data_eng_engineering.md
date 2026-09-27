---
ttl: task_bound
title: "F127 data_eng 数据工程引擎族（湖/冷储/流处理/GPU 资源）复飞案卷"
session: st-c7-mine-20260927
---

# F127 data_eng 数据工程引擎族（A 段，P1，骨架态=unmined(new id)）

> 立卷依据：`00_skeleton_verified.md` §二 D-02 行——"`data_eng`（16 py：data_lake_manager/cold_data_archive_manager 等）→ F127（P1，A 段；与 F08 冷库归档存在冷储交叠=勘误点）"。件数实核=16（§六 P1），与骨架口径吻合。
> **本卷两条主结论**：①与 F125 同形——生产面零 import，判**装饰**；②骨架自标的"与 F08 冷储交叠"经实核**是双活源风险**：F08 现役归档件是 `scripts/ch/archiver.py`（920 行，四命令），而 `data_eng/cold_data_archive_manager.py` 是另一套并行实现、无人调用。

## 一、六向台账（2026-09-27 实证，基准=HEAD 3b4b1f86a1）

| 向 | 实测证据 |
|---|---|
| 实现件 | `src/zephyr/data_eng/`（16 .py 在 HEAD；非 `__init__` 件=9，§六 P1/P2）。九件实名（逐条 `git ls-tree` 命中）：`data_lake_manager.py`、`cold_data_archive_manager.py`、`incremental_update_engine.py`、`stream_processing_engine.py`、`cleaning_anomaly_engine.py`、`data_anomaly_alerter.py`、`quality_sla_breach_predictor.py`、`gpu_resource_manager.py`、`expectation_governance.py`。M1 台账 dir3=`dirs_in_head {src/zephyr/data_eng: 16}`。 |
| 在册态 | 三层齐：`module_translation_registry.yaml` 命中 **30**、`candidate_module_registry.yaml` 命中 **18**、`.importlinter:28` 列 `zephyr.data_eng`、`error_code_registry.yaml:2846/2851/3057…` 逐模块登错误码。头注自我拔高：`cold_data_archive_manager.py` 头部 `[MATURITY] production` / `[STARTUP] imported` / `[CONSUMERS] 运行时装配批（归档调度挂 auto_archive 周期计划 / 归档索引接 SQLite / 清理接存储执行器）`——三条自述**全部与实测矛盾**（见 §三）。 |
| 消费者 | **生产 import=0（AST 实测，§六 W1）**。测试 import=10 文件。M1 台账 dir4 报的两条 symbol 证据本卷逐条否证：①`RepairStrategy used by src/zephyr/autonomy_core/ai_ops_autonomy_card.py`；②`ArchivePlan used by src/zephyr/data/data_compression_archiver.py` —— 后者实测为**同名异类假命中**：`data_compression_archiver.py:75` 自己 `class ArchivePlan:`（:46 出现在 `__all__`，:170 `def plan(...) -> ArchivePlan`），与本包无关。⇒ 机采 symbol 尺在本环节产生假阳性，本卷不采信（§六 C2）。 |
| 测试 | 10 件（§六 T1），代表锚：`tests/data_eng/test_data_lake_manager.py:27`、`tests/data_eng/test_cold_data_archive_manager.py:30`、`tests/data_eng/test_gpu_resource_manager.py:28`；另有 5 件挂在 `tests/zephyr/data/` 下（`test_cleaning_anomaly_engine.py:30`、`test_data_anomaly_alerter.py:26`、`test_expectation_governance.py:32`、`test_incremental_update_engine.py:27`、`test_silent_latch_before_delivery.py:30`）——测试落点与包目录不同名，按目录判覆盖会漏。 |
| 自动化触发 | **零**。M1 dir6 wide=false/narrow=false；本卷复核 `git grep -ln "data_eng" HEAD -- '*.ps1' 'config/*'` 无生产触发腿（§六 A1）。头注 `[CONSUMERS]` 所称"挂 auto_archive 周期计划"经核不成立：现役计划任务名册（`Get-ScheduledTask`，§六 A2）中归档/冷储侧走的是 F08 备份族（DailyBackup/WeeklyVMBackup/ZEPHYR-RESTORE-DRILL），**无任何任务指向 `-m zephyr.data_eng.*`**。 |
| 真源方向 | 未定（本卷判为 P1 记账项）：冷储真源=F08 卷所载 `F:/zephyr_cold` + `scripts/ch/archiver.py` 行为链；本包 `cold_data_archive_manager.py` 自称"归档索引接 SQLite"＝**第二索引真源候选**。血缘/资产真源=depgraph（架构数据=DB）。规则数据侧无对应 YAML。⇒ 按根宪法 §4.2"同真源可派生→必并"，本包冷储腿与 F08 属同域，须合并或明确异域，不得并存两索引。 |
| 门禁与质量尺 | 契约层有（`.importlinter` 层约束 + 错误码在册）；效果层无尺（§六 G1：无 gate 校验"归档计划是否真被执行"）。⇒ 与 F125 同因：在册而红，无人报警。 |
| 运行状态 | **红（装饰态）**；且冷储腿存在与 F08 的双活源风险（F08 侧在产，本侧未接入）。 |

## 二、子模块三级枚举

1. **数据湖与存储族**
   - `data_lake_manager.py`（湖管理）／`cold_data_archive_manager.py`（冷储归档）／`incremental_update_engine.py`（增量更新）
   - 三级=冷储归档件自述三挂载点：归档调度（auto_archive 周期）｜归档索引（SQLite）｜清理执行器 —— 三个挂载点在 HEAD 上**均无供方**（§三.2）
2. **质量与异常族**
   - `cleaning_anomaly_engine.py`（清洗异常）｜`data_anomaly_alerter.py`（异常告警）｜`quality_sla_breach_predictor.py`（SLA 违约预测）｜`expectation_governance.py`（期望治理）
   - 三级=告警出口未接（与 F114 通知路由的挂接在盘上无 import 证据）
3. **计算资源族**：`gpu_resource_manager.py`（GPU 配额）｜`stream_processing_engine.py`（流处理）
   - 三级=GPU 族与 G 段回测 GPU 线（F66-F69 带）的关系未定；本包件零消费者 ⇒ G 段若在用 GPU 配额，用的不是本件（须由 G 段卷交叉确认）
4. **骨架占位族（7 件 `__init__.py`）**：`api/`、`services/`、`models/`、`infrastructure/`、`core/`、`_extensions/` + 包 `__init__`，五层子目录非 `__init__` 件数=0（§六 P3）⇒ 与 F125 同一模板骨架现象。

## 三、接线四态独立复核

**判定=装饰**。判据链：

1. **PROD import=0**：AST 三态分类（§六 W1，`zephyr.data_eng*` 前缀）PROD 计数=0、TEST=10。对照同夜 ml_train PROD=5、nlp PROD=9、infra_ops PROD=1 ⇒ 扫描口径有效，零值可信。
2. **自述与实盘对撞（本卷重点）**：`[CONSUMERS]`/`[MATURITY] production`/`[STARTUP] imported` 三条自述逐条否证——①"imported"：全包无任何非自身、非测试的 importer；②"production"：无生产调用点；③"挂 auto_archive 周期计划"：计划任务名册无该项。⇒ **头部标注在本仓不构成接线证据**，这与 F125 的 `[DEPENDENCIES]` 注释假声明是同一失效模式的两种表现。
3. **同名 symbol 假阳性（防误判为半接线）**：`ArchivePlan` 双定义（本包 vs `data/data_compression_archiver.py:75`）。若按 M1 symbol 尺会误判为"已接线"；按 import 尺判装饰。两把尺结论相反时，**以 import 尺为准**（symbol 文本命中可来自同名/注释/字符串）。
4. **双活源专项**：F08 冷储现役=`scripts/ch/archiver.py`（920 行，archive-range/list/stats/restore/export-only，F08 卷 §二 已锚 :191/:383/:435/:793）；本包 `cold_data_archive_manager.py` 并行存在且零消费。按根宪法 §4.2"同真源可派生→必并／同域重复簇→收敛唯一"，本环节是**潜在第二真源**，不是"尚未接线的补充能力"。该判定与骨架自标"勘误点"一致，本卷把它从"待核"升为"已核为重复簇候选"。
5. **无死引用**：本卷引用路径逐条 `git cat-file -e HEAD:` / `git ls-tree` 实核。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | 全族生产零消费（装饰）；9 件能力对业务链贡献=0 | 施工：逐件判"接入 or 退役"，禁整包留置为潜在第二真源；接入须给红样（先测后接），退役走净零声明 | P1 |
| 2 | 冷储双实现：`cold_data_archive_manager.py` vs F08 `scripts/ch/archiver.py`，且本件自称另立 SQLite 归档索引 | Owner 门位：收敛方向（保 F08 删本件 / 或本件取代 F08）涉及生产归档链路，属根宪法 §5 high 域；本卷只提交判据不代裁 | P1 |
| 3 | 头部 `[MATURITY] production`/`[CONSUMERS]` 与实盘相反的三处假声明在册 | 施工：随接入或未接入实况更正头部；并评估把"头注自述 vs 实测消费者"做成一把 own-scope 尺（防同形复发） | P1 |
| 4 | M1 机采 symbol 尺产生 `ArchivePlan` 假阳性 | 施工：M1 采集器补同名消歧（须 import 面共证才计消费） | P2 |
| 5 | GPU 配额族与 G 段回测 GPU 线的归属边界未定 | 挂起：待 G 段卷交叉确认，避免两卷各记一次 | P2 |
| 6 | 告警出口（`data_anomaly_alerter.py`）与 F114 通知路由未接 | 施工：接入批的一部分，随缺 1 决策 | P2 |

## 五、自审闸三态

**未干。** 已实核且可复算：PROD=0 的 import 面、10 件测试面、三处头注假声明的逐条否证、`ArchivePlan` 同名假阳性拆解、与 F08 的双实现事实、计划任务名册无本包项。未干原因：①9 件**未逐件读实现体**（各件真实能力边界、是否依赖外部服务如 MinIO/对象存储、是否写生产路径）——装饰判定不依赖它，但"接入还是退役"的处置建议依赖它，缺此不能算干；②与 G 段 GPU 面的交叉未做；③缺 2 属 Owner 门位。⇒ 交红线 + 未干。

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
cd /d/ZephyrAlpha
# P1/P2/P3 件数三口径（期望 16 / 9 / 各层 0）
git ls-tree -r --name-only HEAD src/zephyr/data_eng | wc -l
git ls-tree -r --name-only HEAD src/zephyr/data_eng | grep -vc "__init__.py"
for d in api services models infrastructure core _extensions; do echo "$d=$(git ls-tree -r --name-only HEAD src/zephyr/data_eng/$d | grep -vc '__init__.py')"; done
# W1 三态 import 分类（期望 PROD=0）
python -c "
import ast,subprocess,collections
f=collections.Counter()
files={l.split(':',1)[1] for l in subprocess.run(['git','grep','-l','zephyr.data_eng','HEAD','--','*.py'],capture_output=True,text=True,encoding='utf-8').stdout.split()}
for p in sorted(files):
    if p.startswith('src/zephyr/data_eng/'): continue
    s=subprocess.run(['git','show','HEAD:'+p],capture_output=True,text=True,encoding='utf-8',errors='replace').stdout
    if not s.strip(): continue
    try: t=ast.parse(s)
    except Exception: continue
    tc={n.lineno for i in ast.walk(t) if isinstance(i,ast.If) and 'TYPE_CHECKING' in ast.dump(i.test) for n in ast.walk(i) if isinstance(n,(ast.Import,ast.ImportFrom))}
    for n in ast.walk(t):
        ms=[n.module] if isinstance(n,ast.ImportFrom) and n.module else ([a.name for a in n.names] if isinstance(n,ast.Import) else [])
        for m in ms:
            if m.startswith('zephyr.data_eng'):
                k='TC' if n.lineno in tc else ('TEST' if p.startswith('tests/') else 'PROD')
                f[k]+=1; print(k,p+':'+str(n.lineno),m)
print('SUMMARY',dict(f))"
# C1/C2 头注三条假声明 + symbol 假阳性拆解
grep -nE "\[(MATURITY|STARTUP|CONSUMERS)\]" src/zephyr/data_eng/cold_data_archive_manager.py | head -3
grep -n "class ArchivePlan" src/zephyr/data/data_compression_archiver.py src/zephyr/data_eng/cold_data_archive_manager.py
# T1 测试面（期望 10，含 tests/zephyr/data/ 落点）
git grep -l "zephyr\.data_eng" HEAD -- 'tests/*' | wc -l
git grep -l "zephyr\.data_eng" HEAD -- 'tests/*'
# A1 计划任务脚本侧（期望零命中）
git grep -ln "data_eng" HEAD -- '*.ps1' 'config/*' | head
# A2 机器侧任务名册（期望无 data_eng / ConfigCheck 之外的本包项）
powershell -NoProfile -Command "Get-ScheduledTask -TaskName 'Zephyr*' | Select-Object TaskName,State | Format-Table -AutoSize"
# R1 在册三层
grep -c "zephyr[./]data_eng" docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml
grep -c "zephyr[./]data_eng" docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml
grep -n "zephyr.data_eng" .importlinter
# G1 效果尺缺位（期望零命中）
grep -in "data_eng\|archive_plan" docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml | head
```
