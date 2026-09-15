---
ttl: permanent
doc_type: policy
rule_form: checklist
verifiability: manual
title: 缺陷模式库——深度审查强制前置 checklist（14 条，每条带真实案例锚点）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-09-15
topic: deep_review
scope: global
depends_on:
  - deep_review_policy
related_issues: []
---

# 缺陷模式库——深度审查强制前置 checklist

> **定位**：[deep_review_policy](deep_review_policy.md) §8 子节点"缺陷模式库"的落地文件。历史系统性缺陷归纳成机械 checklist——**教训不靠记忆靠清单**。深度审查开工时（审查材料包阶段）轴 A/E **前置强制过一遍**，命中项直接按六轴模板出发现。
> **入册纪律**：仅 T3 事故横向排查确认非孤例、且经 deep_review §6 收口确认的 P0/P1 才新增；必须带 commit/文档锚点+轴标签，**无案例不入册**。
> **退役纪律**：条目已固化为 gate/注册表规则→标"已固化"退役（规范预算净零），每季 T4 审查时清点。
> **防双真源**：audit_prompts_20_ai.md 已固化的教训（夜班三教训等）只留指针不复制——双份承载漂移本身就是本库模式 #4。

## Checklist（14 条）

| # | 模式 | 历史案例 | 审查问句 | 轴 |
|---|---|---|---|---|
| 1 | 统计口径单点漂移 | DSR 分母批内 N→累计 N，0.9809 翻案 0.0517（e58d28df99/5548b45ca4） | 统计量分母/窗口/阈值与真源账本同口径？存量重算过？ | A |
| 2 | 测试日期漂移 | catchup_guard 真实日期漂出 10 天窗口致 3 失败（623e32b9c5） | 断言依赖"今天"吗？拨钟到边界日还绿吗？ | A.3 |
| 3 | 测试假阳性 | stub 静默绕过 DM-90974（e5df571ac9）；±5pp 容差 n=12 统计不可达（f487d44acc） | stub 边界/断言强度/容差可达性？ | A.3 |
| 4 | 双份承载漂移 | N-16 豁免名单 YAML↔兜底常量（audit_prompts L200） | 配置几处承载？改真源后副本同步？一致性红未搁置？ | D |
| 5 | 编号失控 | 43 码未登记+5 重号（audit_prompts L204，127f12d82d 再犯）；号段竞速撞车（5697da2892/20065c08f1） | 新码新号全仓 grep 唯一入册？分配前查最大号？ | D |
| 6 | 数据源静默死亡 | 399106 断更两月 F4 恒 0（91a3c77586/dd04d9d20c）；北向停发融合加零不报错（bf7a8283cd） | 每输入近 N 天有数？断供时报错还是恒 0？ | B |
| 7 | A 股口径/量纲/PIT | 不复权假收益（818d676b3a）；volume 量纲失真（a89335642e）；百万平钱包（d9c5f4bb12）；研报快照冒充历史（56e9183b73） | 数学四问逐项过？复权/单位/PIT 有实证？ | A |
| 8 | 孤儿死码 | wyckoff 引擎结构性死亡（d57b379558）；pf_alloc 无生产调用方（d9c5f4bb12） | grep 生产调用方≥1？空转多久没发现？ | C |
| 9 | 幽灵引用/写入口零校验 | anchor 674 连坐（9005a38a7b） | 写入端有存在性校验？id 形态唯一约定？ | B |
| 10 | YAML 静默缺陷 | PyYAML 双根键静默覆盖（ee6bc34aa8）；尾追病二犯（4cb9d58dd7） | 写后 parse+根键唯一断言？追加位置锚定？ | E |
| 11 | 缓存/进程竞态 | ops_guard 毒缓存 4 gate ImportError（558a4af0e2）；调度器早于修复落盘旧代码驻留（bb4e2f9328）；re-register 时序竞态（da6483a87f） | 修复落盘到生效窗口内谁带病运行？ | E |
| 12 | 假完成状态 | 队列假落地 NOTHING_TO_COMMIT（36784c8a62）；假 done landed_id 系他会话（4deb7b97de） | done 状态逐 blob/逐行核验过真落地？ | E |
| 13 | 外部 API 契约未实测 | QMT price_type LIMIT 0→11 实单拒（ae289436aa） | 三方常量有官方值对照+实单 smoke？ | B |
| 14 | 重构丢边丢路由 | hk_connect_flow frozenset 误丢（74c25717a3）；depgraph 重建丢手工边（e5df571ac9） | 重构后路由表/依赖边/注册表全量对账？ | D |

## 轴标签对照

A=深度轴（数学/实现/测试）、A.3=测试正确性、B=上游轴、C=下游轴（爆炸半径）、D=旁系轴（兄弟/漂移）、E=对抗轴（红蓝）。轴定义见 [deep_review_policy §3](deep_review_policy.md)。

## 维护机制

1. **累积**：每次 T3 事故复盘同批追加（复用既有 fix 提交流，不单独立项）。
2. **消费**：深度审查材料包阶段强制过一遍（deep_review_policy §3 材料包表已挂接）；T3 横向排查时作为排查起点。
3. **退役**：条目固化进 gate/注册表规则后标"已固化"，季度 T4 清点。
4. **来源**：v1.0.0 由 git log 近 200 流+文档挖掘归纳（2026-09-15，子代理挖矿），锚点经主力会话抽查核实（6/6 通过）。

## 修订记录

| 日期 | 版本 | 改动内容 | 为什么改 |
|---|---|---|---|
| 2026-09-15 | 1.0.0 | 初稿：14 条模式（每条带案例锚点+审查问句+轴标签）+ 入册/退役纪律 | deep_review_policy §8 子节点"缺陷模式库"挖掘落地；DSR 翻案等历史教训需要机械化消费通道 |
