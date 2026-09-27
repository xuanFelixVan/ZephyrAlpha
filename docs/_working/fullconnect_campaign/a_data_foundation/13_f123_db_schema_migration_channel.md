---
ttl: task_bound
title: "F123 DB schema 迁移通道（REG-MIGRATION-001 迁移册）复飞案卷"
session: st-c7-mine-20260927
---

# F123 DB schema 迁移通道（A 段 F07 邻位，P0，骨架态=unmined(new id)）

> 立卷依据：`docs/_working/fullconnect_campaign/00_skeleton/00_skeleton_verified.md` §二 B-9 行给 F123 定号，
> 判定理由原文="REG-MIGRATION-001 迁移册 276 行…A 段 F07 邻位，DB schema 迁移通道——F07 只写 depgraph 不含迁移纪律"。
> 本卷首要结论：**该定号理由与册面实态相反**——REG-MIGRATION-001 是"旧路径→新路径"的文件迁移登记表且已冻结退役，
> 与 DB schema 迁移无关；真正的 DB schema 迁移面在盘上以 33 个散装 `apply_*_ddl.py` 存在、无版本册、无回放纪律（见 §三、§四）。

## 一、六向台账（2026-09-27 实证，基准=HEAD 3b4b1f86a1）

| 向 | 实测证据 |
|---|---|
| 实现件 | 命名载体：`docs/01_policies_and_standards/_registry/catalogs/migration_registry.yaml`（实存，276 行，`git cat-file -e HEAD:` 通过；entries=37，status 分布 done=24 / pending=13，实测口径见 §六 M2）。骨架态语义所需载体（schema 迁移通道）：**盘上无此件**——`git ls-tree -r --name-only HEAD \| grep -cE "apply_.*_ddl\.py$"` = 33 个一次性 DDL 脚本（例：`scripts/ch/apply_consensus_daily_ddl.py`、`scripts/ai_layer/apply_ai_layer_scheduling_ddl.py`），无统一入口、无版本序列、无回滚件。 |
| 上游输入 | 人工登记（`[STARTUP] passive`，册头 :6）；无生成器写它——`git grep -ln "migration_registry" HEAD -- 'scripts/governance/generators/*'` 仅命中路径树展示侧两件（见下行），无写者。 |
| 下游消费 | 真实读取方 4 件，全部是**代码搬家脚本**而非 schema 工具：`scripts/migration/dm311_autonomy_core_split.py:50`、`scripts/migration/dm314_infra_ops_split.py:49`、`scripts/governance/generate_project_path_tree.py:674-680`、`scripts/governance/d5_architecture/pre_delete_safety_check.py:77`；另有展示侧标签字典 `scripts/governance/d5_architecture/generators/generate_path_tree.py:447`。M1 六向台账 dir4 亦只采到 config-reader=`generate_path_tree.py` 一腿（`.runtime/tmp/st-c7-m1-inbox/six_direction_ledger.yaml` environments.F123.dir4_consumer）。 |
| 测试 | `git grep -l "migration_registry" HEAD -- 'tests/*'` = **1 件**（§六 T1），且为路径树/展示面断言，非 schema 迁移断言；schema 迁移面测试=**0**（无件可测：无版本册、无回放器）。 |
| 自动化触发 | 无。册头 `[STARTUP] passive`；消费方 `scripts/migration/*.py` 为人工一次性 CLI（`dm311/dm314` 头部 `[INVARIANTS]` 自述"剪切粘贴模式(shutil.move)…移动后更新迁移登记表 status"）。计划任务面零命中（§六 A1）。 |
| 真源与注册表 | ROOR 在册：`docs/registry_of_registries.yaml:408` `- registry_id: REG-MIGRATION-001`，name=**"迁移登记表（已冻结）"**，`maintenance: frozen`；册头自述 `[MATURITY] deprecated`(:7) / `[STABILITY] frozen`(:10) / `[AI_AUTONOMY] ai_read_only`(:12) / `[TTL] permanent … 待全量 pending 条目完成后手动退役删除`(:13)。真源方向：本册=规则数据（YAML 真源，RULE-SSOT）；但它自述"功能与 depgraph edges 表重叠"(:8) ⇒ 同真源可派生 ⇒ 按根宪法 §4.2 内收判据属"必并/退役"族，不属"新建环节"族。 |
| 门禁与质量尺 | 自身带 `[MODIFY-GUARD] 禁止新增条目（已冻结）；仅允许将 pending→done 状态流转`(:9)；消费脚本带 `[MODIFY-GUARD] migration_registry.yaml格式变更需同步`（dm311:9 / dm314:9）。schema 侧对偶门禁缺位：无任何 gate 校验 `apply_*_ddl.py` 与库内实际 schema 一致（§六 G1 实测 gate_registry 零命中 schema-migration 类门）。 |
| 当前运行状态 | **命名载体在跑（只读、冻结、退役轨道）／语义环节空转（无实现）**。13 条 pending 未清即退役未完成，但冻结令禁止新增，故本环节既不能扩展也不已归零。 |

## 二、子模块三级枚举

1. **REG-MIGRATION-001 命名载体族**（一级：路径迁移登记）
   - 二级=数据册：`migration_registry.yaml`（entries 37 / done 24 / pending 13）
   - 三级=条目生命周期：`status: pending → done` 单向流转；旧路径→新路径映射；连字符改名史（`migration-registry.yaml` → snake_case，2026-07-16，册头 :14）
   - 二级=消费端：搬家执行器（`governance_root_split.py`、`dm311_autonomy_core_split.py`、`dm314_infra_ops_split.py`）｜路径树展示器（`generate_project_path_tree.py`、`d5_architecture/generators/generate_path_tree.py`）｜删除前安全闸（`pre_delete_safety_check.py:77` 把它列入删除保护路径）
2. **schema 迁移真实面（骨架定号所指、本卷新发现）**
   - 一级=DDL 施加器 33 件，二级按引擎分族：CH 族（`scripts/ch/apply_*_ddl.py`，例 `apply_consensus_daily_ddl.py`/`apply_anchored_state_ddl.py`/`apply_cross_asset_ddl.py`）｜PG 族（`scripts/industry_graph/apply_industry_graph_ddl.py`，F07 卷已引）｜AI 层族（`scripts/ai_layer/apply_ai_heritage_ddl.py`/`apply_ai_intake_ddl.py`/`apply_ai_layer_scheduling_ddl.py`/`apply_model_library_ddl.py`）
   - 三级=每件的"建表即定版"纪律：无版本号、无 down 脚本、无 `IF NOT EXISTS` 统一约束审查面
   - 一级=底座：`zephyr.infrastructure.database_service`（根宪法 §9.1 唯一 DB 入口，本环节的 DDL 施加须经它，不得裸 connect）
3. **邻位关系**：F07（PG 架构库）＝depgraph 元数据；F126（字段字典）＝字段级 schema 真源；F125（data_governance）含 `core/schema_registry.py`（三级件，见该卷）。三件与 F123 的边界=**"schema 定义"归 F126/F125，"schema 变更落地"归 F123**——后者目前无载体，是本卷 P0 缺口本体。

## 三、接线四态独立复核

四态口径：已接线（有实现+有生产消费者+有触发或明确按需语义）／半接线（部分腿通）／装饰（件在盘但生产面零消费，或守卫无供给方）／死（引用不存在）。

- **REG-MIGRATION-001 命名载体 = 半接线（偏退役）**：读取腿真实通（4 个非展示消费者、`pre_delete_safety_check.py` 的删除保护在用它），写入腿被冻结令关闭（禁止新增，只允许 pending→done），产出侧无人排班执行剩余 13 条 pending。它不是装饰件，但已是"只出不进"的退役通道。
- **骨架定号语义（DB schema 迁移通道）= 装饰偏死**：本环节名义上的实现件在盘上不存在。判据链：①`git grep -il "alembic|schema_migration|migrate\.py" HEAD -- '*.py' '*.toml'` 命中面全为无关噪声（无迁移框架）；②33 个 `apply_*_ddl.py` 之间无序号、无 registry、无 status 字段，`git grep -n "migration_status\|ddl_version" HEAD -- 'scripts/ch/*' 'scripts/ai_layer/*'` 零命中；③无生产消费者读取"迁移状态"（因无状态面可读）。⇒ **"环节在册、载体不存在"是本卷最重要的独立复核结论**，不得因命名册在跑而判本环节已接线。
- **装饰形态专项（本仓最常见假绿源）**：册头 `[CONSUMERS]` 自列 3 个脚本——自述不构成接线证据；实核 4 件真实读取（多出 `pre_delete_safety_check.py`）+ 展示侧 1 件，实测优于自述，故登记面判"通"。反向地，`scripts/_archive/migration/generate_migration_registry.py` 在归档目录，按 `git ls-tree HEAD` 在盘但**不在产**，不消费者数（§六 C2 区分）。
- **无死链**：本卷引用路径逐条经 `git cat-file -e HEAD:<path>` / `ls` 实核存在。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | F123 定号语义（DB schema 迁移通道）盘上无载体：33 件散装 `apply_*_ddl.py` 无版本册、无回放/回滚、无一致性尺 | 施工：先立 schema 迁移登记册（版本序列+引擎+状态+down 策略四字段），再把 33 件纳入登记；净零声明须写明与 depgraph edges 的关系（避免第二真源，根宪法 §4.1） | P0 |
| 2 | 骨架 §二 B-9 的定号理由与 REG-MIGRATION-001 册面实态相反（"迁移纪律"≠"路径映射"） | 挂起：属骨架勘误面，须总筹在 `00_skeleton_verified.md` §二 B-9 行改注，挖矿道不代改总册 | P0 |
| 3 | REG-MIGRATION-001 的 13 条 pending 无排班执行者，退役永不能达成（ROOR 与册头均自述"待全量 pending 完成后退役删除"） | Owner 门位：注册表净删属根宪法 §5 high 域（"注册表净删 → Owner"），本道不代裁 | P0 |
| 4 | schema 面与 F126（field_dictionary 262 fields）/F125（`data_governance/core/schema_registry.py`）无对账尺：改表后字段字典是否同步不可机检 | 施工：与 F126 卷缺口 D1 合并成一批（同一把尺两侧读） | P1 |
| 5 | 33 件 DDL 施加器无 depgraph 登记义务核验（F07 卷 D3 同类） | 施工：`apply_depgraph.py --add-design-node` 补设计节点，随 F123-F132 落号批 | P1 |

## 五、自审闸三态

**未干。** 理由（不含修辞）：①本环节名义语义（schema 迁移通道）的穷尽枚举要求"33 件 DDL 逐件读侧/写侧/幂等面核完"，本卷只完成了**清点与分族**，未逐件验 `CREATE TABLE` 与库内实际列的一致性（那需要 DB 实连，凭据走 secrets 通道，本夜未取）；②缺 1 的替代方案设计未定（登记册字段与净零声明需要总筹确认它不与 depgraph edges 重复，属改判据面）；③缺 3 属 Owner 门位，非本道可闭。已做到的部分：命名载体六向全锚、四态分面判定、33 件分族与"载体不存在"证伪。

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
cd /d/ZephyrAlpha   # 或任一 worktree，HEAD 同基
# M1 命名载体在 HEAD + 行数
git cat-file -e HEAD:docs/01_policies_and_standards/_registry/catalogs/migration_registry.yaml && echo INHEAD
wc -l docs/01_policies_and_standards/_registry/catalogs/migration_registry.yaml
# M2 条目状态分布（期望 entries=37, done=24, pending=13）
python -c "import yaml,io,collections;d=yaml.safe_load(io.open('docs/01_policies_and_standards/_registry/catalogs/migration_registry.yaml',encoding='utf-8'));e=d['entries'];print(len(e),collections.Counter(x.get('status') for x in e))"
# C1/C2 消费者（在产 4 件 + 展示 1 件；归档件单列不计）
git grep -n "migration_registry" HEAD -- 'scripts/*.py' 'src/*.py' ':!tests/*'
git ls-tree -r --name-only HEAD | grep -i migration | grep -v "^docs"
# T1 测试面（期望 1 件）
git grep -l "migration_registry" HEAD -- 'tests/*'
# S1 schema 迁移真实面清点（期望 33）
git ls-tree -r --name-only HEAD | grep -cE "apply_.*_ddl\.py$"
# S2 无迁移框架自证（命中面应为无关噪声）
git grep -il "alembic\|schema_migration" HEAD -- '*.py' '*.toml' | head
# A1 自动化触发面（期望零命中）
git grep -ln "migration_registry" HEAD -- '*.ps1' 'config/*' | head
# G1 schema 迁移门禁缺位自证（期望零命中）
git grep -in "schema.migration\|ddl" docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml | head
# R1 在册态（ROOR frozen 自述）
grep -n -A3 "REG-MIGRATION-001" docs/registry_of_registries.yaml | head -8
```
