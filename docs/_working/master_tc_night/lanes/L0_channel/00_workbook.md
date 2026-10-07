---
ttl: task_bound
completes_when: 总包夜战战役(master_tc_night)归档收尾
---

# L0 总包通道修复车道工作簿（st-mastertc-l0）

> 任务面：R5 病灶改名 / token 批登记 / 死袋捞回 / 裁定袋守护 / 队列提交。
> 本簿由 CREATE-GUARD 批量通道登记 token（master-tc-night-00-workbook-20261007，与各车道 workbook 同名同 token，按 file 路径区分）。

## §一 R5-DIGIT-SUFFIX 病灶诊断与改名裁定

- 门真源：`src/zephyr/gov_enforcement/commit_gates/r5_digit_suffix_gate.py`（gate_id=R5-DIGIT-SUFFIX，priority=35，fail-closed）。
- 触发模式：正则 `_\d+$` 命中 commit 路径任一父目录名，且该目录不在 `git ls-tree HEAD`（增量检测只拦新引入）；`master_tc_20261006` 尾段 `_20261006` 命中。
- 官方逃生三通道：①历史违规（目录已在 HEAD=progressive_convergence 跳过）②目录级豁免标记 `r5_exemption.md`（frontmatter 非空 `r5_digit_suffix_exempt`）③改名去后缀（历史配方）。
- **裁定=改名**：目录 18 文件当时全部 staged=A 且不在 HEAD（`git ls-tree HEAD` 空），既有 r5_exemption.md 标记未能解拦截（标记先于拦截写入但内容物曾为旧快照/门读盘面时序差），改名是治本而非续命：`master_tc_night` 不含数字后缀，且语义更准（夜战战役）。18 文件 `git mv`（index 同步换绑，非裸 mv——目录实际已 tracked，与任务书"尚未 tracked"前提不符，已按实况修正手法）。00_orchestration.md 等目录内 14 文件自引用路径已同步替换，残留=0。r5_exemption.md 保留作审计痕迹（改名后其豁免语义已 moot，战役收尾可删）。旧路径孤儿 claim（18 条）30 分钟 TTL 自动过期，无阻塞。

## §二 token 批登记与 stomper 战根因修复

- 现象：`batch_creation_tokens.py` 写前自检 FAIL——盘上册相对 HEAD 缺 token 条目；手工增量补回（safe_write_text CAS）后 **20 秒内被再抹**（safe_write 审计链：00:20:30 本车道写 / 00:20:50 PID 25644 以我写后内容为基底 overwrite）。
- stomper 身份：`python -m zephyr.gov_enforcement.rule_bridge.commit_belt_daemon`（常驻守护）。写入路径=`_projection_drift_probe` → `projection_generator.run(mode="render")`：投影武装态下盘面 YAML 是 **PG 账本投影**，盘 sha≠state.content_sha256 即判"私改"，从 `registry_snapshot` 最新发布版整册重打（PG-wins）。证据：`.runtime/gate_audit/registry_drift_20261007T002046836549.diff`。
- 根因：`registry_snapshot`（发布快照）落后于 `registry_entry`/YAML——HEAD 独有 36 条 token 从未入 PG；而 YAML→PG 回填通道（dual_track）已于 2026-10-03 退役（`.runtime/registry_ledger/dual_track.enabled.retired-20261003`）。**一切 YAML 手改必被秒级回滚，裸写无解。**
- 正道修复（意图 API 三步，`scripts/governance/d3_metadata/register_tokens_ledger.py`，register→publish→render）：
  - HEAD 独有 36 条补登记入 PG（含死袋 0005 族关键三 token：grid_stats_engine / lead_lag_validator / chart_resonance_prereg）；
  - master_tc_night 新 18 条登记（capability=master_tc_night，created_by=st-mastertc-l0，merge_evaluation=总包夜战施工文档,战役终了归档,无既有真源重复）；
  - publish snapshot **v76** + render 落盘：盘面 creation_tokens=13853 = HEAD 13835 + 18 新增（只增不减机械成立）。
- 已知瑕疵：batch 工具 token 命名按文件 stem 派生，5 个车道 `00_workbook.md` 同名 → 同 token 值 `master-tc-night-00-workbook-20261007` 复用于 5 文件（entry_key=(file,token) 各异，门按 file 路径精确比对不受影响；留待命名规则治理，非本车道裁定权）。
- 提交语义注意（重要经验）：入队预检 CREATE-GUARD 用**落地仿真态**（袋内容 ∪ HEAD 册，`commit_preflight._head_registry_yaml_data`），**不读盘面**——token 册必须与内容同批入袋、或先行落地，否则入队口必拦（本轮 3 次实测）。盘面在册≠可提交。

## §三 死袋捞回台账（.runtime/commit_queue/dead/）

| 袋 | 死因 | 处置 |
|---|------|------|
| q-...-l7-0003 | PERM-TRIGGER（grid_stats_engine 时间触发未注册事件订阅） | **被 0005 取代**：0005 袋内即修复后内容（`_chi2_sf while True` 有界化），且 0003 携带陈旧 registry 快照不可落地。不重投。 |
| q-...-l7-0004 | R5-DIGIT-SUFFIX（master_tc_20261006 目录名） | 改名已根治。按清单换新路径重投（L7 台账取盘面终态 07:5x，较袋内 blob 新）；袋内 registry 快照条目剔除不落地。→ 本车道批次二投递。 |
| q-...-l7-0005 | CREATE-GUARD（落地面盘上基册被翻面，token 实在 HEAD） | **重投为新袋 q-20261007-st-mastertc-l7-0010**（--force 越熔断留痕，同签名死信全仓 551 次；修因=§二 PG 补登记后重投）。 |
| q-...-l7-0007 | 同 0005（重投#1，forced） | 与 0005 blob 逐字节相同 → 合并 0005 一次落地，不重复投。 |
| q-...-l7-0008 | 同 0005（重投#2，forced） | 同上合并。 |
| q-...-l7-0009 | 同 0005（重投#3，钉 base-head 未生效） | 同上合并；其"落地面读 HEAD 册"的判死记录与 §二 提交语义注意互证。 |

## §四 裁定袋守护（q-20261007-st-mastertc-l10-0001）

（状态记录见文末"终态"节；本节登记监控义务。）

## §五 本车道提交批次

- 批次一：capability_canonical_file_registry.yaml（v76/v77 render 面，HEAD+19 只增不减）+ master_tc_night/ 全目录 18 文件（R5 改名+自引用更新）+ 本簿。token 与内容同批=CREATE-GUARD 落地仿真态合法面。
- 入队预检连环门实录（同批三连拦，逐门正门解）：①SESSION-REQUIRED（本车道未走 session_worktree_start，按 2026-08-13 用户裁定以 --allow-overlap 逃生放行）②CREATE-GUARD 落地仿真态（L0 簿创建晚于 token 批→补登记 master-tc-night-l0-channel-workbook-20261007 后过）③TTL-METADATA（docs/_working 临时区 8 个 .md 缺 ttl frontmatter，统一补 `ttl: task_bound`+completes_when）。
- 批次二（批次一 HEAD 落地后）：q-0004 清单 7 文件（start_paper_session / test_fill_jsonl_single_writer / quant_methodology 4 篇 / L7 台账新路径）。

## 终态（收尾时回填）

见 §六。
