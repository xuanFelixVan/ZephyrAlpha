---
ttl: task_bound
doc_type: fig11_step_ledger
map_node: D11-C10
name_zh: 真落盘（worktree+CAS+收敛）
mined: 2026-10-15
ssot: config/dev_delivery_map.yaml#D11-C10
---

# D11-C10 真落盘（worktree+CAS+收敛）

## 1. 定义
提交车道第十环节（全图 4 个 partial 之一，red_reason=broken_supply）：队列项真进 dev 的落地执行体。决策问题=「这条队列项能走完落盘五步（幂等→基底→blob→全门禁→CAS update-ref）真进 dev 吗？」INVARIANTS（landing :8 实读）：永不改主工作区脏文件/单写者/幂等不双落（done+landed_id+is-ancestor+标记 grep 三重）/门禁一套不裁（全门禁链零适配）/CAS 冲突死信不卡队/瞬态环境失败抛 LandingEnvironmentError 退回 pending 绝不死信/热册三连退避/主区受限快进收敛 fail-open/k=4 池/ZEPHYR_ALPHA_ROOT 码面指向（st-maint7-20261014）。

## 2. 六向台账

### 2.1 输入面
- processing 项（袋字节+meta）
- 基底输入：base_head→resolve_base_blobs 取基底树 blob（landing :4663）

### 2.2 输出面
- dev ref CAS 提交+done 回填：`.runtime/commit_queue/done`（812 件实测，图记 798）；landed_at/landed_id 回填（图样例 q-20260925-st-metaq-gc-0026 landed_id=a3bb88146cf48403）
- 收敛留痕：`.runtime/commit_queue/main_workspace_sync.jsonl`（实查在盘）

### 2.3 SSOT 真源
- `config/dev_delivery_map.yaml#D11-C10`（build_status=built、wiring_status=partial、red_reason=broken_supply、deadletter_class env→退回 pending/item→dead）
- 骨架：06_入队排空与真落盘.md+§7 附录复核命令

### 2.4 代码模块
- `scripts/governance/commit_queue_landing.py:8`（INVARIANTS 全声明实读）+`:158`/`:2315`（图 source_anchors，主函数行锚需重扫）
- 同文件 `:2101`/`:4925` resolve_base_blobs 填充+`:4738-4749` 内容级比对（袋字节 git blob id==base_blob）
- `scripts/commit_queue.py` _TRANSIENT_GIT_MARKERS/:2206 _transient_env_failure_of/:2227 环境失败统一出口

### 2.5 门禁约束
- 「门禁一套不裁」（Law 3）：serializer worktree 内走 GitCommitGateway 全门禁链（worktree 形态 100 门禁天然生效，INVARIANTS 原文）；码面指向=ZEPHYR_ALPHA_ROOT 作用域限定使子进程导 serializer 快照面而非主区码面（否则码+测同袋合法提交被迫拆册，深队列必崩——e1_mine_repair.md §5.1 实证）

### 2.6 自动化触发
- drain 自动逐项落地；落地后自动级联扫描（D05）+主区受限收敛+reconciler 改道（C12）

## 3. 自审闸三态

| 向 | 三态 | 依据 |
|---|---|---|
| 输入面 | pass | processing 19 件+基底解析实存 |
| 输出面 | pass | done 812 件+收敛留痕在盘，真落地持续在产 |
| SSOT真源 | warn | partial/broken_supply 判定滞后：done/ 最新项回填与「近 3 日计数复核」骨架命令均成立，broken_supply 红因需总包复核（同 C09） |
| 代码模块 | pass | INVARIANTS+关键函数实存 |
| 门禁约束 | pass | 全门禁链+码面指向治本在码 |
| 自动化触发 | pass | 落地/级联/收敛全自动 |

## 4. 缺口与建议
- 【账务复核】partial 红因 broken_supply 证据面（「断供」指什么）在图中未展开，建议总包复核时把红因写成可证伪句（如「某时窗 done 无新增」）。
- 【建议】瞬态特征串 _TRANSIENT_GIT_MARKERS 与 LandingEnvironmentError 双通道并存（env 标记表注记「此标记只兜历史/直连路径的死信」），建议下批把直连路径全部迁 LandingEnvironmentError 后退役 env 标记兜底分支。
