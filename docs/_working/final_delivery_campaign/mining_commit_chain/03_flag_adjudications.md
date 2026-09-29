---
ttl: task_bound
title: "提交链三 flag 证据链复核与裁定建议（immutable_tree / gate_result_cache / regen_scope）"
session: st-finaldel-m1-20260929
---

# 03 flag 裁定卷（Q4：现值+证据链+一键命令+回滚+裁定建议）

> 现值核对于 2026-09-29：`config/flags.yaml` 工作树==HEAD（git status 干净）；读取语义=直读 YAML（每次调用生效，翻/回滚均**无需重启**任何进程）。

## 一、总表

| flag | 现值（工作树/HEAD） | 接线真源 | 出厂/翻转史 | 裁定建议 |
|---|---|---|---|---|
| `git_operations.immutable_tree`（S1） | **true**（已生效） | `git_commit_gateway.py:219-235`（直读）→`:3076` 门禁链跑 CommitTreeView；15 台全索引门分道 `_tree_view.py:115-133` | 出厂 OFF（4a977608d70 接线）→ 09-26 Owner 批 → ed935c29afd 翻 ON（09-27 00:10） | **无需再裁（已生效）**；补一条 R2 复测留档后闭卷 |
| `gate_result_cache`（T7 键隔离随之 live） | **enabled: true**（production） | `gate_cache_preflight.py:212/305/330`（新键）；门控=P2⑧ 本 flag 单点 | 2026-09-12 Owner 批转正 ON；T7 换键两 commit（df8507ac9b 主体 + cb3c13b74f8 收口）**未动出厂 flag**（两 flag 正交声明在模块 docstring） | **保持 ON**；需补一项翻后复测读数（见 §三） |
| `git_operations.regen_scope` | **"any_worktree"**（未翻） | `scripts/governance/git_hooks/post_commit_regen_yaml.py:131-142` 读、`:310-311` 消费（main_only=worktree 语境只记账不 spawn，记账 P-3 先行已落） | 出厂 any_worktree；M2/T5（批六 ce0dc360b8c）代码就位；翻转=Owner 门位（flag 出厂翻转=high tier） | **可翻（低风险）但非提速杠杆**；建议随 P0/P1 落地后按净零评估，不阻塞 |

## 二、immutable_tree（S1）——已翻转，验收链全绿

**证据链**（全部在案可复核）：
1. 判据达成：`90_verification/s1_acceptance_20260929.md`——`replay_gate_verdicts --since 30 --all`：30 笔×100 台×2 口径=6000 verdict 行，verdict/hits/detail 三维 **100/100 台零漂移**；随 index 规模漂移绊线（612 文件真实共享 index 复刻）不存在；读面收益 own 10.9s vs shared 77.9s = **7.1x**。
2. 安全网自证：selfcheck100（`.runtime/tmp/csx_replay_selfcheck100/selfcheck.json`）=commits 100/files 1522/byte_mismatch 0/worktree_reads 0。
3. 实效：门禁链 P50 64s→**15.6-18.5s**（9/26-27 `gate_execution_stats.jsonl`），达成"<25s"验收目标。
4. 翻转授权：commit `ed935c29afd` message 明记"Owner 09-26 已批准"，系 Owner"全部批准"裁定项①执行件。

**一键命令与回滚**（真源=commit ed935c29afd message + flags.yaml `:49-52` 注释）：
- 翻转/回滚均为 `config/flags.yaml:52` 一值改写（必须 `safe_write_text` CAS，`src/zephyr/shared/io/file_utils.py`），格式：`immutable_tree: true ↔ false`；"回滚=同词反向 replace"（commit 原文）。直读语义=改完即生效，无重启项。
- 注：99_FINAL_REPORT §三.1 与快照 §十三 指向的"快照 §十二 一键命令"在快照文件中**实际缺节**（§十一 直跳 §十三）——翻转命令的真实在案载体即上述 commit message 与 flags.yaml 注释，本卷为补漏归档。

**裁定建议：已生效，闭卷路径=R2 复测**。R2 判据建议：重跑 csx_deep 全集时增读一行"门禁链 p50 连续两日稳定 <25s 且 verdict 漂移告警=0"即可销项；无任何回滚动作建议。

## 三、gate_result_cache（T7 键隔离）——生产 ON+新键 live，欠一张翻后读数

**现值语义澄清（防接力误判）**：快照 §七"T7 flag 出厂 OFF"指施工时点不改任何出厂 flag；T7 新键**没有独立 flag**，它直接替换 P2⑧ 缓存的键公式，随 `gate_result_cache: enabled:true`（2026-09-12 转正，已生产运行 17 天）即已生效。两 flag 正交声明：`gate_cache_preflight.py:49-55`（"缓存启停只归 P2⑧ gate_result_cache，本批不改任何出厂 flag"）。

**证据链**：
1. 键公式（HEAD）：`(gate_id × own_scope × own_content_sha × spec_sha × manifest_inputs_sha × flags_mtime)`，**禁含 head_sha/staged_tree_sha**（`gate_cache_preflight.py:25-55` docstring+`:330` 实装）——"任何人暂存/任何人推进 HEAD 就作废所有人缓存"（24h 87 命中的结构病根）已拔。
2. 判失红测：`tests/git/test_gate_cache_key_isolation.py`——逐字重建旧键公式证明"他人提交推进 HEAD ⇒ 旧键必 miss+新键同场景命中"；门源码一字节/注册表字节篡改 ⇒ 下次必 miss（spec_sha/manifest 机制，`cb3c13b74f8` ①）。
3. 白名单 15 台全实证准入（复用面 10 台+耗时面 5 台，24h 窗 114 链次量取；退役 3 台零触发零消费死条目）；注册表读取类准入的机械前置 `GATE_INPUT_MANIFEST` 已建（现空置，top15 全纯 staged 扫描器）。
4. 测试面：19 绿（13 preflight+6 判别）。
5. 回滚通道（flags.yaml `:101` 原文）："flag OFF+删 `.runtime/gate_cache/`"，永久有效。

**欠账（需补证据）**：B2 原判据"cache_hit 87/24h → >1500/24h"**翻后（新键 live 后）无复测读数在案**——`preflight_events.jsonl` 只有 passed/blocked 两事件（本卷实测），cache_hit/preflight_reused 计数应从 `gate_execution_stats.jsonl` 字段读；建议总筹补一行 24h 读数（T7 落地=2026-09-26 后任意满窗日）即可闭环。

**裁定建议：保持 ON（可翻转→已处于推荐态）**；补读数一项（15 分钟工作量）；白名单扩面（A4 阶梯 S2 曾设想 14→86 台）**不建议一次性扩**——按模块既定纪律"追加 MUST 附同窗实测数据+逐台输入面分析"（`gate_cache_preflight.py:100-101`），逐批实测准入。

## 四、regen_scope——可翻（低风险），但非本战役提速主杠杆

**证据链**：
1. 消费点唯一：`post_commit_regen_yaml.py:131-142`（读 flags `git_operations.regen_scope`，缺省 any_worktree）+ `:310-311`（main_only 且 worktree 语境→只记账 return 0，不 spawn）。
2. 安全性：M2/T5 意图账先行（P-3：无论 spawn 与否先落账，`:297-306`），翻转只抑制执行不丢意图；锁/账/产物根已钉主区（P3 批，ce0dc360b8c）；4×97.3 CPU-s 爆发已由 T5/M2 消除——**即翻转的边际提速收益已被前置批吃掉大半**。
3. 翻转/回滚：flags.yaml `:48` 一值（`"any_worktree"` ↔ `"main_only"`，safe_write_text）；回滚=改回。注释明示"翻转属 Owner 门位（flag 出厂翻转=high tier）"。

**裁定建议：可翻转（建议批，低风险），但排序放 P2**——它是 Owner 门位动作而非施工件；对提交链 P50 无直接影响（worktree post-commit regen 已不占提交临界区），收益面=workers worktree 内的 spawn 负载与 24h CPU。建议与 Rx-1/Rx-3 落地后的 R2 复测同窗翻转，一次留档。

## 五、给总筹的两行呈报

1. 三 flag 中两件（immutable_tree、gate_result_cache 新键）**已是生效态**，呈报清单（99_FINAL_REPORT §三.1/§三.2）应更新为"已执行/已 live"，避免下个会话重复走 Owner 门位；唯一待裁=regen_scope（可随 R2 同窗）。
2. 快照 §十二 缺节（翻转命令指针悬空）由本卷 §二/§三 补漏归档；后续 flag 操作一律以 flags.yaml 注释+commit message 为命令真源。
