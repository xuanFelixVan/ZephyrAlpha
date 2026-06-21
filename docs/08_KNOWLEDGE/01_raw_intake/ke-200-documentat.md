---
module_id: KE-180
status: active
title: 2.2 档位判定规则（防刷分）
category: documentation
---

# 2.2 档位判定规则（防刷分）

2.2 档位判定规则（防刷分）

**硬门槛**（必须全部满足才能升下一档）：

| 升档方向 | 硬门槛 |
|---|---|
| L0 → L1 | ADR accepted + 架构视图定义 |
| L1 → L2 | 至少 1 个代码文件（stub 即可）+ frontmatter 合规 |
| L2 → L3 | pytest ≥ 60% + sprint 验收记录 + folder-charter 签名 |
| L3 → L4 | 真实资金 OR 真实流量 OR 外部依赖命中 + 治理三层 Runtime 拦截激活 + SLO 监控 |
| L4 → L5 | 至少一项：(a) 公开 benchmark 领先；(b) 开源发布 ≥ 100 stars；(c) 顶级机构同行 review 认可；(d) 业界论文引用 |

**档位降级规则**：
- 季度 review 时发现证据失效 → 强制降档（e.g. 测试覆盖 < 60% 从 L3 降 L2）
- 与 09-GOV 四档执行约定一致：档位是"当前真实状态"不是"曾经达到过"
