---
ttl: task_bound
title: "F130 ml_serve 模型服务适配族（codegen/deep_review 适配器/压缩加速/漂移监控）复飞案卷"
session: st-c7-mine-20260927
updated: 2026-09-29
---

# F130 ml_serve 模型服务适配族（J 段，P1，骨架态=unmined(new id)）

> 立卷依据：`00_skeleton_verified.md` §二 D-07 行——"`ml_serve`（11 py：model adapter/compression）→ F130（P1，J 段；与 F89 分界=数值 ML 族 vs LLM 族）"。件数实核=11（§六 P1），非 `__init__` 实体件=4。
> **主结论（红）**：四件实体**生产面零 import、无工厂/注册表按名选取**，唯一在世的跨包文本引用来自归档脚本 ⇒ 判**装饰**。本卷另发现一处需交克隆判据的同名件（`model_drift_monitor.py` 在 gov_drift 与 ml_serve 各有一份），本卷不自行裁定。（后记 2026-09-29：本卷红判已被 SW5 夜战卡1 采纳为定罪依据，退役标记落地——见刷新批注）

## 一、六向台账（2026-09-27 实证，基准=HEAD 3b4b1f86a1）

| 向 | 实测证据 |
|---|---|
| 实现件 | `src/zephyr/ml_serve/`（11 .py 在 HEAD）：实体四件 `codegen_model_adapter.py`、`deep_review_model_adapter.py`、`model_compression_accelerator.py`、`core/model_drift_monitor.py`；其余 7 件为包与骨架层 `__init__.py`（`api/ services/ models/ infrastructure/ core/ _extensions/` 中除 `core/model_drift_monitor.py` 外非 `__init__` 件=0，§六 P3）。 |
| 在册态 | `module_translation_registry.yaml` 命中 **12**、`candidate_module_registry.yaml` 命中 **10**（含 `:16446  promoted_to: src/zephyr/ml_serve/codegen_model_adapter.py`、`:16472  promoted_to: …/deep_review_model_adapter.py` 两处晋升留痕）；`.importlinter:53` 列 `zephyr.ml_serve`；`error_code_registry.yaml:3537/3542/3547` 逐模块登错误码；`config/governance_operations_map.yaml:727-728` 把 `zephyr.ml_serve.core.model_drift_monitor` 登记为运维面条目。⇒ 在册四层齐，且是 12 环节中唯一同时出现在运维地图的一件（该地图本身是否消费该条目，见 §四 缺 4）。 |
| 消费者 | **生产 import=0（AST 实测，§六 W1）**；测试 import=5 文件。跨包文本命中逐条否证：①`scripts/_archive/migration/generate_migration_registry.py`——位于 **`_archive/`** 归档目录且属历史一次性生成器，不计在产消费者；②`config/governance_operations_map.yaml:727`＝登记面（地图条目），无代码读取该键去 import；③`error_code_registry.yaml`／`candidate_module_registry.yaml`＝自我声明面。**注册表/工厂排查（本卷关键否证）**：`git grep -n "ModelAdapter\|model_adapter" HEAD -- '*.py' '*.yaml' ':!tests/*' ':!src/zephyr/ml_serve/*'` 命中面 100% 为上述自我声明，**无任何按名字符串反射装配适配器的代码** ⇒ 排除"配置反射调用"隐藏通路。 |
| 测试 | 5 件：`tests/ml_serve/test_model_compression_accelerator.py:27`、`tests/ml_serve/test_model_drift_monitor.py:26`、`tests/ml_serve/test_codegen_model_adapter.py:25`、`tests/ml_serve/test_deep_review_model_adapter.py:25`（+ 目录内 1 件，§六 T1 列表）。M1 dir5 计数一致。测试是唯一消费者 ⇒ 绿仅证自洽。 |
| 自动化触发 | **零**。M1 dir6 wide=false/narrow=false；`git grep -ln "ml_serve" HEAD -- '*.ps1' 'config/*' 'src/zephyr/data/config/*'` 仅命中运维地图 yaml，无脚本/计划任务腿（§六 A1/A2）。 |
| 真源方向 | 未定（P1 记账）：模型服务侧真源应为 `ml_train/core/model_version_registry.py`（属 F129）+ 推理引擎实现（`ml_train/implementations/default_inference_engine.py`，实测**确实**被 `src/zephyr/intelligence/model_evaluation/implementations/default_inference_engine.py:36` 消费）。⇒ **同族对照效果显著**：F129 有真消费者，F130 一个都没有，说明"serve 层"的能力实际由 ml_train 包内的 inference/implementations 承担，F130 是**并行未启用的第二实现族**。这是本环节真源判定的核心事实，非泛泛"待定"。 |
| 门禁与质量尺 | 契约层在（`.importlinter:53` + 错误码在册）。业务层无尺（§六 G1：`gate_registry.yaml` 内无 model-adapter/compression/漂移相关门）。⇒ "适配器是否真被用于线上模型"不可见。 |
| 当前运行状态 | **红（装饰）**；线上模型路径走 F129 的 inference 腿，不经本包。 |

## 二、子模块三级枚举

1. **模型适配族（2 件）**
   - 二级=按设计对象分：`codegen_model_adapter.py`（代码生成线）／`deep_review_model_adapter.py`(深度评审线)——命名指向 J 段设计门（F94 七段设计 / F95 四对象设计）所定义的两类对象
   - 三级=适配契约（模型 I/O 形状转换、提示装配、结果规整）；**接入点不存在**：J 段两件设计对象的实际 LLM 调用腿经 LSG 通道（F88），未见任何一处把本包适配器作为 client 注入（§六 C2）
2. **压缩加速族（1 件）**：`model_compression_accelerator.py` → 三级=量化/剪枝/蒸馏入口；与 F129 `implementations/` 训练件的关系未声明（压缩产物写回版本注册的路径无证据）
3. **漂移监控族（1 件）**：`core/model_drift_monitor.py`（269 行）→ 三级=漂移类型枚举 + 阈值 + 告警出口；M1 dir4 报 `DriftType used by 4 file(s) e.g. src/zephyr/infrastructure/events/__init__.py` 属**同名 symbol 形态**，须按 §六 C3 用 import 面复核后方可采信（本卷按 PROD=0 结论，不采信该腿）
4. **骨架占位族（7 件 `__init__.py`）**：六层目录除 `core/` 外零实现件（§六 P3）⇒ 与 F125/F127/F128 同形模板骨架。

## 三、接线四态独立复核

**判定=装饰**。判据链：

1. **PROD import=0**（§六 W1）；同夜对照 ml_train PROD=5 / nlp PROD=9 / infra_ops PROD=1 ⇒ 扫描尺有效，零值可信。
2. **TYPE_CHECKING 专项**：本包连 TC 内导入都没有（区别于 F131 `news_sentiment_analyzer.py:53` 的 TC 腿、F129 `ml_experiment_pipeline.py:65` 的 TC 腿）⇒ 纯装饰，非半接线。
3. **反射装配排查**（适配器类组件最常见的隐藏接线形态，专门测）：按类名/模块名在 `config/*.yaml` 与全仓字符串检索，无装配点 ⇒ 不可判"已接线但看不到"。
4. **同名件红旗（须交判据，不由本卷裁）**：`model_drift_monitor.py` 两份并存——`src/zephyr/gov_drift/detector_core/model_drift_monitor.py`（68 行，在册于 `config/governance_operations_map.yaml:409-410`）与 `src/zephyr/ml_serve/core/model_drift_monitor.py`（269 行，:727-728）。行数差 4 倍，**不构成"同物重复"的直接证据**，但同名单词＋都在漂移族 ⇒ 触发 RULE-CLONEGUARD 关注面。本卷按宪法只登记事实，clone 判定归执法尺（§六 D3 给出比对命令），处置列 §四 缺 3。
5. **在册四层不救场**：晋升留痕（`candidate_module_registry.yaml:16446/:16472`）＋运维地图登记＋错误码在册均为登记面；参 F128 §三.4 的"晋升≠接线"通用教训。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | 四件生产零消费；J 段设计对象的模型调用不经本包适配器 | 施工：明确"serve 层要不要独立存在"——若判由 F129 承担，本包转退役（净零声明+撤 `.importlinter` 层）；若判要，补 J 段接入点与红样 | P1 |
| 2 | 真源方向倒挂风险：同名能力（推理/版本/压缩）分散在 F129（在产）与 F130（未用），存在"改错包"风险 | 施工：真源地图加一条"serve 侧唯一入口"声明；与 F129 卷 §二 交叉引用 | P1 |
| 3 | `model_drift_monitor` 双份并存未定 clone 态 | 挂起：交 clone_guard 尺判定（extract 级克隆无逃生），本卷不代判；判定为重复簇后若走向删除属注册表净删 → Owner 门位（根宪法 §5） | P1 |
| 4 | `config/governance_operations_map.yaml` 是否被任何代码/面板消费未测——若非零即地图条目纯装饰，本卷"在册四层齐"之一层随之作废 | 挂起：交治理侧运维地图车道判 | P2 |
| 5 | `DriftType` 等 symbol 腿在 M1 机采中未做同名消歧，会系统性虚高覆盖 | 施工：M1 采集器补 import 面共证（与 F127 缺 4 同一改法） | P2 |

## 五、自审闸三态

**未干。** 已可复算：PROD=0、TC=0、反射装配零命中、在册四层含晋升两处 file:line、双同名件事实与行数对照、与 F129 的"同族一有一无"对照。未干原因：①四件实现体未逐件读，故"退役 vs 接入"的成本与影响未量化，缺 1 给不出推荐方向；②缺 3 的 clone 判定需要跑 `clone_guard` 尺（跨包 extract 级比对），本夜为避免热文件/审计噪声未执行；③`governance_operations_map.yaml` 的消费面未测（缺 4 是悬置前提，会影响 §一 在册态那行的成色）。⇒ 交红线 + 未干，不盖挖干。

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
cd /d/ZephyrAlpha
# P1/P3 件数与骨架层空实现（期望 11 / 除 core 外各层 0）
git ls-tree -r --name-only HEAD src/zephyr/ml_serve | wc -l
for d in api services models infrastructure _extensions; do echo "$d=$(git ls-tree -r --name-only HEAD src/zephyr/ml_serve/$d | grep -vc '__init__.py')"; done
# W1 三态 import 分类（期望 PROD=0 / TC=0）
python -c "
import ast,subprocess,collections
f=collections.Counter()
files={l.split(':',1)[1] for l in subprocess.run(['git','grep','-l','zephyr.ml_serve','HEAD','--','*.py'],capture_output=True,text=True,encoding='utf-8').stdout.split()}
for p in sorted(files):
    if p.startswith('src/zephyr/ml_serve/'): continue
    s=subprocess.run(['git','show','HEAD:'+p],capture_output=True,text=True,encoding='utf-8',errors='replace').stdout
    if not s.strip(): continue
    try: t=ast.parse(s)
    except Exception: continue
    tc={n.lineno for i in ast.walk(t) if isinstance(i,ast.If) and 'TYPE_CHECKING' in ast.dump(i.test) for n in ast.walk(i) if isinstance(n,(ast.Import,ast.ImportFrom))}
    for n in ast.walk(t):
        ms=[n.module] if isinstance(n,ast.ImportFrom) and n.module else ([a.name for a in n.names] if isinstance(n,ast.Import) else [])
        for m in ms:
            if m.startswith('zephyr.ml_serve'):
                k='TC' if n.lineno in tc else ('TEST' if p.startswith('tests/') else 'PROD')
                f[k]+=1; print(k,p+':'+str(n.lineno),m)
print('SUMMARY',dict(f))"
# C1 归档件排除自证（期望：唯一非自我声明命中在 _archive/）
git grep -n "ml_serve" HEAD -- 'scripts/*.py' ':!tests/*' | head
# C2 反射装配排查（期望：命中面全为 registry/契约自我声明）
git grep -n "ModelAdapter\|model_adapter" HEAD -- '*.py' '*.yaml' ':!tests/*' ':!src/zephyr/ml_serve/*'
# C3 DriftType symbol 腿复核（须见 import 才算消费）
git grep -n "class DriftType" HEAD -- '*.py'
# T1 测试面（期望 5 文件）
git grep -l "zephyr\.ml_serve" HEAD -- 'tests/*'
# D1/D2/D3 双同名漂移件比对（行数 + 类面差异）
wc -l src/zephyr/gov_drift/detector_core/model_drift_monitor.py src/zephyr/ml_serve/core/model_drift_monitor.py
diff <(grep -oE "class [A-Za-z_]+" src/zephyr/gov_drift/detector_core/model_drift_monitor.py) <(grep -oE "class [A-Za-z_]+" src/zephyr/ml_serve/core/model_drift_monitor.py)
# A1/A2 触发面（期望无脚本/计划任务腿）
git grep -ln "ml_serve" HEAD -- '*.ps1' 'config/*' 'src/zephyr/data/config/*'
powershell -NoProfile -Command "Get-ScheduledTask -TaskName 'Zephyr*' | Select-Object TaskName,State | Format-Table -AutoSize"
# R1 在册四层
grep -c "zephyr[./]ml_serve" docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml
grep -n "promoted_to: src/zephyr/ml_serve" docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml
grep -n "zephyr.ml_serve\|zephyr.gov_drift.detector_core.model_drift_monitor" config/governance_operations_map.yaml
grep -n "zephyr.ml_serve" .importlinter
# G1 效果尺缺位（期望零命中）
grep -in "ml_serve\|model_adapter\|compression" docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml | head
```

## 七、刷新批注（2026-09-29 st-finaldel-fresha）

### 9/28 后变更（本卷被采纳为定罪依据）
- `794f16569b`（09-29 SW5 夜战卡1·M1 封矿第一批，F125/F127/F128/F130 逐环三选一落地）：ml_serve/__init__.py（+14）现挂 **[DEPRECATED] 2026-09-29 退役标记**——定罪原文逐条引本卷（四件实体 PROD=0/TC=0、无工厂/注册表反射装配、唯一跨包命中在 scripts/_archive 归档件）；successor 声明=serve 层现役 F129 ml_train（core/model_version_registry+implementations/default_inference_engine，后者被 src/zephyr/intelligence/model_evaluation/implementations/default_inference_engine.py:36 真实消费）；model_drift_monitor 双同名件附登记不裁=OWNER-GATE。

### 缺口清单状态修订
- 缺口 1（serve 层去留）：**方向已裁并落地**（退役标记入册；四件实体净删与 .importlinter 撤层未见=净删 Owner 门维持）。
- 缺口 2（真源倒挂/改错包风险）：**已对冲**（successor 声明随标记入册）。
- 缺口 3（双同名 clone 态）：维持 OWNER-GATE 挂起。
- 缺口 4/5：维持。

### 自审闸三态
- **未干（维持）但方向已裁**——本卷红判经 SW5 采纳为封矿定罪依据；缺口 1 主问（"退役 vs 接入"）已由 Owner 通道落地为退役标记；剩余未干面=四件实体净删、clone 尺判定、operations_map 消费面（均 Owner/治理车道）。
