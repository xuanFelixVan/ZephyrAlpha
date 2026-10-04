---
status: active
title: "任务F·挂载义务门禁详版规格 v1（st-tdm-mountgate-20261005 总筹详版）"
module_id: ""
blueprint_id: ""
version: "1.0.0"
created: "2026-10-05"
updated: "2026-10-05"
ttl: task_bound
owner: st-tdm-mountgate-20261005
upstream: "工单占位件 st-tdm-mountgate-20261005；TDM v1.3 立项 0e94229a1b1；layering_policy v1.3"
---

# 任务F·挂载义务门禁详版规格 v1

> 工单占位件明令「开工前总筹出详版规格，勿凭占位件直接施工」——本件即该详版规格。
> 施工面当前**闸死**（前置未满足，见 §2），本件落地后工单处于「规格就绪待前置」态。

## 0. 定位与净零

- **一句话**：把「新模块必有挂载裁决」从君子协定升级为提交时技术强制；同时兑现 TDM v1.3 立项（0e94229a1b1）已批的「蓝图锚↔地图节点引用一致性校验」。
- **净零申报**：与上述已立项项**合流扩展**（一 gate 两职责），非新建第二真源、非第二挂载裁决通道；裁决真源仍=layering_policy v1.3 的三字段纪律（module_mounts 机生禁手改）+ 总筹裁决册增量维护。
- 病根对齐 TRANSLATION-COVERAGE 先例：100% AI 开发下，事后普查治理永远滞后于缺口制造（B 账本实证 233 缺口即一次性的代价）。

## 1. 数据模型（四源一helper）

| 源 | 角色 | 真源位置 | 性质 |
|---|---|---|---|
| 挂载面 | ①已挂判据 | `config/*.yaml` 全景图族：节点 `module_id` + `module_mounts`（工单A 落地后生效） | 规则数据 YAML，只读 |
| 豁免册 | ②豁免判据 | `config/tdm_mount_exemption_registry.yaml`（新建，registry_id=TDM-MOUNT-EXEMPT-001） | 规则数据 YAML |
| 人口面 | 义务域判定 | 23 交易域目录常量（与 `scripts/generate_map_coverage_ledger.py` DOMAIN_DIRS 同源 import） | 代码常量 |
| 蓝图锚 | 一致性判据 | blueprint.md frontmatter `module_id` + .py 头 `[BLUEPRINT]` 行 + depgraph nodes | 架构数据 DB+文件 |

- **共享 helper（单计算双消费，防 gate/生成器漂移）**：`scripts/governance/_shared/mount_obligation.py`
  纯函数集：`build_mounted_set(maps) -> set[str]`（全 config 图 module_id∪module_mounts 并集）、
  `load_exemptions(registry_path) -> dict[mod, entry]`、`extract_blueprint_anchor(text) -> str`、
  `has_not_trading_marker(text) -> str|None`（正则 `\[not-trading:[^\]]+\]`，理由非空）、
  `resolve_module_id(file_path) -> str|None`（depgraph nodes 按 file_path 反查）。
  gate 与 manifest 生成器**都只调它**，禁止两处各写一遍集合逻辑（翻译册 loader 同款先例）。
- **B 账本/e 裁决册（docs/_working/tdm_mount/，ttl=task_bound）只作**工单A 写豁免册的**数据来源**，
  永久 gate/reconciler **禁引临时区**（宪法 §9.4）——豁免真源落地后与临时册脱钩。

## 2. 前置闸（不满足勿开工——当前实测未满足）

```powershell
# 前置1：工单A 落 HEAD（module_mounts 在图）——期望 >=180 行命中
git grep -c "module_mounts" HEAD -- config/trading_decision_map.yaml
# 前置2：B 账本复跑 orphan=55（=e 裁决册 counts.exempt，机生对拍禁手工）
python scripts/generate_map_coverage_ledger.py --check   # 或重跑后核对 unmounted_orphan
```

**2026-10-05 实测**：HEAD=02d4baaf13（policy v1.3 批），TDM 图 module_mounts 零命中；
flash 分支（a80cce5da8，已并入 dev）亦无；B 账本 orphan=233。**两前置均未满足，施工闸死。**
工单A（apply 批）落地后重跑上两命令，双绿即解锁 §8 开工序列。

- 豁免册首拍数据源=e_mount_verdicts_v1.yaml `exempt` 段（55 台，域归属四分布：图9×46/图13×5/GOMAP×3/图11×1）。
- **开放项①（工单A 对拍）**：e .md apply 批规格段写「exempt 61+4 台」，与 e yaml `counts.exempt: 55` 不一致——
  以 yaml 机读为准（55），工单A 落地时机械对拍，差数逐台列名解释。

## 3. Gate 规格（TDM-MOUNT-COVERAGE）

- 文件：`src/zephyr/gov_enforcement/commit_gates/tdm_mount_coverage_gate.py`；
  `make_tdm_mount_coverage_gate() -> GateSpec(gate_id="TDM-MOUNT-COVERAGE", priority=61)`
  （58 depgraph→59 翻译→60 CREATE-GUARD→**61 本 gate**：先确认节点存在，再问挂载裁决）。
- **own-diff 触发集**：`git diff --cached --name-only --diff-filter=A` 命中
  ① 新增 `blueprint.md`（docs/03_modules/**）② 新增 .py（src/zephyr/+scripts/，
  豁免面同 TRANSLATION-COVERAGE `_is_in_scope`：is_test_exempt/demos/test_*前缀/__init__/_archive）。
- own 化：`_split_own_foreign` 同款——外来 staged 命中 warn+审计不阻断（宪法 §3.1）。
- **裁决流（对每个新 .py 模块）**：
  1. `resolve_module_id`（depgraph 反查；58 号 gate 已保证新模块必已登记，查不到=前 gate 失守，fail-open warn）
  2. ①已挂：module_id ∈ build_mounted_set（**读本提交 staged 版图**：commit 内含挂载变更时以暂存区为准，
     防「图+模块同批」被 HEAD 口径误杀——静窗学费「预检读暂存区非工作树」直接适用）
  3. ②豁免：module_id ∈ 豁免册（staged 版同理）
  4. ③标记：本提交新增的 blueprint.md frontmatter/body 或该 .py 头部注释含 `[not-trading:<非空理由>]`
  5. 三选一未命中 → **阻断**，处方文案见 §5
- **撞号拦**：module_id 在 depgraph nodes / 翻译册已注册到**不同 file_path** → 阻断
  （e 裁决册 no2 撞号两对实证：SIG-087/088 双注册；处方=按 no2 案例改号，真空位经 depgraph 逐号核验）
- **蓝图锚一致性（合流职责，对每个新增 blueprint.md）**：
  a. frontmatter `module_id` 与该 commit 内对应 .py `[BLUEPRINT]` 行 module_id 一致（不一致=拦）
  b. 本提交地图 diff 中新增的 module_mounts 引用，其 module_id 必须存在蓝图锚（防幽灵挂载=拦）
  c. 撞号判据 b 覆盖：同 module_id 双 blueprint=拦
- **ERROR_CONTRACT**：check 永不抛异常；git/真源/IO 异常降级 fail-open（passed=True+logger.warning）；
  检出违规 fail-closed 硬阻断（无观察期——豁免册首拍随工单A 同步落地，上线即有全量底册，
  bootstrap 只拦新增文件，存量零误拦面）。
- **前置自锁**：豁免册文件不存在时 gate skip 并留言「前置未落（工单A）」——前置闸在运行时面自证。

## 4. Exemption 册规格（config/tdm_mount_exemption_registry.yaml）

- 条目契约：`module_id` / `target_map`（域归属：图9 策略工厂|图13 交易日循环|GOMAP|图11 交付流水线|…）/
  `conclusion_zh`（大白话结论）/ `basis`（e 裁决册 no1 款|裁定号|Owner 指令号）/ `review_when`（复查条件）。
- 首拍=工单A 从 e 裁决册 exempt 段机械写入（55 台=e yaml 逐模块 `action: exempt` 行，字段映射
  module_id→module_id / target→target_map / criterion+note→conclusion_zh / basis=`e_mount_verdicts_v1 no1`）；
  后续增删走总筹裁决册增量（policy v1.3 维护口径），带依据。
- 与 `config/coverage_exemption_registry.yaml`（COVERAGE-EXEMPTION-001，**file 级**普查豁免，他会话在途收编中）
  **对象不同（module vs file）、消费方不同，不并不可混写**；命名前缀 tdm_mount_ 防撞。

## 5. 处方文案（阻断消息，三选一给活路）

```text
TDM-MOUNT-COVERAGE: 新模块 <file_path>（<module_id>）无挂载裁决。三选一修复后重提：
① 挂图：在总筹裁决册增量登记 mount 行（判据=policy v1.3 挂图 SOP 四判据）→ apply 写 module_mounts → 重跑 manifest；
② 豁免：config/tdm_mount_exemption_registry.yaml 增条（域归属+conclusion_zh+basis+review_when，缺依据不收）；
③ 标记：blueprint.md frontmatter 或模块头注释加 [not-trading:<大白话理由>]（非交易域设施专用）。
撞号时另见：module_id 已被 <other_path> 持有——按 e 裁决册 no2 案例取真空位新号。
```

## 6. Manifest 生成器规格（机生，静态清单禁手工维护铁律）

- 文件：`scripts/generate_mount_obligation_manifest.py`；产物=`docs/_working/tdm_mount/G_mount_obligation_manifest.{md,yaml}`
  （campaign 机生产物，与 B 账本同目录同待遇；gate 不读它——gate 读 §1 四源活算，manifest 是人读投影+对账面，防「缓存漂移杀 gate」）。
- 逻辑：人口（23 域 blueprint module_id 全集）× mounted（shared helper）× exempt（豁免册）× marker →
  三分类（obliged_mounted / obliged_exempt / obliged_marked）+ **red 段=无裁决人口**（应恒空，非空=reconciler 判红）；
  计数一律字段禁散文；`--check` 零写盘；确定性（--anchor 传锚，禁 datetime.now——M46）；safe_write_text 原子写。
- 触发：reconciler 事件重扫后自动重生 + 总筹对审时手动。

## 7. Reconciler 规格（事件触发，禁 cron——宪法四要素）

- 文件：`src/zephyr/governance/audit/tdm_mount_coverage_reconciler.py`；
  `make_tdm_mount_coverage_reconciler(gateway)`，priority=952（挨翻译册 951 之后，同 late-stage warn-only 全扫族）。
- **trigger**（ReconcilerSpec.trigger 签名 `(committed_files) -> bool`）：命中任一
  config 图族 / 豁免册 / docs/03_modules/**/blueprint.md / src|scripts 新 .py / 翻译册 / depgraph 登记面 → True。
- reconcile：shared helper 全量重扫（人口 vs mounted∪exempt∪marker）→ 孤儿判红 →
  落盘 `.runtime/tdm_mount/orphan_report.json`（warn-only 不阻断）→ 调 manifest 生成器重申投影。
- 头注 `# noqa: m10-time-trigger`（commit 事件触发豁免，翻译册 reconciler 同款）；
  永不抛异常；DB/YAML 不可达降级 ReconcileResult(action="warn")；注册接线=git_commit_gateway.py
  翻译册 reconciler 注册行（≈L1860）相邻。

## 8. 注册与名册

1. `in_process_gate_registry.yaml` 增条（gate_id/module_path/factory_function/source=in_process/enabled=true）；
2. `python scripts/governance/d3_metadata/generate_gate_registry.py` 重宣统一册 +
   `reconcile_gate_rosters.py` 三方对账（模块面/in_process/统一册一致+own_scope 值确认=own）；
3. 新 .py 走 `scripts/governance/register_asset.py` 五道手续合一（token/大白话/depgraph/依赖图/头校验）；
4. risk_tier：governance 域新增检查器=medium/low 全自动，非 §5 high 门位（无注册表净删/无 flag 翻转）。

## 9. 测试规格（红蓝各≥3，全 mock 真源，tmp_path 隔离）

`tests/governance/commit_gates/test_tdm_mount_coverage_gate.py`：

| # | 型 | 场景 | 期望 |
|---|---|---|---|
| 1 | 红 | 新 .py 无任何裁决（图豁免标记三无） | 拦，消息含处方三选一 |
| 2 | 红 | 撞号：module_id 已注册到他路径 | 拦，消息含撞号对象 |
| 3 | 红 | 蓝图锚不一致：frontmatter module_id ≠ .py [BLUEPRINT] 行 | 拦 |
| 4 | 红 | 图 diff 幽灵挂载：module_mounts 引用无锚 module_id | 拦 |
| 5 | 蓝 | module_id ∈ 图 module_mounts（staged 同批口径） | 放 |
| 6 | 蓝 | module_id ∈ 豁免册 | 放 |
| 7 | 蓝 | blueprint 含 `[not-trading:<理由>]` | 放 |
| 8 | 蓝 | 豁免册不存在（前置未落）→ skip 非拦 | 放 |
| 9 | 蓝 | 外来 staged 新模块（他 session） | warn 放行+审计 |

`tests/governance/audit/test_tdm_mount_coverage_reconciler.py`：trigger 命中矩阵/孤儿判红落盘/真源不可达 warn 降级，≥3 例。
外加 shared helper 单测（mounted 集合并集口径/marker 正则理由非空）。

## 10. 开工序列（前置双绿后执行）

1. `session_worktree_start`（施工默认隔离）+ 本卡 READY→IN_PROGRESS；
2. capability_lookup.find("挂载 门禁") 留审计 + apply_depgraph --add-design-node 先登记后施工（RULE-DEPGRAPH）；
3. 施工顺序：shared helper → exemption 册首拍对拍（工单A 产物核对）→ gate → reconciler → manifest 生成器 → 名册登记 → 测试；
4. 红蓝全绿+ruff clean → git_commit.py 分批落地（helper+册 / gate+reconciler / 生成器+名册 / tests，或按窗口合并）；
5. 收尾：card_review_automation 两轮 → verify → 交接汇报。

## 11. 验收清单（Gate for gate）

- [ ] 红蓝测试全绿且各≥3；ruff clean
- [ ] 三方门禁名册对账一致；own_scope=own 生效
- [ ] 盘面实测：现存 staged 面零误拦（bootstrap 只拦新增）；豁免 55 台全部放行
- [ ] 前置自锁：删豁免册→gate skip 非拦
- [ ] manifest --check 幂等；reconciler 事件触发实测（造一次模块册 commit 看落盘）
- [ ] align_all / 普查面零回退

## 12. 边界与不做什么

- 不碰 config 图本体挂载写面（归工单A）；不碰 e/B 册（chief 资产，只读输入）；
- 不与 COVERAGE-EXEMPTION-001（file 级）合并；不做 TDM 之外地图的人口面扩展（23 域口径不动，
  其他图未来接同款 gate 属新工单）；无 Owner 门位事项（净零已由工单申报+本规格固化）。
