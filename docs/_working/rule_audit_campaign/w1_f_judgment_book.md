---
ttl: task_bound
completes_when: P1 rules 批落地且验收数字达标
session: st-maxexec-20260920
issue: MAXEXEC-P1
---

# W1-F 判决册（WP9 案卷闸5 逐条判决，裁定#372 承载）

判决人=Max（st-maxexec-20260920，裁定#371 授权）。对象=v2 案卷 1404 份（dossiers_v2_index.yaml，run_stamp=2026-09-19T09:23:06Z @8b056db496）。
判决判据=D6 三闸原文（照抄于 dossiers_v2_summary.yaml 判据版本节）+#346/#347/#349 既有裁定框架。本册判决一经落地，D-14 对 rules/ 的冻结按 #346 框架解除（判案已毕）。

## 一、闸1 悬空强制 142 条逐簇判决（簇内同判，证据=亲验）

机械验证底表：.runtime/tmp/p1_gate1_mechanical.txt（每强制体 file_exists/git grep 实测）。

| 簇 | 条数 | 悬空体 | 实证 | 判决 | 落地动作 |
|---|---|---|---|---|---|
| 1 | 57 | `confirm-action`（trae_021 全族 ABS/PS_STD 条款） | 系交互语义名非实体；语义真承载=risk_tier_registry.yaml human_gate（人工流程类，D6 四类之三）+宪法 §5 人机门位 | **A 映射修正——非悬空** | trae_021 §enforcement 加 `confirm-action`→`risk_tier_registry.human_gate（Owner 确认人工流程）` 映射注记一行；条款正文不动（语义已真承载） |
| 2 | 35 | `scripts/governance/score_architecture.py`（trae_044） | c441a1fca5 迁移→f57016319e 退役（git log --follow 亲验）；现行量化通道=run_all.py+script-manifest | **D3 指向修正至现行体系** | trae_044 四处引用改注"已退役（f57016319e），现行=run_all.py 按 script-manifest 全量"；命令行 `score_architecture.py --quarterly` 改 `run_all.py`（manifest 为准） |
| 3 | 31 | `scripts/governance/d5_architecture/validators/lifecycle/validate_phase_transition.py`（trae_036） | 同 f57016319e 退役；继任者同目录 validate_module_lifecycle.py（8 阶段状态机/逆向转换校验=转换校验本体）+validate_lifecycle_refs.py 实存（头注亲验） | **A 重指继任** | trae_036 executors 改指 validate_module_lifecycle.py + validate_lifecycle_refs.py，附退役史注记 |
| 4 | 2 | `scripts/ide_health_service.py` + `src/zephyr/trading/ide_health_daemon.py`（trae_053） | 6fe7e96dfc 2026-08-28 僵尸清除裁定退役（#346 预判 D3 证实） | **D3 真删终判——改历史注记** | trae_053 references 移除两路径，注"ide_health 族 2026-08-28 僵尸清除退役（6fe7e96dfc）" |
| 5 | 4 | `COMMIT-CRITICAL-SECTION-LOCK`/`git_commit_gateway_critical_section_guard`/`session_worktree_escape_hatch_demotion`（trae_079） | #347 已裁：_GlobalCommitLock 实存 gateway:2360-2366 | **A 身份映射（#347 处方执行）** | trae_079 §enforcement executors 改指 `src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py::_GlobalCommitLock`（code_embedded 保留）；gate_registry 加 commit-gate 型机制条目 |
| 6 | ~10 | `session_worktree_{start,commit,merge,sweep,startup_health}_check` 族 + `capability_lookup_{bypass_policy,health_reconciler,required_gate_whitelist}` 族（trae_065/074 等） | 机制实存（session_worktree_start 实跑亲验含 health_check；capability_lookup 模块在册）；检查名=行为概念分解名 | **A 身份映射——改指模块实名** | executors 改 `zephyr.gov_enforcement.rule_bridge.session_worktree::<实存函数族>` / `zephyr.governance.capability_lookup::<实存函数>`，逐名对函数 |
| 7 | 4 | `commit_gate_bare_subprocess`/`commit_gate_precommit_offline`/`gate_frontmatter_incremental`/`gate_naming_incremental`（trae_067/073/084） | 注册表实名实存：BARE-SUBPROCESS/GATE-PRECOMMIT-OFFLINE/GATE-FRONTMETER→GATE-FRONTMATTER/GATE-NAMING（gate_registry 169 条亲验） | **A 别名改注册表实名** | 条文 executors 用 gate_registry canonical ID |
| 8 | 6 | `static_scan_block`/`static_scan_warn_only`/`task_card_description_audit`/`audit_log_jsonl`/`trae_ide_hardcoded_safety_check`/`safe_write_text_cas`（trae_063/065/066/067/068/073/084/085） | static_scan_*=扫描模式描述（block/warn 是模式非实体），承载=.pre-commit-config.yaml 钩子链本体；safe_write_text_cas→file_utils.safe_write_text 实存（本会话实跑亲验）；其余三名为流程动作描述 | **A 模式名改指载体 + 实名重指** | static_scan_* 改指 `.pre-commit-config.yaml`（钩子链）+模式后缀语义保留；safe_write_text_cas 改 `src/zephyr/shared/io/file_utils.py::safe_write_text`；task_card_description_audit/audit_log_jsonl/trae_ide_hardcoded_safety_check 改指所属实存流程（construction_workflow_policy 审计步/lookup_audit 目录/check 脚本族）——逐条锚定见落地 diff |
| 9 | 4 | `GATE-DD07`/`GATE-PURE-ASSERTION`/`GATE-BASELINE-AWARE`/`scripts/_tmp_scan.py`（agent_constitution_legacy_v1.md） | 出处=已归档历史宪法（零内容丢失档案件） | **E 归档件豁免——不计悬空** | 零改动（对齐 #349 分型适用面精神：归档面不适用现行判据）；GATE-DD07 实际已被 GATE-SCRIPT-Q 合并承载（pre-commit 输出亲验），PURE-ASSERTION 在册 |

簇计=57+35+31+2+4+10+4+6+4=153 条目位＞142（同案卷多强制体去重后 142，簇间有重叠计数，以 index g1_fail=142 为准）。

## 二、闸3 多真源 5 条判决（D1 收敛唯一真源）

| # | 案卷 | 承载面 | 判决 |
|---|---|---|---|
| 1 | trae_037#gov_arch_010_cycle_analysis | 文档+规则YAML（6 值） | **YAML=真源**（RULE-SSOT 规则数据方向），文档段改指针 |
| 2 | trae_047#gov_eng_002_directory_mapping | 代码+文档（3 值） | **代码常量=真源**（M5 处方 :352 同向），文档改派生指针 |
| 3 | construction_workflow_policy#Step3.5 | 文档+规则YAML（1 值） | **YAML=真源**，policy 步骤改指针 |
| 4 | agent_constitution_l0#§9 运维红线@L128 | 代码+文档+YAML（4 值） | 判决=**YAML=真源+宪法行改指针**；宪法属 L0 文件→随 P9 等长替换批联动落地（本批不动宪法，挂账 P9） |
| 5 | agent_constitution_legacy_v1#RULE-GIT-SAFE | 代码+文档（1 值） | **E 归档件豁免**（同簇 9） |

## 三、M1 三分终判（#346 ②③ 兑现）

- **① 29 重指**：patch 本班 `git apply --check` 复验 PASS（16 文件）。判决=**执行**。
- **② 5 条归档当现役**：本班全仓 _archive 引用面实测，rules/ 内归档路径引用仅 trae_058:97 一条（`- path: scripts/governance/_archive/`）——该条是**扫描排除配置的合法引用**（排除归档目录本身），非"当现役"缺陷。A2 原清单 5 条中 ide_health 2 条已在簇 4 终判 D3，其余 3 条经 salvage 无现行价值物。判决=**5 条全部 D3 历史注记/移除**（含 ide_health 2 条），零重建。
- **③ 7 条真删无后继**：根因 commit=f57016319e（score_architecture/validate_phase_transition/validate_dag 三脚本+dimension_audit_matrix.md）。validate_dag.py 与 dimension_audit_matrix.md 的引用面在 rules/ 外（docs/02 架构文档），不属本批。判决=**7 条中 rules/ 面的（簇 2+3+4=68 条位）按上表落地；rules/ 外 2 项挂账 P11 归档循环按 C 类处置**。
- **流程缺陷治本**（#346 上报项）：退役 SOP 补"grep rules/ 引用面清扫"一步——并入既有 construction_workflow_policy 退役步骤（P9 v5 版承载），不立新规则。

## 四、#353① 条文侧收紧（Owner 门位由 #371 授权代行）

#353① 上交项（SSoT 兜底+全局锁 fail-open）按原建议裁：**fail-closed+emergency 通道**——trae_079 §enforcement 增补"锁获取失败=拒绝提交（fail-closed），逃生仅 emergency_commit 显式通道"条文；代码侧 gateway 改造属 #353②③ 同族施工（LSG 配置化+引号路径解析已在 B 列），本批只落条文侧，代码侧挂 P11 按需施工（当前 commit_queue 正门不走该兜底路径，风险敞口=直连模式，已由队列正门+POST-COMMIT-GUARD 双层覆盖）。

## 五、验收数字（落地后复测口径）

1. #344：skip_dirs_docs 加 algo_flow 后 C-04 红数 636→≈27（复测命令见 §六）。
2. #346①：29 行重指后 rules/ 路径引用真删无后继面（排除示例占位符/归档件/动态模板）→0。
3. #350：21 处二值化后闸2 不可二值判定数 v2 9→0（词表收窄另消 13 误报）。
4. 闸1 悬空 142→0（簇 9 豁免 4 条外全数消解；豁免口径=归档件不适用）。
5. 闸3 多真源 5→1（仅留 #4 挂 P9 联动 1 条）。

## 六、复测命令

```bash
python scripts/governance/check_registry_consistency.py  # 或对应 C-04 计数器
git apply --check docs/_working/rule_audit_campaign/a2_handoff/rules_m1_repoint.patch  # 落地后应报 already applied
python .runtime/tmp/recount_g1.py  # 重算悬空数（以 v2 判据重扫 rules/，本批随落地提交到 .runtime/tmp）
```

## 七、证据等级

全部[亲验]（git log --follow/gate_registry 169 条实测/继任脚本头注/本会话 session_worktree_start 与 safe_write_text 实跑/机械验证底表），除：闸3#4 承载值细节[转报·dossiers index]；簇 8 中三名流程动作锚点[推断·落地 diff 时逐条亲验补锚]。
