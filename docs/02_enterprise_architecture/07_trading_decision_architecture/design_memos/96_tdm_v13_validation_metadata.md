---
ttl: permanent
doc_type: architecture_view
title: TDM v1.3——节点验证元数据、衰减联动与重要性分级（SR 11-7 对齐）
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.1.0"
date: 2026-09-14
topic: tdm_v13_validation_metadata
scope: 07_trading_decision_architecture
depends_on:
  - 69_trading_decision_map
related_issues:
  - "#ARCH-CH-027"
---

# 96：TDM v1.3 设计备忘——为什么地图节点需要"验证元数据"

## 1. 为什么做（Why）

Owner 体检（2026-09-14）发现 TDM"被引用、不被阅读"。寻路挖矿（按 TDM 寻路 SOP，两批）对齐
银行界模型清单治理金标准 SR 11-7/SR 26-2 后，确认三个结构性缺口：

1. **节点验证元数据缺失**：置信度三态（verified/proposed/untested）已立（D5），但"verified 是
   谁、什么时候、用哪次回测验证的"没有字段——verdict 无法回溯到证据，地图信用不可审计；
2. **节点级衰减监控未联动**：decay_watch 存在但不按节点挂钩——总闸 L1（生死线）与边缘节点
   的监控待遇无差别；
3. **重要性分级缺失**（SR 26-2 materiality）：节点影响面无档位，验证资源无法按比例分配。

另有消费场景 S3 挖矿收获（arXiv:2601.13770 Look-Ahead-Bench）：**AI 产物应携带"知识生效日"**
（源发布日+生成模型日期），与地图 effective_from 轴（D120 知识漂移）同构——随本批一并落地。

## 2. 设计（What）

### 2.1 节点 schema 增量（v1.2 → v1.3，全部可空、向后兼容）

```yaml
last_validated_at: date        # 最近一次验证日期；verified 节点必填
validated_by: str              # 验证会话/裁定标识（如 run=SCR-C4-20260913-002056 或 裁定#NNN）
materiality: str               # critical(总闸等生死线)/high/normal（缺省 normal）
decay_scan_frequency: str      # critical=monthly/high=quarterly/normal=semiannual
```

- 回填规则：现存 verified 节点的 last_validated_at 取其 evidence 引用的 run 日期；
  proposed/untested 节点留空（诚实）；
- 置信度语义 D5 不变，本批只加"验证的账"，不动判据本体。

### 2.2 衰减联动

decay_watch 扫描器按 materiality 档读 scan_frequency；扫描结果写 node_verdict 台账（追加式），
异常时在晨审输出。总闸 L1 = critical 首批挂入。

### 2.3 S3 知识生效日哨兵

所有 AI 产物（策略翻译件/判据修订/SOP）头部加 `knowledge_effective_from`（源发布日+生成模型
标识）；回测预检（S3）比对 run 窗口与此哨兵——早于它=知识漂移，须声明（复用 D120 机制）。

## 3. 换卷重考协议（本设计的验收）

总闸 L1 判据为 P0 已验证资产（valid p=4.55e-20），本批**不改判据本体、只加元数据**，故重考范围
限定为：①元数据回填后 align_all+双测试套件全绿；②decay_watch critical 档扫描演练一次；
③S3 哨兵在下一批回测（估值类翻译批）中实际消费一次。判据本体若未来变更，另走 D 裁定+全量重考。

## 4. 分批

- 批1（本备忘批准后）：schema v1.3 + 节点元数据回填（脚本生成，禁手挑）+ 教材/对齐件刷新；
- 批2：decay_watch 联动接线（construction SOP 全流程）；
- 批3：S3 哨兵扩展到翻译件头部 + 消费场景 SOP 升 permanent（与本备忘同批互相引用）。

## 5. 非目标

- 不改任何节点判据本体；不做 Owner 否决过的 owner/risk_tier 人格化字段（v1.9 先例）；
- 不引入节点间影响传播查询（D108 拆分三条件未全过，留待有真实复盘需求时再立项）。
