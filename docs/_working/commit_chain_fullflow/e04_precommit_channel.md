---
created: 2026-09-30
ttl: task_bound
title: 提交链路全流通作战·E4 pre-commit hook 通道
session: st-gate-rationalize-20260929
---

# E4 pre-commit hook 通道挖矿册

> 环节定义：`_resolve_commit_result` step 5.5 在 `git commit --no-verify` 之前对 staged 面
> 跑 `python -m pre_commit run --files <own>` 的网关内通道（裁定#341 方案②），含 own-scope
> 临时索引、Phase-A/B 两段式、SKIP 清单、失败归因与遥测。裸 `git commit` 直连面（.git/hooks
> 安装路径）不在本册——其恒被 gate-commit-gw 封死（.pre-commit-config.yaml，裁定册 §5.2）。
> 逐台 hook 裁定真源=`docs/_working/gate_survival_adjudication.md` §5；冲突处按裁定册并注明。

## §0 自审闸三态

**【挖干】**（六向齐、逐件有锚；两处种子漂移如实声明见下）。

- 声明①：通道各锚点行号相对种子**全部漂移**（_run_precommit_channel :3439→:3503；SKIP :464→:470；
  Phase-A/B :3597-3635→:3635-3664；own-scope 索引 :3341-3358→:3398-3415+:3628；慢尾 :388-410→:394-417）——本册一律以 HEAD 实测行号为准；
- 声明②：耗时账两套口径并存——裁定册窗口（9/24 起 141 次：p50 44.3s/p90 157s/快段占 87%）与本册复测
  （187 行、9/24→9/29：p50 49.0s/p90 143.2s/max 1783.8s/快段占 sum 80.5%）；文件仍在增长，
  以裁定册数字为战役基线、复测为现值（自测命令见 §2 遥测行）。

## §1 组件全清单（14 件）

| # | 组件 | 实态（file:line） |
|---|------|------------------|
| 1 | .pre-commit-config.yaml | **64 hook**（yaml.safe_load 实数）=pre-commit 53 + manual 7（gate-arch/gate-naming-audit/gate-frontmatter-audit/gate-bp-place/gate-dedup/sync-audit-protocol-numbers/handoff-log-generate）+ post-commit 3 + commit-msg 1；全 `repo: local` 4 块（:53/:171/:1043/:1056）；`default_install_hook_types: [pre-commit, post-commit, commit-msg]`（:51）；id 全唯一 |
| 2 | 9/30 退役 5 台（种子已验） | 墓碑注释在案：gate-14-authority-registry(:288 死正则零执行)/gate-13-blueprint-overlap(:292 死目录)/gate-22-load-path-integrity(:710 warn 骨架自认 SKIP)/gate-node-label-quality(:887 触发面仅 1 tracked 文件)/gate-drift-light-scan(:924 entry 模块路径坏死，**manual 段**)；执行 commit=03ce599b85（2026-09-30 00:42 +0800，④pre-commit config 五处）；gate-vms-ssot 收缩 integration 单分支（:460-462，governance 分支 2026-06-28 已删）。统一册同步重生成 183→178 条 |
| 3 | Rx-3 确定性快检 fail_fast×4 | check-merge-conflict-marker(:70)/detect-private-key-local(:78)/ruff(:162)/ruff-format(:169) 配 per-hook `fail_fast: true`——红了=必然 own 违规先败即停（commit 60d7bdda65①；慢尾 20 台不配保 own/foreign 归因） |
| 4 | 通道执行入口 `_run_precommit_channel` | git_commit_gateway.py:3503（docstring :3504-3539 载背景/own-scope 机制/归因规则/SKIP 理由）；flag 门 `_precommit_run_enabled`(:477-493，读 `gate_precommit_run`，设施异常回退 OFF)；merge 跳过(:3542-3543) |
| 5 | step 5.5 接线（全局锁内） | `_resolve_commit_result` :3819-3822——staged 校验段（step5）后、`git commit --no-verify`（step6）前；**位于 `_commit_locked` 全局锁内**（TRAE-079 防拆分设计；裁定册 §5.1.1"通道出锁"仍未落=在案结构债）。A1 装表注释自认"本通道常是全链最贵一段（实测单件 ≥6 分钟）"（:3823-3824） |
| 6 | own-scope 临时索引 | env `GIT_INDEX_FILE` 临时索引（:3554-3562，tempfile 于 git-dir）；`_precommit_run_scoped`(:3605-3670)：rev-parse HEAD(:3624)→`read-tree HEAD`(:3628)→`_precommit_build_temp_index`(:3398-3415：`add -f` 分批 200(:3405-3409)+`rm --cached` 删除目标(:3410-3414))→分块 chunks=200(:3634)→跑完 os.remove(:3666-3669)；语义=索引扫描型 hook 只见本提交面，pass_filenames 型由 `--files <own>` 限定（docstring :3511-3516） |
| 7 | Phase-A 快败子集 | `_precommit_fast_subset`(:3672-3710)：单次调用全通道减慢尾（SKIP 反选 :3686），**首败短路**(:3704-3705)；开关 `_precommit_fast_subset_enabled`(:420-428，env ZEPHYR_PRECOMMIT_FAST_SUBSET=0 停用；pytest 环自动 OFF 保集成套件时长)；主流程 :3635-3653 |
| 8 | Phase-B 收窄（Rx-4） | :3654-3664——Phase-A 已绿⇒`_precommit_config_hook_ids`(:436-455，解析 config 全 id，解析失败回全量)减慢尾反选为 extra_skip，Phase-B 只跑慢尾；归因面合并 fa_output+Phase-B 输出(:3663-3664)；回退手柄 `ZEPHYR_PRECOMMIT_PHASEB_FULL=1`(:431-433)。绿路径台次 91→54（commit 60d7bdda65②）；**两段式绿件双付快段调用仍在**（裁定册 §5.1.2，单趟化未落） |
| 9 | 慢尾清单 `_PRECOMMIT_SLOW_TAIL_HOOKS` | :394-417 共 20 台（triple-align/schema-truth/zr-zero-residue/ssot-code/gate-test/test-symbol-validity/errcode-consistency/21-manifest-drift/vocab/16-arch/12-blueprint-provenance/13-blueprint-overlap/14-authority-registry/mcp-contract/c2/codegen-idempotent/adm-manifest/script-q/nested-flat-prefix/rules-integrity）；ruff-format 已移出（:415-416）。**含 2 个已退役死 id（gate-13/gate-14，:406-407）**——SKIP 不存在的 id 无害（:389-390）但属清单漂移债（§3） |
| 10 | 通道 SKIP 清单 `_PRECOMMIT_CHANNEL_SKIP_HOOKS` | :470-473 共 **8 台**：原 3=gate-commit-gw（判定前提"hook 运行=裸 commit"恒真冲突）/gate-worktree-required（与网关内进程 gate 双重计数）/gate-protected-paths（消息盲 hook 杀已审批写入，四死信实证 :458-463）；+5 同脚本 twin（2026-09-30 Owner 批，:464-469）=gate-id-uniq/gate-frontmatter/gate-encoding-safety/gate-directory-contract/gate-doc-node-id（L1=subprocess 调同一 checker 的 thin wrapper 且带 own/foreign 归因；裸 commit 面被 gate-commit-gw 封死）；PURE-SHIM↔gate-ssot-code 一对未跳（三脚本链，裁定册 §5.1.3） |
| 11 | 失败归因器 | `_precommit_classify`(:3712-3732)：失败段解析+own/foreign 归因（证据行剥离 Fix:/->/python 样板防误归因 :3723-3728）；`_precommit_decide_failure`(:3734-3797)：mutation 持续=fail-closed 阻断(:3747-3763)、own 违规=阻断(:3765-3780)、foreign/存量债=warn+审计放行(:3782-3797)；阻断门禁名 **GATE-PRECOMMIT-RUN**；变异侦测重跑 1 次消解并发假阳（`_precommit_execute` :3440-3477，attempts=2）；infra 故障=warn+审计+放行(:3587-3599) |
| 12 | 遥测 `_append_precommit_channel_stat` | :1946-1961——每次通道执行写一行 `.runtime/audit/precommit_channel_stats.jsonl`（total_ms/fast_subset_ms/rc/skipped/infra_error/files_count；独立成册因 commit_block_events 是阈值化只记异常设计）；现 187 行（9/24→9/29） |
| 13 | gate-test（最大单项） | .pre-commit-config.yaml:548-555：`run_gate_chain.py` 顺序执行 pytest `--collect-only -q -m "not slow and not e2e"`（全树收集）+check_test_structure.py；触发面 `^src/zephyr/.*\.py$|^tests/.*\.py$`；tests/ 下 .py 现 **3967** 个（9/24 报告口径 3720，已漂；find 实测 2026-09-30）；增量化=待办 st-gate-rationalize A5（staged 收集，裁定册 §5.2 首行） |
| 14 | 逐台 hook 裁定指针 | 裁定册 §5.2 pre-commit 57 台逐台表（:210-265，其中 4 死台+node-label 已于 9/30 退役出配置）、§5.3 manual/post-commit/commit-msg 12 条（:267-276，含 9/30 退役 drift-light 后现 11 条）、§11.2/§11.4 执行留痕 |

## §2 六向台账

| 组件 | 上游触发源 | 下游消费方 | 输入面 | 输出面 | 真源锚 | 耗时账 |
|------|-----------|-----------|--------|--------|--------|--------|
| step 5.5 调用 | `_resolve_commit_result`（全局锁内） | 阻断串→CommitResult | files 清单 | None=放行/str=GATE-PRECOMMIT-RUN 阻断 | git_commit_gateway.py:3819-3822 | p50 49.0s（复测 187 行）全排他占用全局锁 |
| flag gate_precommit_run | flags.yaml | _run_precommit_channel 首行短路 | config/flags.yaml | bool（异常回退 OFF） | flags.yaml:109-112 | 零 |
| 临时索引 | 通道每次执行 | 索引扫描型 53 hook 的视图 | read-tree HEAD+own add/rm | GIT_INDEX_FILE 隔离判定面 | :3605-3670/:3398-3415 | 3-4 次 git 子进程/笔 |
| Phase-A | _precommit_run_scoped :3641 | 首败短路/Phase-B 收窄枚举 | own 文件 chunks | fa_output+fa_rc | :3672-3710 | 复测快段 sum 12,362s=总 sum 80.5%（裁定册口径 87%/38.4s p50 构成） |
| Phase-B | Phase-A 绿后 :3662 | 归因器 | extra_skip=快段反选 | output/rc/mutation | :3654-3664 | 绿路径 54 台次（Rx-4 后） |
| SKIP 清单 | env SKIP 组装 :3561 | pre_commit 运行时 | 8 个 hook id | 8 台不执行 | :470-473 | 省 5 twin 双跑+防误杀 3 台 |
| 归因器 | rc!=0 | 阻断/warn 审计 jsonl | hook 输出文本+own 文件清单 | own_failed/foreign_failed 分档 | :3712-3797 | 秒级文本处理 |
| 遥测 jsonl | 每次通道执行 | 本册复测/后续战役对比 | 运行元数据 | jsonl 行 | :1946-1961 | 每日≈通道执行数，可控（:1950-1953） |
| gate-test | 触发面 src/tests .py | 阻断/慢尾续跑 | 全树 3967 测试文件收集 | 收集+结构判定 | config:548-555 | 最大单项；A5 增量化待施工 |

## §3 缺陷与已修

**已修（2026-09-29/30 两批）**：

1. SKIP 扩容 +5 同脚本 twin——通道内双跑消除（03ce599b85②；gateway :464-473 注释载 Owner 批依据）。
2. Rx-4 Phase-B 收窄为慢尾续跑——绿路径 91→54 台次、外推 -48s/件（60d7bdda65②；:3654-3664）。
3. Rx-3 四台确定性快检 fail_fast——红路径首红 p50 88-100s→<20s（60d7bdda65①；config :70/:78/:162/:169）。
4. 4 死 hook+node-label 退役、vms-ssot 收缩单分支（03ce599b85④，墓碑 :288/:292/:710/:887/:924）。
5. A1 装表：通道耗时从"24h 账面恒 0 的遥测黑洞"变独立成册分段记录（:3823-3824 注释自认病根；:1946-1961）。

**在案缺陷/债（未清）**：

1. **通道在全局锁内**：p50 ~44-49s 全排他，所有人挡在门外（:3819 接线位于 _commit_locked；处方=出锁+锁内 staged 指纹复核，裁定册 §5.1.1/§8 P1 第8项——须与单趟化一起重设计，裁定册 §11 明示"勿单独拆"）。
2. **两段式绿件双付**：Phase-A 快段调用对绿件多付一次（:3635-3653 结构性存在；单趟化待办，裁定册 §5.1.2/§11）。
3. 慢尾清单含 2 死 id（gate-13/gate-14，:406-407）——无害但漂移，宜随下批 config 触碰同批清理。
4. gateway docstring/flag 描述口径漂移：:3506-3507 仍写"55 台 pre-commit 门禁"、flags.yaml:111 仍写"SKIP=gate-commit-gw+gate-worktree-required"（实际 8 台）——文档债非行为债。
5. gate-test 全树收集 3967 文件=通道最大单项，增量化未施工（A5 待办）。
6. 首过率低：裁定册载 9%（9/24 报告，:387"9% 首过率下 Phase-A 对红件净省"）；本册复测 rc==0 仅 1/187——注意 rc!=0≠阻断（foreign/存量债 warn 放行也 rc=1，归因器分流 :3782-3797），真阻断率须从 commit_block_events.jsonl `precommit_channel_blocked` 事件面取数（移交 E10）。

## §4 待办移交

| 项 | 内容 | 认领 |
|----|------|------|
| T-E4-1 | A5：gate-test 改 staged 测试文件收集（判据保留=测试可导入性；全树收集移 CI/夜检，裁定册 §5.2 首行） | st-gate-rationalize A 段 |
| T-E4-2 | 通道出锁+锁内 staged 指纹复核，与单趟化（拆 Phase-A/B 或 Phase-B 跳过已过台）一并重设计施工（裁定册 §8 P1 第8项/§11——勿单独拆） | B 段（等解锁盯队列） |
| T-E4-3 | 慢尾清单清 2 死 id（gate-13/gate-14，:406-407）随下批 config 同批 | 随 T-E4-2 |
| T-E4-4 | gateway :3506-3507 与 flags.yaml:111 口径刷新（55→53 台、SKIP 2→8 台）随下批 gateway/flags 触碰同批 | 施工班顺手件 |
| T-E4-5 | 真阻断率/首过率从 commit_block_events `precommit_channel_blocked` 面重算（rc 口径只反映 hook 失败不反映阻断） | E10 观测册 M-E10 |
| T-E4-6 | PURE-SHIM↔gate-ssot-code 链内单层化（三脚本链跳过方案，裁定册 §5.1.3 尾） | P1 簇4 批附带评估 |
