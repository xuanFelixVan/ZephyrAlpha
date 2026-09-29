---
ttl: task_bound
---

# 红蓝对抗报告——提交链治理组场景④⑤⑥（2026-09-25，车道 csx-s1）

执行仓：worktree `.worktrees/csx-s1`（基底 90f7a215b5）。全沙盘（tmp_path 一次性仓 + tmp 队列根），
未触生产 `.runtime/commit_queue/`、主区 index、生产钩子。证尺：`tests/governance/test_redblue_governance.py`
（23 测试），红证三查 + 内嵌剥钩红证两组，全部先证能红后钉绿。

## 一、结论速览

| 场景 | 攻面 | 判据 | 结果 |
|---|---|---|---|
| ④a | 三伪造形态直打 reference_transaction_guard.sh | 全部 exit 1 或落审计 | **收紧后达标**（详见红发现 R1） |
| ④b | commit-tree+update-ref 绕 pre-commit | hook 链必须拦 | ✅ 拦截生效；剥钩红证同形必落 |
| ④c | [GW:sid:emergency] 逃生道 | 放行但落审计 | ✅ 放行+unregistered_gw_sid 审计；剥钩红证零审计 |
| ⑤ | GateResultCache 投毒与失效（T7 键=own blob sha） | a-e 五态 | ✅ 5/5（own 变 miss/他人动 hit/mtime 变 miss/畸形返 None/TTL 过 miss） |
| ⑥ | 超顶大批与队首饿死（120 件 < 扫描界 400） | B4 FIFO/B5 退避 | ✅ 4/4（最老件胜出/interactive 不饿死/machine 饿死逃逸双向在位/attempts 退避让位+off 态钉档） |

回归面：新套 23 + 孪生既有 22（marker_forgery/reference_tx_m3/no_verify_threshold）+ 缓存与队列
既有 55（gate_cache_key_isolation/preflight、b5_backoff/base_head/ghost_pending）＝ **100 passed**
（`PYTHONPATH=src`，`python -m pytest`，basetemp `.runtime/tmp/csx_rb_g_bt`）。

## 二、红发现与处置

### R1（本车道收紧落地）冒充在活他人 sid＝静默放行（原三形态中唯一既不 exit 1 也不审计）

- **复现**：bash 直跑 ref_tx guard、合成 stdin `<old> <new> refs/heads/dev`，message
  `[GW:st-csx-victim-lane]`（victim 为注册表内**在活他人**会话），无 GW env、非 emergency。
  收紧前实测：**rc=0、零审计**（红证 A：stash 收紧后重跑 `s4a3` 必红）。即任务口径
  "全部必须 exit 1 或落审计" 对第三形态不成立。
- **定性**：即 reference_transaction_guard.sh / post_commit_guard.sh ★ 段已登记的残余风险②
  （判据是 sid ∈ 会话键，不是 sid == 本笔归属），此前"已登记交总包裁定"但静默面未收窄。
- **处置（warn_only 收窄，不越权断归属）**：两孪生脚本同批加"通道不可证"分支——sid 全部已注册
  但进程无 `ZEPHYR_COMMIT_GATEWAY=1`、message 无 `:emergency]`、无队列 `:q-` 标记 → 落
  `violation=gw_sid_channel_unverifiable` warn_only 审计后放行（不改变任何阻断语义）。通道三豁免
  与合法通道逐一核过：gateway/session_worktree（env 注入，gateway.py:3316、session_worktree.py:3859）、
  emergency_commit（commit_tree 逃生，另有三重留痕）、队列落地（`[GW:{sid}:q-{qid}]` 标记，
  commit_queue_landing 自带留痕）。孪生同步义务履行（两脚本同段同语义）。
- **残留（如实登记，勿宣称"不可伪造"）**：攻击者伪造 env 值或仿冒 `:q-` 标记形状仍不可检；
  归属级治本（commit 可验证载体/HMAC 尾签）仍待总包裁定。
- **回归钉**：`test_s4a3_*`（断言 exit 1 **或**审计，未来升级硬拦仍绿）；`s4a1/s4a2`（未注册 sid、
  注册表字段名当 sid → exit 1+block 审计）。

### R2（既有病根复核，无新动作）

④b plumbing 绕过、④c emergency 审计、⑤ 键隔离/失效矩阵、⑥ B4/B5 调度——HEAD 判据全部在位。
判别力以三查红证背书：

- **红证 A**：回退钩子收紧 → `s4a3` 红（rc=0 零审计）。
- **红证 B**：`GateResultCache._path` 键临时掺回 `staged_tree_sha`（复现 T7 前的全局敏感键）→
  `s5b` 红（他人 index 活动逐出 own 缓存）。
- **红证 C**：`_HEAD_SCAN_BOUND` 临时 400→64 → `s6a` 红（120 件中最老件不可见，字典序短路复活）。
- **内嵌剥钩红证**：`s4b2`（剥 reference-transaction 钩子后同一 bypass 必落地）、`s4c2`（剥钩后
  emergency 落库且零审计）——证明拦截/审计出自钩子本身，尺有判别力。

## 三、逐场景明细

### 场景④（9 测试）
- `s4a1` 未注册 sid：bash 直跑 rc=1 + "伪造 GW 标记" stderr + `action=block` 审计落盘。
- `s4a2` 注册表字段名当 sid（pid/held_files/last_heartbeat/session_id 四参）：全部 rc=1。
- `s4a3` 冒充在活他人 sid：收紧后 warn_only 审计（violation/session_id/action 三字段断言）。
- `s4b1` 无标记 commit-tree+update-ref（不带 old=假 creation）：hook 链 rc≠0、分支零推进。
- `s4c1` 未注册 sid + `:emergency]` CAS 快进：放行 + `unregistered_gw_sid` 审计。
- `s4b2/s4c2` 剥钩红证两组。
- 正控不打死：`test_git_hooks_marker_forgery.py` 11 例全绿（合法网关尾注/文档性提及/真回退/合法 CAS 落地）。

### 场景⑤（5 测试，GateResultCache，tmp 仓 tmp 缓存目录）
- `s5a` own staged 内容改（投毒逆命题：改后即应 fail 的内容）→ miss。
- `s5b` 他人向 index 连塞 3 文件（内证 `write-tree` 全树 sha 必变）→ 仍 hit（键隔离）。
- `s5c` flags.yaml mtime +5s → miss。`s5d` 缓存 JSON 四种畸形（非 JSON/缺 ts/ts 非数/ts=null）→
  lookup 恒返 None 不崩。`s5e` ts=-601s → miss、ts=-100s → hit（界内对照，证 miss 出自 TTL）。

### 场景⑥（4 测试，tmp 队列根，120 件 pending，直测 `cq._pick_head`）
- `s6a` 119 新鲜件 + created_at 最早件（qid 字典序垫底、扫描名单最后）→ 最老件胜出（B4 FIFO）。
- `s6b` 1 interactive（最老）+ 119 machine 洪灌（最老 machine 149s < 30min 饿死线）→ interactive 优先。
- `s6b2` 双向护栏：唯一 machine 件 1900s > 30min 饿死线 → 即便有 interactive 仍放行 machine（不反向饿死）。
- `s6c` attempts=4 毒药件（24h 前居队首）+ 119 正常件 → 退避让位、正常件间 FIFO 保持；
  `s6c2` env `ZEPHYR_CQ_ATTEMPTS_BACKOFF=0` → 回退 created_at FIFO（off 态钉档）。

## 四、产物与改动清单（全在 worktree，未提交）

| 文件 | 动作 |
|---|---|
| `tests/governance/test_redblue_governance.py` | 新建（23 测试：④9/⑤5/⑥4+场景间夹正控） |
| `scripts/governance/git_hooks/reference_transaction_guard.sh` | 收紧：注册 sid 通道不可证 → warn_only 审计（③号静默面收窄段） |
| `scripts/governance/git_hooks/post_commit_guard.sh` | 孪生同步：同语义分支（全部已注册 → exit 0 前置审计分支） |
| `docs/_working/commit_speedup_campaign/70_redblue/redblue_governance.md` | 本报告 |

`src/zephyr/gov_enforcement/rule_bridge/gate_cache_preflight.py` 与 `scripts/commit_queue.py`
仅红证 B/C 临时改动，已逐字节还原（git diff 空）。

## 五、未尽事项

1. **归属级治本待裁定**：`[GW:<victim>:q-伪造qid]` 形状仿冒与 env 伪造仍不可检；治本需
   commit 侧可验证载体（HMAC/note 尾签），维持 ★ 段"交总包裁定"原判，本车道不擅动。
2. post_commit_guard 的 warn-only 审计走 `post_commit_guard_*.json` 且
   `violation=gw_sid_channel_unverifiable`，**不进** no_verify_threshold 的
   `unregistered_session_id` 计数（有意——阈值升级语义勿混）；是否为其单设高基数监控，
   留总包定夺。
3. 场景⑥为调度面直测（`_pick_head` 单元级）；120 件端到端 drain 全链（landing 池化路径）
   未在本车道重放，由既有 b5_backoff/base_head/integration 套件覆盖。
