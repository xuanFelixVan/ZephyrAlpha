---
module_id: KE-module_blu-ai______oac-005
title: AI 施工约定（OaC）
category: module_blueprint
---

# AI 施工约定（OaC）

AI 施工约定（OaC）

```
1. 所有可观测性配置 MUST 在 config/ 目录，与业务代码同仓 git 管理
2. 禁止在 Grafana UI 中手动编辑 Dashboard——Dashboard 定义从 config/dashboards/ 加载
3. Alert rules / SLI registry / Schema 变更 MUST 通过 git PR → 人工确认 → merge → 热加载
4. AI 发现配置问题 → 自动生成 PR 修改 config/ YAML（而非直接修改运行中的配置）
```

---
