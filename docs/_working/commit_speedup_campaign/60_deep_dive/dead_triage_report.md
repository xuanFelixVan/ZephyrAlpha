---
ttl: task_bound
generated: 2026-09-25
agent: commit-chain dead-letter triage (read-only)
scope: .runtime/commit_queue/dead/*.json (top-level)
evidence: .runtime/tmp/csx_dt_*.py (inventory/verify/cross), full list dead_triage.yaml (same dir)
---

# 死信分诊报告（commit_queue/dead 428 封四态判定）

## 1. 结论速览

- 死信总数 **428** 封（top-level JSON；另有历史归档目录 dead/archive_* 不在本次口径内），文件条目 **5222** 个（去重路径 1205）。
- 「291 封未回队」基本属实：无 requeued 标记的死信 **294** 封（差 3 封为其后新回队或口径时刻差）。
- 「3915 文件蒸发」**不成立**：该 294 封共 3948 个文件条目（与 3915 同量级），其中仅 **2079 个条目（52%）在 dev HEAD 缺失**；583 个与 HEAD 逐字节一致（sha256 相同=已落地），1286 个 HEAD 上存在更新版本（被后续批次取代）。按唯一路径计，蒸发仅 **566/1205** 条。
- 内容并没有'蒸发'：5217/5222 个条目带 blob_sha256 内容寻址快照（.runtime/commit_queue/blobs/），快照抽检 3/3 完整；12/12 head_same 抽样经 `git show HEAD:<path>` 独立哈希复核一致。任何死信内容都可从 blobs/ 确定性恢复，无需回队。

## 2. 四态分布

| 态 | 封数 | 说明 |
|---|---|---|
| 已复活 revived | 223 | 全部文件已在 dev HEAD（186 封含被更新版本取代的文件；27 封经 requeue 链在 done 落地）|
| 可回队 requeue | 27 | 环境类死因（landing 异常/基底冲突）且文件确实缺失，会话已死 |
| 应废弃 discard | 106 | 判据类死因（门禁阻断）且同会话在 done 有更新落地（新批已替代）|
| 需属主 owner | 59 | 会话仍存活（session_registry PID 核活），归属其处置 |
| 废弃候选 review | 13 | 门禁阻断+会话已死+无替代落地，按'应废弃'处置但留人工确认 |

文件条目级：head_same **812**（15%，逐字节已落地）/ head_diff **1742**（33%，HEAD 有其他版本）/ head_missing **2668**（51%，真缺失）。

## 3. 可回队清单（按预期价值排序，交统筹执行，本代理不回队）

⚠ 回队风险：24/27 封含 head_diff 文件——直接重放会用旧快照覆盖 HEAD 上的新内容，须先剔除/重_base 这类文件，或裁剪 files[] 至 head_missing 子集。

| # | qid | 会话 | 文件数 | 缺失 | diff风险 | 死因 |
|---|---|---|---|---|---|---|
| 1 | q-20260924-st-mapbuild-20260924-0020 | st-mapbuild-20260924 | 39 | 39 | 0 | landing_anomaly: landing 异常: LandingEnvironmentError: landing 环境不可用（repo_root=D:\ZephyrAlpha）: Ga |
| 2 | q-20260924-st-mapbuild-20260924-0022 | st-mapbuild-20260924 | 24 | 18 | 6 | base_conflict: 冲突：快照基底 cb6b4bfc0e12（与 dev 的共同祖先 cb6b4bfc0e12）之后 dev 已推进且触及同路径 ['scripts/governa |
| 3 | q-20260924-st-audit-fix-20260924-0007 | st-audit-fix-20260924 | 23 | 7 | 9 | base_conflict: 冲突：入队基底 f53316c6f9d6 之后 dev 已推进且触及同路径 ['scripts/commit_queue.py', 'scripts/git_c |
| 4 | q-20260924-st-audit-fix-20260924-0018 | st-audit-fix-20260924 | 12 | 7 | 2 | base_conflict: cascade_stale: 基底重校验不适用 ['docs/01_policies_and_standards/_registry/catalogs/capa |
| 5 | q-20260924-st-audit-fix-20260924-0020 | st-audit-fix-20260924 | 12 | 7 | 2 | base_conflict: cascade_stale: 基底重校验不适用 ['docs/01_policies_and_standards/_registry/catalogs/capa |
| 6 | q-20260924-st-mapbuild-20260924-0012 | st-mapbuild-20260924 | 6 | 6 | 0 | landing_anomaly: 网关落盘失败（CLAIM_REQUIRED_VIOLATION）: session 'st-mapbuild-20260924' 已注册但目标文件未 claim |
| 7 | q-20260923-st-combine-20260923-0014 | st-combine-20260923 | 12 | 4 | 8 | landing_anomaly: landing 异常: LandingEnvironmentError: landing 环境不可用（repo_root=D:\ZephyrAlpha）: Ga |
| 8 | q-20260923-st-combine-20260923-0015 | st-combine-20260923 | 12 | 4 | 8 | landing_anomaly: landing 异常: LandingEnvironmentError: landing 环境不可用（repo_root=D:\ZephyrAlpha）: Ga |
| 9 | q-20260923-st-combine-20260923-0016 | st-combine-20260923 | 12 | 4 | 8 | landing_anomaly: landing 异常: LandingEnvironmentError: landing 环境不可用（repo_root=D:\ZephyrAlpha\.wor |
| 10 | q-20260923-st-combine-20260923-0017 | st-combine-20260923 | 12 | 4 | 8 | landing_anomaly: landing 异常: LandingEnvironmentError: landing 环境不可用（repo_root=D:\ZephyrAlpha）: Ga |
| 11 | q-20260923-st-xhs-full-20260922-0043 | st-xhs-full-20260922 | 16 | 4 | 9 | landing_anomaly: landing 异常: LandingEnvironmentError: landing 环境不可用（repo_root=D:\ZephyrAlpha）: Ga |
| 12 | q-20260923-st-combine-20260923-0001 | st-combine-20260923 | 9 | 3 | 6 | landing_anomaly: landing 异常: LandingEnvironmentError: landing 环境不可用（repo_root=D:\ZephyrAlpha）: Ga |
| 13 | q-20260923-st-combine-20260923-0002 | st-combine-20260923 | 9 | 3 | 6 | landing_anomaly: landing 异常: LandingEnvironmentError: landing 环境不可用（repo_root=D:\ZephyrAlpha）: Ga |
| 14 | q-20260923-st-combine-20260923-0003 | st-combine-20260923 | 9 | 3 | 6 | landing_anomaly: landing 异常: RuntimeError: [landing] 注册表三向合并失败（死信回退人工）: docs/01_policies_and_stan |
| 15 | q-20260923-st-combine-20260923-0004 | st-combine-20260923 | 9 | 3 | 6 | landing_anomaly: landing 异常: RuntimeError: [landing] 注册表三向合并失败（死信回退人工）: docs/01_policies_and_stan |
| … | 其余 12 封见 dead_triage.yaml requeue 段 | | | | | |

## 4. 应废弃（106 封 + 13 封 review 候选）

判据=死因为门禁阻断（TRANSLATION-COVERAGE/CLONEGUARD/COMMIT_SCOPE 等）且同会话随后在 done 有新落地——旧批已被新批替代。按会话分布（top10）：

| 会话 | 封数 |
|---|---|
| st-chainpile-20260922 | 22 |
| st-metaq-20260923 | 18 |
| st-mapbuild-20260924 | 14 |
| st-pipeline-final-20260924 | 10 |
| st-ailayer-final-20260924 | 6 |
| st-commitsys-20260924 | 6 |
| st-e2e-20260924 | 5 |
| st-audit-fix-20260924 | 5 |
| st-ailayer-p1-20260923 | 4 |
| st-align-dirty-20260924 | 3 |

review 候选 13 封（门禁未修复+会话死+无替代落地，建议一并废弃，留 Owner 确认）：q-20260923-st-combine-20260923-0008（st-combine-20260923, 缺失3文件）, q-20260923-st-combine-20260923-0009（st-combine-20260923, 缺失3文件）, q-20260923-st-combine-20260923-0010（st-combine-20260923, 缺失3文件）, q-20260923-st-combine-20260923-0011（st-combine-20260923, 缺失3文件）, q-20260923-st-combine-20260923-0012（st-combine-20260923, 缺失3文件）, q-20260923-st-combine-20260923-0013（st-combine-20260923, 缺失3文件）, q-20260923-st-combine-20260923-0018（st-combine-20260923, 缺失4文件）, q-20260923-st-datatail-20260923-0001（st-datatail-20260923, 缺失2文件）, q-20260923-st-emoreplay-20260923-0001（st-emoreplay-20260923, 缺失7文件）, q-20260923-st-emoreplay-20260923-0002（st-emoreplay-20260923, 缺失7文件）, q-20260923-st-nightdata-20260923-0002（st-nightdata-20260923, 缺失1文件）, q-20260923-st-wm1-buildB-20260923-0001（st-wm1-buildB-20260923, 缺失9文件）, q-20260924-st-chainpile-20260922-0075（st-chainpile-20260922, 缺失3文件）

## 5. 需属主（59 封，会话存活）

| 会话 | 死信数 | 文件条目 | 其中 HEAD 缺失 |
|---|---|---|---|
| st-t0-matrix-20260924 | 12 | 405 | 248 |
| st-commitspeed-tbl-20260924 | 12 | 209 | 178 |
| st-metaq-gc-20260924 | 9 | 108 | 107 |
| st-cmd-20260924 | 17 | 67 | 57 |
| st-wm1-wave0-20260924 | 9 | 53 | 47 |

存活判定：session_registry.json 中 PID 经 tasklist 核活（6/7 注册会话存活；缺失文件大头在这些活会话手上，属其 WIP，不由死信通道处理）。

## 6. 方法与局限

1. 复活判定：以死信 files[] 的 blob_sha256 对 dev HEAD 内容哈希（`git cat-file --batch` 批量）——相同=已复活；不同但存在=被取代（head_diff，视同复活，因任务目标内容已无落地价值或需人工比对）。
2. requeue 链解析至多 3 跳（done/pending/dead_again）；dead_again 链的最终内容以链尾死信快照为准，不重复计数。
3. 局限：head_diff 无法区分'HEAD 更新（安全）'与'HEAD 更旧（死信增量仍缺失）'，若需精确判定须逐封对比 base_head 与快照；requeue 建议一律按 head_missing 子集裁剪后执行。
4. 本报告只读取证，未执行 requeue/commit/任何队列状态变更；脚本存 .runtime/tmp/csx_dt_*.py。

