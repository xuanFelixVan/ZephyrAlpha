---
ttl: task_bound
title: "F132 infra_ops 运维工程域（配置生效核对/loki 日志/存储成本/WAL 监控/拓扑可视化）复飞案卷"
session: st-c7-mine-20260927
---

# F132 infra_ops 运维工程域（I 段，P1，骨架态=unmined(new id)）

> 立卷依据：`00_skeleton_verified.md` §二 D-11 行——"`infra_ops`（6 py：loki/storage_cost/wal_monitor）→ F132（P1，I 段，运维工程域）"。件数实核=6（§六 P1），其中实体 5 件 + 包 `__init__.py`。
> **主结论（黄）**：本包是 12 个补挖环节中**唯一有一件真被自动触发**的包（`config_effect_checker` 日班计划任务 State=Ready、本日 08:05 实跑），但其余 4 件零生产消费者 ⇒ 整包判**半接线**，且那次实跑的 `LastTaskResult=1`（非零）是必须交下游查的红点（本卷不据以判功能失败）。

## 一、六向台账（2026-09-27 实证，基准=HEAD 3b4b1f86a1）

| 向 | 实测证据 |
|---|---|
| 实现件 | `src/zephyr/infra_ops/`（6 .py 在 HEAD）：`config_effect_checker.py`、`loki_log_pipeline.py`、`wal_checkpoint_monitor.py`、`storage_cost_calculator.py`、`runtime_topology_visualizer.py` + `__init__.py`。注意骨架 D-11 只点名 3 件（loki/storage_cost/wal_monitor），**恰好是被动的 3 件**，未点名主动的那件（config_effect_checker）——骨架定号描述与本环节实际唯一在产腿错位，属卷级勘误（§四 缺 5）。 |
| 在册态 | `module_translation_registry.yaml` 命中 **6**、`candidate_module_registry.yaml` 命中 **10**（本包是 12 环节中候选册命中数唯一高于翻译册的一件）；`config/governance_operations_map.yaml` 有本包条目（§六 R3）。迁移史在册：`scripts/migration/dm314_infra_ops_split.py:52  OLD_PREFIX = "zephyr.infra_ops."`（DM-314 拆分件，读 REG-MIGRATION-001，见 F123 卷）。 |
| 消费者 | **生产 import=1 条（AST 实测，§六 W1）**：`src/zephyr/data/scheduler.py:1361  from zephyr.infra_ops.config_effect_checker import (...)`，其上文 :1354 注释自述该腿语义="只在加载时刷新，… 对比磁盘现状"⇒ **事件语义为"调度器加载时核对配置生效态"**，属真消费。其余 4 件：`loki_log_pipeline`/`wal_checkpoint_monitor`/`storage_cost_calculator`/`runtime_topology_visualizer` **生产 import=0**，仅 `tests/infra_ops/` 各 1 件（§六 T1）。`src/zephyr/gov_drift/contract_drift_detector.py` 的命中为文本级（非 import，§六 C2）。 |
| 测试 | 5 件全覆盖 5 实体：`tests/infra_ops/test_config_effect_checker.py:22`、`test_loki_log_pipeline.py:26`、`test_wal_checkpoint_monitor.py:27`、`test_storage_cost_calculator.py:23`、`test_runtime_topology_visualizer.py:27`。⇒ 本包是 12 环节中**测试覆盖最齐**的一件（5/5），但齐覆盖不代表齐接线（4 件仅测试可达）。 |
| 自动化触发 | **有一条，机器实测在案**（§六 A2）：计划任务 `ZephyrAlpha_ConfigCheck` State=**Ready**，Action=`pythonw.exe -m zephyr.infra_ops.config_effect_checker`，注册脚本 `scripts/register_config_check_task.ps1:17/31/47/69/85` 五处指向同一模块；`Get-ScheduledTaskInfo` 实测 LastRunTime=2026-09-27 08:05:01、NextRunTime=2026-09-28 08:05:00（**日班定时**）、LastTaskResult=**1**（非零）。其余 4 件：`git grep -ln "<模块名>" HEAD -- '*.ps1' 'config/*' 'src/zephyr/data/config/*'` 零命中 ⇒ 无触发面。 |
| 真源方向 | 架构数据=DB（depgraph，本包模块身份）；配置生效核对的比对面=配置 YAML（规则数据侧）与磁盘现状，读侧经 `src/zephyr/data/scheduler.py` 的调度配置加载；loki 日志族真源=外部 Loki 服务（**盘上无本仓真源声明**，见 §四 缺 2）。 |
| 门禁与质量尺 | 无本包专属 gate（§六 G1）。但存在两处结构性风险尺需求：①日班任务的**结果码无巡检**（LastTaskResult 非零不报警，参见本仓"黑匣子盲 34.6h"同族形态）；②4 件零触发**无退役判据**（根宪法 §4.2"零触发零消费→退役"当前对它们不生效，因为它们在候选/翻译册里显示为在册件）。 |
| 当前运行状态 | **黄（半接线）**：1 件在产且实跑（结果码待查），4 件装饰。 |

## 二、子模块三级枚举

1. **配置生效核对（在产腿）**：`config_effect_checker.py`
   - 二级=被两路调用：调度器加载内联（`data/scheduler.py:1361`）+ 计划任务独立进程（`-m zephyr.infra_ops.config_effect_checker`）
   - 三级=两路的**语义是否一致未核**（同一函数经两入口跑出不同结论的可能性，本卷未读实现体，列 §四 缺 1）
2. **日志可观测族**：`loki_log_pipeline.py` → 三级=采集/批推/查询三段；外部 Loki 服务在本机的可达性未测（§四 缺 2）
3. **存储与成本族**：`storage_cost_calculator.py` → 三级=冷库/热层成本口径；与 F08 冷库（`F:/zephyr_cold`）+ 备份总仓（`G:/backup`）的地图（INFRA-STORE-003）关系未声明 ⇒ 存在与运维地图另立成本口径的风险（§四 缺 3）
4. **数据库健康族**：`wal_checkpoint_monitor.py` → 三级=PG WAL 检查点滞后监视；与 F07（PG 架构库）、F84/F85 环境启动链的告警出口关系未声明
5. **拓扑可视化族**：`runtime_topology_visualizer.py` → 三级=运行时依赖图渲染；与 F111/F113 前端渲染族关系未声明（前端有面板而无 import ⇒ 可能靠文件产物解耦，须核）
6. **包骨架**：仅 `__init__.py` 一只（本包无 api/services/models/… 空层，**结构最干净的一件**，与 F125/F127/F128/F130 的六层空骨架形成对照）

## 三、接线四态独立复核

**判定=半接线（1 件已接线 / 4 件装饰）**。判据链：

1. **在产腿的三要素齐**：`config_effect_checker` 同时具备 ①真实运行时 import（`data/scheduler.py:1361`，AST 判定非 TYPE_CHECKING，§六 W1）②独立自动触发（计划任务 Ready 且本日实跑）③测试锚（`tests/infra_ops/test_config_effect_checker.py:22`）⇒ 判**已接线**成立，且本卷是实测机器态（`Get-ScheduledTask`/`Get-ScheduledTaskInfo`），非引用册面。
2. **结果码不等于健康**：LastTaskResult=1 只证明"跑完返回非零"。可能语义含：真失败 / 设计上的"发现漂移即非零"（fail-closed 表达） / 环境缺依赖。**本卷不据以判功能坏**，仅登记为必查项（§四 缺 1）。这是刻意避免的反向假绿/假红双向纪律。
3. **四件装饰判据**：PROD import=0 + 触发面零命中（脚本/配置/机器任务三面排查，§六 A1/A3）。特别否证两形态：①`contract_drift_detector.py` 的文本命中不是 import（§六 C2）；②`scripts/_archive/migration/generate_migration_registry.py` 与 `scripts/migration/dm314_infra_ops_split.py` 属归档/一次性迁移件，不计在产消费者。
4. **TYPE_CHECKING 专项**：本包 TC 内导入=0（§六 W1），故 4 件是**纯装饰**而非"类型期装饰"。
5. **定时触发合宪性存疑（只登记不自裁）**：本包唯一在产腿是**日班 Timer** 触发。根宪法 §9.3 的禁 Timer 条款针对 **reconciler**；`config_effect_checker` 是"核对器"语义，是否落入该条款须治理侧定性 ⇒ 本卷把它作为待裁问题列出（§四 缺 4），不自行判违规也不自行豁免。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | 日班 `ZephyrAlpha_ConfigCheck` LastTaskResult=1（非零），退出码语义与实际产出未查；结果码无巡检 | 施工：读 `config_effect_checker.main()` 的退出码约定 + 当日产物日志定性质（真失败 vs fail-closed 表达）；补"计划任务结果码非零即告警"的巡检腿 | P1 |
| 2 | `loki_log_pipeline` 零消费、零触发，且外部 Loki 可达性未声明真源 | 施工：接入或退役二选一，禁留置为"在册而未用"（根宪法 §4.2 零触发零消费→退役） | P1 |
| 3 | `storage_cost_calculator` 与存储地图（INFRA-STORE-003，冷库 F/备份 G）的成本口径关系未声明 ⇒ 双口径风险 | 施工：补真源方向声明后再谈接线；本卷不猜口径 | P1 |
| 4 | 在产腿为日班 Timer 触发，是否落入根宪法 §9.3"reconciler 必须事件触发、禁 cron/Timer/sleep-loop"未定 | Owner 门位（条款适用性定性属判据解释面，挖矿道不自裁）；本卷只提问题并给实测事实 | P1 |
| 5 | 骨架 §二 D-11 描述只点名 3 件被动件、漏点名唯一在产件 `config_effect_checker`，与本环节实际主腿错位 | 挂起：属骨架勘误面，交总筹在 `00_skeleton_verified.md` D-11 行改注；挖矿道不代改总册 | P2 |
| 6 | `wal_checkpoint_monitor`/`runtime_topology_visualizer` 的告警出口与前端渲染出口均未声明（F84/F111/F113 交叉） | 挂起：待三卷交叉确认后统一立接入批 | P2 |

## 五、自审闸三态

**未干。** 已可复算且是实测硬料：计划任务的机器态（名称/State/Action/LastRunTime/NextRunTime/LastTaskResult 六项）、PROD import 精确到 `scheduler.py:1361` 一腿、四件装饰的三面排查、5/5 测试覆盖、在册两册命中数、DM-314 迁移史锚点。未干原因：①**未读 `config_effect_checker.py` 实现体**，故缺 1 的"结果码 1 到底是什么"未闭，而这是本环节唯一在产腿的核心健康判据；②四件装饰件的能力边界与接入成本未逐件评估，处置建议因此只是二选一而非推荐项；③缺 4 属条款解释、缺 5 属总册勘误，均非本道权限。⇒ 本卷交"半接线黄判 + 未干"。

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
cd /d/ZephyrAlpha
# P1 件数（期望 6）
git ls-tree -r --name-only HEAD src/zephyr/infra_ops | wc -l
# A2 机器态六项实测（本卷核心证据）
powershell -NoProfile -Command "Get-ScheduledTask -TaskName 'ZephyrAlpha_ConfigCheck' | Select-Object TaskName,State | Format-List; (Get-ScheduledTask -TaskName 'ZephyrAlpha_ConfigCheck').Actions | Format-List Execute,Arguments; Get-ScheduledTaskInfo -TaskName 'ZephyrAlpha_ConfigCheck' | Format-List LastRunTime,NextRunTime,LastTaskResult"
# A1 注册脚本五处锚点
grep -n "config_effect_checker" scripts/register_config_check_task.ps1
# A3 其余四件触发面（期望零命中）
for m in loki_log_pipeline wal_checkpoint_monitor storage_cost_calculator runtime_topology_visualizer; do echo "$m=$(git grep -l "$m" HEAD -- '*.ps1' 'config/*' 'src/zephyr/data/config/*' | wc -l)"; done
# W1 三态 import 分类（期望 PROD=1 / TC=0）
python -c "
import ast,subprocess,collections
f=collections.Counter()
files={l.split(':',1)[1] for l in subprocess.run(['git','grep','-l','zephyr.infra_ops','HEAD','--','*.py'],capture_output=True,text=True,encoding='utf-8').stdout.split()}
for p in sorted(files):
    if p.startswith('src/zephyr/infra_ops/'): continue
    s=subprocess.run(['git','show','HEAD:'+p],capture_output=True,text=True,encoding='utf-8',errors='replace').stdout
    if not s.strip(): continue
    try: t=ast.parse(s)
    except Exception: continue
    tc={n.lineno for i in ast.walk(t) if isinstance(i,ast.If) and 'TYPE_CHECKING' in ast.dump(i.test) for n in ast.walk(i) if isinstance(n,(ast.Import,ast.ImportFrom))}
    for n in ast.walk(t):
        ms=[n.module] if isinstance(n,ast.ImportFrom) and n.module else ([a.name for a in n.names] if isinstance(n,ast.Import) else [])
        for m in ms:
            if m.startswith('zephyr.infra_ops'):
                k='TC' if n.lineno in tc else ('TEST' if p.startswith('tests/') else 'PROD')
                f[k]+=1; print(k,p+':'+str(n.lineno),m)
print('SUMMARY',dict(f))"
# C1/C2 在产腿上下文与文本命中否证
sed -n '1352,1366p' src/zephyr/data/scheduler.py
git grep -n "infra_ops" HEAD -- src/zephyr/gov_drift/contract_drift_detector.py
# T1 测试面（期望 5，逐件对应）
git grep -l "zephyr\.infra_ops" HEAD -- 'tests/*'
# R1/R2/R3 在册三层
grep -c "zephyr[./]infra_ops" docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml
grep -c "zephyr[./]infra_ops" docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml
grep -n "infra_ops" config/governance_operations_map.yaml | head -4
# D1 迁移史锚点
grep -n "OLD_PREFIX" scripts/migration/dm314_infra_ops_split.py | head -2
# 缺1 待查项（本卷未做，接手者从此处起）
grep -n "SystemExit\|sys.exit\|return 1\|raise " src/zephyr/infra_ops/config_effect_checker.py | head -10
```
