---
ttl: task_bound
session: st-sF-fidelity-20261004
date: 2026-10-04
title: F10 渲染保真差分班——B3 收缩根因机械复现与病灶定位（七册 render↔scan 内存往返，零写盘零提交零判定）
completes_when: 总筹采纳修复方向并派工后随 commitmap_cure 家族归档
---

# F10 渲染保真差分：B3 收缩（TRANSLATION 8761→1262 / RULING 294→41 / CAPCAN 丢383 / ARCH 丢1）根因复现

## §0 结论（一句话）

**七册 render→scan 往返"零条目文本丢失"（0 丢块），收缩全部发生在身份键层**：
B3 期身份口径=`首字段必须标量`（`registry_mass_deletion_gate.entry_identity_key` 旧义）且**按字段位置取键**，
而 PG jsonb 存储按`(键长,字节序)`规范化重排字段（`date(4)<title(5)<status(6)<…`），
`publish_snapshot` 从 `payload.items()` 重建 bundle 条目对（`baseline.py:463-469`）→
`render` 按 jsonb 序发射 → 重扫取到**另一个首字段**推导身份 → 身份键串改变+大量撞并 →
凡按身份键去重计数的消费面（`reconcile` 的 `yaml_map`、账本 UNIQUE 约束比对）即刻坍缩。
**键序敏感性病灶 HEAD 仍在**（fdfe8fe302 只治了 CAPCAN 383 的"非标量首字段→None"支），B3 若今日原样重投，TRANSLATION/RULING/ARCH 三册坍缩将复现。

## §1 方法与口径（每步可复现，全部内存运算零写盘）

链路（任务令原文口径）：

1. 快照：`pg_source.load_latest_snapshot(rid, phys)`（registry_snapshot 表最新版，只读连接）；
   历史版本用 `SELECT bundle FROM registry_ledger.registry_snapshot WHERE registry_id=%s AND snapshot_version=%s`。
2. 渲染：`renderer.render(snap)` 纯函数→内存字符串（**未调用 `run(mode="render")`，未写任何 YAML，未触碰 .runtime/projection/**）。
3. 重扫：与 `baseline._iter_scan_entries` 同口径=`_split_registry_entries(rendered)` + `entry_composite_key(blk.data)`
   （同一对函数；`_iter_scan_entries` 本体只多一步盘读，其行号为文件读取所迫，此处以内存串直喂同两函数）。
4. 差分：快照侧身份集（逐 section 逐条目对 `entry_composite_key(dict(pairs))`）vs 渲染重扫身份集：集合差+计数。
5. B3 时间经复现：身份语义取 `fdfe8fe302~1` 版（首字段必须标量，gate 真源逐字复刻进内存）；
   渲染器=HEAD（`09ca271063` 后 renderer.py 无再改，B3 时即此版）；快照=B3 两轮实发版（见 §2 表注）。

复现命令骨架（Git Bash，D:/ZephyrAlpha，Python 3.12.8）：

```bash
python - <<'EOF'
import sys, json; sys.path.insert(0,'src'); sys.path.insert(0,'.')
from zephyr.governance.registry_projection.pg_source import load_latest_snapshot
from zephyr.governance.registry_projection.renderer import render, self_check
from scripts.governance.commit_queue_landing import _split_registry_entries
from zephyr.governance.registry_ledger.ledger_identity import entry_composite_key
snap = load_latest_snapshot('REG-RULING-001','docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml')
text = render(snap)                      # 内存字符串，禁写盘
self_check(text, snap)                   # 七册全 PASS（见 §3 盲区）
fams, err = _split_registry_entries(text)
from collections import Counter; ids = Counter()
for fk, fam in fams.items():
    for blk in fam.blocks:
        ck = entry_composite_key(blk.data) if isinstance(blk.data, dict) else None
        if ck: ids[(fk or '(root)', ck)] += 1
print(len(ids), sum(c-1 for c in ids.values() if c>1))   # 41 253 —— B3 收缩复现
EOF
```

实证锚（B3 现场留档，本班只读引用）：`.runtime/registry_ledger/reconcile_20261003_194834.json`（render 第一轮后）、
`reconcile_20261003_200309.json`（第二轮后）、`publish_20261003_191825/194700/195246/200152.json`（B3 快照版次）、
`reconcile_20261003_200105/200500.json`（两次抢救后全绿）。git 锚：`09ca271063`（B3 前置渲染器治本）、`fdfe8fe302`（身份语义治本，2026-10-04）。

## §2 逐册差分表

**A 表：B3 时间经复现**（身份=B3 期旧义"首字段必须标量"；快照版=B3 第二轮实发版；与 200309 实证对列）：

| 册 (registry_id) | 快照版 | bundle 条目 | 渲染扫描 blocks | 唯一身份(复现) | 唯一身份(实证 200309) | 撞并(复现/实证) | passthrough | 丢键 | 对齐 |
|---|---|---|---|---|---|---|---|---|---|
| CAPCAN | v5 | 13086 | 13086 | 12700 | 12703 | 3/0 | **383** | **383** | ±3（注1） |
| TRANSLATION | v4 | 8761 | 8762 | 1259 | 1262 | 7498/7495 | 5（注2） | **7499** | ±3（注1） |
| DOC | v3 | 298 | 298 | 298 | 298 | 0/0 | 0 | 0 | **精确** |
| ARCH-ISSUE | v4 | 815 | 816 | 814 | 814 | 1/1 | 1（注2） | **1** | **精确** |
| ERRCODE | v3 | 800 | 800 | 800 | 800 | 0/0 | 0 | 0（但 bf=3/pgo=3，注3） | **精确** |
| CAND | v4 | 623 | 624 | 623 | 623 | 0/0 | 1（注2） | 0 | **精确** |
| RULING | v3 | 294 | 295 | 41 | 41 | 253/253 | 1（注2） | **253** | **精确** |

注1（±3 残差）：CAPCAN/TRANSLATION 复现与实证差恒为 3，归因 B3 窗口内 3 条 token 残影条目的墓碑/复活翻覆
（`09ca271063`③：v3(13086)→v4(13083)→v5(13086=同 sha 复活)；200105 reconcile bf=3 实证）——该 3 行瞬时态不在存世快照里，不可再构，残差 0.023%。
注2：passthrough 的 +1 block = 册首 `unique_key:` 声明族（header_lines verbatim 带出，纯标量族按设计不入账本，非损失）；TRANSLATION 的 5=1(unique_key)+4 条非标量首字段条目。
注3：ERRCODE 无计数损失，但 3 条 related_systems 身份键串改变 → B3 现场 bf=3（**已向账本插入 3 条重复行**）+pgo=3（原键成孤儿漂移）。

**B 表：HEAD 现状**（身份=fdfe8fe302 后新义"向后扫描取首个标量"；快照=当前最新版；同口径内存往返）：

| 册 | 快照 | bundle 条目 | 渲染扫描 blocks | 唯一身份 | 撞并 | 丢/增键 | self_check |
|---|---|---|---|---|---|---|---|
| CAPCAN | v15 | 13354 | 13354 | **13354** | 0 | 0/0 | PASS |
| TRANSLATION | v4 | 8761 | 8762 | **1266** | **7495** | 0/0 | PASS |
| DOC | v3 | 298 | 298 | 298 | 0 | 0/0 | PASS |
| ARCH-ISSUE | v4 | 815 | 816 | **814** | **1** | 0/0 | PASS |
| ERRCODE | v3 | 800 | 800 | 800 | 0 | 0/0 | PASS |
| CAND | v4 | 623 | 624 | 623 | 0 | 0/0 | PASS |
| RULING | v3 | 294 | 295 | **41** | **253** | 0/0 | PASS |

读法：新身份语义治好了 CAPCAN 的 383（aliases 开头条目身份"从无到有"）；**键序撞并（TRANSLATION 7495/RULING 253/ARCH 1）原样存活**——B3 若重投，此三册坍缩重现（外加 ERRCODE 3 键串漂移重复行风险）。

## §3 病灶机理（三条链，均有实锚）

1. **键序链（主犯，撞并 7749）**：PG jsonb 不保字段序（键长+字节序规范化）→ `publish_snapshot` 用 `payload.items()` 重建
   bundle 条目对序（`baseline.py:463-469`）→ render 照序发射 → 重扫"首字段"换人 → 身份键串变。
   RULING 全 294 条键串从 `ruling_id=裁定#N` 变 `date=YYYY-MM-DD`；而裁定批量登记（一天多条：2026-09-17 有 40 条、
   2026-09-16 有 36 条）→ 294 条只剩 41 个日期 → 撞并 253。TRANSLATION 首字段变 `desc_en`（7985 条）/`name_en`（757 条）
   → 8761 剩 1266。ARCH `title(5)<issue_id(8)` 抢占，两条预留段 title 同值 → 丢 1。
2. **非标量首字段链（CAPCAN 383）**：capabilities 条目最短键 `aliases`(7,list) 抢占首字段 → B3 期旧身份义判 None →
   passthrough。fdfe8fe302（2026-10-04）已治：向后扫描取首个标量字段（gate `entry_identity_key`，339-359 行）。
3. **重复行倍增链（放大器）**：`reconcile_registry` 的 `yaml_map[(family,entry_key)]` 按渲染后口径建键，PG 侧按导入期
   口径存键 → 两口径键串不等 → `pg_only` 全量漂移 + `backfill` 用新键串 INSERT（UNIQUE(family,entry_key) 不拦，键不同），
   B3 现场两轮各注入 1261+41+814+5/1262+… 条**重复内容行**（200105/200500 全绿证明已被总筹清理，PG 现存行数已核=正常）。

**守卫盲区实证**：`renderer.self_check`（safe_load 语义等值断言）七册全 PASS——字典比较天然序不敏感，测不出身份口径漂移；
identity 计数坍缩与语义等值**同时成立**，这就是 B3 前自检未拦截的原因。

## §4 病因分类计数与判据（丢键口径=B3 第二轮实证损失）

| 病因 | 判据（机械可验） | 计数 | 明细 |
|---|---|---|---|
| 键序（jsonb 重排抢占首字段→撞并） | jsonb 首键名 ≠ 原序首键名，且新首键值在册内重复 | **7749** | TRANSLATION 7495 + RULING 253 + ARCH 1 |
| 嵌套形态（首字段非标量→身份 None） | bundle 首对值类型 ∉ {str,int,float,bool} | **387** | CAPCAN 383（aliases list）+ TRANSLATION 4 |
| 键序-键串漂移（不丢数，造 pg_only/backfill 重复行） | jsonb 首键名 ≠ 原序首键名，新键值册内唯一 | **8** | ERRCODE 3（related_systems）+ CAPCAN 5（name/domain 抢占） |
| 标量归一 | 键名不变而键值串变（类型强制/引号态） | **0** | 机械验证：七册 25445 行中"键名同、串变"=0 |
| 多行折叠 | 值含 \n 折叠为单行引号串后身份变 | **0** | 折叠存在（summary 折为单行）但值无损，无一丢键归因于折叠 |
| 段序 | 身份键的 family 维度因节段重排而变 | **0** | sections 按族名字节序重排，键含 family 维度，0 换族 |
| 其他 | 以上之外的形态 | **0** | 丢键集合被前两类完全穷尽（同口径往返 0 丢 0 增验证） |

## §5 样本对照（原盘面 vs 渲染，各≈10 行；渲染件=in-memory，未落盘）

**S1 RULING 键序撞并（294→41 病灶；date 抢占首字段）**

```yaml
# 原盘面（ruling_registry.yaml，ruling_id 首字段=身份键 'ruling_id=裁定#20'）
- ruling_id: '裁定#20'
  title: 裁定登记机制治本批次根条目
  date: '2026-07-18'
  category: 治本
  status: active
  summary: >-
    裁定#NNN 登记机制治本批次的根条目，包含子裁定 #20-A（建立 ruling_registry.yaml
    ...
# 渲染后（v3 快照内存串；jsonb 序 date(4)<title(5)<status(6)<summary(7)<category(8)<ruling_id(9)）
- date: "2026-07-18"
  title: 历史裁定补登（裁定#218 即原日期式编号裁定）
  status: active
  summary: "历史裁定补登治本。病根：代码中以日期式编号……（多行折叠为单行引号串）"
  category: 治本
  ruling_id: 裁定#20-F
  related_arch: []
  superseded_by: null
  affected_files:
  - d:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ruling_registry.yaml
```

同日姊妹条目：`2026-07-18` 共 9 条（#19-A/#19-B/#20/#20-A/#20-B/#20-D/#20-E/#20-F/#20-G）渲染后**首字段同为
`date: "2026-07-18"`** → 九条身份键同串 `date=2026-07-18` → 去重坍缩为 1。极值：2026-09-17 一天 40 条裁定同键。

**S2 CAPCAN 非标量首字段（丢 383 病灶；aliases 抢占）**

```yaml
# 原盘面（capabilities 族，aliases 本就是首字段）
- aliases:
  - 挖矿SOP
  - web_mining
  - research_mining
  - 全网调研
  description: 挖矿 SOP——全网调研+内部反查的全面挖掘方法论。触发=建策略/建方案/建文档……
  capability_id: mining_sop
  canonical_override: docs/01_policies_and_standards/sop/mining_sop/mining_sop_policy.md
# 渲染后（v5 快照内存串，形态逐字同——aliases(7) 仍是最短键居首）
- aliases:
  - 挖矿SOP
  - web_mining
  - research_mining
  - 全网调研
  description: 挖矿 SOP——全网调研+内部反查的全面挖掘方法论。触发=建策略/建方案/建文档……
  capability_id: mining_sop
  canonical_override: docs/01_policies_and_standards/sop/mining_sop/mining_sop_policy.md
```

文本零丢失（blocks=13086 全在），但 B3 期身份义"首字段必须标量"遇 list 首字段判 None → passthrough →
yaml_map 缺 383。HEAD 新义（向后扫描）已治——身份取 `description=…`，S2 类条目全部存活（B 表 v15 撞并 0）。

**S3 ARCH title 撞名（815→814 病灶）**

```yaml
# 原盘面：两条独立条目，身份键 issue_id 各异
- issue_id: '#ARCH-001'          - issue_id: '#ARCH-003'
  title: 编号预留段（未使用）      title: 编号预留段（未使用）
  severity: P3低                  severity: P3低
  adjudication: '永久保留为…'      adjudication: '永久保留为…'
  fix_phase: 无需施工（永久预留）  fix_phase: 无需施工（永久预留）
  status: deprecated              status: deprecated
# 渲染后：title(5)<issue_id(8) 抢占 → 两条首字段同值
- title: 编号预留段（未使用）      - title: 编号预留段（未使用）
  status: deprecated              status: deprecated
  created: "2026-06-26"           created: "2026-06-26"
  issue_id: "#ARCH-001"           issue_id: "#ARCH-003"
```

**S4 ERRCODE 键串漂移（bf=3/pgo=3：不丢数但造重复行）**

```yaml
# 原盘面（related_systems 族，身份键 'system=MCP 协议错误码'）
- system: MCP 协议错误码
  format: int（JSON-RPC 标准码 -32700~-32005）
  canonical_file: src/zephyr/infrastructure/error_codes.py
  description: MCP 协议层错误码，与业务 error_code 职责分离
# 渲染后：format(6) 与 system(6) 同长、字节序 f<s → format 抢占
- format: int（JSON-RPC 标准码 -32700~-32005）
  system: MCP 协议错误码
  description: MCP 协议层错误码，与业务 error_code 职责分离
  canonical_file: src/zephyr/infrastructure/error_codes.py
```

身份键变 `format=…`：计数不丢（3 条 format 值互异），但与 PG 存键不等 → B3 现场 backfill 3 条重复行 + 3 条 pg_only。

**免疫对照（DOC/CAND 为何全绿）**：DOC 主族首字段 `file`(4)、CAND 主族 `id`(2)——原序首字段恰好就是 jsonb 最短键，
两种口径取到同一字段 → 键串零漂移（机械验证 298/298、623/623 全等）。免疫是**偶然的字段命名巧合，不是设计保证**。

## §6 修复建议（只列不动手，排序=本班建议优先级）

1. **身份键与字段顺序解耦（治本向）**：`entry_composite_key` 改用各册 `unique_key` 族声明字段（RULING=ruling_id、
   TRANSLATION=module_path、ARCH=issue_id、CAND=id，册内已在声明）而非位置首字段；`registry_catalog.unique_key_fields`
   现种子收 None（`_seed_catalog` 只读 header 标量，声明在族里收不到）——需让 seed 解析 unique_key 族或 publish 侧落显式键。
   前置：先按裁定口径统一"身份键定义真源"（gate/账本/合并器三方同改，红蓝等值断言防分叉）。
2. **bundle 保全序（次选）**：`publish_snapshot` 重建条目对时不用 `payload.items()`，改在导入/意图 API 侧记录字段原序
   （如 payload 附 `__field_order__` 或 registry_entry 增序化列），render 按原序发射——保"渲染=盘面形"语义。
3. **渲染锚定身份（轻量向）**：render 对每条目将册声明身份字段置于首字段（canonicalize 的推广），扫描口径不动。
4. **补 self_check 盲区**：渲染守卫加"身份键往返不变"断言（render→重扫 composite 集 == bundle composite 集），
   现有 safe_load 等值断言序不敏感，测不出本病灶（§3 盲区实证）。
5. **reconcile 口径自检**：对账写路径（backfill）前抽样验证"yaml 键串 ⇄ pg 键串双向可推导"，拦住 B3 式重复行注入
   （B3 现场两轮共注入约 2100+ 条重复行，均靠人工清理回收）。

## §7 边界声明

- 本班纯只读：渲染全部内存串；未调 `run(mode=render)`；未写任何 YAML/.runtime/projection；零提交零裁定；仅本件为产出（claim→写→release 留痕）。
- 快照侧身份集口径=bundle 条目对 `dict(pairs)` 保序复合键；盘面侧证据引用自 B3 现场留档 json（未重放写路径）。
- ±3 残差（§2 注1）为不可再构瞬时态，已在案；TRANSLATION「8761→1262」与复现「8761→1259+3」同一事实两种计时点。
- 修复建议未经裁定，均不动手。判定权归总筹。
