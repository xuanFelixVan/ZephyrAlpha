---
ttl: task_bound
completes_when: 战役收尾（99_final_delivery 落账）后随役归档 archive/2026-10
---

# [BLUEPRINT] | docs/_working/chief_fullchain_20261006/env_mining/env_21_arch_base.md |
<!-- [MODULE]  -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

# ENV-21 架构资产底座挖矿作业簿（B1 批次，2026-10-06）

## §0 环节档案

- **覆盖坐标**：`architecture_model/index.yaml`（74 域机生索引，schema 3.0.3）+ 蓝图 §0.2 分派表（`docs/03_modules/_master_blueprint/blueprint_baseline.md:148`）+ REG-FUNC-DOMAIN-001 功能域册（`docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml`，94 entries）。
- **真源锚**：index←depgraph PG domains 表（`dm200916_write_direct.py` 派生禁手编，GATE-ARCH-MODEL reconciler 自动重生，:29-32 声明）；func 册=模块/脚本功能域声明唯一真源（SSoT 门禁查重叠，`sync_yaml_to_depgraph.py` 回写 depgraph）；蓝图=人工设计态（MOD-MASTER_BLUEPRINT v1.3.4 索引件，指向 baseline/capacity/agent_spec 三拆件）。
- **职责一句话**："AI 找模块只有一条路：按域找"（index :36）——三册构成域分类的派生面（index）/声明面（func）/设计分派面（蓝图 §0.2）三层。
- **状态总判**：index 当日机生最新（last_updated 2026-10-06）；func 册**字段滞后实证**（last_updated 07-19 vs mtime 09-30 07:07，滞后 73 天）；蓝图 §0.2 数字已三代漂移（88 字面→去字面→今 26 行）——三册各自活着，互映射靠散文。

## §1 六向台账

| 向 | 内部反查发现（带路径） | 外部 | 判定 |
|---|---|---|---|
| 上（真源面） | index 真源=depgraph domains 表（query_hints :383 `extract_depgraph.py --summary` 为查询口）；func 册真源=自身 entries（**实测 grep -c "^- domain:"=94，与 ROOR entry_count: 94（:389）一致**，counting_rule"2026-09-06 实测物理真源回填"）；蓝图 §0.2 真源=人工表（kimi audit D-09 批"不扩行"在册） | ROOR :383 func 册 status: active 注"2026-09-18 补（BRK-084：该条目原缺 status 键，是 ROOR 唯一结构不完整条目）"——补键史在册 | pass |
| 下（消费面） | func 册→SSoT 门禁（创建模块/脚本时查功能域重叠，ROOR :384）+`sync_yaml_to_depgraph.py sync_functional_domain_registry`（domain_name_zh 通道，头注 :26-29）；index→query_hints 十四问+GATE-ARCH-MODEL reconciler；蓝图 §0.2→新 AI 冷启动分派（`blueprint_baseline.md:3439`"读本蓝图 §零 分派表→定位你的任务域"） | — | wired |
| 内（三册映射缺口——本簿主挖，五点） | ①**键系三套不互通**：D_*（index 74）vs domain+subdomain（func 94 entries/**79 distinct 域**）vs CT-*/系统名（蓝图 26 行）——无机械映射字段，唯一显式互引=index b_track mcp 条目注"MOD-MASTER-001 §0.2"（:118）。②**包含关系实测**：index74 ⊂ func79（comm 双向比对：index 74 域全被 func 覆盖零缺失；func 多出 5 域=D_EXECUTION/D_ORDER/D_PORTFOLIO/D_SIGNAL/D_TEST）。③**层分布**：L2 45+L1 20+L0 7+**空 2**（D_INFRASTRUCTURE/D_RESEARCH layer_id:null，:264-266/:330-332）——4 值枚举外第 5 态"未分层"在册未声明；**L3_application 枚举在册零使用**（:35/:376）。④func 5 个额外域仅 D_SIGNAL 有退休注记（:1920-1922"源系统已退役、depgraph 已无节点；FDR 条目留存以保历史可追溯"），**其余 4 域无同类注记**。⑤func 头注自陈"全 63 域统一真源"（07-19 治本语）vs 今 79 distinct——头部散文滞后两代 | — | signal |
| 旁（同对象异轴） | 蓝图 §0.2 施工程度列（部分实现/空壳/已实现/设计中）与 index b_track status（implemented 12/under_construction 1）**同对象两轴两判**：如 FLE=b_track under_construction（:102-105）vs 蓝图行"部分实现"——语义接近但无对齐键；GOMAP families（ENV-18 450 模块）是第四套模块清单，经 depgraph 间接挂 74 域 | — | signal |
| 史（数字三代漂移链） | 蓝图 §0.2：旧版":499『### 0.2 AI Agent 分派表 (88域)』"→kimi audit D-09（`docs/_working/archive/2026-09/kimi_audit/adjudications/p7b_bd_family_rulings.md:51`）判"不扩行（无新增任务域）；字面(88域)按文档纪律去字面（ROOR 现值 91）"→今实体 26 行（25 专项+1 横向 CT-* 簇，本簿 awk 实测 :149-176）；**88→91→94 三处数字三个时代**，骨架 `01_skeleton_environments.md:78` 的"88 任务域"承袭的是已废字面 | — | signal |
| 新（本簿 2026-10-06 三条） | ①**func 册字段滞后实证**：last_updated='2026-07-19'（:14）vs mtime=2026-09-30 07:07——滞后 73 天，说明 last_updated 未挂写入路径（sync 通道更新内容但漏更字段，或存在裸写）；②空 layer_id 2 例+L3 零使用=枚举契约与数据漂移；③退休域注记纪律 1/5——D_SIGNAL 式注记未成惯例 | — | signal |

## §2 挖干自评

- **主挖项完成度**：三册互相映射缺口挖到字段级五点（键系/包含/层分布/状态轴/数字漂移）；74 vs 79 vs 26 三数全部实测（grep/comm/awk）非转抄非背数。
- **"88 任务域"疑云收敛**：骨架口径经 kimi audit D-09 裁定链溯源——88 是旧版散文字面已废，现值=26 行实体任务域+横向 CT 簇；ROOR 同期 91→94 又一证"数量勿背数"。
- **三扫收敛**：正向映射（index→func comm 双向）✅；纵向三代（git 头注/mtime/裁定档案）✅；消费面（SSoT 门禁/sync/reconciler/query_hints/冷启动分派）✅。
- **长尾（如实登记）**：depgraph PG domains 表 live 未直查（DB 红线+只读约束，以 index 机生面+extract_depgraph 查询口为间接证据）；"88 域"原始清单旧版全文未取回（D-09 已裁去字面，无施工价值）；func 册 94 entries 与 79 distinct 之差 15=同域多 subdomain 拆条（unique_key=domain+subdomain，:30-32），非漂移。

## §3 挖后自审闸三态裁定

**施工**（字段级小件批，low 域，三件）：
- ①func 册 4 个退休域（D_EXECUTION/D_ORDER/D_PORTFOLIO/D_TEST）补 D_SIGNAL 式退休注记（原因+日期+depgraph 无节点实证）；
- ②func 册 last_updated 纪律收口：核 `sync_yaml_to_depgraph.py` 是否应自动刷新该字段，若有裸写路径则收口到 sync 通道（带路径证伪后定案）；
- ③index 空 layer_id 2 域（D_INFRASTRUCTURE/D_RESEARCH）补层或把"未分层"显式入枚举契约——架构数据走 apply_*.py 直写 DB（RULE-SSOT 分道），GATE-ARCH-MODEL reconciler 重生验证。
- **理由**：全有机械判据、无 Owner 门位（非注册表净删/flag 翻转/生产流转）；涉规则数据（func=YAML）与架构数据（depgraph=DB）须按 RULE-SSOT 分道施工。
- **封矿**：**"三册键系统一/建 D_*↔CT-*↔domain+subdomain 机械映射表"判封矿**——三册真源语义各异（物理分类/功能声明/设计分派），强并违反 w5_1"跨域不同对象不并"；以各自 boundary/注记互指代替映射表（现状 b_track mcp 注即此形态）。
- **解锁条件**：施工件=常规 claim+depgraph 登记（RULE-DEPGRAPH）+CREATE-GUARD/翻译册登记义务照走；封矿件解锁=仅当 Owner 裁定改变三册真源分工时重开。

## §4 挖矿日志

- **轮1（2026-10-06）**：全读 index.yaml 426 行（74 域/12 分区/b_track 13/global_stats/query_hints）+func 册头部与 schema——发现空 layer_id 2 例、L3 零使用、头注 63 域散文。
- **轮2**：三册数量实测（grep -c entries=94/comm 双向比对 74⊂79/awk 数蓝图行=26）；"88 任务域"溯源（kimi audit D-09 档案 :51/:179 双锚）——判定骨架数字承袭已废字面。
- **轮3**：消费面反查（SSoT 门禁/sync_yaml_to_depgraph/query_hints/冷启动行 3439）；func 册 mtime 对拍 last_updated（73 天滞后）；五缺口归纳与三态裁定收口。
