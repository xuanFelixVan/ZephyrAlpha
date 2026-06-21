---
module_id: KE-1041
status: active
title: 5.4 `03_modules/_b_track_interfaces/` — 原 07_ai_engineering（已合并）
category: governance
---

# 5.4 `03_modules/_b_track_interfaces/` — 原 07_ai_engineering（已合并）

5.4 `03_modules/_b_track_interfaces/` — 原 07_ai_engineering（已合并）

> **v3.2.0**：`07_ai_engineering/` 目录已删除，其内容（5 个 B 轨接口规范）已并入 `03_modules/_b_track_interfaces/`。
> 蓝图、接口规范、施工计划统一在 `03_modules/` 下——AI 冷启动只需遍历一个目录树。

**用途**：5 大 AI 核心服务（LSG/VMS/CE/Orc/FLE）接口合同

**准入规则**：
- ✅ `<service>-interface.md`（如 `llm-security-gateway-interface.md`）
- ❌ 业务层蓝图（→ `03_modules/infra_ops/<module>/`）
