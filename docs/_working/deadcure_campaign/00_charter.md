---
ttl: task_bound
completes_when: dead/ 存量袋四终态全覆盖且交付报告经 Owner 消费
---
# 死信清偿专案 · 章程与边界（sid=st-deadcure-20261009）

- 开工：2026-10-09T05:32｜锚点 HEAD=`193dc9db3602`（dev）｜冻结存量=**1704 件**（1701 袋 JSON + 1 空壳 .corrupt-husk + 1 .json.bak-orig + 1 当班新袋）
- 目标：dead/ 每袋达四终态之一——①复活落地 ②归档留痕 ③判废留痕 ④属主退回；按族计里程碑（M1 top5 族→M2 st-cure 余量→M3 收官族→M4 长尾）。
- **边界（防双重施工）**：F-1 十二把回归尺与 tests 新家重建=施工总队车道F，本专案只出源材料指路；业务资产（数据/因子/策略/指标）概念退役=Owner 门位，本专案不代裁；受保护路径（AGENTS.md 等）=Owner 门位。
- 判据铁律：内容级三相对拍（袋 blob git-blob-sha1 vs HEAD blob vs dev 历史行血 lineage），EOL 归一后再比；**禁路径存在级判据**——官方 `dead-archive --days 0` dry-run 实测会把 251 袋未落地内容判为"已落地"归档掉，本专案不采。
- 裁定姿态：每次归档/判废=一次 D1 自裁（Gate 0 存量判退 + E1 内容对比 + E2 先例机检），adjudicator 署名；里程碑汇总裁定入 ruling_registry，不逐袋登记。
- 可逆防护：归档=mv 非删（同卷原子）+ manifest.jsonl 逐件留痕；`deadcure.py restore --qid` 一步回退；blobs/ 零触碰（唯一字节载体）。
