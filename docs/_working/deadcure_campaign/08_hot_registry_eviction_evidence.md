---
ttl: task_bound
completes_when: 车道A-12 落地册面增量正门或门禁改读意图账本后闭环
---
# P1 立项证据包 · 热册（capability 64k 行）整档快照互踩＝提交面常态化自伤（给车道 A-12）

## 一、本专案一小时内被同一机理打断三次的实弹（全部可复跑核验）

| 时刻 | 事件 | 读数 |
|---|---|---|
| 04:35 | 台账袋第一次入队（5 新 .md/.yaml + 册内 25 行 token 同袋原子） | `gate_prerun` 内容硬阻断 1=CLAIM-REQUIRED；入队成功 |
| 06:29 | 同一袋落地被拦死 | `dead/q-20261009-st-deadcure-restore-chief-0001.json` 死因原文：`CREATE-GUARD 阻断: 无 creation_token ... 5 件全列`——**袋内自带册面，门禁落地时读的却是盘上被别道陈旧快照覆盖后的版本** |
| 06:33-06:47 | 我按工具提示做"盘上基底增量补回"后重登 token | `grep -c deadcure_campaign` 在主区盘读数序列：20 → 0 → 5 → 0 → 5（**同一文件被别道整档快照反复回退**） |
| 06:53 | 改走 **token 先行落地 + 内容随后** 两袋配方 → 成功 | 落地 commit `cbc8be4f2d`；此后 `git show HEAD:...capability_canonical_file_registry.yaml \| grep -c deadcure_campaign` = 5、盘 = 5 |

## 二、这不是本专案独有，而是全域写入口都在踩

1. `batch_creation_tokens.py` 的写前"只增不减"自检在 06:33 直接**拒写并给出全域阻塞说明**：
   `FAIL: 写前自检不过…creation_tokens 写前基底相对 HEAD 缺 3 条…成因＝陈旧整文件快照压在盘上（本役 R-063/Q-7 同型）`。
   被缺的 3 条属他队在册条目（`gov-adjudication-routing-…20261008`／`fullscore-night-handoff-…`／`matrix-handoff-closeout-…`），
   即**别道已进 HEAD 的 token 又被陈旧快照抹掉**——任何会话此后登记 token 都会 FAIL，直到有人增量补回。
2. 面积读数：dead/ 语料里 **541 袋**的文件清单含热册（capability/翻译/裁定/gate/实验/风险分级/ROOR），
   即"整档快照进袋"是本仓死信的第一大结构性来源。
3. 前例在册：`a600b7f71910` 提交自述"基于旧 HEAD 丢他会话 rowvec 24 行"（同型事故已发生过并写在正文里）。
4. `docs/_working/commitmap_cure/final_closeout_report.md` §3.1 记录过同族事故（capability 册并发写交错→CREATE-GUARD 全系 fail-closed）。

## 三、可执行处方（本专案已验证其中一条）

- **已验证可用**：把"新资产 token"与"新资产本体"**拆两袋、token 先行落地**（本专案 06:53 实跑通过）。
  写进 SOP 即可省去后来者重复试错：同袋原子在热册上**不成立**（落地读盘不读袋）。
- **处方 A（根治·建议 A-12 立项）**：热册写入改**行级增量正门**——册面写只允许 `+行集`（CAS+只增不减已是现成判据），
  拒收任何"整档快照"进袋（队列在 enqueue 预检即按 `registry_family` 判：袋内含热册且差异非纯增量 → 转 API 工单，不入库）。
- **处方 B（治标·可与 A 并行）**：CREATE-GUARD/同族门禁的 token 读取源改**PG 意图账本**（`REG-CAPCAN-001` 双轨在册），
  而非盘上 YAML 投影——盘投影滞后/回退不再影响判定，符合 RULE-SSOT"规则数据改 YAML 同步 DB"的方向。
- **禁区**：勿用 `git checkout HEAD -- <册>` 修盘（盘上常同时挂着别道未落地条目，整片覆盖＝二次蒸发；工具正文已写死此警告）。
