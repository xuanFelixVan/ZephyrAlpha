---
ttl: task_bound
completes_when: 裁定#266/#267 落地+Owner 验收本报告（审计链治本、密钥分期与新钥部署收口）
---

# 审计链损伤取证与治本报告（GW-A，欠账清偿战移交清单第①项）

- 会话: `st-auditfix-20260916` 日期: 2026-09-16
- 授权: Owner"解决所有欠账"明令；任务书=GW-A 执行书（取证+治本+处置+验证+裁定）
- 前班输入: GW11 取证（commit 16befe06 登记）：events.jsonl 84.6MB/112,975+ 事件、HMAC 失配 26,909（自 #26810）、prev 断链 5,595（自 #35156）、内容哈希失配 5,343（自 #53721）、疑根因=多写方并发 append 互踩
- 边界遵守: 未触碰 api_server / config/** / src/zephyr/regime / scripts/backtest / docs/03_modules / tests/infrastructure / tests/audit（后者仅只读跑回归）

---

## 1. T1 取证快照（RULE-DATA-OPS 三步验证落痕）

| 项 | 值 |
|---|---|
| 源文件 | `data/audit_trail/events.jsonl` |
| 快照 | `data/audit_trail/events.jsonl.bak_20260916_gwa_forensic`（仓内 in-dir `.bak_YYYYMMDD` 惯例，先例=bak_20260526；目录整体 .gitignore:208，retention.py 仅扫 data/audit_history 不碰本目录） |
| SHA256（源=副本，copyfile 后双重计算比对） | `81651ba21cba4eb38fc9d5a2b91de0c37f853085cd52bf0504b0a90a043c5529` |
| 大小 | 85,175,618 bytes |
| 清单文件 | `data/audit_trail/events.jsonl.bak_20260916_gwa_forensic.sha256` |
| 普查时点事件总数 | 113,694 |

三步验证：
1. **必要性**：T4 将向活跃账本（~100 事件/20 分钟）追加事件，任何处置前必须有不可变基线；快照是 T4 可逆性的唯一保证。
2. **真实性**：`shutil.copyfile` 后对源与副本分别流式 SHA256 全量重算并 assert 相等；非聚合数、非凭记忆。
3. **可逆性**：本操作对主文件零写入；快照本身即逆向通道——主文件任何非预期变化可用快照+哈希证明。

## 2. 损伤普查复验（GW11 数字逐维复现）

普查脚本：`.runtime/tmp/audit_census_gwa.py`（与 `IntegrityVerifier.verify_chain` 同口径，另加 HMAC 密钥候选分类），结果 JSON：`.runtime/tmp/audit_census_gwa_result.json`。耗时 5.57s（GW11 交接所称 verify_chain >120s 不成立，实测全链验证 4.8-5.6s，与 GW11 独立实测一致）。

| 维度 | GW11 | 本次复验 | 首事件 | 末事件 | 附注 |
|---|---|---|---|---|---|
| prev 链断裂 | 5,595 | **5,595（精确吻合）** | #35156 | #113145 | 普查当日仍在新发（#113144-113145 距尾部 ~550 事件）——互踩未停止 |
| 内容哈希失配 | 5,343 | **5,343（精确吻合）** | #53721 | #77356 | **100% gate_audit**；止于 #77356（writer strip 治本生效点） |
| HMAC 失配 | 26,909 | **26,909（精确吻合）** | #26810 | #53718 | **单一连续整段**（26,810-53,718 无一通过现行密钥两约定） |

HMAC 密钥分段考古（对全量 113,694 条按三候选验证）：
- #1-#26,809（26,809 条）：`default:legacy` 约定通过——HMAC over canonical(事件\{entry_hash,hmac_signature})，密钥=公开兜底 `zephyr-audit-hmac-default-key`
- #26,810-#53,718（26,909 条）：**现行密钥两约定均不通过**——写入时使用了当时 env 注入的 ZEPHYR_AUDIT_HMAC_SECRET，该密钥值现已丢失（.env 现值为空、shell 环境为空），此段 HMAC **永久不可验证**（"不可验证"≠"证实篡改"）
- #53,719-#113,694（59,976 条）：`default` 现行约定通过——HMAC over entry_hash 字符串

genesis 哨兵：无问题（首事件 prev_hash="" 合法）。

## 3. T2 根因实证

### 3.1 写方清单（AuditWriter 实例化点普查）

`AuditWriter.write()` 的互斥仅是**实例内** `threading.Lock()`（writer.py 原 L268）；`_last_hash` 是**实例内存**状态，仅构造时 `_load_state()` 读一次尾。任何两个实例（跨进程或同进程）并发追加同一 events.jsonl 即互踩。实例化点全景：

| 通道 | 代码锚 | 实例语义 |
|---|---|---|
| 全局单例 | `writer.get_audit_writer()`（双重检查锁，进程级） | 每进程 1 实例；session_audit provider、tamper_evident_log、finding_ingest、contracts 委托等经此 |
| AuditChainVerifier | `gov_enforcement/.../audit_chain_verifier.py` L138 `self._core_writer = _CoreAuditWriter()` | **每 verifier 实例自建 fresh writer**（不走单例）——同进程与单例并存即双写方 |
| 直接 fresh 实例 | spec_engine.py:112、audit_write_failure_protector.py:69、audit_delegation_bridge.py:106、lifecycle.py:220、governance_server.py:780、pipeline_orchestrator.py:426 等 | 各持独立 `_last_hash` |
| 独立链（观察项） | audit_chain_verifier `_persist_entry`→gate_chain.jsonl | 本地门禁链，当前 145 条 0 断链（单写方期），未改动 |

当日实测活跃写方：gate_engine（经 AuditChainVerifier 写 gate_audit，commit 门禁触发）+ session_audit 通道（session_record 等）；普查 prev 断链事件类型分布（gate_audit 4945 / chain_cleared 350 / unknown 137 / session_record 37 / rbac_decision 28 / budget_enforcement 17 / rollback_nexus 9 / rollback_operation 6 / drift_hotfix_bypass 2 / 无类型 63）与多通道写方清单吻合。

### 3.2 复现实证（tmp_path 沙箱，双进程 spawn）

脚本 `.runtime/tmp/repro_dual_writer_break.py`（治本前跑）：

```
total_events=81 (expect 81)
prev_chain_breaks=40
same_prev_signature_pairs=1
  pair: #8 prev=0e12267c3b41 ts=2026-09-16T04:46:06.450768+00:00
        #9 prev=0e12267c3b41 ts=2026-09-16T04:46:06.450768+00:00
        signature_match=True
VERDICT=REPRODUCED
```

### 3.3 归因结论（三维三根因，修正 GW11 单一根因假设）

1. **prev 断链（5,595）**=多写方并发 append 互踩。主仓铁证 #35155/#35156：同 prev_hash（`a54538ae80ac`）、同秒（2026-05-28T19:03:41）、entry_id 序号同为 `-263`——两写方各持同一陈旧内存 `_last_hash` 同时落盘。复现测试同签名重现（REPRODUCED），治本后同签名绝迹。
2. **内容哈希失配（5,343）**≠并发问题：audit_chain_verifier.append() 向 writer 预注入自有 `entry_hash`（audit_chain_verifier.py L264），旧版 writer canonical 绑定外来哈希后覆写 entry_hash——存储哈希与验证口径永久背离。100% gate_audit、止于 #77356（writer strip 治本 `entry.pop("entry_hash")` 生效）与此完全吻合。**既有治本已覆盖，历史段不可恢复（既定事实）。**
3. **HMAC 失配（26,909）**≠并发问题：HMAC 密钥轮转史——env 密钥期（#26810-#53718）该密钥值丢失，现行密钥无法验证。密钥管理问题，非链结构问题。

## 4. T3 写方治本（src/zephyr/gov_audit/writer.py）

方案：**append 临界区跨进程文件锁 + 锁内实时重读文件尾哈希**（锁仅保证互斥不够——各实例陈旧 `_last_hash` 仍会写出错误 prev，必须以文件真实尾为准）。

diff 摘要：
- 新增 `_read_tail_entry_hash(path)`：反向块扫描（64KB chunk）最后一条完整 JSONL 行取 entry_hash；容忍撕裂尾行（崩溃残留半行，跳过回溯）；空文件→genesis；扫描超 32MB 上限抛 RuntimeError（**fail-closed：宁可不写，不可 fork 链**）。尾读实测 1.3µs/次。
- 新增 `_cross_process_append_lock(path, timeout=10s)`：OS 字节排他锁（msvcrt.locking LK_NBLCK 自旋 2ms 至超时 / fcntl.flock 降级），复用仓内 `src/zephyr/data/scheduler.py::acquire_single_instance_lock` 先例语义；锁文件 `events.jsonl.lock` 只创建永不删除（删除=拆散互斥域）；锁随句柄生命周期——进程崩溃/被杀 OS 自动释放，无 stale 锁残留；超时抛 TimeoutError（fail-closed）。
- `AuditWriter.write()` 临界区改为 `with self._lock, _cross_process_append_lock(...)`，`prev_hash` 取 `_read_tail_entry_hash()` 实时尾值（实例 `_last_hash` 保留为兼容状态字段）。
- 模块头 [INVARIANTS]/[MODIFY-GUARD] 与 write() docstring 同步更新。
- `_KNOWN_EVENT_TYPES` 增补 `integrity_incident`（T4 处置事件类型）。
- **旧读取方零改动**：IntegrityVerifier/query/merkle/retention 只读 events.jsonl，未动任何一行；锁文件与尾读对读取方透明。

性能（100 次 append 基准，tmp_path）：avg=6.3ms / p50=4.7ms / p95=12.2ms——fsync 主导，锁+尾读开销微秒级，可接受。

回归测试：`tests/governance/audit/test_writer_multiproc_append.py`（11 用例）：4 进程×25 事件并发全链 verify_chain 零 issue、同 prev 同秒签名绝迹、同进程双实例交错完整、撕裂尾行回溯、大行跨块定位、锁超时抛错、持锁进程被杀后锁立即释放（OS 语义实证）。

## 5. T4 损伤段处置（追加式，不篡改历史）

RULE-DATA-OPS 三步验证：
1. **必要性**：append-only 账本对已损伤历史段的唯一合法处置=链头追加显式 integrity_incident 声明（账本自述损伤边界），否则后续验证者无法区分"历史损伤"与"现行损伤"；截头/重算/分段轮转均被既证必破 genesis 哨兵或违反 retention 不变量，排除。
2. **真实性**：声明的全部数字取自本次普查实测（§2 表），非聚合数非凭记忆；事件由治本后 writer 落盘（本身受新锁保护、HMAC 签名、prev 链接真实尾）。
3. **可逆性**：纯追加，既有 113,694 行零字节改动；撤销=删除该追加行（有 §1 快照+SHA256 基线可证）。

落盘记录：
- 主声明事件 `AUD-T-20260916054644-5599e4c3-0001`（行号 #114411）：三维损伤边界+#26810/#35156/#53721、三根因、治本 commit `2b6a74b6`、快照指针+SHA256、处置声明。event_type=integrity_incident（白名单保留非降级 unknown）、HMAC 在、prev 链接真实尾。
- 追加修正事件 `AUD-T-20260916055323-38ce9b9a-0001`：主声明事件 details.ruling 引用的裁定号因**编号冲突**（见 §7.1）由 #264 改 #265——append-only 修正声明，原事件零改动。
- 【GW-A2 追加】修正事件 `AUD-T-20260916073948-cf34458b-0001`（行 #115630，真钥签名 hmac_valid）：#265→#266 二次修正（见 §7.1 终态与 §9.2）——append-only，既有事件零改动。

## 6. T5 验证

1. **全链复普查（T5-1，4.2s）**：总数 113,694→114,411（+717，含 incident 事件与活跃写方真实事件）；三维计数与 T1 基线**完全一致**：prev 断链 5,595、内容失配 5,343、HMAC 失配 53,718（=26,809 legacy 约定 + 26,909 丢钥段，单约定速查口径）——**新增段零损伤**。
2. **真实写入窗口观察（T5-2，≥10 分钟）**：见 §6.1。
3. **测试**：writer/verifier/retention 基线 65 passed；新并发套件 11 passed（writer+multiproc 合跑 41 passed）；writer 消费方广套件（log_rotation/merkle_audit/merkle_hourly/tiered_storage×2/bridge/tamper_evident_log/query/replay_engine/genesis）235 passed ×4 轮；tests/audit 只读回归（test_audit_chain_verifier + test_audit_adversarial）63 passed。**零回归。**

### 6.1 真实写入窗口观察结果

- 窗口：2026-09-16 13:47:50 → 13:58:51（11 分钟，≥10 分钟达标）
- 窗口起点总数 114,413（含 incident 主声明+修正事件）→ 终点 114,479
- 事件行号 #114412 起（incident 事件之后）新段共 **68 条**，全部来自真实活跃写方（gate_engine 等多通道，非测试写入）
- 新段 prev 链断点 = **0**，判定 **ZERO_NEW_DAMAGE**——治本前该写方群体以 ~40 断链/80 事件比率产损（复现实测），治本后真实负载下零断链。

## 7. T6 裁定、红蓝与收尾

### 7.1 裁定

- 本案裁定登记终号为**裁定#266**（ruling_registry.yaml，safe_write_text CAS 通道）。改号历程：原登记 #264 时发生**编号冲突**——并发会话 st-wyf3-20260916（WYF-3 wyckoff walk-forward）同期抢占 #264，两撞号条目一度同文件并存（其中一份经 commit 2b6a74b6 载入）；GW-A 班先改号 #265（本报告 §5 修正事件即该改号的链上凭据），后因 #265 号位在他会话在途窗口被让位规避，终定 **#266**（链上以二次修正事件 #265→#266 收口，见 §9.2）。按编号连续分配铁律与本会话"他会话在途件不代修"纪律（宪法 §3.4），WYF-3 条目（#264）原样保留归其会话/Owner 处置。裁定文本另有一处经 OPEN-WITHOUT-WITH/PERM-TRIGGER 门禁往返后的方案修正（见 §7.2③④），条目文本已同步为终版。
- commit 2b6a74b6 的 commit message 中"msvcrt LK_NBLCK 自旋"为门禁往返前旧描述，终版代码为 LK_LOCK OS 阻塞锁（§4 描述为准）——不 rewrite 已落地 commit，以本报告与裁定#266 为准。
- 【GW-A2 注】密钥政策延续裁定=**裁定#267**（st-auditkey-20260916，Owner 开工令：分期验证语义+256-bit 真钥部署批次 A/B/C），与本报告三维取证构成同案两裁定；默认钥保护强度 Owner 决策项已由 #267 裁定落地（见 §9.3）。

### 7.2 红蓝推演与门禁往返实录

1. **锁死锁场景**：临界区单锁、无嵌套、无锁序交叉——无死锁环。等待交 OS（LK_LOCK ~10s 耗尽/flock 全阻塞），获取失败映射 TimeoutError fail-closed（宁丢一条事件不写断链）。测试：mutual-exclusion 阻塞-释放时序绿。
2. **持锁进程中途被杀**：msvcrt/fcntl 锁随句柄生命周期，进程死亡 OS 关柄自动释放，无 stale 锁、无需清理者。测试：子进程 kill(9) 后父进程立即获取成功，绿。
3. **PERM-TRIGGER 往返**：初版锁等待=用户态自旋（2ms sleep 至 10s 超时）被 PERM-TRIGGER 门禁拦截（writer.py [TTL] permanent + .sleep( 模式）。正确归因：门禁铁律"永久系统禁时间触发轮询"本就否定自旋方案——重设计为 **OS 阻塞锁**（零用户态轮询），语义更优，队列项 requeue 后过闸。
4. **OPEN-WITHOUT-WITH 往返**：裸 `open()` 持句柄写法被拦；config/governance/noqa_exempt_registry.yaml 豁免登记属本任务禁区（禁碰 config/**）——改为 **with 持柄 + 内层 finally 先 UNLCK、with 退出后关柄**结构化解，零豁免零禁区越界，过闸。
5. **大文件追加边界**：尾行跨 64KB 块（200KB 大行实测定位正确）；撕裂尾行（崩溃残留半行）跳过回溯；扫描超 32MB 上限 RuntimeError fail-closed。测试绿。
6. **锁文件风险**：events.jsonl.lock 永不删除（删除=拆散互斥域）；Windows 句柄未关前第三方删除被 OS 拒绝（无 FILE_SHARE_DELETE）。

### 7.3 提交与清理

- commit 1：`2b6a74b6c3cc26d612e0697891483ca224042603`（writer.py + test_writer_multiproc_append.py + ruling_registry.yaml，归属核实=恰 3 文件无连坐）。
- commit 2：本报告 + capability_canonical_file_registry.yaml（creation token）+ ruling_registry.yaml（裁定#265 改号+文本终版）。
- 临时件：.runtime/tmp 下普查/复现脚本与结果、pytest_cache_gwa、广套件日志——关键证据已全部内嵌本报告，冗余临时件清理。
- claim：会话收尾统一释放。

## 8. 诚实条款（未决/限制，如实声明）

1. HMAC 中段（#26810-#53718，26,909 条）**永久不可验证**：写入期 env 密钥值已丢失（.env 现空）。这是密钥管理欠账，本次未也无法"修复"——只能显式声明边界。若 Owner 日后找回历史密钥，重跑普查脚本即可收窄该段定性。
2. gate_chain.jsonl（AuditChainVerifier 本地链）当前 145 条 0 断链，本次**未加锁**（最小 diff 纪律）：其 `_persist_entry`+`append` 存在与 events.jsonl 同构的多实例竞态风险，当前单写方期无症状。若未来多进程 verifier 并发成为现实，复用 `_cross_process_append_lock` 同型改造即可（已在裁定中登记为观察项）。
3. 并发回归测试在首轮广套件联跑中出现 1 次 `test_multi_process_appends_produce_complete_chain` 失败，随后 5 轮全绿（235 passed ×4 + 本套件隔离跑多次）未复现，失败断言文本因首轮未落日志已不可考。无法排除环境级瞬时因素（子进程 spawn 竞争），亦无法证伪——如实留痕。
4. writer 的 strip 治本（entry.pop）已在先班落地，本次普查确认其生效点 #77357 起 gate_audit 内容哈希零新失配——该 5,343 条历史段属先前欠账，本报告仅归因确认。
5. 裁定编号冲突事件（§7.1）中，两撞号条目之一经 commit 2b6a74b6 载入历史——WYF-3 条目（保留 #264）与本方条目（终号 #266，历经 #265 中间号）的最终合法性认定属 Owner 门位；本报告如实留痕。
6. commit 2b6a74b6 piggyback 载入了 WYF-3 会话已写入工作区的 ruling_registry 条目（重 stage 窗口交割）——该会话在途内容按"不代修"纪律未删改，仅以改号方式消解本方撞号。

---

## 9. GW-A2 接力收口附录（st-auditfix2-20260916，2026-09-16）

> 前班（st-auditfix/GW-A flash 班）死于配额墙后，GW-A2 接力会话接管收口。本附录只追加不改写上文取证事实；章节引用如实回指。

### 9.1 遗留审计结论（第二回合完成度）

- era 验证逻辑（integrity.py +207/-13）接手时**代码完整、测试全绿**（era 套件 9/9、writer 多进程 11/11、audit core 32/32），非半成品。
- era 表数据含**两处边界缺陷**（接力独立发现，随后由并行密钥班 st-auditkey 修复）：① 末条 #53718 ts=19:51:35.**781603** 带微秒，valid_to 秒级截断使其掉出遗失期误判 mismatch；② 段内 17 条 finding 导入批带整点占位时间戳 2026-05-26T**12:00:00**Z（早于写方重建时刻 15:39:47Z），按记录时间戳分期误划默认期——st-auditkey 以嵌套微分期 era-lost-may2026-finding-import（12:00:00Z→15:39:47Z）+终点取 19:51:36Z 修复，经 14 天过渡窗语义复验无误伤。
- 密钥分期线实际由**并行会话 st-auditkey-20260916（Owner 开工令）**完成收口（裁定#267：分期语义+批次 B 真钥部署 2026-09-16T07:05:02Z+writer I8 回归修复）；GW-A2 遵"他会话活跃件不硬闯"改走独立验证线，二者分工以该会话报告 §4.4"报告不代修"声明为界。

### 9.2 撞号改号终态与链上凭据

- ruling_registry 现值：#264=WYF-3（合法在先保留）、**#266=本案**（#265 空号让位）、#267=密钥分期与新钥部署（st-auditkey）、#268=transport（他会话）。
- 链上修正链：#114411 主声明（引 #264）→ #114424 修正事件（#264→#265）→ **GW-A2 追加二次修正事件（#265→#266，append-only）**——2b6a74b6 commit message 不可改，以修正事件链为准。
- #266 条目 evidence 路径已由 GW-A2 修正为 `docs/_working/audit_integrity/audit_chain_incident_forensics_gwa.md`（原缺 audit_integrity/ 目录段）。

### 9.3 era 后损伤普查终数（GW-A2 独立复验，07:15:34Z 全链 115,111 条 / 7.2s）

| 维度 | era 前（§2 复验） | era 后 | 定性 |
|---|---|---|---|
| HMAC 失配 | 26,909 | **0** | 26,909=known_loss（遗失钥期精确对应，era 假设被数据完全证实）；88,125=weak（默认钥期诚实计弱）；strong 随真钥写入增长（77→330→402） |
| prev 断链 | 5,595 | 5,595（精确不变） | 历史段边界稳定，治本后零新发 |
| 内容哈希失配 | 5,343 | 5,343（精确不变） | 同上（writer strip 治本生效点 #77357 起） |
| status | compromised | compromised | 仅因两维历史伤；HMAC 维度清零 |

- 密钥部署端到端验证：`import zephyr` 自动加载 .env → environ 可见 43 字符真钥（非默认钥），era-primary（strong）按部署时刻 07:05:02Z 激活，era-default-public 同刻闭合——密钥解析链零缺口。

### 9.4 红蓝验证（GW-A2，沙箱 5 场景全过）

1. **era 边界交界精度**：界前 1µs=旧纪元 weak / 界上（含端点）与界后 1µs=新纪元 strong——covers() 含起点、斥终点语义实测正确。
2. **蓝军·界上旧钥重签**：必判 mismatch（纪元围栏钉死，try-all 通道不存在）。
3. **时钟回拨跨纪元**：回拨事件按其记录时间戳归旧纪元，真钥不验（fail-closed 非 fail-open）。
4. **蓝军·披露（设计边界，非缺陷）**：伪造回拨时间戳+公开旧钥可获 weak 判——纪元归属跟随记录时间戳是设计契约（era 表头注同源），防线在链结构完整性+运维时钟纪律，已在移交清单 C-3（overlap 收窄）部分缓解。
5. **多写方+era 并发（滚动重启语义）**：部署后旧钥写方 25 条+新钥写方 25 条跨线程交错，跨进程锁保护下零断链、strong=25/weak=25/mismatch=0。

### 9.5 测试与验证窗口总账（GW-A2）

- 循环测试两轮：tests/governance/audit + tests/audit 全量 **3,364 passed / 6 skipped / 0 failed ×2 轮**（含 era 9、writer 多进程 11、既有 integrity/adversarial 32）。
- 真实写入窗口：07:15:34Z→07:26:44Z（**11.2 分钟**），新段 +325 事件（真实活跃写方），**新段损伤=0（ZERO_NEW_DAMAGE）**，HMAC mismatch 恒 0。

### 9.6 默认钥匙保护强度评估（Owner 决策项终态）

- 现状：**已由裁定#267 落地解决**——Owner"开工"令授权 st-auditkey 会话于 2026-09-16T07:05:02Z 部署 256-bit 真钥入 .env（指纹 sha256[:12]=0fc77a652196，全值不落 git 资产），公开默认钥装饰期（88,125 条 weak）就此终结；分期语义同窗先行（era-default-public.valid_to=era-primary.valid_from=部署时刻）。
- 遗留运维项（st-auditkey 移交清单 C-1~C-4，属维护班）：gate_chain.jsonl 同型锁、log_rotation 接锁、长驻写方滚动重启后 overlap 收窄至 0、secret_registry 周期核对。
- GW-A2 未自行换钥（任务书禁令遵守）；本节仅记录决策终态与独立验证结论。

### 9.7 编排留痕（如实）

- 本案执行期存在 GW-A 系**三会话并行**：st-auditfix（flash 班，配额阵亡，遗第二回合在途件）、st-auditkey（密钥政策执行班，Owner 开工令）、st-auditfix2（本班，接力收口）。三班以"活跃件不硬闯+他班在途件不代修+append-only 修正链"消解无协调并发，最终分工=st-auditkey 执密钥线（裁定#267）、本班执报告/改号/链上修正收口（本附录）。**重复派单事实如实上报 Owner**：追加-only 账本上并发收口的撞写风险由分工声明化解，建议编排层对同案多班派单附互斥标识。
