---
ttl: task_bound
doc_type: report
title: 深度审查报告——F04 UFL确定性分层（UflDeterministicLayer）
owner: st-deeprev-20260918
reviewer_model: GLM-5.3-Flash
baseline_commit: 2fa92002c3
created: 2026-09-18
---

# 深度审查报告：F04 UFL确定性分层（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: 闸门（特征确定性标记+fail-closed 过滤视图）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/factor/ufl_deterministic_layer.py:70(:84 classify_from_inputs, :105 门面)`
- 生产调用方: **无**（唯一引用=factor/__init__.py re-export；header [CONSUMERS] 自认"候选"）
- 测试文件: tests/factor/test_ufl_deterministic_layer.py（存在）
- 变更热力: 2026 年 5 commits（低热）
- 材料包缺项: 运行时证据包缺（未接线对象，无运行行为可取证）

## 1 对象快照

纯内存"标记台账+行级打标+确定性视图 SQL+读侧过滤"四件套；确定性=输入⊆价量封闭集可重放。排除项：storage_tiering.UFLFactLayer（D_DATA 存储层写闸，语义平行件，已走查分工声明）。数学核心：无算法（逻辑/字符串/SQL 生成件），四问聚焦边界与注入面。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| C | **孤儿（模式#8）**：生产调用方=0（grep 全仓仅 re-export）；打标台账纯内存，进程重启即空→若未来接线，fail-closed 语义=重启后所有因子被判非确定（安全方向但全空视图） | ufl_deterministic_layer.py:112-116; grep 消费方 | P2 | grep 生产 import；重启进程后 deterministic_factor_ids()==∅ |
| A | mark() 异值冲突拒绝不可撤销：误标 is_deterministic=True 后进程内无法纠正（无 unmark/重置 API）；"追加式禁改"语义与"内存台账随进程生灭"自相矛盾——非真持久事实层 | :120-135 | P3 | mark(fid,True) 后 mark(fid,False) 观察抛错 |
| A | classify_from_inputs 封闭集含 vwap/turnover 派生量：若上游 vwap 派生引入非确定源（实时快照兜底），推导失真——当前价量派生下成立，属隐含契约未文档化 | :61-63, 84-92 | P3 | 代码走查 |
| A（注入面） | **SQL 生成闭合**：标识符白名单 ^[A-Za-z_][A-Za-z0-9_]*(\.[...])*$ + 单引号双写 :95-102,240；factor_id 经 _quote_literal 转义后进 IN 谓词，无法逃逸字符串字面量 | :66, 95-102, 236-243 | ✓ 查无 | 构造 factor_id="x'); DROP--" 看 SQL 输出仍为安全字面量 |
| A（边界） | 空确定性集→WHERE 1=0（fail-closed 显式空视图）✓；sorted 输出确定性 ✓；空 factor_id/缺 factor_id 列 ValueError ✓ 与 ERROR_CONTRACT 一致 | :238-242, 184-185, 205-208 | ✓ 查无 | 构造空集/缺键行跑 tag/filter |
| D | is_deterministic 同名概念双承载：本件（元数据标记）vs storage_tiering.py:23（存储写闸 UFLMutationError）vs replay_engine.py——分工已声明（header :31-36）但无一致性 gate，改一头另一头不报 | :31-36; data/storage_tiering.py:23,228-240 | P3（模式#4 风险登记） | 对读三处语义 |
| E | filter_deterministic 未标记行静默滤除（fail-closed 符合设计）但无"滤除计数/审计"返回——批量滤除不可观测 | :192-211 | P3 | 调用后无任何被滤行信息可查 |

## 3 SOTA 对照

- docstring 自称"feast 式标记+视图"：对照 Feast feature store 的 on-demand/source 确定性标注——**受阻未搜**（本批检索预算用于数学核心；本件为 feast 语义的窄子集，立卡依赖接线决策而非外部做法）。
- 结论：受阻如实记。

## 4 缺陷清单

1. **P2 孤儿+重启失忆**：候选消费方未接线+台账无持久化通道（header :24-25 声称"打标落元数据层"，代码无任何持久化钩子——文档承诺与实现不符）。建议：接线前先定台账持久化真源（YAML/DB），否则视图每次重建为空。验证法：重启后集合为空。
2. **P3 组**：mark 不可撤销的运维刚性、封闭集含派生量的隐含契约、滤除不可观测、is_deterministic 三处承载无一致性 gate。

## 5 挂起疑问

- "打标落元数据层"（:24-25）与代码无持久化之间的落差是有意（装配批补）还是漂移——待 Owner 裁定；影响接线排期。

## 6 完备性自评

六轴全查（F 受阻记）。数学四问以边界/注入面覆盖（无算法递推）。长尾：①并发 mark 竞态（dict 非线程安全，单线程假设未文档化）；②CREATE OR REPLACE VIEW 对 CH 版本依赖（21.x+）未验证目标库版本。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
