---
module_id: KE-027--------------gate-registr-005
status: active
title: 6.19 门禁-登记表原子同步铁律（Gate-Registry Atomic Sync Mandate）
category: agent_instruction
---

# 6.19 门禁-登记表原子同步铁律（Gate-Registry Atomic Sync Mandate）

6.19 门禁-登记表原子同步铁律（Gate-Registry Atomic Sync Mandate）

> **v1.0.0（2026-05-06）**：对标 K8s CRD 注册——自定义资源必须同时定义 CRD YAML + 注册到 apiextensions。gate-registry 与本规则同时诞生于"9 个 GATE 失联事故"的根因分析。

**核心原则**：任何 pre-commit hook 的新增/修改/删除 → AI MUST 重新运行 `generate_gate_registry.py` 并确认 `--check` 通过。三文件**原子同步**——改一个不改另外两个 = bug。

**原子同步三文件**：
1. `.pre-commit-config.yaml` — hook 定义（id / name / entry / files）
2. `gate-registry.md` — 自动生成物（运行 `generate_gate_registry.py`），不得手工编辑
3. `registry-master-index.yaml` — REG-GATE-001 `entry_count` MUST 等于 gate-registry 的 `total_gates`

**施工流程**：
```
ADD/MODIFY pre-commit hook
    ↓
python scripts/governance/generators/generate_gate_registry.py
    ↓
python scripts/governance/generators/generate_gate_registry.py --check  # MUST PASS
    ↓
更新 registry-master-index.yaml REG-GATE-001 entry_count
    ↓
git commit — pre-commit GATE-19 会再校验一遍漂移
```

**为什么生成器 regex 必须从 name 字段提取**：pre-commit hook 的 `id` 字段格式不统一（`gate-01-*` vs `gate-zr-*` vs `gate-ssot`）。`name` 字段永远以 `GATE-XX:` 开头，是唯一可靠的结构化 GATE ID 来源。**如果今后 hook name 格式改变 → 同时更新本脚本的 regex 匹配**。

**事后检查机制**：
- **GATE-19（静态清单漂移检测）**：commit 时运行 `generate_gate_registry.py --check`，硬阻断漂移
- **防范能力**：只要 GATE-19 在 pre-commit 中保持 active，任何"加了 hook 忘了同步"的漂移都会被拦截

**为什么不是 CI 阶段再查**：等 CI 发现漂移 = merge 已完成 = 回滚成本远高于 commit 时拦截。对标 GitHub's shift-left on security——Infracost / Trivy / tfsec 都在 pre-commit 跑。
