---
ttl: task_bound
working_doc_type: fig11_step_ledger
map_node: D11-S04
name_zh: 改前 claim（文件锁+基线快照）
mined: 2026-10-15
ssot: config/dev_delivery_map.yaml#D11-S04
---

# D11-S04 改前 claim（文件锁+基线快照）

## 1. 定义
会话车道第四环节：动手前领地。决策问题=「动手前这份文件归谁？基线快照锚在哪次 claim？」路径=lock_files acquire（CLI 锁）→网关 claim_files（基线=首次 claim 快照，幂等重跑不覆盖）；热文件另走 safe_write_text CAS 通道；git_commit.py --claim-only 前移协议。

## 2. 六向台账

### 2.1 输入面
- CLI：`scripts/lock_files.py` acquire/batch（:693 `def cmd_acquire(`、:818 `def cmd_acquire_batch(`）
- 网关协议：`scripts/git_commit.py` --claim-only（ERROR_CONTRACT :13 exit 7=claim-only 部分文件被他人持有）
- adopt 语义：claim_files(adopt_prior_work=True) 认领前序未提交变更（gateway INVARIANTS :8）

### 2.2 输出面
- 锁注册表：`.ailocks/registry.json`（实存在盘）
- 基线快照：`.runtime/claim_snapshots/`（2026-10-15 实查 959 件在产；图记 09-25 为 877 件，持续增长）
- 失败保留+TTL 收窄：--failed-claim-ttl 缺省 300s（git_commit.py:34/:662）

### 2.3 SSOT 真源
- `config/dev_delivery_map.yaml#D11-S04`（wired/production，MOD-INF-005）
- 骨架：`docs/_archive/_working_cleared/map_build/fig11_delivery/02_claim协议与暂存晋升.md`

### 2.4 代码模块
- `scripts/lock_files.py:693` cmd_acquire（图记 :549，行锚漂移 +144，符号在位）
- `src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py:1549` `def claim_files(self, session_id, files, adopt_prior_work=False)`（图记 :1257，行锚漂移 +292；tracker #92 幂等基线语义在 INVARIANTS）
- `scripts/git_commit.py` --claim-only 前移协议（:315-317 与 --reconciler-verify 互斥校验实读）

### 2.5 门禁约束
- 联动门：CLAIM-REQUIRED（in_process 册在案，commit 时无 claim 阻断 exit 6）、FOREIGN-CHANGE-DETECTION（基线外判外来）、HELD-OVERLAP（他人持有阻断 exit 5）——三门均挂 C05 链，本环节是它们的数据源
- 热文件：`src/zephyr/shared/io/file_utils.py` safe_write_text（宪法 §1.13 CAS）

### 2.6 自动化触发
- commit 成功 finally 自动结算释放；失败自动保留+300s TTL 收窄（claim_retention 台账）
- 快照自动落盘：每次 claim 生成基线快照件

## 3. 自审闸三态

| 向 | 三态 | 依据 |
|---|---|---|
| 输入面 | pass | CLI/网关/adopt 三入口实存 |
| 输出面 | pass | .ailocks+claim_snapshots 959 件在产 |
| SSOT真源 | pass | 图/骨架/政策齐 |
| 代码模块 | pass | 三锚点实存（行锚漂移 +144/+292） |
| 门禁约束 | pass | 三门联动关系与图 exit 码矩阵一致 |
| 自动化触发 | pass | 结算/保留/TTL 全自动 |

## 4. 缺口与建议
- 【行锚滞后】两主锚行号漂移百级（高频演化文件），同 S02 建议：生成器重扫刷新或标快照日期。
- 【观测建议】claim_snapshots 959 件无 TTL 说明（store_refs retention=commit 结算即释放指锁；快照件自身清理策略未见），建议补快照件轮换口径。
