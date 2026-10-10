---
ttl: task_bound
owner: st-maint1-20261010
campaign: 维护一班（T3 收口 + 本班终局账）
---

# 维护一班终局账（T3 收口版，2026-10-10 夜批复后）

本件同时承担两职：①T3 写码车道 `st-maint1-t3lane` 的施工台账（原缺）；
②本班终局账第十节（原写在各班 00_ledger.md 上，落 dev 时因"两侧皆改"三方冲突
死信回人工；此处按 dev 现值重 derive 为独立新件，避免再撞同一冲突，
并取代车道分支 5c49b5f5 上的那份未落地内容）。

## 一、T3 判据与落点（实测行号）

三证旁证立法：**PID 亡＝必要非充分**。`session_concurrency.py`
`collect_alive_side_evidence()` 三证＝①心跳文件新鲜（90s 窗内 **且末行 status!=exited**
——在册铁律：exited 只证守护进程死不证会话死）②该 sid 在 pending/processing 有
900s 窗内的袋 ③分支 ref 提交时刻在 900s 窗内（**只读 refs，禁 index mtime**：
`git status` 会回写 linked worktree 的 index，观测即污染观测对象）。
三处判死轨同批受闸：`_is_session_alive`（pid>0 亡支）／
`_salvage_takeover_ledger`（`_pid_dead` 单独不得 `write_takeover_entry`）／
`liveness_verdict`（P1 TAKEOVER-PENDING 与 P4 PID-DEAD 判死前必须消费心跳旁证）。
阈值零新增（90/900 复用既有常量）；读不到证据=无正证（不新增判活通道，也不把读失败
当活证）；回退手柄 `ZEPHYR_ALIVE_SIDE_EVIDENCE=0` 整轴停用=逐字回到修码前行为。
写侧零变更：`list_active` 加 `mutating` 形参并新增 `list_active_readonly()`，
缺省副作用面一字不改（72 处调用方依赖）。
立案侧 `session_takeover_ledger.py` 的 `death_evidence` 增 `alive_side_evidence` 字段。

## 二、那条"真红"的归因更正（我一度据此刹车）

`tests/gov/session/test_session_concurrency.py::...::test_logical_request_exempt`
- **不是 T3 引入的**：同一测试在 dev 基线（主区、不含 T3 改动）上**一样红**，
  且 `git diff` 显示 T3 车道**零行触碰 logical**。对照基座复跑＝在册判据。
- 真因＝**测试夹具自相矛盾**：本例意图是"chief/总包 keepalive 不受限流"，
  却用非 chief 形态 sid `sess-guard-4`，于是先被 W-29 防伪造闸
  （`_verify_chief_form` 失败 ⇒ logical=True→False，`session_concurrency.py:709`）
  降级，限速豁免面根本没被测到。
- 实测对照：chief 形态 sid（含 `_CHIEF_FORM_TOKENS` 之 `chief`）首注与重注
  `logical=True` **都保住** ⇒ 限速豁免语义本来就正确，无需改生产码。
- 处方＝修夹具（改 `sess-chief-guard-4` 并断言首注即 True），
  **并新增反向钉桩** `test_non_chief_logical_request_downgraded`
  钉住"非 chief 请求 logical 必须降级"——防止我把这次修正变成放松门禁。
  未动任何判据阈值，未放松任何闸。

## 三、验证

- T3 会话族：`tests/gov/session/`（排除基线本就 collection 炸的
  `test_session_conflict.py`，其 `ModuleNotFoundError: zephyr.orchestrator.lifecycle`
  属存量面，该目录主区仅剩 `__pycache__`）**全绿**；
- 新红证 `test_takeover_pid_false_positive.py` **16 例全绿**；
- 夹具修正单独放到 dev 基线上复跑亦绿 ⇒ 证明不依赖 T3 才绿。

## 四、本班 T1/T2 的验收终态（随批复①②③④收线）

| 批复 | 终态（实测） |
|---|---|
| ① 运行面收口 | 主区那两份"比 HEAD 旧的未提交字节"状态码为 `M `（已暂存且工作树与 index 一致），即**暂存区里装着会把两项修复删回去的整档旧快照**＝在册"整树回退炸弹"形态。回退源已指认：baseline=历史提交 `d615…`/`d625d93961` 整档版本，recon=`41fe98b49e` 整档版本。处置：先存证（未提交字节 git 侧不可恢复）→ 零在飞 claim 核账（9 个活跃会话 held_files 命中=0）→ 从 HEAD 刷新 → **belt daemon 换码重启**（旧实例 53724 起于 19:17:20、早于刷新故 import 旧码；新实例 **pid=54448 / 20:27:20**，唯一实例）→ 复跑验证：主区 import 面两修复均在岗、同签名"顶层键缺失"最晚仍是 **13:14** 之后零新增、三口径册面健康、PG v>=178 空上下文版数=0 |
| ② T3 做完 | 夹具归因更正见上；T3 入袋（本件为随袋台账） |
| ③ 夜矿不代投 | 遵令，交回属主 st-nightmine2：`00_final_report.md` 整文件三方真冲突（两侧皆改），须以其 dev 现值重 derive；本班未动其内容 |
| ③ 宪法行政袋代投 | **已落 dev**：三证齐（注册表 `get_session`=None／无心跳文件／分支最后提交 12:33:42）；sha 对账两枚 MATCH（`7455bde9…`12695B／`8a8b005b…`4055B）；字节取自队列 blob 原快照并双抄 `.runtime/quarantine/maint1_constland_safety/`；归属注记"代投自死袋 blob"，`created_by` 仍归 st-constland-20261010；袋内第三件（账本投影）故意不带——落地内容由 PG render 决定 |
| ④ T5(c) 撤令 | 遵令撤销。双证在册：`description_cn` 在 `nodes_metadata` 25 列中；`design_note` 全仓零写面、`git log --all -S` 空。若后续有 dry-run 报错原文再重立 |

## 五、仍挂账的呈批面（未动，理由随条）

P-1 账本测试残渣 9 行（`sess-A`/`s`，七路径盘面与 dev 双双不存在）——属 §9.6 测试隔离
一类病灶，建议注册表车道建"孤儿 token 清扫"机械判据统一清（零散退役会被
`reconcile_registry` 的复活优先分支从其他车道盘面再灌回）。
P-2 REGISTRY-YAML-PARSE 自身零审计静默出口（`registry_yaml_parse_gate.py:364-365`
早于 `:385 _audit`，own_scope 筛空时既放行又不留一行）——改它=改审计面语义，交门主车道。
P-3 `commit_queue.py:1921 _session_ghost_dead` exited 短路：govjudge R9 修复只活在死车道
index，未落 HEAD——该文件属死信三期在飞域，本班禁改。
P-4 **T4 今晚两次亲身命中**：门吃 `git show :<册>`（index）与 HEAD 投影，意图 API 只写
盘面。已验证绕行＝投袋前①车道 `git checkout dev -- <册>`（私有 index，不污染共享面）
②`git add` 自己路径使 index==盘面。治本处方＝CREATE-GUARD 预检加 PG 账本第三读取源
（`REG-CAPCAN-001/creation_tokens/entry_key=file=<路径>|token=<token>` 复合键），
但必须同批带"账本不可达即 fail-closed 退回投影口径"的红证，否则变成新的静默放行面。
P-5 `ruling_registry.yaml:3543` 裁定#436 教了不存在的参数 `--verify-landed`
（实现只有 `--no-verify-landed`）。

## 六、T3 提交面残余闸（本班最后一次尝试的实况与解锁配方）

T3 内容与验证均已完成（§一～三），但**尚未落 dev**，卡在提交通道的三道闸连环，
与代码质量无关：

| 闸 | 现象 | 性质 |
|---|---|---|
| SESSION-REQUIRED | t3lane 的注册条目反复判死；其 heartbeat daemon 建道 >1800s 已 idle 自退，单 `register(pid=0)` 救不回 | 正是 T3 要治的病（在册铁律：短命进程须 pid=0；守护自退后需重拉守护而非只改注册表） |
| CREATE-GUARD | `01_final_account.md` 的 token **已在 PG(v182)、已在盘面、已在 index**，仍判"无 token" | 即 P-4/T4 本体，第三度亲身命中 |
| HOT-FILE-BASE-FRESHNESS | 本车道基底落后 dev，携册提交被拦 | 基底同步问题 |

解锁配方（顺序敏感，接手班照此三步即可，约 10 分钟）：
1. 车道内 `git merge dev --no-edit`（把基底对齐 dev；车道私有 index，不动主区）；
2. 车道内 `python scripts/governance/registry_projection/registry_projection_generator.py
   --render --registry-id REG-CAPCAN-001 --physical-path <CAP册> --project-root <车道>`
   使**车道盘面/index/HEAD 三处同源且含 v182 的 token**，随后先把该册单独提交入车道 HEAD
   （commit message 带 `[allow-mass-deletion:键序归一口径伪影+双口径零丢失]`）；
3. 再 `git_commit.py --session <活车道sid> --files <五件> --allow-multi-domain --enqueue`。
   注：五件＝session_concurrency.py / session_takeover_ledger.py /
   test_takeover_pid_false_positive.py / test_session_concurrency.py / 01_final_account.md。

存活面（四处，字节已核）：`st-maint1-t3lane` 工作树、`st-maint1-20261010` 工作树、
`.runtime/quarantine/maint1_t3_deliverable/`（本目录，双抄）、以及本件正文。

## 七、批复③ daemon 双实例——根因不是"该杀哪个"，是看门狗时钟口径不同源

实测（2026-10-10 20:5x，主区真心跳）：

| 项 | 值 |
|---|---|
| 心跳写侧 `wall_ts` | `1791637069.43`（= unix `time.time()` 秒） |
| 真实年龄 | **6 秒**（阈 600 ⇒ 应判活） |
| 看门狗 Stage 1 算式 | `[DateTimeOffset]::UtcNow.UtcTicks / 1e7 - [double]$j.wall_ts` |
| 该式算出的 age | **62,135,596,806 秒**（≈1969 年） |

`.NET UtcTicks/1e7` 是"自 0001-01-01 的秒数"，与写侧 unix 秒**不同源** ⇒ age 恒越阈值 ⇒
Stage 1 永远判死 ⇒ 转入 Stage 2（CIM，负载下可空返回）⇒ **每分钟 spawn 一个重复 daemon**。
这正是 `belt_watchdog.ps1` 文件头自己警告的 pileup disease（历史上堆到 6-8 个）。
当晚实测到 20:27 / 20:52 / 20:57 三波新实例，与"每分一次"完全吻合。

处置（按批复"禁盲杀"）：**先修口径，不动实例**。锁与心跳当前都归
pid=54448（20:27:20 起，含本班全部修复），重复实例因拿不到
`.runtime/commit_queue/belt_daemon.lock` 而无写权，属 churn 而非双写。
修后看门狗 Stage 1 会正确判活，spawn 自然停；已存在的多余实例待其自然退出即可，
无需人为 kill。

红证 `tests/gov/infra/test_belt_watchdog_clock_unit.py`（4 例）：
①主案断言 age 必须 `ToUnixTimeSeconds` 且不含 `UtcTicks`——**在未修的主区副本上实测红**，
失败原文即那行 `$age = [DateTimeOffset]::UtcNow.UtcTicks / 10000000.0 - [double]$j.wall_ts`；
②同式复算当晚两个数，钉住非理论推测；
③**反向钉桩**：age 599→活、601/7200→死，防我把"修口径"变成"永不 spawn"的新洞；
④跨侧对账：写侧确为 `time.time()`，若写侧改用单调钟本测试即失效报警（防止只修一侧）。
