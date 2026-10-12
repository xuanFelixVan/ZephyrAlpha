---
ttl: task_bound
completes_when: 各承接方确认收到并各自入册；本班不在任何他班真源面上落码
session: st-fclean4-20261012
lane: wave4-main
role: 交接包（三张卡＋呈批面）
---

# 终清波四·交接与呈批（本班末笔，2026-10-12 夜）

> 铁律复述：本班在**任何他班真源面零落码**（撞件即撤，见 `22_` §1-②与 §2 末）；下列每条都带本班实测数与复算入口。

## 卡 A → 维护三班（`st-maint3-20261011`，你班今晨 20:50 仍提交、`worktree_drift_watchdog.py` 及其测件在你班暂存面 +99/−6）

| # | 事项 | 本班实测 | 你要做的动作 |
|---|---|---|---|
| A1 | **Q1 保留窗**：REDUNDANT 30d→7d | 数值无任何配置面（唯一读点 `:98`/`:545`；两门册 0 命中；`trae_085` 不带数；`data_retention_contract.yaml` 0 命中，正对照 18 条 INV-RET）；`git log -S` 证该常量自 `3429157b779` 从未改过且从未登记裁定 | 你的池面回退方向分量落定后，按 `22_` §2 预备改子加 `_QUARANTINE_REDUNDANT_RETENTION_DAYS=7`＋分类读册（**读不到 class 一律走 30 天＝保守**）；同步 `# [INVARIANTS] :8` 与 `architecture_issue_registry.yaml:3159` 散文＋补一条裁定。**前置**：A2 未落码时 Q1 是空转改子 |
| A2 | **清理器吃保护面**（统筹批为缩容硬前置） | `ops_guard_delete.jsonl` 内 1,502 条 drift 文件删除记 `verdict=ALLOWED ∧ is_protected_zone=true ∧ reason="reconciler 已声明 delete（声明制直通）"`；面从 7,434→6,480 枚由此而来 | 你主区工作区面那版 `reconciliation_registry.py`（+33/−1，含 `protected_skipped` 与 walk 剪枝）**尽快落袋**；落袋后请复跑本班留的红证用例（两条断言：保护区过期件存活＋`protected_skipped=1`，在旧码上必红） |
| A3 | **tamper 清单与自家 sweep 不同步** | `worktree_drift_watchdog.py:1151-1171` 只对 `known_quarantine` 名单判 `is_dir()`；`_sweep_quarantine`（`:543-544`/`:579-590`）删除时**不 purge 名单** ⇒ 现值 `quarantine_tamper` 234 条全是自家机制造的假警（该信号本为 #ARCH-264 O4 抓带外裸删而设） | 请并入你 M3/M5 那簇一起修（sweep 删除即从 known_quarantine 摘除，并留一行审计）；**在你这条修落地前，任何"按文件抽取"的 quarantine 去重都会稀释取证信号** |
| A4 | **`.runtime/tmp/rescue/<sid>` 是 24h TTL 面** | 本班 5 棵 needs_rescue 车道的未跟踪件被在册 `lane-archive` 移入此处（nightmine 249 项等）；同面另有 `docs/_working` 禁 `.json` 与清理器双重风险 | 非缓存件本班已复制进保护区并留 sha 册；**缓存类未跟踪件只活在 rescue 面**，本班判定可再生故未永久留存——若你判其不可再生，须在入袋后 24h 内搬家，过期不可追 |
| A5 | **guard_recycle 审计无会话署名** | 本班 149 条 `guard_recycle` 行 `session_id="ops-guard-unknown"`（未设 `ZEPHYR_SESSION_ID`） | 属主车道可考虑让 `guard_recycle` 在缺 env 时回落进程注册表 sid（与"写者必须署名"方向闸同向）；本班不自改你的门 |
| A6 | 承接波三那条（未闭环） | `st-dexp-20261009.json` 分片 JSON 损坏仍在（本班 21:35 复测＝`corrupt:JSONDecodeError`）；该车道今已被本班归档退场，退场时 `archive` 的 `unregister` 走的是它自己的片 | 请复核该片随退场是否已消失（现 `.runtime/session_registry/` 5 片，dexp 不在册）；**它那条移交单**（波三 `26_`）仍需你确认承接 |

## 卡 B → 周期班／影子续跑班

- M12 影子现值：day1＝1 个合格日（5 轮全 PASS），**最早转正日 2026-10-19**；转正与计划任务注册**同批呈**（现 54 支 `Zephyr*` 任务无一为 closeout，符合"影子期不注册"）。
- 跨轮比较口径固定＝`would_n ＋ new/gone 差集`（`would_set_sha256` 全等只在同日两轮之间合法）。
- 跑轮命令与四件合格判据在 `23_` §4；**禁加 `--execute`**；判活一律 `list_active_readonly()`。

## 卡 C → Owner／统筹 呈批面（本班权限外，全部只登记）

| # | 事项 | 本班能给的最强证据 | 不批会怎样 |
|---|---|---|---|
| C1 | `docs/_working/regsolo_campaign/99_delivery.md` 能否落册 | 其 `:155` 引 `ARCH-383` 号，而 `architecture_issue_registry.yaml` 内 0 命中、尾号止于 ARCH-382、PG 无 architecture_issues 表 ⇒ 波三判"门拦得对"，本班复核同判。正本在波三存证面＋本班保护区副本（sha 同值，已入 `evidence/aidrafts_fingerprint.yaml`） | 属主车道已亡（`st-regsolo-20261010` 今被本班归档）。要么授权"由维护三班补登一条 ARCH 条目并说明出处"，要么授权"改写该行"，要么判它"仅存证不落册"——三选一都需你点头，本班不自造条目、不改他班正文 |
| C2 | 取证窗深度（M5 实质前置之③之后）要动哪一把闸 | 两把闸实测：`audit_jsonl_writer.py:57` 50MB×`:62` backup_count=3 ⇒ ops_guard_delete 4.22d／feature_flags 0.21d 且在缩；且**轮转段名 `<f>.jsonl.<N>` 不被清理器豁免** ⇒ 深度被硬顶在 7 天以下，只提 backup_count 长不出 14 天 | 不裁定则"缩容 gate_audit/audit"无合法前置；且 A2 落地后仍会有"7 天天花板"残留 |
| C3 | 波三遗留 Owner 面维持不动 | only-copy 死信 1,425 袋/2.61GB、tmp C2 业务资产 49.88 GiB、两份未纳管明文密钥（其中 regsolo 那份随本班归档**少了一处明文副本**，主仓原件未动）、波二 C 件"照批清"批文原话未验 | 同波三陈报，本班未扩面 |
| C4 | **Q2 结论＝负结果**（去重在本面结构性不成立） | 原型 149 件/2.99MB 全等归档→放量 405 件/12.97MB→测得 135 枚空壳＋约 398 处悬空空子目录（400 处全在本班触过的 427 枚目录内，未触目录仅 2 处）→**整批回滚**并复验：审计表 8,072 行**全部在位且 sha 全等、空壳 0、回收站 0 件** | 若要继续 Q2，须改按**整枚目录**去重＋先修 A3；本班判断"按文件抽取"不划算，已把这条写进 `22_` §3 供你复核 |

## 本班自犯汇总（供周审计，明细在各册）

1. M2 mutating 死判前置证明与执行隔 45 分钟未复测（`21_` §3）。
2. Q2 放量用 8 分钟前快照算配额 ⇒ 造出 135 枚空壳（`22_` §6-1）。
3. Q2 自检尺 `rglob('*')` 把空子目录计入 ⇒ "0 空壳"假绿（`22_` §6-2）。
4. `guard_recycle` 未带会话署名（`22_` §6-3）。
5. 曾把 5 枚运行态件双写进 `docs/_working`（DCR 禁 `.json`），当窗自纠撤回（`21_` §4）。
