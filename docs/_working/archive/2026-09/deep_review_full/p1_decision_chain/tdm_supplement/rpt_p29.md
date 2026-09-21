---
ttl: task_bound
title: 深度审查作业簿——事件图谱传导
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：事件图谱传导（P29）（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件零漂移已核）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/intelligence/news_chain_node_linker.py`
- TDM 节点: TDM-E-L2-09-1（stage）
- 备注: 阶段0对账补册对象（T08 缺口清册）
- 生产调用方: **有真实消费链：`intelligence/chain_impact_stream.py:91-93,436`（W5 盘中事件冲击流，from_pg 生产加载）→ `frontend/dashboard/api_server.py:4139,4149`（仪表盘端点 lazy import）——非孤儿**
- 测试文件: `tests/intelligence/test_news_chain_node_linker.py`（22 用例，本班次实跑 22/22 绿）

## 1 对象快照

298 行规则法 MVP（MOD-INT-NEWS-CHAIN，接线 W3）：新闻文本→产业链图谱节点链接。词表=ig_node JOIN active 链（剔墓碑"已并入"/泛化词候选>8 整词剔除/纯 ASCII 两字母词剔除）；最长词优先+span 占用防嵌套重复命中；ASCII 词边界防拆词（"IP"⊂"IPO" 实证案）；置信度 name 0.90/alias 0.80、歧义×0.8。ERROR_CONTRACT：注入畸形条目抛 ZA-IT-0029；PG 不可达 from_pg 显式抛（W5 catch 降级）；空词表 fail-open 返回空。测试覆盖：墓碑/泛化/ASCII 边界/歧义/畸形注入，断言精确（含实证回归 case）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 逻辑①：最长优先+span 占用算法正确——`sorted(key=len, reverse=True)` 扫描序、`_overlaps` 区间相交判定 `start<e and s<end`（:142-144）为标准 [start,end) 相交式；同词多次出现非重叠 span 均产出（:273-297 循环正确） | news_chain_node_linker.py:142-144,271-297 | 通过 | tests 覆盖嵌套/多命中 |
| A 深度 | 边界②：空文本/空词表→空元组（:267-268）；畸形条目 raise（:180-181）；置信度 `min(1.0, 0.9×0.8)=0.72` 恒在 [0,1] 无越界；归一化 len<2 剔除（:199-202）防单字噪声 | :180-181,199-202,267-268 | 通过 | — |
| A 深度 | 语义③：**同词候选组置信度取 `candidates[0][4]`（组内首条来源）**（:281）——当同名 term 分别来自 A 节点 name 与 B 节点 alias 时组内混源，取 0.90 还是 0.80 取决于 entries 注入顺序=顺序依赖的隐式不确定性 | :279-282 | P3 | 构造两条目（name"X"+alias"X"）换序对拍 confidence |
| B 上游 | checklist #6 断供：PG 断供→from_pg 显式抛（:236 契约"调用方 W5 流层 catch 降级"）——fail-closed 设计、断供有痕，**非恒0非静默**；词表空（查询为空）fail-open 返回空=降级链最后一级，语义声明清楚 | :232-254 | 通过 | mock conn_factory 抛异常观察 |
| B 上游 | checklist #9 幽灵引用：词表来自 ig_node 主键，node_id 存在性由来源表保证；SQL 只读 JOIN active 链（:111-115）模块级常量+noqa 豁免声明 | :111-115 | 通过 | — |
| C 下游 | 消费方=chain_impact_stream（真实 import:91-93 + 生产 from_pg:436）→ api_server 端点:4139；本对象 link() 返回错值→W5 流把伪节点冲击下发仪表盘（决策链末端=人工看板，爆炸半径=前端展示层）；**同节点多 span 命中产出重复 ChainNodeHit，去重责任在消费方——隐式契约未见文档** | chain_impact_stream.py:91-93,436; api_server.py:4139 | P3 | 构造文本含同词两处观察重复 hit |
| D 旁系 | checklist #4 双承载：与 news_symbol_linker（标的级链接器）为同代际兄弟——归一化复用其 normalize_text（:80，无复制=正确方向）；词表 SQL、_TOMBSTONE_MARK、置信度常量各自持有但用途不同（节点级 vs 标的级），无同式两算 | :80,102-107 | 通过 | grep `normalize_text` 引用 |
| E 对抗 | 五问：①静默失败=from_pg 连接关闭异常静默 pass（:250-251，只读已完成，无害留痕）②假阳性=泛化词剔除阈值 8 为硬编码（:99）——若图谱新增 9+ 同名节点是真环节组则整词被误剔（结构性漏报，MVP 声明可接受）③断了没人知道=PG 断供显式抛，W5 有 catch 降级约定④重触发幂等（纯函数只读）⑤时序=N/A | :99,250-251 | P3 | ig_node 造 9 同名观察词表缺失 |
| F 新鲜度 | 规则词典匹配 vs 业界 NER/知识图谱事件抽取：MVP 选择规则法与低延迟盘中流场景匹配；供应链事件沿链传导对股价的影响有实证文献支撑（Emerald/IJOPM 供应链质量事件→股价；Wiley/Jacobs 2022 −3.33% 一级供应商传导效应）——**对等已有（规则法 MVP 声明诚实），NER 升级留白合理** | https://www.emerald.com/ijopm/article/43/2/197/144760 ；https://onlinelibrary.wiley.com/doi/full/10.1002/joom.1197 | 通过 | WebSearch 2026-09-18 |

## 3 SOTA 对照

- 对等已有：规则词典+最长匹配为实体链接 MVP 常规实现；图谱节点级事件传导的经济学有效性有文献支撑（IJOPM 2022 供应链质量事件研究）。
- 立卡候选：无（源码已声明 NER/语义模型为"不做什么"边界，属后续代际）。
- 驳回：无。

## 4 缺陷清单

1. P3：置信度混源顺序依赖（candidates[0][4]）——同 norm 词 name/alias 混组时置信度随注入顺序漂移；建议=组内按 source 优先级取分或拆组；验证法=§2 A 轴对拍。
2. P3：同节点多 span 重复 hit 无去重约定，去重责任隐式落在 W5 消费方——建议头注补契约；验证法=同词两处文本观察。
3. P3：泛化词剔除阈值 MAX_CANDIDATES_PER_TERM=8 硬编码无校准记录——图谱扩链后可能结构性漏报真环节词；建议=接线统计后校准。

## 5 挂起疑问

- aliases 列"当前全空但 schema 支持"（:23,:110）——alias 路径（置信度 0.80）实际未曾在真实词表运行，路径属未实证分支。

## 6 完备性自评

六轴全查（F 带 URL）。长尾：①`chain_impact_stream` 自身深审属 W5（不在本批），其 catch 降级行为未逐行验②ig_node/ig_chain 数据质量（墓碑标注纪律）未做数据画像③`_splits_ascii_token` 仅处理 ASCII 边界，中英混合词（如"AI眼镜"）边界语义靠约定——tests 有 case 但真实词表分布未验。

## 7 收口裁定（收口方填）
