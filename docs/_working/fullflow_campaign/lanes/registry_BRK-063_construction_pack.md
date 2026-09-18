---
ttl: task_bound
completes_when: PAN-ASSET-01..04 与 PAN-RISK-01 五项高优先全景图建成并被 panorama_registry 索引收录
---

# 施工包 · BRK-063 五项高优先级全景图未建（交 Max 直接开工，无需重新勘察）

> 车道 `st-ff-registry-20260918`。属**新建类**（一夜建不完）→ 只出施工包，不硬建。
> 本包所有 file:line 为 2026-09-18 实测。

## 1. 现状（精确落点）

| 对象 | 真源位置 | 实测事实 |
|---|---|---|
| 待建清单本体 | `scripts/governance/d5_architecture/generators/generate_panorama_registry.py` §`PENDING_PANORAMAS` 常量 | 16 项，注释明文"真源=硬编码常量（用户裁定不建 panorama_registry.yaml）"；每项带 `plan_folder` / `plan_generator` / `data_source_tbd` / `related_blueprints` |
| 5 项高优先 | 同上常量内 `PAN-ASSET-01..04` + `PAN-RISK-01` | PAN-ASSET-01 资产CMDB / 02 API契约目录 / 03 数据目录 / 04 数据血缘 / PAN-RISK-01 风险敞口 |
| 索引产物 | `docs/02_enterprise_architecture/00_overview_entry/panorama_registry.md` | **实测该路径被 `.gitignore:546 docs/02_enterprise_architecture/00_overview_entry/*.md` 排除** → 产物不入库，只由 reconciler 现生；施工时勿 commit 该 .md |
| 触发机制 | 同生成器头注释 `[CONSUMERS] CI自动触发(GATE-ARCH-DIAGRAM reconciler post-commit)` | 建完图后须把条目从 `PENDING_PANORAMAS` 移入 `BUILT_PANORAMAS`（含 `generator`/`output_path`/`artifact_path`），否则索引仍报"待建" |

## 2. 缺哪几件（按依赖顺序）

1. **表先于图**：`depgraph.interface_contracts` 实测仅 **5 行**（全项目 3477 个可导入模块）、
   `dataflow_datasets` 76 行中 production=0、`dataflow_runs` **0 行**、
   `dataflow_datasets_metadata` / `dataflow_jobs_metadata` **0 行**（普查 BRK-059/060 已立）。
   → PAN-ASSET-02（API 契约目录）与 PAN-ASSET-03/04（数据目录/血缘）**没有可画的底**：
   先把这四张表的元数据填上（`sync_yaml_to_depgraph.py` / `apply_dataflowgraph.py` 通道），再画。
2. **PAN-ASSET-01 资产 CMDB**：`data/asset_index/unified-asset-index.yaml`（ROOR REG-INVF-001 在册，
   status=draft）已是"六大目录文件资产 + 四维分类"的现成底，缺的是**生成器**（把该 YAML + 24 个对账注册表
   汇成 CMDB 视图）。可复用件：`docs/01_policies_and_standards/_registry/catalogs/registry-master-index.yaml`
   的生成器 `scripts/governance/generators/generate_registry_master_index.py`（同形态，抄其幂等/落盘写法）。
3. **PAN-RISK-01 风险敞口**：底料已存在且比想象的多 ——
   `docs/01_policies_and_standards/_registry/catalogs/risk_limit_registry.yaml`（9 类限额，ROOR 在册）
   + `config/flags.yaml` 风险位 + `risk_tier_registry.yaml`（域→tier→human_gate）。
   缺的是**聚合视图**（按域展开敞口/限额占用）。注意 `risk/` 属 D_RISK 高门位域：只读聚合，禁改风控码。
4. **目录先建**：`08_asset_panorama/`、`11_risk_panorama/` 两目录尚不存在（生成器"目录规划"段标 ⏳）。
   建目录 = 触发 DIRECTORY-CONTRACT 检查，命名禁数字后缀之外的变体。
5. **FDR 侧挂接**：新图若引入新域，须同批补 `functional_domain_registry.yaml`（本车道刚把 11 个 depgraph
   域补登，FDR 现 94 条）+ ROOR 登记，否则 BM-INV-008/新域检查会红。

## 3. 每件改法（统一配方）

- 生成器落 `scripts/governance/d5_architecture/generators/generate_<name>_panorama.py`
  （**禁落 `scripts/governance/` 根**，ARCH-031）。
- 新 .py 三件套（缺一即队列死信，R-017②：token 必须同批进 `--files`）：
  `apply_depgraph.py --add-design-node <path> <MOD-ID> <D_域> --granularity file`
  → `batch_creation_tokens.py --prefix <完整文件路径> --created-by <sid> --capability <cap>`（单值 argparse，逐文件）
  → `add_module_translation.py --path <f> --domain <D_*> --name-zh <中> --plain-zh <大白话≥8字>`（**主仓跑**）。
- 只读 depgraph 用 `get_depgraph_pg_connection(superuser=True, read_only=True)`；
  SQL 提为模块级 `SQL_*` 常量；表名若属已注册品类走 `get_registry().table()`；`c1_market` 全系查询带 `FINAL`。
- 输出幂等（相同输入→相同输出）：产物里禁写时间戳到判定字段，`generated_at` 只放 frontmatter
  （参考 `generate_battle_map_diagram.py::_make_frontmatter` 与 `align_battle_map.py` 同法）。
- 建完后：`PENDING_PANORAMAS` → `BUILT_PANORAMAS` 移条目 + 跑 `generate_panorama_registry.py` 重生索引。

## 4. 验收判据（六向台账口径，见 FLOWTHROUGH_ACCEPTANCE_SPEC §1）

每项全景图必须逐向给实测证据，任一空 = 判红，禁以"图已画"上报：

| 向 | 本簇判据 |
|---|---|
| ①入口有料 | 给出底表/底册实测行数（如 `interface_contracts` 行数从 5 → N，命令+输出） |
| ②转化能跑 | 生成器真跑一次：`python .../generate_*.py` rc=0 + 耗时（不是 import 成功） |
| ③出口有货 | 产物落盘字节数/节点数实测 + 读盘回解析逐位对比（禁只报内存值） |
| ④下游能取 | **至少一个 src/ 内真实读者**或索引收录证据（`panorama_registry.md` 现役表出现该 ID）；`scripts/` 里的 import 不算引用 |
| ⑤哨兵在岗 | 新表/新册若有数据面，须在 `data_supply_sentinel.yaml` 有阈值行且实跑 breach=0 |
| ⑥失败会响 | 故意把底表指空 → 生成器必须**非零退出或显式 fail-closed**，禁静默产出空图冒充"已建"（本车道在 family_registry 生成器里已钉此判据：真源缺失 → `FileNotFoundError` → exit 1） |

**灌水试验能红**（§3.4）：断掉任一底表 → 图必须报红并指出断在哪一跳；探针按字节还原。

## 5. 风险与回滚

- 风险 A：`dataflow_*` 元数据补填涉及 `sync_yaml_to_depgraph.py`（P2/#161 通道），改错会牵动第三全景图全量重生 →
  先 `--dry-run`/只读探一行，再批量。
- 风险 B：PAN-RISK-01 触 D_RISK（high 门位域）——**只读聚合可自动，任何限额数值改动 = Owner 门位**。
- 风险 C：产物 .md 被 .gitignore 排除（实测 `00_overview_entry/*.md`、`07_.../battle_map/*.md` 同规则）→
  提交清单里若出现这些路径会被忽略，别误判"没写进去"；要交付的是**生成器与真源 YAML**，产物由 reconciler 现生。
- 回滚：每项独立成批，revert 对应 commit 即回到"待建"状态（`PENDING_PANORAMAS` 未移条目前，索引零变化）。
