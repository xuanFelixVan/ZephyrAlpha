---
ttl: task_bound
title: "F128 data_security 数据安全族（脱敏引擎/访问审计/AI 脱敏管线）复飞案卷"
session: st-c7-mine-20260927
updated: 2026-09-29
---

# F128 data_security 数据安全族（K 段，P1，骨架态=unmined(new id)）

> 立卷依据：`00_skeleton_verified.md` §二 D-04 行——"`data_security`（10 py：masking/access_auditor）→ F128（P1，K 段；与 F88/F105 异域）"。件数实核=10（§六 P1），非 `__init__` 件=3。
> **主结论（红）**：三件实现全在盘、三件测试全绿、三层名册全在册，但**生产面零 import、零动态挂载、零计划任务** ⇒ 判**装饰**。骨架自标的"与 F88（LSG）/F105（密钥治理）异域"经本卷实核**成立**（异域不同对象，按根宪法 §4.2 不并），但"异域"不等于"已接线"。**〔过时标记 2026-09-29：M1 封矿第一批已按本卷判据落退役标记（[DEPRECATED]+无继任/known-gap 注记），物理净删待 Owner 门，见卷末刷新批注〕**

## 一、六向台账（2026-09-27 实证，基准=HEAD 3b4b1f86a1）

| 向 | 实测证据 |
|---|---|
| 实现件 | `src/zephyr/data_security/`（10 .py 在 HEAD）：实体三件 `data_masking_engine.py`、`data_access_auditor.py`、`ai_masking_pipeline.py`；其余 7 件为包与骨架层 `__init__.py`（`api/ services/ models/ infrastructure/ core/ _extensions/` 六层非 `__init__` 件数=0，§六 P3）。 |
| 在册态 | `module_translation_registry.yaml` 命中 **11**、`candidate_module_registry.yaml` 命中 **6** 且含**晋升记录**：`candidate_module_registry.yaml:12903  promoted_to: src/zephyr/data_security/data_access_auditor.py`、`:12929  promoted_to: …/data_masking_engine.py`；`.importlinter:30` 列 `zephyr.data_security`；`error_code_registry.yaml:3096-3102` 逐模块登错误码。⇒ 在册面完整，"候选→晋升"流程确实走过（与 F125/F127 相比，本包有显式晋升留痕）。 |
| 消费者 | **生产 import=0（AST 实测，§六 W1）**；测试 import=3 文件。M1 台账 dir4 唯一 symbol 腿 `SourceType used by 2 file(s) e.g. src/zephyr/security/llm_defense/llm_security/layers/l1_input.py` 本卷**否证为同名假阳性**：`l1_input.py:29` 自有 `class SourceType(Enum)`（:163/:167/:172 全用自身枚举成员 `URL_CONTENT/NETWORK/TOOL_RESULT/MCP/FILE`），与本包零 import 关系（§六 C2）。⇒ 不可据此判 LSG 消费了本包。 |
| 测试 | 3 件：`tests/data_security/test_data_masking_engine.py:25`、`tests/data_security/test_data_access_auditor.py:25`、`tests/data_security/test_ai_masking_pipeline.py:25`。M1 dir5 计数与实测一致（本包是 12 环节中机采与实测最吻合的一件）。 |
| 自动化触发 | **零**。M1 dir6 wide=false/narrow=false；本卷复核 `git grep -ln "data_security" HEAD -- '*.ps1' 'config/*' 'src/zephyr/data/config/*'` 零命中（§六 A1）；机器侧计划任务名册（`Get-ScheduledTask -TaskName 'Zephyr*'`）无脱敏/审计类任务（§六 A2）。⇒ 三件均无触发面，属"按需但无按需调用方"。 |
| 真源方向 | 未定，本卷记为 P1：审计日志真源应为何物（`.runtime` 落盘？DB 表？F102 审计体系？）无声明；`data_access_auditor.py` 与既有审计面 `docs/01_policies_and_standards/_registry/catalogs/` 下的审计体系（F102）之间无派生关系登记。脱敏规则真源（列级白名单/正则集）落在何处亦未声明。⇒ RULE-SSOT 判定缺口。 |
| 门禁与质量尺 | 契约层在（`.importlinter` 层 + 错误码在册）。业务效果层无尺：§六 G1 实测 `gate_registry.yaml` 内与 masking/PII/脱敏相关门零命中 ⇒ **没有任何门禁保证"该脱敏的数据实际被脱敏"**。这与安全类环节的常规要求（执法点必须在写出口）差距最大，是本卷最严重的红。 |
| 当前运行状态 | **红（装饰）**。风险定性：脱敏件不被调用＝数据出口以未脱敏形态流转；该风险与 F88（LSG，输入侧防御，另有其自身执法面）不重叠，LSG 不做列级脱敏。 |

## 二、子模块三级枚举

1. **脱敏族**
   - `data_masking_engine.py`（引擎，二级）→ 三级=策略执行点（列级/行级/值级替换与置空）、豁免与白名单载体（**盘上无对应规则 YAML**，见 §一 真源方向行）
   - `ai_masking_pipeline.py`（AI 前置脱敏管线，二级）→ 三级=LLM 输入侧脱敏（语义上应挂 F88 LSG 的 l1_input 之前，**实测两侧未接**：LSG 用自己的 SourceType，未 import 本件）
2. **审计族**
   - `data_access_auditor.py`（二级）→ 三级=访问事件采集 / 落盘 / 事后核查；其落盘真源未声明（§四 缺 2）
3. **骨架占位族（7 件 `__init__.py`）**：`api/`、`services/`、`models/`、`infrastructure/`、`core/`、`_extensions/` + 包 `__init__`，六层零实现件（§六 P3）⇒ 与 F125/F127 同形的模板骨架。
4. **异域边界（本卷新证的三向关系）**：F88=LSG LLM 输入输出防御（`src/zephyr/security/llm_defense/…`）／F105=密钥治理（`secrets.py` 通道）／F128=数据层脱敏与访问审计。三者对象不同，按根宪法 §4.2"跨域不同对象→不并"，本卷**不支持**以"LSG 已接线"替 F128 免罪，也不主张合并。

## 三、接线四态独立复核

**判定=装饰**。判据链四条：

1. **PROD import=0**（§六 W1，AST 三态分类：PROD/TEST/TYPE_CHECKING，`zephyr.data_security*` 前缀）。同夜对照 ml_train PROD=5、nlp PROD=9、infra_ops PROD=1 ⇒ 尺有效。
2. **TYPE_CHECKING 专项**：本包连"TYPE_CHECKING 内导入"这种最弱的装饰形态都没有——是**零引用**，故不是"半接线偏装饰"而是纯装饰。
3. **动态挂载排查（装饰判定的必要反面）**：`git grep` 字符串口径检索 `config/*.yaml`、`src/zephyr/data/config/schedule.yaml`、`*.ps1` 均无本包件名 ⇒ 不存在"靠配置反射调用"的隐藏通路（区别于 F132 `infra_ops` 那种 `-m zephyr.infra_ops.config_effect_checker` 的计划任务挂载，见该卷）。
4. **晋升在册≠接线**：`candidate_module_registry.yaml:12903/:12929` 的 `promoted_to` 只证明候选件通过了入册评审，不证明运行时有人调它。**晋升留痕与消费证据是两件事**，本仓若把前者当后者即产生系统性假绿——本卷把它作为通用教训登记（§四 缺 5）。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | 三件生产零消费；AI 脱敏管线未挂 LSG 入口，列级脱敏无任何出口调用 **〔09-29 已裁退役方向（空缺转 known-gap），见刷新批注〕** | 施工：定接入点（数据出口 + LSG l1_input 前置各一），先写红样再接线；输出走 tmp_path（根宪法 §9.6） | P1 |
| 2 | 真源方向未定：脱敏规则册与访问审计日志各以何为准（YAML？DB 表？F102 审计体系？） | 挂起：属 RULE-SSOT 立法面，须真源地图定档后回填；挖矿道不自裁 | P1 |
| 3 | 无任何 gate 保证"该脱敏的字段实际被脱敏"（§六 G1 零命中） | 施工：新增效果型 own-scope 尺（根宪法 §3.3），与 F126 字段字典的敏感标记联动最省 | P1 |
| 4 | 与 F88/F105 的异域判定虽成立，但三者在"数据出口安全"上无编排真源（谁先谁后无定义） | 挂起：安全族编排归治理侧，本卷只交判据 | P2 |
| 5 | `promoted_to` 晋升留痕被误当接线的系统性风险（本包是实例） | 施工：候选册字段语义加注（晋升=入册通过，非运行时消费），或补一把"晋升后是否有 PROD import"的巡检 | P2 |

## 五、自审闸三态

**未干。** 已可复算：PROD=0、`SourceType` 同名假阳性拆解、晋升留痕两处 file:line、六层骨架零实现、触发面三重排查（脚本/配置/机器任务）全零。未干原因：①三件实现体**未逐件读**，故"接入点该设在哪、脱敏覆盖面多大"无量化，缺 1 的施工方案因此未定；②敏感字段清单在本仓是否存在（可能在 F126 字段字典的某维度里）未逐条核，缺 3 的尺设计依赖它；③缺 2 属真源立法面。本卷价值=把 F128 从"零证据"推进到"安全类装饰红账 + 通用假绿教训（晋升≠接线）"。**〔过时标记 2026-09-29：缺 1 的"接入 or 退役"已由 M1 封矿裁为退役标记落地，刷新见卷末批注〕**

## 刷新批注（2026-09-29 st-finaldel-freshb）

> 刷新基线：HEAD dev @ 0cacd4a64d（09-29）；对卷内真源跑 `git log --since=2026-09-28` 复核＋码面现读。

- **翻面 commit**：`794f16569b`（09-29 09:54，[SW5 夜战卡1·M1 封矿第一批] ③F128 退役标记）。
- **影响（处置方向已裁=退役，物理净删待 Owner 门）**：
  - 判据采纳：本卷"三件纯装饰（PROD=0 且无 TC 腿/零挂载/零任务；SourceType 消费腿=同名假阳性）"的判定链被封矿批复用为退役依据；F88/F105 异域实核结论（不并、不覆盖列级脱敏）亦被采纳。
  - 落地物：`src/zephyr/data_security/__init__.py` 包门面落 **[DEPRECATED]**（:40 现锚"2026-09-29 夜战 SW5 依 F128 案卷"）+ **successor 注记**（:45-46"无直接继任——F88 LSG 与 F105 经实核异域不同对象，不覆盖列级脱敏/访问审计能力；能力空缺语义转 known-gap 登记"）。
  - Owner 门登记：99_skipped_for_owner.md **#42/43/44**（与 F127/F130 同批，safe_write_text CAS）——物理净删候选归 Owner。
- **缺口状态修订**：缺口1 P1→**退役方向已裁**（补接线选项被否；列级脱敏能力空缺转 known-gap 显式登记——风险不再隐性）｜缺口2（真源方向 RULE-SSOT）维持挂起｜缺口3（效果尺）未落（known-gap 登记不替代尺）｜缺口4/5 维持。
- **自审闸三态（刷新后）**：**未干（维持）但处置方向已闭**——卷作 M1 封矿 F128 环的**退役前判据基线**使用；§五①逐件阅读转为净删前尽调语义，②敏感字段清单核对仍开放（known-gap 的未来补线依赖它）。
- **复跑**：`git show 794f16569b --stat`｜`sed -n '40,47p' src/zephyr/data_security/__init__.py`（DEPRECATED+known-gap 注记）｜`grep -n "promoted_to: src/zephyr/data_security" docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml`（晋升留痕与本批退役注记对照=“晋升≠接线”通用教训的双锚）。

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
cd /d/ZephyrAlpha
# P1/P3 件数与骨架层空实现自证（期望 10 / 各层 0）
git ls-tree -r --name-only HEAD src/zephyr/data_security | wc -l
for d in api services models infrastructure core _extensions; do echo "$d=$(git ls-tree -r --name-only HEAD src/zephyr/data_security/$d | grep -vc '__init__.py')"; done
# W1 三态 import 分类（期望 PROD=0）
python -c "
import ast,subprocess,collections
f=collections.Counter()
files={l.split(':',1)[1] for l in subprocess.run(['git','grep','-l','zephyr.data_security','HEAD','--','*.py'],capture_output=True,text=True,encoding='utf-8').stdout.split()}
for p in sorted(files):
    if p.startswith('src/zephyr/data_security/'): continue
    s=subprocess.run(['git','show','HEAD:'+p],capture_output=True,text=True,encoding='utf-8',errors='replace').stdout
    if not s.strip(): continue
    try: t=ast.parse(s)
    except Exception: continue
    tc={n.lineno for i in ast.walk(t) if isinstance(i,ast.If) and 'TYPE_CHECKING' in ast.dump(i.test) for n in ast.walk(i) if isinstance(n,(ast.Import,ast.ImportFrom))}
    for n in ast.walk(t):
        ms=[n.module] if isinstance(n,ast.ImportFrom) and n.module else ([a.name for a in n.names] if isinstance(n,ast.Import) else [])
        for m in ms:
            if m.startswith('zephyr.data_security'):
                k='TC' if n.lineno in tc else ('TEST' if p.startswith('tests/') else 'PROD')
                f[k]+=1; print(k,p+':'+str(n.lineno),m)
print('SUMMARY',dict(f))"
# C2 SourceType 同名假阳性拆解（期望：l1_input 自有 class，且无 data_security import）
grep -n "class SourceType\|data_security" src/zephyr/security/llm_defense/llm_security/layers/l1_input.py | head -3
# T1 测试面（期望 3）
git grep -l "zephyr\.data_security" HEAD -- 'tests/*'
# A1/A2 触发面（期望脚本与配置零命中；机器任务无本包项）
git grep -ln "data_security" HEAD -- '*.ps1' 'config/*' 'src/zephyr/data/config/*' | head
powershell -NoProfile -Command "Get-ScheduledTask -TaskName 'Zephyr*' | Select-Object TaskName,State | Format-Table -AutoSize"
# R1 在册三层 + 晋升留痕
grep -c "zephyr[./]data_security" docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml
grep -n "promoted_to: src/zephyr/data_security" docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml
grep -n "zephyr.data_security" .importlinter architecture_model/contracts/error_code_registry.yaml | head -4
# G1 效果尺缺位（期望零命中）
grep -in "masking\|脱敏\|data_security" docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml | head
```
