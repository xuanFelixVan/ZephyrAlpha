---
ttl: task_bound
---

# M3 分册 03 · 注册表族治理（ROOR 之外的真源册清单）

> 挖掘 2026-09-25 ｜ 车道 M3 ｜ 只读挖矿，零 commit。ROOR=`docs/registry_of_registries.yaml`（77 册）。
> gate 三册 115/102/180 底数出处：`docs/_working/commit_speedup_campaign/90_verification/decisions_log.md` 19:3x 行（:33）。

## 一、环节定义与边界

一句话：ROOR 总纲之下 M3 关心的真源册子集（gate/能力/翻译/风险/裁定/词表）——
各自的维护方式（生成器 vs 手工）、生成器入口、实测条目数、已知漂移及现状复核。

## 二、六向台账

| 向 | 内容 |
|---|---|
| 上游输入 | 生成器（generate_gate_registry.py 等）、手工编辑、reconciler auto-commit（gate_registry_sync/in_process_drift） |
| 下游消费 | gate_auto_registrar.py（YAML 驱动注册）、capability_lookup、翻译 loader 三层、risk_tier 门位判定 |
| 自动化触发 | gate_registry.yaml 由 post-commit reconciler 重生成（GATE-GATE-REGISTRY-SYNC, priority=830）；in_process 册双向漂移检测（GATE-IN-PROCESS-REGISTRY-DRIFT, priority=831） |
| 真源与注册表 | 本册；ROOR 为发现唯一入口（RULE-REGISTRY） |
| 门禁与质量尺 | RULE-REGISTRY（勿背数）、文档纪律"计数用字段不写死"（宪法 §4.3）、REGISTRY-MASS-DELETION 门 |
| 当前运行状态 | 黄（gate 三册两口径漂移仍在：模块 114 vs 在册 102 vs 总册 180；own_scope 缺口变形态存续） |

## 三、ROOR 总纲底数（实测 2026-09-25）

- **77 个 registry_id**；维护方式分布：**manual 58 / auto·script_generated·code_inline 13 / frozen 3**
  （grep 计数可复现）。→ 全项目注册表 75% 手工维护，是"静态清单禁手工维护"红线的系统性张力面。
- tier0 核心源码级 10 册；gate 相关四册：REG-GATE-001（rule_enforcement/_registry.yaml, 91 条, manual）、
  REG-GATE-CAT-001（catalogs gate 总册, 169 条底数, manual）、in_process 册（#ARCH-GATE-REGISTRY-AUTO-001 治本产物）、
  catalogs/gate_registry.yaml（auto 机生）。

## 四、M3 真源册逐册台账（实测数字）

| 册 | 路径 | 条目（实测） | 维护 | 生成器/对账 | 漂移判定 |
|---|---|---|---|---|---|
| gate 总册 | docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml | **180**（total_gates 字段） | **auto**（generated_by=scripts/governance/generators/generate_gate_registry.py, maintenance=auto, **generated_at=2026-09-24T07:29:34Z 当日再生**） | post-commit reconciler GATE-GATE-REGISTRY-SYNC | 与 in_process 册差 78（180 vs 102）——总册含 pre-commit+规则册+runtime 各面，非同对象不并（w5_1 判据），但**比例差无册面解释**=待补注释 |
| in_process 册 | 同目录 in_process_gate_registry.yaml | **102/102 自洽**（total_gates=102） | 手工追加条目+YAML 驱动自动注册（gate_auto_registrar.py）；册头无 generated_at（手工册特征） | GATE-IN-PROCESS-REGISTRY-DRIFT 双向漂移检测（warn） | 自洽但滞后于模块面（见下） |
| commit_gates 模块面 | src/zephyr/gov_enforcement/commit_gates/*.py | **114**（非 test .py，19:3x 底数 115，**-1**） | 代码即真源 | GATE-MODULE-INVENTORY-SYNC（正向漂移检测 priority=820） | 三口径 114/102/180 与底数 115/102/180 相比：**模块面又漂 1**，102/180 未变——C1-E5"名册不同步"病灶仍在 |
| own_scope 机生面 | gate_registry.yaml gates[].own_scope | **True 33 / False 80 / 缺失 67**（=180） | 机生（当日再生后显式 False 80 出现） | generate_gate_registry.py | 19:3x 记"own_scope=None 实为 67"；现状=67 缺失+80 显式 False=**147/180 非 own-scope**。机器写了 False 但 67 条连字段都没有——机生覆盖缺口从"全缺"收敛为"边界缺"，方向改善、未清零 |
| 规则册（REG-GATE-001） | src/zephyr/gov_enforcement/rule_enforcement/_registry.yaml | **91** | manual | 无机生 | ROOR 记 91=实测 91，自洽 |
| 能力卡 | data/capability_cards/ | **44 卡** | 手工 | capability_lookup 渐进披露 | — |
| capability canonical | catalogs/capability_canonical_file_registry.yaml | 存在（结构型） | manual | — | — |
| 术语三层-术语 | catalogs/terminology_glossary.yaml | **279 entries** | manual | translation loader 消费 | — |
| 术语三层-域 | catalogs/functional_domain_registry.yaml | **94 entries** | manual | 同上 | — |
| 术语三层-模块 | catalogs/module_translation_registry.yaml | **7776 entries** | manual | 同上 + TRANSLATION-COVERAGE Layer4 reconciler（priority=951 全扫落 drift_report） | — |
| risk_tier 门位册 | catalogs/risk_tier_registry.yaml | tier_1_governance，结构 tier: high|medium|low + **default_tier: low** | manual | 宪法 §5 未列出域默认 low | — |
| 裁定册 | catalogs/ruling_registry.yaml | **231 rulings** | manual（RULE-RULING：裁定#NNN 同 commit 原子） | — | — |
| ROOR 自身 | docs/registry_of_registries.yaml | 77 registry_id | manual | registry-consistency 校验脚本扫描范围由它驱动 | — |
| 脚本清单主册 | scripts/script-manifest.yaml（REG-SCRIPT-001） | ROOR 记 991 | **auto**（generate_manifest.py 全树再生） | 机生 | — |

### 卫生漂移（顺带实证）
- catalogs/ 目录内残留 `.tmp.21732.*`（alert_threshold_registry.yaml.tmp.*）与
  `.bak_pre_one_question`（candidate_module_registry.yaml.bak）——注册表目录非零临时文件，safe_write 残片/手工备份未清。

## 五、堵点与病灶

| # | 现象 | 根因 | 修法草案 | 工作量 | 本车道可修 |
|---|------|------|---------|--------|-----------|
| G1 | 三口径漂移 114/102/180 且无自动对账闭环 | in_process 册人工追加、模块面自由增删；GATE-INVENTORY-SYNC 只 warn | 对账生成器化：generate_gate_registry.py 扩展输出三口径 diff 段（19:3x 修法方向已指同名册对账生成器化，未落地） | M | 修法可出，施工待批 |
| G2 | own_scope 67 条字段缺失 | 机生扫描面对部分 gate 类型不可达（推断，需生成器侧确认） | 生成器补全缺省值（如 own_scope: unknown）替代缺失，消歧"没扫到"vs"确认非" | S | 是 |
| G3 | ROOR 77 册 75% manual | 无再生器 | 按 w5_1 内收判据逐册判"同真源可派生→必并"——单独立项，不宜本战役内动 | L | 待裁 |
| G4 | catalogs 内 tmp/bak 残片 | safe_write 崩溃残片未回收、手工备份违规 | 清理+补 safe_write 残片回收钩子 | S | 是 |
| G5 | ms≥1.0 过滤盲区 42-44%（C1-§3）"零触发零消费"不可证 | commit_gate_registry.py:108 过滤在采集层 | stats 落盘去门槛（ms 字段全量、视图层过滤）——19:3x 修法方向 | M | 施工归 commit_speedup 批次 |

## 六、提速与合并机会
1. **翻译三册与 module_translation_registry（7776 条）是最大手工册**：已有 TRANSLATION-COVERAGE 双层（gate+reconciler），
   生成器化方向=从 depgraph 派生基线、人工只补差异（对齐"凡条目列表+计数必须生成器产出"红线）。
2. gate 总册（auto）与规则册（manual, 91）同为 gate 名录但对象不同（执行面 vs canonical 登记）——**不并**（跨域不同对象），
   但应在 ROOR 两条目的 description 互相指认，消"比例差无解释"。

## 七、自审闸三态
**挖干可施工**（每册有实测条目数+维护方式+对账机制；G1/G2/G4 本车道可施工；G3/G5 待裁/归他车道）。
底数核对结论：**19:3x 的 115/102/180 → 现状 114/102/180**（模块面 -1，其余两册数未变；own_scope 缺口从 67 全缺变 67 缺失+80 显式 False）。

## 八、复核命令
```bash
grep -c "registry_id:" docs/registry_of_registries.yaml                # 77
python -c "import yaml; d=yaml.safe_load(open('docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml',encoding='utf-8')); print(d['total_gates'], d['generated_at'])"   # 180 2026-09-24T07:29:34Z
python -c "import yaml; d=yaml.safe_load(open('docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml',encoding='utf-8')); print(d['total_gates'], len(d['gates']))"  # 102 102
find src/zephyr/gov_enforcement/commit_gates -maxdepth 1 -name "*.py" ! -name "__init__.py" ! -name "test_*" | wc -l   # 114
```
