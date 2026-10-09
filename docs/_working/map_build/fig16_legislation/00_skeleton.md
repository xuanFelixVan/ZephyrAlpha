---
ttl: task_bound
completes_when: 图16 四件套（config/governance_legislation_map.yaml+生成器+校验器+GOVERNANCE-LEGISLATION-MAP gate）与 master map 激活边随批落地后，本件退役为归档参考
title: 图16 治理立法流图·状态机总骨架（00_skeleton，本图唯一收敛基准）
owner: st-fig16-20261005
---

# 图16 治理立法流图 00_skeleton

> 一句话域：**一条裁定（治理立法）从"呈报"到"生效/取代/废弃"的状态序列，以及承载它的机械流水线（取号→意图登记→同commit原子门→快照→投影→消费→取代链→复活禁令）——不管裁定内容本身写了什么（那是各规则真源），不管治理运行时怎么跑（那是图10 GOMAP）**。
> 准入依据=裁定#486 ①（Owner 2026-10-05 双批，立项卡呈批制首例；四道门全过、两道保险丝）。普查判定原文=`docs/_working/map_census/00_panorama_map_census_v1.md:60`（图16 行）——本骨架**取代其"与 GOMAP 扩治理排程层合并评估"倾向**（该评估基于 PG 化前 7 步手工流程前提，7f0beccac4 cutover 后前提已失效；实测立法链已是一条全自动机械流水线，见 §2）。
> **对旧战役骨架的取代对账**：`docs/_working/map_build/fig16_ruling/00_skeleton.md`（st-mapbuild-20260924，结论=不建）自带重开触发条件（其 §6.2）——R-1 取号器落地已触发（`scripts/governance/next_ruling_id.py`，Z-38 落地）、R-5 撞号处置制度化已触发（裁定#485 ①跳号永不复用+void 墓碑台账）、R-2 前提被 pg_ledger cutover 改写（registry_entry/event/snapshot 三表面即流程位置维度的机械载体）。裁定#486 即 Owner 认可的重开件，旧件按其自身 completes_when 退役为归档参考。编号分族声明：旧环节号 `D16-01..14` 归档不改义；本骨架采用分族编号 `D16-S*`（状态）/`D16-N*`（机械机构）/`D16-T*`（合法迁移）/`D16-X*`（禁止边），与旧环节号不互用不互指，防考古混线。
> 本图是**实例级状态机**（对象=一条裁定，键=ruling_id），不是环节流程图；机械节点是状态机的**承载机构清单**，不是工作流站点。旧骨架 E1"机生两难"（真源无流程位置字段⇒只能手画流程）对状态机形态失效：状态枚举=账本 payload.status 机械闭集，无需手画任何流程格。
> 状态纪律=`sop/mining_sop/skeleton_mining_policy.md` §5：每个 ✅ 必附实查路径/命令。本件全部计数在主区 2026-10-05 实测（复核命令见 §7）。

## §0 域定义与四道门实证（裁定#486 ①）

**域职责**：管"一条治理立法的可信生命周期与它的机械承载链"——编号唯一不回收、登记必经意图API、引用必同 commit 原子、取代必有链、复活必开新号。存在理由：裁定是全仓最高效力规则资产，其登记面曾被"grep-and-claim 占位"病根支配（裁定#20-A 治本）；今天这条链每小时都在被全仓消费（任何 `裁定#NNN` 引用、任何审批授权、任何取号动作都打在上面），却没有一张图说清它的状态与禁令——本图补这个缺。

| 门 | 论证（实查锚） | 判 |
|---|---|---|
| ①独立触发+终点 | 触发=裁定事件（呈报/撞号/让号/执行完毕）；终点=superseded/deprecated/decided/void 四终态。生命期跨月（裁定#1 草案至今在册），非单次流程 | PASS |
| ②跨模块交接 | 呈报口（map_build 立项卡/总包令）→取号器（next_ruling_id）→意图API（registry_ledger.api）→原子门74（ruling_reference_gate）→快照（publish_snapshot）→投影（ruling_registry.yaml render）→消费方（approval_resolver/reference 类 gates/对齐清单）→取代链。五站七件三种介质（PG 账本/yaml 投影/占号文件） | PASS |
| ③不被现有图覆盖 | 图10 GOMAP 管治理**运行时**（families/pipeline：谁在跑、谁守护谁）；本图管治理**立法面**（规则怎么诞生、怎么死）。对象不同（运行进程 vs 立法条目）、键空间不同（families/tags vs ruling_id）、词汇零交（GOMAP 全文无 ruling_id 键，`config/governance_operations_map.yaml` 实查）——跨域不同对象不并（w5_1） | PASS |
| ④机生真源 | pg_ledger 账本（REG-RULING-001，PG 344 行=active 302+retired 43，快照 v9）+裁定册 yaml（303 条投影）双面在册；生成器只做机读镜像，实例计数全部账本现算 | PASS |

**两道保险丝（裁定#486 ①）**：
- 结构下限：有意义节点（§1 六态+§2 九机构）=**15 ≥ 12**，判活，不停工（判据过程见 §5）；
- 实例纪律：裁定实例=**数据行非节点**（INV-1 同款）——302 条在册裁定一条都不进 nodes，实例计数只进图 counts 段，由生成器对账本现算。

## §1 状态全集（6 态，编号 D16-S1..S6；枚举真源=账本 payload.status 实测，禁自造）

实测分布（PG `registry_entry` WHERE registry_id='REG-RULING-001' AND status='active'，2026-10-05）：`active 282 / decided 13 / superseded 4 / void 2 / draft 1 / deprecated 0`（yaml 投影面 303 条含本批 #486 同分布）。

| state_id | value | name_zh | 语义 | 实测 | 终态 | 真源锚 |
|---|---|---|---|---|---|---|
| D16-S1 | draft | 草案 | 已占号登记、尚未生效；审批通道不认（`approval_resolver.py:274` 仅 active 放行） | 1（裁定#1） | 否 | `ruling_registry.yaml` 裁定#1 条目 |
| D16-S2 | active | 生效中 | 主通道在册态；唯一能承载 approved_paths 授权与被 gate74 认可引用的状态 | 282 | 否 | `approval_resolver.py:274`；裁定#461 授权在窗实证 |
| D16-S3 | superseded | 被取代 | 新裁定取代旧裁定；superseded_by 必填（#20-D 铁律9） | 4（#165/#199/#201/#468+账本观测） | 是 | `ruling_registry.yaml` 铁律#9 注 |
| D16-S4 | deprecated | 已废弃 | 四值枚举内预留废弃位；当前零实例（结构性预留，非自造） | 0 | 是 | `ruling_registry.yaml` 铁律#4 四值枚举；裁定#480 字段补丁批（f2dd263898）_ruling_channel 枚举铁律 |
| D16-S5 | void | 撞号墓碑 | 枚举外观测旁支：撞号处置留痕 tombstone，非裁定（占号防复用） | 2（#265/#408） | 是 | 裁定#265/#408 条目原文"tombstone，非裁定" |
| D16-S6 | decided | 已决归档 | 枚举外观测旁支：战役代裁/呈裁执行完毕归档（决策内容已消费，不再构成活授权） | 13（#403-#409/#481/#482 等） | 是 | 裁定#409/#481 等条目 status 字段实测 |

> 枚举纪律：S1-S4=机械闭集（四值枚举铁律，裁定#480 补丁批立；`approval_resolver._ruling_channel` 按此消费）；S5/S6=登记面历史遗留旁支，**照实收录不禁化**（禁自造状态的对面是禁删实测态）；两者不得承载授权（通道只认 active）。

## §2 机械节点清单（9 机构，编号 D16-N1..N9；每节点真源映射）

| node_id | 名称 | 职责一句话 | 真源（文件:锚点） | 实查证据 |
|---|---|---|---|---|
| D16-N1 | 呈报口 | 立项卡/总包令/呈裁件把立法意图送入链路；立项卡呈批制后 GO/NO-GO 权在 Owner（裁定#486 ②） | `docs/_working/map_build/22_fig15_card_lifecycle_charter.md`（先例）；`docs/_working/map_census/00_panorama_map_census_v1.md:60` | 图16 本卡=总包令内嵌裁定呈批首例 ✅ |
| D16-N2 | 取号器 | 裁定#NNN 原子占号：--next 幂等查询/--claim O_EXCL 独占/--release 仅本会话；编号不回收 | `scripts/governance/next_ruling_id.py`（Z-38 落地，裁定#20-D 铁律2） | 本包 claim_486.json 占号在案 ✅ |
| D16-N3 | 意图API | register/update/retire 按条目声明；接口负面清单（禁整册写）；CAS 409 拒绝记事件；retire 强制 authority_ref | `src/zephyr/governance/registry_ledger/api.py` §3.1/§3.2（W-M1） | 本包 #486 登记 entry_pk=72970/事件 110318 ✅ |
| D16-N4 | 同commit原子门74 | 新增 `裁定#NNN` 引用必须在册且册面同 commit；L1 编号空洞 warn；L2 原子性 hard block | `src/zephyr/gov_enforcement/commit_gates/ruling_reference_gate.py:301`（priority=74，#20-A/#20-B/#20-G） | 门槛常量 `_MANUAL_STAGE=False` 实查 ✅ |
| D16-N5 | publish 快照 | active 条目集发布为不可变快照；同 content_sha=noop 幂等；身份键置首防 jsonb 重排 | `src/zephyr/governance/registry_ledger/baseline.py:558` publish_snapshot | 现行 snapshot_version=9（本包 #486 发布）✅ |
| D16-N6 | render 投影 | 册 yaml=PG 投影（PG-wins 回滚盘面私改）；render 通道单写者；cutover=7f0beccac4 | `docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml`（册头 unique_key/entry_schema） | yaml 303 条 vs PG active 302 行=投影在途窗口实测 ✅ |
| D16-N7 | 消费方索引 | 谁在消费裁定：审批通道（_ruling_channel：active+expires_at+approved_paths）、reference 类 gates、取号分母、对齐清单挂轴。消费方运行宿主=GOMAP-001 域 git_commit_gateway 门链/图11 D11-C05 执行面；`cross_map_edge: {to: GOMAP-001, basis: 裁定#486①}` `feeds_map: GOMAP-001`（交接面处方B-16） | `src/zephyr/gov_enforcement/commit_gates/approval_resolver.py:266`；`scripts/governance/next_ruling_id.py --next` | 裁定#461 授权通道消费实证（本包批①过闸）✅ |
| D16-N8 | 取代链 | superseded_by 单向指针 + related_rulings 双向关联，议题-裁定互溯 | `ruling_registry.yaml` 铁律#9/#10 注；`next_ruling_id.py` 语义（ruling_id 键锚定防 related_rulings 误报） | 实测 5 条取代链：#165→#ARCH-016/#199→#200/#201→#ARCH-045/#265→#266/#468→#474 ✅ |
| D16-N9 | 复活禁令 | 编号不回收、跳号永不复用；复活=新号+related_rulings 指回（跨实例边）；撞号=void 墓碑 | `scripts/governance/next_ruling_id.py`（释放≠可复用）；BT-201 撞号事故制度化（裁定#485 ①） | 占号文件无 TTL 回收+CONFLICT_DUPLICATE 409 机械拒 ✅ |

## §3 迁移全集（9 条合法边 + 7 条禁止边）

### §3.1 合法迁移表（actor/credential 按机械事实归类）

| transition_id | from→to | 触发机械 | 凭证 | 实证 |
|---|---|---|---|---|
| D16-T1 | ∅→S1 draft | register(status=draft)（占号后草案先行） | 占号 claim | 裁定#1 在册 draft ✅ |
| D16-T2 | ∅→S2 active | register(status=active) 直批登记（主通道） | Owner 批文/呈裁批 | 本包 #486；#451/#452 同款 ✅ |
| D16-T3 | ∅→S6 decided | register(status=decided) 随批即决（战役代裁形态） | Owner 批文 | 裁定#404/#407 条目 ✅ |
| D16-T4 | ∅→S5 void | register(status=void) 撞号墓碑随处置批登记 | 处置批文 | 裁定#408 条目 ✅ |
| D16-T5 | S1→S2 | update 状态翻转（草案过批生效） | Owner 批文 | 四值枚举通道合法位（`approval_resolver.py:274` 消费面） |
| D16-T6 | S2→S3 | update + superseded_by 必填（#20-D 铁律9） | 新裁定号 | 5 条实测取代链 ✅ |
| D16-T7 | S2→S4 | update 废弃（枚举预留位） | Owner 批文 | 零实例（结构性预留） |
| D16-T8 | S2→S6 | update 执行完毕归档（decided） | 执行批 | #409 族归档形态 ✅ |
| D16-T9 | ∅→S2（**跨实例**） | 复活=新号 register + related_rulings 指回旧号；旧号状态不变 | 新批文 | 图15 D15-M17 同构；#20-D 编号不回收的合法出路 |

### §3.2 禁止边（禁止边是一半价值，一条不许丢）

| edge_id | 禁令 | 机械捕手 | 真源 |
|---|---|---|---|
| D16-X1 | 任何态→S2 同号就地复活（改旧条目翻回 active=伪造授权） | CONFLICT_DUPLICATE 409（同号异指纹）/事件审计 | #20-D 铁律2；`api.py` OK_NOOP 仅同键**同指纹** |
| D16-X2 | S3→S2 撤销取代（取代链单向不可逆） | 无 API 通道语义（update 须 reason+审计，翻转为伪造） | `ruling_registry.yaml` 铁律#9 |
| D16-X3 | 未占号登记（grep-and-claim 占位复辟） | 取号器分母感知（--next 列在途占号） | #20-A；`next_ruling_id.py` INVARIANTS |
| D16-X4 | 未登记先引用（悬空 `裁定#NNN`） | RULING-REFERENCE gate74 L2 hard block | #20-B/#20-G；`ruling_reference_gate.py:301` |
| D16-X5 | 整册写绕过意图API（write_whole_registry 型接口） | 接口负面清单（API 不存在该接口面） | `registry_ledger/api.py` §3.1 |
| D16-X6 | 册 yaml 手改偏离账本（绕开 render 单写者私改投影） | PG-wins render 回滚=伪影 | 7f0beccac4 cutover；publish_snapshot 手术2 注 |
| D16-X7 | 占号转让/复用/回收（stale 占号人工 --release；跳号永不复用） | O_EXCL 独占+释放≠可复用 | `next_ruling_id.py`；裁定#485 ①跳号台账 |

> 禁边与合法边并存自洽检查：X1 禁"同号复活"而 T9 开"新号指回"——唯一合法出路是新实例边，与图15 封卡/复活同构。

## §4 实例面与 counts 口径（裁定实例=数据行非节点）

- 实例键空间：`ruling_id`（`裁定#NNN` 或 `裁定#NNN-X` 子裁定；捕获组 `\d+(?:-[A-Z]+)?`）。与其他键空间不相交（card_id/CAND-*/TDM-*/DS-* 等）。
- counts 段全部由生成器对账本现算（`registry_entry` active 行 payload）：`entries_total`（投影面）/ `ledger_rows_active` / `ledger_rows_retired` / `by_status`（六态分布）/ `superseded_by_chains` / `snapshot_version`。**禁手画禁散文写死数字**。
- 对拍基准（2026-10-05 实测，生成器首跑应复现）：投影面 303 条（含 #486）；PG active 302 / retired 43；by_status=active 282 / decided 13 / superseded 4 / void 2 / draft 1 / deprecated 0；取代链 5；快照 v9。
- 漂移语义：账本每小时可能新增裁定 ⇒ counts 对拍**只对生成时点负责**；gate/align_all 取结构面（枚举/迁移/禁边/机构真源），counts 对拍属 CLI live 面（同图15 实例面口径——提交面一项不放宽，实例面不进硬闸）。

## §5 保险丝判活（裁定#486 ①结构下限）

有意义节点 = §1 状态 6 + §2 机械机构 9 = **15 ≥ 12** ⇒ 保险丝未触发，不停工、不写 16_fuse_alert.md、不降级注册表面板。（禁硬凑：15 节点逐条对应实查锚，无一节凑数——S4 deprecated 零实例但属四值枚举铁律成员，D16-N5/N6 在 cutover 前曾合为一步，现实测两面分立各有真源。）

## §6 边界声明（三不吞）

1. **不吞裁定正文**：图只存 ruling_id 引用与状态/机构结构，裁定内容一律指向册条目（INV-1 型；40 字滑窗校验归校验器）。
2. **不吞图10 运行时**：GOMAP 管治理进程运行面；本图管立法条目状态面。families/tags 词汇与本图零交（实查 `config/governance_operations_map.yaml` 无 ruling_id 键）。
3. **不吞门禁引擎内部**：N4/N7 只登记"门存在与优先级/通道"事实，gate 内部判据改动走各自真源文件，本图只放指针。

## §7 实查命令附录（全部只读；PATH=Python 3.12 前置）

```bash
# 状态分布（PG 账本 payload.status）
python - <<'EOF'
import sys; sys.path.insert(0,'src'); sys.path.insert(0,'.')
from zephyr.governance.registry_ledger import api as lg
from zephyr.governance.registry_ledger.registry_ledger_ddl import SCHEMA_NAME
from collections import Counter
conn = lg._open_default_conn()
with conn.cursor() as cur:
    t = lg._t('registry_entry', SCHEMA_NAME)
    cur.execute(f"SELECT payload->>'status', count(*) FROM {t} WHERE registry_id='REG-RULING-001' AND status='active' GROUP BY 1")
    print(sorted(cur.fetchall()))
conn.close()
EOF
# 投影面条目数与取代链
python -c "import yaml;d=yaml.safe_load(open('docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml',encoding='utf-8'));es=d['entries'];print(len(es),sum(1 for e in es if e.get('superseded_by')))"
# 快照版本
# （publish_snapshot 返回 snapshot_version；本包 #486 发布后 v9）
# 占号在途
python scripts/governance/next_ruling_id.py --next
```
