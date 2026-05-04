---
module_id: ARCH-ENDGAME-001
doc_type: reference
title: 架构终局锁定声明
version: 0.1.0
status: draft
layer: cross_layer
date: '2026-04-22'
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
depends_on:
  - {target: EA-ARCH-MODEL-INDEX, at: "§文件清单", why: "同目录索引——终局锁定文件由 architecture-model 索引管理，引用其文件清单"}
ttl: permanent
---

## 一、架构终局定义

当以下所有条件同时满足时，架构终局全貌完成：

| 条件 | 验收标准 | 当前状态 |
|------|---------|---------|
| 所有 P0/P1 模块已注入 | `module-id-registry.yaml` 中 P0/P1 模块全部 status ≠ planned | ⏳ 待完成 |
| 所有 P0 模块接口契约已定义 | `cross-layer-contracts.yaml` 中 P0 模块契约全部 frozen | ⏳ 待完成 |
| 依赖图完整且无环 | `check_dependency_direction.py` PASS，DAG 无环 | ⏳ 待完成 |
| SSoT 矛盾清零 | `validate_ssot.py` 报告矛盾 = 0 | ⏳ 待完成（scaffold-3） |
| 五大目标全部 PASS | D1~D5 验收标准全部满足 | ⏳ 待完成 |
| 基线指纹已生成 | `architecture-baseline-fingerprint.yaml` 存在 | ⏳ 待完成 |

## 二、锁定后的变更规则

架构终局锁定后（status: Active），以下规则生效：

| 操作类型 | 是否允许 | 审批要求 |
|---------|---------|---------|
| 通过 OCP 扩展点新增模块 | ✅ 允许 | 通过 module_injection_check.py 验证即可 |
| 修改已锁定模块的接口契约 | ❌ 禁止 | 必须走 Emergency Change Board |
| 修改已锁定模块的依赖关系 | ❌ 禁止 | 必须走 Emergency Change Board |
| 修改架构不变量（invariants.yaml） | ❌ 禁止 | 必须走 Emergency Change Board + Owner 签字 |
| 新增架构层（L14+） | ❌ 禁止 | 必须走 Emergency Change Board + Owner 签字 + ADR |

## 三、Emergency Change Board 协议

当需要修改已锁定架构时：

```
1. 提交变更请求（在 Session Log 中描述变更内容和原因）
2. Owner 审查变更请求
3. Owner 批准后，创建 ADR 记录变更决策
4. 执行变更，更新基线指纹
5. 更新本文件的变更记录
```

## 四、基线指纹（锁定后填入）

```yaml
# 锁定时填入
baseline_fingerprint:
  locked_at: "YYYY-MM-DD"
  total_modules: 0  # 锁定时需替换为 _index.yaml global_stats 实际值
  p0_modules: 0  # 锁定时需替换
  p1_modules: 0
  total_contracts: 0
  total_dependency_edges: 0
  sha256_index_yaml: ""
  sha256_contracts_yaml: ""
  sha256_runtime_planes_yaml: ""
```

## 五、变更记录

| 日期 | 变更类型 | 变更内容 | ADR | Owner 确认 |
|------|---------|---------|-----|-----------|
| 2026-04-22 | 文件创建 | 初始草稿，等待 beta 完成后激活 | — | — |

---

*本文件由 ZephyrAlpha Owner 维护。status 从 Draft → Active 的转换必须由 Owner 手动执行。*

> **2026-05-02 审计澄清**：前两次审计曾建议将 status 改为 `active`，但经评估 `draft` 是当前正确状态——终局条件（§三）全部标注"待完成"，在条件满足前标 `active` 会制造虚假信号。后续审计请勿重复提出此问题。
