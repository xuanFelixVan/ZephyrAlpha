---
module_id: KE-agent_inst-6_2________atomic_transaction_-005
title: 6.2 原子事务模式（Atomic Transaction Mode）
category: agent_instruction
---

# 6.2 原子事务模式（Atomic Transaction Mode）

6.2 原子事务模式（Atomic Transaction Mode）

所有文件修改必须是原子操作——一步完成、直接到位。**禁止**间接引用和多次跳转映射。

- **规则**：
  - 修改一个文件时，相关联动修改必须在同一操作用中完成
  - 禁止"本文件已废弃，请参见 X"的占位跳转文件——废弃走 `superseded_by` 字段
  - 引用链不超过 3 层（见 GOV-DOC-009 DOC-009）
  - 跨文件一致性修复：如果一个修改需要在 N 个文件中同步，全部在同一批 SearchReplace 调用中完成
- **大白话**：改东西就一步到位，不要"A 指向 B，B 指向 C"拐几个弯。改一个东西时，所有受影响的文件一起改，不用以后再补

- **测试标记注册链（Test Marker Registration Chain）**：`--strict-markers` 强制要求所有 `@pytest.mark.*` 装饰器必须在 `pyproject.toml [tool.pytest.ini_options] markers` 列表中显式注册。添加/修改任何 `@pytest.mark.*` 装饰器时，**必须在同一 atomic batch 内同步更新 `pyproject.toml` 的 markers 列表**——漏掉这一步会导致 CI 失败（`Unknown marker` Error）。此依赖链条的登记表身份为 REG-INFRA-002（测试标记依赖登记表），新增 marker 后 entry_count 同步+1；自动对账由 `validate_config_integrity.py` L10 层执行。对标 ITIL SACM → 跨系统配置依赖必须显式登记到 CMDB；禁止隐式约定"markers 会自动被识别"——`--strict-markers` 模式下不会。
