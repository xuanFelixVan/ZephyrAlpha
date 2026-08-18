# 域架构文档（派生产物，已离库）

> **本目录下的 `*.md` 文件（除本 README）已于 2026-08-05 离库（#ARCH-GOV-BUDGET-001 / I-GOV-1）。**
> 这些文档由 [`generate_domain_doc.py`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/generators/generate_domain_doc.py) 从 depgraph (PostgreSQL) 派生，是构建产物而非源真源。

## 为什么离库

派生产物入 git 是 post-commit reconciler 非收敛循环的数学根因：生成器任一非确定性（时间戳/SQL 排序/换行符）→ diff → auto-commit → 再次触发 reconciler → 跨 commit 永续循环。治本：源真源（DB + 生成器代码）已跟踪，派生产物离库，按需生成。详见 [AGENTS.md §11.1.4](file:///d:/ZephyrAlpha/AGENTS.md)。

## 如何生成查看

```powershell
# 生成全部 73 个域文档（+ 联动 HTML）
python scripts/governance/d5_architecture/generators/generate_domain_doc.py --all

# 或用本地 HTTP 服务一键生成 + 浏览器查看
python scripts/serve_docs.py
```

生成后用浏览器打开 `http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/<文件名>.html`（可缩放 Mermaid 图）。

## 源真源

- **depgraph (PostgreSQL)**：nodes + edges 表，模块依赖关系唯一真源
- **生成器代码**：`scripts/governance/d5_architecture/generators/generate_domain_doc.py`
- **模块翻译真源**：`docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml`

本目录的 .md 文件是上述真源的函数产物，重新生成即可恢复，无需版本控制跟踪。
