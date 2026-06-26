---
module_id: KE-1361
status: active
title: 10.3 门禁模板本身升级流程
category: module_blueprint
ttl: permanent
---

# 10.3 门禁模板本身升级流程

10.3 门禁模板本身升级流程

```
1. 修改 _template.yaml → bump schema_version
2. 归档当前模板 → _template_v{N}.yaml（铁律四——不删除）
3. 在 gate-engine blueprint 变更记录中登记
4. 通知所有门禁维护者评估是否需要迁移
```

---
---
