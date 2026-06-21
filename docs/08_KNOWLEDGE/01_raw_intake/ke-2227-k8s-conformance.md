---
module_id: KE-2134-------k8s-conformance-003
status: active
title: 3.6 按标签分类（K8s Conformance 对齐）
category: module_blueprint
---

# 3.6 按标签分类（K8s Conformance 对齐）

3.6 按标签分类（K8s Conformance 对齐）

> 对标 K8s `[Conformance]`/`[Disruptive]` 标签聚焦机制——脚本可被打上多个标签，`--tags` 参数按标签选择执行。

| 标签 | 含义 | 示例应用 |
|------|------|---------|
| `[Quick]` | 快速检查，<5s 完成 | 文件存在性检查、格式校验 |
| `[Security]` | 安全相关扫描 | SAST扫描、密钥检测、CVE审计 |
| `[Disruptive]` | 可能修改文件或影响环境的脚本 | 自动格式化、数据库迁移校验 |
| `[Critical]` | P0优先级，出错必须立即修复 | 编码安全检查、pre-commit核心门禁 |
| `[AI-Generated]` | 针对 AI 产出的专项检查 | 幻觉检测、AI生成代码质量 |
| `[Periodic]` | 周期性运行（非每次提交触发） | 周度审计报告、覆盖率趋势分析 |

> **使用方式**：`python scripts/governance/run_all.py --tags Security,Quick` → 只运行**同时**打有 Security **和** Quick 标签的脚本（AND 语义）。
>
> **自动推导规则**（`generate_script_manifest.py` 生成时自动计算，存入 `script-manifest.yaml`）：
>
> | 来源 | 规则 |
> |------|------|
> | 维度 | D1-D4,D8 → `Quick` / D5,D7 → `Critical` / D6,D11 → `Security`, `Critical` / D9,D12 → `AI-Generated`, `Periodic` / D10 → `Periodic` |
> | 前缀 | `fix_*`, `generate_*` → `Disruptive`（追加） / `audit_*` → `Periodic`（追加） |
> | 优先级 | P0 → `Critical`（追加，若未因维度获得） |
>
> **AI 公约**：新脚本**无需在 `__manifest__` 块中显式声明 tags**——生成器自动从维度+前缀+优先级推导。标签总会出现在 `script-manifest.yaml` 中，run_all.py 从 manifest 读取标签执行过滤。

---
