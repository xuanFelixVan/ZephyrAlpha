---
ttl: task_bound
title: "L线 potential_consumers 回放台账（总筹裁-07）"
session: zc-lane-l-20260927
completes_when: "供数反查轴经守卫稳定运行且战役收官归档后转入 docs 归档面"
---

# lane_l_replay_ledger.md — L 线 potential_consumers 二次清零：取证+回放+守卫台账

> 会话=zc-lane-l-20260927｜授权=总筹裁-07（90_rulings_ledger.md 裁-07，RULE-DATA-OPS 三步验证过）
> 日期=2026-09-27｜写路径=Librarian 唯一写路径（零裸 SQL 写、零 TRUNCATE/DELETE、零手工 UPDATE）

## 1. 取证结论（元凶）

**首轮清零（直接元凶）**：`st-audit-fix-20260924` 的 post-commit reconciler 全量再采集。
- 68 条回填存证：lib_events event 68 条 `detail ILIKE '%backfill%'`，actor=st-cmd-20260924，action=update，
  时间窗=2026-09-24 12:39:18.495～12:39:18.587（单批机械回填，供给册 S1-S70 批1）。
- 68 资产回填后**首次被触碰**：68/68 全部在 **2026-09-24 16:30:11**（±50ms）被
  actor=st-audit-fix-20260924、action=register 触碰（该轮全量 33,717 register/时）。
- 时代码状态：clobber 窗口 [952a827db6 09-24 12:01, 1e9b34999d 09-25 02:40)——Python 侧
  `f.get("potential_consumers") or []`（12b00068b5 L156/L227）把"缺省"变"显式空数组"，
  冲突分支 `COALESCE(EXCLUDED.pc, 存量)` 对 '{}' 无保护 → 68 条当场清零。
- 证据边界：16:30 触碰即清零的推断基于该窗口代码的机械行为（空数组经 EXCLUDED 直达冲突赋值），
  无逐行前后镜像存证；但①该窗口 SQL 行为已被影子表探针复现 ②回填后到 16:30 前无其他触碰，
  链路唯一。

**持续清零（根因，1e9b34999d "修复"不彻底）**：
- VALUES 分支 `COALESCE(%s::text[], '{}')` 在 INSERT 求值期把 NULL **预空成 '{}'**，
  EXCLUDED.pc 恒非 NULL → 冲突分支引用 EXCLUDED 的 COALESCE 守卫**恒失效**。
- 受控探针（temp 影子表，rollback 零持久）：HEAD 语义 None 冲突 → `[]`（清零）；
  修复形态（冲突分支引裸参数）None 冲突 → 保留存量。生产意外实证：探针误落行
  （见 §5）两步 upsert 后 pc=['KEEP-A','KEEP-B']→[]，与探针一致。
- 后果：09-25～09-27 每轮全量 ingest（st-wm1-wave0 09-25 169,734、st-qmine/st-bca-a-ps1/
  st-ddup/st-backup-cold/st-zmaster/st-chief3/st-commitspeed-tbl/st-chief5 等每日 ~34k）
  每轮都在清零 → 44,816 行该字段全空、--feeds 恒空。**不修根因，任何回放必被下一轮再清。**

## 2. 时间线（关键锚点）

| 时点 | 事件 |
|---|---|
| 09-24 12:01 | 952a827db6 扩列（ON CONFLICT COALESCE 出现，但 Python `or []` 未修） |
| 09-24 12:08 | 12b00068b5 --feeds 反查面（当时实测 24_daban 命中 block_trade_detail） |
| 09-24 12:39:18 | #410②批1 回填 68 资产（st-cmd-20260924，存证 68 events） |
| 09-24 16:30:11 | **st-audit-fix-20260924 全量 ingest 首轮清零（元凶）** |
| 09-25 02:40 | 1e9b34999d Python 传 None + VALUES COALESCE（预空缺陷引入，守卫仍失效） |
| 09-25～09-27 | 多轮全量 ingest 持续清零（st-wm1-wave0 169,734 等） |
| 09-27 03:0x | L 线受控探针双证 + 根因修复 + 回放 |

## 3. 回放（经 Librarian.act 唯一写路径）

- 重建口径：数组=事件 detail.labels_added（与 12b00068b5 提交信息"24_daban 命中"互证）；
  provenance 原样入 detail。68 事件=68 资产 1:1，distinct 标签 65 个。
- 逐条 `act("update", asset_id, actor=zc-lane-l-20260927, fields={当前行全字段透传
  （kind/home/status/owner_domain/retention/tags 无条件覆盖列必须透传）+ potential_consumers=重建数组},
  detail={replay 标记+labels_added+provenance})`。
- **计数：before=0 → after=68（written=68/68，errors=0）**。
- 抽检：dragon_tiger 7 标签、block_trade_detail 2 标签完整复原。

## 4. 守卫与修复（本批 commit）

1. `_SQL_UPSERT_ASSET` 冲突分支改引裸参数 `COALESCE(%s::text[], lib_assets.potential_consumers)`，
   占位 13→15，act/register_batch 参数传两次；None=保留、显式 []=有意清空语义不变（ledger_schema.py）。
2. `ingest_with_shrink_guard`（library_regen_reconciler.py）：全量入账前后供数非空计数快照对比，
   缩水=先写 audit 告警事件（LIB:INGEST-SHRINK-GUARD）再 raise LibraryIngestShrinkError
   （reconciler fail-soft 折叠 warn；事件触发，零 cron/sleep-loop）。
3. 测试：tests/library 42 passed, 4 skipped。skip=pg_db 真语义轨（本机未配独立测试 PG，
   ZEPHYR_TEST_PG 轨按设计 skip；零生产触碰）。关键反证断言：冲突分支禁现
   `EXCLUDED.potential_consumers`（本缺陷类最小锁定）。
4. 验收：`--feeds 24_daban` → 命中 TBL:ch:c1_market.block_trade_detail（与 09-24 首次验收一致）；
   `--feeds 游资温度` → 命中 TBL:ch:c1_market.dragon_tiger（7 标签）。
   `--feeds dragon_tiger` 零命中属预期：该轴匹配"消费方标签含关键词"，回填标签无此子串。

## 5. 事故记录（L 线自伤，已按协议处置）

首个探针脚本（lane_l_pg_probe.py）误将 upsert 常量打向真实 lib_assets（temp 表未用同名影子），
且 reader 角色连接 autocommit=True → 探针行 P:keep（registered_by=probe）于 09-27 03:04:09 落产账。
处置：`Librarian.act("delete", authority="总筹裁-07 附带处置…")` 死亡证明软删除（event 1994629，
status=deceased）。该事故顺带完成 HEAD 缺陷的生产实证。后续探针改用 pg_temp 同名影子+rollback。

## 6. 落地与残余风险

- 批1（代码+测试 5 文件）：qid=q-20260927-zc-lane-l-20260927-0001 → **973b03c3a4**（973b03c3a400fce3c09220112daa9cefe61e08e8，03:40 落地，git log -1 --name-only 核归属=恰 5 文件零搭便车）。
- 实战验证：03:28 st-fms-chief-20260927 全量轮（34,236 register，吃工作区已修代码）后非空计数仍=68。
- 批2（本台账）：见 91_progress.md 同日行。
- 残余风险：①修复落地前已启动的长驻进程若内存持有旧 SQL 常量，其触发的全量 ingest 仍会清零
  （守卫同因失效）——重启后自愈；②--feeds 反查面匹配的是消费方标签，非资产名。
