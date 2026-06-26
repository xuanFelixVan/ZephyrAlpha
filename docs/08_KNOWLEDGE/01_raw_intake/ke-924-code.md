---
module_id: KE-846
status: active
title: 3. CODE 域（代码级强制规则）
category: governance_rule
ttl: permanent
---

# 3. CODE 域（代码级强制规则）

3. CODE 域（代码级强制规则）

> 来源：`src/` 下的 Python 代码。这些规则已在代码层面强制执行，违反会抛异常或被 CI 拦截。
> 登记的目的是让 AI 和人类知道这些规则存在，避免在文档中重复声明。

| 登记号 | 规则内容 | 强制方式 | 代码路径 | 锁定状态 |
|--------|---------|---------|---------|:--------:|
| CODE-001 | 禁止 float 参与金融计算——Money 构造时 float 直接抛 MoneyPrecisionError | code | `src/zephyr/shared/contracts/money.py` L152-158, L195-198, L206-209 | 🔒 |
| CODE-002 | 禁止 naive datetime 进入系统——ensure_utc() 对无 tzinfo 的 datetime 抛 NaiveDatetimeError | code | `src/zephyr/shared/contracts/timestamp.py` L98-161 | 🔒 |
| CODE-003 | 禁止 datetime.now() / datetime.utcnow()——全公司唯一获取当前时间的方式是 utcnow() | code | `src/zephyr/shared/contracts/timestamp.py` L79-95 | 🔒 |
| CODE-004 | 禁止 shell=True 执行子进程——沙箱强制 list[str] 形式传入命令 | code | `src/zephyr/llm-security/process_sandbox.py` L36-37 | 🔒 |
| CODE-005 | subprocess 调用必须设置 timeout（默认 60 秒）——超时进程树被强制终止 | code | `src/zephyr/llm-security/process_sandbox.py` L33-34 | 🔒 |
| CODE-006 | deny 规则不可绕过——命中 deny 必须返回 CapabilityDenied | code | `src/zephyr/shared/capability.py` L14 | 🔒 |
| CODE-007 | 知识库写入必须传 provenance——缺失抛 WriteTraceMissing | code | `src/zephyr/kb/unified_memory_api.py` L17, L23 | 🔒 |
| CODE-008 | HOT_PATH_ACTIVATED=False 时禁止调用 Hot Path 代码路径——违反即 CI gate 驳回 | code | `src/zephyr/shared/contracts/runtime_plane_tag.py` L132 | 🔒 |
| CODE-009 | contracts 目录禁止放业务逻辑——只放数据结构定义 | doc | `src/zephyr/shared/contracts/__init__.py` L9 | 🔒 |
| CODE-010 | SSoT 注册表同步暂存约束（C-1~C-4）——新增/删除治理文件时注册表必须同步 | hook | `src/zephyr/hooks/ssot_guard.py` L27-30 | 🔒 |

---
