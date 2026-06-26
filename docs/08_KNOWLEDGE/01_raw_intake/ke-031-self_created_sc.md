---
module_id: KE-031------------self-created-sc-005
status: active
title: 6.5 脚本自创入库强制约定（Self-Created Script Library Mandatory Registration）
category: agent_instruction
ttl: permanent
---

# 6.5 脚本自创入库强制约定（Self-Created Script Library Mandatory Registration）

6.5 脚本自创入库强制约定（Self-Created Script Library Mandatory Registration）

> **v2.0.0（2026-05-02）**：触发条件从"治理/审计/校验脚本"升级为"任何 .py 文件"——从语义触发改为行为触发，消除 AI 自我豁免漏洞。对标 Kubernetes Admission Controller（准入控制器——所有资源创建请求必须通过审核） + Git pre-commit hooks（任何文件变更都触发检查）。

AI 在完成任务过程中通过 Write 工具创建的任何 `.py` 文件，**必须在同一 session 内完成入库或例外论证**。禁止"先写个临时脚本扔根目录，以后再整理"——不存在"以后"。

**为什么是"任何 .py 文件"而不是"治理/审计/校验脚本"**：语义分类（"这个脚本算不算治理类"）给了 AI 自我豁免的空间——AI 可以自欺说"这只是个辅助脚本，不算治理工具"。行为触发（"你是不是创建了 .py 文件"）是事实判断——事实不可欺。对标 K8s Admission Controller：准入控制器不区分"正式 Deployment"还是"临时 Pod"，一律进入审核链。

- **两阶段预检（取代自我分类）**——创建任何 `.py` 文件前，AI MUST 执行：
  - **阶段1（事实判定）**：这个文件的落位是否在 `scripts/governance/` 下？
    - ✅ 是 → 走正常入库流程（三件套强制清单）
    - ❌ 否 → 进入阶段2
  - **阶段2（例外判定）**：这个文件是否属于以下**明确豁免**？
    - `src/zephyr/` 下的正式代码 → ✅ 豁免（由 pre-commit/CI 管理）
    - `tests/` 下的测试代码 → ✅ 豁免（由测试框架管理）
    - 项目外部的独立脚本（如 `scripts/governance/reports/` 生成脚本）→ ✅ 豁免
    - **以上都不匹配 → 🔴 违规**——必须在 Session Log 中明确论证"为什么不能放入 scripts/governance/ 的理由 + 为什么是真正的一次性"，论证不充分视为入库失败
- **先查后建（防重复造轮子）**：创建新脚本前，**必须先检查 scripts/governance/ 下是否已有功能等价或可扩展复用的脚本**。检查方式：
  - `python scripts/governance/run_all.py --list` 列出所有已注册脚本的 description
  - 搜索 `scripts/governance/` 下的同名或类似文件
  - 如果有可复用的 → 扩展现有脚本而非新建；如果确实无 → 继续三件套入库
- **三件套强制清单**（缺少任何一项视为未完成入库）：
  1. **脚本落位**：放入 `scripts/governance/{dimension}/`，文件名遵循 `validate_*` / `detect_*` / `audit_*` 约定
  2. **manifest注册**：在 `scripts/governance/script-manifest.yaml` 添加条目（dimensions/priority/timeout/args/description）
  3. **运行验证**：`python scripts/governance/{dimension}/{script}.py --warn-only` → exit 0 + 零诊断
- **入口文件**：`scripts/governance/index.md` §AI施工约定 含详细创建注册工作流
- **专业参考**：ITIL SACM → Configuration Item Registration（配置项登记——任何新资产创建后必须立即注册到CMDB）/ Kubernetes → Admission Controller（准入控制器——不区分资源类型，所有创建请求一律进入审核链）/ Git → pre-commit hooks（任何文件变更都触发检查，不区分"正式"还是"临时"）

> **通俗解释（v2.0 更新）**：以前规则说"治理脚本要入库"，AI 可以狡辩"我这不算治理脚本"就绕过了。现在升级成——不管你写的是什么类型的脚本，只要是 .py 文件，只有三个合法去处：scripts/governance/（工具脚本）、src/zephyr/（正式代码）、tests/（测试代码）。不在这三个地方的，必须在 Session Log 里写清楚为什么。就像 K8s 的准入控制器——不管你是正式应用还是临时 Pod，进集群就得过审核。
