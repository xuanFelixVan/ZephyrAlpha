---
ttl: task_bound
completes_when: X01 处方 P1（HEAD∪盘面并集口径）落地或移交方签收
created: 2026-10-07
---

# X01 立案：creation_token 三方口径矛盾（预检"已登记" vs 落地 CREATE-GUARD 拦）

> 立案：st-mastertc-l1（L1 治理A），2026-10-07 总包夜战。处置=立案+处方落档销账，移交 **L3 提交链 / 维护班** 施工。本卡不改代码。

## 一、症状（三方口径各执一词）

| 方 | 判定点 | 读的信源 | 答案 |
|---|---|---|---|
| A 预检工具 `scripts/governance/d3_metadata/batch_creation_tokens.py` | 登记前查重 `scan_unregistered`→`load_registered()`（L96-111） | **主区盘面** registry（`_REGISTRY.read_text`） | "已登记"→跳过登记 |
| B 落地门 `src/zephyr/gov_enforcement/commit_gates/create_guard.py` `_load_capability_registry`（L733-） | commit 时 token 精确比对 | **主区盘面** registry（`anchor_main_root` 锚定，裁定#480 手术③）+ fail-closed | "未登记"→硬阻断 |
| C HEAD `git show HEAD:docs/01.../capability_canonical_file_registry.yaml` | 持久真源 | git 对象库 | 条目在/不在（双方都不读它做成员判定） |

矛盾形态：A 在 T1 读盘面答"已登记"（不再登记）→ 并发窗口内盘面条目被蒸发 → B 在 T2 读盘面答"未登记"→ commit 硬拦。开发者视角="预检说有、门禁说没有"。

## 二、根因：并发 stomper 战 + 成员判定读 stale 盘面基

1. registry 是热文件：多会话各持自己基底做 read-modify-write，写者 A 的基底缺写者 B 刚落的条目 ⇒ B 的条目被 A 的写**蒸发**（stomper 战）。queue serializer 落地链 reset 到 dev 基底同样会回写旧盘面。
2. `create_guard._load_capability_registry` 虽经裁定#480 手术③把读点从 session worktree 锚回**主区盘面**，但主区盘面仍是 stomper 战战场——它锚定了"哪块盘"，没锚定"哪个时点的真相"。fail-closed 只保证读不到时阻断，不保证读到的内容是登记时的内容。
3. `batch_creation_tokens.py` 的 B22 写前/写后闸（对照 HEAD 防净删）**只防本工具自己**把蒸发固化；它 `load_registered()` 的"已登记"判定同样吃盘面，不读 HEAD 成员集。
4. 三方没有一个共同时基：盘面@T1（A）、盘面@T2（B）、HEAD（持久真相）。

## 三、治本处方（移交 L3/维护班，按优先序）

P1 **成员判定改 HEAD∪盘面并集口径**（处方主线，本卡裁定背书）：
- `create_guard._load_capability_registry` 载体不变（解析/fail-closed 语义不动），token 成员判定处并集 `git show HEAD:<registry>` 条目集 ∪ 主区盘面条目集。HEAD=append-mostly 持久真相（进了 HEAD 的登记不可被盘面蒸发否定），盘面=在途未提交登记。并集方向**只宽不窄**（不比任一单面更严），保留"两源皆不可达→fail-closed"。
- `batch_creation_tokens.py` `load_registered()` 同口径（HEAD∪盘面），使预检与门禁答案机械一致——三方坍缩为两方且恒等。
- 反向面（登记是否真落）：保留 B22 双闸不动——它管"本工具写出后不净删"，与成员判定正交。

P2 **热册写入统一 safe_write_text+CAS**（宪法硬规则 13 已立，巡检该 registry 落地情况）：CAS 失败即重读重写，从源头压缩 stomper 窗口。

P3 **盘面蒸发侦探**（可选，维护班）：`block_flip_eligible` 同款机读审计——登记工具写后 5s 抽查盘面条目仍在，蒸发即记 `.runtime/gate_audit/creation_token_eviction.jsonl`，为 stomper 战定量取证。

## 四、验收判据（给施工方）

1. 复现用例：tmp_path 双写者——T1 盘面登记 X → T2 他人从无 X 的基底整写盘面 → commit 携 X 新文件必须过（HEAD∪盘面口径下 X∈HEAD 或 X∈盘面任一即放行；两处皆无仍硬拦=负例不放松）。
2. 预检与门禁同一夹具下答案恒等（参数化对拍）。
3. 现有 CREATE-GUARD 全套测试绿，fail-closed 面不回退。

## 五、移交与销账

- 移交：L3 提交链车道（commit 面归口）或维护班（夜间窗口后）。
- 本卡（X01）以立案+处方落档销账，不改代码；Owner 晨会可凭本档派工。
- 关联：裁定#480 手术③（worktree 锚主区）、#ARCH-324（approval_resolver 先例）、宪法硬规则 13（safe_write_text）。
