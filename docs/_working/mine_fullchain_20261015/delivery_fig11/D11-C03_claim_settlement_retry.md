---
ttl: task_bound
doc_type: fig11_step_ledger
map_node: D11-C03
name_zh: claim 结算与失败重试语义
mined: 2026-10-15
ssot: config/dev_delivery_map.yaml#D11-C03
---

# D11-C03 claim 结算与失败重试语义

## 1. 定义
提交车道第三环节：claim 生命周期结算。决策问题=「成功才释放 claim？失败保留并重试要不要带 --adopt-prior-work？」契约（git_commit.py:32-36 文件头）：成功释放/失败保留+.ailocks TTL 收窄至 --failed-claim-ttl（缺省 300s）；--adopt-prior-work 治 FOREIGN_CHANGE 恶性循环（失败提交 finally 释放 claim 但文件保持 staged，不带 adopt 的重新 claim 会把 staged 差异判外来）；死会话 stale claim=网关 release_files 精准释放。

## 2. 六向台账

### 2.1 输入面
- commit 结果（OK/失败各态）
- 重试请求（--adopt-prior-work，git_commit.py:1187 argparse 实读：「allow_overlap 在 commit 时绕 gate，adopt-prior-work 在 claim 时认领附审计」）
- 死会话释放请求：gateway release_files

### 2.2 输出面
- 结算台账：`.runtime/claim_snapshots/claim_retention.jsonl`（失败保留+TTL 收窄留痕；图 exec_evidence 在盘；本车道复核 claim_snapshots 目录 959 件在产）
- adopt 审计：.runtime/claim_snapshots/{sid}_adopted.jsonl（实际基线 diff_size+sha256）

### 2.3 SSOT 真源
- `config/dev_delivery_map.yaml#D11-C03`（wired/production，exit_codes=[1,6,7]）
- 骨架：04_提交正门与全局锁.md；宪法 §2.3（失败重试带 --adopt-prior-work 铁律）

### 2.4 代码模块
- `scripts/git_commit.py:683` `def _retain_claims_after_failure(`+`:737` `def _settle_claims_after_commit(`（图记 :680/:734，行锚微漂 +3）
- 同文件 `:494` `claimed = gw.claim_files(args.session, files, adopt_prior_work=args.adopt_prior_work)`（主流程接线实读）
- `src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py:1549` claim_files（adopt 空基线语义在 INVARIANTS :8，tracker #92 幂等基线不覆盖）

### 2.5 门禁约束
- 联动门：CLAIM-REQUIRED（exit 6 双义：无 claim/或 release-only 回读仍有持有）、FOREIGN-CHANGE（exit 1，处方=--adopt-prior-work）——结算语义即这两门的状态机供给

### 2.6 自动化触发
- commit finally 自动结算/保留；TTL 自动收窄；exit 1 处方自动递送（C02）

## 3. 自审闸三态

| 向 | 三态 | 依据 |
|---|---|---|
| 输入面 | pass | commit 结果+adopt 参数+release 通道实存 |
| 输出面 | pass | retention 台账+adopt 审计面在案 |
| SSOT真源 | pass | 图/骨架/宪法三层一致 |
| 代码模块 | pass | 三锚点实存（行锚微漂 +3） |
| 门禁约束 | pass | exit 1/6/7 与两门联动自洽 |
| 自动化触发 | pass | finally 自动结算 |

## 4. 缺口与建议
- 【观测建议】claim_retention.jsonl 单独健康计数（保留量/ TTL 内重试成功率）未见聚合出口，建议并入 C13。
- 【语义提示】FOREIGN_CHANGE 恶性循环的根治依赖提交人读处方；建议 exit 1 输出直接内联 --adopt-prior-work 完整命令样例（现处方文案已在矩阵，递送面归 C02 收口）。
