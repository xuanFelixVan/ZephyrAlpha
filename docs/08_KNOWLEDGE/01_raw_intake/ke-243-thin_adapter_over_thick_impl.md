---
module_id: KE-222
status: active
title: 原则 2：Thin Adapter Over Thick Implementation / 薄适配器优于厚实现
category: documentation
ttl: permanent
---

# 原则 2：Thin Adapter Over Thick Implementation / 薄适配器优于厚实现

原则 2：Thin Adapter Over Thick Implementation / 薄适配器优于厚实现

> 当决策为 Buy/Buy+Wrap 时，必须通过 OCP 扩展点 + ACL 适配器引入，避免业务逻辑与开源项目深度耦合。

**实现路径**（对齐 KBG-0004 + 03-AA §4.4）：
```
开源项目 API
    ↓
ACL adapter（薄层封装，翻译为 canonical schema）
    ↓
OCP 扩展点基类（业务层只依赖抽象接口，不依赖具体开源库）
    ↓
业务逻辑
```

**关键约束**：
- 业务代码**禁止**直接 `import` 开源库的内部类/函数
- 所有 OSS 交互必须经过 adapter，adapter 实现 OCP 基类接口
- 更换开源库 → 只换 adapter，业务代码零变动
- Adapter 代码量应 ≤ 业务逻辑代码量的 20%（"薄"的量化标准）

---
